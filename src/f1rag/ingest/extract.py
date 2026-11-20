"""Validate the entity/relationship extractions before they go into Neo4j.

The extractions are JSON files written against a fixed vocabulary:
  data/entities/vocab.json               entity types, a closed list of relation types, canonical entities with aliases
  data/entities/extractions/<B1..>.json  one batch per article:
      {"article": "B1",
       "mentions":      [{"clause_id": "B1.6.3", "entities": ["pit lane", "steward", ...]}],
       "relationships": [{"subject": "pit lane speeding", "relation": "PUNISHABLE_BY", "object": "fine",
                          "context": "during free practice ...", "source_ids": ["B1.6.3"]}]}

The Pydantic models check each file's shape. validate() then checks the batches against the vocabulary and
provisions.json: known clause ids, known entities and relations, and that both ends of every relationship
are mentioned in every clause it cites (so each edge can be traced back to the text).

Run:  python -m f1rag.ingest.extract
"""

import json
from collections import Counter

from pydantic import BaseModel, Field, field_validator

from .. import config



class Entity(BaseModel):
    """A canonical entity from the vocabulary."""
    name: str
    type: str
    aliases: list[str] = []
    glossary_term: str | None = None

    @field_validator("name")
    @classmethod
    def lowercase_name(cls, value: str) -> str:
        """Canonical names must be lowercase."""
        if value != value.lower():
            raise ValueError(f"canonical name must be lowercase: {value!r}")
        return value


class Vocab(BaseModel):
    """The whole vocabulary file."""
    entity_types: dict[str, str]
    relation_types: dict[str, str]
    entities: list[Entity]


class Mention(BaseModel):
    """The entities one clause mentions."""
    clause_id: str
    entities: list[str] = Field(min_length=1)


class Relationship(BaseModel):
    """One fact: subject -relation-> object, with an optional condition and the clauses that state it."""
    subject: str
    relation: str
    object: str
    context: str | None = None
    source_ids: list[str] = Field(min_length=1)

    @field_validator("context")
    @classmethod
    def no_blank_context(cls, value: str | None) -> str | None:
        """Context is either missing (None) or real text, never an empty string."""
        if value is not None and not value.strip():
            raise ValueError("context must be null or non-empty")
        return value


class Batch(BaseModel):
    """One article's extraction file."""
    article: str
    mentions: list[Mention]
    relationships: list[Relationship]


def load_vocab() -> Vocab:
    """Read and shape-check data/entities/vocab.json."""
    return Vocab.model_validate_json(config.VOCAB_FILE.read_text())


def article_number(path) -> int:
    """B11.json -> 11, so the batches sort as B1, B2, ..., B11 rather than B1, B10, B11, B2."""
    return int(path.stem[1:])


def load_batches() -> list[Batch]:
    """Read and shape-check every data/entities/extractions/B*.json, in article order."""
    files = sorted(config.EXTRACTIONS_DIR.glob("B*.json"), key=article_number)
    batches = []
    for f in files:
        batches.append(Batch.model_validate_json(f.read_text()))
    return batches


def validate(vocab: Vocab, batches: list[Batch]) -> list[str]:
    """Cross-file checks. Returns a list of problems (empty means OK)."""
    provision_ids = set()
    for p in json.loads(config.PROVISIONS_FILE.read_text()):
        provision_ids.add(p["id"])
    term_names = set()
    for t in json.loads(config.TERMS_FILE.read_text()):
        term_names.add(t["term"])
    entity_names = set()
    for e in vocab.entities:
        entity_names.add(e.name)

    errors = []

    # Vocabulary: no duplicate names, known types, known glossary terms.
    name_counts = Counter()
    for e in vocab.entities:
        name_counts[e.name] += 1
    for name, count in name_counts.items():
        if count > 1:
            errors.append(f"vocab: duplicate entity {name!r}")
    for e in vocab.entities:
        if e.type not in vocab.entity_types:
            errors.append(f"vocab: {e.name!r} has unknown type {e.type}")
        if e.glossary_term and e.glossary_term not in term_names:
            errors.append(f"vocab: {e.name!r} links to unknown glossary term {e.glossary_term!r}")

    # Batches: known clauses and entities, each clause listed once, relationships traceable to their clauses.
    seen_clauses = set()
    for batch in batches:
        mentioned_in = {}  # clause id -> set of entity names it mentions
        for mention in batch.mentions:
            if mention.clause_id not in provision_ids:
                errors.append(f"{batch.article}: unknown clause {mention.clause_id}")
            if mention.clause_id in seen_clauses:
                errors.append(f"{batch.article}: clause {mention.clause_id} appears in more than one mention entry")
            seen_clauses.add(mention.clause_id)
            for name in mention.entities:
                if name not in entity_names:
                    errors.append(f"{batch.article}/{mention.clause_id}: unknown entity {name!r}")
            mentioned_in[mention.clause_id] = set(mention.entities)

        for rel in batch.relationships:
            label = f"{batch.article}: {rel.subject} {rel.relation} {rel.object}"
            if rel.relation not in vocab.relation_types:
                errors.append(f"{label}: unknown relation")
            for clause_id in rel.source_ids:
                clause_entities = mentioned_in.get(clause_id, set())
                missing = {rel.subject, rel.object} - clause_entities
                if missing:
                    errors.append(f"{label}: {sorted(missing)} not mentioned in source clause {clause_id}")
    return errors


def main() -> None:
    """Validate all batches, print counts and any problems."""
    vocab = load_vocab()
    batches = load_batches()
    errors = validate(vocab, batches)

    n_clauses = 0
    n_mentions = 0
    n_relationships = 0
    for batch in batches:
        n_clauses += len(batch.mentions)
        n_relationships += len(batch.relationships)
        for mention in batch.mentions:
            n_mentions += len(mention.entities)
    print(f"{len(batches)} batches, {n_clauses} clauses, {n_mentions} mentions, {n_relationships} relationships")

    if errors:
        print(f"{len(errors)} problem(s):")
        for error in errors:
            print("  " + error)
        raise SystemExit(1)
    print("OK")


if __name__ == "__main__":
    main()
