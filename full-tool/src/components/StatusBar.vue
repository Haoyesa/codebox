<template>
  <footer class="status-bar">
    <div class="status-left">
      <span class="status-item" title="当前版本">
        <i data-lucide="git-branch"></i>
        <span>v{{ appVersion }}</span>
      </span>
      <span v-if="updateInfo.hasUpdate" class="status-item update-badge" @click="openReleasePage">
        <i data-lucide="arrow-up-circle"></i>
        <span>发现新版本 v{{ updateInfo.latestVersion }}</span>
      </span>
      <span v-else-if="updateInfo.checked" class="status-item muted">
        <i data-lucide="check-circle-2"></i>
        <span>已是最新</span>
      </span>
    </div>
    <div class="status-right">
      <button
        class="theme-toggle"
        :title="isDark ? '切换亮色模式' : '切换暗色模式'"
        @click="toggleTheme"
      >
        <i v-if="isDark" data-lucide="sun"></i>
        <i v-else data-lucide="moon"></i>
      </button>
      <span class="status-item" title="内存占用">
        <i data-lucide="cpu"></i>
        <span>{{ memoryText }}</span>
      </span>
      <span class="status-item" title="当前 Tab">
        <i data-lucide="layout"></i>
        <span>{{ currentTabLabel }}</span>
      </span>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';

const props = defineProps({
  currentTab: { type: String, default: 'p1' }
});

const tabLabels = {
  p1: '文档导出', p2: '场景排版', p3: '拼图排版',
  p4: '飞书上传', p5: '小红书抓图', p6: '爆款素材',
  p7: 'HighMD', p8: '设置'
};

const appVersion = '1.0.0';
const currentTabLabel = computed(() => tabLabels[props.currentTab] || '-');

// 暗色模式
const isDark = ref(false);
function toggleTheme() {
  isDark.value = !isDark.value;
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light');
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
}

// 内存占用
const memoryText = ref('0 MB');
let memTimer = null;
function updateMemory() {
  if (window.electronAPI?.getAppMetrics) {
    window.electronAPI.getAppMetrics().then(m => {
      const mb = (m.workingSetSize / 1024).toFixed(0);
      memoryText.value = mb + ' MB';
    }).catch(() => {});
  } else {
    const mem = performance.memory;
    if (mem) {
      const mb = (mem.usedJSHeapSize / 1024 / 1024).toFixed(0);
      memoryText.value = mb + ' MB';
    }
  }
}

// 更新检测
const updateInfo = ref({ checked: false, hasUpdate: false, latestVersion: '' });
async function checkUpdate() {
  try {
    const res = await fetch('https://api.github.com/repos/Haoyesa/codebox/releases/latest', {
      headers: { 'Accept': 'application/vnd.github.v3+json' }
    });
    if (!res.ok) return;
    const data = await res.json();
    const latest = data.tag_name?.replace(/^v/, '') || '';
    if (latest && latest !== appVersion) {
      updateInfo.value = { checked: true, hasUpdate: true, latestVersion: latest };
    } else {
      updateInfo.value = { checked: true, hasUpdate: false, latestVersion: '' };
    }
  } catch {
    updateInfo.value = { checked: false, hasUpdate: false, latestVersion: '' };
  }
}
function openReleasePage() {
  window.electronAPI?.openExternal?.('https://github.com/Haoyesa/codebox/releases/latest');
}

onMounted(() => {
  // 恢复主题
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') {
    isDark.value = true;
    document.documentElement.setAttribute('data-theme', 'dark');
  }
  updateMemory();
  memTimer = setInterval(updateMemory, 5000);
  // 延迟检测更新，不阻塞启动
  setTimeout(checkUpdate, 3000);
});

onBeforeUnmount(() => {
  clearInterval(memTimer);
});
</script>

<style scoped>
.status-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  height: 28px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px;
  background: linear-gradient(180deg, rgba(244,245,248,0.95) 0%, rgba(244,245,248,0.98) 100%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid var(--border-2);
  font-size: 11px;
  color: var(--text-3);
  z-index: 40;
  user-select: none;
}
.status-left, .status-right {
  display: flex; align-items: center; gap: 12px;
}
.status-item {
  display: inline-flex; align-items: center; gap: 4px;
  transition: color .15s;
}
.status-item i[data-lucide] { width: 12px; height: 12px; }
.status-item:hover { color: var(--text); }
.status-item.muted { opacity: 0.6; }
.update-badge {
  color: var(--primary);
  font-weight: 600;
  cursor: pointer;
  animation: pulseBadge 2s ease-in-out infinite;
}
.update-badge:hover { color: var(--primary-deep); }
@keyframes pulseBadge {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
.theme-toggle {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px;
  border: 0; border-radius: 6px;
  background: transparent;
  color: var(--text-3);
  cursor: pointer;
  transition: background .15s, color .15s, transform .1s;
}
.theme-toggle:hover { background: var(--panel-2); color: var(--text); }
.theme-toggle:active { transform: scale(0.92); }
.theme-toggle i[data-lucide] { width: 13px; height: 13px; }
</style>
