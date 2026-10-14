@echo off
title IoT Troubleshooter - Frontend
echo Starting IoT Troubleshooter Frontend...
echo.
cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo Installing Node dependencies (first time only)...
    npm install
)

echo.
echo Frontend starting on http://localhost:5173
echo Open this URL in your browser.
echo Press Ctrl+C to stop.
echo.
npm run dev
pause
