"""FastAPI main application.

This is the entry point for the PDF/Word to MediaWiki conversion API.
"""

import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import config
from app.routers import convert, files, health


def get_base_path() -> Path:
    """Get the base path for the application.

    When running as a PyInstaller executable, returns sys._MEIPASS.
    Otherwise returns the directory containing this script.

    Returns:
        Path to the base directory
    """
    if getattr(sys, "frozen", False):
        # Running as PyInstaller executable
        return Path(sys._MEIPASS)
    else:
        # Running as normal Python script
        # Go up from backend/app to project root
        return Path(__file__).parent.parent.parent


# Create FastAPI application
app = FastAPI(
    title="PDF/Word → MediaWiki API",
    description="Convert PDF and DOCX files to MediaWiki markup with image extraction",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=config.api_prefix)
app.include_router(convert.router, prefix=config.api_prefix)
app.include_router(files.router, prefix=config.api_prefix)

# Mount static files for images (in project root)
images_path = str(config.get_project_path(config.images_dir))
app.mount("/immagini", StaticFiles(directory=images_path), name="immagini")

# Get path to Angular frontend build (for production/exe mode)
# Use get_base_path() to handle both normal and PyInstaller execution
base_path = get_base_path()
frontend_build_path = base_path / "frontend" / "dist" / "pdf-word-mediawiki" / "browser"

# Debug logging for frontend path
print(f"[STARTUP] Base path: {base_path}")
print(f"[STARTUP] Frontend path: {frontend_build_path}")
print(f"[STARTUP] Frontend exists: {frontend_build_path.exists()}")

if frontend_build_path.exists():
    # List files in frontend directory
    try:
        files = list(frontend_build_path.iterdir())
        print(f"[STARTUP] Files in frontend dir: {len(files)} files")
        for f in files[:5]:  # Print first 5 files
            print(f"[STARTUP]   - {f.name}")
    except Exception as e:
        print(f"[STARTUP] Error listing files: {e}")

# Mount Angular frontend static files if build exists
if frontend_build_path.exists():
    print("[STARTUP] Mounting frontend static files...")

    # Mount assets folder
    assets_path = frontend_build_path / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")
        print("[STARTUP] [OK] Mounted /assets")

    # Mount other static files (js, css, etc.)
    app.mount("/static", StaticFiles(directory=str(frontend_build_path)), name="static")
    print("[STARTUP] [OK] Mounted /static")
else:
    print("[STARTUP] [WARN] Frontend build directory NOT FOUND!")


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - serves Angular frontend or API info.

    Returns:
        Angular index.html if build exists, otherwise API information
    """
    # Serve Angular frontend if build exists
    if frontend_build_path.exists():
        index_path = frontend_build_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))

    # Fallback to API information (for development mode)
    return {
        "name": "PDF/Word → MediaWiki API",
        "version": "1.0.0",
        "docs": "/docs",
        "scalar": "/scalar",
        "redoc": "/redoc",
        "health": f"{config.api_prefix}/health",
    }


@app.get("/scalar", response_class=HTMLResponse, include_in_schema=False)
async def scalar_docs() -> str:
    """Serve Scalar API documentation UI.

    Returns:
        HTML page with Scalar documentation UI
    """
    return """
    <!doctype html>
    <html>
      <head>
        <meta charset='utf-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1'>
        <title>API Documentation - Scalar</title>
      </head>
      <body>
        <script
          id="api-reference"
          data-url="/openapi.json">
        </script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
      </body>
    </html>
    """


# Catch-all route for Angular routing (must be last!)
# This handles client-side routes like /convert, /results, etc.
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_angular_routes(full_path: str):
    """Serve Angular frontend for all unmatched routes.

    This allows Angular's client-side routing to work properly.
    All API routes are already handled by the routers above.

    Args:
        full_path: The requested path

    Returns:
        File if exists, otherwise index.html for Angular routing
    """
    if frontend_build_path.exists():
        # Try to serve the specific file first
        file_path = frontend_build_path / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))

        # Otherwise serve index.html for Angular routing
        index_path = frontend_build_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))

    # If no frontend build, return 404-like message
    return {"error": "Frontend not built. Run: cd frontend && npm run build"}
