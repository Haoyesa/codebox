# 简历优化 + 面试题小程序 v0.1 设计文档

> **范围**: 微信原生小程序 + 微信云开发 + 腾讯混元多模态,聚焦"上传/导入简历 → AI 优化 + 诊断打分 → 左右编辑 → 保存"一条主链路,配套一个简版 H5 管理后台维护 Prompt 模板与行业岗位库。
> **非范围**: 面试题生成、求职信/自我介绍、版本切换器、会员支付、OCR 兜底(扫描件)、用户/订单/审核/数据看板 —— 全部延后到 v0.2~v0.4。

---

## 1. 目标与非目标

### 1.1 目标

1. 求职用户可以**上传任意格式简历(Word/PDF/图片)或手动填写**,通过混元多模态解析为结构化数据。
2. 选中求职身份(应届/社招/转行/国企/外企) + 目标岗位(行业 → 岗位 → 职级)后,**一键生成基于 STAR 法则的优化版简历 + 4 维度诊断打分**。
3. 提供**左右对照编辑器**,允许用户逐段微调优化结果,并保存到云端(同一份简历上回填优化结果)。
4. 维护人员可以**在 H5 后台编辑分行业/岗位/职级的 Prompt 模板**与**行业岗位树**,支撑前端"目标岗位选择器"与 AI 输出的精细化。

### 1.2 非目标(明确不做)

- 面试题生成、求职信、自我介绍 → v0.2
- 多版本切换器(专业/简洁/国企/英文) → v0.2
- 会员体系、支付、退款 → v0.3
- 扫描件 OCR 专项优化(混元已支持图片输入) → v0.3
- 用户增长、运营、数据看板 → v0.4
- 多管理员、权限分级、操作审计 → v0.4

---

## 2. 角色与关键场景

### 2.1 求职用户(C 端)

- **首次使用**: 微信授权登录 → 选择身份 → 选择目标岗位 → 选导入方式(上传/拍照/手动) → 解析确认 → 一键优化 → 看到左右对照 + 评分 → 编辑保存 → 历史可见。
- **复用**: 历史列表 → 点开任意一份 → 继续编辑或重新生成。

### 2.2 维护人员(Admin)

- 登录 H5 后台 → 维护行业岗位树 → 维护 Prompt 模板(按身份 × 行业 × 职级组织)。

---

## 3. 架构总览

### 3.1 分层

```
+--------------------------------------------------+
|  C 端: 微信原生小程序(miniapp/)                   |
|  - pages/ 组件式页面                              |
|  - lib/  API/Auth/Storage/Adapter 封装            |
|  - styles/ 设计 token + reset                     |
+--------------------+-----------------------------+
                     | wx.cloud.callFunction
                     v
+--------------------------------------------------+
|  微信云开发(cloudfunctions/)                     |
|  - 业务函数: login / parseResume / optimizeResume|
|    / saveResume / listResumes / getResume         |
|    / listPromptTemplates / savePromptTemplate    |
|    / listIndustries / saveIndustry               |
|  - _shared/ 混元 adapter + 内容安全 + 鉴权        |
+--------------------+-----------------------------+
                     | wx-server-sdk + tencentcloud-sdk
                     v
+--------------------------------------------------+
|  外部: 腾讯混元(hunyuan-pro / hunyuan-vision)    |
|       微信内容安全 API(security.msgSecCheck)      |
+--------------------------------------------------+

+--------------------------------------------------+
|  Admin: Vue 3 + Vite + Element Plus(admin/)      |
|  - 部署到微信云开发「静态网站托管」               |
|  - 通过云函数 HTTP 触发器访问后台数据             |
+--------------------------------------------------+
```

### 3.2 关键架构决策

