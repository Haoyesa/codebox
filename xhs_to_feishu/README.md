# 小红书爆款笔记采集 → 飞书多维表格

## 功能

输入关键词，采集小红书搜索结果前 20 篇爆款笔记，写入飞书多维表格。

## 文件结构

- `xhs_collector.py` - 采集主脚本
- `feishu_client.py` - 飞书多维表格写入客户端
- `config.example.py` - 配置模板（复制为 config.py 后填入你的值）

## 使用流程

1. 复制 `config.example.py` 为 `config.py`
2. 填入飞书多维表格的 App Token 和 Table ID
3. 运行 `python xhs_collector.py`
4. 输入关键词，即可采集并写入飞书