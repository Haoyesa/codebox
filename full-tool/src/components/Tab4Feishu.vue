<template>
  <section :class="$attrs.class">
    <p class="desc">配置多个图片文件夹，一键上传至飞书多维表格附件字段。</p>

    <div class="card">
      <div class="form-grid">
        <div class="form-row">
          <label class="form-label">App ID</label>
          <div class="form-input-group">
            <input
              v-model="appId"
              :type="showAppId ? 'text' : 'password'"
              placeholder="cli_xxxxxxxxxxxxxxxx"
              class="mono"
            />
            <button class="btn-icon" :title="showAppId ? '隐藏' : '显示'" @click="showAppId = !showAppId">
              <i :data-lucide="showAppId ? 'eye-off' : 'eye'"></i>
            </button>
          </div>
        </div>
        <div class="form-row">
          <label class="form-label">App Secret</label>
          <div class="form-input-group">
            <input
              v-model="appSecret"
              :type="showSecret ? 'text' : 'password'"
              placeholder="应用密钥"
              class="mono"
            />
            <button class="btn-icon" :title="showSecret ? '隐藏' : '显示'" @click="showSecret = !showSecret">
              <i :data-lucide="showSecret ? 'eye-off' : 'eye'"></i>
            </button>
          </div>
        </div>
        <div class="row" style="gap: 8px; margin-top: 4px;">
          <button class="btn btn-sm" :disabled="state.isVerifying" @click="verifyAuth">
            <i data-lucide="check"></i>{{ state.isVerifying ? '验证中…' : '验证授权' }}
          </button>
          <span v-if="state.authOk" class="tag tag-green" style="margin-left: 4px;">
            <PulseDot />已认证
          </span>
          <span v-else-if="state.authError" class="tag tag-amber" style="margin-left: 4px;">
            失败：{{ state.authError }}
          </span>
        </div>

        <div class="form-row">
          <label class="form-label">表格链接</label>
          <input v-model="tableUrl" type="text" placeholder="多维表格链接" />
        </div>

        <div class="form-row">
          <label class="form-label">飞书附件字段</label>
          <input v-model="attachField" type="text" placeholder="内容页图片" />
        </div>

        <div class="form-row form-row-2col">
          <div>
            <label class="form-label">表格起始行</label>
            <input v-model.number="rowStart" type="number" min="1" />
          </div>
          <div>
            <label class="form-label">表格结束行</label>
            <input v-model.number="rowEnd" type="number" min="1" />
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
            <input v-model="f.path" type="text" placeholder="选择文件夹" class="path-input mono" readonly />
            <button class="btn btn-sm" @click="pickFolderPath(f)">
              <i data-lucide="folder-open"></i>选择
            </button>
            <label class="checkbox" style="margin-left: 8px;">
              <input v-model="f.recursive" type="checkbox" />
              <span class="box"></span>递归
            </label>
            <input v-model.number="f.perRow" type="number" min="1" max="20" class="num" title="每行写入图片数" />
            <span class="muted" style="font-size: 12px;">张/行</span>
            <button class="btn-icon" title="移除" @click="removeFolder(f.id)">
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
          <PulseDot :color="state.dotClass" />
          <span style="margin-left: 6px;">{{ state.statusText }}</span>
        </span>
      </div>

      <div v-if="uploadProgress.status !== 'idle'" class="upload-progress">
        <ProgressBar :percent="uploadProgress.total ? uploadProgress.current / uploadProgress.total * 100 : 0" />
        <div class="row-spread" style="font-size: 12px; color: var(--text-2); margin-top: 6px;">
          <span>{{ uploadProgress.status === 'running' ? '上传中…' : '完成' }}</span>
          <span class="mono">{{ uploadProgress.current }}/{{ uploadProgress.total }}</span>
        </div>
      </div>

      <EmptyState v-if="!appId || !appSecret" icon="settings" title="配置飞书应用信息后开始上传" subtitle="填写 App ID 和 App Secret 并验证通过后即可使用" style="margin-top: 16px; border-top: 1px solid var(--border-2); padding-top: 24px;" />

      <div v-if="state.progress.total > 0" style="margin-top: 12px;">
        <ProgressBar :percent="state.progress.percent" />
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
import { useToast } from '../composables/useToast.js';
import ProgressBar from './ProgressBar.vue';
import EmptyState from './EmptyState.vue';
import PulseDot from './PulseDot.vue';
const toast = useToast();

const appId = ref('');
const appSecret = ref('');
const showAppId = ref(false);
const showSecret = ref(false);
const tableUrl = ref('');
const attachField = ref('内容页图片');
const rowStart = ref(2);
const rowEnd = ref(2);

const folders = ref([]); // {id, path, recursive, perRow}
let folderId = 1;

