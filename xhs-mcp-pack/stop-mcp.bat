@echo off
chcp 65001 >nul
echo 停止小红书 MCP 服务...
echo.
taskkill /F /IM xiaohongshu-mcp.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] 服务已停止
) else (
    echo [INFO] 服务未运行或已停止
)
pause
