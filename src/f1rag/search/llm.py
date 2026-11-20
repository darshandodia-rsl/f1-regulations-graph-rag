"""Turn retrieved graph context into a cited answer with a Groq model.

The chain is LangChain's LCEL pipe syntax:  PROMPT | chat_model().with_structured_output(Answer, ...)
  PROMPT           ChatPromptTemplate: fills {context} and {question} into a list of messages
                   (system, user). Nothing is sent yet.
  with_structured_output
                   wraps ChatGroq. It turns the Answer Pydantic model into a JSON Schema and sends it
                   as `response_format={"type": "json_schema", ..., "strict": true}` with the messages
                   to Groq's OpenAI-style /chat/completions endpoint. With strict mode Groq constrains
                   decoding, so the reply is always JSON matching the schema. A parser then validates
                   that JSON into an Answer object.
Each piece is a Runnable, so `chain.invoke({...})` runs them left to right.

format_context() turns the retrieved Documents (text plus graph expansion in their metadata) into the
text the model reads, trimmed to a character budget.

Run:  python -m f1rag.search.llm "What happens if a driver ignores a red flag?"
"""

import re
import sys
import textwrap
from functools import cache

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from .. import config
from .retrieve import FOCUS, HYBRID, fact_line, retrieve

# Maximum context size: about 6k tokens at ~4 characters per token.
MAX_CONTEXT_CHARS = 24_000
MAX_RELATED_CHARS = 800  # each cited or shared clause is cut to this; the seed clauses are kept whole

SYSTEM = """You answer questions about the FIA 2026 Formula 1 Sporting Regulations (Section B).

Rules:
- Use only the regulation text in the context below. If it does not contain the answer, say so plainly and set answerable to false.
- Cite the clause behind every claim with its ID in square brackets, e.g. [B1.6.3]. Only cite IDs that appear in the context.
- List every clause ID you cited in citations, each once, written exactly as in the context (e.g. B1.6.3).
- Be concise and precise: keep numbers, times and conditions exactly as written.
- Glossary definitions explain terms; they are not rules by themselves.
- "Facts" are one-line summaries extracted from the clauses in their brackets. Use them to find related rules, prefer the clause text when both are present, and cite the bracketed clause.

Context:
{context}"""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", "{question}"),
])

class Answer(BaseModel):
    """The model's reply, in the shape Groq is told to return."""

    answer: str = Field(description="The answer in Markdown, citing clauses inline as [B1.6.3].")
    citations: list[str] = Field(description="Every clause ID cited in the answer, each once, e.g. B1.6.3.")
    answerable: bool = Field(description="False if the context does not contain the answer.")


# Citations are clause IDs inside brackets: [B1.6.3], and the other forms the model writes:
# [**B1.6.3 iii**], [B1.9.6 b ii], 【B7.2.2】, or several in one bracket like [B1.6.3, B1.6.4].
BRACKET = re.compile(r"[\[【]([^\]】]*)[\]】]")
CLAUSE_ID = re.compile(r"\b(?:App)?B\d+(?:\.\d+)*(?:-part\d+)?")


def cited_ids(text: str) -> list[str]:
    """Every clause ID inside a bracket, in order of appearance (repeats kept)."""
    ids = []
    for inside in BRACKET.findall(text):
        for clause_id in CLAUSE_ID.findall(inside):
            ids.append(clause_id)
    return ids


@cache  # create the client once and reuse it
def chat_model(model: str = config.GROQ_ANSWER_MODEL, temperature: float = 0.0) -> ChatGroq:
    """The Groq chat model. Exits with a message if no API key is set."""
    if not config.GROQ_API_KEY:
        sys.exit("GROQ_API_KEY is not set. Copy .env.example to .env and fill it in.")
    # The client retries rate-limit (429) errors itself, honouring Groq's retry-after header.
    return ChatGroq(model=model, temperature=temperature, api_key=config.GROQ_API_KEY, max_retries=8)


def shorten(text: str) -> str:
    """Put the text on one line and cut it to MAX_RELATED_CHARS."""
    one_line = " ".join(text.split())
    return textwrap.shorten(one_line, MAX_RELATED_CHARS, placeholder=" ...")


