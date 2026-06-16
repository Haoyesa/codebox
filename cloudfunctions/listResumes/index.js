// @created 2026-06-16 v0.1 - 简历列表(分页,按 updatedAt 倒序)
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');

exports.main = async (event) => {
  try {
    const page = Math.max(Number(event.page) || 1, 1);
    const pageSize = Math.min(Number(event.pageSize) || 10, 50);
    const db = cloud.database();
    const col = db.collection('resumes').where({ _openid: cloud.OPENID });
    const total = (await col.count()).total;
    const res = await col.orderBy('updatedAt', 'desc').skip((page - 1) * pageSize).limit(pageSize).get();
    return ok({ list: res.data, total, page, pageSize });
  } catch (err) {
    return fail(err.code || 'INTERNAL', err.message);
  }
};