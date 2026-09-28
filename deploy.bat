@echo off
setlocal enabledelayedexpansion
title AION X 2.0 — Deployment & Launcher

echo ==============================================================================
echo           🧬 AION X 2.0 — AUTONOMOUS SCIENTIFIC DISCOVERY ENGINE
echo ==============================================================================
echo.
echo Select deployment mode:
echo   [1] Local Native Launch (Streamlit HUD on http://localhost:8501)
echo   [2] Docker Containerized Deployment (Build and Run via Docker Compose)
echo   [3] Run Automated Test Suite (Pytest 82+ Verification Tests)
echo   [4] Initialize Git Repository and Commit Updates
echo   [5] Exit
echo.

set /p choice="Enter option [1-5]: "

if "%choice%"=="1" (
    echo.
    echo [INFO] Starting AION X 2.0 locally...
    set TURBO_MODE=1
    streamlit run app.py --server.port 8501
    goto end
)

if "%choice%"=="2" (
    echo.
    echo [INFO] Deploying container via Docker Compose...
    docker compose up --build -d
    echo [SUCCESS] AION X is running at http://localhost:8501
    goto end
)

if "%choice%"=="3" (
    echo.
    echo [INFO] Running test suite...
    pytest -v
    pause
    goto end
)

if "%choice%"=="4" (
    echo.
    echo [INFO] Initializing Git repository and committing changes...
    git init
    git add .
    git commit -m "feat: AION X 2.0 production updates, AST security hardening, CI/CD and containerization"
    echo [SUCCESS] Repository initialized and committed.
    pause
    goto end
)

:end
