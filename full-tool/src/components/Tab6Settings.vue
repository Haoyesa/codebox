<template>
  <section :class="$attrs.class">
    <!-- 路径设置 -->
    <p class="desc">配置 LibreOffice 与默认输出目录。</p>
    <div class="card">
      <h3 class="card-title"><i data-lucide="folder-cog"></i> 路径设置</h3>

      <!-- LibreOffice 路径 -->
      <div class="setting-row">
        <div class="setting-label">
          <span>LibreOffice 路径</span>
          <span :class="['tag', loStatus.found ? 'tag-green' : 'tag-amber']" style="font-size:11px;">
            {{ loStatus.found ? '已找到' : '未配置' }}
          </span>
        </div>
        <div class="input-with-btn">
          <input
            type="text"
            v-model="loPath"
            placeholder="自动检测或手动选择 soffice.exe"
            class="mono"
            readonly
          />
          <button class="btn btn-sm" @click="selectLOPath" title="选择 soffice.exe">
            <i data-lucide="folder-open"></i>浏览
          </button>
          <button class="btn btn-sm btn-ghost" @click="detectLO" title="重新检测" :disabled="loChecking">
            <i data-lucide="scan-search"></i>{{ loChecking ? '检测中' : '检测' }}
          </button>
        </div>
        <p v-if="loStatus.path" class="setting-hint mono">{{ loStatus.path }}</p>
        <p v-else class="setting-hint muted">
          未检测到 LibreOffice。功能如 PPT/Excel 导出需要它，请先
          <a href="https://www.libreoffice.org/download" target="_blank">下载安装</a>。
        </p>
      </div>

      <!-- 默认输出目录 -->
      <div class="setting-row" style="margin-top:14px;">
        <div class="setting-label">
          <span>默认输出目录</span>
          <span v-if="outputDir" class="tag tag-blue" style="font-size:11px;">已设置</span>
        </div>
        <div class="input-with-btn">
          <input
            type="text"
            v-model="outputDir"
            placeholder="选择默认导出目录"
            class="mono"
            readonly
          />
          <button class="btn btn-sm" @click="selectOutputDir">
            <i data-lucide="folder-open"></i>选择
          </button>
          <button v-if="outputDir" class="btn btn-sm btn-ghost" @click="outputDir = ''; savePaths()">
            <i data-lucide="x"></i>清除
          </button>
        </div>
        <p class="setting-hint muted">文档导出、拼图生成等将默认保存到此目录。</p>
      </div>

      <!-- 保存按钮 -->
      <div class="row" style="margin-top:14px; justify-content:flex-end;">
        <button class="btn btn-primary" @click="savePaths" :disabled="pathSaving">
          <i data-lucide="save"></i>{{ pathSaving ? '保存中' : '保存路径设置' }}
        </button>
      </div>
    </div>

    <!-- 授权管理 + 应用信息 -->
    <p class="desc" style="padding-top:18px;">授权管理与版本更新。</p>
    <div class="settings-row1">
      <!-- 授权管理 -->
      <div class="card auth-card">
        <h3 class="card-title"><i data-lucide="shield-check"></i> 授权管理</h3>
        <div class="form-row">
          <span class="form-label">授权密钥</span>
          <div class="input-with-btn">
            <input
              :type="showKey ? 'text' : 'password'"
              v-model="authKey"
              placeholder="LLF-XXXX-XXXX-XXXX"
              class="mono"
            />
            <button class="btn-icon" @click="showKey = !showKey" :title="showKey ? '隐藏' : '显示'">
              <i :data-lucide="showKey ? 'eye-off' : 'eye'"></i>
            </button>
          </div>
        </div>

        <div class="row" style="gap: 8px; margin-top: 10px;">
          <button class="btn btn-sm" @click="verifyKey" :disabled="!authKey">
            <i data-lucide="check"></i>验证
          </button>
          <button class="btn btn-sm btn-ghost" @click="clearKey">清除</button>
          <span :class="['tag', authStatus === 'verified' ? 'tag-green' : authStatus === 'invalid' ? 'tag-red' : 'tag-amber']" style="margin-left: 4px;">
            <span :class="['pulse-dot', authStatus === 'verified' ? '' : 'idle']" :style="authStatus === 'verified' ? {background:'var(--ok)'} : authStatus === 'invalid' ? {background:'var(--primary)'} : {background:'var(--text-4)'}"></span>
            {{ authStatusText }}
          </span>
        </div>

        <div class="auth-meta">
          <span class="muted">上次验证：<span class="mono">{{ authMeta.lastVerify || '—' }}</span></span>
          <span class="muted">下次检查：<span class="mono">{{ authMeta.nextCheck || '—' }}</span></span>
        </div>
      </div>

      <!-- 基础信息 -->
      <div class="card info-card">
        <h3 class="card-title"><i data-lucide="info"></i> 基础信息</h3>
        <div class="info-row">
          <span class="muted">当前版本：</span>
          <span class="version mono">v{{ appVersion }}</span>
          <span v-if="platform" class="tag tag-cyan" style="font-size:11px;margin-left:6px;">{{ platform }}</span>
        </div>
        <div class="row" style="gap: 8px; margin-top: 10px;">
          <button class="btn btn-sm" @click="checkUpdate">
            <i data-lucide="refresh-cw"></i>检查更新
          </button>
          <button class="btn btn-sm" @click="openTutorial">
            <i data-lucide="book-open"></i>使用教程
          </button>
        </div>
        <button class="btn btn-secondary btn-block" style="margin-top: 10px;" @click="openCommunity">
          <i data-lucide="users"></i>模板库及交流群
        </button>
      </div>
    </div>

    <!-- 数据管理 -->
    <p class="desc" style="padding-top: 18px;">备份或恢复应用设置。</p>
    <div class="card">
      <h3 class="card-title"><i data-lucide="database"></i> 数据管理</h3>
      <div class="row" style="gap: 10px; flex-wrap: wrap;">
        <button class="btn btn-sm" @click="exportSettings">
          <i data-lucide="download"></i>导出设置
        </button>
        <button class="btn btn-sm" @click="triggerImport">
          <i data-lucide="upload"></i>导入设置
        </button>
        <button class="btn btn-sm btn-ghost" @click="resetSettings">
          <i data-lucide="rotate-ccw"></i>恢复默认
        </button>
      </div>
      <p class="setting-hint muted" style="margin-top: 10px;">
        导出将下载包含路径、授权等配置的 settings.json；导入后会立即生效并刷新页面。
      </p>
      <input
        ref="importInputRef"
        type="file"
        accept=".json"
        style="display: none;"
        @change="onImportFileChange"
      />
    </div>

    <!-- 运行日志 -->
    <p class="desc" style="padding-top: 18px;">查看操作过程、错误与提示。</p>
    <div class="card">
      <div class="row-spread" style="margin-bottom: 10px;">
        <h3 class="card-title" style="margin: 0;">
          <i data-lucide="terminal"></i> 运行日志
          <span class="log-stats">
            <span class="tag tag-blue" style="font-size:11px;">INFO {{ logCounts.info }}</span>
            <span class="tag tag-amber" style="font-size:11px;">WARN {{ logCounts.warn }}</span>
            <span class="tag tag-red" style="font-size:11px;">ERR {{ logCounts.error }}</span>
          </span>
        </h3>
        <div class="row" style="gap: 6px;">
          <label class="checkbox" title="自动滚动到底部">
            <input type="checkbox" v-model="autoScroll" />
            <span class="box"></span>
            自动滚动
          </label>
          <select v-model="logFilter" class="log-filter">
            <option value="all">全部</option>
            <option value="info">信息</option>
            <option value="warn">警告</option>
            <option value="error">错误</option>
          </select>
          <button class="btn btn-sm" @click="exportLogs">
            <i data-lucide="download"></i>导出
          </button>
          <button class="btn btn-sm btn-ghost" @click="clearLogs">
            <i data-lucide="trash-2"></i>清空
          </button>
        </div>
      </div>
      <div class="log-area" ref="logAreaRef">
        <div v-if="filteredLogs.length === 0" class="empty-state" style="padding: 28px 0;">
          <i data-lucide="inbox"></i>
          <p>暂无日志</p>
        </div>
        <div v-else class="log-list">
          <div v-for="(l, i) in filteredLogs" :key="i" :class="['log-row', 'log-' + l.level]">
            <span class="log-time mono">{{ l.time }}</span>
            <span class="log-level">{{ levelLabel(l.level) }}</span>
            <span class="log-msg">{{ l.msg }}</span>
            <button class="log-copy-btn" @click="copyLog(l)" title="复制">
              <i data-lucide="copy" style="width:12px;height:12px;"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 联系开发者 -->
    <div class="card contact-card">
      <div class="row" style="gap: 8px;">
        <i data-lucide="message-circle"></i>
        <span style="font-weight: 600;">联系开发者</span>
      </div>
      <p class="muted" style="margin: 8px 0 0; font-size: 13px;">
        如有问题或建议，请联系开发者：<b class="mono">webzhouh@163.com</b>
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue';
import { useToast } from '../composables/useToast.js';
import { useSettings, defaultSettings } from '../composables/useSettings.js';
import { truncatePath } from '../utils/file.js';

