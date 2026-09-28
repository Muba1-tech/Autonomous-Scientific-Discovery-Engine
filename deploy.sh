#!/bin/bash
set -e

echo "=============================================================================="
echo "          🧬 AION X 2.0 — AUTONOMOUS SCIENTIFIC DISCOVERY ENGINE              "
echo "=============================================================================="
echo ""

MODE="${1:-local}"

if [ "$MODE" == "docker" ]; then
    echo "[INFO] Deploying container via Docker Compose..."
    docker compose up --build -d
    echo "[SUCCESS] AION X is running at http://localhost:8501"
elif [ "$MODE" == "test" ]; then
    echo "[INFO] Running test suite..."
    pytest -v
elif [ "$MODE" == "ci" ]; then
    echo "[INFO] Running CI verification..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pytest -v --tb=short
else
    echo "[INFO] Starting AION X 2.0 natively..."
    export TURBO_MODE=1
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
fi