| 决策 | 选择 | 理由 |
|---|---|---|
| 前端框架 | 微信原生(WXML/WXSS/JS) | 用户指定;零编译依赖 |
| 语言 | 原生 JS + JSDoc 注释 | 避免 TS 工程化开销,v0.1 业务规模无需类型系统 |
| 状态管理 | `Page.data` + `getApp().globalData` | 小程序原生足够;v0.2 再考虑 Pinia 类方案 |
| UI 库 | 自建 design token + 基础组件 | 体积/适配可控;避免引入额外成本 |
| Admin 框架 | Vue 3 + Vite + Element Plus | 国内后台主流,云开发静态托管友好 |
| 后端 | 微信云开发(云函数 + NoSQL + 存储) | 用户指定;免运维;BaaS 化 |
| 大模型 | 腾讯混元(多模态 + 文本) | 用户指定;适配 AI 扶持计划 |
| 调用方式 | 统一 `HunyuanAdapter`,默认 `mock`,环境变量切换 `live` | 用户选项 B |
| 数据库 | 微信云开发 NoSQL(类 MongoDB) | 4 个集合(users / resumes / prompt_templates / industries),无强关系,无事务需求 |
| 文件存储 | 微信云开发存储(简历文件/图片) | 自带 CDN + 加密 |
| 鉴权 | C 端用 `wx.cloud` 自带 `_openid` 注入;Admin 用账号密码 + token | 最低成本满足基本安全 |

---

## 4. 仓库结构

```
D:\project\
|-- miniapp/                          # 微信原生小程序
|   |-- app.js
|   |-- app.json
|   |-- app.wxss
|   |-- project.config.json
|   |-- sitemap.json
|   |-- pages/
|   |   |-- index/                    # 落地 + 入口
|   |   |-- identity/                 # 求职身份选择
|   |   |-- target/                   # 行业-岗位-职级 三级联动
|   |   |-- import/                   # 导入方式选择
|   |   |-- upload/                   # 文件上传(Word/PDF/图片)
|   |   |-- camera/                   # 拍照/相册
|   |   |-- form/                     # 手动填写表单
|   |   |-- confirm/                  # 解析结果确认/微调
|   |   |-- preview/                  # 优化结果 + 左右编辑 + 评分
|   |   |-- history/                  # 历史列表
|   |   `-- profile/                  # 个人中心(v0.1 占位)
|   |-- components/
|   |   |-- btn/                      # 通用按钮
|   |   |-- card/                     # 卡片容器
|   |   |-- tag/                      # 标签
|   |   |-- score-bar/                # 评分条
|   |   |-- editor-row/               # 单段对照编辑行
|   |   |-- empty/                    # 空状态
|   |   `-- toast/                    # 轻提示
|   |-- lib/
|   |   |-- api.js                    # 云函数调用封装
|   |   |-- auth.js                   # 登录 + token 持久化
|   |   |-- storage.js                # wx.storage 封装
|   |   `-- config.js                 # 环境配置
|   |-- styles/
|   |   |-- tokens.wxss               # CSS 变量
|   |   `-- reset.wxss                # 基础 reset
|   `-- utils/
|       |-- format.js                 # 日期/手机号格式化
|       `-- validate.js               # 表单校验
|
|-- cloudfunctions/                   # 微信云开发云函数
|   |-- _shared/
|   |   |-- hunyuan.js                # 混元 adapter
|   |   |-- auth.js                   # 鉴权 + openid 提取
|   |   |-- security.js               # 内容安全审核
|   |   `-- response.js               # 统一响应包装
|   |-- login/                        # 微信登录换 openid
|   |-- parseResume/                  # 解析简历
|   |-- optimizeResume/               # 优化简历 + 评分(不写库)
|   |-- saveResume/                   # 保存/更新简历
|   |-- listResumes/                  # 简历列表
|   |-- getResume/                    # 简历详情
|   |-- listPromptTemplates/          # [Admin] 模板列表
|   |-- savePromptTemplate/           # [Admin] 模板保存
|   |-- listIndustries/               # 行业岗位树(共享)
|   `-- saveIndustry/                 # [Admin] 行业岗位保存
|
|-- admin/                            # H5 管理后台
|   |-- index.html
|   |-- package.json
|   |-- vite.config.js
|   |-- public/
|   `-- src/
|       |-- main.js
|       |-- App.vue
|       |-- router/index.js
|       |-- api/                      # 云函数 HTTP 调用封装
|       |-- views/
|       |   |-- Login.vue
|       |   |-- PromptTemplates.vue
|       |   `-- Industries.vue
|       `-- components/
|
|-- docs/
|   `-- superpowers/
|       |-- specs/
|       |   `-- 2026-06-16-resume-mini-program-v0.1-design.md   # 本文件
|       `-- plans/
|           `-- 2026-06-16-resume-mini-program-v0.1-plan.md     # 实施计划
|
`-- README.md
```

