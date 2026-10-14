@echo off
title IoT Troubleshooter - Backend
echo Starting IoT Troubleshooter Backend...
echo.
cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install fastapi "uvicorn[standard]" "pydantic>=2.0" python-dotenv httpx --quiet

echo.
echo Backend starting on http://localhost:8000
echo API Docs at http://localhost:8000/docs
echo Press Ctrl+C to stop.
echo.
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
