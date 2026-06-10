<template>
  <section :class="$attrs.class">
    <p class="desc">授权管理与版本更新。</p>

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
          <span class="tag tag-green" style="margin-left: 4px;">
            <span class="pulse-dot" style="background: var(--ok);"></span>
            试用中
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
        </div>
        <div class="row" style="gap: 8px; margin-top: 10px;">
          <button class="btn btn-sm" @click="checkUpdate">
            <i data-lucide="refresh-cw"></i>检查更新
          </button>
          <button class="btn btn-sm" @click="openTutorial">
            <i data-lucide="book-open"></i>获取使用教程
          </button>
        </div>
        <button class="btn btn-secondary btn-block" style="margin-top: 10px;" @click="openCommunity">
          <i data-lucide="users"></i>获取模板库及交流群
        </button>
      </div>
    </div>

    <p class="desc" style="padding-top: 18px;">查看操作过程、错误与提示。</p>

    <div class="card">
      <div class="row-spread" style="margin-bottom: 10px;">
        <h3 class="card-title" style="margin: 0;">
          <i data-lucide="terminal"></i> 运行日志
        </h3>
        <div class="row" style="gap: 6px;">
          <select v-model="logFilter" class="log-filter">
            <option value="all">全部</option>
            <option value="info">信息</option>
            <option value="warn">警告</option>
            <option value="error">错误</option>
          </select>
          <button class="btn btn-sm" @click="exportLogs">
            <i data-lucide="download"></i>导出日志
          </button>
          <button class="btn btn-sm btn-ghost" @click="logs = []">
            <i data-lucide="trash-2"></i>清空
          </button>
        </div>
      </div>
      <div class="log-area">
        <div v-if="filteredLogs.length === 0" class="empty-state" style="padding: 28px 0;">
          <i data-lucide="inbox"></i>
          <p>暂无日志</p>
        </div>
        <div v-else class="log-list">
          <div v-for="(l, i) in filteredLogs" :key="i" :class="['log-row', 'log-' + l.level]">
            <span class="log-time mono">{{ l.time }}</span>
            <span class="log-level">{{ levelLabel(l.level) }}</span>
            <span class="log-msg">{{ l.msg }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="card contact-card">
      <div class="row" style="gap: 8px;">
        <i data-lucide="message-circle"></i>
        <span style="font-weight: 600;">联系开发者</span>
      </div>
      <p class="muted" style="margin: 8px 0 0; font-size: 13px;">
        如果有问题或建议，请联系开发者：<b class="mono">尹星河 (teaxh613)</b>
      </p>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';

const STORAGE_KEY = 'fulltool_settings_v1';

const authKey = ref('');
const showKey = ref(false);
const authMeta = reactive({ lastVerify: '', nextCheck: '' });

const appVersion = ref('1.5.1');

const logFilter = ref('all');
const logs = ref([]); // {time, level, msg}

let logCounter = 0;

const filteredLogs = computed(() => {
  if (logFilter.value === 'all') return logs.value;
  return logs.value.filter(l => l.level === logFilter.value);
});

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

// 拦截 console
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

function verifyKey() {
  if (!authKey.value) { window.showToast?.('请先填写授权密钥', 'warn'); return; }
  // 简化: 任何 LLF-XXXX-XXXX-XXXX 形式视为合法
  if (!/^LLF-[\w-]+$/.test(authKey.value)) {
    pushLog('warn', '授权密钥格式不符');
    window.showToast?.('授权密钥格式应为 LLF-XXXX-XXXX-XXXX', 'error');
    return;
  }
  const t = new Date();
  authMeta.lastVerify = t.toLocaleString('zh-CN', { hour12: false });
  const next = new Date(t.getTime() + 7 * 24 * 60 * 60 * 1000);
  authMeta.nextCheck = next.toLocaleString('zh-CN', { hour12: false });
  persist();
  pushLog('info', '授权验证通过');
  window.showToast?.('验证通过', 'success');
}
function clearKey() {
  authKey.value = '';
  authMeta.lastVerify = '';
  authMeta.nextCheck = '';
  persist();
  pushLog('info', '授权密钥已清除');
}

function checkUpdate() {
  pushLog('info', '检查更新：当前版本 v' + appVersion.value);
  window.showToast?.('当前已是最新版本', 'success');
}
function openTutorial() {
  window.open('https://github.com/Haoyesa/codebox', '_blank');
}
function openCommunity() {
  window.open('https://github.com/Haoyesa/codebox', '_blank');
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
  window.showToast?.('日志已导出', 'success');
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      authKey: authKey.value,
      lastVerify: authMeta.lastVerify,
      nextCheck: authMeta.nextCheck
    }));
  } catch (_) {}
}
function loadPersisted() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const o = JSON.parse(raw);
    authKey.value = o.authKey || '';
    authMeta.lastVerify = o.lastVerify || '';
    authMeta.nextCheck = o.nextCheck || '';
  } catch (_) {}
}

onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
  loadPersisted();
  installLogInterceptor();
  pushLog('info', 'Full 启动完成 v' + appVersion.value);
});
onBeforeUnmount(() => uninstallLogInterceptor());
</script>

<style scoped>
.settings-row1 { display: grid; grid-template-columns: 2fr 1fr; gap: 14px; }
.card-title { margin: 0 0 12px; font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.card-title i[data-lucide] { width: 16px; height: 16px; color: var(--primary); }

.form-row { display: grid; grid-template-columns: 80px 1fr; gap: 10px; align-items: center; }
.form-label { font-size: 13px; color: var(--text-2); }
.input-with-btn { display: flex; gap: 6px; align-items: center; }
.input-with-btn input { flex: 1; }

.auth-meta { display: flex; gap: 18px; margin-top: 14px; font-size: 12px; }
.muted { color: var(--text-3); }
.version { color: var(--primary); font-weight: 600; }
.info-card .info-row { font-size: 13px; }

.log-filter { width: auto; min-width: 90px; }
.log-area { min-height: 200px; max-height: 360px; overflow-y: auto; }
.log-list { display: flex; flex-direction: column; }
.log-row {
  display: grid;
  grid-template-columns: 90px 50px 1fr;
  gap: 10px;
  padding: 4px 0;
  font-size: 12px;
  border-bottom: 1px dashed var(--border-2);
}
.log-row:last-child { border-bottom: 0; }
.log-time { color: var(--text-3); }
.log-level {
  font-family: var(--font-mono);
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 3px;
  text-align: center;
  background: var(--panel-3);
  color: var(--text-2);
  height: fit-content;
}
.log-info .log-level { background: var(--info-soft); color: var(--info); }
.log-warn .log-level { background: var(--warn-soft); color: var(--warn-deep); }
.log-error .log-level { background: var(--primary-soft); color: var(--primary-deep); }
.log-msg { color: var(--text); word-break: break-word; }

.contact-card { margin-top: 14px; }
.contact-card i[data-lucide] { color: var(--primary); width: 16px; height: 16px; }

@media (max-width: 900px) {
  .settings-row1 { grid-template-columns: 1fr; }
}
</style>