---

## 5. 数据模型(微信云开发 NoSQL)

### 5.1 `users`(登录后惰性创建)

```js
{
  _id: "auto",
  _openid: "openid_xxx",
  identity: "freshgrad",            // freshgrad | social | transition | stateowned | foreign
  targetIndustry: "internet",
  targetJob: "frontend",
  targetLevel: "mid",
  createdAt: 1718515200000,
  updatedAt: 1718515200000
}
```

### 5.2 `resumes`(结构化简历 + 优化结果,合并为一个文档)

```js
{
  _id: "auto",
  _openid: "openid_xxx",
  source: "word",                   // word | pdf | image | manual
  fileID: "cloud://xxx.docx",       // 原始文件 fileID(manual 时为空)
  data: {                           // 结构化原版
    name: "张三",
    phone: "13800000001",
    email: "zhangsan@example.com",
    education: [
      { school: "清华大学", major: "计算机", degree: "本科", startDate: "2018-09", endDate: "2022-06" }
    ],
    work: [
      { company: "字节跳动", title: "前端工程师", startDate: "2022-07", endDate: "至今",
        description: "负责抖音 Web 端性能优化,FCP 从 2.1s 降至 1.3s" }
    ],
    projects: [
      { name: "电商中后台", role: "前端负责人", period: "2023-01 ~ 2023-12",
        description: "主导微前端架构落地,接入 12 个子应用,首屏 < 1.2s" }
    ],
    skills: ["JavaScript", "TypeScript", "React", "Webpack"]
  },
  // 下面是首次保存为 null、优化后回填的字段
  identity: "social",
  targetIndustry: "internet",
  targetJob: "frontend",
  targetLevel: "mid",
  optimized: { /* 优化版结构化数据,与 data 同构,首次保存为 null */ },
  score: {
    match: 85,                        // 匹配度
    completeness: 90,                 // 完整性
    professional: 80,                 // 专业性
    quantified: 70,                   // 量化度
    total: 81                         // 加权总分
  },
  suggestions: [
    "工作经历缺少用户量级与业务规模描述",
    "项目经历建议补充技术选型理由"
  ],
  createdAt: 1718515200000,
  updatedAt: 1718515200000
}
```

**模型说明**:`data` 是用户上传/手填的原版结构化简历,`optimized` 是 AI 优化后的版本,`score` + `suggestions` 跟随 `optimized` 一同生成。首次保存只填 `data` 及以上 raw 字段,`optimized`/`score`/`suggestions` 留空;点"一键优化"调 `optimizeResume` 拿到结果后,再用 `saveResume` 回填到同一文档。这样一份"用户拥有的简历"在 DB 里只有一条记录,前端"历史列表"就是 `resumes` 集合按 `updatedAt` 倒序。

### 5.3 `prompt_templates`(Admin 维护)

```js
{
  _id: "auto",
  type: "optimize",                   // optimize | parse
  identity: "social",                 // 五选一
  industry: "internet",               // 行业 code 或 * 表示通用
  level: "mid",                       // 职级或 *
  version: 1,
  template: "你是一名资深互联网行业 HR ...",
  variables: ["structuredResume", "targetJob", "targetLevel"],
  active: true,
  updatedAt: 1718515200000,
  updatedBy: "admin"
}
```

