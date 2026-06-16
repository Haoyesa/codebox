// @created 2026-06-16 v0.1 - 个人中心(v0.1 占位)
const app = getApp();

Page({
  data: { identity: null },
  onShow() { this.setData({ identity: app.globalData.identity }); },
  onReset() {
    app.globalData.identity = null;
    app.globalData.target = null;
    app.globalData.currentResumeId = null;
    wx.showToast({ title: '已重置', icon: 'success' });
    this.setData({ identity: null });
  },
});