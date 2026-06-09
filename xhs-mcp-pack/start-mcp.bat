@echo off
chcp 65001 >nul
echo ========================================
echo    小红书 MCP 服务器 (BitBrowser模式)
echo ========================================
echo.
echo BitBrowser ID: 980cce7b931f4d3abc63b815d9be3859
echo 服务地址: http://127.0.0.1:18060/mcp
echo 按 Ctrl+C 停止服务
echo.
xiaohongshu-mcp.exe -port :18060
pause
