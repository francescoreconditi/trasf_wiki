"""File serving router.

Handles serving of output files and image downloads.
"""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

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
