"""Parse the regulations PDF into structured provisions and glossary terms.

The document is numbered, and each numbered unit becomes a "provision":

    ARTICLE B1: ORGANISATION OF A COMPETITION       -> level "article"
    B1.6       Pit Entry Road, Pit Lane ...          -> level "section"
    B1.6.3     Driving in the Pit Entry Road ...     -> level "clause"
               a. A speed limit of 80km/h ...           (sub-items stay inside the clause text)

Every provision has an id, title, text and parent. Appendix B1 (Definitions) is also parsed into a
glossary of terms. Output: data/parsed/provisions.json and data/parsed/terms.json.
"""

import json
import re
from dataclasses import asdict, dataclass, field

import pymupdf

from .. import config

ARTICLE_RE = re.compile(r"^(ARTICLE|APPENDIX) (B\d+): (.+)$")
SECTION_RE = re.compile(r"^(B\d+\.\d+)\s+(.+)$")
CLAUSE_RE = re.compile(r"^(B\d+\.\d+\.\d+)\s*(.*)$")
DEFINITION_RE = re.compile(r"^“([^”]+)”(?:\s*\(or “([^”]+)”\))?\s*:?\s*(.*)$")

# Running headers/footers repeated on every page.
NOISE_RE = re.compile(
    r"^(SECTION B: SPORTING REGULATIONS|(?:2026\s+)+Formula 1 Regulations - Section B|©2026 Fédération|Issue\s+\d+|\.\./\.\.)"
)

FIRST_BODY_PAGE = 4  # pages 1-3 are the cover and table of contents
# Appendix B5 lists changes for 2027+ and re-uses article numbers, so parsing stops there.
STOP_HEADING = "APPENDIX B5"

# Pink text marks changes vs the previous issue: struck through = deleted, otherwise newly added.
PINK_RGB = 0xFF00FF

MAX_CHUNK_CHARS = 2500  # long unstructured appendices are split into chunks of this size
# List markers at the start of a line, outermost level first: "1. ", "a. ", "ii. ".
LIST_MARKERS_RE = [
    re.compile(r"^\d+[.)]\s"),
    re.compile(r"^[a-z][.)]\s"),
    re.compile(r"^(?:iv|ix|v?i{1,3}|v|x)[.)]\s"),
]


@dataclass
class Provision:
    """One article, section or clause."""
    id: str
    level: str  # "article" | "section" | "clause"
    title: str
    parent: str | None
    text_lines: list[str] = field(default_factory=list)
    advisory_committee: str | None = None
    governance: str | None = None

    @property
    def text(self) -> str:
        """The provision's body text as one string."""
        return "\n".join(self.text_lines).strip()


def _looks_like_title(s: str) -> bool:
    """'Driving in the Pit Entry Road' is a title; 'During a Championship each Competitor...' is body text.

    A title is short, has no closing punctuation, and most of its longer words are capitalised.
    """
    if not s or len(s) > 90 or s[-1] in ".,;:":
        return False
    long_words = []
    for word in re.findall(r"[A-Za-z][\w’'()-]*", s):
        if len(word) > 3:
            long_words.append(word)
    if not long_words:
        return False
    capitalised = 0
    for word in long_words:
        if word[0].isupper():
            capitalised += 1
    return capitalised / len(long_words) >= 0.6


def _is_pink(rgb) -> bool:
    """True if the colour (r, g, b as 0-1 floats) is the pink used for changes."""
    if rgb is None:
        return False
    red, green, blue = rgb[0], rgb[1], rgb[2]
    return round(red, 2) == 1.0 and round(green, 2) == 0.0 and round(blue, 2) == 1.0


def _strike_rects(page: pymupdf.Page) -> list[pymupdf.Rect]:
    """The strikethrough lines on a page: thin pink lines/rectangles drawn over the text."""
    rects = []
    for drawing in page.get_drawings():
        rect = drawing["rect"]
        if rect.height < 2 and (_is_pink(drawing.get("fill")) or _is_pink(drawing.get("color"))):
            rects.append(rect)
    return rects


