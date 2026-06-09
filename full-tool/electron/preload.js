const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // 文件选择
  openFiles: (options) => ipcRenderer.invoke('dialog:openFiles', options),
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  selectOutputDir: () => ipcRenderer.invoke('dialog:selectOutputDir'),

  // LibreOffice 转换
  libreOfficeConvert: (options) => ipcRenderer.invoke('libreoffice:convert', options),

  // 文件系统
  readDir: (path) => ipcRenderer.invoke('fs:readDir', path),
  getFileInfo: (path) => ipcRenderer.invoke('fs:getFileInfo', path),
  saveFile: (options) => ipcRenderer.invoke('dialog:saveFile', options),

  // 下载
  downloadFile: (options) => ipcRenderer.invoke('download:file', options),

  // 平台信息
  platform: process.platform
});