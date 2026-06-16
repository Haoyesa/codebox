// @created 2026-06-16 v0.1 - 文件上传 + 解析
const api = require('../../lib/api.js');

Page({
  data: { uploading: false, fileName: '' },

  onChoose() {
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      success: (res) => {
        const f = res.tempFiles[0];
        if (f.size > 10 * 1024 * 1024) {
          wx.showToast({ title: '文件不能超过 10MB', icon: 'none' });
          return;
        }
        this.setData({ fileName: f.name });
        this.doUploadAndParse(f.path);
      },
    });
  },

  async doUploadAndParse(filePath) {
    this.setData({ uploading: true });
    try {
      const ts = Date.now();
      const safeName = (this.data.fileName || 'file').replace(/[^\w.\-]/g, '_');
      const cloudPath = 'resumes/' + ts + '_' + safeName;
      const up = await wx.cloud.uploadFile({ cloudPath, filePath });
      const { data } = await api.call('parseResume', { fileID: up.fileID });
      wx.redirectTo({
        url: '/pages/confirm/confirm?data=' + encodeURIComponent(JSON.stringify(data)) + '&fileID=' + encodeURIComponent(up.fileID),
      });
    } catch (e) {
      console.error(e);
    } finally {
      this.setData({ uploading: false });
    }
  },
});