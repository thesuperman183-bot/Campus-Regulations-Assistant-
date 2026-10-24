#!/usr/bin/env bash
# ==============================================================================
# SSIT Campus Regulations Assistant - Start FastAPI Backend
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"

echo "=========================================================="
echo " Starting SSIT Campus Regulations Assistant Backend"
echo "=========================================================="

cd "$BACKEND_DIR"

# Check for .env file
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    echo "[Info] No .env found. Copying .env.example -> .env (Demonstration mode)"
    cp .env.example .env
  fi
fi

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
  echo "[Setup] Creating Python virtual environment in backend/venv..."
  python3 -m venv venv
  source venv/bin/activate
  echo "[Setup] Installing requirements..."
  pip install --upgrade pip
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

echo "[Ready] Starting Uvicorn server on http://localhost:8000"
echo "Interactive Swagger Docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop."
echo "----------------------------------------------------------"

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
