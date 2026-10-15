"""PDF extraction service using PyMuPDF.

This module handles extraction of text and images from PDF files.
"""

import re
from collections import Counter
from pathlib import Path
from typing import Any

import fitz  # PyMuPDF

from app.models.dto import ExtractedData
from app.services.pdf_text_layout import (
    ParagraphBuilder,
    VisualRow,
    area_text,
    block_rows,
)
from app.services.storage import save_image

# Table-of-contents row: title, dot leaders, page number ("3.1 Ordine ....... 5")
TOC_ENTRY_PATTERN = re.compile(
    r"^(?P<title>.*?\S)\s*[.…·](?:\s*[.…·]){3,}\s*(?P<page>\d+)$"
)

# Leading section number ("1.", "3.1", "3.1.2")
SECTION_NUMBER_PATTERN = re.compile(r"^(\d+(?:\.\d+)*)\.?\s")

# Header/footer areas (points, ~2.5 cm): only repeated text there is dropped
HEADER_MARGIN = 70
FOOTER_MARGIN = 70

# Margin text that is only a page number ("3", "- 3 -", "Pag. 3 di 27")
PAGE_NUMBER_PATTERN = re.compile(
    r"^[\W_]*(pag(ina)?\.?\s*)?#(\s*(di|/|of)\s*#)?[\W_]*$"
)

# A first page with more non-heading text than this is not a cover
MAX_COVER_BODY_CHARS = 300

# Tables smaller than this are discarded (e.g. dashed frames around figures)
MIN_TABLE_ROWS = 2
MIN_TABLE_COLS = 2


def _match_toc_entry(line_text: str) -> tuple[int, str] | None:
    """Recognize a table-of-contents row and return its level and title.

    Args:
        line_text: Text of a visual row

    Returns:
        Tuple of (level, title) if the row is a TOC entry, None otherwise.
        The level is the depth of the section number ("1." -> 1, "3.1" -> 2).
    """
    match = TOC_ENTRY_PATTERN.match(line_text.strip())
    if not match:
        return None

    title = match.group("title").strip()
    number_match = SECTION_NUMBER_PATTERN.match(title)
    level = number_match.group(1).count(".") + 1 if number_match else 1
    return level, title


def _cell_text(blocks: list[dict], cell: tuple | None, styled: bool) -> str:
    """Return the text of a table cell for the ROW/HEADER_ROW markers.

    Args:
        blocks: Text blocks of the page
        cell: Cell bbox (None for a cell covered by a merged cell)
        styled: Keep bold/italic as wiki markup (header cells are already
            rendered bold by the wiki, so they are emitted plain)

    Returns:
        Single-line cell text with pipes escaped
    """
    if not cell:
        return ""
    text = area_text(blocks, cell)
    if not styled:
        text = re.sub(r"'{2,}", "", text.replace("<nowiki/>", ""))
    return text.replace("|", "&#124;")


def _extract_tables(page: fitz.Page) -> list[dict]:
    """Detect tables on a page and convert them to pseudo-blocks.

    Args:
        page: PDF page

    Returns:
        List of blocks with type "table", their bbox and the table markers
    """
    table_blocks = []
    try:
        # "lines_strict" ignores the borders of shaded cell backgrounds, which
        # would otherwise split header cells into extra columns
        tables = page.find_tables(strategy="lines_strict").tables
    except Exception as e:
        print(f"Error detecting tables on page {page.number + 1}: {e}")
        return table_blocks

    blocks = page.get_text("dict")["blocks"]
    for table in tables:
        rows = [
            [_cell_text(blocks, cell, styled=row_index > 0) for cell in row.cells]
            for row_index, row in enumerate(table.rows)
        ]
        rows = [row for row in rows if any(row)]
        if not rows:
            continue
        # Cell borders and shaded backgrounds produce spurious empty columns
        keep = [c for c in range(len(rows[0])) if any(row[c] for row in rows)]
        rows = [[row[c] for c in keep] for row in rows]
        if len(rows) < MIN_TABLE_ROWS or len(keep) < MIN_TABLE_COLS:
            continue

        markers = ["TABLE_START", "HEADER_ROW:" + " | ".join(rows[0])]
        markers.extend("ROW:" + " | ".join(row) for row in rows[1:])
        markers.append("TABLE_END")
        table_blocks.append(
            {"type": "table", "bbox": tuple(table.bbox), "markers": markers}
        )

    return table_blocks


