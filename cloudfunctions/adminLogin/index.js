// @created 2026-06-16 v0.1 - Admin 登录(账号密码换 token)
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_TOKEN_SECRET, ADMIN_TOKEN_TTL } = require('../_shared/config');
const { ok, fail } = require('../_shared/response');
const { signAdminToken } = require('../_shared/auth');
const crypto = require('crypto');

function hash(pwd) {
  return crypto.createHash('sha256').update(pwd).digest('hex');
}

exports.main = async (event) => {
  const { username, password } = event;
  if (typeof username !== 'string' || typeof password !== 'string') {
    return fail('AUTH_FAIL', '账号或密码错误');
  }
  if (hash(username) !== hash(ADMIN_USERNAME) || hash(password) !== hash(ADMIN_PASSWORD)) {
    return fail('AUTH_FAIL', '账号或密码错误');
  }
  const exp = Date.now() + ADMIN_TOKEN_TTL * 1000;
  const token = signAdminToken(username, exp);
  return ok({ token, exp });
};