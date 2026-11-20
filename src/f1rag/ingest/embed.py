"""Embed the clauses and the entities into Neo4j vector indexes, using LangChain.

Clauses: each clause becomes one or more Chunk nodes linked to it:

    (:Chunk {id, clause_id, text, embedding})-[:CHUNK_OF]->(:Clause)

Short clauses are one chunk. Long clauses are split into overlapping windows, each with its own vector.
Every chunk starts with a header naming the clause and where it sits in the document.

Keywords: a Neo4j full-text (Lucene, BM25) index `chunk_fulltext` over Chunk.text, for hybrid search
(retrieve.py). It uses Lucene's `english` analyzer: lowercases, drops stop words ("what", "the") and stems
("penalties" -> "penalti"), so the question's words match their other forms in the clauses.

Entities: each Entity node gets an `embedding` from a short "name card" (name, type, aliases and, for the
24 glossary entities, the definition), in the vector index `entity_embedding`. It lets a question find the
entities it is about directly, e.g. "Can a driver use Overtake behind the Safety Car?" -> overtake, safety car.
A card beat a card plus the entity's facts on the golden set: the facts pulled matches towards entities
that merely appear in many facts (e.g. "fine"). `graph entities` deletes all Entity nodes, so run
`embed entities` again after it.

LangChain pieces used here:
  FastEmbedEmbeddings            wrapper around the local fastembed model
  RecursiveCharacterTextSplitter splits on paragraph, then line, then sentence boundaries
  Neo4jVector.from_documents     embeds the texts, writes Chunk nodes, creates the vector index
  Neo4jVector.from_existing_graph
                                 embeds a property of nodes that already exist (here Entity.card), writes the
                                 vectors onto those nodes and creates the vector index

Run:  python -m f1rag.ingest.embed [chunks|keywords|entities]     (default: chunks, which also builds keywords)
"""

import argparse
import json
from functools import cache

from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_neo4j import Neo4jVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .. import config
from . import graph

INDEX_NAME = "chunk_embedding"
KEYWORD_INDEX_NAME = "chunk_fulltext"
ENTITY_INDEX_NAME = "entity_embedding"
CHUNK_CHARS = 1500
CHUNK_OVERLAP = 200


@cache  # create the model once and reuse it
def embeddings() -> FastEmbedEmbeddings:
    """The embedding model. Downloads it (~130 MB) on first use, then runs on CPU."""
    return FastEmbedEmbeddings(model_name=config.EMBED_MODEL)


def breadcrumb(provision: dict, provisions_by_id: dict) -> str:
    """Where a provision sits, e.g. "B1 Official Instructions > B1.6 Sanctions" (nearest parent last)."""
    crumbs = []
    parent_id = provision["parent"]
    while parent_id:
        parent = provisions_by_id[parent_id]
        crumbs.insert(0, f"{parent_id} {parent['title']}".strip())
        parent_id = parent["parent"]
    return " > ".join(crumbs)


def build_chunks() -> list[Document]:
    """One Document per chunk. The header (clause id and breadcrumb) is embedded with the text."""
    provisions = json.loads(config.PROVISIONS_FILE.read_text())
    provisions_by_id = {}
    for p in provisions:
        provisions_by_id[p["id"]] = p
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_CHARS, chunk_overlap=CHUNK_OVERLAP)

    docs = []
    for p in provisions:
        if p["level"] != "clause" or not p["text"].strip():
            continue
        header = f"{p['id']} ({breadcrumb(p, provisions_by_id)})"
        pieces = splitter.split_text(p["text"])
        for chunk_number, piece in enumerate(pieces):
            docs.append(Document(
                page_content=f"{header}\n{piece}",
                metadata={"clause_id": p["id"], "chunk": chunk_number},
            ))
    return docs