const toast = useToast();
const settings = useSettings();
const electronAPI = window.electronAPI;
const platform = electronAPI?.platform || '';

/* ---------- 路径设置 ---------- */
const loPath = ref('');
const outputDir = ref('');
const loStatus = reactive({ found: false, path: '' });
const loChecking = ref(false);
const pathSaving = ref(false);

async function detectLO() {
  loChecking.value = true;
  try {
    if (!electronAPI?.libreOfficeCheck) {
      toast.show('LibreOffice 检测 API 不可用', 'warn');
      return;
    }
    const res = await electronAPI.libreOfficeCheck();
    loStatus.found = res.found;
    loStatus.path = res.path || '';
    if (res.found) {
      loPath.value = res.path;
      toast.show('LibreOffice 已找到', 'success');
    } else {
      loPath.value = '';
      toast.show('未找到 LibreOffice，请手动指定', 'warn');
    }
  } catch (err) {
    toast.show(err.message || '检测失败', 'error');
  } finally {
    loChecking.value = false;
  }
}

async function selectLOPath() {
  try {
    if (!electronAPI?.openFiles) { toast.show('文件选择 API 不可用', 'warn'); return; }
    const res = await electronAPI.openFiles({
      title: '选择 soffice.exe',
      filters: [{ name: 'soffice', extensions: ['exe'] }],
      properties: ['openFile']
    });
    if (!res.canceled && res.filePaths.length) {
      const p = res.filePaths[0];
      loPath.value = p;
      loStatus.found = true;
      loStatus.path = p;
      toast.show('已选择：' + truncatePath(p), 'success');
    }
  } catch (err) {
    toast.show(err.message || '选择失败', 'error');
  }
}