def format_context(docs: list[Document], budget: int = MAX_CONTEXT_CHARS) -> str:
    """Lay out seeds, the clauses they cite, entity facts, clauses sharing entities, then glossary terms.

    Each item appears once, and the budget is filled in that order.
    """
    seed_ids = set()
    for doc in docs:
        seed_ids.add(doc.metadata["id"])

    seeds = []    # full text of each seed clause
    related = {}  # clause id -> text of a clause a seed cites
    facts = []    # one-line entity facts
    shared = {}   # clause id -> text of a clause sharing entities with a seed
    terms = {}    # term name -> definition

    for doc in docs:
        m = doc.metadata

        head = f"[{m['id']}]"
        if m.get("path"):
            head += f" ({' > '.join(m['path'])})"
        block = f"{head}\n{doc.page_content.strip()}"
        if m.get("referenced_by"):
            block += f"\nCited by (text not included): {', '.join(m['referenced_by'])}"
        seeds.append(block)

        for ref in m.get("references", []):
            if ref["id"] in seed_ids or ref["id"] in related:
                continue
            if ref["text"]:
                body = shorten(ref["text"])
            else:  # a section or article: no text of its own, just a heading
                body = f"({ref['level']} containing {', '.join(ref['clauses'])})"
            related[ref["id"]] = f"[{ref['id']}] {ref['title']}: {body}"

        for term in m.get("terms", []):
            if term["name"] in terms:
                continue
            if term.get("abbreviation"):
                name = f"{term['name']} ({term['abbreviation']})"
            else:
                name = term["name"]
            definition = " ".join(term["definition"].split())
            terms[term["name"]] = f"{name}: {definition}"

        for fact in m.get("facts", []):
            line = fact_line(fact)
            if line not in facts:
                facts.append(line)

        for other in m.get("shared", []):
            if other["id"] in seed_ids or other["id"] in shared:
                continue
            body = shorten(other["text"] or "")
            title = other["title"] or ""
            shared[other["id"]] = f"[{other['id']}] {title} (shares: {', '.join(other['via'])}): {body}"

    # A clause already included because a seed cites it doesn't need repeating as a shared-entity clause.
    for clause_id in list(shared):
        if clause_id in related:
            del shared[clause_id]

    # Fill the budget in priority order.
    sections = [
        ("Matching clauses", seeds),
        ("Clauses they cite", list(related.values())),
        ("Facts from the entity graph", facts),
        ("Clauses about the same things", list(shared.values())),
        ("Glossary", list(terms.values())),
    ]
    parts = []
    used = 0
    for title, items in sections:
        kept = []
        for item in items:
            if used + len(item) > budget:
                break
            kept.append(item)
            used += len(item)
        if kept:
            parts.append(f"## {title}\n\n" + "\n\n".join(kept))
    return "\n\n".join(parts)


def answer(
    question: str,
    k: int = 5,
    expand: bool = True,
    entities: bool = True,
    focus: int | None = FOCUS,
    hybrid: bool = HYBRID,
) -> tuple[Answer, list[Document], str]:
    """Retrieve, then answer. Returns (the structured answer, retrieved docs, the context the model saw)."""
    docs = retrieve(question, k=k, expand=expand, entities=entities, focus=focus, hybrid=hybrid)
    context = format_context(docs)
    # strict=True: Groq enforces the schema while decoding (supported for the gpt-oss models).
    chain = PROMPT | chat_model().with_structured_output(Answer, method="json_schema", strict=True)
    result = chain.invoke({"context": context, "question": question})
    return result, docs, context


def citation_ids(result: Answer) -> list[str]:
    """The clause IDs in result.citations, with extras like '**' or ' iii' stripped."""
    ids = []
    for citation in result.citations:
        ids.extend(CLAUSE_ID.findall(citation))
    return ids


def check_citations(result: Answer, context: str) -> tuple[list[str], list[str]]:
    """Split the IDs the answer cites into (found in context, not in context), each listed once."""
    known = set(cited_ids(context))
    found = []
    unknown = []
    for clause_id in citation_ids(result):
        if clause_id in found or clause_id in unknown:
            continue
        if clause_id in known:
            found.append(clause_id)
        else:
            unknown.append(clause_id)
    return found, unknown


if __name__ == "__main__":
    result, _, _ = answer(" ".join(sys.argv[1:]))
    print(result.model_dump_json(indent=2))