匹配规则:先查 `(type, identity, industry, level)`,未命中降级到 `(type, identity, *, *)`,再降级到 `(type, *, *, *)`。每次保存新模板自动 `version += 1`,旧版本保留以便回滚。

### 5.4 `industries`(Admin 维护)

```js
{
  _id: "auto",
  code: "internet",
  name: "互联网",
  icon: "💻",
  jobs: [
    { code: "frontend", name: "前端工程师",
      levels: [
        { code: "junior", name: "初级" },
        { code: "mid", name: "中级" },
        { code: "senior", name: "高级" }
      ]
    },
    { code: "backend", name: "后端工程师", levels: [...] }
  ],
  companies: ["字节跳动", "腾讯", "阿里巴巴", "美团", "京东"],
  sort: 1,
  updatedAt: 1718515200000
}
```

种子数据:v0.1 写入 12 个行业(互联网/金融/咨询/快消/制造/教育/医疗/汽车/地产/传媒/国企/外企),每个行业 3-8 个核心岗位,共 60+ 岗位,每岗 3-4 个职级。

---

## 6. 业务流程

### 6.1 主链路(用户视角)

```
首页
  |-- 未登录 -> 调 wx.login -> login 云函数 -> 拿到 token + openid
  |-- 已登录但未选身份 -> 跳 identity 页
  |-- 已选身份 + 已选目标 -> 跳 import 页
       |-- 上传 Word/PDF/图片
       |     |-- wx.uploadFile -> 拿到 fileID
       |     |-- 调 parseResume 云函数(fileID)
       |     |-- 拿到结构化 JSON -> 跳 confirm 页
       |           |-- 用户微调 -> 确认 -> 调 saveResume(只存 data)
       |-- 拍照/相册
       |     `-- 同上传路径
       `-- 手动填写
             `-- 在 form 页填完 -> 调 saveResume -> 拿到 resumeId
  |-- confirm 后或表单完成后 -> 跳 preview 页
       |-- 点"一键优化" -> 调 optimizeResume(只算不存)
       |     |-- 展示左右对照 + 4 维评分 + 建议列表
       |     |-- 用户可逐段编辑
       |     `-- 点"保存" -> 调 saveResume(回填 optimized/score 到同文档)
  `-- 历史页 -> 列表展示 -> 点开复用 preview
```

### 6.2 时序图(关键路径)

```
用户           小程序            云函数            混元
 |  点击上传     |                 |                 |
 |------------> |                 |                 |
 |              | wx.uploadFile   |                 |
 |              |-------------->  |                 |
 |              |                 | 存到云存储       |
 |              | <----- fileID   |                 |
 |              |                 |                 |
 |              | wx.cloud.callFunction(parseResume) |
 |              |----------------------------->     |
 |              |                 | 下载 buffer     |
 |              |                 | hunyuan.parse() |
 |              |                 |-------------->  |
 |              |                 | <--- JSON       |
 |              | <--- {data}     |                 |
 |  跳 confirm   |                 |                 |
 |  编辑确认     |                 |                 |
 |------------> |                 |                 |
 |              | wx.cloud.callFunction(saveResume)  |
 |              |----------------------------->       |
 |              | <--- {resumeId}                    |
 |              |                 |                 |
 |  跳 preview   |                 |                 |
 |  点击一键优化 |                 |                 |
 |------------> |                 |                 |
 |              | wx.cloud.callFunction(optimizeResume) |
 |              |----------------------------->       |
 |              |                 | 取 prompt 模板  |
 |              |                 | hunyuan.optimize() |
 |              |                 |-------------->  |
 |              |                 | <--- 优化结果    |
 |              |                 | 内容安全审核     |
 |              | <--- {optimized, score, suggestions} |
 |  展示对照     |                 |                 |
 |  编辑保存     |                 |                 |
 |              | wx.cloud.callFunction(saveResume, 完整) |
 |              |----------------------------->       |
