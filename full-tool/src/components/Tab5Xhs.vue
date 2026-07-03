<template>
  <section :class="$attrs.class">
    <p class="desc">输入商品链接，自动抓取主图与详情图并保存到文件夹。</p>

    <div class="xhs-layout">
      <div class="card xhs-side">
        <div class="form-block">
          <label class="form-label">商品链接（每行一个）</label>
          <textarea
            v-model="urlText"
            placeholder="https://www.xiaohongshu.com/goods-detail/..."
            rows="6"
            class="mono"
          ></textarea>
        </div>

        <div class="form-block">
          <div class="row" style="gap: 8px;">
            <button class="btn btn-sm" @click="pickOutput">
              <i data-lucide="folder-open"></i>选择输出目录
            </button>
            <span class="muted path" :title="outputDir" style="font-size: 12px;">
              {{ outputDir || '未设置' }}
            </span>
          </div>
        </div>

        <div class="action-row">
          <button class="btn btn-primary btn-lg" :disabled="!canStart || state.isRunning" @click="startDownload">
            <i data-lucide="download"></i>
            {{ state.isRunning ? '下载中…' : '开始下载' }}
          </button>
          <button class="btn btn-warn" :disabled="!state.isRunning" @click="stopDownload">停止</button>
          <span class="muted" style="margin-left: 6px;">
            <span class="pulse-dot" :class="state.dotClass"></span>
            <span style="margin-left: 6px;">{{ state.statusText }}</span>
          </span>
        </div>

        <div class="task-block">
          <h4 class="task-title">任务列表</h4>
          <div v-if="tasks.length === 0" class="task-empty">暂无任务</div>
          <div v-else class="task-list">
            <div v-for="t in tasks" :key="t.id" class="task-item">
              <div class="task-row1">
                <span class="task-status" :class="'st-' + t.status">{{ statusLabel(t.status) }}</span>
                <span class="task-name" :title="t.url">{{ t.title || t.url }}</span>
              </div>
              <div v-if="t.status === 'running' || t.status === 'done'" class="progress-bar" style="margin-top: 4px;">
                <div class="fill" :style="{ width: t.percent + '%' }"></div>
              </div>
              <div v-if="t.message" class="task-msg">{{ t.message }}</div>
              <div v-if="t.status === 'error'" style="margin-top: 4px;">
                <button class="btn btn-sm" @click="retryTask(t)">重试</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card xhs-browser">
        <div class="browser-bar">
          <span class="browser-status mono">内置浏览器</span>
          <span class="muted" style="margin-left: 8px;">{{ state.isRunning ? '抓取中' : '待机' }}</span>
          <div class="row" style="margin-left: auto; gap: 6px;">
            <button class="btn-icon" @click="browserBack" title="后退"><i data-lucide="arrow-left"></i></button>
            <button class="btn-icon" @click="browserRefresh" title="刷新"><i data-lucide="rotate-cw"></i></button>
            <button class="btn-icon" @click="browserHome" title="首页"><i data-lucide="home"></i></button>
            <button class="btn btn-sm" @click="manualParse" title="重新注入解析脚本">手动解析</button>
          </div>
        </div>
        <div class="browser-frame">
          <webview
            v-if="showWebview"
            ref="webviewRef"
            :src="browserUrl"
            class="webview-el"
            partition="persist:xhs"
            allowpopups
          ></webview>
          <div v-else class="browser-placeholder">
            <i data-lucide="globe" style="width: 32px; height: 32px; opacity: 0.4;"></i>
            <p>任务开始后会在此展示预览</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue';
import { useToast } from '../composables/useToast.js';

const toast = useToast();
const urlText = ref('');
const outputDir = ref('');
const tasks = ref([]); // {id, url, title, status, percent, message}
let taskId = 1;

const state = reactive({
  isRunning: false,
  statusText: '待命',
  dotClass: 'idle'
});

const showWebview = ref(false);
const browserUrl = ref('https://www.xiaohongshu.com');
const webviewRef = ref(null);

const canStart = computed(() => {
  const urls = parseUrls();
  return urls.length > 0 && outputDir.value;
});

function parseUrls() {
  return urlText.value.split(/\r?\n/).map(s => s.trim()).filter(Boolean);
}

