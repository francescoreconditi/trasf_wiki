# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PDF/Word → MediaWiki Converter.

This creates a standalone Windows executable with all dependencies embedded.
"""

from pathlib import Path

# Get project root
project_root = Path(SPECPATH)

# Build configuration
block_cipher = None

a = Analysis(
    ['launcher_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include Angular frontend build
        ('frontend/dist/pdf-word-mediawiki', 'frontend/dist/pdf-word-mediawiki'),

        # Include backend application code
        ('backend/app', 'backend/app'),

        # Note: output/immagini directory is created automatically by backend at runtime
        # No need to include it in the build
    ],
    hiddenimports=[
        # FastAPI and related
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'fastapi.staticfiles',
        'fastapi.responses',
        'starlette',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.responses',
        'starlette.routing',
        'pydantic',
        'pydantic.generics',
        'pydantic_core',

        # Document processing
        'pymupdf',
        'fitz',
        'docx',
        'python_docx',
        'lxml',
        'lxml._elementpath',
        'lxml.etree',

        # ODT processing (odfpy)
        'odf',
        'odf.opendocument',
        'odf.text',
        'odf.teletype',
        'odf.table',
        'odf.style',
        'defusedxml',
        'defusedxml.ElementTree',

        # RTF processing
        'striprtf',
        'striprtf.striprtf',

        # Image processing
        'PIL',
        'PIL._imaging',
        'PIL.Image',

        # Standard library imports that might be missed
        'email.mime',
        'email.mime.multipart',
        'email.mime.text',
        'email.mime.base',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'IPython',
        'jupyter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ConvertitorePDF',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable with UPX (reduces size)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window (GUI mode)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # TODO: Add icon file if available (icon='icon.ico')
)
