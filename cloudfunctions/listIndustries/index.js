// @created 2026-06-16 v0.1 - 列出行业岗位树
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');

exports.main = async () => {
  try {
    const db = cloud.database();
    const res = await db.collection('industries').orderBy('sort', 'asc').get();
    return ok({ list: res.data });
  } catch (err) {
    console.error('[listIndustries]', err);
    return fail('INTERNAL', err.message);
  }
};