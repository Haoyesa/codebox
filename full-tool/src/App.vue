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
      <Tab1Export v-if="currentTab === 'p1'" />
      <Tab2Scene v-else-if="currentTab === 'p2'" />
      <Tab3Resize v-else-if="currentTab === 'p3'" />
      <Tab4Combine v-else-if="currentTab === 'p4'" />
      <Tab5Text v-else-if="currentTab === 'p5'" />
      <Tab6Settings v-else-if="currentTab === 'p6'" />
    </main>

    <!-- Toast notification -->
    <div :class="['toast', toast.type]" ref="toastRef">{{ toast.message }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { FileText, Image, Expand, Layers, Type, Settings } from 'lucide-vue-next';
import Tab1Export from './components/Tab1Export.vue';
import Tab2Scene from './components/Tab2Scene.vue';
import Tab3Resize from './components/Tab3Resize.vue';
import Tab4Combine from './components/Tab4Combine.vue';
import Tab5Text from './components/Tab5Text.vue';
import Tab6Settings from './components/Tab6Settings.vue';

// Tab definitions
const tabs = [
  { id: 'p1', label: '文档导出', icon: 'file-text' },
  { id: 'p2', label: '场景化排版', icon: 'image' },
  { id: 'p3', label: '图片缩放', icon: 'expand' },
  { id: 'p4', label: '图片拼接', icon: 'layers' },
  { id: 'p5', label: '文字工具', icon: 'type' },
  { id: 'p6', label: '设置', icon: 'settings' }
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
});
</script>