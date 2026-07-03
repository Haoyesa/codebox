<template>
  <section class="page">
    <p class="desc">
      选择文件后将自动扫描并导出 PNG，支持放大与裁剪。
      <span v-if="!loFound" class="tag tag-amber" style="margin-left: 8px;">
        <i data-lucide="alert-triangle" style="width:12px;height:12px"></i>
        未检测到 LibreOffice
      </span>
    </p>

    <div class="exp-grid">
      <!-- 文件选择卡片 -->
      <div class="card">
        <div class="card-section" :class="{ dragging: isDragging }" @dragover.prevent="onDragOver" @dragleave="onDragLeave" @drop.prevent="onDrop">
          <div class="label">文件选择</div>
          <div class="pick-buttons">
            <button class="btn" @click="pickFiles">
              <i data-lucide="file-plus"></i>
              选择文件
            </button>
            <button class="btn" @click="pickFolder">
              <i data-lucide="folder-open"></i>
              选择文件夹
            </button>
          </div>
          <div class="full-pick">
            <button class="btn" @click="pickOutputDir">
              <i data-lucide="folder-output"></i>
              {{ state.outputDir || '选择输出目录' }}
            </button>
          </div>
        </div>

        <div class="meta-row">
          <span class="meta">
            <i data-lucide="file" style="width:12px;height:12px"></i>
            文件：<b>{{ state.files.length }}</b>
          </span>
          <span class="meta">
            <i data-lucide="folder" style="width:12px;height:12px"></i>
            文件夹：<b>{{ state.folders.length }}</b>
          </span>
          <span v-if="state.outputDir" class="meta meta-dir" :title="state.outputDir">
            <i data-lucide="folder-output" style="width:12px;height:12px"></i>
            {{ truncatePath(state.outputDir) }}
          </span>
        </div>

        <!-- 最近文件 -->
        <div v-if="recentFiles.length > 0" class="recent-files">
          <div class="recent-files-label muted mono">最近文件</div>
          <div class="recent-files-list">
            <button
              v-for="(path, i) in recentFiles"
              :key="i"
              class="recent-file-item"
              :title="path"
              @click="addFileFromRecent(path)"
            >
              <i data-lucide="clock" style="width:12px;height:12px"></i>
              <span class="mono">{{ truncatePath(path) }}</span>
            </button>
          </div>
        </div>

        <!-- 文件列表 -->
        <div v-if="state.files.length > 0" class="file-list">
          <div class="file-list-header">
            <span>已选文件 ({{ state.files.length }})</span>
            <button class="btn btn-ghost btn-sm" @click="clearFiles">清空</button>
          </div>
          <div class="file-list-items">
            <div v-for="(f, i) in state.files.slice(0, 5)" :key="i" class="file-item">
              <i data-lucide="file-text" style="width:14px;height:14px;color:var(--text-3)"></i>
              <span class="file-name">{{ f.name }}</span>
              <span class="file-size">{{ formatSize(f.size) }}</span>
            </div>
            <div v-if="state.files.length > 5" class="file-more">
              还有 {{ state.files.length - 5 }} 个文件...
            </div>
          </div>
        </div>
        <div v-else class="empty-state" style="min-height: 140px;">
          <i data-lucide="file-plus"></i>
          <p>选择或拖拽 PDF/DOCX/PPT/XLS 文件开始导出</p>
          <p style="font-size:12px;margin-top:4px;color:var(--text-3);">支持单个文件、批量选择或整个文件夹</p>
        </div>

        <div class="action-row">
          <span class="export-status" :class="statusClass">
            <template v-if="state.isExporting">
              <span class="spinner"></span>
              {{ state.statusText }}
            </template>
            <template v-else>
              {{ state.statusText }}
            </template>
          </span>
          <button v-if="state.isExporting" class="btn btn-warn btn-sm" @click="cancelExport">
            取消
          </button>
        </div>
      </div>

      <!-- 导出设置卡片 -->
      <div class="card">
        <div class="card-section">
          <div class="setting-row">
            <span class="setting-label">清晰度倍率</span>
            <select v-model="settings.scale">
              <option value="1">1x（默认）</option>
              <option value="1.5">1.5x</option>
              <option value="2">2x</option>
              <option value="3">3x</option>
              <option value="4">4x</option>
            </select>
          </div>

          <div class="setting-2col">
            <div>
              <div class="label">导出前几页</div>
              <input
                type="text"
                v-model="settings.pages"
                placeholder="留空=全部"
              />
            </div>
            <div class="checkbox-group">
              <label class="checkbox">
                <input type="checkbox" v-model="settings.subdir" />
                <span class="box"></span>
                输出到子文件夹
              </label>
            </div>
          </div>

          <div class="divider"></div>

          <div class="setting-row">
            <span class="setting-label">输出格式</span>
            <div class="format-chips">
              <button
                v-for="fmt in formats"
                :key="fmt"
                :class="['format-chip', { active: settings.format === fmt }]"
                @click="settings.format = fmt"
              >
                {{ fmt }}
              </button>
            </div>
          </div>
        </div>

        <div class="export-block">
          <button
            class="big"
            :disabled="!canStart || state.isExporting"
            @click="startExport"
          >
            <template v-if="state.isExporting">
              导出中... {{ state.progress }}%
            </template>
            <template v-else>
              <i data-lucide="download" style="width:18px;height:18px"></i>
              开始导出
            </template>
          </button>
          <button
            class="secondary"
            :disabled="!canStart || state.isExporting"
            @click="exportFullPreview"
            title="把当前文件所有页面拼成一张长图，输出为 -preview.png"
          >
            <i data-lucide="layers" style="width:16px;height:16px"></i>
            输出整张预览图
          </button>
        </div>

        <div v-if="state.isExporting" class="progress-section">
          <div class="progress-bar">
            <div class="fill" :style="{ width: state.progress + '%' }"></div>
          </div>
          <div class="progress-info">
            <span>{{ state.currentFile }}</span>
            <span>{{ state.doneCount }}/{{ state.totalCount }}</span>
          </div>
        </div>

        <!-- 导出进度条（含日志） -->
        <div v-if="exportProgress.status !== 'idle'" class="export-progress">
          <div class="progress-header">
            <span>{{ exportProgress.status === 'running' ? '导出中' : exportProgress.status === 'done' ? '完成' : '出错' }}</span>
            <span class="mono">{{ exportProgress.current }}/{{ exportProgress.total }}</span>
            <button class="btn btn-ghost btn-xs" @click="closeProgress" title="关闭">X</button>
          </div>
          <div class="progress-bar-exp">
            <div class="progress-fill-exp" :style="{ width: (exportProgress.total ? exportProgress.current / exportProgress.total * 100 : 0) + '%' }"></div>
          </div>
          <div v-if="exportLog.length" class="export-log">
            <div v-for="(log, i) in exportLog" :key="i" class="export-log-item">
              <span class="mono">{{ log.time }}</span>
              <span :class="'log-' + log.level">{{ log.msg }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- LibreOffice 下载提示 -->
    <div v-if="!loFound" class="card tip-card" style="margin-top: 16px;">
      <div class="tip-icon">!</div>
      <div class="tip-content">
        <b>未检测到 LibreOffice</b><br>
        <span>.docx 可通过内置引擎导出；其他格式（PDF/PPT/XLS 等）需要 LibreOffice。</span>
        <div class="tip-actions">
          <button class="btn btn-primary btn-sm" @click="downloadLO">
            <i data-lucide="download"></i>
            下载 LibreOffice
          </button>
          <button class="btn btn-ghost btn-sm" @click="pickLOPath">
            <i data-lucide="settings"></i>
            手动指定 soffice.exe
          </button>
        </div>
      </div>
    </div>
    <div v-else-if="state.loPath" class="meta meta-lo" :title="state.loPath">
      <i data-lucide="check-circle" style="width:12px;height:12px;color:var(--ok)"></i>
      LibreOffice：{{ truncatePath(state.loPath) }}
      <button class="btn btn-ghost btn-sm" style="margin-left: 6px;" @click="pickLOPath">更换</button>
    </div>

    <!-- JS 兑底渲染节点（.docx 脱机路径） -->
    <div id="lo-render-host" class="render-host" aria-hidden="true"></div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import * as mammoth from 'mammoth';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import { pdfToPngs } from '../utils/pdfToPngs.js';
import { formatSize, truncatePath, getExt, getMimeFromPath, safeOutputDir, getBasename } from '../utils/file.js';
import { useSettings } from '../composables/useSettings.js';
import { useToast } from '../composables/useToast.js';

const toast = useToast();

// Formats
const formats = ['PNG', 'JPG', 'PDF', 'SVG'];

// State
const state = reactive({
  files: [],
  folders: [],
  outputDir: '',
  isExporting: false,
  progress: 0,
  statusText: '选择文件或文件夹后自动扫描',
  currentFile: '',
  doneCount: 0,
  totalCount: 0,
  cancelRequested: false,
  failedFiles: [],
  skippedFiles: [],
  loFound: true,
  loPath: ''
});

const settings = reactive({
  scale: '1',
  pages: '',
  subdir: false,
  format: 'PNG'
});

const loFound = ref(true);
const isDragging = ref(false);
const recentFiles = ref([]);
let exportAbortController = null;

// Export progress & log
const exportProgress = ref({ current: 0, total: 0, status: 'idle' });
const exportLog = ref([]);
let hideTimer = null;

// Computed
const canStart = computed(() => {
  return (state.files.length > 0 || state.folders.length > 0) && state.outputDir;
});

const statusClass = computed(() => {
  if (state.isExporting) return 'status-exporting';
  if (!canStart.value) return 'status-idle';
  return 'status-ready';
});

// Methods

async function pickFiles() {
  if (!window.electronAPI) {
    // Fallback for browser dev
    const input = document.createElement('input');
    input.type = 'file';
    input.multiple = true;
    input.accept = '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx';
    input.onchange = (e) => {
      state.files = Array.from(e.target.files);
      state.statusText = `已选择 ${state.files.length} 个文件`;
      toast.show(`已选择 ${state.files.length} 个文件`);
    };
    input.click();
    return;
  }

  const result = await window.electronAPI.openFiles();
  if (!result.canceled && result.filePaths.length > 0) {
    // Convert paths to file info objects
    state.files = result.filePaths.map(p => ({
      path: p,
      name: getBasename(p),
      size: 0
    }));
    state.statusText = `已选择 ${state.files.length} 个文件`;
    toast.show(`已选择 ${state.files.length} 个文件`, 'success');
    addRecentFiles(result.filePaths);
    await nextTick();
    window.lucide?.createIcons();
  }
}

async function pickFolder() {
  if (!window.electronAPI) {
    toast.show('浏览器模式下无法选择文件夹，请使用 Electron 版本', 'error');
    return;
  }

  const result = await window.electronAPI.openDirectory();
  if (!result.canceled && result.filePaths.length > 0) {
    const folderPath = result.filePaths[0];
    // Read all supported files in this folder
    const dirResult = await window.electronAPI.readDir(folderPath);
    if (dirResult.success) {
      const supportedExt = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'];
      state.folders.push({
        path: folderPath,
        name: getBasename(folderPath),
        files: dirResult.files.filter(f => {
          return supportedExt.includes(getExt(f));
        })
      });
      state.statusText = `已选择文件夹：${getBasename(folderPath)}`;
      toast.show('文件夹已添加', 'success');
      await nextTick();
      window.lucide?.createIcons();
    }
  }
}

async function pickOutputDir() {
  if (!window.electronAPI) {
    toast.show('浏览器模式下无法选择目录，请使用 Electron 版本', 'error');
    return;
  }

  try {
    const result = await window.electronAPI.selectOutputDir();
    if (result.canceled) return;
    if (result.filePaths && result.filePaths.length > 0) {
      state.outputDir = result.filePaths[0];
      state.statusText = '输出目录已设置';
      toast.show('输出目录已设置', 'success');
    }
  } catch (err) {
    console.error('[pickOutputDir]', err);
    toast.show('选择目录失败：' + (err.message || '未知错误'), 'error');
  }
}

function clearFiles() {
  state.files = [];
  state.statusText = '选择文件或文件夹后自动扫描';
}

// Recent files
function loadRecentFiles() {
  try {
    const raw = localStorage.getItem('fulltool_recent_files');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        recentFiles.value = parsed;
      }
    }
  } catch (_) {
    recentFiles.value = [];
  }
}