def _is_inside_table(bbox: tuple | list, table_blocks: list[dict]) -> bool:
    """Check whether the center of a bbox falls inside any detected table.

    Args:
        bbox: (x0, y0, x1, y1) of a text line
        table_blocks: Tables detected on the same page

    Returns:
        True if the line belongs to a table
    """
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    for table in table_blocks:
        x0, y0, x1, y1 = table["bbox"]
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            return True
    return False


def _block_text(block: dict) -> str:
    """Return the plain text of a text block."""
    return " ".join(
        span.get("text", "").strip()
        for line in block.get("lines", [])
        for span in line.get("spans", [])
        if span.get("text", "").strip()
    )


def _margin_key(text: str) -> str:
    """Normalize margin text so that running headers/footers compare equal.

    Page numbers change on every page, so digits are replaced by a placeholder.
    """
    return re.sub(r"\d+", "#", text.strip().lower())


def _in_margin(bbox: tuple | list, page_height: float) -> bool:
    """Check whether a block starts in the header or footer area."""
    return bbox[1] < HEADER_MARGIN or bbox[1] > page_height - FOOTER_MARGIN


def _find_running_texts(doc: fitz.Document) -> set[str]:
    """Collect header/footer texts that repeat across pages.

    Args:
        doc: Open PDF document

    Returns:
        Normalized texts (see _margin_key) found in the margins of at least
        two pages and at least a third of the pages
    """
    pages_by_key: Counter[str] = Counter()
    for page in doc:
        keys = {
            _margin_key(_block_text(block))
            for block in page.get_text("dict")["blocks"]
            if block.get("type", 0) == 0 and _in_margin(block["bbox"], page.rect.height)
        }
        pages_by_key.update(key for key in keys if key)

    min_pages = max(2, doc.page_count // 3)
    return {key for key, count in pages_by_key.items() if count >= min_pages}


PageItem = tuple[str, int, Any]


def _page_items(
    sorted_blocks: list[dict],
    table_blocks: list[dict],
    page_height: float,
    running_texts: set[str],
) -> list[PageItem]:
    """Flatten the blocks of a page into items in reading order.

    Args:
        sorted_blocks: Text, image and table blocks sorted top to bottom
        table_blocks: Tables of the page (their text is skipped in text blocks)
        page_height: Page height, to detect header/footer areas
        running_texts: Repeated header/footer texts (see _find_running_texts)

    Returns:
        List of (kind, block index, payload) where kind is "row" (payload:
        VisualRow), "toc" ((level, title)), "table" (markers) or "image" (None)
    """
    items: list[PageItem] = []
    for block_id, block in enumerate(sorted_blocks):
        block_type = block.get("type", 0)
        if block_type == "table":
            items.append(("table", block_id, block["markers"]))
            continue

        # Skip running headers/footers: in the margins, drop images and text
        # that repeats across pages or is just a page number. Other margin
        # text (e.g. a heading low on the page) is content.
        if _in_margin(block["bbox"], page_height):
            if block_type != 0:
                continue
            key = _margin_key(_block_text(block))
            if not key or key in running_texts or PAGE_NUMBER_PATTERN.match(key):
                continue

        if block_type == 1:
            items.append(("image", block_id, None))
        elif block_type == 0:
            rows = block_rows(block, lambda bbox: _is_inside_table(bbox, table_blocks))
            for row in rows:
                toc_entry = _match_toc_entry(row.plain)
                if toc_entry:
                    items.append(("toc", block_id, toc_entry))
                else:
                    items.append(("row", block_id, row))
    return items


def _merge_wrapped_toc_rows(items: list[PageItem]) -> list[PageItem]:
    """Join TOC titles that wrap onto two rows.

    A row without dot leaders that follows a TOC entry may be the first half
    of a long title whose second half carries the leaders and page number.
    """
    merged: list[PageItem] = []
    i = 0
    while i < len(items):
        item = items[i]
        if (
            item[0] == "row"
            and merged
            and merged[-1][0] == "toc"
            and i + 1 < len(items)
            and items[i + 1][0] == "row"
        ):
            combined = _match_toc_entry(f"{item[2].plain} {items[i + 1][2].plain}")
            if combined:
                merged.append(("toc", item[1], combined))
                i += 2
                continue
        merged.append(item)
        i += 1
    return merged


def _format_cover_page(lines: list[str]) -> list[str]:
    """Turn the headings of a cover page into emphasized text.

    A first page made only of a few large lines (title, subtitle, version) is
    a cover: emitting it as headings would put it in the wiki TOC.

    Args:
        lines: Marker lines of the first page

    Returns:
        The lines, with cover headings replaced by bold/italic paragraphs
    """
    if any(
        line.startswith(("TOC_ENTRY", "LIST_ITEM", "TABLE_START")) for line in lines
    ):
        return lines
    headings = [line.split(":", 1)[1] for line in lines if line.startswith("HEADING")]
    if not headings or any(SECTION_NUMBER_PATTERN.match(h) for h in headings):
        return lines
    body_chars = sum(
        len(line)
        for line in lines
        if line and not line.startswith(("HEADING", "IMAGE:"))
    )
    if body_chars > MAX_COVER_BODY_CHARS:
        return lines

    result: list[str] = []
    for line in lines:
        if line.startswith("HEADING"):
            text = line.split(":", 1)[1].strip()
            result.extend([f"'''{text}'''" if not result else f"''{text}''", ""])
        else:
            result.append(line)
    return result


def _normalize_heading_levels(text: str) -> str:
    """Renumber heading levels so that the largest heading used is level 1.

    Levels come from font-size ratios, so a document may use e.g. only levels
    2 and 3; in MediaWiki its chapters should still be "== ... ==".
    """
    levels = sorted({int(level) for level in re.findall(r"^HEADING(\d):", text, re.M)})
    mapping = {old: new for new, old in enumerate(levels, start=1)}
    return re.sub(
        r"^HEADING(\d):",
        lambda m: f"HEADING{mapping[int(m.group(1))]}:",
        text,
        flags=re.M,
    )


def _detect_heading_level(font_size: float, base_font_size: float) -> int:
    """Detect heading level based on font size relative to base text.

    Args:
        font_size: Font size of the current text
        base_font_size: Base font size for normal text

    Returns:
        Heading level (0 for normal text, 1-6 for headings)
    """
    # Calculate size ratio
    ratio = font_size / base_font_size

    # Define thresholds for heading levels
    # Level 1: 2x or more (very large titles)
    # Level 2: 1.5x - 2x (section titles)
    # Level 3: 1.2x - 1.5x (subsection titles)
    # Level 4: 1.1x - 1.2x (minor headings)
    # Normal: < 1.1x

    if ratio >= 2.0:
        return 1
    elif ratio >= 1.5:
        return 2
    elif ratio >= 1.2:
        return 3
    elif ratio >= 1.1:
        return 4
    else:
        return 0  # Normal text


def _merge_consecutive_headings(text: str) -> str:
    """Merge consecutive headings of the same level that are likely part of the same title.

    When a title in the PDF is split across multiple lines, it gets extracted as
    multiple heading markers. This function merges them back together.

    Args:
        text: Extracted text with HEADING markers

    Returns:
        Text with consecutive headings of the same level merged
    """
    lines = text.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Check if this is a heading
        if line.startswith("HEADING"):
            # Extract level and text
            match = re.match(r"HEADING(\d):(.*)", line)
            if match:
                level = match.group(1)
                heading_text = match.group(2).strip()

                # Look ahead for consecutive headings of the same level
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()

                    # Check if it's empty line (skip it)
                    if not next_line:
                        j += 1
                        continue

                    # Check if it's another heading of the same level
                    next_match = re.match(r"HEADING(\d):(.*)", next_line)
                    starts_new_section = next_match and SECTION_NUMBER_PATTERN.match(
                        next_match.group(2).strip()
                    )
                    if (
                        next_match
                        and next_match.group(1) == level
                        and not starts_new_section
                    ):
                        # Merge with current heading
                        heading_text += " " + next_match.group(2).strip()
                        j += 1
                    else:
                        # Different level or not a heading - stop merging
                        break

                # Add merged heading
                result.append(f"HEADING{level}:{heading_text}")

                # Skip the lines we merged
                i = j
                continue

        # Not a heading or not matched - add as is
        result.append(lines[i])
        i += 1

    return "\n".join(result)


def extract_pdf(file_path: Path, job_id: str | None = None) -> ExtractedData:
    """Extract text and images from PDF file with inline image positioning.

    Args:
        file_path: Path to PDF file
        job_id: Optional job ID for organizing extracted images

    Returns:
        ExtractedData with text, images, and metadata
    """
    text_content = []
    images_list = []
    metadata = {}

    try:
        # Open PDF
        doc = fitz.open(str(file_path))

        # Extract metadata
        metadata = {
            "title": doc.metadata.get("title", ""),
            "author": doc.metadata.get("author", ""),
            "subject": doc.metadata.get("subject", ""),
            "pages": str(doc.page_count),
        }

        # First pass: detect tables and find the "normal" text size, i.e. the
        # size carrying most characters outside tables (table text is often
        # smaller and would otherwise turn body paragraphs into headings)
        tables_by_page = [_extract_tables(page) for page in doc]
        chars_by_size: Counter[float] = Counter()
        for page, table_blocks in zip(doc, tables_by_page):
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    if _is_inside_table(line["bbox"], table_blocks):
                        continue
                    for span in line.get("spans", []):
                        size = round(span.get("size", 0), 1)
                        if size > 0:
                            chars_by_size[size] += len(span.get("text", "").strip())

        base_font_size = (
            chars_by_size.most_common(1)[0][0] if chars_by_size else 12
        )  # Default fallback

        running_texts = _find_running_texts(doc)

        # Process each page
        for page_num, page in enumerate(doc, start=1):
            # Get page dimensions to detect header/footer areas
            page_height = page.rect.height

            # Get page layout with text blocks and image positions
            blocks = page.get_text("dict")["blocks"]

            # Build a map of image xrefs to saved paths
            image_map = {}
            image_list = page.get_images(full=True)
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                try:
                    # Extract and save image
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    base_name = f"pdf_page{page_num}_img{img_index}"
                    image_path = save_image(image_bytes, image_ext, base_name, job_id)
                    images_list.append(image_path)
                    image_map[xref] = image_path

                except Exception as e:
                    print(
                        f"Error extracting image {img_index} from page {page_num}: {e}"
                    )
                    continue

            # Tables become pseudo-blocks placed at their vertical position
            table_blocks = tables_by_page[page_num - 1]

            # Sort blocks by vertical position (top to bottom, left to right)
            sorted_blocks = sorted(
                blocks + table_blocks, key=lambda b: (b["bbox"][1], b["bbox"][0])
            )

            # Flatten the page into rows, tables and images, top to bottom
            items = _page_items(sorted_blocks, table_blocks, page_height, running_texts)
            items = _merge_wrapped_toc_rows(items)

            page_content: list[str] = []
            builder = ParagraphBuilder(page_content)
            prev_block = None
            for kind, block_id, payload in items:
                if kind == "table":
                    builder.flush()
                    page_content.extend(payload)
                    page_content.append("")
                    continue
                if kind == "image":
                    builder.break_lists()
                    if image_map:
                        # Images are matched to image blocks in reading order
                        xref = next(iter(image_map))
                        page_content.append(f"IMAGE:{image_map.pop(xref)}")
                    continue
                if kind == "toc":
                    builder.break_lists()
                    level, title = payload
                    page_content.append(f"TOC_ENTRY{level}:{title}")
                    continue

                row: VisualRow = payload
                first_in_block = block_id != prev_block
                prev_block = block_id
                heading_level = _detect_heading_level(row.size, base_font_size)
                if heading_level > 0:
                    builder.break_lists()
                    page_content.append(f"HEADING{heading_level}:{row.plain}")
                    continue
                builder.add_row(row, first_in_block)
            builder.flush()

            if page_num == 1 and doc.page_count > 1:
                page_content = _format_cover_page(page_content)

            # Add page content with page marker
            if page_content:
                page_text = "\n".join(page_content)
                text_content.append(f"# Page {page_num}\n\n{page_text}\n")

        doc.close()

    except Exception as e:
        raise ValueError(f"Failed to extract PDF: {str(e)}")

    # Combine all text
    full_text = "\n".join(text_content)

    # Post-process: merge consecutive headings of the same level
    full_text = _merge_consecutive_headings(full_text)
    full_text = _normalize_heading_levels(full_text)

    return ExtractedData(text=full_text, images=images_list, metadata=metadata)
