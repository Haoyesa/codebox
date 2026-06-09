@echo off
cd /d D:\project\chrome-devtools-mcp-clean
set BIT_BROWSER_MODE=true
set BIT_BROWSER_ID=68b8252b06454718b2c65b7dd1639341
set BIT_BROWSER_API_HOST=127.0.0.1
set BIT_BROWSER_API_PORT=54345
start "XHS-MCP" python server.py
echo MCP 服务已启动
pause