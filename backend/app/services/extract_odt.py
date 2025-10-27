"""ODT extraction service using odfpy.

This module handles extraction of text and images from OpenDocument Text files.
"""

import base64
import zipfile
from pathlib import Path

from odf import teletype, text as odf_text
from odf.opendocument import load

from app.models.dto import ExtractedData
from app.services.storage import save_image


def _extract_text_from_element(element, image_map: dict[str, str]) -> str:
    """Extract text from ODF element with formatting markers.

    Args:
        element: ODF element to extract text from
        image_map: Dictionary mapping image names to saved paths

    Returns:
        Text with formatting markers
    """
    result = []

    # Get all text from element
    text_content = teletype.extractText(element)
    if text_content:
        result.append(text_content)

    return "".join(result)


def _detect_heading_style(paragraph) -> int:
    """Detect if paragraph is a heading and return its level.

    Args:
        paragraph: ODF paragraph element

    Returns:
        Heading level (0 for normal text, 1-6 for headings)
    """
    # Check style name
    style_name = paragraph.getAttribute("stylename")
    if not style_name:
        return 0

    style_lower = style_name.lower()

    # Common heading style patterns in ODT
    if "heading" in style_lower or "title" in style_lower:
        # Try to extract level from style name
        if "1" in style_name or "heading_20_1" in style_lower:
            return 1
        elif "2" in style_name or "heading_20_2" in style_lower:
            return 2
        elif "3" in style_name or "heading_20_3" in style_lower:
            return 3
        elif "4" in style_name or "heading_20_4" in style_lower:
            return 4
        elif "5" in style_name or "heading_20_5" in style_lower:
            return 5
        elif "6" in style_name or "heading_20_6" in style_lower:
            return 6
        else:
            return 1  # Default to H1 if level unclear

    return 0


def _extract_images_from_odt(
    file_path: Path, job_id: str | None = None
) -> dict[str, str]:
    """Extract images from ODT file (which is a ZIP).

    Args:
        file_path: Path to ODT file
        job_id: Optional job ID for organizing images

    Returns:
        Dictionary mapping internal image names to saved paths
    """
    image_map = {}

    try:
        with zipfile.ZipFile(file_path, "r") as odt_zip:
            # List all files in Pictures directory
            image_files = [
                name for name in odt_zip.namelist() if name.startswith("Pictures/")
            ]

            for img_index, image_name in enumerate(image_files):
                try:
                    # Read image data
                    image_bytes = odt_zip.read(image_name)

                    # Determine file extension
                    ext = Path(image_name).suffix.lstrip(".")
                    if not ext:
                        ext = "png"  # Default fallback

                    # Generate base name
                    base_name = f"odt_img{img_index}"

                    # Save image
                    saved_path = save_image(image_bytes, ext, base_name, job_id)
                    image_map[image_name] = saved_path

                except Exception as e:
                    print(f"[WARN] Error extracting image {image_name}: {e}")
                    continue

    except Exception as e:
        print(f"[WARN] Error opening ODT as ZIP: {e}")

    return image_map


def extract_odt(file_path: Path, job_id: str | None = None) -> ExtractedData:
    """Extract text and images from ODT file.

    Args:
        file_path: Path to ODT file
        job_id: Optional job ID for organizing extracted images

    Returns:
        ExtractedData with text, images, and metadata
    """
    text_content = []
    images_list = []
    metadata = {}

    try:
        # First extract images from ZIP structure
        image_map = _extract_images_from_odt(file_path, job_id)
        images_list = list(image_map.values())

        # Load ODT document
        doc = load(str(file_path))

        # Extract metadata
        try:
            meta = doc.meta
            metadata = {
                "title": teletype.extractText(meta.getElementsByType(odf_text.Title)[0])
                if meta.getElementsByType(odf_text.Title)
                else "",
                "author": teletype.extractText(
                    meta.getElementsByType(odf_text.InitialCreator)[0]
                )
                if meta.getElementsByType(odf_text.InitialCreator)
                else "",
                "subject": teletype.extractText(
                    meta.getElementsByType(odf_text.Subject)[0]
                )
                if meta.getElementsByType(odf_text.Subject)
                else "",
            }
        except Exception as e:
            print(f"[WARN] Error extracting metadata: {e}")
            metadata = {}

        # Extract text content
        paragraphs = doc.text.getElementsByType(odf_text.P)

        for para in paragraphs:
            # Check if paragraph is a heading
            heading_level = _detect_heading_style(para)

            # Extract text
            para_text = teletype.extractText(para).strip()

            if not para_text:
                continue

            if heading_level > 0:
                # Mark as heading
                text_content.append(f"HEADING{heading_level}:{para_text}")
            else:
                # Check for bold/italic by examining spans
                has_formatting = False
                spans = para.getElementsByType(odf_text.Span)

                if spans:
                    span_texts = []
                    for span in spans:
                        span_text = teletype.extractText(span).strip()
                        if span_text:
                            # Get style name to detect formatting
                            style = span.getAttribute("stylename")
                            if style:
                                style_lower = style.lower()
                                if "bold" in style_lower and "italic" in style_lower:
                                    span_texts.append(f"BOLDITALIC:{span_text}")
                                    has_formatting = True
                                elif "bold" in style_lower or "strong" in style_lower:
                                    span_texts.append(f"BOLD:{span_text}")
                                    has_formatting = True
                                elif (
                                    "italic" in style_lower or "emphasis" in style_lower
                                ):
                                    span_texts.append(f"ITALIC:{span_text}")
                                    has_formatting = True
                                else:
                                    span_texts.append(span_text)
                            else:
                                span_texts.append(span_text)

                    if has_formatting:
                        text_content.append("".join(span_texts))
                    else:
                        text_content.append(para_text)
                else:
                    # No spans, just add paragraph text
                    text_content.append(para_text)

        # Handle lists
        lists = doc.text.getElementsByType(odf_text.List)
        for lst in lists:
            list_items = lst.getElementsByType(odf_text.ListItem)
            for item in list_items:
                item_text = teletype.extractText(item).strip()
                if item_text:
                    # Mark as list item
                    text_content.append(f"LIST:{item_text}")

        # Insert image markers at appropriate positions
        # For ODT, we insert all images at the end as a section
        if images_list:
            text_content.append("\nHEADING2:Immagini\n")
            for img_path in images_list:
                text_content.append(f"IMAGE:{img_path}")

    except Exception as e:
        raise ValueError(f"Failed to extract ODT: {str(e)}")

    # Combine all text
    full_text = "\n".join(text_content)

    return ExtractedData(text=full_text, images=images_list, metadata=metadata)
