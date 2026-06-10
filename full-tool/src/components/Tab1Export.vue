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
        <div class="card-section">
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
import { Download, FileText, FolderOpen, FolderOutput, AlertTriangle } from 'lucide-vue-next';
import * as mammoth from 'mammoth';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

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
let exportAbortController = null;

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
function truncatePath(p) {
  if (!p) return '';
  if (p.length <= 30) return p;
  return '...' + p.slice(-27);
}

function formatSize(bytes) {
  if (!bytes) return '';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

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
      window.showToast?.(`已选择 ${state.files.length} 个文件`);
    };
    input.click();
    return;
  }

  const result = await window.electronAPI.openFiles();
  if (!result.canceled && result.filePaths.length > 0) {
    // Convert paths to file info objects
    state.files = result.filePaths.map(p => ({
      path: p,
      name: p.split(/[\\/]/).pop(),
      size: 0
    }));
    state.statusText = `已选择 ${state.files.length} 个文件`;
    window.showToast?.(`已选择 ${state.files.length} 个文件`, 'success');
    await nextTick();
    window.lucide?.createIcons();
  }
}

async function pickFolder() {
  if (!window.electronAPI) {
    window.showToast?.('浏览器模式下无法选择文件夹，请使用 Electron 版本', 'error');
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
        name: folderPath.split(/[\\/]/).pop(),
        files: dirResult.files.filter(f => {
          const ext = f.split('.').pop().toLowerCase();
          return supportedExt.includes(ext);
        })
      });
      state.statusText = `已选择文件夹：${folderPath.split(/[\\/]/).pop()}`;
      window.showToast?.('文件夹已添加', 'success');
      await nextTick();
      window.lucide?.createIcons();
    }
  }
}

async function pickOutputDir() {
  if (!window.electronAPI) {
    window.showToast?.('浏览器模式下无法选择目录，请使用 Electron 版本', 'error');
    return;
  }

  try {
    const result = await window.electronAPI.selectOutputDir();
    if (result.canceled) return;
    if (result.filePaths && result.filePaths.length > 0) {
      state.outputDir = result.filePaths[0];
      state.statusText = '输出目录已设置';
      window.showToast?.('输出目录已设置', 'success');
    }
  } catch (err) {
    console.error('[pickOutputDir]', err);
    window.showToast?.('选择目录失败：' + (err.message || '未知错误'), 'error');
  }
}

function clearFiles() {
  state.files = [];
  state.statusText = '选择文件或文件夹后自动扫描';
}

function cancelExport() {
  state.cancelRequested = true;
  if (exportAbortController) {
    exportAbortController.abort();
  }
  state.statusText = '正在取消...';
}

