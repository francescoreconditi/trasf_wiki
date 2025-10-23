"""File conversion router.

Handles PDF/DOCX upload and conversion to MediaWiki format.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import config
from app.models.dto import ConvertResponse
from app.services.convert_wikitext import to_wikitext
from app.services.extract_docx import extract_docx
from app.services.extract_pdf import extract_pdf
from app.services.storage import (
    cleanup_upload,
    generate_job_id,
    save_output,
    save_upload,
)

router = APIRouter(tags=["convert"])


@router.post(
    "/convert",
    response_model=ConvertResponse,
    summary="Convert PDF/DOCX to MediaWiki markup",
    description="Upload a PDF or DOCX file and receive MediaWiki formatted text with extracted images",
)
async def convert_file(file: UploadFile = File(...)) -> ConvertResponse:
    """Convert uploaded PDF/DOCX file to MediaWiki format.

    Args:
        file: Uploaded PDF or DOCX file

    Returns:
        ConvertResponse with converted text, images, and warnings

    Raises:
        HTTPException: If file format is unsupported or processing fails
    """
    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = file.filename.lower().rsplit(".", 1)[-1]
    if f".{ext}" not in config.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(config.allowed_extensions)}",
        )

    # Check file size (basic check)
    # Note: FastAPI has max_upload_size, but we can add custom validation here
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to start

    if file_size > config.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {config.max_file_size_mb}MB",
        )

    # Generate job_id BEFORE extraction to organize images by job
    job_id = generate_job_id()

    # Save uploaded file
    try:
        upload_path = save_upload(file)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to save upload: {str(e)}"
        ) from e

    # Extract content based on file type (pass job_id to organize images)
    try:
        if ext == "pdf":
            extracted = extract_pdf(upload_path, job_id)
        elif ext == "docx":
            extracted = extract_docx(upload_path, job_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as e:
        cleanup_upload(upload_path)
        raise HTTPException(
            status_code=500, detail=f"Extraction failed: {str(e)}"
        ) from e

    # Convert to MediaWiki format
    try:
        wikitext, warnings = to_wikitext(extracted)
    except Exception as e:
        cleanup_upload(upload_path)
        raise HTTPException(
            status_code=500, detail=f"Conversion failed: {str(e)}"
        ) from e

    # Save output with original filename
    try:
        save_output(file.filename, wikitext)
    except Exception as e:
        # Not critical - we can still return the result
        warnings.append(f"Failed to save output file: {str(e)}")

    # Clean up uploaded file
    cleanup_upload(upload_path)

    return ConvertResponse(
        id=job_id,
        filename=file.filename,
        mediawiki_text=wikitext,
        images=extracted.images,
        warnings=warnings,
    )
