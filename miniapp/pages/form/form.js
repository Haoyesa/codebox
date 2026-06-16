// @created 2026-06-16 v0.1 - 手动填写简历
const api = require('../../lib/api.js');
const app = getApp();

Page({
  data: {
    data: {
      name: '', phone: '', email: '',
      education: [{ school: '', major: '', degree: '', startDate: '', endDate: '' }],
      work: [{ company: '', title: '', startDate: '', endDate: '', description: '' }],
      projects: [],
      skills: [],
      skillsText: '',
    },
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({ ['data.' + field]: e.detail.value });
  },

  onEduInput(e) {
    const { idx, field } = e.currentTarget.dataset;
    const edu = this.data.data.education.slice();
    edu[idx][field] = e.detail.value;
    this.setData({ 'data.education': edu });
  },

  addEdu() {
    this.setData({
      'data.education': this.data.data.education.concat([{ school: '', major: '', degree: '', startDate: '', endDate: '' }]),
    });
  },

  onWorkInput(e) {
    const { idx, field } = e.currentTarget.dataset;
    const w = this.data.data.work.slice();
    w[idx][field] = e.detail.value;
    this.setData({ 'data.work': w });
  },

  addWork() {
    this.setData({
      'data.work': this.data.data.work.concat([{ company: '', title: '', startDate: '', endDate: '', description: '' }]),
    });
  },

  onSkillsInput(e) {
    const skills = e.detail.value.split(/[,,\s、]+/).filter(Boolean);
    this.setData({ 'data.skills': skills, 'data.skillsText': e.detail.value });
  },

  async onSave() {
    const data = this.data.data;
    if (!data.name) { wx.showToast({ title: '请填姓名', icon: 'none' }); return; }
    try {
      const target = app.globalData.target || {};
      const { resumeId } = await api.call('saveResume', {
        source: 'manual', data: data,
        identity: app.globalData.identity,
        targetIndustry: target.industry, targetJob: target.job, targetLevel: target.level,
      });
      app.globalData.currentResumeId = resumeId;
      wx.redirectTo({ url: '/pages/preview/preview?id=' + resumeId });
    } catch (e) {}
  },
});