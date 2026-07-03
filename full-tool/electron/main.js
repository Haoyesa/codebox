const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');
const os = require('os');

let mainWindow;

const http = require('http');

// ========== 安全辅助函数 ==========

/**
 * Check whether a target path is within allowed directories.
 * Prevents directory traversal attacks from the renderer.
 */
function isPathAllowed(targetPath) {
  if (typeof targetPath !== 'string' || !targetPath) return false;
  const normalized = path.resolve(targetPath);
  const allowed = [
    app.getPath('home'),
    app.getPath('desktop'),
    app.getPath('documents'),
    app.getPath('downloads'),
    app.getPath('temp'),
    app.getPath('userData'),
    process.cwd()
  ].filter(Boolean);
  return allowed.some(base => normalized.startsWith(path.resolve(base)));
}

function validatePath(targetPath, operation) {
  if (!isPathAllowed(targetPath)) {
    throw new Error(`Path not allowed for ${operation}: ${targetPath}`);
  }
}

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
      nodeIntegration: false,
      webviewTag: true
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
  try {
    const result = await dialog.showOpenDialog(mainWindow, {
      properties: ['openDirectory', 'createDirectory']
    });
    return result;
  } catch (err) {
    console.error('[IPC] dialog:selectOutputDir error:', err.message);
    throw err;
  }
});

// 查找 LibreOffice 可执行文件：先读用户配置覆盖，再试 where soffice.exe，再试常见安装路径
// Return true only if `exe` lives in a real LO install dir
// (one that ships the bundled runtime / uno bridge next to it).
// Skips stubs like the Microsoft Store shim, which has no DLLs.
function isRealLO(exe) {
  try {
    const dir = path.dirname(exe);
    return ['soffice.bin', 'oosplash.exe', 'fundamentalrc', path.join('ure', 'bin')]
      .some((rel) => fs.existsSync(path.join(dir, rel)));
  } catch (_) { return false; }
}

function findLibreOffice() {
  const settingsPath = path.join(app.getPath('userData'), 'lo-path.txt');
  if (fs.existsSync(settingsPath)) {
    const p = fs.readFileSync(settingsPath, 'utf8').trim();
    if (p && fs.existsSync(p) && isRealLO(p)) return p;
  }

  if (process.platform === 'win32') {
    try {
      const out = require('child_process').execSync('where soffice.exe', {
        encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'],
        windowsHide: true
      });
      const hits = out.split(/\r?\n/).map(x => x.trim()).filter(Boolean);
      for (const h of hits) {
        if (fs.existsSync(h) && isRealLO(h)) return h;
      }
    } catch (_) { /* not in PATH */ }
  }

  const candidates = [
    'C:/Program Files/LibreOffice/program/soffice.exe',
    'C:/Program Files (x86)/LibreOffice/program/soffice.exe',
    '/usr/bin/soffice',
    '/Applications/LibreOffice.app/Contents/MacOS/soffice'
  ];
  for (const c of candidates) {
    if (fs.existsSync(c) && isRealLO(c)) return c;
  }
  return null;
}

// 检测 LibreOffice 是否可用
ipcMain.handle('libreoffice:check', async () => {
  const exe = findLibreOffice();
  return { found: !!exe, path: exe || null };
});