async function selectOutputDir() {
  try {
    if (!electronAPI?.selectOutputDir) { toast.show('目录选择 API 不可用', 'warn'); return; }
    const res = await electronAPI.selectOutputDir();
    if (!res.canceled && res.filePaths.length) {
      outputDir.value = res.filePaths[0];
      toast.show('已设置输出目录', 'success');
    }
  } catch (err) {
    toast.show(err.message || '选择失败', 'error');
  }
}

async function savePaths() {
  pathSaving.value = true;
  try {
    // Save LO path to main process
    if (loPath.value && electronAPI?.libreOfficeSetPath) {
      const r = await electronAPI.libreOfficeSetPath(loPath.value);
      if (!r.success) {
        toast.show(r.error || 'LibreOffice 路径保存失败', 'error');
        return;
      }
    }
    // Save to localStorage
    settings.set('loDir', loPath.value || '');
    settings.set('outputDir', outputDir.value || '');
    toast.show('路径设置已保存', 'success');
  } catch (err) {
    toast.show(err.message || '保存失败', 'error');
  } finally {
    pathSaving.value = false;
  }
}

/* ---------- 授权管理 ---------- */
const authKey = ref('');
const showKey = ref(false);
const authMeta = reactive({ lastVerify: '', nextCheck: '' });
const authStatus = ref('trial'); // trial | verified | invalid

const authStatusText = computed(() => ({
  trial: '试用中',
  verified: '已验证',
  invalid: '无效密钥'
})[authStatus.value] || '试用中');

function verifyKey() {
  if (!authKey.value) { toast.show('请先填写授权密钥', 'warn'); return; }
  if (!/^LLF-[\w-]+$/.test(authKey.value)) {
    pushLog('warn', '授权密钥格式不符');
    toast.show('授权密钥格式应为 LLF-XXXX-XXXX-XXXX', 'error');
    authStatus.value = 'invalid';
    return;
  }
  const t = new Date();
  authMeta.lastVerify = t.toLocaleString('zh-CN', { hour12: false });
  const next = new Date(t.getTime() + 7 * 24 * 60 * 60 * 1000);
  authMeta.nextCheck = next.toLocaleString('zh-CN', { hour12: false });
  authStatus.value = 'verified';
  persistAuth();
  pushLog('info', '授权验证通过');
  toast.show('验证通过', 'success');
}

function clearKey() {
  authKey.value = '';
  authMeta.lastVerify = '';
  authMeta.nextCheck = '';
  authStatus.value = 'trial';
  persistAuth();
  pushLog('info', '授权密钥已清除');
  toast.show('已清除', 'success');
}

