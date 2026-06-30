<template>
  <div class="app">
    <!-- Top navigation bar -->
    <header class="topbar">
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
          {{ tab.label }}
        </button>
      </nav>
    </header>

    <!-- Page content -->
    <main>
      <keep-alive>
        <component :is="currentTabComponent" :class="['page', { active: true }]" />
      </keep-alive>
    </main>

    <!-- Toast notification -->
    <div :class="['toast', toast.type, { show: toast.message }]" ref="toastRef">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, defineAsyncComponent } from 'vue';
import { ToastSymbol, createToast } from './composables/useToast.js';
import { provide } from 'vue';

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

onMounted(() => {
  window.showToast = toast.show;
  if (window.lucide) window.lucide.createIcons();

  window.addEventListener('error', (e) => {
    console.error('[Global Error]', e.message, e.filename, e.lineno);
  });
  window.addEventListener('unhandledrejection', (e) => {
    console.error('[Unhandled Promise]', e.reason);
  });
});
</script>
