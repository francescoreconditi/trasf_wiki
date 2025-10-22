"""PDF extraction service using PyMuPDF.

This module handles extraction of text and images from PDF files.
"""

from pathlib import Path

import fitz  # PyMuPDF

from app.models.dto import ExtractedData
from app.services.storage import save_image


def extract_pdf(file_path: Path) -> ExtractedData:
    """Extract text and images from PDF file.

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
            # Extract text
            page_text = page.get_text("text")
            if page_text.strip():
                text_content.append(f"# Page {page_num}\n\n{page_text}\n")

            # Extract images
            image_list = page.get_images(full=True)
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                try:
                    # Extract image
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # Save image
                    base_name = f"page{page_num}_img{img_index}"
                    image_path = save_image(image_bytes, image_ext, base_name)
                    images_list.append(image_path)

                except Exception as e:
                    # Skip problematic images
                    print(
                        f"Error extracting image {img_index} from page {page_num}: {e}"
                    )
                    continue

        doc.close()

    except Exception as e:
        raise ValueError(f"Failed to extract PDF: {str(e)}")

    # Combine all text
    full_text = "\n".join(text_content)

    return ExtractedData(text=full_text, images=images_list, metadata=metadata)
