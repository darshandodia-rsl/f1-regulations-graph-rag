"""Retrieval: vector search finds seed clauses, then the graph expands around them.

Why the graph: vector search only finds clauses whose wording is close to the question. The
answer often also needs clauses that read differently but are linked to those seeds: a clause
they cite, a glossary definition, or a rule elsewhere about the same thing (e.g. a question
about the Safety Car finds B5.13.1, but the Overtake rule for Safety Car periods is in B7.2.2).
The graph follows those links from each seed.

How it runs, step by step:
  1. The question is embedded (with bge's query instruction in front).
  2. Neo4jVector runs  CALL db.index.vector.queryNodes('chunk_embedding', k * 3, $vector)
     which yields the closest Chunk nodes as `node` plus a similarity `score`.
     With hybrid=True (the default) it also runs a keyword search,
       CALL db.index.fulltext.queryNodes('chunk_fulltext', $question)
     (Lucene BM25, english analyzer), scales each list's scores by its own best score (so each list's
     top hit scores 1.0), keeps each chunk's higher score and takes the top k * 3. Keywords catch what
     embeddings blur: clause ids ("B1.6.3"), session names ("SQ2"), amounts ("€1000"), document codes.
     The keyword search gets the plain question; only the vector gets bge's instruction.
  3. Our `retrieval_query` is appended to that call, so the expansion below runs inside the
     same Cypher query, once per seed chunk. Every field becomes part of the seed's metadata.

     a) Structural expansion (Phase 2 graph, built from the PDF's numbering, no LLM):
        Chunk -CHUNK_OF-> Clause                    the seed clause itself (`text`)
        Clause -PART_OF*-> Section/Article          where it sits (`path`, the breadcrumb)
        Clause -REFERENCES-> Provision              clauses/sections it cites (`references`)
        Clause <-REFERENCES- Clause                 clauses that cite it (`referenced_by`, ids only)
        Clause -USES_TERM-> Term                    glossary definitions (`terms`)

     b) Entity expansion (Phase 5 graph). Entities are the things the rules talk about
        ("safety car period", "overtake", "5-second penalty"). Each clause MENTIONS the
        entities in it, and entities are linked by typed relationships (SIGNALS,
        APPLIES_DURING, PUNISHABLE_BY, ...) that record which clauses state them (`source_ids`).
        Two fields are added per seed:

        `facts`: Clause -MENTIONS-> Entity -[fact]- Entity
            Short subject-relation-object statements about the seed's entities, taken from
            OTHER clauses, e.g. for seed B5.13.1:
                "overtaking APPLIES_DURING safety car period [B5.13.2]"
            They tell the model what the rest of the rulebook says about the things in the
            seed, without spending the space on whole clauses. Each fact keeps its source
            clause ids, so the model can cite them. Up to MAX_FACTS per seed.

        `shared`: Clause -MENTIONS-> Entity <-MENTIONS- Provision
            Whole provisions that mention the same entities as the seed, i.e. other rules
            about the same things. Each shared entity adds 1/mention_count to the weight,
            so sharing a rare entity counts for more than sharing a common one. For
            B5.13.1 the top one is B5.13.2 (shares "safety car period", "fia light panel",
            "safety car deployed message"). Up to MAX_SHARED per seed.

        Both only go through entities mentioned by at most HUB_CAP provisions. Hubs like
        "driver" or "f1 car" appear almost everywhere, so following them would link every
        clause to every other clause and fill the context with noise.
  4. Neo4jVector turns each row into a LangChain Document (text + metadata dict).
  5. retrieve() keeps the best chunk of each clause and returns the top k clauses.
     llm.format_context() then lays the seeds and everything in their metadata out for the model.

expand=False runs only the first line of 3a (vector search only).
entities=False keeps the structural expansion (3a) but skips the entity part (3b).
focus=N (default FOCUS = 8; needs expand and entities on) trims what 3a and 3b added, using the question's entities.
  The expansion starts from the seeds and never looks at the question, so this step makes it question-aware:
    1. match_entities finds the ENTITY_K entities whose name cards are closest to the question.
    2. Every clause the expansion added (cited clauses, shared-entity clauses, facts' source clauses) is
       ranked by how many of those entities it mentions, then by their summed scores.
    3. Only the top N clauses are kept. A fact stays if at least one of its source clauses is kept.
  Seeds, breadcrumbs and glossary terms are never trimmed.
Run:  python -m f1rag.search.retrieve "What happens if a driver ignores a red flag?" [--no-entities] [--no-expand]
      python -m f1rag.search.retrieve "..." [--focus N | --no-focus] [--no-hybrid]
      python -m f1rag.search.retrieve "..." --match-entities    (only the entities the question matches)
"""

