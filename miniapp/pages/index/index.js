// @created 2026-06-16 v0.1 - 首页
const auth = require('../../lib/auth.js');
const app = getApp();

Page({
  data: {
    identity: null,
  },

  onShow() {
    this.setData({ identity: app.globalData.identity });
  },

  async onStart() {
    try {
      await auth.login();
      if (!app.globalData.identity) {
        wx.navigateTo({ url: '/pages/identity/identity' });
      } else {
        wx.navigateTo({ url: '/pages/import/import' });
      }
    } catch (e) {
      // toast 已在 api.js 触发
    }
  },

  onGoHistory() {
    wx.switchTab({ url: '/pages/history/history' });
  },
});