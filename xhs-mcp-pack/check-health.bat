@echo off
chcp 65001 >nul
echo 检查小红书 MCP 服务健康状态...
echo.
curl -s http://127.0.0.1:18060/mcp
if %ERRORLEVEL% EQU 0 (
    echo [OK] MCP 服务运行正常
) else (
    echo [ERROR] MCP 服务未运行
)
pause
