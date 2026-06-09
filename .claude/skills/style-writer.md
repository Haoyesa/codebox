---
name: style-writer
description: 模仿博主风格创作小红书笔记和公众号文章，支持配图建议
parameters:
  type: object
  properties:
    content_type:
      type: string
      enum: ["小红书笔记", "公众号文章"]
      description: 内容形式
    style_sample:
      type: string
      description: 博主风格样本文本（用于分析表达模式）
    keywords:
      type: string
      description: 核心关键词（用逗号分隔）
    topic:
      type: string
      description: 主题或核心观点
  required: ["content_type", "style_sample", "keywords", "topic"]
---

## 风格分析

拿到风格样本后，先分析：
- **句式特征**：短句/长句、感叹词、问句比例
- **词汇偏好**：口头禅、高频词、语气词
- **段落节奏**：每段长度、换行频率
- **互动模式**：有无自问自答、@提及、标签使用

---

## 小红书笔记生成

**结构**：
1. 标题（带emoji，关键词前置）
2. 开篇hook（引发好奇/共鸣）
3. 正文（分段短句，口语化）
4. 结尾互动（提问/引导评论）
5. 标签（#关键词 格式）

**配图建议**：
- 封面图风格/色调
- 正文章节配图清单
- 文字叠加建议

---

## 公众号文章生成

**结构**：
1. 标题（引发共鸣/悬念）
2. 开头（引入场景/痛点）
3. 正文（分小节，有节奏）
4. 结尾（金句/行动号召）

**配图建议**：
- 封面图风格
- 每段落配图描述
- banner/分隔图建议

---

## 输出格式

```
【内容平台】：小红书笔记 / 公众号文章

【标题】

正文内容...

---

【配图建议】
1. 封面图：xxx
2. 正文配图：xxx
3. 结尾引导图：xxx
```