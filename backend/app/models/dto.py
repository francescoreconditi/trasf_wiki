"""Data Transfer Objects (DTOs) for API communication.

This module defines all Pydantic models used for request/response handling
in the API endpoints.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ConvertResponse(BaseModel):
    """Response model for file conversion endpoint.

    Attributes:
        id: Unique identifier for the conversion job
        filename: Original filename of uploaded file
        mediawiki_text: Converted text in MediaWiki markup format
        images: List of image paths (relative URLs for frontend)
        warnings: List of warnings encountered during conversion
    """

    id: str = Field(..., description="Unique job identifier")
    filename: str = Field(..., description="Original filename")
    mediawiki_text: str = Field(..., description="Converted MediaWiki markup text")
    images: list[str] = Field(
        default_factory=list, description="List of extracted image paths"
    )
    warnings: list[str] = Field(default_factory=list, description="Conversion warnings")


class JobStatus(BaseModel):
    """Status model for async job tracking (future use).

    Attributes:
        id: Unique job identifier
        status: Current job status
        error: Error message if status is ERROR
    """

    id: str = Field(..., description="Job identifier")
    status: Literal["PENDING", "RUNNING", "DONE", "ERROR"] = Field(
        ..., description="Current job status"
    )
    error: str | None = Field(default=None, description="Error message if job failed")


class HealthResponse(BaseModel):
    """Health check response model.

    Attributes:
        status: Health status indicator
    """

    status: str = Field(default="ok", description="Health status")


class ExtractedData(BaseModel):
    """Internal model for extracted document data.

    Attributes:
        text: Extracted plain text from document
        images: List of saved image filenames
        metadata: Document metadata (title, author, etc.)
    """

    text: str = Field(..., description="Extracted text content")
    images: list[str] = Field(
        default_factory=list, description="List of extracted image filenames"
    )
    metadata: dict[str, str] = Field(
        default_factory=dict, description="Document metadata"
    )
