<template>
  <section :class="$attrs.class">
    <p class="desc">配置多个图片文件夹，一键上传至飞书多维表格附件字段。</p>

    <div class="card">
      <div class="form-grid">
        <div class="form-row">
          <label class="form-label">授权码</label>
          <div class="form-input-group">
            <input
              :type="showToken ? 'text' : 'password'"
              v-model="token"
              placeholder="PersonalBaseToken"
              class="mono"
            />
            <button class="btn-icon" @click="showToken = !showToken" :title="showToken ? '隐藏' : '显示'">
              <i :data-lucide="showToken ? 'eye-off' : 'eye'"></i>
            </button>
          </div>
        </div>

        <div class="form-row">
          <label class="form-label">表格链接</label>
          <input type="text" v-model="tableUrl" placeholder="多维表格链接" />
        </div>

        <div class="form-row">
          <label class="form-label">飞书附件字段</label>
          <input type="text" v-model="attachField" placeholder="内容页图片" />
        </div>

        <div class="form-row form-row-2col">
          <div>
            <label class="form-label">表格起始行</label>
            <input type="number" v-model.number="rowStart" min="1" />
          </div>
          <div>
            <label class="form-label">表格结束行</label>
            <input type="number" v-model.number="rowEnd" min="1" />
          </div>
        </div>
      </div>

      <div class="divider-neon"></div>

      <div class="folder-block">
        <div class="row-spread">
          <div>
            <span class="folder-title">图片文件夹配置</span>
            <span class="muted" style="margin-left: 8px;">
              可多次添加文件夹；每行按配置数量合并写入；顺序模式按文件名排序并循环。
            </span>
          </div>
          <button class="btn btn-secondary" @click="addFolder">
            <i data-lucide="plus"></i>添加文件夹
          </button>
        </div>

        <div v-if="folders.length === 0" class="folder-empty">
          点击「+ 添加文件夹」配置上传目录
        </div>
        <div v-else class="folder-list">
          <div v-for="(f, i) in folders" :key="f.id" class="folder-item">
            <span class="folder-idx mono">#{{ i + 1 }}</span>
            <input type="text" v-model="f.path" placeholder="选择文件夹" class="path-input mono" readonly />
            <button class="btn btn-sm" @click="pickFolderPath(f)">
              <i data-lucide="folder-open"></i>选择
            </button>
            <label class="checkbox" style="margin-left: 8px;">
              <input type="checkbox" v-model="f.recursive" />
              <span class="box"></span>递归
            </label>
            <input type="number" v-model.number="f.perRow" min="1" max="20" class="num" title="每行写入图片数" />
            <span class="muted" style="font-size: 12px;">张/行</span>
            <button class="btn-icon" @click="removeFolder(f.id)" title="移除">
              <i data-lucide="x"></i>
            </button>
          </div>
        </div>
      </div>

      <div class="action-row">
        <button class="btn btn-primary btn-lg" :disabled="!canStart || state.isUploading" @click="startUpload">
          <i data-lucide="upload-cloud"></i>
          {{ state.isUploading ? '上传中…' : '开始一键上传' }}
        </button>
        <button class="btn btn-warn" :disabled="!state.isUploading" @click="cancelUpload">取消</button>
        <span class="muted" style="margin-left: 8px;">
          <span class="pulse-dot" :class="state.dotClass"></span>
          <span style="margin-left: 6px;">{{ state.statusText }}</span>
        </span>
      </div>

      <div v-if="state.progress.total > 0" style="margin-top: 12px;">
        <div class="progress-bar"><div class="fill" :style="{ width: state.progress.percent + '%' }"></div></div>
        <div class="row-spread" style="font-size: 12px; color: var(--text-2); margin-top: 6px;">
          <span>{{ state.progress.label }}</span>
          <span class="mono">{{ state.progress.done }}/{{ state.progress.total }}</span>
        </div>
      </div>

      <div v-if="state.logs.length" class="log-pane">
        <div v-for="(log, i) in state.logs" :key="i" class="log-line" :class="log.type">
          <span class="log-time mono">{{ log.time }}</span>
          <span class="log-msg">{{ log.msg }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';

const token = ref('');
const showToken = ref(false);
const tableUrl = ref('');
const attachField = ref('内容页图片');
const rowStart = ref(2);
const rowEnd = ref(2);

const folders = ref([]); // {id, path, recursive, perRow}
let folderId = 1;

const state = reactive({
  isUploading: false,
  statusText: '待命',
  dotClass: 'idle',
  progress: { total: 0, done: 0, percent: 0, label: '' },
  logs: []
});

const canStart = computed(() => {
  return token.value && tableUrl.value && attachField.value && folders.value.length > 0;
});

function log(type, msg) {
  const t = new Date();
  const time = t.toTimeString().slice(0, 8);
  state.logs.unshift({ type, msg, time });
  if (state.logs.length > 200) state.logs.length = 200;
}

function addFolder() {
  folders.value.push({ id: folderId++, path: '', recursive: true, perRow: 1 });
}
function removeFolder(id) {
  folders.value = folders.value.filter(f => f.id !== id);
}

async function pickFolderPath(folder) {
  if (!window.electronAPI) {
    window.showToast?.('请在 Electron 版本中选择目录', 'warn');
    return;
  }
  const r = await window.electronAPI.openDirectory();
  if (r.canceled || !r.filePaths.length) return;
  folder.path = r.filePaths[0];
}

function parseBitable(url) {
  // 飞书表格链接常见形式：
  // https://xxx.feishu.cn/base/{appToken}?table={tableId}
  // https://xxx.feishu.cn/wiki/{wikiToken} ... 这种需要先 wiki resolve
  try {
    const u = new URL(url);
    const parts = u.pathname.split('/').filter(Boolean);
    const baseIdx = parts.indexOf('base');
    if (baseIdx < 0) return null;
    const appToken = parts[baseIdx + 1];
    const tableId = u.searchParams.get('table') || u.searchParams.get('view');
    if (!appToken || !tableId) return null;
    return { appToken, tableId };
  } catch (_) { return null; }
}

let abortFlag = false;
async function startUpload() {
  if (!canStart.value) {
    window.showToast?.('请补全授权码、表格链接、文件夹', 'warn');
    return;
  }
  const bitable = parseBitable(tableUrl.value);
  if (!bitable) {
    window.showToast?.('无法解析表格链接，请检查格式', 'error');
    return;
  }
  abortFlag = false;
  state.isUploading = true;
  state.dotClass = '';
  state.statusText = '上传中…';
  state.progress = { total: 0, done: 0, percent: 0, label: '' };
  state.logs = [];

  try {
    // 1) 展开文件夹，收集所有图片
    const allImages = [];
    for (const f of folders.value) {
      if (!f.path) continue;
      const r = await window.electronAPI.readDir(f.path);
      if (!r.success) {
        log('err', `读取目录失败：${f.path} - ${r.error}`);
        continue;
      }
      const exts = ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp'];
      const list = r.files.filter(name => exts.includes(name.split('.').pop().toLowerCase()));
      list.sort((a, b) => a.localeCompare(b, 'zh-Hans-CN', { numeric: true }));
      for (const name of list) {
        allImages.push({ folder: f, name, path: f.path.replace(/[\\/]+$/, '') + '/' + name });
      }
    }
    if (allImages.length === 0) {
      throw new Error('所有文件夹中没有找到图片');
    }
    log('info', `共找到 ${allImages.length} 张图片`);

    // 2) 列出表格记录
    state.statusText = '获取表格记录…';
    const headers = { Authorization: 'Bearer ' + token.value };
    const recordsRes = await fetch(
      `https://open.feishu.cn/open-apis/bitable/v1/apps/${bitable.appToken}/tables/${bitable.tableId}/records?page_size=500`,
      { headers }
    );
    const recordsData = await recordsRes.json();
    if (recordsData.code !== 0) {
      throw new Error('获取记录失败：' + (recordsData.msg || JSON.stringify(recordsData)));
    }
    const records = recordsData.data.items || [];
    log('info', `表格共 ${records.length} 条记录`);

    // 3) 计算每个目标行需要的图片
    const rows = [];
    const startIdx = Math.max(0, rowStart.value - 1);
    const endIdx = Math.min(records.length, rowEnd.value);
    for (let i = startIdx; i < endIdx; i++) {
      const perRow = folders.value[0]?.perRow || 1;
      const imgs = [];
      for (let k = 0; k < perRow; k++) {
        const idx = (i - startIdx) * perRow + k;
        if (idx < allImages.length) imgs.push(allImages[idx]);
      }
      rows.push({ record: records[i], images: imgs });
    }
    if (rows.length === 0) {
      throw new Error('行范围没有命中任何记录');
    }
    state.progress.total = rows.length;
    log('info', `将处理 ${rows.length} 行`);

    // 4) 逐行上传
    for (let r = 0; r < rows.length; r++) {
      if (abortFlag) break;
      const row = rows[r];
      state.progress.label = `行 ${r + 1} - 上传 ${row.images.length} 张`;
      log('info', `开始行 ${r + 1}: ${row.images.length} 张`);

      for (let k = 0; k < row.images.length; k++) {
        if (abortFlag) break;
        const img = row.images[k];
        try {
          // a. 读文件 → base64
          const fr = await window.electronAPI.readFile(img.path);
          if (!fr.success) throw new Error(fr.error);
          const bytes = new Uint8Array(fr.data);
          let binary = '';
          for (let b = 0; b < bytes.byteLength; b++) binary += String.fromCharCode(bytes[b]);
          const base64 = btoa(binary);

          // b. 调 Feishu upload_attachment API
          const form = new FormData();
          form.append('file_name', img.name);
          form.append('parent_type', 'bitable_image');
          form.append('parent_node', bitable.appToken);
          form.append('size', String(bytes.byteLength));
          form.append('file', new Blob([bytes], { type: 'image/' + (img.name.split('.').pop() || 'png').toLowerCase() }), img.name);

          const upRes = await fetch(`https://open.feishu.cn/open-apis/bitable/v1/apps/${bitable.appToken}/tables/${bitable.tableId}/records/${row.record.record_id}/upload_attachment`, {
            method: 'POST',
            headers: { Authorization: 'Bearer ' + token.value },
            body: form
          });
          const upData = await upRes.json();
          if (upData.code !== 0) {
            log('err', `${img.name} 上传失败：${upData.msg || JSON.stringify(upData)}`);
          } else {
            log('ok', `${img.name} ✓`);
          }
        } catch (e) {
          log('err', `${img.name} 失败：${e.message}`);
        }
      }

      state.progress.done = r + 1;
      state.progress.percent = Math.round((state.progress.done / state.progress.total) * 100);
    }

    if (abortFlag) {
      state.statusText = '已取消';
      state.dotClass = 'warn';
      window.showToast?.('已取消上传', 'warn');
    } else {
      state.statusText = '上传完成';
      state.dotClass = '';
      log('ok', '全部完成');
      window.showToast?.(`完成 ${state.progress.done} 行`, 'success');
    }
  } catch (err) {
    log('err', err.message);
    state.statusText = '出错：' + err.message;
    state.dotClass = 'err';
    window.showToast?.(err.message, 'error');
  } finally {
    state.isUploading = false;
  }
}

function cancelUpload() {
  abortFlag = true;
  state.statusText = '正在取消…';
}

onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
});
</script>

