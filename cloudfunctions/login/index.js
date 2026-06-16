// @created 2026-06-16 v0.1 - 微信登录换 openid
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');

exports.main = async (event, context) => {
  try {
    const { code } = event;
    if (!code) return fail('BAD_REQUEST', 'code 必填');

    // 真实流程:cloud.openapi.auth.code2Session({ code })
    // 测试 / 本地:直接用 context.OPENID(云开发自动注入)
    const openid = cloud.OPENID || context.OPENID;
    if (!openid) return fail('LOGIN_FAIL', 'no openid');

    const db = cloud.database();
    const exist = await db.collection('users').where({ _openid: openid }).count();
    const isNewUser = exist.total === 0;
    if (isNewUser) {
      await db.collection('users').add({
        data: { _openid: openid, createdAt: Date.now(), updatedAt: Date.now() },
      });
    }

    return ok({
      token: openid,        // v0.1 简化:用 openid 当 token
      openid,
      isNewUser,
    });
  } catch (err) {
    console.error('[login]', err);
    return fail('LOGIN_FAIL', err.message);
  }
};