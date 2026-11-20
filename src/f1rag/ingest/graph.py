"""Load the parsed regulations into Neo4j.

Running example: clause B1.6.3 "Driving in the Pit Entry Road, Pit Lane And Pit Exit Road" (the 80 km/h
pit lane speed limit). Its text includes "ii. In accordance with Article B1.9.3 the stewards may impose an
additional penalty..." and "iii. During a TTCS, the stewards may impose either a 5-Second Penalty...".

  load_structure()  provisions, hierarchy, cross-references and glossary terms (no LLM, no embeddings)
    (:Provision:Article|Section|Clause {id, title, text, ...})   (:Provision:Clause {id: 'B1.6.3', ...})
    (clause)-[:PART_OF]->(section)-[:PART_OF]->(article)         (B1.6.3)-[:PART_OF]->(B1.6)-[:PART_OF]->(B1)
    (provision)-[:REFERENCES]->(provision)                       (B1.6.3)-[:REFERENCES]->(B1.9.3)
    (provision)-[:USES_TERM]->(:Term)                            (B1.6.3)-[:USES_TERM]->(:Term {name: 'Pit Lane'})

  embed.py adds a Chunk layer on top:
    (:Chunk {id, clause_id, text, embedding})-[:CHUNK_OF]->(:Clause)   + vector index chunk_embedding
                                                                 (B1.6.3#0), (B1.6.3#1) -[:CHUNK_OF]->(B1.6.3)

  load_entities()  the validated extractions in data/entities/extractions/ (see extract.py)
    (:Entity:<Type> {name, type, aliases, mention_count})        (:Entity:Infringement {name: 'pit lane speeding'})
    (provision)-[:MENTIONS]->(entity)                            (B1.6.3)-[:MENTIONS]->(pit lane speeding)
    (entity)-[:IS_TERM]->(:Term)                                 (pit lane)-[:IS_TERM]->(:Term {name: 'Pit Lane'})
    (entity)-[:<RELATION> {context, source_ids}]->(entity)       (pit lane speeding)-[:PUNISHABLE_BY
                                                                 {context: 'during a TTCS', source_ids: ['B1.6.3']}]
                                                                 ->(5-second penalty)

Run:  python -m f1rag.ingest.graph structure [--reset]   |   python -m f1rag.ingest.graph entities   |   python -m f1rag.ingest.graph stats

Open Neo4j Browser and try:  MATCH p=(:Clause {id:'B1.6.3'})-[*1..2]-() RETURN p
"""

import argparse
import json
import re

from neo4j import Driver, GraphDatabase

from .. import config
from . import extract

# "B1.9.3" or "B1.6.2c" in the text, but not the "B1" in "Appendix B1".
REF_RE = re.compile(r"(?<!Appendix )\b(B\d+(?:\.\d+){0,2})[a-z]?\b")
APPENDIX_REF_RE = re.compile(r"\bAppendix (B\d+)\b")


def driver() -> Driver:
    """A new Neo4j driver for the configured database."""
    return GraphDatabase.driver(config.NEO4J_URI, auth=(config.NEO4J_USER, config.NEO4J_PASSWORD))


def run_query(cypher: str, **params) -> list[dict]:
    """Run one Cypher query and return its rows as dicts."""
    with driver() as d:
        records, _, _ = d.execute_query(cypher, params, database_=config.NEO4J_DATABASE)
        rows = []
        for record in records:
            rows.append(record.data())
        return rows


# ---------------------------------------------------------------------------------------------
# Helpers that compute edges in Python before writing them
# ---------------------------------------------------------------------------------------------

def find_references(provision: dict, known_ids: set[str]) -> set[str]:
    """The provisions this one refers to. 'Article B1.6.2c' resolves to B1.6.2 (the most specific id that exists).

    B1.6.3 ("In accordance with Article B1.9.3 ...") -> {'B1.9.3'}
    """
    found = set()
    for raw in REF_RE.findall(provision["text"]):
        # Drop the last ".part" until the id exists: B1.6.9 -> B1.6 -> B1.
        candidate = raw
        while candidate and candidate not in known_ids:
            candidate = candidate.rpartition(".")[0]
        if candidate:
            found.add(candidate)

    for appendix in APPENDIX_REF_RE.findall(provision["text"]):
        if "App" + appendix in known_ids:
            found.add("App" + appendix)

    # Don't link a provision to itself or to its own ancestors (B1.6.3 mentioning "B1.6").
    # Compare on "." boundaries: B11.4.10 is not a descendant of B11.4.1.
    references = set()
    for ref in found:
        is_self = provision["id"] == ref
        is_ancestor = provision["id"].startswith(ref + ".")
        if not is_self and not is_ancestor:
            references.add(ref)
    return references


