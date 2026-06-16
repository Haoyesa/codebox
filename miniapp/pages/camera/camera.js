// @created 2026-06-16 v0.1 - 拍照/相册
const api = require('../../lib/api.js');

Page({
  data: { uploading: false },

  onCamera() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera'],
      camera: 'back',
      success: (res) => this.handleImage(res.tempFiles[0].tempFilePath),
    });
  },

  onAlbum() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      success: (res) => this.handleImage(res.tempFiles[0].tempFilePath),
    });
  },

  async handleImage(filePath) {
    this.setData({ uploading: true });
    try {
      const ts = Date.now();
      const m = filePath.match(/\.(\w+)$/);
      const ext = m ? m[1] : 'jpg';
      const cloudPath = 'resumes/' + ts + '.' + ext;
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