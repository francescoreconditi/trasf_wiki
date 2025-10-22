"""PDF extraction service using PyMuPDF.

This module handles extraction of text and images from PDF files.
"""

from pathlib import Path

import fitz  # PyMuPDF

from app.models.dto import ExtractedData
from app.services.storage import save_image


def extract_pdf(file_path: Path) -> ExtractedData:
    """Extract text and images from PDF file with inline image positioning.

    Args:
        file_path: Path to PDF file

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

        # Process each page
        for page_num, page in enumerate(doc, start=1):
            # Get page dimensions to detect header/footer areas
            page_rect = page.rect
            page_height = page_rect.height

            # Define header and footer margins (in points)
            # Typical: 50-70 points (~1.7-2.4 cm) for header/footer
            header_margin = 70  # Top margin to exclude
            footer_margin = 70  # Bottom margin to exclude

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
                    image_path = save_image(image_bytes, image_ext, base_name)
                    images_list.append(image_path)
                    image_map[xref] = image_path

                except Exception as e:
                    print(
                        f"Error extracting image {img_index} from page {page_num}: {e}"
                    )
                    continue

            # Sort blocks by vertical position (top to bottom, left to right)
            sorted_blocks = sorted(blocks, key=lambda b: (b["bbox"][1], b["bbox"][0]))

            # Process blocks in order
            page_content = []
            for block in sorted_blocks:
                block_type = block.get("type", 0)
                bbox = block.get("bbox", [0, 0, 0, 0])

                # Check if block is in header or footer area
                block_top = bbox[1]  # y0 coordinate (top of block)
                block_bottom = bbox[3]  # y1 coordinate (bottom of block)

                # Skip blocks in header area (top of page)
                if block_top < header_margin:
                    continue

                # Skip blocks in footer area (bottom of page)
                if block_bottom > (page_height - footer_margin):
                    continue

                if block_type == 0:  # Text block
                    # Extract text from lines
                    lines = block.get("lines", [])
                    for line in lines:
                        spans = line.get("spans", [])
                        line_text = "".join(span.get("text", "") for span in spans)
                        if line_text.strip():
                            page_content.append(line_text)

                elif block_type == 1:  # Image block
                    # Find the image xref for this block
                    # Match by comparing image dimensions/position
                    # Since we already saved all images, insert marker
                    if image_map:
                        # Use the first available image from map
                        # (Better heuristic could match by position, but this works for most cases)
                        for xref, img_path in list(image_map.items()):
                            page_content.append(f"IMAGE:{img_path}")
                            # Remove from map to avoid duplicates
                            del image_map[xref]
                            break

            # Add page content with page marker
            if page_content:
                page_text = "\n".join(page_content)
                text_content.append(f"# Page {page_num}\n\n{page_text}\n")

        doc.close()

    except Exception as e:
        raise ValueError(f"Failed to extract PDF: {str(e)}")

    # Combine all text
    full_text = "\n".join(text_content)

    return ExtractedData(text=full_text, images=images_list, metadata=metadata)
