@echo off
echo ========================================
echo Project Setup - PDF/Word to MediaWiki
echo ========================================
echo.

echo [1/4] Setting up Backend...
cd backend
call uv venv
call .venv\Scripts\activate.bat
call uv sync
call uv pip install ruff
cd ..
echo Backend setup complete!
echo.

echo [2/4] Setting up Frontend...
cd frontend
call npm install
cd ..
echo Frontend setup complete!
echo.

echo [3/4] Creating directories...
if not exist "backend\uploads" mkdir backend\uploads
if not exist "output\immagini" mkdir output\immagini
if not exist "output\testo_wiki" mkdir output\testo_wiki
echo Directories created!
echo.

echo [4/4] Setup complete!
echo.
echo ========================================
echo To start the application:
echo.
echo 1. Run: start-backend.bat (in one terminal)
echo 2. Run: start-frontend.bat (in another terminal)
echo 3. Open: http://localhost:4200
echo ========================================
pause