function saveRecentFiles() {
  try {
    localStorage.setItem('fulltool_recent_files', JSON.stringify(recentFiles.value));
  } catch (_) {}
}

function addRecentFiles(paths) {
  if (!paths || paths.length === 0) return;
  const filtered = paths.filter(p => typeof p === 'string' && p.length > 0);
  const current = recentFiles.value.filter(p => !filtered.includes(p));
  recentFiles.value = [...filtered, ...current].slice(0, 10);
  saveRecentFiles();
}

async function addFileFromRecent(filePath) {
  if (!filePath) return;
  if (state.files.some(f => f.path === filePath)) {
    toast.show('该文件已在列表中', 'warn');
    return;
  }

  if (window.electronAPI) {
    try {
      const info = await window.electronAPI.getFileInfo(filePath);
      if (info && info.exists) {
        state.files.push({
          path: filePath,
          name: getBasename(filePath),
          size: info.size || 0
        });
        state.statusText = `已选择 ${state.files.length} 个文件`;
        toast.show('已添加：' + getBasename(filePath), 'success');
        addRecentFiles([filePath]);
        await nextTick();
        window.lucide?.createIcons();
      } else {
        toast.show('文件不存在：' + truncatePath(filePath), 'error');
        // Remove from recent if file no longer exists
        recentFiles.value = recentFiles.value.filter(p => p !== filePath);
        saveRecentFiles();
      }
    } catch (err) {
      toast.show('添加失败：' + (err.message || '未知错误'), 'error');
    }
  } else {
    // Browser fallback cannot access local file path
    toast.show('浏览器模式下无法添加本地文件', 'error');
  }
}

