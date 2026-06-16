// @created 2026-06-16 v0.1 - 解析结果确认/微调
const api = require('../../lib/api.js');
const app = getApp();

Page({
  data: { data: null, fileID: '', skillsText: '' },

  onLoad(q) {
    try {
      const data = JSON.parse(decodeURIComponent(q.data));
      this.setData({ data: data, fileID: q.fileID || '', skillsText: (data.skills || []).join(', ') });
    } catch (e) {
      wx.showToast({ title: '数据异常', icon: 'none' });
    }
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({ ['data.' + field]: e.detail.value });
  },

  onSkillsInput(e) {
    const skills = e.detail.value.split(/[,,\s、]+/).filter(Boolean);
    this.setData({ skillsText: e.detail.value, 'data.skills': skills });
  },

  onWorkInput(e) {
    const { idx, field } = e.currentTarget.dataset;
    const w = this.data.data.work.slice();
    w[idx][field] = e.detail.value;
    this.setData({ 'data.work': w });
  },

  async onConfirm() {
    const { data, fileID } = this.data;
    if (!data.name) { wx.showToast({ title: '请填姓名', icon: 'none' }); return; }
    try {
      const target = app.globalData.target || {};
      let source = 'manual';
      if (fileID) {
        if (/\.pdf$/i.test(fileID)) source = 'pdf';
        else if (/\.(jpe?g|png)$/i.test(fileID)) source = 'image';
        else source = 'word';
      }
      const { resumeId } = await api.call('saveResume', {
        source: source, fileID: fileID, data: data,
        identity: app.globalData.identity,
        targetIndustry: target.industry, targetJob: target.job, targetLevel: target.level,
      });
      app.globalData.currentResumeId = resumeId;
      wx.redirectTo({ url: '/pages/preview/preview?id=' + resumeId });
    } catch (e) {}
  },
});