function statusLabel(s) {
  return { pending: '等待', running: '进行', done: '完成', error: '失败', skipped: '跳过' }[s] || s;
}

async function pickOutput() {
  if (!window.electronAPI) {
    toast.show('请在 Electron 版本中使用', 'warn');
    return;
  }
  const r = await window.electronAPI.selectOutputDir();
  if (r.canceled || !r.filePaths.length) return;
  outputDir.value = r.filePaths[0];
}

function parseXhsUrl(url) {
  // https://www.xiaohongshu.com/goods-detail/{id}
  const m = url.match(/goods-detail\/([\w-]+)/);
  return m ? m[1] : null;
}

let abortFlag = false;
async function startDownload() {
  if (!canStart.value) {
    toast.show('请补全链接和输出目录', 'warn');
    return;
  }
  const urls = parseUrls();
  tasks.value = urls.map(url => ({
    id: taskId++, url, status: 'pending', percent: 0, message: ''
  }));
  abortFlag = false;
  state.isRunning = true;
  state.statusText = '下载中…';
  state.dotClass = '';

  // 启动预览
  showWebview.value = true;
  await nextTick();

  for (const t of tasks.value) {
    if (abortFlag) break;
    await scrapeSingleTask(t);
  }

  state.isRunning = false;
  state.statusText = abortFlag ? '已停止' : '完成';
  state.dotClass = abortFlag ? 'warn' : '';
  toast.show(state.statusText, abortFlag ? 'warn' : 'success');
}

function stopDownload() {
  abortFlag = true;
  state.statusText = '正在停止…';
}

