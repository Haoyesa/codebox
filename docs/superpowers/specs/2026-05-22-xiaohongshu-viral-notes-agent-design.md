## 背景

目标是创建一个可被 Codex 自动发现和调用的新 agent/skill，用于采集并拆解“小红书轻资产副业创业知识库”赛道中的爆款笔记。

第一版以“直接联网搜索并抓取小红书爆款笔记”为主流程，依赖现有第三方采集接口或爬虫能力，不从用户手动样本出发。

## 目标

- 面向“轻资产副业创业知识库”赛道采集公开可获取的小红书笔记
- 在赛道内部做相对热度判断，而不是固定点赞阈值
- 产出结构化 JSON 为主的爆款拆解结果
- 同时沉淀可复用的标题、结构、钩子、转化模式

## 非目标

- 不做自动发帖
- 不做复杂数据库和定时调度
- 不承诺绕过平台登录、风控或私有内容限制
- 不在第一版构建完整长期数据管道

## 方案选择

考虑过三个方案：

1. 纯 skill 流程：只写 SKILL.md，由 agent 自由调用外部能力完成采集和分析
2. skill + 脚本增强：skill 负责触发条件和流程，脚本负责清洗、打分、导出
3. 完整数据管道：增加本地库、历史基线、增量去重和调度

选择方案 2。

原因：

- 采集与拆解仍然保留 agent 的灵活性
- 容易漂移的字段统一、相对热度计算、结构化导出可以固定在脚本中
- 比完整数据管道更轻，适合第一版快速落地

## 技术前提

工作区中已经存在以下线索，说明本地已有可复用的小红书 MCP 接入准备：

- `D:\project\xhs_mcp_config.json`
- `D:\project\xhs_mcp_test.py`

其中配置声明了 `xiaohongshu-mcp` SSE 服务地址：`http://127.0.0.1:18060/mcp`。

因此第一版 skill 默认围绕已有 MCP 能力编排，而不是重新设计新的抓取链路。

## Skill 命名与位置

建议 skill 名称：

`xiaohongshu-viral-notes-agent`

建议创建位置：

`C:\Users\25147\.codex\skills`

原因：

- 符合 skill 自动发现路径
- 名称清晰表达平台、对象和目标
- 后续可继续扩展到其他赛道，而无需改 skill 框架

## 运行模型

默认由用户通过显式 prompt 调用 skill，例如：

`Use $xiaohongshu-viral-notes-agent to collect and analyze viral Xiaohongshu notes in the light-asset side-business knowledge-base niche.`

### 输入参数

- `keywords`
  - 关键词列表，例如：`轻资产副业`、`创业知识库`、`个人IP变现`、`低成本创业`
- `time_window_days`
  - 时间窗口，默认 `7`
- `sample_limit`
  - 每个关键词最大采样量，默认 `20-30`
- `output_format`
  - 默认 `json`，可选 `csv`、`markdown`
- `output_path`
  - 输出目录

### 执行链路

1. 调用现有 `xiaohongshu-mcp` 抓取公开内容
2. 将原始结果传给标准化脚本
3. 脚本统一字段、做赛道识别并计算相对热度
4. agent 基于结构化结果生成爆款拆解
5. 输出 JSON 为主结果，必要时补充 CSV 或 Markdown

## 相对热度定义

第一版不使用固定绝对阈值，而使用赛道内相对热度。

建议定义：

- 先按关键词和子赛道形成样本池
- 使用互动指标构建综合分数
- 在样本池内部按分位排序
- 重点关注该样本池内前 10%-20% 的内容

第一版脚本中可采用可解释的线性打分：

`relative_heat_score = weighted(like_count, collect_count, comment_count, recency_factor)`

其中：

- `collect_count` 权重可高于 `like_count`
- `comment_count` 反映讨论意愿，可作为辅助增强项
- `recency_factor` 用于避免旧内容长期压制新内容

具体权重在脚本中集中定义，便于以后调整。

## 输出结构

主产物为 JSON 文件，schema 尽量稳定，以便后续接入知识库、选题器、仿写器或历史比较流程。