import argparse
import logging
import textwrap
from functools import cache

from langchain_core.documents import Document
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain_neo4j.vectorstores.neo4j_vector import SearchType

from .. import config
from ..ingest.embed import ENTITY_INDEX_NAME, INDEX_NAME, KEYWORD_INDEX_NAME, embeddings

# bge models expect this instruction in front of search queries (not in front of documents).
# FastEmbedEmbeddings doesn't add it, so it is added here.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

VECTOR_ONLY_QUERY = """
MATCH (node)-[:CHUNK_OF]->(c:Clause)
RETURN c.text AS text, score, {id: c.id} AS metadata
ORDER BY score DESC
"""

# Entities mentioned by more provisions than this are hubs and are not used for expansion.
HUB_CAP = 12
ENTITY_K = 10       # question-matched entities used by focus
FOCUS = 8           # graph-added clauses kept by default (None keeps them all)
HYBRID = True       # seeds from vector + keyword search by default (False: vector only)
MAX_FACTS = 12      # entity facts per seed
MAX_SHARED = 3      # clauses sharing entities with each seed

# Facts are ranked first by how many of their ends (0-2) are non-hub entities the seed mentions,
# then by how rare those entities are.
ENTITY_FIELDS = """
  facts: COLLECT {
    MATCH (c)-[:MENTIONS]->(e:Entity)-[r]-(:Entity)
    WHERE e.mention_count <= $hub_cap AND any(s IN r.source_ids WHERE s <> c.id)
    WITH r, count(DISTINCT e) AS ends_in_seed, min(e.mention_count) AS rarity
    ORDER BY ends_in_seed DESC, rarity, type(r), startNode(r).name, endNode(r).name
    LIMIT $max_facts
    RETURN {subject: startNode(r).name, relation: type(r), object: endNode(r).name,
            context: r.context, source_ids: r.source_ids}
  },
  shared: COLLECT {
    MATCH (c)-[:MENTIONS]->(e:Entity)<-[:MENTIONS]-(x:Provision)
    WHERE e.mention_count <= $hub_cap AND x <> c
    WITH x, sum(1.0 / e.mention_count) AS weight, collect(e.name) AS via
    ORDER BY weight DESC, x.id
    LIMIT $max_shared
    RETURN x {.id, .title, .text, via: via, weight: round(weight, 3)}
  },"""

# The /*ENTITY_FIELDS*/ marker is replaced by ENTITY_FIELDS, or removed when entities are off.
GRAPH_QUERY = """
MATCH (node)-[:CHUNK_OF]->(c:Clause)
RETURN c.text AS text, score, {
  id: c.id,/*ENTITY_FIELDS*/
  path: COLLECT {
    MATCH hops = (c)-[:PART_OF*]->(a)
    RETURN trim(a.id + ' ' + a.title) ORDER BY length(hops) DESC
  },
  references: COLLECT {
    MATCH (c)-[:REFERENCES]->(r:Provision)
    RETURN r {.id, .title, .text, .level,
              clauses: COLLECT { MATCH (x:Clause)-[:PART_OF]->(r) RETURN x.id ORDER BY x.id }}
    ORDER BY r.id
  },
  referenced_by: COLLECT { MATCH (x:Clause)-[:REFERENCES]->(c) RETURN x.id ORDER BY x.id },
  terms: COLLECT {
    MATCH (c)-[:USES_TERM]->(t:Term) RETURN t {.name, .abbreviation, .definition} ORDER BY t.name
  }
} AS metadata
ORDER BY score DESC
"""


def _retrieval_query(expand: bool, entities: bool) -> str:
    """The Cypher that runs after the vector search, for the chosen mode."""
    if not expand:
        return VECTOR_ONLY_QUERY
    if entities:
        return GRAPH_QUERY.replace("/*ENTITY_FIELDS*/", ENTITY_FIELDS)
    return GRAPH_QUERY.replace("/*ENTITY_FIELDS*/", "")