// Drag & drop
function onDragOver(e) {
  e.preventDefault();
  isDragging.value = true;
}
function onDragLeave(e) {
  if (!e.currentTarget.contains(e.relatedTarget)) {
    isDragging.value = false;
  }
}
async function onDrop(e) {
  e.preventDefault();
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (!files || files.length === 0) return;

  const added = [];
  const addedPaths = [];
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (window.electronAPI && file.path) {
      added.push({ path: file.path, name: getBasename(file.path), size: file.size || 0 });
      addedPaths.push(file.path);
    } else {
      added.push(file);
    }
  }

  if (added.length > 0) {
    state.files = [...state.files, ...added];
    state.statusText = `已选择 ${state.files.length} 个文件`;
    toast.show(`已添加 ${added.length} 个文件`, 'success');
    if (addedPaths.length > 0) addRecentFiles(addedPaths);
    await nextTick();
    window.lucide?.createIcons();
  }
}

function cancelExport() {
  state.cancelRequested = true;
  if (exportAbortController) {
    exportAbortController.abort();
  }
  state.statusText = '正在取消...';
}

function addLog(level, msg) {
  const now = new Date();
  const time = String(now.getHours()).padStart(2, '0') + ':' +
               String(now.getMinutes()).padStart(2, '0') + ':' +
               String(now.getSeconds()).padStart(2, '0');
  exportLog.value = [{ time, level, msg }, ...exportLog.value].slice(0, 10);
}

function closeProgress() {
  if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }
  exportProgress.value = { current: 0, total: 0, status: 'idle' };
  exportLog.value = [];
}

