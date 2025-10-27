"""RTF extraction service using striprtf.

This module handles extraction of text from Rich Text Format files.
Note: RTF image extraction is complex and not implemented in this version.
"""

import re
from pathlib import Path

from striprtf.striprtf import rtf_to_text

from app.models.dto import ExtractedData


def _detect_heading_from_text(line: str) -> tuple[int, str]:
    """Detect if a line is a heading based on text patterns.

    Args:
        line: Line of text to analyze

    Returns:
        Tuple of (heading_level, cleaned_text)
        heading_level is 0 for normal text, 1-6 for headings
    """
    # Check for common heading patterns
    stripped = line.strip()

    # Check for numbered sections like "1. Title", "1.1 Title", etc.
    number_pattern = r"^(\d+\.)+\s+(.+)$"
    match = re.match(number_pattern, stripped)
    if match:
        # Count dots to determine depth
        dots = stripped.split()[0].count(".")
        level = min(dots, 6)  # Max heading level is 6
        text = match.group(2).strip()
        return (level, text)

    # Check for ALL CAPS (common for titles)
    if len(stripped) > 3 and stripped.isupper() and not stripped.endswith("."):
        return (1, stripped)

    # Check for short lines that might be titles (< 80 chars, no period at end)
    if (
        len(stripped) < 80
        and len(stripped) > 3
        and not stripped.endswith(".")
        and not stripped.endswith(",")
        and not stripped.endswith(";")
    ):
        # Check if line starts with capital and doesn't have multiple sentences
        if stripped[0].isupper() and stripped.count(".") == 0:
            # Likely a heading
            return (2, stripped)

    return (0, stripped)


def _parse_rtf_formatting(text: str) -> list[str]:
    """Parse text and detect formatting patterns.

    Args:
        text: Plain text extracted from RTF

    Returns:
        List of text lines with formatting markers
    """
    lines = text.split("\n")
    formatted_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append("")
            continue

        # Detect headings
        heading_level, clean_text = _detect_heading_from_text(line)

        if heading_level > 0:
            formatted_lines.append(f"HEADING{heading_level}:{clean_text}")
        else:
            # Check for list patterns
            # Bullet lists: • text, - text, * text
            bullet_pattern = r"^[•\-\*]\s+(.+)$"
            bullet_match = re.match(bullet_pattern, line)
            if bullet_match:
                formatted_lines.append(f"LIST:{bullet_match.group(1)}")
                continue

            # Numbered lists: 1. text, a) text, i. text
            num_list_pattern = r"^(\d+|[a-z]|[ivxlcdm]+)[\.\)]\s+(.+)$"
            num_match = re.match(num_list_pattern, line.lower())
            if num_match:
                formatted_lines.append(f"LIST:{num_match.group(2)}")
                continue

            # Normal text
            formatted_lines.append(line)

    return formatted_lines


def extract_rtf(file_path: Path, job_id: str | None = None) -> ExtractedData:
    """Extract text from RTF file.

    Args:
        file_path: Path to RTF file
        job_id: Optional job ID (not used for RTF, no image extraction)

    Returns:
        ExtractedData with text and metadata

    Note:
        RTF image extraction is not implemented due to complexity.
        Images embedded in RTF files will not be extracted.
    """
    text_content = []
    images_list = []
    metadata = {}

    try:
        # Read RTF file
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            rtf_content = f.read()

        # Extract plain text using striprtf
        plain_text = rtf_to_text(rtf_content)

        # Parse and format text
        formatted_lines = _parse_rtf_formatting(plain_text)

        # Try to extract metadata from RTF header
        try:
            # Extract title (if present in RTF info block)
            title_match = re.search(r"\\title\s+([^}]+)", rtf_content)
            if title_match:
                metadata["title"] = title_match.group(1).strip()

            # Extract author (if present)
            author_match = re.search(r"\\author\s+([^}]+)", rtf_content)
            if author_match:
                metadata["author"] = author_match.group(1).strip()

            # Extract subject (if present)
            subject_match = re.search(r"\\subject\s+([^}]+)", rtf_content)
            if subject_match:
                metadata["subject"] = subject_match.group(1).strip()

        except Exception as e:
            print(f"[WARN] Error extracting RTF metadata: {e}")

        # Combine formatted text
        text_content = formatted_lines

    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
                rtf_content = f.read()
            plain_text = rtf_to_text(rtf_content)
            formatted_lines = _parse_rtf_formatting(plain_text)
            text_content = formatted_lines
        except Exception as e:
            raise ValueError(
                f"Failed to read RTF file with multiple encodings: {str(e)}"
            )

    except Exception as e:
        raise ValueError(f"Failed to extract RTF: {str(e)}")

    # Join text with newlines
    full_text = "\n".join(text_content)

    # Add note about image extraction limitation
    if "image" in rtf_content.lower() or "pict" in rtf_content.lower():
        # RTF might contain images but we can't extract them easily
        full_text += (
            "\n\nHEADING2:Nota\n"
            "Le immagini embedded in RTF non possono essere estratte automaticamente. "
            "Si consiglia di convertire il file in DOCX per una migliore estrazione delle immagini."
        )

    return ExtractedData(text=full_text, images=images_list, metadata=metadata)