@cache  # one connection pool for every mode
def _graph() -> Neo4jGraph:
    """The Neo4j connection the stores share.

    AuraDB closes connections that sit idle, and a long-running `f1rag serve` would then send its next
    query down a dead one (a read timeout, then IncompleteCommit). liveness_check_timeout makes the
    driver ping a pooled connection that has been idle for over 30 s before reusing it, and open a
    fresh one if the ping fails. refresh_schema=False skips Neo4jGraph's schema scan, which isn't needed.
    """
    return Neo4jGraph(
        url=config.NEO4J_URI,
        username=config.NEO4J_USER,
        password=config.NEO4J_PASSWORD,
        database=config.NEO4J_DATABASE,
        refresh_schema=False,
        driver_config={"liveness_check_timeout": 30},
    )


@cache  # create one store per mode and reuse it
def _store(expand: bool, entities: bool, hybrid: bool) -> Neo4jVector:
    """A Neo4jVector over the existing chunk index (plus the keyword index when hybrid), using the
    retrieval query for this mode."""
    if hybrid:
        search = {"search_type": SearchType.HYBRID, "keyword_index_name": KEYWORD_INDEX_NAME}
    else:
        search = {"search_type": SearchType.VECTOR}
    return Neo4jVector.from_existing_index(
        embeddings(),
        graph=_graph(),
        index_name=INDEX_NAME,
        retrieval_query=_retrieval_query(expand, entities),
        **search,
    )


# Each entity hit comes back as a Document whose text is the entity's name card.
ENTITY_MATCH_QUERY = """
RETURN node.card AS text, score, {name: node.name, type: node.type, mention_count: node.mention_count} AS metadata
ORDER BY score DESC
"""


@cache
def _entity_store() -> Neo4jVector:
    """A Neo4jVector over the entity_embedding index (Entity nodes' name cards, see ingest/embed.py)."""
    return Neo4jVector.from_existing_index(
        embeddings(),
        graph=_graph(),
        index_name=ENTITY_INDEX_NAME,
        retrieval_query=ENTITY_MATCH_QUERY,
    )


def match_entities(question: str, k: int = 10) -> list[Document]:
    """The k entities whose name cards are closest to the question, best first (score in metadata)."""
    hits = _entity_store().similarity_search_with_score(QUERY_PREFIX + question, k=k)
    entities = []
    for doc, score in hits:
        doc.metadata["score"] = round(score, 4)
        entities.append(doc)
    return entities


def _focus(question: str, docs: list[Document], keep: int) -> None:
    """Prune unfocused graph-expanded context so only the `keep` companion clauses most
    relevant to the user's specific question remain in `docs` metadata (mutates in place).
    """
    # 1. Identify which graph entities the user's question is actually asking about.
    matched = {}
    for e in match_entities(question, k=ENTITY_K):
        matched[e.metadata["name"]] = e.metadata["score"]

    # 2. Gather all external rules pulled in by 1-hop/2-hop graph expansion across all seed docs.
    # Exclude primary seed clauses (seed_ids) so top vector/keyword hits are never pruned.
    seed_ids = {d.metadata["id"] for d in docs}
    candidates = set()
    for d in docs:
        m = d.metadata
        candidates.update(r["id"] for r in m.get("references", []))
        candidates.update(x["id"] for x in m.get("shared", []))
        for fact in m.get("facts", []):
            candidates.update(fact["source_ids"])
    candidates -= seed_ids

    # 3. Intersect graph-expanded candidate rules with the entities matched from the question.
    # Candidate rules that mention zero question entities are naturally dropped here.
    rows = _graph().query("""MATCH (p:Provision)-[:MENTIONS]->(e:Entity)
                             WHERE p.id IN $ids AND e.name IN $names
                             RETURN p.id AS id, collect(e.name) AS names""",
                          params={"ids": sorted(candidates), "names": list(matched)})

    # 4. Rank surviving candidates by multi-concept coverage first (-len(scores)), using
    # cumulative entity similarity (-sum(scores)) and clause ID as tie-breakers.
    ranked = []
    for row in rows:
        scores = [matched[name] for name in row["names"]]
        ranked.append((-len(scores), -sum(scores), row["id"]))
    kept = {clause_id for _, _, clause_id in sorted(ranked)[:keep]}

    # 5. Strip unkept references, sister rules, and unsupported facts from each document's metadata
    # so the LLM prompt stays focused and free of tangential graph noise.
    for d in docs:
        m = d.metadata
        m["references"] = [r for r in m.get("references", []) if r["id"] in kept]
        m["shared"] = [x for x in m.get("shared", []) if x["id"] in kept]
        m["facts"] = [f for f in m.get("facts", []) if kept & set(f["source_ids"])]