// 用户手动指定 LibreOffice 路径
ipcMain.handle('libreoffice:setPath', async (event, exePath) => {
  if (typeof exePath !== 'string' || !fs.existsSync(exePath)) {
    return { success: false, error: '路径不存在或无效' };
  }
  try {
    const settingsPath = path.join(app.getPath('userData'), 'lo-path.txt');
    fs.writeFileSync(settingsPath, exePath, 'utf8');
    return { success: true, path: exePath };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// LibreOffice 转换
ipcMain.handle('libreoffice:convert', async (event, { inputPath, outputDir, format = 'PNG', scale = 1 }) => {
  const loExe = findLibreOffice();
  if (!loExe) {
    throw new Error('未找到 LibreOffice；请先到 https://www.libreoffice.org/download 下载安装，或在设置里手动指定 soffice.exe 路径');
  }

  const fmtMap = { PNG: 'png', JPG: 'jpg', JPEG: 'jpg', PDF: 'pdf', SVG: 'svg' };
  // Plan B: LO only produces PDF. Image formats (PNG/JPG) are
  // rendered from the PDF in the renderer using pdfjs-dist. The LO PNG
  // filter was unstable on this user's install (crashed silently with
  // exit 1 / no stderr even though PDF export worked perfectly).
  const loFormat = 'pdf';
  const convertSpec = loFormat;

  // Normalize both paths to forward-slash absolute form. LO on Windows
  // misparses --outdir / input args when they contain backslashes mixed
  // with spaces or non-ASCII characters (a frequent cause of the
  // "impl_store ... 0x81a" half of the bootstrap error).
  let finalOut = String(outputDir).replace(/\\/g, '/');
  let finalIn = String(inputPath).replace(/\\/g, '/');
  if (!path.isAbsolute(finalOut)) finalOut = path.resolve(finalOut).replace(/\\/g, '/');
  if (!path.isAbsolute(finalIn)) finalIn = path.resolve(finalIn).replace(/\\/g, '/');
  try { fs.mkdirSync(finalOut, { recursive: true }); } catch (_) {}
  // Unique profile dir per invocation. Reusing one across runs is
  // Stable per-user profile dir. The earlier unique-per-run profile was
  // the trigger for the 0-byte PDFs on this user's install: combined
  // with --nofirststartwizard (now removed), it left the profile
  // uninitialized, LO bailed silently, wrote 0 bytes. A stable dir
  // lets first-use init run on the first call and the profile is
  // reusable across runs.
  const userProfile = path.join(os.tmpdir(), 'fulltool-lo-profile');
  try { fs.rmSync(userProfile, { recursive: true, force: true }); } catch (_) {}
  try { fs.mkdirSync(userProfile, { recursive: true }); } catch (_) {}
  const profileArg = '-env:UserInstallation=file:///' + userProfile.replace(/\\/g, '/');

  const args = [profileArg,
    '--headless',
    '--nologo',
    '--norestore',
    '--convert-to', convertSpec,
    '--outdir', finalOut,
    finalIn
  ];

  console.log('[LibreOffice]', loExe, '[' + profileArg + ']', args.join(' '));

  const loDir = path.dirname(loExe);

  // Sanity-fill the env vars cmd/soffice tend to look up on Windows.
  // When our parent process is something stripped-down (e.g. VS Code
  // debug, nvm-windows, etc.) the child sees an empty USERPROFILE / TMP
  // and the bootstrap or profile write goes sideways.
  const sysRoot = process.env.SystemRoot || process.env.windir || 'C:\\Windows';
  const sys32 = path.join(sysRoot, 'System32');
  const comSpec = process.env.ComSpec || path.join(sys32, 'cmd.exe');
  // Build a fallback PATH that doesn't depend on process.env.PATH being
  // sane: LO program dir first, then the standard Windows system dirs.
  // The parent process PATH is still appended for things like a custom
  // git / python install that soffice might want to find.
  const systemPathParts = [
    sys32,
    sysRoot,
    path.join(sys32, 'Wbem'),
    path.join(sys32, 'WindowsPowerShell', 'v1.0')
  ].filter(Boolean);
  const fallbackPath = [loDir].concat(systemPathParts).concat([process.env.PATH || ''])
    .filter(Boolean)
    .join(path.delimiter);
  const env = Object.assign({}, process.env, {
    HOME: os.homedir(),
    USERPROFILE: os.homedir(),
    APPDATA: process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'),
    LOCALAPPDATA: process.env.LOCALAPPDATA || path.join(os.homedir(), 'AppData', 'Local'),
    TMP: os.tmpdir(),
    TEMP: os.tmpdir(),
    SystemRoot: sysRoot,
    windir: sysRoot,
    ComSpec: comSpec,
    PATH: fallbackPath
  });

  return await new Promise((resolve, reject) => {
    // The cwd-only fix doesn't bootstrap reliably on every Windows LO
    // install (the install prefix lookup in cppuhelper/paths.cxx still bails
    // out when the bootstrap.ini / registry / exe-path lookups miss). The
    // robust Windows recipe is: explicitly prepend the program dir to PATH
    // AND cd into it inside the same command line that runs soffice. Doing
    // it via cmd.exe /c keeps the spawn args handling we already have and
    // also gives LO a proper console-attached env.
    // Always wrap every token in double quotes. cmd.exe handles
    // superfluous outer quotes fine, and skipping the check is what
    // caused `set PATH=C:\\Program Files\\...` to be misparsed as
    // `set PATH=C:\\Program` (everything past the first space was
    // dropped) — which is why we were getting exit code 1.
    // Drop the cmd.exe wrapper entirely. spawn passes args to
    // soffice directly (no shell, no cmd tokenizing, no chained
    // command parsing) so the args array cannot get mangled by the
    // cmd line. cwd handles the program-dir-chdir requirement, env
    // handles the bootstrap, and we never need a set PATH or any
    // quoting gymnastics.
    const proc = spawn(loExe, args, {
      shell: false,
      windowsHide: true,
      cwd: loDir,
      env: env
    });
    let stdout = '', stderr = '';
    proc.stdout.on('data', d => stdout += d.toString('utf8'));
    proc.stderr.on('data', d => stderr += d.toString('utf8'));
    proc.on('error', err => reject(new Error('启动 LibreOffice 失败: ' + err.message)));
    proc.on('close', (code) => {
      if (code === 0) {
        const base = path.basename(inputPath, path.extname(inputPath));
        const outFile = path.join(outputDir, base + '.' + loFormat);
        // Sanity check with retry. On Windows the file can be 0 bytes
        // for a few ms after LO exits if the write was buffered; we
        // also see it when the profile is locked. Wait briefly then
        // re-check; if still empty, that's a real failure.
        const checkAfterDelay = (attempt) => new Promise((resolveChk) => {
          setTimeout(() => {
            try {
              if (fs.existsSync(outFile)) {
                const sz = fs.statSync(outFile).size;
                if (sz > 0) return resolveChk(sz);
              }
            } catch (_) {}
            if (attempt < 4) return resolveChk(checkAfterDelay(attempt + 1));
            resolveChk(0);
          }, 200);
        });
        checkAfterDelay(0).then((okSize) => {
          if (okSize === 0) {
          const size = okSize; // 0 means file still 0 bytes after retries
          reject(new Error(
            'LibreOffice 退出码 0 但输出文件不存在或为 0 字节 (' + size + ' bytes, ' +
            'expected path: ' + outFile + ')。常见原因：输出目录无写权限 / 杀软拦截写入 / ' +
            '输入文件 LO 不识别 / 上一次 LO 异常退出导致 user profile 锁未释放 ' +
            '(删除 C:/Users/25147/AppData/Local/Temp/fulltool-lo-profile 后重试)。' +
            ' | cmd: ' + loExe + ' ' + args.map(String).map(s => /[\s"&|<>^()]/.test(s) ? '"' + s + '"' : s).join(' ')
          ));
            return;
          }
          let pdfBytes = null;
        try { pdfBytes = fs.readFileSync(outFile); } catch (_) {}
        resolve({ success: true, outputPath: outFile, fileSize: okSize, pdfBytes: pdfBytes ? Array.from(pdfBytes) : null, format: 'pdf', requestedFormat: String(format || 'PDF').toUpperCase(), scale: Number(scale) || 1 });
        });
      } else {
        const tail = (stderr || stdout || '').trim();
        const hint = tail
          ? tail
          : ('退出码 ' + code +
             '（0xC0000409 常见于 DLL 版本冲突、杀毒拦截、或 VC++ 运行库缺失；' +
             '试一下关闭杀毒、用 LO 安装包里的 Repair 修一下）');
        reject(new Error('LibreOffice ' + hint + ' | cmd: ' + loExe + ' ' + args.map(String).map(s => /[\s"&|<>^()]/.test(s) ? '"' + s + '"' : s).join(' ')));
      }
    });
  });
});

// 读取文件字节（供 renderer 解析 .docx 等使用）
ipcMain.handle('fs:readFile', async (event, filePath) => {
  try {
    validatePath(filePath, 'readFile');
    const buf = fs.readFileSync(filePath);
    return { success: true, data: buf.buffer.slice(buf.byteOffset, buf.byteOffset + buf.byteLength) };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

ipcMain.handle('fs:readDir', async (event, dirPath, options) => {
  try {
    validatePath(dirPath, 'readDir');
    const recursive = !!(options && options.recursive);
    if (!recursive) {
      const files = fs.readdirSync(dirPath);
      return { success: true, files };
    }
    // Recursive walk; returns names of files matching the optional extension filter.
    const out = [];
    const exts = (options && options.extensions || []).map(s => String(s).toLowerCase());
    const skip = new Set(['node_modules', '.git', '$RECYCLE.BIN', 'System Volume Information']);
    function walk(dir, depth) {
      if (depth > 8) return;
      let entries;
      try { entries = fs.readdirSync(dir, { withFileTypes: true }); }
      catch (_) { return; }
      for (const ent of entries) {
        if (skip.has(ent.name)) continue;
        const full = path.join(dir, ent.name);
        if (ent.isDirectory()) { walk(full, depth + 1); continue; }
        if (!ent.isFile()) continue;
        if (exts.length) {
          const dot = ent.name.lastIndexOf('.');
          const ext = dot >= 0 ? ent.name.slice(dot + 1).toLowerCase() : '';
          if (!exts.includes(ext)) continue;
        }
        out.push(ent.name);
      }
    }
    walk(dirPath, 0);
    return { success: true, files: out };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// 获取文件信息
ipcMain.handle('fs:getFileInfo', async (event, filePath) => {
  try {
    validatePath(filePath, 'getFileInfo');
    const stats = fs.statSync(filePath);
    return { success: true, size: stats.size, mtime: stats.mtime };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// 写入文件
ipcMain.handle('fs:writeFile', async (event, filePath, data) => {
  try {
    validatePath(filePath, 'writeFile');
    const buffer = Buffer.from(data);
    fs.writeFileSync(filePath, buffer);
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
});
  // ---- Feishu / Lark open platform ----
  // Renderer cannot fetch open.feishu.cn directly because CORS blocks the
  // preflight even in Electron with webSecurity on. We proxy these calls
  // through the main process which has no CORS restriction.
  const FEISHU_BASE = 'https://open.feishu.cn/open-apis';
  const feishuCache = { appId: '', token: '', expire: 0 };

  ipcMain.handle('feishu:getToken', async (event, { appId, appSecret } = {}) => {
    try {
      if (!appId || !appSecret) return { success: false, error: '缺少 AppID 或 AppSecret' };
      if (feishuCache.appId === appId && feishuCache.token && Date.now() < feishuCache.expire - 60_000) {
        return { success: true, token: feishuCache.token, cached: true, expire: feishuCache.expire };
      }
      const r = await fetch(`${FEISHU_BASE}/auth/v3/tenant_access_token/internal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify({ app_id: appId, app_secret: appSecret })
      });
      const data = await r.json();
      if (data.code !== 0) return { success: false, error: data.msg || `code=${data.code}`, raw: data };
      feishuCache.appId = appId;
      feishuCache.token = data.tenant_access_token;
      feishuCache.expire = Date.now() + (Number(data.expire) || 7200) * 1000;
      return { success: true, token: data.tenant_access_token, expire: feishuCache.expire };
    } catch (err) {
      return { success: false, error: err.message };
    }
  });

  async function getFeishuToken(appId, appSecret) {
    if (feishuCache.appId === appId && feishuCache.token && Date.now() < feishuCache.expire - 60_000) {
      return feishuCache.token;
    }
    const r = await fetch(`${FEISHU_BASE}/auth/v3/tenant_access_token/internal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
      body: JSON.stringify({ app_id: appId, app_secret: appSecret })
    });
    const data = await r.json();
    if (data.code !== 0) throw new Error(data.msg || `feishu auth code=${data.code}`);
    feishuCache.appId = appId;
    feishuCache.token = data.tenant_access_token;
    feishuCache.expire = Date.now() + (Number(data.expire) || 7200) * 1000;
    return feishuCache.token;
  }

  ipcMain.handle('feishu:listRecords', async (event, { appId, appSecret, appToken, tableId, pageSize = 500 } = {}) => {
    try {
      const token = await getFeishuToken(appId, appSecret);
      const r = await fetch(`${FEISHU_BASE}/bitable/v1/apps/${appToken}/tables/${tableId}/records?page_size=${pageSize}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await r.json();
      if (data.code !== 0) return { success: false, error: data.msg || `code=${data.code}`, raw: data };
      return { success: true, items: data.data.items || [], total: data.data.total || 0 };
    } catch (err) {
      return { success: false, error: err.message };
    }
  });

  // Upload one file to bitable_image drive. Returns file_token.
  ipcMain.handle('feishu:uploadAttachment', async (event, { appId, appSecret, appToken, filePath, fileName } = {}) => {
    try {
      validatePath(filePath, 'feishu:uploadAttachment');
      const token = await getFeishuToken(appId, appSecret);
      const buf = fs.readFileSync(filePath);
      const safeName = String(fileName || path.basename(filePath)).replace(/"/g, '');
      const boundary = '----FullToolBoundary' + Math.random().toString(36).slice(2);
      const enc = (s) => Buffer.from(s, 'utf8');
      const head = (name, extra = '') => enc(`--${boundary}\r\nContent-Disposition: form-data; name="${name}"${extra}\r\n\r\n`);
      const parts = [
        head('file_name') + enc(safeName) + enc('\r\n'),
        head('parent_type') + enc('bitable_image') + enc('\r\n'),
        head('parent_node') + enc(appToken) + enc('\r\n'),
        enc(`--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="${safeName}"\r\nContent-Type: application/octet-stream\r\n\r\n`),
        buf,
        enc(`\r\n--${boundary}--\r\n`)
      ];
      const body = Buffer.concat(parts);
      const r = await fetch(`${FEISHU_BASE}/drive/v1/medias/upload_all`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': `multipart/form-data; boundary=${boundary}`
        },
        body
      });
      const data = await r.json();
      if (data.code !== 0) return { success: false, error: data.msg || `code=${data.code}`, raw: data };
      return { success: true, fileToken: data.data.file_token };
    } catch (err) {
      return { success: false, error: err.message };
    }
  });

  // Update one record's attachment field with one or more file_tokens.
  ipcMain.handle('feishu:updateRecord', async (event, { appId, appSecret, appToken, tableId, recordId, field, fileTokens } = {}) => {
    try {
      const token = await getFeishuToken(appId, appSecret);
      const r = await fetch(`${FEISHU_BASE}/bitable/v1/apps/${appToken}/tables/${tableId}/records/${recordId}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json; charset=utf-8' },
        body: JSON.stringify({ fields: { [field]: fileTokens.map(t => ({ file_token: t })) } })
      });
      const data = await r.json();
      if (data.code !== 0) return { success: false, error: data.msg || `code=${data.code}`, raw: data };
      return { success: true, record: data.data && data.data.record };
    } catch (err) {
      return { success: false, error: err.message };
    }
  });

// 删除文件（用于清理临时 PDF 中间产物）
ipcMain.handle('fs:unlink', async (event, filePath) => {
  try {
    if (typeof filePath !== 'string' || !filePath) return { success: false, error: 'invalid path' };
    validatePath(filePath, 'unlink');
    fs.unlinkSync(filePath);
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

// 重命名文件
ipcMain.handle('fs:renameFile', async (event, oldPath, newName) => {
  try {
    validatePath(oldPath, 'renameFile');
    if (/\.\./.test(newName) || /[\\\/]/.test(newName)) throw new Error('Invalid newName');
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
    validatePath(savePath, 'download:file');
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

ipcMain.handle('shell:openExternal', async (event, url) => {
  const { shell } = require('electron');
  await shell.openExternal(url);
  return { success: true };
});