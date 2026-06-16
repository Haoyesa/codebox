// @created 2026-06-16 v0.1 - 目标岗位选择(行业-岗位-职级)
const api = require('../../lib/api.js');
const app = getApp();

Page({
  data: {
    industries: [],
    selectedIndustry: null,
    jobs: [],
    selectedJob: null,
    levels: [],
    selectedLevel: null,
  },

  onLoad() { this.loadIndustries(); },

  async loadIndustries() {
    try {
      const { list } = await api.call('listIndustries');
      this.setData({ industries: list });
    } catch (e) { /* toast */ }
  },

  onPickIndustry(e) {
    const ind = this.data.industries.find(i => i.code === e.currentTarget.dataset.code);
    this.setData({
      selectedIndustry: ind,
      jobs: ind ? ind.jobs : [],
      selectedJob: null,
      levels: [],
      selectedLevel: null,
    });
  },

  onPickJob(e) {
    const job = this.data.jobs.find(j => j.code === e.currentTarget.dataset.code);
    this.setData({
      selectedJob: job,
      levels: job ? job.levels : [],
      selectedLevel: null,
    });
  },

  onPickLevel(e) {
    const level = this.data.levels.find(l => l.code === e.currentTarget.dataset.code);
    this.setData({ selectedLevel: level });
  },

  onConfirm() {
    const { selectedIndustry, selectedJob, selectedLevel } = this.data;
    if (!selectedIndustry || !selectedJob || !selectedLevel) {
      wx.showToast({ title: '请选完三级', icon: 'none' });
      return;
    }
    app.globalData.target = {
      industry: selectedIndustry.code,
      job: selectedJob.code,
      level: selectedLevel.code,
    };
    wx.navigateTo({ url: '/pages/import/import' });
  },
});