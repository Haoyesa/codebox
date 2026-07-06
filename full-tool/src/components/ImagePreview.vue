<template>
  <Teleport to="body">
    <Transition name="preview-fade">
      <div v-if="visible" class="image-preview-overlay" @click="close">
        <div class="image-preview-content" @click.stop>
          <img :src="src" :alt="alt" class="preview-img" />
          <div class="preview-toolbar">
            <span class="preview-name">{{ name }}</span>
            <button class="preview-close" :title="i18n.ImagePreview.close" @click="close">
              <i data-lucide="x"></i>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const i18n = {
  ImagePreview: { alt: '图片预览', close: '关闭 (ESC)' }
};

const visible = ref(false);
const src = ref('');
const alt = ref(i18n.ImagePreview.alt);
const name = ref('');

function open(url, options = {}) {
  src.value = url;
  alt.value = options.alt || i18n.ImagePreview.alt;
  name.value = options.name || i18n.ImagePreview.alt;
  visible.value = true;
  // 渲染 lucide 图标
  requestAnimationFrame(() => window.lucide?.createIcons());
}

function close() {
  visible.value = false;
  setTimeout(() => {
    src.value = '';
    alt.value = '';
  }, 300);
}

function onKeydown(e) {
  if (e.key === 'Escape' && visible.value) {
    close();
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown);
  window.imagePreview = { open, close };
});

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown);
});

defineExpose({ open, close });
</script>

<style scoped>
.image-preview-overlay {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.88);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 2000;
  padding: 40px;
  cursor: zoom-out;
}
.image-preview-content {
  position: relative;
  max-width: 90vw; max-height: 90vh;
  display: flex; flex-direction: column;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.4);
  cursor: default;
}
.preview-img {
  max-width: 100%; max-height: 82vh;
  object-fit: contain;
  display: block;
  background: #000;
}
.preview-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  background: rgba(15, 23, 42, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}
.preview-name {
  font-size: 13px; color: var(--text-3);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 70%;
}
.preview-close {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px;
  border: 0; border-radius: 6px;
  background: transparent;
  color: var(--text-3);
  cursor: pointer;
  transition: background .15s, color .15s;
}
.preview-close:hover { background: rgba(255,255,255,0.1); color: #fff; }
.preview-close i[data-lucide] { width: 16px; height: 16px; }

/* Transition */
.preview-fade-enter-active,
.preview-fade-leave-active {
  transition: opacity .25s ease, transform .25s ease;
}
.preview-fade-enter-from,
.preview-fade-leave-to {
  opacity: 0;
  transform: scale(0.96);
}
.preview-fade-enter-active .image-preview-content,
.preview-fade-leave-active .image-preview-content {
  transition: transform .25s cubic-bezier(.34,1.56,.64,1);
}
.preview-fade-enter-from .image-preview-content,
.preview-fade-leave-to .image-preview-content {
  transform: scale(0.92);
}
</style>
