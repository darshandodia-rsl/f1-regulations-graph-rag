"""Compare retrieval (and optionally citations) with and without the graph.

Golden set: data/eval/golden_set.json, each question with `gold_clauses` (the clauses needed to answer it).

Retrieval modes, same vector search for the seeds in all of them:
  vector     seeds only                                  (retrieve(expand=False))
  structure  + breadcrumb, cited clauses, glossary       (retrieve(entities=False))
  graph      + entity facts and clauses sharing entities (retrieve(focus=None): the full expansion)
  focus8     graph, keeping only the 8 added clauses that best match the question's entities
             (retrieve(focus=8), Phase 5b)
  hybrid     focus8 with seeds from vector + keyword (full-text) search: the app's default
These all pass hybrid explicitly, so the first four keep vector-only seeds and stay comparable.

Retrieval metrics (no LLM calls), over the answerable questions:
  seed hit rate     a gold clause is among the k seeds
  seed MRR          1 / rank of the first gold seed (0 if none)
  seed recall/precision@k
  context recall    share of gold clauses whose text is in the context the model sees
                    ("text"), or that appear at all, also as a fact's source ("text+facts")
  context precision share of clauses with text in the context that are gold
The context is the formatted text from llm.format_context(), so the context budget is applied.

With --answers it also asks the model (one Groq call per question per mode) and scores:
  citation precision/recall   cited clause ids vs gold_clauses
  refusal                     on the unanswerable questions, whether the model set answerable=false

Run:  python -m f1rag.evaluation.evaluate [-k 5] [--answers] [--modes graph,focus8]
"""

import argparse
import json
import logging
import re
import time

from .. import config
from ..search.llm import Answer, answer, cited_ids, citation_ids, format_context
from ..search.retrieve import retrieve

GOLDEN_FILE = config.EVAL_DIR / "golden_set.json"
RESULTS_FILE = config.EVAL_DIR / "results.json"

# The options passed to retrieve() / answer() in each mode.
MODES = {
    "vector": {"expand": False, "hybrid": False},
    "structure": {"expand": True, "entities": False, "hybrid": False},
    "graph": {"expand": True, "entities": True, "focus": None, "hybrid": False},
    "focus8": {"expand": True, "entities": True, "focus": 8, "hybrid": False},
    "hybrid": {"expand": True, "entities": True, "focus": 8, "hybrid": True},
}

# A clause whose text is in the context starts a line with its id: "[B1.6.3] ..." (seeds, cited and
# shared clauses). Facts only mention ids at the end of the line.
TEXT_ID = re.compile(r"^\[((?:App)?B\d[\w.\-]*)\]", re.MULTILINE)

# Phrases that mean "the context doesn't say": "does not specify", "isn't mentioned", "no information", ...
def ratio(num: int, den: int) -> float | None:
    """num / den, or None when den is 0."""
    if den == 0:
        return None
    return num / den


def score_retrieval(question: dict, docs, context: str) -> dict:
    """Retrieval metrics for one question: how many gold clauses the seeds and the context contain."""
    gold = set(question["gold_clauses"])
    seeds = []
    for d in docs:
        seeds.append(d.metadata["id"])
    text_ids = set(TEXT_ID.findall(context))
    any_ids = set(cited_ids(context))

    # Rank (1-based) of the first seed that is a gold clause, or None.
    first_gold_rank = None
    for rank, seed in enumerate(seeds, start=1):
        if seed in gold:
            first_gold_rank = rank
            break

    if first_gold_rank is None:
        reciprocal_rank = 0.0
    else:
        reciprocal_rank = 1 / first_gold_rank

    gold_seeds = gold & set(seeds)
    return {
        "seeds": seeds,
        "seed_hit": first_gold_rank is not None,
        "seed_rr": reciprocal_rank,
        "seed_recall": ratio(len(gold_seeds), len(gold)),
        "seed_precision": ratio(len(gold_seeds), len(seeds)),
        "context_recall_text": ratio(len(gold & text_ids), len(gold)),
        "context_recall_any": ratio(len(gold & any_ids), len(gold)),
        "context_precision": ratio(len(gold & text_ids), len(text_ids)),
        "context_clauses": len(text_ids),
        "context_chars": len(context),
        "missing": sorted(gold - any_ids),
    }


