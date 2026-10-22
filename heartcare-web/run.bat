@echo off
REM HeartCare MVP — one command: FastAPI + Next.js (Windows)
REM Usage: run.bat [backend_port] [frontend_port]   (defaults 8001 / 3000)
setlocal
cd /d "%~dp0"
set BACKEND_PORT=%1
if "%BACKEND_PORT%"=="" set BACKEND_PORT=8001
set FRONTEND_PORT=%2
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=3000
set PY=..\.venv\Scripts\python.exe

if not exist "%PY%" (
  echo Missing ..\.venv — run: cd .. ^&^& uv venv ^&^& uv pip install -r heartcare-web\requirements-api.txt
  exit /b 1
)

set NEXT_PUBLIC_API_URL=http://localhost:%BACKEND_PORT%
echo backend  http://localhost:%BACKEND_PORT%  docs: http://localhost:%BACKEND_PORT%/docs
echo frontend http://localhost:%FRONTEND_PORT%
start "heartcare-backend" "%PY%" -m uvicorn api.main:app --port %BACKEND_PORT% --app-dir "%CD%"
start "heartcare-frontend" /d "%CD%\web" cmd /c "set NEXT_PUBLIC_API_URL=http://localhost:%BACKEND_PORT% && npm run dev -- --port %FRONTEND_PORT%"
echo Two windows opened (backend + frontend). Close them to stop.
endlocal
