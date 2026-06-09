# PPT生成Agent - 项目规范

## 核心功能

- 输入：关键词 + 背景信息 + 使用场景
- 输出：PPTX文件
- 能力：AI扩写内容 + 风格自动匹配

## 技术方案

- **后端**：Python + FastAPI
- **AI生成**：Claude API (内容扩写)
- **PPTX生成**：python-pptx
- **部署**：本地运行 + 可Docker化

## 使用场景（首批）

1. 投融资汇报
2. 内部培训
3. 产品介绍

## 风格映射

| 场景 | 风格 |
|------|------|
| 投融资汇报 | 深蓝+金色，专业商务 |
| 内部培训 | 蓝绿渐变，清新学院 |
| 产品介绍 | 科技感强，渐变配色 |

## 项目结构

```
ppt-agent/
├── app.py              # FastAPI入口
├── generator/          # 核心生成逻辑
│   ├── content.py      # AI内容生成
│   ├── style.py        # 风格选择
│   └── pptx.py         # PPTX构建
├── templates/          # 风格模板配置
├── static/             # 前端静态文件
└── requirements.txt
```

## 输入字段

```json
{
  "keywords": "string",
  "background": "string",
  "scene": "投融资汇报|内部培训|产品介绍"
}
```

## 输出

- Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation
- 文件名：ppt_{timestamp}.pptx