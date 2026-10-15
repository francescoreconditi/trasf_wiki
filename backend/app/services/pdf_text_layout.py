"""Text layout helpers for the PDF extractor.

This module turns PyMuPDF text blocks into visual rows that keep bold/italic
styling, and reassembles rows into paragraphs and list items.
"""

import re

from pydantic import BaseModel, Field

# Bullet glyphs that start a list item ("• testo", "– testo")
BULLET_PATTERN = re.compile(r"^([•●▪■◦○·\-–—])\s+(?=\S)")

# Numbered list item ("1. testo", "2) testo"); section numbers such as
# "3.1 Titolo" don't match because the number must be followed by a space
NUMBER_PATTERN = re.compile(r"^(\d{1,2})[.)]\s+(?=\S)")

# Two rows on the same visual line differ by at most this many points
ROW_Y_TOLERANCE = 2

# A horizontal gap wider than this fraction of the font size is a space
SPACE_GAP_RATIO = 0.2

# Indentation difference (points) that makes a list item nested
LIST_INDENT_TOLERANCE = 3

# Wiki markup for (bold, italic) styles
STYLE_MARKERS = {(True, False): "'''", (False, True): "''", (True, True): "'''''"}

# Characters that have a meaning at the start of a wiki line
WIKI_LINE_START = ("*", "#", ":", ";", "=", "{|", "|", "!", "----")


class TextRun(BaseModel):
    """A piece of text with a single style."""

    text: str
    bold: bool = False
    italic: bool = False


class VisualRow(BaseModel):
    """A visual line of a text block.

    Attributes:
        runs: Styled text pieces with whitespace already normalized
        size: Average font size of the row
        x0: Left coordinate of the row
    """

    runs: list[TextRun] = Field(default_factory=list)
    size: float
    x0: float

    @property
    def plain(self) -> str:
        """Row text without styling."""
        return "".join(run.text for run in self.runs)


class ListItem(BaseModel):
    """A list item recognized at the start of a row."""

    kind: str  # "b" bullet, "n" numbered
    number: int | None = None
    prefix_len: int  # Characters of the bullet/number to drop


def _span_style(span: dict) -> tuple[bool, bool]:
    """Return (bold, italic) for a PyMuPDF span."""
    flags = span.get("flags", 0)
    font = span.get("font", "").lower()
    bold = bool(flags & 16) or any(w in font for w in ("bold", "black", "heavy"))
    italic = bool(flags & 2) or "italic" in font or "oblique" in font
    return bold, italic


def _normalize_runs(raw_runs: list[TextRun]) -> list[TextRun]:
    """Collapse whitespace across runs and merge runs with the same style.

    Whitespace-only runs take the style of the previous run, so that a space
    between two bold words doesn't split the bold text.
    """
    runs: list[TextRun] = []
    prev_space = True  # Drops leading whitespace
    for raw in raw_runs:
        text = re.sub(r"\s+", " ", raw.text)
        if prev_space:
            text = text.lstrip(" ")
        if not text:
            continue
        prev_space = text.endswith(" ")
        if runs and (
            not text.strip()
            or (runs[-1].bold, runs[-1].italic) == (raw.bold, raw.italic)
        ):
            runs[-1].text += text
        else:
            runs.append(TextRun(text=text, bold=raw.bold, italic=raw.italic))

    while runs and runs[-1].text.endswith(" "):
        runs[-1].text = runs[-1].text.rstrip(" ")
        if not runs[-1].text:
            runs.pop()
    return runs


def _row_from_lines(lines: list[dict]) -> VisualRow | None:
    """Build a visual row from the PDF lines that share the same y."""
    raw_runs: list[TextRun] = []
    sizes: list[float] = []
    for line_index, line in enumerate(lines):
        if line_index:
            raw_runs.append(TextRun(text=" "))
        prev_span: dict | None = None
        for span in line.get("spans", []):
            text = span.get("text", "")
            if not text:
                continue
            if prev_span is not None:
                gap = span["bbox"][0] - prev_span["bbox"][2]
                touching_space = prev_span["text"][-1:].isspace() or text[:1].isspace()
                if not touching_space and gap > SPACE_GAP_RATIO * span.get("size", 10):
                    raw_runs.append(TextRun(text=" "))
            bold, italic = _span_style(span)
            raw_runs.append(TextRun(text=text, bold=bold, italic=italic))
            sizes.append(span.get("size", 0))
            prev_span = span

    runs = _normalize_runs(raw_runs)
    if not runs or not sizes:
        return None
    return VisualRow(
        runs=runs,
        size=sum(sizes) / len(sizes),
        x0=min(line["bbox"][0] for line in lines),
    )


def block_rows(block: dict, skip_line) -> list[VisualRow]:
    """Split a text block into visual rows.

    Args:
        block: PyMuPDF text block
        skip_line: Callable telling whether a line bbox must be ignored
            (e.g. because it belongs to a table)

    Returns:
        Visual rows, top to bottom
    """
    groups: list[list[dict]] = []
    current_y: float | None = None
    for line in block.get("lines", []):
        if skip_line(line["bbox"]):
            continue
        line_y = line["bbox"][1]
        if current_y is not None and abs(line_y - current_y) <= ROW_Y_TOLERANCE:
            groups[-1].append(line)
        else:
            groups.append([line])
            current_y = line_y

    rows = [_row_from_lines(group) for group in groups]
    return [row for row in rows if row is not None]