def score_answer(question: dict, result: Answer) -> dict:
    """Answer metrics: citation precision/recall, or for unanswerable questions whether the model refused."""
    gold = set(question["gold_clauses"])
    cited = set(citation_ids(result))
    row = {"answer": result.answer, "cited": sorted(cited), "answerable": result.answerable}
    if gold:
        row["citation_precision"] = ratio(len(gold & cited), len(cited))
        row["citation_recall"] = ratio(len(gold & cited), len(gold))
    else:
        row["refused"] = not result.answerable
    return row


def mean(rows: list[dict], key: str) -> float | None:
    """Average of `key` over the rows that have a value for it."""
    values = []
    for row in rows:
        if row.get(key) is not None:
            values.append(row[key])
    if not values:
        return None
    return sum(values) / len(values)


def format_cell(value: float | None) -> str:
    """'-' for no value, two decimals for ratios (<= 1), whole numbers for counts."""
    if value is None:
        return "-"
    if value <= 1:
        return f"{value:.2f}"
    return f"{value:.0f}"


def summary_table(results: dict[str, list[dict]], keys: list[str]) -> str:
    """A text table with one row per metric and one column per mode."""
    header = f"{'metric':<22}"
    for mode in results:
        header += f"{mode:>11}"
    lines = [header]

    for key in keys:
        line = f"{key:<22}"
        for rows in results.values():
            line += f"{format_cell(mean(rows, key)):>11}"
        lines.append(line)
    return "\n".join(lines)


def main() -> None:
    """Run every golden question in every mode, print the summary and save per-question results."""
    logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)
    parser = argparse.ArgumentParser(description="Evaluate retrieval modes on the golden set.")
    parser.add_argument("-k", type=int, default=5, help="number of seed clauses")
    parser.add_argument("--answers", action="store_true", help="also generate answers (Groq) and score citations")
    parser.add_argument("--modes", default=",".join(MODES), help="comma-separated modes to run (default: all)")
    args = parser.parse_args()
    modes = {}
    for mode in args.modes.split(","):
        modes[mode] = MODES[mode]

    golden = json.loads(GOLDEN_FILE.read_text())
    results = {}
    for mode in modes:
        results[mode] = []

    for question in golden:
        for mode, options in modes.items():
            if args.answers:
                result, docs, context = answer(question["question"], k=args.k, **options)
            else:
                docs = retrieve(question["question"], k=args.k, **options)
                context = format_context(docs)

            row = {"id": question["id"], "type": question["type"]}
            if question["gold_clauses"]:
                row.update(score_retrieval(question, docs, context))
            if args.answers:
                row.update(score_answer(question, result))
                time.sleep(2)  # stay under Groq's per-minute token limit
            results[mode].append(row)
        print(f"  {question['id']} done")

    # Retrieval metrics only exist for answerable questions (those with gold clauses).
    answerable = {}
    for mode, rows in results.items():
        answerable[mode] = []
        for row in rows:
            if "seed_hit" in row:
                answerable[mode].append(row)

    retrieval_keys = ["seed_hit", "seed_rr", "seed_recall", "seed_precision", "context_recall_text",
                      "context_recall_any", "context_precision", "context_clauses", "context_chars"]
    print(f"\nRetrieval, {len(next(iter(answerable.values())))} answerable questions, k={args.k}\n")
    print(summary_table(answerable, retrieval_keys))

    print("\nGold clauses not reached (not even as a fact source):")
    for i, question in enumerate(golden):
        cells = []
        any_missing = False
        for mode in modes:
            missing = results[mode][i].get("missing")
            if missing:
                any_missing = True
                cells.append(f"{mode}: {','.join(missing)}")
            else:
                cells.append(f"{mode}: ok")
        if any_missing:
            print(f"  {question['id']} {question['type']:<13} " + "  ".join(cells))

    if args.answers:
        print("\nAnswers\n")
        print(summary_table(results, ["citation_precision", "citation_recall", "refused"]))

    output = {"k": args.k, "answers": args.answers, "results": results}
    RESULTS_FILE.write_text(json.dumps(output, indent=1))
    print(f"\nPer-question results: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
