#!/usr/bin/env bash
# ==============================================================================
# SSIT Campus Regulations Assistant - Start React Frontend (Vite)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "=========================================================="
echo " Starting SSIT Campus Regulations Assistant Frontend"
echo "=========================================================="

cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
  echo "[Setup] Installing npm packages..."
  npm install
fi

echo "[Ready] Starting Vite dev server on http://localhost:5173"
echo "Proxying /api -> http://localhost:8000"
echo "Press Ctrl+C to stop."
echo "----------------------------------------------------------"

npm run dev