// .docx 走纯 JS 兜底（mammoth → html2canvas → png/jpg/pdf）
async function convertDocxViaJS(filePath, format, scale) {
  const r = await window.electronAPI.readFile(filePath);
  if (!r.success) throw new Error('读取文件失败：' + r.error);
  const result = await mammoth.convertToHtml({ arrayBuffer: r.data });
  const html = result.value || '';
  if (!html.trim()) throw new Error('docx 内容为空');

  const baseName = getBasename(filePath).replace(/\.docx?$/i, '');
  const fmt = String(format || 'PNG').toUpperCase();
  const ext = fmt === 'JPG' ? 'jpg' : fmt === 'PDF' ? 'pdf' : 'png';

  const host = document.getElementById('lo-render-host');
  if (!host) throw new Error('找不到渲染节点 lo-render-host');
  host.innerHTML = '<div class="lo-doc">' + html + '</div>';
  await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
  const target = host.firstElementChild;
  if (!target) throw new Error('渲染目标为空');

  const canvas = await html2canvas(target, {
    scale: scale || 1,
    backgroundColor: '#ffffff',
    useCORS: true,
    logging: false
  });

  const safeDir = safeOutputDir(state.outputDir);
  const outPath = safeDir + '/' + baseName + '.' + ext;

  if (fmt === 'PDF') {
    const orient = canvas.width >= canvas.height ? 'l' : 'p';
    const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: orient });
    const pageW = pdf.internal.pageSize.getWidth();
    const pageH = pdf.internal.pageSize.getHeight();
    const ratio = canvas.height / canvas.width;
    const imgW = pageW;
    const imgH = imgW * ratio;
    const dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    if (imgH <= pageH) {
      pdf.addImage(dataUrl, 'JPEG', 0, 0, imgW, imgH);
    } else {
      let remaining = imgH;
      let yPos = 0;
      pdf.addImage(dataUrl, 'JPEG', 0, 0, imgW, imgH);
      remaining -= pageH;
      yPos += pageH;
      while (remaining > 0) {
        pdf.addPage();
        pdf.addImage(dataUrl, 'JPEG', 0, -yPos, imgW, imgH);
        remaining -= pageH;
        yPos += pageH;
      }
    }
    const ab = pdf.output('arraybuffer');
    await window.electronAPI.writeFile(outPath, ab);
  } else {
    const mime = ext === 'jpg' ? 'image/jpeg' : 'image/png';
    const blob = await new Promise(res => canvas.toBlob(res, mime, 0.92));
    if (!blob) throw new Error('canvas 转 blob 失败');
    const ab = await blob.arrayBuffer();
    await window.electronAPI.writeFile(outPath, ab);
  }
  host.innerHTML = '';
}

async function startExport() {
  if (!canStart.value || state.isExporting) return;

  state.isExporting = true;
  state.progress = 0;
  state.cancelRequested = false;
  state.doneCount = 0;
  state.failedFiles = [];
  state.skippedFiles = [];

  // 汇总所有待处理文件
  const allFiles = [];
  for (const f of state.files) {
    allFiles.push({ path: f.path, name: f.name, ext: getExt(f.name) });
  }
  for (const folder of state.folders) {
    for (const fileName of folder.files) {
      allFiles.push({
        path: folder.path + '/' + fileName,
        name: fileName,
        ext: getExt(fileName)
      });
    }
  }
  const totalFiles = allFiles.length;
  state.totalCount = totalFiles;

  // 初始化进度条
  exportProgress.value = { current: 0, total: totalFiles, status: 'running' };
  exportLog.value = [];
  if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }

  if (totalFiles === 0) {
    toast.show('没有可导出的文件', 'error');
    state.isExporting = false;
    return;
  }

  state.statusText = '正在准备导出...';

  if (!window.electronAPI) {
    simulateExport();
    return;
  }

  const fmt = settings.format;
  const scale = parseFloat(settings.scale) || 1;

  // 实时再检测一次 LO 状态
  await checkLibreOffice();
  const loAvailable = state.loFound;

  const hasNonDocx = allFiles.some(f => f.ext !== 'docx');
  if (!loAvailable && hasNonDocx) {
    toast.show('未检测到 LibreOffice，PDF/PPT/XLS 等格式将跳过；.docx 仍可导出', 'warn');
  }

  let successCount = 0;
  for (let i = 0; i < allFiles.length; i++) {
    if (state.cancelRequested) break;
    const file = allFiles[i];
    state.currentFile = file.name;
    state.statusText = '正在导出：' + file.name;

    try {
      if (file.ext === 'docx') {
        await convertDocxViaJS(file.path, fmt, scale);
      } else {
        if (!loAvailable) {
          state.skippedFiles.push(file.name);
          toast.show(file.name + ' 需 LibreOffice（点 Tab1 底部提示卡下载安装）', 'warn');
        } else {
          const loRes = await window.electronAPI.libreOfficeConvert({
            inputPath: file.path,
            outputDir: state.outputDir,
            format: fmt,
            scale: scale
          });
          // LO only emits PDF. If the user picked an image format, do the
          // PDF->PNG conversion in the renderer using pdfjs-dist.
          const reqFmt = (loRes && loRes.requestedFormat) || 'PDF';
          if (reqFmt !== 'PDF' && loRes && loRes.outputPath) {
            const base = file.name.replace(/\.[^.]+$/, '');
            // Pass inline bytes from main when available so we do not
            // need to re-read the file (and so we cannot hit a Windows
            // file-cache mismatch). Fall back to disk read otherwise.
            const pngs = await pdfToPngs({ pdfPath: loRes.outputPath, pdfBytes: loRes.pdfBytes, scale });
            for (let p = 0; p < pngs.length; p++) {
              const page = pngs[p];
              const ab = await page.blob.arrayBuffer();
              const target = state.outputDir + '/' + base + '-page-' + String(p + 1).padStart(2, '0') + '.png';
              await window.electronAPI.writeFile(target, new Uint8Array(ab));
            }
            // Tidy up: remove the temp PDF so the output dir only has the
            // images the user actually asked for.
            try { await window.electronAPI.unlink(loRes.outputPath); } catch (_) {}
          }
        }
      }
      if (state.skippedFiles.indexOf(file.name) < 0 || file.ext === 'docx') {
        successCount++;
        addLog('info', '已导出：' + file.name);
      }
    } catch (err) {
      console.error('Convert failed for', file.name, err);
      state.failedFiles.push({ name: file.name, reason: (err && err.message) || String(err) });
      addLog('error', '失败：' + file.name + ' - ' + ((err && err.message) || String(err)));
      toast.show('转换失败：' + file.name, 'error');
    }
    state.doneCount = successCount + state.failedFiles.length + state.skippedFiles.length;
    state.progress = Math.round((state.doneCount / totalFiles) * 100);
    exportProgress.value.current = state.doneCount;
  }

  // 设置最终状态
  if (state.cancelRequested) {
    exportProgress.value.status = 'done';
    addLog('warn', '导出已取消');
  } else if (state.failedFiles.length > 0) {
    exportProgress.value.status = 'error';
    addLog('error', state.failedFiles.length + ' 个文件导出失败');
  } else {
    exportProgress.value.status = 'done';
    addLog('info', '全部导出完成');
  }
  // 3 秒后自动隐藏
  hideTimer = setTimeout(() => { closeProgress(); }, 3000);

  // 收尾汇总
  const failed = state.failedFiles.length;
  const skipped = state.skippedFiles.length;
  // 按扩展名分组跳过文件
  const skipByExt = {};
  for (const name of state.skippedFiles) {
    const ext = getExt(name);
    skipByExt[ext] = (skipByExt[ext] || 0) + 1;
  }
  const skipExtSummary = Object.keys(skipByExt).length
    ? '（' + Object.entries(skipByExt).map(([e, n]) => e + ' ×' + n).join('，') + '）'
    : '';
  const skipHint = skipped > 0 ? ' — 需 LibreOffice，可点 Tab1 底部下载或手动指定 soffice.exe' : '';

  if (state.cancelRequested) {
    state.statusText = '已取消（成功 ' + successCount + '，失败 ' + failed + '，跳过 ' + skipped + skipExtSummary + '）';
    toast.show('导出已取消', 'warn');
  } else {
    let msg = '导出完成：成功 ' + successCount;
    if (failed > 0) msg += '，失败 ' + failed;
    if (skipped > 0) msg += '，跳过 ' + skipped + skipExtSummary;
    state.statusText = msg + skipHint;
    toast.show(msg, failed > 0 ? 'warn' : (skipped > 0 ? 'warn' : 'success'));
  }
  state.isExporting = false;
  state.currentFile = '';
}

