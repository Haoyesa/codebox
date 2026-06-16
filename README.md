
# 简历优化 + 面试题小程序 v0.1

> AI 驱动的简历优化工具,微信原生小程序 + 微信云开发 + 腾讯混元大模型。

## 目录

- [快速开始](#快速开始)
- [环境变量](#环境变量)
- [数据库初始化](#数据库初始化)
- [Admin 后台](#admin-后台)
- [故障排查](#故障排查)
- [设计文档](#设计文档)

## 快速开始

### 1. 准备
- Node.js 20+
- 微信开发者工具(最新稳定版)
- 微信小程序 AppID(测试号也行,小程序后台 → 开发管理 → 开发设置可获取)
- 已开通的云开发环境(小程序后台 → 云开发 → 创建环境,选"按量付费"即可,v0.1 几乎不花钱)

### 2. 克隆 + 配置
```bash
git clone <your-repo>
cd project
npm install                # 装 jest 等开发依赖
```

### 3. 填 AppID 与云环境 ID
编辑 `miniapp/lib/config.js`:
```js
const CLOUD_ENV_ID = 'your-cloud-env-id';  // ← 替换
```
编辑 `miniapp/project.config.json` 的 `appid` 字段。

### 4. 部署云函数
微信开发者工具导入 `miniapp/`,右键 `cloudfunctions/` 下每个函数目录 → "上传并部署:云端安装依赖"。

部署顺序建议: `_shared`(无需单独部署,被引用) → `login` → `listIndustries` → `saveIndustry` → `listPromptTemplates` → `savePromptTemplate` → `parseResume` → `optimizeResume` → `saveResume` → `listResumes` → `getResume` → `adminLogin`。

### 5. 数据库初始化
详见下方"数据库初始化"。

### 6. 预览小程序
微信开发者工具点击"编译",模拟器即可看到首页。

## 环境变量

在云开发控制台 → 云函数 → 对应函数 → 配置 → 添加环境变量:

| 变量 | 必填 | 默认 | 说明 |
|---|---|---|---|
| HUNYUAN_MODE | 否 | mock | `mock` / `live` |
| HUNYUAN_SECRET_ID | live 模式必填 | - | 腾讯云 API 密钥 ID |
| HUNYUAN_SECRET_KEY | live 模式必填 | - | 腾讯云 API 密钥 Key |
| HUNYUAN_REGION | 否 | ap-guangzhou | 混元服务地域 |
| ADMIN_USERNAME | 是 | admin | Admin 登录账号 |
| ADMIN_PASSWORD | 是 | changeme | Admin 登录密码(请改!) |
| ADMIN_TOKEN_SECRET | 是 | dev-only-... | Admin token 签名密钥(请改!) |
| ADMIN_TOKEN_TTL | 否 | 7200 | token 有效期(秒) |

## 数据库初始化

v0.1 初始化数据:
- 12 个行业 + 60+ 岗位(来自 `cloudfunctions/_shared/seed.js`)
- 6 个默认 Prompt 模板(5 种身份 + parse,来自 `cloudfunctions/_shared/defaultPrompts.js`)

### 方法 A:用 Admin 后台
启动 Admin 后台后,登录后会自动加载行业岗位数据(只读,需手工添加)。

### 方法 B:本地 seed 脚本
```bash
# 在云开发控制台"云函数"→"高级"→"本地调试"中,执行 initData 脚本
# 或者写一个临时云函数 initData,执行后删除
```

具体操作:
1. 创建 `cloudfunctions/initData/index.js`:
   ```javascript
   const cloud = require('wx-server-sdk');
   cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
   const { INDUSTRIES } = require('../_shared/seed');
   const { DEFAULT_TEMPLATES } = require('../_shared/defaultPrompts');

   exports.main = async () => {
     const db = cloud.database();
     for (const ind of INDUSTRIES) {
       const exist = await db.collection('industries').where({ code: ind.code }).count();
       if (exist.total === 0) await db.collection('industries').add({ data: { ...ind, createdAt: Date.now(), updatedAt: Date.now() } });
     }
     for (const tpl of DEFAULT_TEMPLATES) {
       const exist = await db.collection('prompt_templates').where({ type: tpl.type, identity: tpl.identity }).count();
       if (exist.total === 0) await db.collection('prompt_templates').add({ data: { ...tpl, active: true, createdAt: Date.now(), updatedAt: Date.now() } });
     }
     return { industries: INDUSTRIES.length, templates: DEFAULT_TEMPLATES.length };
   };
   ```
2. 上传并部署 initData
3. 在云开发控制台的"云函数测试"里调用 `initData`,看到返回 `{ industries: 12, templates: 6 }`
4. 验证:`listIndustries` 应返回 12 条;`listPromptTemplates` 应返回 6 条
5. **删除 initData 函数**(留作后门有安全风险)

## Admin 后台

```bash
cd admin
npm install
npm run dev                 # 本地开发
npm run build               # 产物在 dist/
```

部署到生产:
1. 在云开发控制台 → 静态网站托管 → 上传 `admin/dist/`
2. 配置 `admin/.env.production` 的 `VITE_API_BASE` 为云函数 HTTP 触发器 URL 前缀
3. 重新 `npm run build`,再上传

云函数 HTTP 触发器配置:控制台 → 云函数 → 选函数 → 触发管理 → 添加 HTTP 触发器。给以下函数都配:
- adminLogin
- listIndustries
- saveIndustry
- listPromptTemplates
- savePromptTemplate

## 故障排查

| 症状 | 排查 |
|---|---|
| 小程序白屏 | 检查 `miniapp/lib/config.js` 的 `CLOUD_ENV_ID` 是否正确 |
| 云函数 404 | 函数未上传,右键对应目录重新上传 |
| 云函数返回 "cloud function error" | 看云开发控制台 → 云函数 → 日志 |
| AI 返回内容异常 | 确认 `HUNYUAN_MODE=mock`,此时应返回张三固定数据;如仍异常,看 `_shared/hunyuan.js` 是否被改坏 |
| Admin 登录失败 | 检查 `ADMIN_USERNAME` / `ADMIN_PASSWORD` 环境变量是否设置 |
| 文件上传失败 | 文件超过 10MB,或云存储未开通 |

## 设计文档

- [v0.1 设计文档](docs/superpowers/specs/2026-06-16-resume-mini-program-v0.1-design.md)
- [v0.1 实施计划](docs/superpowers/plans/2026-06-16-resume-mini-program-v0.1-plan.md)
