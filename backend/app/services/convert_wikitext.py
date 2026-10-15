"""MediaWiki text conversion service.

This module converts extracted text to MediaWiki markup format.
"""

import re

from app.models.dto import ExtractedData


def to_wikitext(extracted: ExtractedData) -> tuple[str, list[str]]:
    """Convert extracted text to MediaWiki markup.

    Args:
        extracted: ExtractedData containing text and images

    Returns:
        Tuple of (wikitext, warnings)
    """
    warnings = []
    lines = extracted.text.split("\n")
    wiki_lines = []

    # Track if we're inside a table
    in_table = False

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        i += 1

        # Handle PDF list items: a whole run of items is rendered at once
        if line.startswith("LIST_ITEM:"):
            items, i = _collect_list_run(lines, i - 1)
            wiki_lines.extend(_render_list_run(items))
            wiki_lines.append("")
            continue

        # Skip empty lines outside tables
        if not line:
            if not in_table:
                wiki_lines.append("")
            continue

        # Handle headings (DOCX style markers)
        if line.startswith("HEADING"):
            match = re.match(r"HEADING(\d):(.+)", line)
            if match:
                level = int(match.group(1))
                text = match.group(2).strip()
                equals = "=" * (level + 1)  # MediaWiki uses more = for lower levels
                wiki_lines.append(f"{equals} {text} {equals}")
                wiki_lines.append("")
                continue

        # Handle table-of-contents entries as internal links to sections
        if line.startswith("TOC_ENTRY"):
            match = re.match(r"TOC_ENTRY(\d):(.+)", line)
            if match:
                level = int(match.group(1))
                title = match.group(2).strip()
                wiki_lines.append(f"{'*' * level} [[#{title}|{title}]]")
                continue

        # Handle bullet lists
        if line.startswith("LIST_BULLET:"):
            text = line[12:].strip()  # Remove "LIST_BULLET:" prefix
            formatted = _convert_formatting(text)
            wiki_lines.append(f"* {formatted}")
            continue

        # Handle numbered lists
        if line.startswith("LIST_NUMBER:"):
            text = line[12:].strip()  # Remove "LIST_NUMBER:" prefix
            formatted = _convert_formatting(text)
            wiki_lines.append(f"# {formatted}")
            continue

        # Handle tables
        if line == "TABLE_START":
            in_table = True
            wiki_lines.append('{| class="zcsTable"')
            continue
        elif line == "TABLE_END":
            in_table = False
            wiki_lines.append("|}")
            wiki_lines.append("")
            continue
        elif line.startswith("HEADER_ROW:"):
            cells = line[11:].split(" | ")
            wiki_lines.append("|-")
            for cell in cells:
                wiki_lines.append(f"! {cell.strip()}")
            continue
        elif line.startswith("ROW:"):
            cells = line[4:].split(" | ")
            wiki_lines.append("|-")
            for cell in cells:
                wiki_lines.append(f"| {cell.strip()}")
            continue

        # Handle PDF page markers (optional: remove or convert)
        if line.startswith("# Page "):
            # Skip page markers or convert to comments
            continue

        # Convert bold/italic and images (basic pattern matching)
        line = _convert_formatting(line)

        # Convert URLs to MediaWiki format
        line = _convert_urls(line)

        wiki_lines.append(line)

    wikitext = "\n".join(wiki_lines).strip() + "\n"
    # One blank line is enough to separate paragraphs
    wikitext = re.sub(r"\n{3,}", "\n\n", wikitext)

    # Generate warnings if needed
    if not extracted.text.strip():
        warnings.append("No text content extracted from document")

    return wikitext, warnings


ListItem = tuple[str, int, int | None, str]

LIST_ITEM_PATTERN = re.compile(r"LIST_ITEM:([bn]):(\d+):(\d*):(.*)")


def _collect_list_run(lines: list[str], start: int) -> tuple[list[ListItem], int]:
    """Collect consecutive LIST_ITEM markers starting at ``start``.

    Blank lines and page markers between items don't break the list (a list
    may continue on the next page). A top-level item numbered 1 starts a new
    list.

    Args:
        lines: Extracted text lines
        start: Index of the first LIST_ITEM line

    Returns:
        Tuple of (items as (kind, level, number, text), index after the run)
    """
    items: list[ListItem] = []
    i = start
    end = start
    while i < len(lines):
        line = lines[i].strip()
        if not line or line.startswith("# Page "):
            i += 1
            continue
        match = LIST_ITEM_PATTERN.match(line)
        if not match:
            break
        kind, level, number, text = match.groups()
        number_value = int(number) if number else None
        if items and int(level) == 1 and kind == "n" and number_value == 1:
            break
        text = _convert_urls(_convert_formatting(text.strip()))
        items.append((kind, int(level), number_value, text))
        i += 1
        end = i
    return items, end