// 把多张页面图按原始比例纵向拼成一张长图，超高时按比例缩到 maxTotalHeight 以内
// 避免触发 canvas 尺寸上限。pages 形如 [{ width, height, blob }]
async function stitchPagesToSingleImage(pages, options = {}) {
  if (!pages || pages.length === 0) throw new Error('没有可拼接的页面');
  if (pages.length === 1) return pages[0].blob;

  const maxTotalHeight = options.maxTotalHeight || 16000;
  const bitmaps = await Promise.all(pages.map(async (p) => {
    const bm = await createImageBitmap(p.blob);
    return { bm, w: bm.width, h: bm.height };
  }));

  const maxWidth = Math.max(...bitmaps.map(b => b.w));
  const ratios = bitmaps.map(b => maxWidth / b.w);
  const scaledHeights = bitmaps.map((b, i) => Math.round(b.h * ratios[i]));
  const rawHeight = scaledHeights.reduce((a, b) => a + b, 0);

  let outW = maxWidth;
  let outH = rawHeight;
  if (rawHeight > maxTotalHeight) {
    const k = maxTotalHeight / rawHeight;
    outW = Math.round(maxWidth * k);
    outH = maxTotalHeight;
  }

  const canvas = document.createElement('canvas');
  canvas.width = outW;
  canvas.height = outH;
  const ctx = canvas.getContext('2d');
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, outW, outH);

  let y = 0;
  for (let i = 0; i < bitmaps.length; i++) {
    const drawH = Math.round(bitmaps[i].h * (outW / bitmaps[i].w));
    ctx.drawImage(bitmaps[i].bm, 0, y, outW, drawH);
    y += drawH;
    bitmaps[i].bm.close?.();
  }

  return await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
}