def retrieve(question: str, k: int = 5, expand: bool = True, entities: bool = True,
             focus: int | None = FOCUS, hybrid: bool = HYBRID) -> list[Document]:
    """The k best-matching clauses (with graph context when expand=True), best first.

    focus=N keeps only the N graph-added clauses that best match the question's entities (see _focus);
    focus=None keeps the full expansion. hybrid=False finds the seeds by vector search alone.
    """
    params = {"hub_cap": HUB_CAP, "max_facts": MAX_FACTS, "max_shared": MAX_SHARED}
    # Long clauses have several chunks, so fetch extra and keep only each clause's best chunk.
    # Embed here rather than in similarity_search_with_score, which would also send bge's instruction to the
    # keyword search: the vector gets the instruction, the keyword search (query=) the plain question.
    vector = embeddings().embed_query(QUERY_PREFIX + question)
    hits = _store(expand, entities, hybrid).similarity_search_with_score_by_vector(
        vector, k=k * 3, params=params, query=question)

    seen_ids = set()
    docs = []
    for doc, score in hits:
        if doc.metadata["id"] in seen_ids:
            continue
        seen_ids.add(doc.metadata["id"])
        doc.metadata["score"] = round(score, 4)
        docs.append(doc)
    docs = docs[:k]
    if focus is not None and expand and entities:
        _focus(question, docs, focus)
    return docs


def fact_line(fact: dict) -> str:
    """One entity fact as text, e.g. 'unsafe release PUNISHABLE_BY fine (during a TTCS ...) [B1.6.2]'."""
    if fact["context"]:
        context = f" ({fact['context']})"
    else:
        context = ""
    cites = ""
    for source_id in fact["source_ids"]:
        cites += f"[{source_id}]"
    return f"{fact['subject']} {fact['relation']} {fact['object']}{context} {cites}"


def short(text: str, width: int = 300) -> str:
    """Put the text on one line and cut it to `width` characters."""
    return textwrap.shorten(" ".join(text.split()), width=width, placeholder=" ...")


def show(docs: list[Document]) -> None:
    """Print what retrieval found, so you can see what the graph added."""
    for n, doc in enumerate(docs, start=1):
        m = doc.metadata
        print(f"\n[{n}] {m['id']}  score={m['score']}")
        if m.get("path"):
            print(f"    in: {' > '.join(m['path'])}")
        print(textwrap.indent(short(doc.page_content, 500), "    "))

        for ref in m.get("references", []):
            if ref["text"]:
                body = short(ref["text"], 200)
            else:
                body = f"({ref['level']} with clauses {', '.join(ref['clauses'])})"
            print(f"    -> cites {ref['id']} {ref['title']}: {body}")
        if m.get("referenced_by"):
            print(f"    <- cited by: {', '.join(m['referenced_by'])}")
        for term in m.get("terms", []):
            print(f"    term {term['name']}: {short(term['definition'], 150)}")
        for other in m.get("shared", []):
            print(f"    ~ shares {', '.join(other['via'])} with {other['id']} (weight {other['weight']}): "
                  f"{short(other['text'], 150)}")
        for fact in m.get("facts", []):
            print(f"    * {fact_line(fact)}")


def main() -> None:
    """Retrieve for one question from the command line and print the result."""
    # Hide Neo4j's deprecation notice for db.index.vector.queryNodes, printed on every query (as cli.py does).
    logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)
    parser = argparse.ArgumentParser(description="Show what GraphRAG retrieval finds for a question.")
    parser.add_argument("question")
    parser.add_argument("-k", type=int, default=5, help="number of seed clauses")
    parser.add_argument("--no-expand", action="store_true", help="vector search only, no graph")
    parser.add_argument("--no-entities", action="store_true", help="structural graph only, no entity expansion")
    parser.add_argument("--focus", type=int, default=FOCUS, help=f"graph-added clauses to keep (default {FOCUS})")
    parser.add_argument("--no-focus", action="store_true", help="keep the full graph expansion")
    parser.add_argument("--no-hybrid", action="store_true", help="seeds from vector search only (no keyword search)")
    parser.add_argument("--match-entities", action="store_true", help="only list the entities the question matches")
    args = parser.parse_args()
    if args.match_entities:
        for e in match_entities(args.question):
            m = e.metadata
            print(f"{m['score']:.4f}  {m['name']} ({m['type'].lower()}, {m['mention_count']} mentions)")
        return
    docs = retrieve(args.question, k=args.k, expand=not args.no_expand, entities=not args.no_entities,
                    focus=None if args.no_focus else args.focus, hybrid=not args.no_hybrid)
    show(docs)


if __name__ == "__main__":
    main()