```

---

## 7. 关键模块设计

### 7.1 混元 Adapter(`cloudfunctions/_shared/hunyuan.js`)

**职责**:统一封装混元调用,支持 mock / live 两种模式,业务函数无需关心底层实现。

**接口**:

```js
class HunyuanAdapter {
  constructor({ mode, secretId, secretKey, region }) { ... }

  async parseResume({ fileBuffer, mimeType, filename }) { ... }
  async optimizeResume({ structuredResume, identity, industry, level, job, promptTemplate }) { ... }
}
```

**模式切换**:
- `mode = 'mock'`:返回硬编码样例数据
- `mode = 'live'`:调用 `tencentcloud-sdk-nodejs` 的 `hunyuan` 包

**环境变量**:
- `HUNYUAN_MODE`: `mock` | `live`,默认 `mock`
- `HUNYUAN_SECRET_ID` / `HUNYUAN_SECRET_KEY`: live 模式必填
- `HUNYUAN_REGION`: 默认 `ap-guangzhou`

**Mock 实现要点**:
- `parseResume`:忽略文件内容,返回固定结构化简历(张三,字节前端,3 年经验)
- `optimizeResume`:在原版基础上做轻微改写 + 返回固定评分(80/85/90/75)+ 3 条固定建议
- 随机延迟 800-1500ms 模拟真实网络

**Live 实现要点**:
- `parseResume`:走 `hunyuan.vision.ChatCompletions`,传文件 base64 + prompt 要求"输出严格 JSON,字段为 name/phone/email/education/work/projects/skills"
- `optimizeResume`:走 `hunyuan.ChatCompletions`,prompt 模板由 Admin 配置,要求输出 `{optimized, score, suggestions}`
- 失败重试 1 次,仍失败抛 `HunyuanError`
- 单次调用超时 20s,避免云函数超时(默认 20s,留余量)

### 7.2 内容安全(`cloudfunctions/_shared/security.js`)

**职责**:对 AI 生成的简历文本与用户输入做敏感词过滤。

**实现**:调用 `wx-server-sdk` 的 `cloud.openapi.security.msgSecCheck`,返回 `Risky` 时拒绝保存,`Review` 标记待人工复审,`Pass` 放行。

**触发点**:
- `optimizeResume` 返回前过滤 `optimized` 字段
- `saveResume` 入库前再过滤一次
- Admin 后台保存 Prompt 模板时过滤

### 7.3 鉴权(`cloudfunctions/_shared/auth.js`)

**C 端**:微信云开发自动注入 `event.userInfo.openId`,所有业务函数信任此字段作为 `_openid`。`login` 函数接收 `code` 调 `code2Session` 换 openid + session_key,返回自定义 token(简化为 openid 本身,云开发环境内不需 JWT)。

**Admin**:账号密码从环境变量读取,登录成功返回短期 token(2h),用 `crypto.createHmac` 签名,载荷含 `username` + `exp`。所有 Admin 云函数验证 `event.adminToken`,失败返回 401。

### 7.4 业务函数规约

每个云函数遵循统一结构:

```js
// cloudfunctions/<name>/index.js
const { authUser } = require('../_shared/auth');
const { ok, fail } = require('../_shared/response');

