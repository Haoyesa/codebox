// @created 2026-06-16 v0.1 - 选择求职身份
const app = getApp();

const IDENTITIES = [
  { code: 'freshgrad', name: '应届毕业生', desc: '即将或刚刚毕业,求职经验较少', icon: '🎓' },
  { code: 'social', name: '社招跳槽', desc: '有工作经验,寻求新机会', icon: '🚀' },
  { code: 'transition', name: '转行', desc: '跨行业或跨岗位', icon: '🔀' },
  { code: 'stateowned', name: '国企', desc: '倾向稳定、长期发展', icon: '🏛️' },
  { code: 'foreign', name: '外企', desc: '英文简历,注重表达专业度', icon: '🌐' },
];

Page({
  data: { items: IDENTITIES, selected: null },

  onSelect(e) {
    this.setData({ selected: e.currentTarget.dataset.code });
  },

  onConfirm() {
    if (!this.data.selected) {
      wx.showToast({ title: '请先选择身份', icon: 'none' });
      return;
    }
    app.globalData.identity = this.data.selected;
    wx.navigateTo({ url: '/pages/target/target' });
  },
});