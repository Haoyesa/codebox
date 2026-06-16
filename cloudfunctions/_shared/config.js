// @created 2026-06-16 v0.1 - 运行时配置(从环境变量读取)
'use strict';

module.exports = {
  ADMIN_USERNAME: process.env.ADMIN_USERNAME || 'admin',
  ADMIN_PASSWORD: process.env.ADMIN_PASSWORD || 'changeme',
  ADMIN_TOKEN_SECRET: process.env.ADMIN_TOKEN_SECRET || 'dev-only-secret-replace-in-prod-12345',
  ADMIN_TOKEN_TTL: Number(process.env.ADMIN_TOKEN_TTL) || 7200,
  HUNYUAN_MODE: process.env.HUNYUAN_MODE || 'mock',
  HUNYUAN_SECRET_ID: process.env.HUNYUAN_SECRET_ID || '',
  HUNYUAN_SECRET_KEY: process.env.HUNYUAN_SECRET_KEY || '',
  HUNYUAN_REGION: process.env.HUNYUAN_REGION || 'ap-guangzhou',
};