exports.main = async (event, context) => {
  try {
    const openid = authUser(context);
    // ... 业务逻辑
    return ok({ ... });
  } catch (err) {
    console.error('[funcName] error', err);
    return fail(err.code || 'INTERNAL', err.message);
  }
};
```

**响应格式**:
```js
ok(data)    // { code: 0, message: 'ok', data }
fail(code, msg)  // { code: 'PARSE_FAIL', message: '简历解析失败', data: null }
```

**业务函数清单**:

| 函数 | 入参 | 出参 | 鉴权 |
|---|---|---|---|
| `login` | `{ code }` | `{ token, openid, isNewUser }` | 无 |
| `parseResume` | `{ fileID }` | `{ data }` | 用户 |
| `optimizeResume` | `{ resumeId, identity, industry, job, level }` | `{ optimized, score, suggestions }` | 用户 |
| `saveResume` | `{ id?, data, identity?, target?, optimized?, score?, suggestions? }` | `{ resumeId }` | 用户 |
| `listResumes` | `{ page, pageSize }` | `{ list, total }` | 用户 |
| `getResume` | `{ id }` | `{ resume }` | 用户 |
| `listPromptTemplates` | `{ type?, identity?, industry?, level? }` | `{ list }` | Admin |
| `savePromptTemplate` | `{ id?, type, identity, industry, level, template, variables }` | `{ id, version }` | Admin |
| `listIndustries` | `{}` | `{ list }` | 共享(读开放) |
| `saveIndustry` | `{ id?, code, name, jobs, companies }` | `{ id }` | Admin |

---

## 8. UI 设计 Token

`miniapp/styles/tokens.wxss`:

```css
page {
  /* 主色: 沉稳靛蓝,求职工具专业感 */
  --color-primary: #4F46E5;
  --color-primary-hover: #4338CA;
  --color-primary-bg: #EEF2FF;
  --color-secondary: #06B6D4;

  /* 语义色 */
  --color-success: #10B981;
  --color-warning: #F59E0B;
  --color-danger: #EF4444;

  /* 中性色 */
  --color-text: #111827;
  --color-text-secondary: #6B7280;
  --color-text-tertiary: #9CA3AF;
  --color-border: #E5E7EB;
  --color-border-strong: #D1D5DB;
  --color-bg: #F9FAFB;
  --color-bg-card: #FFFFFF;
  --color-bg-mask: rgba(0, 0, 0, 0.5);

  /* 间距(4 基础) */
  --space-1: 4px;   --space-2: 8px;   --space-3: 12px;
  --space-4: 16px;  --space-5: 20px;  --space-6: 24px;
  --space-8: 32px;  --space-10: 40px; --space-12: 48px;

  /* 圆角 */
  --radius-sm: 4px;  --radius-md: 8px;
  --radius-lg: 12px; --radius-full: 9999px;

  /* 字号 */
  --font-xs: 11px;  --font-sm: 13px; --font-base: 15px;
  --font-lg: 17px;  --font-xl: 19px; --font-2xl: 22px;
  --font-3xl: 28px;

  /* 字重 */
  --font-normal: 400; --font-medium: 500;
  --font-semibold: 600; --font-bold: 700;

  /* 阴影 */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.08);

  /* 行高 */
  --line-tight: 1.25;  --line-normal: 1.5;  --line-loose: 1.75;
}
```

**视觉基调**:白底卡片 + 大留白 + 靛蓝主色点缀;避免整屏紫/深色;圆角偏圆润(`--radius-md` 8px,卡片 12px)。

---

## 9. 错误处理

| 场景 | 处理 |
|---|---|
| 用户拒绝授权登录 | 首页 toast + 重试按钮 |
| 云函数 5xx | toast + 重试按钮 |
| `parseResume` 混元返回非 JSON | 后端正则容错,失败时返回 mock 占位 + 前端提示"解析失败,请尝试手动填写" |
| `optimizeResume` 评分字段缺失 | 后端默认值补全(各维度 70) |
| 内容安全审核 `Risky` | 返回 `CONTENT_RISKY`,前端 toast |
| 文件上传失败 | 前端预校验,toast 提示 |
| 拍照无权限 | 引导用户到设置开启 |
| Admin 登录失败 5 次 | 锁定 10 分钟(用云开发内存缓存) |

**前端错误处理规范**:
- `lib/api.js` 统一捕获云函数错误,toast 提示 `result.message`
- 列表页加载失败展示空状态 + 重试按钮
- 表单提交失败保留用户输入

---

## 10. 安全与合规

1. **数据隔离**:每个云函数自动按 `_openid` 过滤数据
2. **简历加密**:微信云开发存储默认静态加密
3. **敏感词过滤**:所有 AI 输出过 `msgSecCheck`
4. **Admin 安全**:账号密码走 HTTPS + 短期 token;操作记录 `updatedBy` + `updatedAt`
5. **用户协议与隐私政策**:首页底部加链接(v0.1 占位静态页)
6. **数据保留期**:v0.1 不设自动删除,用户可手动清空历史(v0.1 UI 占位)

---

## 11. 测试策略

| 层次 | 工具 | 覆盖范围 | 通过标准 |
|---|---|---|---|
| 单元 | Jest(本地 node 环境) | `hunyuan.js` mock 路径、prompt 模板匹配、auth token 验签 | 核心路径覆盖率 > 70% |
| 集成 | Jest + 云开发本地模拟 | 每个云函数成功/失败路径 | 每函数至少 1 happy + 1 sad 用例 |
| 端到端 | 微信开发者工具 + 手动 | 主链路 5 个页面跳转 + 优化/编辑/保存 | 5 个核心场景跑通 |
| 真机 | 微信扫码预览 | iOS + Android 各 1 台 | 不崩、UI 不错位 |

**v0.1 不做的**:UI 自动化测试、性能压测、安全渗透测试。

---

## 12. 部署

### 12.1 小程序

1. 微信开发者工具导入 `miniapp/`
2. 填入 AppID + 云开发环境 ID(在 `miniapp/lib/config.js` 顶部配置)
3. 上传代码 → 体验版 → 邀请测试
4. 提交审核(企业主体优先)

### 12.2 云函数

- 微信开发者工具右键 `cloudfunctions/<name>` → 上传并部署
- 或 `tcb` CLI:`tcb fn deploy <name>`
- 部署前在云开发控制台配置环境变量 `HUNYUAN_MODE` 等

### 12.3 Admin H5

```bash
cd admin
npm install
npm run build
# 产物在 admin/dist/,上传到云开发「静态网站托管」根目录
```

### 12.4 数据库初始化

v0.1 首次部署后,跑一次种子脚本(做成 Admin 的"初始化数据"按钮,或 `seed.js` 通过 `tcb` CLI 执行):
- 插入 12 个行业 + 60+ 岗位
- 插入 3-5 个默认 Prompt 模板(覆盖 5 种身份 × 通用行业)

---

## 13. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| 混元多模态对扫描版 PDF 识别率低 | 用户解析失败率高 | Mock 保底;失败时引导手动填;v0.3 优化 |
| 混元返回非严格 JSON | 后端解析异常 | 严格 prompt + 正则容错 + 失败降级 |
| 微信云函数 20s 超时 | 长文件处理失败 | 控制文件 ≤ 5MB(mock);live 监控超时率 |
| 用户隐私顾虑 | 不愿上传 | 首页明示数据用途 + 隐私政策 |
| 个人主体小程序审核受限 | 涉及 AI 内容可能被拒 | 先做体验版不审核;企业主体更稳 |
| Admin 后台被爆破 | Prompt 模板被改 | 密码 + token;v0.4 接 IP 白名单 |

---

## 14. 后续版本路线图

- **v0.2(2-3 周)**:面试题生成 + 求职信 + 自我介绍 + 版本切换器
- **v0.3(2 周)**:会员体系 + 微信支付 + OCR 兜底
- **v0.4(2-3 周)**:用户/订单/退款后台 + 内容审核工作流 + 数据看板

---

## 15. 关键术语

- **STAR 法则**:Situation + Task + Action + Result,简历经历的标准化写法
- **多模态**:支持文本 + 图片 + 文件输入
- **Prompt 模板**:发给大模型的指令字符串,含变量占位
- **行业岗位库**:行业 → 岗位 → 职级的树形数据
- **诊断打分**:4 维度(匹配度/完整性/专业性/量化度)0-100 评分
