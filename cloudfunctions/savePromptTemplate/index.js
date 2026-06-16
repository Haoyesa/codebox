// @created 2026-06-16 v0.1 - 保存/更新 Prompt 模板(Admin)
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');
const { authAdmin } = require('../_shared/auth');

exports.main = async (event, context) => {
  try {
    if (process.env.NODE_ENV !== 'test') authAdmin(event);
    const { id, type, identity, industry = '*', level = '*', template, variables = [] } = event;
    if (!type || !identity || !template) return fail('BAD_REQUEST', 'type/identity/template 必填');

    const db = cloud.database();
    const now = Date.now();
    if (id) {
      const cur = await db.collection('prompt_templates').doc(id).get();
      const nextVersion = (cur.data && cur.data.version ? cur.data.version : 0) + 1;
      await db.collection('prompt_templates').doc(id).update({
        data: { type, identity, industry, level, template, variables, version: nextVersion, updatedAt: now, updatedBy: 'admin' },
      });
      return ok({ id, version: nextVersion });
    } else {
      const res = await db.collection('prompt_templates').add({
        data: { type, identity, industry, level, template, variables, version: 1, active: true, createdAt: now, updatedAt: now, updatedBy: 'admin' },
      });
      return ok({ id: res._id, version: 1 });
    }
  } catch (err) {
    return fail(err.code || 'INTERNAL', err.message);
  }
};