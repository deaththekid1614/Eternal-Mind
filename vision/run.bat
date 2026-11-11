@echo off
setlocal
cd /d "%~dp0"
python -B server.py
if errorlevel 1 (
    echo.
    echo Could not start the Vison dashboard. Make sure Python is installed and on PATH.
    pause
)
endlocal