// 整张预览图：把每个文件的所有页面拼成一张长图，输出为 -preview.png
async function exportFullPreview() {
  if (!canStart.value || state.isExporting) return;
  if (!window.electronAPI) {
    toast.show('该功能需要在 Electron 版本中使用', 'error');
    return;
  }

  state.isExporting = true;
  state.progress = 0;
  state.cancelRequested = false;
  state.doneCount = 0;
  state.failedFiles = [];
  state.skippedFiles = [];

  // 汇总所有待处理文件
  const allFiles = [];
  for (const f of state.files) {
    allFiles.push({ path: f.path, name: f.name, ext: getExt(f.name) });
  }
  for (const folder of state.folders) {
    for (const fileName of folder.files) {
      allFiles.push({
        path: folder.path + '/' + fileName,
        name: fileName,
        ext: getExt(fileName)
      });
    }
  }
  const totalFiles = allFiles.length;
  state.totalCount = totalFiles;

  // 初始化进度条
  exportProgress.value = { current: 0, total: totalFiles, status: 'running' };
  exportLog.value = [];
  if (hideTimer) { clearTimeout(hideTimer); hideTimer = null; }

  if (totalFiles === 0) {
    toast.show('没有可导出的文件', 'error');
    state.isExporting = false;
    return;
  }

  state.statusText = '正在准备预览图...';
  await checkLibreOffice();
  const loAvailable = state.loFound;
  const scale = parseFloat(settings.scale) || 1;

  const hasNonDocx = allFiles.some(f => f.ext !== 'docx');
  if (!loAvailable && hasNonDocx) {
    toast.show('未检测到 LibreOffice，PDF/PPT/XLS 等格式将跳过；.docx 仍可导出', 'warn');
  }

  let successCount = 0;
  for (let i = 0; i < allFiles.length; i++) {
    if (state.cancelRequested) break;
    const file = allFiles[i];
    state.currentFile = file.name;
    state.statusText = '正在拼接：' + file.name;

    try {
      const base = file.name.replace(/\.[^.]+$/, '');
      const outPath = state.outputDir + '/' + base + '-preview.png';
      const pages = []; // [{ width, height, blob }]

      if (file.ext === 'docx') {
        // JS 路径：mammoth -> html -> html2canvas，单张长图
        const r = await window.electronAPI.readFile(file.path);
        if (!r.success) throw new Error('读取文件失败：' + r.error);
        const result = await mammoth.convertToHtml({ arrayBuffer: r.data });
        const html = result.value || '';
        if (!html.trim()) throw new Error('docx 内容为空');

        const host = document.getElementById('lo-render-host');
        if (!host) throw new Error('找不到渲染节点 lo-render-host');
        host.innerHTML = '<div class="lo-doc">' + html + '</div>';
        await new Promise(res => requestAnimationFrame(() => requestAnimationFrame(res)));
        const target = host.firstElementChild;
        if (!target) throw new Error('渲染目标为空');
        const canvas = await html2canvas(target, {
          scale: scale,
          backgroundColor: '#ffffff',
          useCORS: true,
          logging: false
        });
        const blob = await new Promise(res => canvas.toBlob(res, 'image/png'));
        if (!blob) throw new Error('canvas 转 blob 失败');
        pages.push({ width: canvas.width, height: canvas.height, blob });
        host.innerHTML = '';
      } else if (file.ext === 'pdf') {
        // 已是 PDF：直接走 pdfjs，避免再过一遍 LO
        const data = await window.electronAPI.readFile(file.path);
        if (!data.success) throw new Error('读取文件失败：' + data.error);
        const pngs = await pdfToPngs({ pdfBytes: data.data, scale });
        for (const p of pngs) pages.push({ width: p.width, height: p.height, blob: p.blob });
      } else {
        // 其他格式：LO -> PDF -> pdfToPngs
        if (!loAvailable) {
          state.skippedFiles.push(file.name);
          toast.show(file.name + ' 需 LibreOffice（点 Tab1 底部提示卡下载安装）', 'warn');
          state.doneCount = successCount + state.failedFiles.length + state.skippedFiles.length;
          state.progress = Math.round((state.doneCount / totalFiles) * 100);
          exportProgress.value.current = state.doneCount;
          addLog('warn', '跳过：' + file.name + '（需 LibreOffice）');
          continue;
        }
        const loRes = await window.electronAPI.libreOfficeConvert({
          inputPath: file.path,
          outputDir: state.outputDir,
          format: 'PDF',
          scale: scale
        });
        if (!loRes || !loRes.outputPath) throw new Error('LibreOffice 转换失败');
        const pngs = await pdfToPngs({ pdfPath: loRes.outputPath, pdfBytes: loRes.pdfBytes, scale });
        for (const p of pngs) pages.push({ width: p.width, height: p.height, blob: p.blob });
        try { await window.electronAPI.unlink(loRes.outputPath); } catch (_) {}
      }

      if (pages.length === 0) throw new Error('未生成任何页面');

      const finalBlob = await stitchPagesToSingleImage(pages);
      if (!finalBlob) throw new Error('拼接失败');
      const ab = await finalBlob.arrayBuffer();
      await window.electronAPI.writeFile(outPath, new Uint8Array(ab));
      successCount++;
      addLog('info', '已生成预览：' + file.name);
    } catch (err) {
      console.error('Preview export failed for', file.name, err);
      state.failedFiles.push({ name: file.name, reason: (err && err.message) || String(err) });
      addLog('error', '预览失败：' + file.name + ' - ' + ((err && err.message) || String(err)));
      toast.show('预览生成失败：' + file.name, 'error');
    }
    state.doneCount = successCount + state.failedFiles.length + state.skippedFiles.length;
    state.progress = Math.round((state.doneCount / totalFiles) * 100);
    exportProgress.value.current = state.doneCount;
  }

  // 设置最终状态
  if (state.cancelRequested) {
    exportProgress.value.status = 'done';
    addLog('warn', '预览导出已取消');
  } else if (state.failedFiles.length > 0) {
    exportProgress.value.status = 'error';
    addLog('error', state.failedFiles.length + ' 个文件预览生成失败');
  } else {
    exportProgress.value.status = 'done';
    addLog('info', '全部预览图生成完成');
  }
  // 3 秒后自动隐藏
  hideTimer = setTimeout(() => { closeProgress(); }, 3000);

  // 收尾汇总
  const failed = state.failedFiles.length;
  const skipped = state.skippedFiles.length;
  if (state.cancelRequested) {
    state.statusText = '已取消（成功 ' + successCount + '，失败 ' + failed + '，跳过 ' + skipped + '）';
    toast.show('预览导出已取消', 'warn');
  } else {
    let msg = '预览图已生成：' + successCount + ' 张';
    if (failed > 0) msg += '，失败 ' + failed;
    if (skipped > 0) msg += '，跳过 ' + skipped;
    state.statusText = msg;
    toast.show(msg, failed > 0 || skipped > 0 ? 'warn' : 'success');
  }
  state.isExporting = false;
  state.currentFile = '';
}

