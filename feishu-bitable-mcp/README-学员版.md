# 飞书多维表格 MCP 学员安装包（Windows）

## 1. 快速安装

1. 解压压缩包到本地固定路径（建议英文路径）。
2. 双击运行 `install.bat`。
3. 打开 `.env`，填写飞书凭证（两种方式二选一）：
   - `FEISHU_APP_ID` + `FEISHU_APP_SECRET`
   - `FEISHU_USER_ACCESS_TOKEN`
4. 运行 `check-env.bat`，看到 `[OK]` 再进行下一步。

## 2. 手动启动与停止（可选）

- 启动：`start-mcp.bat`
- 停止：`Ctrl + C`（或运行 `stop-mcp.bat` 强制结束）

说明：日常在 AI 客户端里配置好 MCP 后，一般不需要手动双击 `start-mcp.bat`，客户端会按配置自动拉起进程。

## 3. 配置 MCP 客户端

- 模板目录：`mcp-config`
  - `codex-config-snippet.toml`
  - `cursor-mcp.json`
  - `vscode-mcp.json`
  - `claude-mcp.json`

使用方式：

1. 把模板中的 `D:\YOUR_UNZIP_PATH\student-pack-win-x64\...` 改为你的真实解压路径。
2. 在 `env` 里填真实凭证。
3. 如果使用 `FEISHU_USER_ACCESS_TOKEN`，可将 `FEISHU_APP_ID/FEISHU_APP_SECRET` 留空。

## 4. 自检建议

在 AI 客户端里测试：

1. 先调用 `bitable_list_tables`（使用你已有的 `app_token`）。
2. 再调用 `bitable_list_fields`（补上 `table_id`）。
3. 最后调用 `bitable_search_records`（确认读权限可用）。

## 5. 常见问题

- 提示 `Python not found`：安装 Python 3.10+ 并勾选 PATH。
- 提示鉴权失败：检查应用权限、密钥是否填错、是否使用了错误租户。
- 工具列表为空：确认 MCP 配置路径正确，并重启 AI 客户端。
