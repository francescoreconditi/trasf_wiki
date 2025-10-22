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

    for line in lines:
        line = line.strip()

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
            wiki_lines.append('{| class="wikitable"')
            continue
        elif line == "TABLE_END":
            in_table = False
            wiki_lines.append("|}")
            wiki_lines.append("")
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

    wikitext = "\n".join(wiki_lines)

    # Generate warnings if needed
    if not extracted.text.strip():
        warnings.append("No text content extracted from document")

    return wikitext, warnings


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
