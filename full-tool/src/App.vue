<template>
  <div class="app">
    <!-- Top navigation bar -->
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <div class="brand-mark">F</div>
          <span class="brand-name">Full Tool</span>
        </div>
        <nav class="tabs" role="tablist">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="['tab', { active: currentTab === tab.id }]"
            :aria-selected="currentTab === tab.id"
            role="tab"
            @click="switchTab(tab.id)"
          >
            <i :data-lucide="tab.icon"></i>
            <span>{{ tab.label }}</span>
          </button>
        </nav>
        <div class="topbar-spacer"></div>
        <!-- Global search -->
        <div class="global-search" :class="{ active: searchFocus }">
          <i data-lucide="search"></i>
          <input
            ref="searchRef"
            v-model="searchQuery"
            placeholder="搜索功能..."
            @focus="searchFocus = true"
            @blur="onSearchBlur"
            @keydown.down.prevent="onSearchDown"
            @keydown.up.prevent="onSearchUp"
            @keydown.enter.prevent="onSearchEnter"
            @keydown.esc="searchFocus = false"
          />
          <span class="search-shortcut">Ctrl K</span>
          <Transition name="search-dropdown">
            <div v-if="searchFocus && filteredSearchItems.length" class="search-dropdown" @mousedown.prevent>
              <div
                v-for="(item, idx) in filteredSearchItems"
                :key="item.id"
                :class="['search-item', { active: searchIndex === idx }]"
                @mouseenter="searchIndex = idx"
                @click="goSearchItem(item)"
              >
                <i :data-lucide="item.icon"></i>
                <div class="search-item-info">
                  <div class="search-item-title">{{ item.title }}</div>
                  <div class="search-item-desc">{{ item.desc }}</div>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </header>

    <!-- Page content -->
    <main>
      <keep-alive>
        <ErrorBoundary>
          <Suspense>
            <template #default>
              <component :is="currentTabComponent" :class="['page', { active: true }]" />
            </template>
            <template #fallback>
              <SkeletonLoader />
            </template>
          </Suspense>
        </ErrorBoundary>
      </keep-alive>
    </main>

    <!-- Toast notification -->
    <div :class="['toast', toast.type, { show: toast.message }]" ref="toastRef">{{ toast.message }}</div>

    <!-- Global image preview -->
    <ImagePreview ref="imagePreviewRef" />

    <!-- Bottom status bar -->
    <StatusBar :current-tab="currentTab" />

    <!-- Global confirm dialog -->
    <ConfirmDialog ref="confirmRef" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent } from 'vue';
import { ToastSymbol, createToast } from './composables/useToast.js';
import { provide } from 'vue';
import StatusBar from './components/StatusBar.vue';
import ImagePreview from './components/ImagePreview.vue';
import ConfirmDialog from './components/ConfirmDialog.vue';
import SkeletonLoader from './components/SkeletonLoader.vue';
import ErrorBoundary from './components/ErrorBoundary.vue';

// Tab 定义
const tabs = [
  { id: 'p1', label: '文档一键导出', icon: 'file-text', component: () => import('./components/Tab1Export.vue') },
  { id: 'p2', label: '场景化图片排版', icon: 'image', component: () => import('./components/Tab2Scene.vue') },
  { id: 'p3', label: '百变拼图排版', icon: 'layout-grid', component: () => import('./components/Tab3Puzzle.vue') },
  { id: 'p4', label: '飞书一键上传', icon: 'upload-cloud', component: () => import('./components/Tab4Feishu.vue') },
  { id: 'p5', label: '小红书商品下载', icon: 'shopping-bag', component: () => import('./components/Tab5Xhs.vue') },
  { id: 'p6', label: '小红书爆款素材', icon: 'flame', component: () => import('./components/Tab6XhsGen.vue') },
  { id: 'p7', label: 'HighMD', icon: 'notebook-pen', component: () => import('./components/Tab7Uplog.vue') },
  { id: 'p8', label: '设置', icon: 'settings', component: () => import('./components/Tab6Settings.vue') }
];

const currentTab = ref('p1');
const confirmRef = ref(null);
const searchRef = ref(null);
const searchQuery = ref('');
const searchFocus = ref(false);
const searchIndex = ref(0);

