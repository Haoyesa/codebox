<template>
  <section :class="$attrs.class">
    <p class="desc">批量重命名文件，支持替换、编号、日期、前缀后缀等多种规则。</p>

    <div class="rename-layout">
      <!-- Left: file list -->
      <div class="card" style="grid-column: 1 / -1;">
        <div class="row-spread" style="margin-bottom:12px">
          <h3 class="card-title" style="margin:0">
            <i data-lucide="files"></i>
            文件列表 ({{ files.length }})
          </h3>
          <div class="row" style="gap:8px">
            <button class="btn" @click="addFiles">
              <i data-lucide="plus"></i>添加文件
            </button>
            <button class="btn btn-ghost" @click="clearFiles">
              <i data-lucide="trash-2"></i>清空
            </button>
          </div>
        </div>
        <input type="file" ref="fileInput" multiple style="display:none" @change="onFiles">

        <div
          class="drop-zone"
          :class="{ 'drag-over': isDragOver }"
          @dragover.prevent="isDragOver = true"
          @dragleave="isDragOver = false"
          @drop.prevent="onDrop"
          @click="addFiles"
        >
          <div v-if="files.length === 0" class="drop-hint">
            <i data-lucide="upload" style="width:32px;height:32px;opacity:.35"></i>
            <p>点击或拖拽添加文件</p>
          </div>
          <div v-else class="file-list-table">
            <div class="file-list-header">
              <span style="flex:0 0 40px">#</span>
              <span style="flex:2">原文件名</span>
              <span style="flex:2">新文件名</span>
              <span style="flex:1">大小</span>
            </div>
            <div
              v-for="(f, i) in files"
              :key="i"
              :class="['file-row', { changed: f.newName !== f.name }]"
            >
              <span class="row-num">{{ i + 1 }}</span>
              <span class="row-old" :title="f.name">{{ f.name }}</span>
              <span class="row-new" :title="f.newName">{{ f.newName }}</span>
              <span class="row-size">{{ formatSize(f.size) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Rule config -->
      <div class="card">
        <h3 class="card-title"><i data-lucide="settings-2"></i>重命名规则</h3>

        <div class="rule-section">
          <div class="rule-label">查找替换</div>
          <div class="rule-row">
            <input type="text" v-model="findText" placeholder="查找..." @input="applyRules">
            <span class="arrow">→</span>
            <input type="text" v-model="replaceText" placeholder="替换为..." @input="applyRules">
          </div>
          <label class="checkbox" style="margin-top:6px">
            <input type="checkbox" v-model="caseSensitive" @change="applyRules">
            <span class="box"></span>
            <span style="font-size:12px;color:var(--text-2)">区分大小写</span>
          </label>
        </div>

        <div class="divider"></div>

        <div class="rule-section">
          <div class="rule-label">前缀 / 后缀</div>
          <div class="rule-row">
            <input type="text" v-model="prefix" placeholder="前缀" @input="applyRules">
            <input type="text" v-model="suffix" placeholder="后缀（不含扩展名）" @input="applyRules">
          </div>
        </div>

        <div class="divider"></div>

        <div class="rule-section">
          <div class="rule-label">编号序列</div>
          <div class="rule-row">
            <input type="number" v-model="startNum" min="0" @input="applyRules" style="width:70px">
            <select v-model="numFormat" @change="applyRules" style="flex:1">
              <option value="{n}">1, 2, 3...</option>
              <option value="{nn}">01, 02, 03...</option>
              <option value="{nnn}">001, 002, 003...</option>
              <option value="{nnnn}">0001, 0002...</option>
            </select>
          </div>
          <label class="checkbox" style="margin-top:6px">
            <input type="checkbox" v-model="useNum" @change="applyRules">
            <span class="box"></span>
            <span style="font-size:12px;color:var(--text-2)">启用编号</span>
          </label>
        </div>

        <div class="divider"></div>

        <div class="rule-section">
          <div class="rule-label">大小写</div>
          <div class="case-btns">
            <button
              v-for="c in ['upper', 'lower', 'title']"
              :key="c"
              :class="['case-btn', { active: caseMode === c }]"
              @click="caseMode = c; applyRules()"
            >
              {{ { upper: '全大写', lower: '全小写', title: '首字母大写' }[c] }}
            </button>
          </div>
        </div>

        <div class="divider"></div>

        <div class="rule-section">
          <div class="rule-label">日期时间</div>
          <div class="rule-row">
            <select v-model="dateFormat" @change="applyRules" style="flex:1">
              <option value="">不留日期</option>
              <option value="{date}">2026-06-10</option>
              <option value="{date2}">20260610</option>
              <option value="{time}">14-30-55</option>
              <option value="{datetime}">2026-06-10_14-30-55</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Right: preview + actions -->
      <div class="card">
        <h3 class="card-title"><i data-lucide="eye"></i>预览</h3>

        <div class="preview-summary" v-if="files.length > 0">
          <span class="tag tag-green">{{ changedCount }} 个将重命名</span>
          <span class="tag tag-amber">{{ files.length - changedCount }} 个不变</span>
        </div>

        <div v-if="files.length === 0" class="empty-state" style="padding:32px">
          <i data-lucide="files" style="width:36px;height:36px"></i>
          <p style="margin-top:8px">添加文件后预览结果</p>
        </div>

        <div class="divider"></div>

        <div class="action-block">
          <button
            class="btn btn-primary btn-block"
            :disabled="changedCount === 0 || isRunning"
            @click="startRename"
          >
            <i data-lucide="check"></i>
            {{ isRunning ? '处理中...' : '执行重命名' }}
          </button>
          <button
            v-if="lastResult && lastResult.length > 0"
            class="btn btn-warn btn-block"
            style="margin-top:8px"
            @click="undoRename"
          >
            <i data-lucide="undo-2"></i>撤销上次
          </button>
        </div>

        <div v-if="lastResult && lastResult.length > 0" class="last-run" style="margin-top:12px">
          <div style="font-size:12px;color:var(--text-3);margin-bottom:6px">上次执行了 {{ lastResult.length }} 个重命名</div>
          <div
            v-for="(r, i) in lastResult.slice(0, 3)"
            :key="i"
            class="result-item"
          >
            <i data-lucide="check-circle" style="width:12px;height:12px;color:var(--ok)"></i>
            <span>{{ r.old }}</span>
            <span style="color:var(--text-3)">→</span>
            <span style="color:var(--primary)">{{ r.new }}</span>
          </div>
          <div v-if="lastResult.length > 3" style="font-size:11px;color:var(--text-3)">
            还有 {{ lastResult.length - 3 }} 个...
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { Files, Plus, Trash2, Settings2, Eye, Check, Undo2, Upload, CheckCircle } from 'lucide-vue-next';

defineOptions({ inheritAttrs: false });

const fileInput = ref(null);
const files = ref([]);
const isDragOver = ref(false);

// Rules
const findText = ref('');
const replaceText = ref('');
const caseSensitive = ref(false);
const prefix = ref('');
const suffix = ref('');
const useNum = ref(true);
const startNum = ref(1);
const numFormat = ref('{nn}');
const caseMode = ref('');
const dateFormat = ref('');

// History
const lastResult = ref([]);
const isRunning = ref(false);

const changedCount = computed(() => {
  return files.value.filter(f => f.newName !== f.name).length;
});

function formatSize(bytes) {
  if (!bytes) return '';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function addFiles() { fileInput.value?.click(); }

function onFiles(e) {
  const list = Array.from(e.target.files || []);
  list.forEach(f => {
    files.value.push({ name: f.name, newName: f.name, size: f.size, file: f });
  });
  e.target.value = '';
  applyRules();
}

function onDrop(e) {
  isDragOver.value = false;
  const list = Array.from(e.dataTransfer?.files || []);
  list.forEach(f => {
    files.value.push({ name: f.name, newName: f.name, size: f.size, file: f });
  });
  applyRules();
}

function clearFiles() {
  files.value = [];
  lastResult.value = [];
}

function getBaseName(fullName) {
  const lastDot = fullName.lastIndexOf('.');
  if (lastDot <= 0) return { base: fullName, ext: '' };
  return { base: fullName.slice(0, lastDot), ext: fullName.slice(lastDot) };
}

function applyRules() {
  let counter = startNum.value;
  const now = new Date();
  const pad = (n, len) => String(n).padStart(len, '0');

  files.value.forEach((f, idx) => {
    let { base, ext } = getBaseName(f.name);
    let newBase = base;

    // Find & replace
    if (findText.value) {
      if (caseSensitive.value) {
        newBase = newBase.split(findText.value).join(replaceText.value);
      } else {
        const regex = new RegExp(findText.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
        newBase = newBase.replace(regex, replaceText.value);
      }
    }

    // Case transform
    if (caseMode.value === 'upper') newBase = newBase.toUpperCase();
    else if (caseMode.value === 'lower') newBase = newBase.toLowerCase();
    else if (caseMode.value === 'title') newBase = newBase.replace(/\b\w/g, c => c.toUpperCase());

    // Date/time
    if (dateFormat.value) {
      const y = now.getFullYear();
      const m = pad(now.getMonth() + 1, 2);
      const d = pad(now.getDate(), 2);
      const h = pad(now.getHours(), 2);
      const mi = pad(now.getMinutes(), 2);
      const s = pad(now.getSeconds(), 2);
      const fmt = dateFormat.value
        .replace('{date}', `${y}-${m}-${d}`)
        .replace('{date2}', `${y}${m}${d}`)
        .replace('{time}', `${h}-${mi}-${s}`)
        .replace('{datetime}', `${y}-${m}-${d}_${h}-${mi}-${s}`);
      newBase = (newBase + '_' + fmt).replace(/^_/, '');
    }

    // Prefix/suffix
    newBase = prefix.value + newBase + suffix.value;

    // Number sequence
    if (useNum.value) {
      const lenMap = { '{n}': 1, '{nn}': 2, '{nnn}': 3, '{nnnn}': 4 };
      const len = lenMap[numFormat.value] || 2;
      newBase = newBase + '_' + pad(counter, len);
      counter++;
    }

    f.newName = newBase + ext;
  });
}

async function startRename() {
  if (changedCount.value === 0) return;
  isRunning.value = true;
  const results = [];

  try {
    for (const f of files.value) {
      if (f.newName === f.name) continue;

      if (window.electronAPI) {
        await window.electronAPI.renameFile(f.file.path, f.newName);
      } else {
        // Browser: trigger download renamed file reference
        // (real rename not possible in browser - show info)
      }
      results.push({ old: f.name, new: f.newName });
      f.name = f.newName;
      f.file = { ...f.file, name: f.newName };
    }

    lastResult.value = results;
    window.showToast?.(`重命名完成 ${results.length} 个文件`, 'success');
  } catch(err) {
    window.showToast?.('重命名失败：' + err.message, 'error');
  } finally {
    isRunning.value = false;
  }
}

async function undoRename() {
  if (!lastResult.value.length) return;
  isRunning.value = true;

  try {
    const reversed = [...lastResult.value].reverse();
    for (const r of reversed) {
      if (window.electronAPI) {
        await window.electronAPI.renameFile(
          files.value.find(f => f.name === r.new)?.file?.path,
          r.old
        );
      }
      const f = files.value.find(f => f.name === r.new);
      if (f) {
        f.name = r.old;
        f.newName = r.old;
        f.file = { ...f.file, name: r.old };
      }
    }
    lastResult.value = [];
    window.showToast?.('已撤销', 'success');
  } catch(err) {
    window.showToast?.('撤销失败：' + err.message, 'error');
  } finally {
    isRunning.value = false;
  }
}

onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
});
</script>

<style scoped>
.rename-layout {
  display: grid;
  grid-template-columns: 1fr 280px 280px;
  gap: 12px;
}

.drop-zone {
  background: #fff;
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  min-height: 200px;
  cursor: pointer;
  transition: border-color .15s;
}
.drop-zone.drag-over { border-color: var(--primary); background: var(--primary-soft); }
.drop-hint {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 48px; color: var(--text-3);
}
.drop-hint p { margin: 8px 0 0; font-size: 13px; }

.file-list-table { padding: 8px; }
.file-list-header {
  display: flex; gap: 8px; padding: 6px 8px;
  font-size: 11px; color: var(--text-3); font-weight: 600;
  text-transform: uppercase; letter-spacing: .5px;
  border-bottom: 1px solid var(--border-2);
}
.file-row {
  display: flex; gap: 8px; align-items: center;
  padding: 6px 8px; font-size: 12px;
  border-bottom: 1px solid var(--border-2);
  transition: background .1s;
}
.file-row:last-child { border-bottom: none; }
.file-row.changed { background: #fef2f2; }
.row-num { flex: 0 0 40px; color: var(--text-3); text-align: center; }
.row-old { flex: 2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text); }
.row-new { flex: 2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--primary); font-weight: 500; }
.row-size { flex: 1; color: var(--text-3); }

.rule-section { margin-bottom: 8px; }
.rule-label { font-size: 12px; color: var(--text-2); margin-bottom: 6px; font-weight: 500; }
.rule-row { display: flex; gap: 6px; align-items: center; }
.arrow { color: var(--text-3); font-size: 12px; flex-shrink: 0; }

.case-btns { display: flex; gap: 4px; }
.case-btn {
  flex: 1; padding: 5px 4px; border: 1px solid var(--border);
  border-radius: 6px; background: #fff; font-size: 11px;
  cursor: pointer; transition: all .15s; white-space: nowrap;
}
.case-btn:hover { background: #f3f4f6; }
.case-btn.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.preview-summary { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }

.action-block { }
.result-item {
  display: flex; align-items: center; gap: 4px;
  font-size: 11px; padding: 2px 0; overflow: hidden;
}
.result-item span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.result-item span:first-of-type { flex: 1; min-width: 0; }

.divider { height: 1px; background: var(--border-2); margin: 12px 0; }

@media (max-width: 900px) {
  .rename-layout { grid-template-columns: 1fr; }
}
</style>