// 核心抓取+下载逻辑，处理单个任务
async function scrapeSingleTask(t) {
  t.status = 'running';
  t.message = '抓取商品信息…';
  try {
    const goodId = parseXhsUrl(t.url);
    if (!goodId) {
      t.status = 'error';
      t.message = '无法解析商品 ID';
      return;
    }

    // 调用 webview 内部页面拿到 cookies（让 webview 访问商品页）
    const meta = await fetchGoodsFromWebview(webviewRef.value, t.url);
    if (!meta) {
      // 回退: 尝试直接 fetch
      t.message = '直连抓取（无 Cookie）…';
      const direct = await directFetch(t.url);
      if (!direct) {
        t.status = 'error';
        t.message = '访问被拒绝，小红书需要登录，请在 webview 中登录后重试';
        return;
      }
      if (!direct.title) {
        t.status = 'error';
        t.message = '未找到商品标题，请确保链接正确';
        return;
      }
      if (!direct.images || direct.images.length === 0) {
        t.status = 'error';
        t.message = '未找到商品图片，请检查链接';
        return;
      }
      Object.assign(t, { title: direct.title, images: direct.images });
    } else {
      if (!meta.title) {
        t.status = 'error';
        t.message = '未找到商品标题，请确保链接正确';
        return;
      }
      if (!meta.images || meta.images.length === 0) {
        t.status = 'error';
        t.message = '未找到商品图片，请检查链接';
        return;
      }
      Object.assign(t, { title: meta.title, images: meta.images });
    }

    t.message = `共 ${t.images.length} 张图片`;

    // 下载图片
    for (let i = 0; i < t.images.length; i++) {
      if (abortFlag) break;
      const url = t.images[i];
      try {
        const buf = await fetchAsBuffer(url);
        if (!buf) { t.message = `第 ${i + 1} 张下载失败`; continue; }
        const ext = (url.match(/\.(png|jpg|jpeg|webp)/i)?.[1] || 'jpg').toLowerCase();
        const safeTitle = (t.title || goodId).replace(/[\\/:*?"<>|]/g, '_').slice(0, 60);
        const fileName = `${safeTitle}_${String(i + 1).padStart(2, '0')}.${ext}`;
        const fullPath = outputDir.value.replace(/[\\/]+$/, '') + '/' + fileName;
        await window.electronAPI.writeFile(fullPath, buf);
      } catch (e) {
        toast.show('写入文件失败: ' + e.message, 'error');
      }
      t.percent = Math.round(((i + 1) / t.images.length) * 100);
    }

    t.status = abortFlag ? 'skipped' : 'done';
    t.percent = 100;
    t.message = abortFlag ? '已停止' : `已保存 ${t.images.length} 张`;
  } catch (e) {
    t.status = 'error';
    t.message = e.message;
  }
}

// 重试单个失败任务
async function retryTask(t) {
  if (state.isRunning) {
    toast.show('请等待当前任务完成后再重试', 'warn');
    return;
  }
  abortFlag = false;
  state.isRunning = true;
  state.statusText = '重试中…';
  state.dotClass = '';
  showWebview.value = true;
  await nextTick();
  await scrapeSingleTask(t);
  state.isRunning = false;
  state.statusText = abortFlag ? '已停止' : '完成';
  state.dotClass = abortFlag ? 'warn' : '';
  toast.show(state.statusText, abortFlag ? 'warn' : 'success');
}

// 尝试从 webview 内部获取商品数据
async function fetchGoodsFromWebview(wv, url) {
  if (!wv) return null;
  try {
    // 让 webview 加载目标页
    wv.src = url;
    // 等待页面加载完成
    await new Promise((resolve) => {
      const onLoad = () => { wv.removeEventListener('did-finish-load', onLoad); resolve(); };
      wv.addEventListener('did-finish-load', onLoad);
      setTimeout(resolve, 8000);
    });
    // 注入脚本抓数据
    const result = await wv.executeJavaScript(`
      (function() {
        try {
          // 多选择器逐步尝试标题
          let title = '';
          const titleSelectors = ['h1', '.title', '.goods-title', '.main-title'];
          for (const sel of titleSelectors) {
            const el = document.querySelector(sel);
            if (el && el.innerText && el.innerText.trim()) {
              title = el.innerText.trim();
              break;
            }
          }
          if (!title) title = document.title || '';

          // 多选择器逐步尝试图片
          let imgs = [];
          const imgSelectors = ['.picture img', 'img', '[data-src]', '[src]'];
          for (const sel of imgSelectors) {
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
              const srcs = Array.from(els).map(el => {
                if (sel === '[data-src]') return el.dataset?.src || el.getAttribute('data-src');
                if (sel === '[src]') return el.getAttribute('src');
                return el.src || el.dataset?.src;
              }).filter(s => s && s.startsWith('http'));
              if (srcs.length > 0) {
                imgs = srcs;
                break;
              }
            }
          }

          return JSON.stringify({ title, images: imgs });
        } catch (e) { return 'null'; }
      })();
    `);
    if (!result || result === 'null') return null;
    return JSON.parse(result);
  } catch (_) { return null; }
}

// 直连 fetch (大概率 403/401,作为兜底)
async function directFetch(url) {
  try {
    const res = await fetch(url, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' }
    });
    if (!res.ok) return null;
    const html = await res.text();
    const titleMatch = html.match(/<title>([^<]+)<\/title>/);
    const imgs = Array.from(html.matchAll(/(?:src|data-src)="(https?:\/\/[^"]+\.(?:png|jpg|jpeg|webp)[^"]*)"/gi))
      .map(m => m[1])
      .filter(Boolean);
    return { title: titleMatch?.[1] || '商品', images: imgs };
  } catch (_) { return null; }
}

async function fetchAsBuffer(url) {
  try {
    const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
    if (!res.ok) return null;
    const ab = await res.arrayBuffer();
    return ab;
  } catch (_) { return null; }
}

function browserBack() {
  try { webviewRef.value?.goBack(); } catch (_) {}
}
function browserRefresh() {
  try { webviewRef.value?.reload(); } catch (_) {}
}
function browserHome() {
  browserUrl.value = 'https://www.xiaohongshu.com';
  showWebview.value = true;
  nextTick(() => webviewRef.value?.setAttribute('src', browserUrl.value));
}

// 手动解析：用户点击按钮时重新注入脚本解析当前 webview 页面
const manualParse = async () => {
  const wv = webviewRef.value;
  if (!wv) {
    toast.show('Webview 未初始化', 'warn');
    return;
  }
  try {
    const result = await wv.executeJavaScript(`
      (function() {
        try {
          let title = '';
          const titleSelectors = ['h1', '.title', '.goods-title', '.main-title'];
          for (const sel of titleSelectors) {
            const el = document.querySelector(sel);
            if (el && el.innerText && el.innerText.trim()) {
              title = el.innerText.trim();
              break;
            }
          }
          if (!title) title = document.title || '';

          let imgs = [];
          const imgSelectors = ['.picture img', 'img', '[data-src]', '[src]'];
          for (const sel of imgSelectors) {
            const els = document.querySelectorAll(sel);
            if (els.length > 0) {
              const srcs = Array.from(els).map(el => {
                if (sel === '[data-src]') return el.dataset?.src || el.getAttribute('data-src');
                if (sel === '[src]') return el.getAttribute('src');
                return el.src || el.dataset?.src;
              }).filter(s => s && s.startsWith('http'));
              if (srcs.length > 0) {
                imgs = srcs;
                break;
              }
            }
          }

          return JSON.stringify({ title, images: imgs });
        } catch (e) { return 'null'; }
      })();
    `);
    if (!result || result === 'null') {
      toast.show('解析失败，页面可能未加载完成', 'warn');
      return;
    }
    const data = JSON.parse(result);
    if (!data.title && data.images.length === 0) {
      toast.show('解析失败：未找到商品内容', 'warn');
    } else if (!data.title) {
      toast.show('未找到商品标题，但找到 ' + data.images.length + ' 张图片', 'warn');
    } else {
      toast.show('解析成功: ' + data.title + ' (' + data.images.length + ' 张图片)', 'success');
    }
  } catch (e) {
    toast.show('解析出错: ' + e.message, 'error');
  }
};

onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
});
</script>