def find_terms(provision: dict, terms: list[dict]) -> list[str]:
    """The glossary terms whose name or abbreviation appears in the provision's text.

    B1.6.3 -> ['Fast Lane', 'Lap Time Classified Session', 'Pit Exit Road', 'Pit Lane',
               'Total Time Classified Session']   (the last one matched by its abbreviation "TTCS")
    """
    text = provision["text"]
    hits = []
    for t in terms:
        name = t["term"].removesuffix("(s)")
        name_found = re.search(rf"\b{re.escape(name)}", text, re.IGNORECASE)
        abbreviation_found = t["abbreviation"] and re.search(rf"\b{re.escape(t['abbreviation'])}\b", text)
        if name_found or abbreviation_found:
            hits.append(t["term"])
    return hits


# ---------------------------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------------------------

# Uniqueness constraints (these also create an index, so MERGE/MATCH by id is fast).
STRUCTURE_SCHEMA = [
    "CREATE CONSTRAINT provision_id IF NOT EXISTS FOR (p:Provision) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT term_name IF NOT EXISTS FOR (t:Term) REQUIRE t.name IS UNIQUE",
]


def load_structure(reset: bool = False) -> None:
    """Load provisions, hierarchy, cross-references and glossary terms.

    reset=True wipes the whole database first. Otherwise provisions and terms no longer in the files are
    removed and all structural edges are rebuilt, leaving chunks and entities alone.
    """
    provisions = json.loads(config.PROVISIONS_FILE.read_text())
    terms = json.loads(config.TERMS_FILE.read_text())
    known_ids = set()
    for p in provisions:
        known_ids.add(p["id"])
    term_names = []
    for t in terms:
        term_names.append(t["term"])

    with driver() as d:
        d.verify_connectivity()

        def q(cypher: str, **params):
            d.execute_query(cypher, params, database_=config.NEO4J_DATABASE)

        if reset:
            print("Clearing database...")
            q("MATCH (n) DETACH DELETE n")
        else:
            q("MATCH (p:Provision) WHERE NOT p.id IN $ids DETACH DELETE p", ids=list(known_ids))
            q("MATCH (t:Term) WHERE NOT t.name IN $names DETACH DELETE t", names=term_names)
            q("MATCH (:Provision)-[r:PART_OF|REFERENCES|USES_TERM]->() DELETE r")
            q("MATCH (p:Provision) REMOVE p:Article:Section:Clause")
        for statement in STRUCTURE_SCHEMA:
            q(statement)

        # --- Provisions + hierarchy ------------------------------------------------------------
        # B1.6.3 becomes (:Provision:Clause {id: 'B1.6.3', parent: 'B1.6', ...})-[:PART_OF]->(B1.6).
        q(
            """UNWIND $rows AS r
               MERGE (p:Provision {id: r.id})
               SET p.level = r.level, p.title = r.title, p.text = r.text, p.parent = r.parent,
                   p.advisory_committee = r.advisory_committee, p.governance = r.governance""",
            rows=provisions,
        )
        # Labels can't be parameters in Cypher, so one statement per level.
        for level, label in [("article", "Article"), ("section", "Section"), ("clause", "Clause")]:
            q(f"MATCH (p:Provision {{level: $level}}) SET p:{label}", level=level)
        q("""MATCH (c:Provision) WHERE c.parent IS NOT NULL
             MATCH (parent:Provision {id: c.parent})
             MERGE (c)-[:PART_OF]->(parent)""")

        # --- Cross references ------------------------------------------------------------------
        # B1.6.3 adds the row {"src": "B1.6.3", "dst": "B1.9.3"}.
        refs = []
        for p in provisions:
            for target in find_references(p, known_ids):
                refs.append({"src": p["id"], "dst": target})
        q("""UNWIND $refs AS x
             MATCH (a:Provision {id: x.src}), (b:Provision {id: x.dst})
             MERGE (a)-[:REFERENCES]->(b)""", refs=refs)
        print(f"  {len(provisions)} provisions, {len(refs)} cross-references")

        # --- Glossary terms --------------------------------------------------------------------
        # B1.6.3 adds rows like {"pid": "B1.6.3", "term": "Pit Lane"}.
        q("""UNWIND $terms AS t
             MERGE (x:Term {name: t.term})
             SET x.abbreviation = t.abbreviation, x.definition = t.definition""", terms=terms)
        uses = []
        for p in provisions:
            for term in find_terms(p, terms):
                uses.append({"pid": p["id"], "term": term})
        q("""UNWIND $uses AS u
             MATCH (p:Provision {id: u.pid}), (t:Term {name: u.term})
             MERGE (p)-[:USES_TERM]->(t)""", uses=uses)
        print(f"  {len(terms)} terms, {len(uses)} term usages")


