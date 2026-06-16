// @created 2026-06-16 v0.1 - 小程序入口
const { CLOUD_ENV_ID } = require('./lib/config.js');

App({
  globalData: {
    userInfo: null,
    identity: null,
    target: null,
    currentResumeId: null,
  },

  onLaunch() {
    if (!wx.cloud) {
      console.error('当前微信版本过低,请升级到 8.0.30+');
      return;
    }
    wx.cloud.init({
      env: CLOUD_ENV_ID,
      traceUser: true,
    });
  },
});