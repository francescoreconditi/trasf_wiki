#!/bin/bash
echo "========================================"
echo "Starting Backend Server"
echo "========================================"
cd backend
source .venv/bin/activate
echo ""
echo "Backend running at: http://localhost:8000"
echo "API Docs (Scalar): http://localhost:8000/scalar"
echo "API Docs (Swagger): http://localhost:8000/docs"
echo ""
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
