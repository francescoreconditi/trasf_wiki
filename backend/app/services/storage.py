"""File storage management service.

This module handles all file operations including uploads, image saving,
and output storage with proper sanitization and collision prevention.
"""

import re
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import config


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to remove dangerous characters.

    Args:
        filename: Original filename to sanitize

    Returns:
        Sanitized filename safe for filesystem operations
    """
    # Remove path separators and dangerous characters
    name = re.sub(r'[<>:"/\\|?*]', "", filename)
    # Remove leading/trailing dots and spaces
    name = name.strip(". ")
    # If empty after sanitization, use default
    return name if name else "unnamed"


def generate_job_id() -> str:
    """Generate unique job identifier.

    Returns:
        UUID-based job ID as string
    """
    return str(uuid.uuid4())


def save_upload(file: UploadFile) -> Path:
    """Save uploaded file to upload directory.

    Args:
        file: FastAPI UploadFile object

    Returns:
        Absolute path to saved file
    """
    job_id = generate_job_id()
    original_name = file.filename or "upload"
    safe_name = sanitize_filename(original_name)

    # Add job_id prefix to avoid collisions
    filename = f"{job_id}_{safe_name}"
    upload_path = config.get_absolute_path(config.upload_dir) / filename

    # Save file
    with upload_path.open("wb") as buffer:
        buffer.write(file.file.read())

    return upload_path


def save_image(
    image_bytes: bytes,
    extension: str,
    base_name: str = "img",
    job_id: str | None = None,
) -> str:
    """Save image bytes to images directory.

    Args:
        image_bytes: Image binary data
        extension: File extension (e.g., 'png', 'jpg')
        base_name: Base name for the image file
        job_id: Optional job ID to organize images in subdirectories

    Returns:
        Relative path for frontend access (e.g., '/immagini/job_id/img-uuid.png')
    """
    # Generate unique filename with full UUID for guaranteed uniqueness
    unique_id = str(uuid.uuid4())
    safe_base = sanitize_filename(base_name)
    filename = f"{safe_base}-{unique_id}.{extension.lower()}"

    # Save to images directory (in project root)
    images_path = config.get_project_path(config.images_dir)

    # If job_id is provided, create subdirectory
    if job_id:
        job_images_path = images_path / job_id
        job_images_path.mkdir(parents=True, exist_ok=True)
        file_path = job_images_path / filename
        relative_url = f"/immagini/{job_id}/{filename}"
    else:
        file_path = images_path / filename
        relative_url = f"/immagini/{filename}"

    # Write image to disk
    with file_path.open("wb") as f:
        f.write(image_bytes)

    # Return relative URL for frontend
    return relative_url


def save_output(original_filename: str, wikitext: str) -> Path:
    """Save converted MediaWiki text to output directory.

    Args:
        original_filename: Original filename (e.g., 'pippo.pdf')
        wikitext: MediaWiki formatted text

    Returns:
        Absolute path to saved output file
    """
    # Remove extension and add .wiki
    base_name = sanitize_filename(original_filename)
    name_without_ext = base_name.rsplit(".", 1)[0] if "." in base_name else base_name
    filename = f"{name_without_ext}.wiki"

    # Save to output directory (in project root)
    output_path = config.get_project_path(config.output_dir)
    file_path = output_path / filename

    with file_path.open("w", encoding="utf-8") as f:
        f.write(wikitext)

    return file_path


def cleanup_upload(file_path: Path) -> None:
    """Remove uploaded file after processing.

    Args:
        file_path: Path to file to remove
    """
    try:
        if file_path.exists():
            file_path.unlink()
    except Exception:
        # Log error in production but don't fail the request
        pass
