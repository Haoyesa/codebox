@echo off
chcp 65001 >nul
echo 检查端口 18060...
echo.
netstat -ano | findstr "18060"
if %ERRORLEVEL% EQU 0 (
    echo [OK] 端口 18060 已被占用
) else (
    echo [INFO] 端口 18060 可用
)
pause
