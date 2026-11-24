@echo off
setlocal EnableExtensions
title Indian Nutrition ^& Diet Planner - local website launcher
cd /d "%~dp0"

echo ============================================================
echo   Indian Nutrition ^& Diet Planner - local website
echo ============================================================
echo   Backend : http://127.0.0.1:8000  (FastAPI, /docs for API)
echo   Frontend: http://127.0.0.1:5173  (<< open this one)
echo ============================================================
echo.

REM ---------- basic checks ----------
if not exist "backend\app\main.py" (
    echo [ERROR] backend\app\main.py was not found.
    echo         Run this file from the project root folder.
    goto :fail
)
if not exist "frontend\package.json" (
    echo [ERROR] frontend\package.json was not found.
    goto :fail
)

where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js was not found on PATH. Install Node.js 18 or newer.
    goto :fail
)
for /f "delims=" %%v in ('node --version') do echo [ok] Node.js %%v

REM ---------- backend virtual environment ----------
if not exist "backend\venv\Scripts\python.exe" (
    echo [setup] Creating backend virtual environment...
    where py >nul 2>&1
    if errorlevel 1 (
        python -m venv backend\venv
    ) else (
        py -m venv backend\venv
    )
    if errorlevel 1 (
        echo [ERROR] Could not create backend\venv. Install Python 3.11+ first.
        goto :fail
    )
    echo [setup] Installing backend dependencies ^(this can take a few minutes^)...
    "backend\venv\Scripts\python.exe" -m pip install --upgrade pip
    "backend\venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo [ERROR] Backend dependency installation failed. See the messages above.
        goto :fail
    )
)
echo [ok] Backend environment found.

REM ---------- frontend dependencies ----------
if not exist "frontend\node_modules" (
    echo [setup] Installing frontend dependencies...
    pushd frontend
    call npm install
    if errorlevel 1 (
        popd
        echo [ERROR] npm install failed. See the messages above.
        goto :fail
    )
    popd
)
echo [ok] Frontend dependencies found.
echo.

REM ---------- start backend ----------
echo [start] Backend  ^(FastAPI, port 8000^)...
start "Nutrition Planner - Backend" cmd /k ""%~dp0backend\venv\Scripts\python.exe" -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000"

set "TRIES=0"
:wait_backend
timeout /t 2 /nobreak >nul
curl -s -o nul http://127.0.0.1:8000/api/health
if not errorlevel 1 goto backend_ready
set /a TRIES+=1
if %TRIES% lss 20 goto wait_backend
echo [WARN] Backend has not answered on port 8000 yet.
echo        Check the "Nutrition Planner - Backend" window for errors.
goto start_frontend

:backend_ready
echo [ok] Backend is answering on http://127.0.0.1:8000

REM ---------- start frontend ----------
:start_frontend
echo.
echo [start] Frontend ^(Vite, port 5173^)...
start "Nutrition Planner - Frontend" cmd /k "cd /d ""%~dp0frontend"" && npm run dev"

set "TRIES=0"
:wait_frontend
timeout /t 2 /nobreak >nul
curl -s -o nul http://127.0.0.1:5173/
if not errorlevel 1 goto frontend_ready
set /a TRIES+=1
if %TRIES% lss 20 goto wait_frontend
echo [WARN] Frontend has not answered on port 5173 yet.
echo        Check the "Nutrition Planner - Frontend" window for errors.
goto finish

:frontend_ready
echo [ok] Frontend is answering on http://127.0.0.1:5173

:finish
echo.
echo ============================================================
echo   OPEN THIS ADDRESS IN YOUR BROWSER:
echo       http://localhost:5173
echo.
echo   API documentation:  http://localhost:8000/docs
echo   Backend health:     http://localhost:8000/api/health
echo ============================================================
echo.
echo Two terminal windows are now open (backend and frontend).
echo Close them, or press Ctrl+C in each, to stop the servers.
echo.
start "" http://localhost:5173
pause
exit /b 0

:fail
echo.
echo ============================================================
echo   STARTUP FAILED - see the error above.
echo ============================================================
pause
exit /b 1
