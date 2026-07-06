const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // 文件选择
  openFiles: (options) => ipcRenderer.invoke('dialog:openFiles', options),
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  selectOutputDir: () => ipcRenderer.invoke('dialog:selectOutputDir'),

  // LibreOffice 转换
  libreOfficeConvert: (options) => ipcRenderer.invoke('libreoffice:convert', options),
  libreOfficeCheck: () => ipcRenderer.invoke('libreoffice:check'),
  libreOfficeSetPath: (exePath) => ipcRenderer.invoke('libreoffice:setPath', exePath),

  // 文件系统
  readDir: (path, options) => ipcRenderer.invoke('fs:readDir', path, options),
  readFile: (path) => ipcRenderer.invoke('fs:readFile', path),
  getFileInfo: (path) => ipcRenderer.invoke('fs:getFileInfo', path),
  saveFile: (options) => ipcRenderer.invoke('dialog:saveFile', options),
  writeFile: (path, data) => ipcRenderer.invoke('fs:writeFile', path, data),
  unlink: (path) => ipcRenderer.invoke('fs:unlink', path),
  renameFile: (oldPath, newName) => ipcRenderer.invoke('fs:renameFile', oldPath, newName),

  // 下载
  downloadFile: (options) => ipcRenderer.invoke('download:file', options),

  // Feishu / Lark open platform (proxied through main to avoid CORS).
  feishuGetToken: (payload) => ipcRenderer.invoke('feishu:getToken', payload),
  feishuResolveWiki: (payload) => ipcRenderer.invoke('feishu:resolveWiki', payload),
  feishuListRecords: (payload) => ipcRenderer.invoke('feishu:listRecords', payload),
  feishuUploadAttachment: (payload) => ipcRenderer.invoke('feishu:uploadAttachment', payload),
  feishuUpdateRecord: (payload) => ipcRenderer.invoke('feishu:updateRecord', payload),

  // 平台信息
  platform: process.platform,

  // 外部链接
  openExternal: (url) => ipcRenderer.invoke('shell:openExternal', url),

  // 日志持久化
  logRead: () => ipcRenderer.invoke('log:read'),
  logWrite: (logs) => ipcRenderer.invoke('log:append', logs)
});