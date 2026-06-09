
=======================================
    小红书 MCP - Windows 版本
=======================================

一、快速开始
-----------
1. 双击 start-mcp.bat 启动服务
2. 在 Claude Code 中配置 MCP (见下方)
3. 开始使用

二、配置 Claude Code
-------------------
在 Claude Code 设置中添加 MCP 服务器配置：

{
  "mcpServers": {
    "xiaohongshu-mcp": {
      "type": "sse",
      "url": "http://127.0.0.1:18060/mcp"
    }
  }
}

三、其他脚本
-----------
- start-mcp.bat     启动 MCP 服务（会显示输出）
- check-health.bat   检查服务健康状态
- check-login.bat    检查小红书登录状态
- check-port.bat     检查端口占用
- stop-mcp.bat      停止 MCP 服务

四、注意
------
- 首次使用需要通过 check-login.bat 获取二维码登录
- cookies.json 会自动保存在当前目录
- 服务默认监听 18060 端口

版本: 20260324-192016
日期: 2026-03-24
