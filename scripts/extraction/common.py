"""Shared builder for the extraction batches (data/entities/extractions/<article>.json).

Each B<n>.py holds one article's extraction, written by hand against data/entities/vocab.json:
  MENTIONS = {clause_id: [entity names mentioned]}
  add_fact(clause_id, subject, RELATION, *objects, context="optional condition")   one call per fact
and ends with build("B<n>", MENTIONS), which checks everything against the vocabulary and
provisions.json, merges repeated facts (same triple + context) into one with all source ids,
and writes the JSON.

Run from this folder:  python3 B5.py   (or all: for a in $(seq 1 11); do python3 B$a.py; done)
"""

import json
import sys
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# Short names for entities the batch files use often.
SG = "stop-and-go penalty"
DT = "drive-through penalty"
S5 = "5-second penalty"
S10 = "10-second penalty"
LT = "lap time classified session"
TT = "total time classified session"
ISC = "international sporting code"
REGS = "fia f1 regulations"
SFC = "standard format competition"
AFC = "alternative format competition"

# Every fact added by add_fact(), as (subject, relation, object, clause_id, context).
FACTS = []


def add_fact(clause_id, subject, relation, *objects, context=None):
    """Record that `clause_id` states `subject relation object`, once per object."""
    for obj in objects:
        FACTS.append((subject, relation, obj, clause_id, context))


def clauses_to_extract(article, provisions):
    """The article's clauses (plus sections that have their own text), excluding appendix parts."""
    clause_ids = []
    for p in provisions:
        if "-part" in p["id"]:
            continue
        if p["id"].split(".")[0] != article:
            continue
        is_clause = p["level"] == "clause"
        is_section_with_text = p["level"] == "section" and p["text"].strip()
        if is_clause or is_section_with_text:
            clause_ids.append(p["id"])
    return clause_ids


def check(clause_ids, mentions, entity_names, relation_names):
    """Every problem with the mentions and facts, as a list of messages (empty means OK)."""
    errors = []
    for clause_id in clause_ids:
        if clause_id not in mentions:
            errors.append(f"missing clause {clause_id}")
    for clause_id in mentions:
        if clause_id not in clause_ids:
            errors.append(f"unknown clause {clause_id}")
    for clause_id, names in mentions.items():
        for name in names:
            if name not in entity_names:
                errors.append(f"{clause_id}: unknown entity {name!r}")

    for subject, relation, obj, clause_id, context in FACTS:
        if relation not in relation_names:
            errors.append(f"bad relation {relation}")
        if context is not None and not (isinstance(context, str) and context.strip()):
            errors.append(f"bad context {context!r}")
        if clause_id not in clause_ids:
            errors.append(f"relationship cites unknown clause {clause_id}")
        # Both ends of a fact must be mentioned in the clause that states it.
        for end in (subject, obj):
            if end not in mentions.get(clause_id, []):
                errors.append(f"{clause_id}: {subject} {relation} {obj} -> {end!r} not in clause mentions")
    return errors


def build(article, mentions):
    """Check the article's mentions and facts, then write data/entities/extractions/<article>.json."""
    with open(DATA_DIR / "entities" / "vocab.json") as f:
        vocab = json.load(f)
    with open(DATA_DIR / "parsed" / "provisions.json") as f:
        provisions = json.load(f)

    entity_names = set()
    for entity in vocab["entities"]:
        entity_names.add(entity["name"])
    relation_names = set(vocab["relation_types"])
    clause_ids = clauses_to_extract(article, provisions)

    errors = check(clause_ids, mentions, entity_names, relation_names)
    if errors:
        print(article, "ERRORS:\n" + "\n".join(errors))
        sys.exit(1)

    # Merge repeated facts (same subject, relation, object and context) into one with all their clauses.
    source_ids_by_fact = {}
    for subject, relation, obj, clause_id, context in FACTS:
        key = (subject, relation, obj, context)
        if key not in source_ids_by_fact:
            source_ids_by_fact[key] = []
        if clause_id not in source_ids_by_fact[key]:
            source_ids_by_fact[key].append(clause_id)

    mention_rows = []
    for clause_id in clause_ids:
        # Drop repeated names, keeping the first occurrence.
        unique_names = []
        for name in mentions[clause_id]:
            if name not in unique_names:
                unique_names.append(name)
        mention_rows.append({"clause_id": clause_id, "entities": unique_names})

    relationship_rows = []
    for (subject, relation, obj, context), source_ids in source_ids_by_fact.items():
        relationship_rows.append({"subject": subject, "relation": relation, "object": obj,
                                  "context": context, "source_ids": source_ids})

    output = {"article": article, "mentions": mention_rows, "relationships": relationship_rows}
    with open(DATA_DIR / "entities" / "extractions" / f"{article}.json", "w") as f:
        json.dump(output, f, indent=1, ensure_ascii=False)

    entity_counts = Counter()
    for row in mention_rows:
        for name in row["entities"]:
            entity_counts[name] += 1
    with_context = 0
    for row in relationship_rows:
        if row["context"]:
            with_context += 1
    print(f"{article}: clauses {len(clause_ids)}, mentions {sum(entity_counts.values())}, "
          f"entities {len(entity_counts)}, relationships {len(relationship_rows)} ({with_context} with context)")
