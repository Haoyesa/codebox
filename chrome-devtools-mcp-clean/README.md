# Chrome DevTools MCP 部署指南

用于比特浏览器(Bit Browser)的 MCP 服务器，提供 Chrome DevTools Protocol 功能。

## 前置要求

- Python 3.10+
- 比特浏览器已安装并启用 Local API
- 已获取比特浏览器实例 ID

## 安装步骤

### 1. 安装依赖

**方式一：使用 uv (推荐)**
```bash
uv sync
```

**方式二：使用 pip**
```bash
pip install -r requirements.txt
```

### 2. 获取比特浏览器实例 ID

1. 打开比特浏览器客户端
2. 右键点击目标浏览器窗口 → 选择"复制 ID"
3. 将复制的 ID 提供给 AI 助手

### 3. 生成 ccswitch 配置

⚠️ **重要：路径必须根据你的实际解压位置修改**

AI 助手会根据你的信息生成如下格式的配置：

```json
{
  "args": [
    "<项目绝对路径>/server.py"
  ],
  "command": "python",
  "env": {
    "BIT_BROWSER_API_HOST": "localhost",
    "BIT_BROWSER_API_PORT": "54345",
    "BIT_BROWSER_ID": "<你的实例ID>",
    "BIT_BROWSER_MODE": "true"
  }
}
```

**路径配置注意事项：**
- `args[0]` 必须是 `server.py` 的**绝对路径**
- 示例配置中的路径是示例，**必须替换**为你的实际路径
- Windows 路径分隔符可用 `/` 或 `\\`

**如何获取正确路径：**
```bash
# 进入项目目录后执行
pwd                    # Linux/macOS
cd && cd               # Windows，显示当前路径
```

### 4. 应用配置

将生成的 JSON 配置复制到 ccswitch 的 MCP 配置区域。

### 5. 验证

执行以下命令测试连接：
```
connect_to_browser()
get_connection_status()
```

## 配置文件说明

`configs/` 目录包含各 IDE 的配置示例：
- `vscode-augment.json` - VSCode + Augment 配置
- `claude-desktop.json` - Claude Desktop 配置
- `windsurf.json` - Windsurf IDE 配置
- `multi-instance-example.json` - 多实例配置示例

## 项目结构

```
chrome-devtools-mcp/
├── server.py          # MCP 服务器入口
├── pyproject.toml     # 项目配置和依赖
├── requirements.txt   # pip 依赖列表
├── src/               # 源代码目录
│   ├── main.py
│   ├── client.py
│   ├── cdp_context.py
│   └── tools/         # 工具模块
└── configs/           # 配置示例
```

## 故障排查

| 问题 | 解决方法 |
|------|---------|
| "Browser instance not found" | 检查 BIT_BROWSER_ID 是否正确 |
| "Failed to get Bit Browser connection info" | 确认比特浏览器运行且 Local API 已启用 |
| ModuleNotFoundError | 执行 `pip install -r requirements.txt` |
| "server.py not found" 或路径错误 | 确认 `args[0]` 使用的是绝对路径，且路径正确 |
| MCP 服务器启动失败 | 检查：1) 路径是否正确 2) 依赖是否安装 3) Python 是否可用 |