def _is_struck(span: dict, strikes: list[pymupdf.Rect]) -> bool:
    """True if a strike line crosses the span horizontally and sits near its vertical middle."""
    x0, y0, x1, y1 = span["bbox"]
    span_middle = (y0 + y1) / 2
    for r in strikes:
        overlaps_horizontally = r.x0 < x1 and r.x1 > x0
        strike_middle = (r.y0 + r.y1) / 2
        near_middle = abs(strike_middle - span_middle) < (y1 - y0) * 0.3
        if overlaps_horizontally and near_middle:
            return True
    return False


def _remove_deleted_text(page: pymupdf.Page) -> None:
    """Redact pink, struck-through spans in the in-memory page (the PDF on disk is untouched).

    Pink text that is not struck through is newly added text and is kept like any other.
    """
    strikes = _strike_rects(page)
    if not strikes:
        return
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["color"] == PINK_RGB and _is_struck(span, strikes):
                    x0, y0, x1, y1 = span["bbox"]
                    inset = (y1 - y0) * 0.2  # stay clear of neighbouring spans and lines
                    page.add_redact_annot(pymupdf.Rect(x0 + 0.5, y0 + inset, x1 - 0.5, y1 - inset))
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE)


def _read_lines() -> list[str]:
    """All body text lines of the PDF, with deleted text, headers and footers removed."""
    doc = pymupdf.open(config.PDF_PATH)
    lines = []
    for page in doc.pages(FIRST_BODY_PAGE - 1):
        _remove_deleted_text(page)
        for raw in page.get_text(sort=True).splitlines():
            # Collapse runs of spaces left by the PDF layout (and by removed text), keeping leading indent.
            line = re.sub(r"(?<=\S)[ \t]{2,}", " ", raw).rstrip()
            stripped = line.strip()
            if not stripped or NOISE_RE.match(stripped) or stripped in {"B", "0"}:
                continue
            # The header line also carries the page tab ("... 0   B"); drop anything that starts with it.
            if stripped.startswith("SECTION B:"):
                continue
            lines.append(line)
    return lines


def parse_provisions() -> list[Provision]:
    """Walk the lines, starting a new provision at each article, section or clause heading."""
    provisions = {}
    current = None  # the provision that body text is appended to
    article = None
    section = None

    for line in _read_lines():
        if line.startswith(STOP_HEADING):
            break

        article_match = ARTICLE_RE.match(line)
        if article_match:
            _, article_id, title = article_match.groups()
            # Appendices share numbers with articles (Appendix B1 vs Article B1), so they get their own ids.
            if line.startswith("APPENDIX"):
                article_id = "App" + article_id
            if article_id not in provisions:
                provisions[article_id] = Provision(article_id, "article", title.strip(), None)
            article = provisions[article_id]
            current = article
            section = None
            continue

        stripped = line.strip()
        if article and stripped.startswith("Advisory Committee:"):
            article.advisory_committee = stripped.split(":", 1)[1].strip()
            continue
        if article and stripped.startswith("Governance:"):
            article.governance = stripped.split(":", 1)[1].strip()
            continue

        clause_match = CLAUSE_RE.match(line)
        if clause_match:
            clause_id, rest = clause_match.groups()
            if _looks_like_title(rest):
                title = rest
            else:
                title = ""
            if section:
                parent = section.id
            elif article:
                parent = article.id
            else:
                parent = None
            if clause_id not in provisions:
                provisions[clause_id] = Provision(clause_id, "clause", title, parent)
            current = provisions[clause_id]
            # Text on the heading line that isn't a title is the start of the clause body.
            if rest and not title:
                current.text_lines.append(rest)
            continue

        section_match = SECTION_RE.match(line)
        if section_match:
            section_id, title = section_match.groups()
            if section_id not in provisions:
                if article:
                    parent = article.id
                else:
                    parent = None
                provisions[section_id] = Provision(section_id, "section", title.strip(), parent)
            section = provisions[section_id]
            current = section
            continue

        if current:
            current.text_lines.append(stripped)

    return list(provisions.values())


