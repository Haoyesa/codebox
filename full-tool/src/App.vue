<template>
  <div class="app">
    <!-- Top navigation bar -->
    <header class="topbar">
      <nav class="tabs">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="['tab', { active: currentTab === tab.id }]"
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
      <Tab3Resize :class="['page', { active: currentTab === 'p3' }]" />
      <Tab4Combine :class="['page', { active: currentTab === 'p4' }]" />
      <Tab5Text :class="['page', { active: currentTab === 'p5' }]" />
      <Tab6Settings :class="['page', { active: currentTab === 'p6' }]" />
      <Tab7Rename :class="['page', { active: currentTab === 'p7' }]" />
    </main>

    <!-- Toast notification -->
    <div :class="['toast', toast.type]" ref="toastRef">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { FileText, Image, Expand, Layers, Type, Settings, FilePen } from 'lucide-vue-next';
import Tab1Export from './components/Tab1Export.vue';
import Tab2Scene from './components/Tab2Scene.vue';
import Tab3Resize from './components/Tab3Resize.vue';
import Tab4Combine from './components/Tab4Combine.vue';
import Tab5Text from './components/Tab5Text.vue';
import Tab6Settings from './components/Tab6Settings.vue';
import Tab7Rename from './components/Tab7Rename.vue';

// Tab definitions
const tabs = [
  { id: 'p1', label: '文档导出', icon: 'file-text' },
  { id: 'p2', label: '场景化排版', icon: 'image' },
  { id: 'p3', label: '图片缩放', icon: 'expand' },
  { id: 'p4', label: '图片拼接', icon: 'layers' },
  { id: 'p5', label: '文字工具', icon: 'type' },
  { id: 'p6', label: '设置', icon: 'settings' },
  { id: 'p7', label: '批量重命名', icon: 'file-pen' }
];

const currentTab = ref('p1');

// Toast system
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
  currentTab.value = id;
}

onMounted(() => {
  // Initialize lucide icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // Provide global toast function
  window.showToast = showToast;

  // Global Vue error handler
  window.addEventListener('error', (e) => {
    console.error('[Global Error]', e.message, e.filename, e.lineno);
  });
  window.addEventListener('unhandledrejection', (e) => {
    console.error('[Unhandled Promise]', e.reason);
  });
});
</script>