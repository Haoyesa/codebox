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
  readDir: (path) => ipcRenderer.invoke('fs:readDir', path),
  readFile: (path) => ipcRenderer.invoke('fs:readFile', path),
  getFileInfo: (path) => ipcRenderer.invoke('fs:getFileInfo', path),
  saveFile: (options) => ipcRenderer.invoke('dialog:saveFile', options),
  writeFile: (path, data) => ipcRenderer.invoke('fs:writeFile', path, data),
  unlink: (path) => ipcRenderer.invoke('fs:unlink', path),
  renameFile: (oldPath, newName) => ipcRenderer.invoke('fs:renameFile', oldPath, newName),

  // 下载
  downloadFile: (options) => ipcRenderer.invoke('download:file', options),

  // 平台信息
  platform: process.platform
});