<style scoped>
.xhs-layout { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: stretch; }
.xhs-side, .xhs-browser { display: flex; flex-direction: column; min-height: 560px; }
.form-block { margin-bottom: 14px; }
.form-label { display: block; font-size: 13px; color: var(--text-2); margin-bottom: 6px; }
.muted { color: var(--text-3); }
.path { word-break: break-all; flex: 1; }
.action-row { display: flex; align-items: center; gap: 10px; margin: 6px 0 14px; flex-wrap: wrap; }

.task-block { flex: 1; display: flex; flex-direction: column; min-height: 0; }
.task-title { font-size: 13px; font-weight: 600; margin: 0 0 8px; }
.task-empty {
  padding: 32px 20px !important; border: 1.5px dashed var(--border-strong); border-radius: var(--radius);
  color: var(--text-3); font-size: 13px; text-align: center;
  transition: border-color .2s, background .2s;
  flex: 1;
}
.task-empty:hover { border-color: var(--neon-cyan); background: var(--neon-cyan-soft); }
.task-list { display: flex; flex-direction: column; gap: 6px; overflow-y: auto; max-height: 100%; }
.task-item {
  padding: 8px 10px; background: var(--panel-2);
  border: 1px solid var(--border); border-radius: 8px;
  transition: border-color .15s, box-shadow .15s, transform .15s;
}
.task-item:hover { border-color: var(--border-strong); box-shadow: var(--shadow-sm); transform: translateX(2px); }
.task-row1 { display: flex; align-items: center; gap: 8px; }
.task-status {
  font-family: var(--font-mono);
  font-size: 10px; padding: 2px 7px; border-radius: 6px;
  background: var(--panel-3); color: var(--text-2);
  font-weight: 500;
  transition: transform .15s;
}
.task-item:hover .task-status { transform: scale(1.05); }
.task-status.st-running { background: var(--neon-cyan-soft); color: #0369a1; }
.task-status.st-done { background: var(--ok-soft); color: var(--ok-deep); }
.task-status.st-error { background: var(--primary-soft); color: var(--primary-deep); }
.task-status.st-skipped { background: var(--warn-soft); color: var(--warn-deep); }
.task-name { font-size: 12px; color: var(--text); flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.task-msg { font-size: 11px; color: var(--text-3); margin-top: 4px; font-family: var(--font-mono); }

.browser-bar {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
  background: linear-gradient(180deg, var(--panel-2) 0%, var(--panel-3) 100%);
}
.browser-status {
  font-size: 12px; color: var(--text-2);
  font-family: var(--font-mono);
}
.browser-frame {
  flex: 1; position: relative; background: var(--panel-2);
  border-radius: 0 0 var(--radius) var(--radius);
  overflow: hidden;
}
.webview-el { width: 100%; height: 100%; min-height: 480px; border: 0; }
.browser-placeholder {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: var(--text-3); gap: 10px;
}
</style>