const searchItems = [
  { id: 'p1', title: '文档一键导出', desc: 'PDF/PPT/Excel 批量导出图片', icon: 'file-text', tab: 'p1' },
  { id: 'p2', title: '场景化图片排版', desc: '画布合成与场景模板', icon: 'image', tab: 'p2' },
  { id: 'p3', title: '百变拼图排版', desc: '九宫格拼图与批量生成', icon: 'layout-grid', tab: 'p3' },
  { id: 'p4', title: '飞书一键上传', desc: '飞书多维表格与附件上传', icon: 'upload-cloud', tab: 'p4' },
  { id: 'p5', title: '小红书商品下载', desc: '商品图片批量采集', icon: 'shopping-bag', tab: 'p5' },
  { id: 'p6', title: '小红书爆款素材', desc: '爆款素材生成器', icon: 'flame', tab: 'p6' },
  { id: 'p7', title: 'HighMD 编辑器', desc: 'Markdown 图文笔记', icon: 'notebook-pen', tab: 'p7' },
  { id: 'p8', title: '设置', desc: '路径、授权与日志', icon: 'settings', tab: 'p8' }
];

const filteredSearchItems = computed(() => {
  if (!searchQuery.value.trim()) return searchItems;
  const q = searchQuery.value.toLowerCase();
  return searchItems.filter(i => i.title.toLowerCase().includes(q) || i.desc.toLowerCase().includes(q));
});

function onSearchBlur() {
  setTimeout(() => { searchFocus.value = false; }, 150);
}
function onSearchDown() {
  if (searchIndex.value < filteredSearchItems.value.length - 1) searchIndex.value++;
}
function onSearchUp() {
  if (searchIndex.value > 0) searchIndex.value--;
}
function onSearchEnter() {
  const item = filteredSearchItems.value[searchIndex.value];
  if (item) goSearchItem(item);
}
function goSearchItem(item) {
  switchTab(item.tab);
  searchQuery.value = '';
  searchFocus.value = false;
  searchIndex.value = 0;
}

// 组件映射缓存
const componentCache = new Map();

const currentTabComponent = computed(() => {
  const tab = tabs.find(t => t.id === currentTab.value);
  if (!tab) return null;
  if (!componentCache.has(tab.id)) {
    componentCache.set(tab.id, defineAsyncComponent(tab.component));
  }
  return componentCache.get(tab.id);
});

// Toast 系统 - provide 给子组件，同时保持 window.showToast 兼容
const toast = createToast();
provide(ToastSymbol, toast);

function switchTab(id) {
  if (id === currentTab.value) return;
  currentTab.value = id;
  // 切 tab 后重新渲染 lucide 图标
  requestAnimationFrame(() => window.lucide?.createIcons());
}

// 全局 confirm 方法
async function globalConfirm(options) {
  return confirmRef.value?.open(options) || Promise.resolve(false);
}

// 键盘快捷键
function onKeydown(e) {
  // Ctrl/Cmd + 1~8 切换 Tab
  if ((e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey) {
    const num = parseInt(e.key, 10);
    if (num >= 1 && num <= 8) {
      e.preventDefault();
      const tab = tabs[num - 1];
      if (tab) switchTab(tab.id);
      return;
    }
    // Ctrl+K 聚焦搜索框
    if (e.key === 'k' || e.key === 'K') {
      e.preventDefault();
      searchRef.value?.focus();
      return;
    }
    // Ctrl+S 保存当前模板（仅对拼图和HighMD）
    if (e.key === 's' || e.key === 'S') {
      e.preventDefault();
      window.dispatchEvent(new CustomEvent('app:shortcut', { detail: { action: 'save', tab: currentTab.value } }));
      return;
    }
  }
  // ESC 关闭弹窗
  if (e.key === 'Escape') {
    // 关闭图片预览
    if (window.imagePreview) window.imagePreview.close();
    // 触发 ESC 快捷键事件给当前 Tab
    window.dispatchEvent(new CustomEvent('app:shortcut', { detail: { action: 'escape', tab: currentTab.value } }));
  }
}

onMounted(() => {
  window.showToast = toast.show;
  window.appConfirm = globalConfirm;
  if (window.lucide) window.lucide.createIcons();

  window.addEventListener('error', (e) => {
    console.error('[Global Error]', e.message, e.filename, e.lineno);
    window.showToast?.('运行时错误: ' + e.message, 'error');
  });
  window.addEventListener('unhandledrejection', (e) => {
    console.error('[Unhandled Promise]', e.reason);
    window.showToast?.('未处理的异步错误', 'error');
    e.preventDefault();
  });
  document.addEventListener('keydown', onKeydown);
});
</script>
