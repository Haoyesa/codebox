@echo off
setlocal enableextensions
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv not found. Run install.bat first.
  exit /b 1
)

if not exist ".env" (
  echo [WARN] .env not found. Create it from .env.template.
)

echo [INFO] Starting feishu-bitable MCP over stdio...
".venv\Scripts\python.exe" -m feishu_bitable_mcp.server
exit /b %errorlevel%
