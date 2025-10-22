"""FastAPI main application.

This is the entry point for the PDF/Word to MediaWiki conversion API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import config
from app.routers import convert, files, health

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


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint with API information.

    Returns:
        API information and available endpoints
    """
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