function simulateExport() {
  // Browser fallback simulation
  let p = 0;
  const interval = setInterval(() => {
    if (state.cancelRequested) {
      clearInterval(interval);
      state.isExporting = false;
      state.statusText = `已取消（${state.doneCount}/${state.totalCount}）`;
      return;
    }

    p += Math.random() * 15;
    if (p >= 100) {
      p = 100;
      clearInterval(interval);
      state.progress = 100;
      state.statusText = `导出完成：${state.files.length} 个文件`;
      state.isExporting = false;
      toast.show('导出完成！', 'success');
    } else {
      state.progress = Math.round(p);
      state.statusText = `正在导出... ${Math.round(p)}%`;
    }
  }, 200);
}

async function downloadLO() {
  toast.show('正在打开下载页面...', 'info');
  // Open LibreOffice download page
  window.open('https://www.libreoffice.org/download/download/', '_blank');
}

async function checkLibreOffice() {
  if (!window.electronAPI) { state.loFound = false; return; }
  try {
    const r = await window.electronAPI.libreOfficeCheck();
    state.loFound = !!r.found;
    state.loPath = r.path || '';
  } catch (_) {
    state.loFound = false;
  }
}

async function pickLOPath() {
  if (!window.electronAPI) {
    toast.show('请在 Electron 版本中设置', 'error');
    return;
  }
  const r = await window.electronAPI.openFiles({
    properties: ['openFile'],
    filters: [{ name: 'LibreOffice (soffice.exe)', extensions: ['exe'] }]
  });
  if (r.canceled || !r.filePaths || r.filePaths.length === 0) return;
  const exePath = r.filePaths[0];
  const res = await window.electronAPI.libreOfficeSetPath(exePath);
  if (res.success) {
    state.loFound = true;
    state.loPath = res.path;
    toast.show('已指定 LibreOffice 路径：' + res.path, 'success');
  } else {
    toast.show('设置失败：' + (res.error || '未知错误'), 'error');
  }
}

onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
  await checkLibreOffice();
  loadRecentFiles();
  // Load default output dir from settings
  const defaultOut = useSettings().get('outputDir');
  if (defaultOut && !state.outputDir) {
    state.outputDir = defaultOut;
  }
});
</script>

<style scoped>
/* Tab 1 specific styles */
.exp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.pick-buttons { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
.pick-buttons .btn { height: 38px; }
.full-pick { margin-bottom: 12px; }
.full-pick .btn {
  width: 100%; height: 38px;
  justify-content: flex-start;
  padding-left: 12px;
  color: var(--text-2);
}
.full-pick .btn:hover { color: var(--text); }

.meta-row {
  display: flex; gap: 8px; align-items: center; flex-wrap: wrap;
  margin-bottom: 12px; font-size: 12px; color: var(--text-2);
}
.meta-row .meta {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 4px 10px;
  background: linear-gradient(180deg, var(--panel-2) 0%, var(--panel-3) 100%);
  border: 1px solid var(--border-2);
  border-radius: 8px;
  font-family: var(--font-mono);
  transition: border-color .15s, box-shadow .15s;
}
.meta-row .meta:hover { border-color: var(--border-strong); box-shadow: var(--shadow-sm); }
.meta-row .meta b { color: var(--text); font-weight: 600; }
.meta-dir { max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.action-row {
  display: flex; justify-content: space-between; align-items: center;
  padding-top: 12px; border-top: 1px solid var(--border-2);
}
.action-left { display: flex; gap: 8px; }
.export-status {
  font-size: 12px; color: var(--text-2);
  display: flex; align-items: center; gap: 6px;
}
.status-exporting { color: var(--primary); font-weight: 500; }
.status-ready { color: var(--ok); }

.spinner {
  width: 12px; height: 12px;
  border: 2px solid var(--primary-soft);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* File list */
.file-list { margin-top: 12px; }
.file-list-header {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 12px; color: var(--text-2); margin-bottom: 8px;
  padding: 0 4px;
}
.file-list-items { max-height: 160px; overflow-y: auto; padding: 2px; }
.file-item {
  display: flex; align-items: center; gap: 8px;
  padding: 5px 8px; font-size: 12px;
  border-radius: 6px;
  transition: background .15s;
  cursor: default;
}
.file-item:hover { background: var(--panel-2); }
.file-item i[data-lucide] { flex-shrink: 0; }
.file-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text); }
.file-size {
  color: var(--text-3);
  font-family: var(--font-mono);
  font-size: 11px;
  flex-shrink: 0;
}
.file-more {
  font-size: 11px; color: var(--text-3);
  padding: 6px 8px;
  text-align: center;
  font-family: var(--font-mono);
}

/* Settings */
.setting-row {
  display: grid; grid-template-columns: auto 1fr;
  gap: 12px; align-items: center; margin-bottom: 12px;
}
.setting-label { font-size: 13px; color: var(--text-2); white-space: nowrap; }
.setting-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.checkbox-group { display: flex; align-items: end; padding-bottom: 8px; }

.format-chips { display: flex; gap: 6px; }
.format-chip {
  padding: 4px 12px; border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--panel); font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all .15s;
}
.format-chip:hover { border-color: var(--primary-2); }
.format-chip.active {
  background: var(--primary-soft); color: var(--primary);
  border-color: var(--primary-soft);
}