// .docx 走纯 JS 兜底（mammoth → html2canvas → png/jpg/pdf）
async function convertDocxViaJS(filePath, format, scale) {
  const r = await window.electronAPI.readFile(filePath);
  if (!r.success) throw new Error('读取文件失败：' + r.error);
  const result = await mammoth.convertToHtml({ arrayBuffer: r.data });
  const html = result.value || '';
  if (!html.trim()) throw new Error('docx 内容为空');

  const baseName = filePath.split(/[\\/]/).pop().replace(/\.docx?$/i, '');
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

  const safeDir = String(state.outputDir).replace(/[\\/]+$/, '');
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
    allFiles.push({ path: f.path, name: f.name, ext: f.name.split('.').pop().toLowerCase() });
  }
  for (const folder of state.folders) {
    for (const fileName of folder.files) {
      allFiles.push({
        path: folder.path + '/' + fileName,
        name: fileName,
        ext: fileName.split('.').pop().toLowerCase()
      });
    }
  }
  const totalFiles = allFiles.length;
  state.totalCount = totalFiles;

  if (totalFiles === 0) {
    window.showToast?.('没有可导出的文件', 'error');
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
    window.showToast?.('未检测到 LibreOffice，PDF/PPT/XLS 等格式将跳过；.docx 仍可导出', 'warn');
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
          window.showToast?.(file.name + ' 需 LibreOffice（点 Tab1 底部提示卡下载安装）', 'warn');
        } else {
          await window.electronAPI.libreOfficeConvert({
            inputPath: file.path,
            outputDir: state.outputDir,
            format: fmt,
            scale: scale
          });
        }
      }
      if (state.skippedFiles.indexOf(file.name) < 0 || file.ext === 'docx') {
        successCount++;
      }
    } catch (err) {
      console.error('Convert failed for', file.name, err);
      state.failedFiles.push({ name: file.name, reason: (err && err.message) || String(err) });
      window.showToast?.('转换失败：' + file.name, 'error');
    }
    state.doneCount = successCount + state.failedFiles.length + state.skippedFiles.length;
    state.progress = Math.round((state.doneCount / totalFiles) * 100);
  }

  // 收尾汇总
  const failed = state.failedFiles.length;
  const skipped = state.skippedFiles.length;
  // 按扩展名分组跳过文件
  const skipByExt = {};
  for (const name of state.skippedFiles) {
    const ext = (name.split('.').pop() || '?').toLowerCase();
    skipByExt[ext] = (skipByExt[ext] || 0) + 1;
  }
  const skipExtSummary = Object.keys(skipByExt).length
    ? '（' + Object.entries(skipByExt).map(([e, n]) => e + ' ×' + n).join('，') + '）'
    : '';
  const skipHint = skipped > 0 ? ' — 需 LibreOffice，可点 Tab1 底部下载或手动指定 soffice.exe' : '';

  if (state.cancelRequested) {
    state.statusText = '已取消（成功 ' + successCount + '，失败 ' + failed + '，跳过 ' + skipped + skipExtSummary + '）';
    window.showToast?.('导出已取消', 'warn');
  } else {
    let msg = '导出完成：成功 ' + successCount;
    if (failed > 0) msg += '，失败 ' + failed;
    if (skipped > 0) msg += '，跳过 ' + skipped + skipExtSummary;
    state.statusText = msg + skipHint;
    window.showToast?.(msg, failed > 0 ? 'warn' : (skipped > 0 ? 'warn' : 'success'));
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
      window.showToast?.('导出完成！', 'success');
    } else {
      state.progress = Math.round(p);
      state.statusText = `正在导出... ${Math.round(p)}%`;
    }
  }, 200);
}

async function downloadLO() {
  window.showToast?.('正在打开下载页面...', 'info');
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
    window.showToast?.('请在 Electron 版本中设置', 'error');
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
    window.showToast?.('已指定 LibreOffice 路径：' + res.path, 'success');
  } else {
    window.showToast?.('设置失败：' + (res.error || '未知错误'), 'error');
  }
}

onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
  await checkLibreOffice();
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
  display: inline-flex; align-items: center; gap: 4px;
  padding: 3px 8px; background: #f3f4f6; border-radius: 6px;
}
.meta-row .meta b { color: var(--text); font-weight: 500; }
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
}
.file-list-items { max-height: 140px; overflow-y: auto; }
.file-item {
  display: flex; align-items: center; gap: 8px;
  padding: 4px 0; font-size: 12px;
  border-bottom: 1px solid var(--border-2);
}
.file-item:last-child { border-bottom: none; }
.file-name { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text); }
.file-size { color: var(--text-3); }
.file-more { font-size: 12px; color: var(--text-3); padding: 4px 0; }

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
  background: #fff; font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all .15s;
}
.format-chip:hover { border-color: var(--primary-2); }
.format-chip.active {
  background: var(--primary-soft); color: var(--primary);
  border-color: #fecaca;
}

/* Export block */
.export-block { margin-top: 14px; }
.export-block .big {
  width: 100%; padding: 14px 18px;
  background: linear-gradient(180deg, var(--primary) 0%, #f56565 100%);
  color: #fff; border: 0; border-radius: 8px;
  font-size: 15px; font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(239,68,68,.3);
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: filter .15s, transform .1s;
}
.export-block .big:hover:not(:disabled) { filter: brightness(1.05); }
.export-block .big:active:not(:disabled) { transform: scale(0.98); }
.export-block .big:disabled { opacity: 0.6; cursor: not-allowed; }

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

/* JS .docx 脱机渲染节点（页面外脱机布局） */
.render-host {
  position: fixed;
  left: -10000px;
  top: 0;
  width: 794px;
  pointer-events: none;
  z-index: -1;
  background: #fff;
}
.render-host .lo-doc {
  padding: 48px;
  font-size: 14px;
  line-height: 1.6;
  color: #111;
  background: #fff;
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

@media (max-width: 900px) {
  .exp-grid { grid-template-columns: 1fr; }
}
</style>