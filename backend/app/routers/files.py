"""File serving router.

Handles serving of output files and image downloads.
"""

import io
import zipfile
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import config

router = APIRouter(tags=["files"])


@router.get(
    "/files/output/{job_id}",
    response_class=FileResponse,
    summary="Download converted MediaWiki text file",
)
async def download_output(job_id: str) -> FileResponse:
    """Download the converted MediaWiki text file for a specific job.

    Args:
        job_id: Unique job identifier

    Returns:
        FileResponse with the .wiki file

    Raises:
        HTTPException: If file not found
    """
    # Sanitize job_id to prevent path traversal
    if not job_id.replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid job ID")

    output_path = config.get_absolute_path(config.output_dir) / f"{job_id}.wiki"

    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=str(output_path),
        filename=f"{job_id}.wiki",
        media_type="text/plain",
    )


@router.get(
    "/files/images/{job_id}/download-all",
    response_class=StreamingResponse,
    summary="Download all extracted images as ZIP",
)
async def download_all_images(job_id: str) -> StreamingResponse:
    """Download all extracted images for a specific job as a ZIP file.

    Args:
        job_id: Unique job identifier

    Returns:
        StreamingResponse with ZIP file containing all images

    Raises:
        HTTPException: If no images found or invalid job ID
    """
    # Sanitize job_id to prevent path traversal
    if not job_id.replace("-", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid job ID")

    # Get images directory for this job (use get_project_path like save_image does)
    images_dir = config.get_project_path(config.images_dir) / job_id

    if not images_dir.exists():
        raise HTTPException(status_code=404, detail="Images directory not found")

    # Get all image files
    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp"]:
        image_files.extend(images_dir.glob(ext))

    if not image_files:
        raise HTTPException(status_code=404, detail="No images found for this job")

    # Create ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zip_file:
        for image_file in image_files:
            # Add file to zip with its name (without full path)
            zip_file.write(image_file, arcname=image_file.name)

    # Seek to beginning of buffer
    zip_buffer.seek(0)

    # Return as streaming response
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={job_id}_images.zip"},
    )
