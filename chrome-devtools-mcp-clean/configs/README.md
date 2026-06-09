# 配置文件说明

⚠️ **警告：配置文件中的路径是示例，使用前必须修改！**

根据你使用的 IDE 选择对应的配置示例。

## 使用方法

1. 打开对应的 `.json` 文件
2. **修改 `args` 中的路径为你的实际路径（重要！）**
3. **修改 `env.BIT_BROWSER_ID` 为你从比特浏览器复制的实例 ID（重要！）**
4. 将配置复制到 ccswitch 或对应 IDE 的 MCP 配置区域

### 必须修改的两个地方

**1. server.py 路径（args）**
```json
"args": [
  "D:/github/chrome-devtools-mcp-clean/server.py"  // ← 改为你实际的路径
]
```

**2. 比特浏览器实例 ID（BIT_BROWSER_ID）**
```json
"env": {
  "BIT_BROWSER_ID": "63de02b1ebb34145b7b7886294821a72"  // ← 改为你的真实 ID
}
```

## 获取比特浏览器实例 ID

1. 打开比特浏览器客户端
2. 在窗口列表中找到目标窗口
3. 右键点击 → 复制 ID
4. ID 格式类似：`18e396868d654d949a847e018286b978`

## 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `BIT_BROWSER_ID` | 浏览器实例 ID（必须修改）| - |
| `BIT_BROWSER_API_PORT` | Local API 端口 | 54345 |
| `BIT_BROWSER_API_HOST` | API 主机地址 | localhost |
| `BIT_BROWSER_MODE` | 启用比特浏览器模式 | true |
