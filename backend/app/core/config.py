"""Application configuration management.

This module handles all configuration settings for the application including
paths, file limits, and allowed file types.
"""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Main application configuration.

    Manages all paths, file restrictions, and application settings.
    """

    # Base directories
    base_dir: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent)
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent
    )
    upload_dir: Path = Field(default_factory=lambda: Path("uploads"))
    images_dir: Path = Field(default_factory=lambda: Path("output/immagini"))
    output_dir: Path = Field(default_factory=lambda: Path("output/testo_wiki"))

    # File restrictions
    allowed_extensions: set[str] = Field(default={".pdf", ".docx"})
    max_file_size_mb: int = Field(default=50)

    # File naming
    keep_original_names: bool = Field(default=False)

    # API settings
    api_prefix: str = Field(default="/api")
    cors_origins: list[str] = Field(default=["*"])

    def get_absolute_path(self, relative_path: Path) -> Path:
        """Convert relative path to absolute based on base_dir.

        Args:
            relative_path: Path relative to base directory

        Returns:
            Absolute path
        """
        return self.base_dir / relative_path

    def get_project_path(self, relative_path: Path) -> Path:
        """Convert relative path to absolute based on project root.

        Args:
            relative_path: Path relative to project root

        Returns:
            Absolute path
        """
        return self.project_root / relative_path

    def ensure_directories(self) -> None:
        """Create all required directories if they don't exist."""
        # Upload dir is relative to backend
        upload_path = self.get_absolute_path(self.upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)

        # Images and output dirs are relative to project root
        for dir_path in [self.images_dir, self.output_dir]:
            abs_path = self.get_project_path(dir_path)
            abs_path.mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = AppConfig()
config.ensure_directories()