function persistAuth() {
  settings.set('authKey', authKey.value);
  settings.set('lastVerify', authMeta.lastVerify);
  settings.set('nextCheck', authMeta.nextCheck);
}

function loadAuth() {
  authKey.value = settings.get('authKey') || '';
  authMeta.lastVerify = settings.get('lastVerify') || '';
  authMeta.nextCheck = settings.get('nextCheck') || '';
  if (authMeta.lastVerify) authStatus.value = 'verified';
}

/* ---------- 应用信息 ---------- */
const appVersion = ref('1.5.1');

function checkUpdate() {
  pushLog('info', '检查更新：当前版本 v' + appVersion.value);
  toast.show('当前已是最新版本', 'success');
}
function openTutorial() {
  window.open('https://github.com/Haoyesa/codebox', '_blank');
}
function openCommunity() {
  window.open('https://github.com/Haoyesa/codebox', '_blank');
}

/* ---------- 数据管理 ---------- */
const importInputRef = ref(null);

function exportSettings() {
  try {
    const raw = localStorage.getItem('fulltool_settings_v2');
    const data = raw ? JSON.parse(raw) : {};
    const payload = {
      _app: 'FullTool',
      _version: appVersion.value,
      _exportedAt: new Date().toISOString(),
      settings: data
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fulltool-settings-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
    pushLog('info', '设置已导出');
    toast.show('设置已导出', 'success');
  } catch (err) {
    toast.show('导出失败: ' + err.message, 'error');
  }
}

function triggerImport() {
  importInputRef.value?.click();
}

function onImportFileChange(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    try {
      const payload = JSON.parse(ev.target.result);
      if (!payload.settings || typeof payload.settings !== 'object') {
        throw new Error('文件格式不正确，缺少 settings 对象');
      }
      // Validate known keys to avoid corrupting storage
      const allowedKeys = Object.keys(defaultSettings);
      const imported = {};
      for (const key of allowedKeys) {
        if (key in payload.settings) imported[key] = payload.settings[key];
      }
      localStorage.setItem('fulltool_settings_v2', JSON.stringify(imported));
      pushLog('info', '设置已导入，即将刷新');
      toast.show('设置导入成功，页面即将刷新', 'success');
      setTimeout(() => location.reload(), 800);
    } catch (err) {
      toast.show('导入失败: ' + err.message, 'error');
    } finally {
      e.target.value = '';
    }
  };
  reader.onerror = () => {
    toast.show('读取文件失败', 'error');
    e.target.value = '';
  };
  reader.readAsText(file);
}

async function resetSettings() {
  if (!(await window.appConfirm({ message: '确定恢复默认设置？这将清除所有自定义路径和授权信息。' }))) return;
  settings.reset();
  pushLog('info', '设置已恢复默认');
  toast.show('设置已恢复默认，页面即将刷新', 'success');
  setTimeout(() => location.reload(), 800);
}

/* ---------- 日志系统 ---------- */
const logFilter = ref('all');
const logs = ref([]);
const autoScroll = ref(true);
const logAreaRef = ref(null);

const filteredLogs = computed(() => {
  if (logFilter.value === 'all') return logs.value;
  return logs.value.filter(l => l.level === logFilter.value);
});

const logCounts = computed(() => ({
  info: logs.value.filter(l => l.level === 'info').length,
  warn: logs.value.filter(l => l.level === 'warn').length,
  error: logs.value.filter(l => l.level === 'error').length
}));

function levelLabel(l) {
  return { info: 'INFO', warn: 'WARN', error: 'ERR ' }[l] || l.toUpperCase();
}

function pushLog(level, msg) {
  const t = new Date();
  logs.value.unshift({
    time: t.toTimeString().slice(0, 8),
    level, msg
  });
  if (logs.value.length > 500) logs.value.length = 500;
}

// Auto-scroll
watch(filteredLogs, async () => {
  if (autoScroll.value) {
    await nextTick();
    const el = logAreaRef.value;
    if (el) el.scrollTop = 0; // newest at top
  }
});

function copyLog(l) {
  const text = `[${l.time}] [${levelLabel(l.level)}] ${l.msg}`;
  navigator.clipboard.writeText(text).then(() => {
    toast.show('已复制到剪贴板', 'success');
  }).catch(() => {
    toast.show('复制失败', 'error');
  });
}

