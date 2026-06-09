@echo off
setlocal enableextensions
cd /d "%~dp0"

echo [INFO] Safe stop mode:
echo [INFO] 1) If you started MCP in a terminal with start-mcp.bat, switch to that terminal.
echo [INFO] 2) Press Ctrl+C to stop the server.
echo [INFO] 3) If the terminal is gone, restart MCP once and stop it with Ctrl+C.
exit /b 0