### 顶层字段

- `run_meta`
- `track_summary`
- `notes`
- `viral_patterns`
- `content_opportunities`

### notes 字段

每条爆款笔记包含：

- `note_id`
- `title`
- `url`
- `author`
- `publish_time`
- `like_count`
- `collect_count`
- `comment_count`
- `keyword`
- `subtrack`
- `relative_heat_score`
- `hook_type`
- `structure_type`
- `cta_type`
- `summary`

### viral_patterns 字段

每条模式归纳包含：

- `pattern_name`
- `evidence_note_ids`
- `what_it_is`
- `why_it_works`
- `reusable_template`
- `risk_or_limit`

## 拆解方法

agent 需要基于结构化样本输出以下洞察：

- 标题套路
- 选题方向
- 开头钩子
- 正文结构
- 转化动作

拆解逻辑应优先回答：

- 这类内容在说什么
- 为什么在该赛道内跑得更好
- 哪些表达方式可迁移复用
- 哪些模式只在特定阶段或特定人群有效

## 子赛道识别

“轻资产副业创业知识库”本身比较宽，需要额外做子赛道识别，便于相对热度不失真。

第一版建议从以下方向切分：

- 个人 IP 与知识变现
- 低成本创业案例
- 副业项目拆解
- 内容引流与成交
- AI 提效创业

后续由 `references/track-rules.md` 定义更细的识别规则和关键词映射。

## Skill 目录设计

建议目录：

```text
xiaohongshu-viral-notes-agent/
├─ SKILL.md
├─ agents/
│  └─ openai.yaml
├─ scripts/
│  └─ normalize_xhs_notes.py
└─ references/
   ├─ output-schema.md
   └─ track-rules.md
```

### SKILL.md

包含：

- 触发条件
- 输入约定
- 采集流程
- 清洗和打分流程
- 拆解流程
- 输出 schema 的使用方式
- 边界和限制

### agents/openai.yaml

包含：

- `display_name`
- `short_description`
- `default_prompt`

默认 prompt 必须显式提到 `$xiaohongshu-viral-notes-agent`。

### scripts/normalize_xhs_notes.py

职责：

- 读取 MCP 采集结果
- 标准化字段
- 做子赛道识别
- 计算 `relative_heat_score`
- 输出统一 JSON

### references/output-schema.md

职责：

- 说明 JSON 字段定义
- 提供示例对象
- 说明哪些字段是必须、哪些字段允许为空

### references/track-rules.md

职责：

- 说明“轻资产副业创业知识库”赛道的识别规则
- 记录推荐关键词
- 给出子赛道划分建议

## 验证策略

skill 创建完成后需要进行基础校验：

1. 运行 `init_skill.py` 初始化目录
2. 补齐 SKILL.md、references、scripts
3. 运行 `quick_validate.py` 校验 skill 结构与 frontmatter

如果本地环境允许，再补充两类运行验证：

- skill 层验证：检查能否被正确发现和触发
- 数据层验证：对一组样本输入确认 JSON schema 正常输出

## 风险与限制

- `xiaohongshu-mcp` 当前是否可用，需要运行时再验证
- 小红书公开内容的可得性会受平台风控和页面变化影响
- 第一版“相对热度”是启发式评分，不等于真实平台推荐权重
- 没有历史库时，赛道内相对比较只基于本次样本池

## 当前结论

第一版按以下结论执行：

- 创建 skill 名称：`xiaohongshu-viral-notes-agent`
- 位置：`C:\Users\25147\.codex\skills`
- 方案：`skill + 脚本增强`
- 主输出：结构化 `JSON`
- 主赛道：`轻资产副业创业知识库`
- 热度判断：赛道内相对热度
- 采集方式：基于现有第三方采集接口/MCP

## 说明

当前工作区 `D:\project` 不是 git 仓库，因此本次只能写出 spec 文件，不能在当前目录完成“提交 spec 到 git”这一步。skill 实际创建目录位于 `C:\Users\25147\.codex\skills` 时，也将同样受其所在目录是否为 git 仓库所约束。
