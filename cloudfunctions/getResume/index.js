// @created 2026-06-16 v0.1 - 简历详情
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');

exports.main = async (event) => {
  try {
    const { id } = event;
    if (!id) return fail('BAD_REQUEST', 'id 必填');
    const res = await cloud.database().collection('resumes').doc(id).get();
    if (!res.data) return fail('NOT_FOUND', '简历不存在');
    return ok({ resume: res.data });
  } catch (err) {
    return fail(err.code || 'INTERNAL', err.message);
  }
};