"""Command line entry point.

  f1rag ask "What happens if a driver ignores a red flag?" [-k 5] [--no-expand] [--no-entities] [--no-focus] [--show-context]
  f1rag serve [--port 8000]      the web page and its search API (api.py)

`ask` prints the answer, then the clauses it cites with their text (the relevant clauses).
"""

import argparse
import json
import logging
import textwrap
from functools import cache

from . import config
from .search.llm import Answer, answer, check_citations
from .search.retrieve import FOCUS


@cache  # read the file once
def provisions() -> dict[str, dict]:
    """Every provision from Phase 1, by id."""
    items = json.loads(config.PROVISIONS_FILE.read_text())
    return {p["id"]: p for p in items}


def breadcrumb(clause_id: str) -> str:
    """Where a provision sits, e.g. 'B1 ORGANISATION OF A COMPETITION > B1.6 Penalties'."""
    by_id = provisions()
    crumbs = []
    parent = by_id[clause_id]["parent"]
    while parent:
        crumbs.insert(0, f"{parent} {by_id[parent]['title']}".strip())
        parent = by_id[parent]["parent"]
    return " > ".join(crumbs)


def print_answer(result: Answer, context: str, show_context: bool) -> None:
    """Print the answer, then each cited clause with its text."""
    if show_context:
        print(f"\n--- context ({len(context)} chars) ---\n{context}\n--- end context ---")
    print(f"\n{result.answer}\n")
    if not result.answerable:
        print("(The model found no answer in the retrieved clauses.)\n")

    found, unknown = check_citations(result, context)
    if not found:
        print("Citations: none")
    else:
        print("Citations:")
        for clause_id in found:
            p = provisions().get(clause_id)
            if p is None:
                print(f"\n[{clause_id}]")
                continue
            print(f"\n[{clause_id}] {breadcrumb(clause_id)}")
            body = p["text"] or p["title"]
            print(textwrap.indent(textwrap.fill(" ".join(body.split()), 100), "    "))
    if unknown:
        print("\nWarning: cited but not in the context: " + ", ".join(unknown))


def ask(args: argparse.Namespace) -> None:
    """Answer a single question from the command line."""
    result, _, context = answer(
        args.question,
        k=args.k,
        expand=not args.no_expand,
        entities=not args.no_entities,
        focus=None if args.no_focus else FOCUS,
    )
    print_answer(result, context, args.show_context)


def serve(args: argparse.Namespace) -> None:
    """Run the web page and its search API."""
    import uvicorn  # imported here so `ask` doesn't load the web stack

    uvicorn.run("f1rag.api:app", host="127.0.0.1", port=args.port)


def main() -> None:
    """Parse the command line and run `ask` or `serve`."""
    # Hide Neo4j's deprecation notice for db.index.vector.queryNodes, printed on every query.
    logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(prog="f1rag", description="GraphRAG search over the 2026 F1 Sporting Regulations.")
    commands = parser.add_subparsers(dest="command", required=True)

    ask_parser = commands.add_parser("ask", help="answer one question")
    ask_parser.add_argument("question")
    ask_parser.add_argument("-k", type=int, default=5, help="number of seed clauses")
    ask_parser.add_argument("--no-expand", action="store_true", help="vector search only, no graph")
    ask_parser.add_argument("--no-entities", action="store_true", help="structural graph only, no entity expansion")
    ask_parser.add_argument("--no-focus", action="store_true", help="keep the full graph expansion (no entity-match pruning)")
    ask_parser.add_argument("--show-context", action="store_true", help="print the context sent to the model")
    ask_parser.set_defaults(func=ask)

    serve_parser = commands.add_parser("serve", help="run the web page and its search API")
    serve_parser.add_argument("--port", type=int, default=8000)
    serve_parser.set_defaults(func=serve)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
