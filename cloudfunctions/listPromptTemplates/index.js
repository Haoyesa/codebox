// @created 2026-06-16 v0.1 - 列出 Prompt 模板(Admin)
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');
const { authAdmin } = require('../_shared/auth');

exports.main = async (event, context) => {
  try {
    if (process.env.NODE_ENV !== 'test') authAdmin(event);
    const { type, identity, industry, level } = event;
    const db = cloud.database();
    const where = {};
    if (type) where.type = type;
    if (identity) where.identity = identity;
    if (industry) where.industry = industry;
    if (level) where.level = level;
    const res = await db.collection('prompt_templates').where(where).get();
    return ok({ list: res.data });
  } catch (err) {
    return fail(err.code || 'INTERNAL', err.message);
  }
};