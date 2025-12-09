@echo off
echo Starting FastAPI Backend Server...
echo.
echo Server will be accessible from:
echo   - Local: http://localhost:8000
echo   - Network: http://[YOUR_IP]:8000
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d %~dp0
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000









