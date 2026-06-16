// @created 2026-06-16 v0.1 - 历史列表
const api = require('../../lib/api.js');

Page({
  data: { list: [], loading: true },

  onShow() { this.load(); },

  async load() {
    this.setData({ loading: true });
    try {
      const { list } = await api.call('listResumes', { page: 1, pageSize: 50 });
      this.setData({ list: list });
    } catch (e) {} finally {
      this.setData({ loading: false });
    }
  },

  onTap(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/preview/preview?id=' + id });
  },
});