def load_entities() -> None:
    """Load entities, MENTIONS, IS_TERM and the typed relationships between entities.

    Validates the batches first and refuses to load if anything is wrong. Existing Entity nodes (and all
    their edges) are deleted first, so re-running gives the same graph. Provisions, terms and chunks are untouched.
    """
    vocab = extract.load_vocab()
    batches = extract.load_batches()
    errors = extract.validate(vocab, batches)
    if errors:
        raise ValueError(f"{len(errors)} extraction problem(s), first: {errors[0]} (run python -m f1rag.ingest.extract)")

    entities = []
    for e in vocab.entities:
        entities.append(e.model_dump())
    # From B1.6.3: mention rows like {"pid": "B1.6.3", "name": "pit lane speeding"}, and relationship rows like
    # {"subject": "pit lane speeding", "relation": "PUNISHABLE_BY", "object": "5-second penalty",
    #  "context": "during a TTCS", "source_ids": ["B1.6.3"]}.
    mentions = []
    relationships = []
    for batch in batches:
        for mention in batch.mentions:
            for name in mention.entities:
                mentions.append({"pid": mention.clause_id, "name": name})
        for rel in batch.relationships:
            relationships.append(rel.model_dump())
    # Entities tied to a glossary term, e.g. "pit lane" (glossary_term "Pit Lane").
    glossary_links = []
    for e in entities:
        if e["glossary_term"]:
            glossary_links.append(e)

    with driver() as d:
        d.verify_connectivity()

        def q(cypher: str, **params):
            d.execute_query(cypher, params, database_=config.NEO4J_DATABASE)

        q("MATCH (e:Entity) DETACH DELETE e")
        q("CREATE CONSTRAINT entity_name IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")

        q("""UNWIND $rows AS r
             CREATE (e:Entity {name: r.name, type: r.type, aliases: r.aliases})""", rows=entities)
        # A second label per type (INFRINGEMENT -> :Infringement for "pit lane speeding") so Browser colours them
        # and queries can say (:Penalty).
        for entity_type in vocab.entity_types:
            q(f"MATCH (e:Entity {{type: $t}}) SET e:{entity_type.title()}", t=entity_type)

        q("""UNWIND $rows AS r
             MATCH (p:Provision {id: r.pid}), (e:Entity {name: r.name})
             MERGE (p)-[:MENTIONS]->(e)""", rows=mentions)
        # How many provisions mention each entity; retrieval uses this to skip hubs. "pit lane speeding" gets 1
        # (only B1.6.3), "pit lane" 77 and "driver" 125.
        q("""MATCH (e:Entity)
             SET e.mention_count = COUNT { (:Provision)-[:MENTIONS]->(e) }""")

        q("""UNWIND $rows AS r
             MATCH (e:Entity {name: r.name}), (t:Term {name: r.glossary_term})
             MERGE (e)-[:IS_TERM]->(t)""", rows=glossary_links)

        # Relationship types can't be parameters in Cypher, so one statement per type (the names come from
        # the validated closed list, so formatting them in is safe). CREATE, not MERGE: the same triple
        # with a different context is a separate edge. The B1.6.3 row above becomes
        # (pit lane speeding)-[:PUNISHABLE_BY {context: 'during a TTCS', source_ids: ['B1.6.3']}]->(5-second penalty).
        for rel_type in vocab.relation_types:
            rows = []
            for rel in relationships:
                if rel["relation"] == rel_type:
                    rows.append(rel)
            q(f"""UNWIND $rows AS r
                  MATCH (s:Entity {{name: r.subject}}), (o:Entity {{name: r.object}})
                  CREATE (s)-[:{rel_type} {{context: r.context, source_ids: r.source_ids}}]->(o)""", rows=rows)

        print(f"  {len(entities)} entities, {len(mentions)} mentions, {len(relationships)} relationships")


def stats() -> list[dict]:
    """Node counts per label and relationship counts per type."""
    nodes = run_query("MATCH (n) UNWIND labels(n) AS kind RETURN kind, count(*) AS count ORDER BY kind")
    rels = run_query("MATCH ()-[r]->() RETURN '-[' + type(r) + ']->' AS kind, count(*) AS count ORDER BY kind")
    return nodes + rels


def main() -> None:
    """Load the structure or the entities (or neither, for `stats`), then print the graph counts."""
    parser = argparse.ArgumentParser(description="Load the regulations graph into Neo4j.")
    parser.add_argument("what", choices=["structure", "entities", "stats"])
    parser.add_argument("--reset", action="store_true", help="structure only: wipe the whole database first")
    args = parser.parse_args()
    if args.what == "structure":
        load_structure(reset=args.reset)
    elif args.what == "entities":
        load_entities()
    for row in stats():
        print(f"  {row['kind']:<20} {row['count']}")


if __name__ == "__main__":
    main()
