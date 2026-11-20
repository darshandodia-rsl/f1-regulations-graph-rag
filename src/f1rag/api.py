"""HTTP API for the web page: one search endpoint, plus the page itself.

  f1rag serve [--port 8000]      then open http://127.0.0.1:8000/

POST /api/search {"question": "..."} runs the same pipeline as `f1rag ask` (vector seeds, graph
expansion, Groq answer) and returns JSON the page renders:
  answer       the model's Markdown, with inline [B1.6.3] citations
  answerable   false when the retrieved clauses don't hold the answer
  citations    the clauses the answer cites, with breadcrumb and full text
  retrieved    vector-search seeds the answer didn't cite
  related      clauses the graph added (cited by a seed, or sharing its entities) that weren't cited
Everything else under / is served from web/ as static files.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from neo4j.exceptions import DriverError, Neo4jError
from pydantic import BaseModel, Field

from . import config
from .cli import breadcrumb, provisions
from .search.llm import answer, check_citations

WEB_DIR = config.PROJECT_ROOT / "web"
MAX_RELATED = 6  # graph-added clauses shown on the page


class SearchRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class Clause(BaseModel):
    id: str
    breadcrumb: str
    title: str
    text: str


class SearchResponse(BaseModel):
    question: str
    answer: str
    answerable: bool
    citations: list[Clause]
    retrieved: list[Clause]
    related: list[Clause]


def clause(clause_id: str) -> Clause | None:
    """A provision from provisions.json, ready for the page."""
    p = provisions().get(clause_id)
    if p is None:
        return None
    return Clause(id=clause_id, breadcrumb=breadcrumb(clause_id), title=p["title"] or "", text=p["text"] or "")


def clauses(ids: list[str]) -> list[Clause]:
    """Each id once, in order, skipping ids that aren't provisions."""
    found = []
    for clause_id in dict.fromkeys(ids):
        c = clause(clause_id)
        if c is not None:
            found.append(c)
    return found


app = FastAPI(title="F1 Regulations Helper")


@app.post("/api/search")
def search(request: SearchRequest) -> SearchResponse:
    # A plain `def`: FastAPI runs it in a worker thread, so the slow Neo4j and Groq calls don't block the server.
    try:
        result, docs, context = answer(request.question)
    except (DriverError, Neo4jError) as e:
        # e.g. AuraDB timing out or resuming from pause: say so instead of a bare 500
        raise HTTPException(503, "The Neo4j database didn't answer. Try again in a moment.") from e
    cited, _ = check_citations(result, context)

    seeds = [doc.metadata["id"] for doc in docs]
    added = []
    for doc in docs:
        added += [ref["id"] for ref in doc.metadata.get("references", [])]
        added += [other["id"] for other in doc.metadata.get("shared", [])]

    seen = set(cited)
    retrieved = [i for i in seeds if i not in seen]
    seen.update(retrieved)
    related = [i for i in dict.fromkeys(added) if i not in seen]

    return SearchResponse(
        question=request.question,
        answer=result.answer,
        answerable=result.answerable,
        citations=clauses(cited),
        retrieved=clauses(retrieved),
        related=clauses(related)[:MAX_RELATED],
    )


# Mounted last, so /api/search wins over a static file of the same path.
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