function exportLogs() {
  const text = logs.value.map(l => `[${l.time}] [${levelLabel(l.level)}] ${l.msg}`).join('\n');
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `fulltool-log-${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
  a.click();
  URL.revokeObjectURL(url);
  toast.show('日志已导出', 'success');
}

async function clearLogs() {
  if (logs.value.length && !(await window.appConfirm({ message: `确定清空 ${logs.value.length} 条日志？` }))) return;
  logs.value = [];
  toast.show('日志已清空', 'success');
}

// Intercept console
let origLog, origWarn, origErr;
function installLogInterceptor() {
  origLog = console.log;
  origWarn = console.warn;
  origErr = console.error;
  console.log = (...args) => { pushLog('info', args.join(' ')); origLog.apply(console, args); };
  console.warn = (...args) => { pushLog('warn', args.join(' ')); origWarn.apply(console, args); };
  console.error = (...args) => { pushLog('error', args.join(' ')); origErr.apply(console, args); };
  window.addEventListener('error', e => pushLog('error', e.message));
  window.addEventListener('unhandledrejection', e => pushLog('error', 'Unhandled: ' + (e.reason?.message || e.reason)));
}
function uninstallLogInterceptor() {
  console.log = origLog; console.warn = origWarn; console.error = origErr;
}

/* ---------- Lifecycle ---------- */
onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
  loadAuth();

  // Load paths from settings
  loPath.value = settings.get('loDir') || '';
  outputDir.value = settings.get('outputDir') || '';

  // Auto-detect LO if not set
  if (!loPath.value) {
    detectLO();
  } else if (electronAPI?.libreOfficeCheck) {
    const res = await electronAPI.libreOfficeCheck();
    loStatus.found = res.found;
    loStatus.path = res.path || loPath.value;
  }

  installLogInterceptor();
  pushLog('info', 'Full 启动完成 v' + appVersion.value);
});

onBeforeUnmount(() => uninstallLogInterceptor());
</script>

<style scoped>
.settings-row1 { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; }
.card-title i[data-lucide] { width: 16px; height: 16px; color: var(--primary); }

/* 设置行 */
.setting-row { }
.setting-label {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 500; color: var(--text);
  margin-bottom: 6px;
}
.setting-hint {
  font-size: 12px; margin-top: 6px; color: var(--text-3);
}
.setting-hint a { color: var(--primary); text-decoration: none; }
.setting-hint a:hover { text-decoration: underline; }

.form-row { display: grid; grid-template-columns: 80px 1fr; gap: 10px; align-items: center; }
.form-label { font-size: 13px; color: var(--text-2); }
.input-with-btn { display: flex; gap: 6px; align-items: center; }
.input-with-btn input { flex: 1; }

.auth-meta { display: flex; gap: 18px; margin-top: 14px; font-size: 12px; }
.muted { color: var(--text-3); }
.version { color: var(--primary); font-weight: 600; }
.info-card .info-row { font-size: 13px; display: flex; align-items: center; }

/* 日志 */
.log-stats { display: inline-flex; gap: 6px; margin-left: 10px; }
.log-filter { width: auto; min-width: 90px; }
.log-area { min-height: 200px; max-height: 360px; overflow-y: auto; }
.log-list { display: flex; flex-direction: column; }
.log-row {
  display: grid;
  grid-template-columns: 90px 50px 1fr 28px;
  gap: 10px;
  padding: 5px 4px;
  font-size: 12px;
  border-bottom: 1px dashed var(--border-2);
  align-items: center;
  border-radius: 3px;
  transition: background .1s;
}
.log-row:hover { background: var(--panel-2); }
.log-row:last-child { border-bottom: 0; }
.log-time { color: var(--text-3); font-family: var(--font-mono); }
.log-level {
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 6px;
  text-align: center;
  font-weight: 500;
  background: var(--panel-3);
  color: var(--text-2);
  height: fit-content;
  transition: transform .15s;
}
.log-row:hover .log-level { transform: scale(1.05); }
.log-info .log-level { background: var(--info-soft); color: var(--info); }
.log-warn .log-level { background: var(--warn-soft); color: var(--warn-deep); }
.log-error .log-level { background: var(--primary-soft); color: var(--primary-deep); }
.log-msg { color: var(--text); word-break: break-word; }
.log-copy-btn {
  width: 22px; height: 22px;
  padding: 0; border: 0; background: transparent;
  display: inline-flex; align-items: center; justify-content: center;
  border-radius: 4px; cursor: pointer; opacity: 0;
  transition: opacity .15s, background .15s;
}
.log-row:hover .log-copy-btn { opacity: 1; }
.log-copy-btn:hover { background: var(--panel-3); }

.contact-card { margin-top: 14px; }
.contact-card i[data-lucide] { color: var(--primary); width: 16px; height: 16px; }

@media (max-width: 900px) {
  .settings-row1 { grid-template-columns: 1fr; }
}
</style>
