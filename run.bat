@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND_PYTHON=%ROOT%backend\.venv\Scripts\python.exe"

if not exist "%BACKEND_PYTHON%" (
    echo Backend virtual environment not found: "%BACKEND_PYTHON%"
    pause
    exit /b 1
)

if not exist "%ROOT%frontend\node_modules" (
    echo Frontend dependencies not found. Run "npm install" in the frontend folder first.
    pause
    exit /b 1
)

start "Eternal Mind Backend" /D "%ROOT%backend" "%BACKEND_PYTHON%" -m uvicorn app.main:app --reload
start "Eternal Mind Frontend" /D "%ROOT%frontend" cmd /k npm run dev

endlocal