def _size(lines: list[str]) -> int:
    """Length of the lines joined with newlines."""
    return len("\n".join(lines))


def _pack(pieces: list[list[str]]) -> list[list[str]]:
    """Merge consecutive pieces into chunks, starting a new chunk when the next piece would go over MAX_CHUNK_CHARS."""
    chunks = []
    current = []
    for piece in pieces:
        if current and _size(current + piece) > MAX_CHUNK_CHARS:
            chunks.append(current)
            current = []
        current = current + piece
    if current:
        chunks.append(current)
    return chunks


def _chunk_lines(lines: list[str], markers: list[re.Pattern]) -> list[list[str]]:
    """Split lines into chunks of at most MAX_CHUNK_CHARS, along list items where possible.

    First split at the top-level list markers, one chunk per item (items are never merged, so each chunk
    stays a single idea). Items still over the limit are split at the next marker level. With no marker
    levels left, lines are packed up to the limit.
    """
    if _size(lines) <= MAX_CHUNK_CHARS:
        return [lines]

    for level, marker in enumerate(markers):
        # Start a new segment at every line that begins with this marker.
        segments = []
        for line in lines:
            if marker.match(line) or not segments:
                segments.append([])
            segments[-1].append(line)

        if len(segments) > 1:
            deeper_markers = markers[level + 1:]
            chunks = []
            for segment in segments:
                chunks.extend(_chunk_lines(segment, deeper_markers))
            return chunks

    single_lines = []
    for line in lines:
        single_lines.append([line])
    return _pack(single_lines)


def _starts_with_list_marker(line: str) -> bool:
    """True if the line begins with "1. ", "a. ", "ii. " or similar."""
    for marker in LIST_MARKERS_RE:
        if marker.match(line):
            return True
    return False


def split_long_unstructured(provisions: list[Provision]) -> list[Provision]:
    """Split long appendices (tables/lists with no clause numbers) into "-partN" clause chunks."""
    result = []
    for p in provisions:
        if p.level != "article" or len(p.text) <= MAX_CHUNK_CHARS:
            result.append(p)
            continue

        # Keep the appendix itself (without text) as the parent of its parts.
        result.append(Provision(p.id, p.level, p.title, p.parent, [], p.advisory_committee, p.governance))
        chunks = _chunk_lines(p.text_lines, LIST_MARKERS_RE)
        for part, chunk in enumerate(chunks, start=1):
            # A chunk that starts at a list item is named after it ("... - 1. BRAKES"); others are just numbered.
            if _starts_with_list_marker(chunk[0]):
                title = f"{p.title} - {chunk[0][:60].strip()}"
            else:
                title = f"{p.title} (part {part})"
            result.append(Provision(f"{p.id}-part{part}", "clause", title, p.id, chunk))
    return result


def parse_definitions(provisions: list[Provision]) -> list[dict]:
    """Turn Appendix B1 into [{term, abbreviation, definition}]."""
    appendix = None
    for p in provisions:
        if p.id == "AppB1":
            appendix = p
            break
    if appendix is None:
        return []

    terms = []
    for line in appendix.text_lines:
        definition_match = DEFINITION_RE.match(line)
        if definition_match:
            term, abbreviation, rest = definition_match.groups()
            terms.append({"term": term.strip(), "abbreviation": abbreviation, "definition": rest.strip()})
        elif terms:
            # A continuation line of the previous definition.
            terms[-1]["definition"] += " " + line
    return terms


def run() -> tuple[list[dict], list[dict]]:
    """Parse the PDF and write provisions.json and terms.json. Returns (provisions, terms)."""
    provisions = parse_provisions()
    terms = parse_definitions(provisions)
    provisions = split_long_unstructured(provisions)

    records = []
    for p in provisions:
        record = asdict(p)
        record["text"] = p.text
        del record["text_lines"]
        records.append(record)

    config.PROVISIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.PROVISIONS_FILE.write_text(json.dumps(records, indent=2, ensure_ascii=False))
    config.TERMS_FILE.write_text(json.dumps(terms, indent=2, ensure_ascii=False))
    return records, terms
