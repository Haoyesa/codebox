<template>
  <slot v-if="!hasError" />
  <div v-else class="error-fallback">
    <i data-lucide="alert-triangle"></i>
    <div class="error-title">{{ i18n.ErrorBoundary.title }}</div>
    <div class="error-msg">{{ errorMessage }}</div>
    <button class="btn btn-sm" @click="retry">
      <i data-lucide="refresh-cw"></i>{{ i18n.ErrorBoundary.retry }}
    </button>
  </div>
</template>

<script setup>
import { ref, onErrorCaptured, nextTick } from 'vue';
import { logger } from '../composables/useLogger.js';

const i18n = {
  ErrorBoundary: { title: '组件加载出错', unknown: '未知错误', retry: '重试' }
};

const hasError = ref(false);
const errorMessage = ref('');

onErrorCaptured((err) => {
  hasError.value = true;
  errorMessage.value = err?.message || i18n.ErrorBoundary.unknown;
  logger.error('[ErrorBoundary]', err);
  return false; // 阻止错误继续传播
});

function retry() {
  hasError.value = false;
  errorMessage.value = '';
  nextTick(() => window.lucide?.createIcons());
}
</script>

<style scoped>
.error-fallback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--text-3);
  text-align: center;
  min-height: 300px;
}
.error-fallback i[data-lucide] {
  width: 40px; height: 40px;
  color: var(--warn);
}
.error-title {
  font-size: 16px; font-weight: 600;
  color: var(--text);
}
.error-msg {
  font-size: 13px; color: var(--text-3);
  max-width: 400px;
  word-break: break-word;
}
</style>