const uploadProgress = ref({ current: 0, total: 0, status: 'idle' });
let hideProgressTimer = null;

const state = reactive({
  isVerifying: false,
  authOk: false,
  authError: '',
  isUploading: false,
  statusText: '待命',
  dotClass: 'idle',
  progress: { total: 0, done: 0, percent: 0, label: '' },
  logs: []
});

const canStart = computed(() => {
  return appId.value && appSecret.value && state.authOk && tableUrl.value && attachField.value && folders.value.length > 0;
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

async function verifyAuth() {
  if (!appId.value || !appSecret.value) {
    toast.show('请先填写 App ID 和 App Secret', 'warn');
    return;
  }
  state.isVerifying = true;
  state.authError = '';
  try {
    const r = await window.electronAPI.feishuGetToken({ appId: appId.value, appSecret: appSecret.value });
    if (!r.success) { state.authError = r.error || '验证失败'; state.authOk = false; toast.show(state.authError, 'error'); }
    else { state.authOk = true; toast.show('飞书授权验证通过', 'success'); }
  } catch (e) {
    state.authError = e.message; state.authOk = false;
    toast.show('授权验证失败: ' + e.message, 'error');
  } finally {
    state.isVerifying = false;
  }
}

async function pickFolderPath(folder) {
  if (!window.electronAPI) {
    toast.show('请在 Electron 版本中选择目录', 'warn');
    return;
  }
  try {
    const r = await window.electronAPI.openDirectory();
    if (r.canceled || !r.filePaths.length) return;
    folder.path = r.filePaths[0];
  } catch (err) {
    toast.show('选择目录失败: ' + err.message, 'error');
  }
}

async function parseBitable(url) {
  // 飞书表格链接常见形式：
  // https://xxx.feishu.cn/base/{appToken}?table={tableId}
  // https://xxx.feishu.cn/wiki/{wikiToken}?table={tableId}
  try {
    const u = new URL(url);
    const parts = u.pathname.split('/').filter(Boolean);
    // Wiki 链接: https://xxx.feishu.cn/wiki/{wikiToken}
    const wikiIdx = parts.indexOf('wiki');
    if (wikiIdx >= 0) {
      const wikiToken = parts[wikiIdx + 1];
      if (!wikiToken) return null;
      if (!window.electronAPI?.feishuResolveWiki) {
        toast.show('当前环境不支持 Wiki 链接解析', 'error');
        return null;
      }
      const res = await window.electronAPI.feishuResolveWiki({
        appId: appId.value, appSecret: appSecret.value, wikiToken
      });
      if (!res?.success) {
        toast.show(res?.error || 'Wiki 链接解析失败', 'error');
        return null;
      }
      const tableId = u.searchParams.get('table') || u.searchParams.get('view');
      if (!tableId) {
        toast.show('Wiki 链接缺少 table/view 参数', 'error');
        return null;
      }
      return { appToken: res.appToken, tableId };
    }
    // 普通 Bitable 链接
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
    toast.show('请补全授权码、表格链接、文件夹', 'warn');
    return;
  }
  const bitable = await parseBitable(tableUrl.value);
  if (!bitable) {
    toast.show('无法解析表格链接，请检查格式', 'error');
    return;
  }
  abortFlag = false;
  state.isUploading = true;
  state.dotClass = '';
  state.statusText = '上传中…';
  state.progress = { total: 0, done: 0, percent: 0, label: '' };
  state.logs = [];
  uploadProgress.value = { current: 0, total: 0, status: 'running' };
  if (hideProgressTimer) { clearTimeout(hideProgressTimer); hideProgressTimer = null; }

  try {
    // 1) 展开文件夹，收集所有图片
    const allImages = [];
    for (const f of folders.value) {
      if (!f.path) continue;
      // Walk recursively when the user opted in; the main process skips hidden/system dirs
// and limits depth to 8. Pass an extension filter so we never have to post-filter in JS.
const r = await window.electronAPI.readDir(f.path, { recursive: !!f.recursive, extensions: ['png','jpg','jpeg','webp','gif','bmp'] });
      if (!r.success) {
        log('err', `读取目录失败：${f.path} - ${r.error}`);
        continue;
      }
      // main process already filtered by extension; just sort.
      const list = r.files.slice().sort((a, b) => a.localeCompare(b, 'zh-Hans-CN', { numeric: true }));
      for (const name of list) {
        allImages.push({ folder: f, name, path: f.path.replace(/[\\/]+$/, '') + '/' + name });
      }
    }
    if (allImages.length === 0) {
      throw new Error('所有文件夹中没有找到图片');
    }
    log('info', `共找到 ${allImages.length} 张图片`);

    // 2) 列出表格记录 (走 IPC 代理, 避免 CORS)
    state.statusText = '获取表格记录…';
    const lr = await window.electronAPI.feishuListRecords({
      appId: appId.value, appSecret: appSecret.value,
      appToken: bitable.appToken, tableId: bitable.tableId
    });
    if (!lr.success) throw new Error('获取记录失败：' + (lr.error || JSON.stringify(lr.raw || {})));
    const records = lr.items;
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
    uploadProgress.value.total = rows.length;
    uploadProgress.value.current = 0;
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
          // a. 上传文件到 bitable 附件中转, 拿 file_token
          const up = await window.electronAPI.feishuUploadAttachment({
            appId: appId.value, appSecret: appSecret.value,
            appToken: bitable.appToken, filePath: img.path, fileName: img.name
          });
          if (!up.success) {
            log('err', `${img.name} 上传失败：${up.error || JSON.stringify(up.raw || {})}`);
            continue;
          }
          // b. 把 file_token 写进本行记录的附件字段
          const ur = await window.electronAPI.feishuUpdateRecord({
            appId: appId.value, appSecret: appSecret.value,
            appToken: bitable.appToken, tableId: bitable.tableId,
            recordId: row.record.record_id, field: attachField.value, fileTokens: [up.fileToken]
          });
          if (!ur.success) {
            log('err', `${img.name} 写记录失败：${ur.error || JSON.stringify(ur.raw || {})}`);
          } else {
            log('ok', `${img.name} ✓`);            log('ok', `${img.name} ✓`);
          }
        } catch (e) {
          log('err', `${img.name} 失败：${e.message}`);
          toast.show(`${img.name} 处理失败: ${e.message}`, 'error');
        }
      }

      state.progress.done = r + 1;
      state.progress.percent = Math.round((state.progress.done / state.progress.total) * 100);
      uploadProgress.value.current = r + 1;
    }

    if (abortFlag) {
      state.statusText = '已取消';
      state.dotClass = 'warn';
      toast.show('已取消上传', 'warn');
    } else {
      state.statusText = '上传完成';
      state.dotClass = '';
      log('ok', '全部完成');
      toast.show(`完成 ${state.progress.done} 行`, 'success');
    }
  } catch (err) {
    log('err', err.message);
    state.statusText = '出错：' + err.message;
    state.dotClass = 'err';
    toast.show(err.message, 'error');
  } finally {
    uploadProgress.value.status = 'done';
    if (hideProgressTimer) clearTimeout(hideProgressTimer);
    hideProgressTimer = setTimeout(() => {
      uploadProgress.value = { current: 0, total: 0, status: 'idle' };
    }, 3000);
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
  margin-top: 12px; padding: 32px 12px;
  border: 1.5px dashed var(--border-strong);
  border-radius: var(--radius);
  text-align: center;
  color: var(--text-3);
  font-size: 13px;
  transition: border-color .2s, background .2s;
}
.folder-empty:hover { border-color: var(--neon-cyan); background: var(--neon-cyan-soft); }
.folder-list { display: flex; flex-direction: column; gap: 6px; margin-top: 12px; }
.folder-item {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 10px;
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: border-color .15s, box-shadow .15s, transform .15s;
}
.folder-item:hover { border-color: var(--border-strong); box-shadow: var(--shadow-sm); transform: translateX(2px); }
.folder-idx {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 28px; height: 22px;
  background: var(--neon-cyan-soft);
  color: #0369a1;
  border-radius: 6px;
  font-size: 11px; font-weight: 600;
  font-family: var(--font-mono);
  transition: transform .15s;
}
.folder-item:hover .folder-idx { transform: scale(1.05); }
.path-input { flex: 1; background: #fff; font-size: 12px; }
.num { width: 56px; }

.action-row {
  display: flex; align-items: center; gap: 10px;
  margin-top: 18px;
}

.log-pane {
  margin-top: 14px; max-height: 200px; overflow-y: auto;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.02) 0%, rgba(15, 23, 42, 0.04) 100%);
  border: 1px solid var(--border-2);
  border-radius: 8px;
  padding: 10px 12px;
  font-family: var(--font-mono);
  font-size: 12px;
  line-height: 1.6;
}
.log-line { display: flex; gap: 8px; padding: 2px 0; border-radius: 3px; transition: background .1s; }
.log-line:hover { background: rgba(15, 23, 42, 0.03); }
.log-time { color: var(--text-3); flex-shrink: 0; }
.log-msg { color: var(--text-2); }
.log-line.ok .log-msg { color: var(--ok-deep); }
.log-line.err .log-msg { color: var(--primary-deep); }
.log-line.info .log-msg { color: var(--text-2); }

.upload-progress { margin-top: 12px; }
</style>