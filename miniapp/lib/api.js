// @created 2026-06-16 v0.1 - 云函数调用封装
const storage = require('./storage');

const CLOUD_FUNC_TIMEOUT = 30000;

function call(name, data) {
  if (data === undefined) data = {};
  return new Promise(function (resolve, reject) {
    if (!wx.cloud) return reject(new Error('云开发未初始化'));
    wx.cloud.callFunction({
      name: name,
      data: data,
      timeout: CLOUD_FUNC_TIMEOUT,
    }).then(function (res) {
      const payload = res && res.result;
      if (!payload) return reject(new Error('empty response'));
      if (payload.code !== 0) {
        wx.showToast({ title: payload.message || '请求失败', icon: 'none' });
        return reject(new Error(payload.message || 'cloud function error'));
      }
      resolve(payload.data);
    }).catch(function (err) {
      console.error('[api]', name, err);
      wx.showToast({ title: (err && (err.errMsg || err.message)) || '网络异常', icon: 'none' });
      reject(err);
    });
  });
}

module.exports = { call: call };