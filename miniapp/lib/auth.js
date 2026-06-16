// @created 2026-06-16 v0.1 - 登录管理
const api = require('./api');
const storage = require('./storage');

const TOKEN_KEY = 'auth_token';
const OPENID_KEY = 'openid';

async function login() {
  const cached = storage.get(TOKEN_KEY);
  if (cached) return { token: cached, openid: storage.get(OPENID_KEY), isNewUser: false };
  const loginRes = await new Promise(function (resolve, reject) {
    wx.login({ success: resolve, fail: reject });
  });
  const data = await api.call('login', { code: loginRes.code });
  storage.set(TOKEN_KEY, data.token);
  storage.set(OPENID_KEY, data.openid);
  return data;
}

function logout() {
  storage.remove(TOKEN_KEY);
  storage.remove(OPENID_KEY);
}

function getToken() { return storage.get(TOKEN_KEY); }

module.exports = { login: login, logout: logout, getToken: getToken };