<style scoped>
.form-grid { display: grid; gap: 14px; }
.form-row { display: grid; grid-template-columns: 100px 1fr; gap: 12px; align-items: center; }
.form-row-2col { grid-template-columns: 100px 1fr 1fr; }
.form-label { font-size: 13px; color: var(--text-2); }
.form-input-group { display: flex; gap: 6px; align-items: center; }
.form-input-group input { flex: 1; }

.folder-block { margin-top: 4px; }
.folder-title { font-weight: 600; font-size: 14px; }
.muted { color: var(--text-3); font-size: 13px; }
.folder-empty {
  margin-top: 12px; padding: 28px 12px;
  border: 1px dashed var(--border-strong);
  border-radius: var(--radius);
  text-align: center;
  color: var(--text-3);
  font-size: 13px;
}
.folder-list { display: flex; flex-direction: column; gap: 8px; margin-top: 12px; }
.folder-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px;
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.folder-idx {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 28px; height: 22px;
  background: var(--neon-cyan-soft);
  color: #0369a1;
  border-radius: 4px;
  font-size: 11px; font-weight: 600;
}
.path-input { flex: 1; background: #fff; font-size: 12px; }
.num { width: 56px; }

.action-row {
  display: flex; align-items: center; gap: 10px;
  margin-top: 18px;
}

.log-pane {
  margin-top: 14px; max-height: 200px; overflow-y: auto;
  background: rgba(15, 23, 42, 0.03);
  border: 1px solid var(--border-2);
  border-radius: 8px;
  padding: 8px 12px;
  font-family: var(--font-mono);
  font-size: 12px;
}
.log-line { display: flex; gap: 8px; padding: 2px 0; }
.log-time { color: var(--text-3); flex-shrink: 0; }
.log-msg { color: var(--text-2); }
.log-line.ok .log-msg { color: var(--ok-deep); }
.log-line.err .log-msg { color: var(--primary-deep); }
.log-line.info .log-msg { color: var(--text-2); }
</style>