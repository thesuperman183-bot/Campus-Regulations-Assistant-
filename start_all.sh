#!/usr/bin/env bash
# ==============================================================================
# SSIT Campus Regulations Assistant - Start Full-Stack Application
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================================="
echo " Starting SSIT Campus Regulations Assistant (Full Stack)"
echo "=========================================================="

trap 'kill 0' EXIT

# 1. Start Backend in background
echo "[1/2] Starting FastAPI backend on http://localhost:8000..."
"$SCRIPT_DIR/run_backend.sh" &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# 2. Start Frontend
echo "[2/2] Starting React frontend on http://localhost:5173..."
"$SCRIPT_DIR/run_frontend.sh" &
FRONTEND_PID=$!

wait
