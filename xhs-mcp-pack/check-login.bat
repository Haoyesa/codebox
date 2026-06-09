@echo off
chcp 65001 >nul
echo 检查小红书登录状态...
echo.
curl -s http://127.0.0.1:18060/health/login
if %ERRORLEVEL% EQU 0 (
    echo [OK] 检查请求已发送
) else (
    echo [ERROR] 无法连接到 MCP 服务
)
pause
