@echo off
echo ========================================
echo  Plugs Backend - Starting FastAPI Server
echo ========================================
echo.

cd /d d:\backend

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [1/3] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [1/3] No venv found - using system Python
)

REM Install/update dependencies
echo [2/3] Installing dependencies...
pip install -r requirements.txt --quiet

REM Start the FastAPI server
echo [3/3] Starting FastAPI server on http://127.0.0.1:8000
echo.
echo  API Docs: http://127.0.0.1:8000/docs
echo  Jobs:     http://127.0.0.1:8000/jobs
echo  Health:   http://127.0.0.1:8000/
echo.
echo  Press Ctrl+C to stop the server.
echo ========================================

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

pause
