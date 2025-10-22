#!/bin/bash
echo "========================================"
echo "Project Setup - PDF/Word to MediaWiki"
echo "========================================"
echo ""

echo "[1/4] Setting up Backend..."
cd backend
uv venv
source .venv/bin/activate
uv sync
uv pip install ruff
cd ..
echo "Backend setup complete!"
echo ""

echo "[2/4] Setting up Frontend..."
cd frontend
npm install
cd ..
echo "Frontend setup complete!"
echo ""

echo "[3/4] Creating directories..."
mkdir -p backend/uploads
mkdir -p output/immagini
mkdir -p output/testo_wiki
echo "Directories created!"
echo ""

echo "[4/4] Setup complete!"
echo ""
echo "========================================"
echo "To start the application:"
echo ""
echo "1. Run: ./start-backend.sh (in one terminal)"
echo "2. Run: ./start-frontend.sh (in another terminal)"
echo "3. Open: http://localhost:4200"
echo "========================================"
