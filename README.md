# 简历优化 + 面试题小程序 v0.1

> AI 驱动的简历优化 + 面试题生成工具,聚焦求职场景。

## 快速开始

参见 `docs/superpowers/specs/2026-06-16-resume-mini-program-v0.1-design.md` 了解设计;本文档只说"怎么跑起来"。

### 环境要求
- Node.js 20+ (LTS)
- 微信开发者工具(最新稳定版)
- 微信小程序 AppID(测试号也行)
- (可选)腾讯云密钥,用于激活真实混元调用

### 目录
- `miniapp/` - 微信原生小程序
- `cloudfunctions/` - 微信云开发云函数
- `admin/` - H5 管理后台(Vue 3 + Vite)
- `docs/superpowers/` - 设计文档与实施计划

### 启动

1. **微信开发者工具** 导入 `miniapp/`,填入 AppID,即可在模拟器预览
2. **云函数**:在 `cloudfunctions/` 目录右键上传并部署每个函数
3. **Admin 后台**:
   ```bash
   cd admin
   npm install
   npm run dev      # 本地开发
   npm run build    # 产物在 dist/,上传到云开发静态托管
   ```

### 环境变量

在微信云开发控制台配置:
- `HUNYUAN_MODE` - `mock`(默认) | `live`
- `HUNYUAN_SECRET_ID` - live 模式必填
- `HUNYUAN_SECRET_KEY` - live 模式必填
- `HUNYUAN_REGION` - 默认 `ap-guangzhou`
- `ADMIN_USERNAME` - Admin 登录账号,默认 `admin`
- `ADMIN_PASSWORD` - Admin 登录密码(初次部署必须改)
- `ADMIN_TOKEN_SECRET` - Admin token 签名密钥
- `ADMIN_TOKEN_TTL` - token 有效期(秒),默认 7200

### 当前状态

- v0.1 主链路已实现(上传/解析/优化/编辑/保存/历史)
- v0.1 Admin 仅包含 Prompt 模板与行业岗位库两个模块
- v0.2+ 计划见设计文档 §14
