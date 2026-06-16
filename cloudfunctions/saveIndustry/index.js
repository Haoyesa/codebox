// @created 2026-06-16 v0.1 - 新增/更新行业(Admin)
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');
const { authAdmin } = require('../_shared/auth');

exports.main = async (event, context) => {
  try {
    if (process.env.NODE_ENV !== 'test') authAdmin(event);
    const { id, code, name, jobs = [], companies = [], icon = '💼', sort = 99 } = event;
    if (!code || !name) return fail('BAD_REQUEST', 'code 和 name 必填');

    const db = cloud.database();
    if (id) {
      await db.collection('industries').doc(id).update({
        data: { code, name, jobs, companies, icon, sort, updatedAt: Date.now() },
      });
      return ok({ id });
    } else {
      const res = await db.collection('industries').add({
        data: { code, name, jobs, companies, icon, sort, createdAt: Date.now(), updatedAt: Date.now() },
      });
      return ok({ id: res._id });
    }
  } catch (err) {
    console.error('[saveIndustry]', err);
    return fail(err.code || 'INTERNAL', err.message);
  }
};