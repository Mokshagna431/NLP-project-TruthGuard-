@echo off
echo ===================================================
echo Starting TruthGuard FastAPI REST Backend...
echo URL: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo ===================================================
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" -m backend.server
) else (
    python -m backend.server
)
pause
