@echo off
setlocal enableextensions
cd /d "%~dp0"

set "PY_CMD="
where py >nul 2>nul
if %errorlevel%==0 set "PY_CMD=py -3"

if not defined PY_CMD (
  where python >nul 2>nul
  if %errorlevel%==0 set "PY_CMD=python"
)

if not defined PY_CMD (
  echo [ERROR] Python 3.10+ not found. Install from https://www.python.org/downloads/
  exit /b 1
)

echo [INFO] Using Python command: %PY_CMD%
%PY_CMD% -c "import sys; print('[INFO] Python version:', sys.version.split()[0]); raise SystemExit(0 if sys.version_info[:2] >= (3, 10) else 1)"
if errorlevel 1 (
  echo [ERROR] Python 3.10+ is required.
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creating virtual environment...
  %PY_CMD% -m venv .venv
  if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    exit /b 1
  )
) else (
  echo [INFO] Existing .venv found. Reusing it.
)

echo [INFO] Bootstrapping pip...
".venv\Scripts\python.exe" -m ensurepip --upgrade >nul 2>nul

echo [INFO] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
  echo [ERROR] pip upgrade failed.
  exit /b 1
)

echo [INFO] Installing MCP package...
".venv\Scripts\python.exe" -m pip install .
if errorlevel 1 (
  echo [ERROR] pip install failed.
  exit /b 1
)

if not exist ".env" (
  copy ".env.template" ".env" >nul
  echo [INFO] Created .env from .env.template. Fill credentials before starting.
)

echo [OK] Install completed.
echo [NEXT] 1) Edit .env  2) Run check-env.bat  3) Configure MCP client
exit /b 0
