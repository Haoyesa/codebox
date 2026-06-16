// @created 2026-06-16 v0.1 - 选择简历导入方式
const app = getApp();

const WAYS = [
  { key: 'upload', icon: '📄', name: '上传文件', desc: '支持 Word / PDF / 图片,最大 10MB' },
  { key: 'camera', icon: '📷', name: '拍照 / 相册', desc: '拍简历照片或选图' },
  { key: 'form',   icon: '✍️', name: '手动填写', desc: '在表单中填写基本信息' },
];

Page({
  data: { ways: WAYS },
  onPick(e) {
    const key = e.currentTarget.dataset.key;
    if (key === 'form') {
      wx.navigateTo({ url: '/pages/form/form' });
    } else {
      wx.navigateTo({ url: '/pages/' + key + '/' + key });
    }
  },
});