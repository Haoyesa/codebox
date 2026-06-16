// @created 2026-06-16 v0.1 - 优化结果 + 左右编辑 + 评分
const api = require('../../lib/api.js');
const app = getApp();

Page({
  data: {
    resumeId: null,
    original: null,
    optimized: null,
    score: null,
    suggestions: [],
    loading: false,
    saving: false,
    optimizing: false,
  },

  onLoad(q) {
    this.setData({ resumeId: q.id });
    this.loadResume();
  },

  async loadResume() {
    this.setData({ loading: true });
    try {
      const { resume } = await api.call('getResume', { id: this.data.resumeId });
      this.setData({
        original: resume.data,
        optimized: resume.optimized,
        score: resume.score,
        suggestions: resume.suggestions || [],
      });
      if (!resume.optimized) this.runOptimize();
    } catch (e) {} finally {
      this.setData({ loading: false });
    }
  },

  async runOptimize() {
    this.setData({ optimizing: true });
    try {
      const target = app.globalData.target || {};
      const { optimized, score, suggestions } = await api.call('optimizeResume', {
        resumeId: this.data.resumeId,
        identity: app.globalData.identity,
        industry: target.industry, job: target.job, level: target.level,
      });
      this.setData({ optimized: optimized, score: score, suggestions: suggestions });
    } catch (e) {} finally {
      this.setData({ optimizing: false });
    }
  },

  onOptimizedWorkInput(e) {
    const { idx, field } = e.currentTarget.dataset;
    const w = this.data.optimized.work.slice();
    w[idx][field] = e.detail.value;
    this.setData({ 'optimized.work': w });
  },

  async onSave() {
    this.setData({ saving: true });
    try {
      const target = app.globalData.target || {};
      await api.call('saveResume', {
        id: this.data.resumeId,
        source: 'word',
        data: this.data.original,
        optimized: this.data.optimized,
        score: this.data.score,
        suggestions: this.data.suggestions,
        identity: app.globalData.identity,
        targetIndustry: target.industry, targetJob: target.job, targetLevel: target.level,
      });
      wx.showToast({ title: '已保存', icon: 'success' });
      setTimeout(function () { wx.switchTab({ url: '/pages/history/history' }); }, 800);
    } catch (e) {} finally {
      this.setData({ saving: false });
    }
  },

  onCopy() {
    const text = JSON.stringify(this.data.optimized, null, 2);
    wx.setClipboardData({
      data: text,
      success: function () { wx.showToast({ title: '已复制', icon: 'success' }); },
    });
  },
});