def _center_inside(bbox: tuple | list, area: tuple | list) -> bool:
    """Check whether the center of ``bbox`` falls inside ``area``."""
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    return area[0] <= cx <= area[2] and area[1] <= cy <= area[3]


def area_text(blocks: list[dict], area: tuple | list) -> str:
    """Render the styled text whose spans fall inside an area (e.g. a cell).

    Args:
        blocks: Text blocks of the page (``page.get_text("dict")["blocks"]``)
        area: (x0, y0, x1, y1) of the area

    Returns:
        Single-line wiki text with bold/italic markup
    """
    runs: list[TextRun] = []
    for block in blocks:
        for line in block.get("lines", []):
            spans = [
                s for s in line.get("spans", []) if _center_inside(s["bbox"], area)
            ]
            if not spans:
                continue
            row = _row_from_lines([{**line, "spans": spans}])
            if row:
                if runs:
                    runs.append(TextRun(text=" "))
                runs.extend(row.runs)
    return render_runs(runs)


def match_list_item(plain: str) -> ListItem | None:
    """Recognize a bullet or numbered list item at the start of a row."""
    bullet = BULLET_PATTERN.match(plain)
    if bullet:
        return ListItem(kind="b", prefix_len=bullet.end())
    number = NUMBER_PATTERN.match(plain)
    if number:
        return ListItem(kind="n", number=int(number.group(1)), prefix_len=number.end())
    return None


def _join_wiki(pieces: list[str]) -> str:
    """Concatenate pieces, separating apostrophes that would merge into markup."""
    result = ""
    for piece in pieces:
        if result.endswith("'") and piece.startswith("'"):
            result += "<nowiki/>"
        result += piece
    return result


def drop_prefix(runs: list[TextRun], chars: int) -> list[TextRun]:
    """Return a copy of the runs without their first ``chars`` characters."""
    result: list[TextRun] = []
    for run in runs:
        text = run.text
        if chars:
            dropped = min(chars, len(text))
            text, chars = text[dropped:], chars - dropped
        if text:
            result.append(TextRun(text=text, bold=run.bold, italic=run.italic))
    return result


def render_runs(runs: list[TextRun]) -> str:
    """Render styled runs as wiki text.

    Args:
        runs: Styled text pieces (normalized here, so rows can be appended)

    Returns:
        Text with ''' / '' markup around bold and italic parts
    """
    pieces: list[str] = []
    for run in _normalize_runs(runs):
        marker = STYLE_MARKERS.get((run.bold, run.italic))
        core = run.text.strip()
        if not marker or not core:
            pieces.append(run.text)
            continue
        lead = run.text[: len(run.text) - len(run.text.lstrip())]
        trail = run.text[len(run.text.rstrip()) :]
        pieces.extend([lead, marker, core, marker, trail])
    return _join_wiki([piece for piece in pieces if piece]).strip()


def escape_line_start(text: str) -> str:
    """Prevent a paragraph from being parsed as wiki list/heading/table syntax."""
    if text.startswith(WIKI_LINE_START):
        return "<nowiki/>" + text
    return text


class ParagraphBuilder:
    """Reassemble visual rows into paragraphs and list items.

    Rows of the same block are joined until a new list item, heading or block
    starts. Output lines use the extractor markers:
    a paragraph is a plain line followed by a blank line, a list item is
    ``LIST_ITEM:<b|n>:<level>:<number>:<text>``.
    """

    def __init__(self, output: list[str]) -> None:
        self.output = output
        self.kind: str | None = None  # None, "text" or a list kind
        self.number: int | None = None
        self.level = 0
        self.runs: list[TextRun] = []
        # Left x of the open list levels, to compute nesting
        self.list_indents: list[float] = []

    def flush(self) -> None:
        """Emit the paragraph or list item being built."""
        if self.kind is None:
            return
        text = render_runs(self.runs)
        if self.kind == "text":
            self.output.append(escape_line_start(text))
            self.output.append("")
        elif text:
            number = self.number if self.number is not None else ""
            self.output.append(f"LIST_ITEM:{self.kind}:{self.level}:{number}:{text}")
        self.kind, self.number, self.runs = None, None, []

    def break_lists(self) -> None:
        """Close the current paragraph and forget list nesting."""
        self.flush()
        self.list_indents = []

    def add_row(self, row: VisualRow, first_in_block: bool) -> None:
        """Add a body-text row (not a heading or TOC entry)."""
        item = match_list_item(row.plain)
        if item and item.kind == "n" and not first_in_block and self.kind == "text":
            # A wrapped line that happens to start with a number
            item = None

        if item:
            self.flush()
            while (
                self.list_indents
                and self.list_indents[-1] > row.x0 + LIST_INDENT_TOLERANCE
            ):
                self.list_indents.pop()
            if (
                not self.list_indents
                or row.x0 > self.list_indents[-1] + LIST_INDENT_TOLERANCE
            ):
                self.list_indents.append(row.x0)
            self.kind, self.number = item.kind, item.number
            self.level = len(self.list_indents)
            self.runs = drop_prefix(row.runs, item.prefix_len)
            return

        if self.kind is not None and not first_in_block:
            # Wrapped line of the current paragraph or list item: styles are
            # rendered on the whole paragraph, so a wrapped bold stays one run
            self.runs += [TextRun(text=" "), *row.runs]
            return

        self.break_lists()
        self.kind = "text"
        self.runs = list(row.runs)
