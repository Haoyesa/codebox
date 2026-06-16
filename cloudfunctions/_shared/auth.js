// @created 2026-06-16 v0.1 - 鉴权工具(C 端 _openid + Admin token)
'use strict';

const crypto = require('crypto');
const { ADMIN_TOKEN_SECRET, ADMIN_TOKEN_TTL } = require('./config');

class AuthError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

function authUser(context) {
  // 微信云开发自动注入 userInfo.openId
  const openid = (context && context.OPENID) || (context && context.userInfo && context.userInfo.openId);
  if (!openid) {
    throw new AuthError('UNAUTHORIZED', 'missing openid in context');
  }
  return openid;
}

function signAdminToken(username, exp) {
  const payload = `${username}.${exp}`;
  const sig = crypto.createHmac('sha256', ADMIN_TOKEN_SECRET).update(payload).digest('hex');
  return Buffer.from(payload).toString('base64url') + '.' + sig;
}

function verifyAdminToken(token) {
  if (typeof token !== 'string' || !token.includes('.')) {
    throw new AuthError('UNAUTHORIZED', 'invalid token format');
  }
  const dot = token.indexOf('.');
  const b64 = token.slice(0, dot);
  const sig = token.slice(dot + 1);
  const payload = Buffer.from(b64, 'base64url').toString('utf8');
  const [username, expStr] = payload.split('.');
  const exp = Number(expStr);
  const expectedSig = crypto.createHmac('sha256', ADMIN_TOKEN_SECRET).update(payload).digest('hex');
  // timingSafeEqual 要求等长 buffer
  if (sig.length !== expectedSig.length || !crypto.timingSafeEqual(Buffer.from(sig, 'utf8'), Buffer.from(expectedSig, 'utf8'))) {
    throw new AuthError('UNAUTHORIZED', 'bad signature');
  }
  if (Date.now() > exp) {
    throw new AuthError('TOKEN_EXPIRED', 'token expired');
  }
  return { username, exp };
}

function authAdmin(event) {
  const token = event && event.adminToken;
  if (!token) {
    throw new AuthError('UNAUTHORIZED', 'missing admin token');
  }
  return verifyAdminToken(token);
}

module.exports = { AuthError, authUser, authAdmin, signAdminToken, verifyAdminToken };