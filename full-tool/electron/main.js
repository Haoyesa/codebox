const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;

const http = require('http');

function waitForVite(port, retries = 30) {
  return new Promise((resolve, reject) => {
    function tryPort(p) {
      const req = http.get(`http://localhost:${p}`, (res) => {
        if (res.statusCode === 200) { resolve(p); }
      });
      req.on('error', () => {
        if (p <= port + 10) { setTimeout(() => tryPort(p + 1), 500); }
        else { reject(new Error('Vite server not found')); }
      });
      req.setTimeout(1000, () => {
        req.destroy();
        if (p <= port + 10) { setTimeout(() => tryPort(p + 1), 500); }
        else { reject(new Error('Vite server timeout')); }
      });
    }
    tryPort(port);
  });
}

async function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 800,
    minWidth: 960,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    },
    icon: path.join(__dirname, '../public/icon.ico'),
    show: false
  });

  // 开发模式等待 Vite 启动，生产模式加载打包文件
  if (process.env.NODE_ENV === 'development' || !app.isPackaged) {
    try {
      const vitePort = await waitForVite(5173);
      console.log('Vite ready on port', vitePort);
      mainWindow.loadURL(`http://localhost:${vitePort}`);
    } catch (e) {
      console.error('Failed to connect to Vite:', e.message);
      app.quit();
      return;
    }
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// ========== IPC 处理 ==========

// 选择文件
ipcMain.handle('dialog:openFiles', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: '办公文档', extensions: ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'] }
    ],
    ...options
  });
  return result;
});

// 选择文件夹
ipcMain.handle('dialog:openDirectory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return result;
});

// 选择输出目录
ipcMain.handle('dialog:selectOutputDir', async () => {
  console.log('[IPC] dialog:selectOutputDir called, mainWindow exists:', !!mainWindow);
  try {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory', 'createDirectory']
    });
    console.log('[IPC] dialog result:', JSON.stringify(result));
    return result;
  } catch (err) {
    console.error('[IPC] dialog:selectOutputDir error:', err.message);
    throw err;
  }
});

// LibreOffice 转换
ipcMain.handle('libreoffice:convert', async (event, { inputPath, outputDir, scale = 1 }) => {
  return new Promise((resolve, reject) => {
    // 查找 LibreOffice 可执行文件路径
    const loPaths = [
      'C:/Program Files/LibreOffice/program/soffice.exe',
      'C:/Program Files (x86)/LibreOffice/program/soffice.exe',
      path.join(app.getPath('userData'), 'LibreOffice/App/libreoffice/program/soffice.exe')
    ];

    let loExe = loPaths.find(p => fs.existsSync(p));
    if (!loExe) {
      reject(new Error('未找到 LibreOffice，请先下载安装'));
      return;
    }

    const outputPath = outputDir.replace(/\\/g, '/');
    const args = [
      '--headless',
      '--convert-to', 'png',
      '--outdir', outputPath,
      inputPath
    ];

    console.log('Running LibreOffice:', loExe, args.join(' '));

    const proc = spawn(loExe, args, { shell: true });
    let stdout = '', stderr = '';

    proc.stdout.on('data', d => stdout += d);
    proc.stderr.on('data', d => stderr += d);

    proc.on('close', (code) => {
      if (code === 0) {
        resolve({ success: true, output: outputPath });
      } else {
        reject(new Error(stderr || `LibreOffice 转换失败，退出码: ${code}`));
      }
    });

    proc.on('error', err => reject(err));
  });
});

// 读取目录下的所有文件
ipcMain.handle('fs:readDir', async (event, dirPath) => {
  try {
    const files = fs.readdirSync(dirPath);
    return { success: true, files };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// 获取文件信息
ipcMain.handle('fs:getFileInfo', async (event, filePath) => {
  try {
    const stats = fs.statSync(filePath);
    return { success: true, size: stats.size, mtime: stats.mtime };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// 写入文件
ipcMain.handle('fs:writeFile', async (event, filePath, data) => {
  try {
    const buffer = Buffer.from(data);
    fs.writeFileSync(filePath, buffer);
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// 重命名文件
ipcMain.handle('fs:renameFile', async (event, oldPath, newName) => {
  try {
    const dir = path.dirname(oldPath);
    const newPath = path.join(dir, newName);
    fs.renameSync(oldPath, newPath);
    return { success: true, newPath };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// 保存文件（用于导出）
ipcMain.handle('dialog:saveFile', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

// 下载文件
ipcMain.handle('download:file', async (event, { url, savePath }) => {
  return new Promise((resolve, reject) => {
    const https = require('https');
    const http = require('http');
    const file = fs.createWriteStream(savePath);
    const get = url.startsWith('https') ? https.get : http.get;

    get(url, (response) => {
      if (response.statusCode === 302 || response.statusCode === 301) {
        file.close();
        resolve({ redirect: true, location: response.headers.location });
        return;
      }
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve({ success: true });
      });
    }).on('error', (err) => {
      fs.unlink(savePath, () => {});
      reject(err);
    });
  });
});