def _numbering_is_sequential(items: list[ListItem]) -> bool:
    """Check whether wiki "#" numbering would reproduce the item numbers."""
    expected: dict[int, int] = {}
    for kind, level, number, _ in items:
        # Deeper levels restart when a shallower item appears
        for deeper in [lv for lv in expected if lv > level]:
            del expected[deeper]
        if kind != "n":
            expected.pop(level, None)
            continue
        if number is not None and number != expected.get(level, 1):
            return False
        expected[level] = (number or expected.get(level, 1)) + 1
    return True


def _render_list_run(items: list[ListItem]) -> list[str]:
    """Render a run of list items as wiki lists.

    Wiki "*"/"#" syntax is used when possible; when the numbering doesn't
    start at 1 (e.g. a list resumed after a table) HTML lists with explicit
    item numbers are used, since "#" always counts from 1.
    """
    if _numbering_is_sequential(items):
        lines = []
        prefix_kinds: list[str] = []
        for kind, level, _, text in items:
            prefix_kinds = prefix_kinds[: level - 1]
            prefix_kinds += ["b"] * (level - 1 - len(prefix_kinds)) + [kind]
            prefix = "".join("#" if k == "n" else "*" for k in prefix_kinds)
            lines.append(f"{prefix} {text}")
        return lines

    html: list[str] = []
    stack: list[str] = []
    for kind, level, number, text in items:
        tag = "ol" if kind == "n" else "ul"
        while len(stack) > level:
            html.append(f"</li></{stack.pop()}>")
        if len(stack) == level and stack[-1] != tag:
            html.append(f"</li></{stack.pop()}>")
        elif len(stack) == level:
            html.append("</li>")
        while len(stack) < level:
            html.append(f"<{tag}>")
            stack.append(tag)
        value = f' value="{number}"' if tag == "ol" and number is not None else ""
        html.append(f"<li{value}>{text}")
    while stack:
        html.append(f"</li></{stack.pop()}>")
    return html


def _convert_formatting(text: str) -> str:
    """Convert formatting markers to MediaWiki markup.

    Args:
        text: Text with formatting markers (BOLD:, ITALIC:, BOLDITALIC:)

    Returns:
        Text with MediaWiki formatting (''', '', etc.)
    """
    # Process text sequentially to handle markers correctly
    result = []
    i = 0
    while i < len(text):
        # Check for IMAGE marker
        if text[i:].startswith("IMAGE:"):
            i += 6  # len("IMAGE:")
            # Find the end of the filename (next marker or end)
            end = i
            while end < len(text):
                if (
                    text[end:].startswith("BOLD:")
                    or text[end:].startswith("ITALIC:")
                    or text[end:].startswith("BOLDITALIC:")
                    or text[end:].startswith("IMAGE:")
                ):
                    break
                end += 1
            filename = text[i:end]
            # Extract just the filename without the /immagini/ prefix
            clean_filename = filename.split("/")[-1] if "/" in filename else filename
            result.append(
                f'<div class="img_container">[[Immagine:{clean_filename}]]</div>'
            )
            i = end
        # Check for BOLDITALIC marker
        elif text[i:].startswith("BOLDITALIC:"):
            i += 11  # len("BOLDITALIC:")
            # Find the end of this formatted section (next marker or end)
            end = i
            while end < len(text):
                if (
                    text[end:].startswith("BOLD:")
                    or text[end:].startswith("ITALIC:")
                    or text[end:].startswith("BOLDITALIC:")
                    or text[end:].startswith("IMAGE:")
                ):
                    break
                end += 1
            result.append(f"'''''{text[i:end]}'''''")
            i = end
        # Check for BOLD marker
        elif text[i:].startswith("BOLD:"):
            i += 5  # len("BOLD:")
            end = i
            while end < len(text):
                if (
                    text[end:].startswith("BOLD:")
                    or text[end:].startswith("ITALIC:")
                    or text[end:].startswith("BOLDITALIC:")
                    or text[end:].startswith("IMAGE:")
                ):
                    break
                end += 1
            result.append(f"'''{text[i:end]}'''")
            i = end
        # Check for ITALIC marker
        elif text[i:].startswith("ITALIC:"):
            i += 7  # len("ITALIC:")
            end = i
            while end < len(text):
                if (
                    text[end:].startswith("BOLD:")
                    or text[end:].startswith("ITALIC:")
                    or text[end:].startswith("BOLDITALIC:")
                    or text[end:].startswith("IMAGE:")
                ):
                    break
                end += 1
            result.append(f"''{text[i:end]}''")
            i = end
        else:
            result.append(text[i])
            i += 1

    return "".join(result)


def _convert_urls(text: str) -> str:
    """Convert plain URLs to MediaWiki link format.

    Args:
        text: Text possibly containing URLs

    Returns:
        Text with MediaWiki formatted links
    """
    # Match http/https URLs
    url_pattern = r"(https?://[^\s]+)"
    text = re.sub(url_pattern, r"[\1]", text)

    return text