def load_chunks() -> None:
    """Embed every chunk, write them to Neo4j (replacing old ones) and link each to its clause."""
    docs = build_chunks()

    chunk_ids = []
    clause_ids = set()
    for d in docs:
        chunk_ids.append(f"{d.metadata['clause_id']}#{d.metadata['chunk']}")
        clause_ids.add(d.metadata["clause_id"])
    print(f"Embedding {len(docs)} chunks from {len(clause_ids)} clauses...")

    Neo4jVector.from_documents(
        docs,
        embeddings(),
        url=config.NEO4J_URI,
        username=config.NEO4J_USER,
        password=config.NEO4J_PASSWORD,
        database=config.NEO4J_DATABASE,
        index_name=INDEX_NAME,
        node_label="Chunk",
        ids=chunk_ids,
        pre_delete_collection=True,  # replace the old chunks and index
    )

    # Neo4jVector only writes the Chunk nodes; link each one to its clause.
    graph.run_query("""MATCH (ch:Chunk)
                       MATCH (c:Clause {id: ch.clause_id})
                       MERGE (ch)-[:CHUNK_OF]->(c)""")
    print(graph.run_query("MATCH (:Chunk)-[r:CHUNK_OF]->() RETURN count(r) AS chunk_of_edges")[0])
    load_keyword_index()


def load_keyword_index() -> None:
    """(Re)create the full-text index over the chunks' text, used by hybrid search.

    Plain Cypher rather than LangChain: Neo4jVector can create a full-text index, but not with a chosen
    analyzer (it would use Neo4j's default, which keeps stop words).
    """
    graph.run_query(f"DROP INDEX {KEYWORD_INDEX_NAME} IF EXISTS")
    graph.run_query(f"""CREATE FULLTEXT INDEX {KEYWORD_INDEX_NAME} FOR (c:Chunk) ON EACH [c.text]
                        OPTIONS {{indexConfig: {{`fulltext.analyzer`: 'english'}}}}""")
    graph.run_query("CALL db.awaitIndexes(300)")
    print(f"Full-text index {KEYWORD_INDEX_NAME} built over Chunk.text (english analyzer)")


def entity_card(entity: dict) -> str:
    """The text embedded for an entity, e.g.
    "pit lane (location). Also called: Pit Lane, pit lanes. Pit Lane: the area of the circuit ..."."""
    card = f"{entity['name']} ({entity['type'].lower()})"
    if entity["aliases"]:
        card += ". Also called: " + ", ".join(entity["aliases"])
    if entity["definition"]:
        card += ". " + " ".join(entity["definition"].split())
    return card


def load_entity_embeddings() -> None:
    """Write a name card onto every Entity node, then embed the cards into the entity_embedding index."""
    entities = graph.run_query("""MATCH (e:Entity)
                                  OPTIONAL MATCH (e)-[:IS_TERM]->(t:Term)
                                  RETURN e.name AS name, e.type AS type, e.aliases AS aliases,
                                         t.definition AS definition""")
    cards = []
    for e in entities:
        cards.append({"name": e["name"], "card": entity_card(e)})
    print(f"Embedding {len(cards)} entities, e.g. {cards[0]['card']!r}")

    # from_existing_graph only embeds nodes whose embedding is null, so clear the old vectors and index first.
    graph.run_query("""UNWIND $rows AS r
                       MATCH (e:Entity {name: r.name})
                       SET e.card = r.card
                       REMOVE e.embedding""", rows=cards)
    graph.run_query(f"DROP INDEX {ENTITY_INDEX_NAME} IF EXISTS")

    Neo4jVector.from_existing_graph(
        embeddings(),
        url=config.NEO4J_URI,
        username=config.NEO4J_USER,
        password=config.NEO4J_PASSWORD,
        database=config.NEO4J_DATABASE,
        node_label="Entity",
        text_node_properties=["card"],
        embedding_node_property="embedding",
        index_name=ENTITY_INDEX_NAME,
    )
    print(graph.run_query("MATCH (e:Entity) RETURN count(e.embedding) AS embedded, count(e) AS entities")[0])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed clauses or entities into Neo4j vector indexes.")
    parser.add_argument("what", nargs="?", choices=["chunks", "keywords", "entities"], default="chunks")
    what = parser.parse_args().what
    if what == "entities":
        load_entity_embeddings()
    elif what == "keywords":
        load_keyword_index()
    else:
        load_chunks()
