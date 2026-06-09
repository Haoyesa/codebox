@echo off
taskkill /F /FI "WINDOWTITLE eq XHS-MCP*" 2>nul
echo MCP 服务已停止
pause