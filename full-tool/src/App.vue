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
      <Tab1Export :class="['page', { active: currentTab === 'p1' }]" />
      <Tab2Scene :class="['page', { active: currentTab === 'p2' }]" />
      <Tab3Puzzle :class="['page', { active: currentTab === 'p3' }]" />
      <Tab4Feishu :class="['page', { active: currentTab === 'p4' }]" />
      <Tab5Xhs :class="['page', { active: currentTab === 'p5' }]" />
      <Tab6Settings :class="['page', { active: currentTab === 'p6' }]" />
    </main>

    <!-- Toast notification -->
    <div :class="['toast', toast.type, { show: toast.message }]" ref="toastRef">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import {
  FileText, Image as ImageIcon, LayoutGrid,
  UploadCloud, ShoppingBag, Settings
} from 'lucide-vue-next';
import Tab1Export from './components/Tab1Export.vue';
import Tab2Scene from './components/Tab2Scene.vue';
import Tab3Puzzle from './components/Tab3Puzzle.vue';
import Tab4Feishu from './components/Tab4Feishu.vue';
import Tab5Xhs from './components/Tab5Xhs.vue';
import Tab6Settings from './components/Tab6Settings.vue';

// Tab 定义（对齐截图）
const tabs = [
  { id: 'p1', label: '文档一键导出', icon: 'file-text' },
  { id: 'p2', label: '场景化图片排版', icon: 'image' },
  { id: 'p3', label: '百变拼图排版', icon: 'layout-grid' },
  { id: 'p4', label: '飞书一键上传', icon: 'upload-cloud' },
  { id: 'p5', label: '小红书商品下载', icon: 'shopping-bag' },
  { id: 'p6', label: '设置', icon: 'settings' }
];

const currentTab = ref('p1');

// Toast 系统
const toast = ref({ message: '', type: '' });
let toastTimer = null;

function showToast(message, type = '', duration = 2500) {
  toast.value = { message, type };
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.value.message = '';
  }, duration);
}

function switchTab(id) {
  if (id === currentTab.value) return;
  currentTab.value = id;
  // 切 tab 后重新渲染 lucide 图标
  requestAnimationFrame(() => window.lucide?.createIcons());
}

onMounted(() => {
  if (window.lucide) window.lucide.createIcons();
  window.showToast = showToast;

  window.addEventListener('error', (e) => {
    console.error('[Global Error]', e.message, e.filename, e.lineno);
  });
  window.addEventListener('unhandledrejection', (e) => {
    console.error('[Unhandled Promise]', e.reason);
  });
});
</script>