/* Export block */
.export-block { margin-top: 14px; }
.export-block .big {
  width: 100%; padding: 14px 18px;
  background: linear-gradient(180deg, var(--primary) 0%, var(--primary-2) 100%);
  color: #fff; border: 0; border-radius: 8px;
  font-size: 15px; font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 14px var(--primary-glow);
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: filter .15s, transform .1s;
}
.export-block .big:hover:not(:disabled) { filter: brightness(1.05); }
.export-block .big:active:not(:disabled) { transform: scale(0.98); }
.export-block .big:disabled { opacity: 0.6; cursor: not-allowed; }
.export-block .secondary {
  width: 100%;
  margin-top: 8px;
  padding: 10px 16px;
  background: var(--panel);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  transition: border-color .15s, color .15s, background .15s, transform .1s;
}
.export-block .secondary:hover:not(:disabled) {
  border-color: var(--primary-2);
  color: var(--primary);
  background: var(--primary-soft);
}
.export-block .secondary:active:not(:disabled) { transform: scale(0.99); }
.export-block .secondary:disabled { opacity: 0.5; cursor: not-allowed; }

/* Progress */
.progress-section { margin-top: 12px; }
.progress-info {
  display: flex; justify-content: space-between;
  font-size: 11px; color: var(--text-3); margin-top: 6px;
}

/* Tip card */
.tip-card { display: flex; gap: 12px; padding: 16px; }
.tip-icon {
  width: 24px; height: 24px; flex-shrink: 0;
  border-radius: 50%;
  background: var(--warn-soft); color: var(--warn);
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700;
}
.tip-content { font-size: 13px; line-height: 1.6; }

@keyframes spin { to { transform: rotate(360deg); } }

.card-section {
  transition: border-color 0.2s, background 0.2s;
  border: 2px solid transparent;
}
.card-section.dragging {
  border: 2px dashed var(--neon-cyan);
  background: var(--neon-cyan-soft);
}

/* JS .docx 脱机渲染节点（页面外脱机布局） */
.render-host {
  position: fixed;
  left: -10000px;
  top: 0;
  width: 794px;
  pointer-events: none;
  z-index: -1;
  background: var(--panel);
}
.render-host .lo-doc {
  padding: 48px;
  font-size: 14px;
  line-height: 1.6;
  color: #111;
  background: var(--panel);
  font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", sans-serif;
  word-wrap: break-word;
}
.render-host .lo-doc img { max-width: 100%; height: auto; }
.render-host .lo-doc table { border-collapse: collapse; width: 100%; }
.render-host .lo-doc td,
.render-host .lo-doc th { border: 1px solid #ddd; padding: 4px 8px; }
.render-host .lo-doc p { margin: 0 0 8px 0; }

.tip-actions { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
.meta-lo { color: var(--text-2); display: inline-flex; align-items: center; gap: 6px; margin-top: 10px; }

.recent-files { margin-top: 10px; }
.recent-files-label {
  font-size: 11px;
  margin-bottom: 6px;
  color: var(--text-3);
}
.recent-files-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.recent-file-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 3px 8px;
  font-size: 11px;
  color: var(--text-2);
  background: var(--panel-2);
  border: 1px solid var(--border-2);
  border-radius: 6px;
  cursor: pointer;
  transition: border-color .15s, background .15s;
  max-width: 100%;
}
.recent-file-item:hover {
  border-color: var(--primary-2);
  background: var(--primary-soft);
  color: var(--primary);
}
.recent-file-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ---- 导出进度条（含日志） ---- */
.export-progress {
  margin-top: 14px;
  padding: 12px 14px;
  background: var(--panel-2);
  border: 1px solid var(--border-2);
  border-radius: 10px;
}

.export-progress .progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  margin-bottom: 6px;
  color: var(--text-2);
}

.export-progress .progress-header .mono {
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-3);
}

.export-progress .progress-header .btn-xs {
  padding: 0 4px;
  font-size: 11px;
  line-height: 1;
  color: var(--text-3);
  background: transparent;
  border: none;
  cursor: pointer;
  border-radius: 4px;
}
.export-progress .progress-header .btn-xs:hover {
  color: var(--text);
  background: var(--panel-3);
}

.progress-bar-exp {
  height: 6px;
  background: var(--panel-2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill-exp {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--neon-magenta));
  border-radius: 3px;
  transition: width .3s ease;
}

.export-log {
  margin-top: 8px;
  max-height: 160px;
  overflow-y: auto;
  font-size: 11px;
}

.export-log-item {
  display: flex;
  gap: 8px;
  padding: 2px 0;
  align-items: baseline;
}

.export-log-item .mono {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--text-3);
  flex-shrink: 0;
}

.export-log-item .log-info {
  color: var(--text-2);
}
.export-log-item .log-error {
  color: var(--danger);
}
.export-log-item .log-warn {
  color: var(--warn);
}

@media (max-width: 900px) {
  .exp-grid { grid-template-columns: 1fr; }
}
</style>