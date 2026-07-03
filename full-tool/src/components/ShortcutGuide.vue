<template>
  <Teleport to="body">
    <Transition name="guide-fade">
      <div v-if="visible" class="guide-overlay" @click.self="close">
        <div class="guide-box">
          <div class="guide-head">
            <i data-lucide="command"></i>
            <span class="guide-title">快捷键</span>
            <button class="guide-close-btn" @click="close" title="关闭 (ESC)">
              <i data-lucide="x"></i>
            </button>
          </div>
          <div class="guide-body">
            <div class="guide-group">
              <div class="guide-group-title">导航</div>
              <div class="guide-item">
                <span class="guide-label">切换功能标签页</span>
                <span class="guide-keys">
                  <kbd>Ctrl</kbd><span class="guide-plus">+</span><kbd>1</kbd><span class="guide-sep">~</span><kbd>8</kbd>
                </span>
              </div>
              <div class="guide-item">
                <span class="guide-label">聚焦全局搜索</span>
                <span class="guide-keys"><kbd>Ctrl</kbd><span class="guide-plus">+</span><kbd>K</kbd></span>
              </div>
            </div>
            <div class="guide-group">
              <div class="guide-group-title">操作</div>
              <div class="guide-item">
                <span class="guide-label">保存当前模板</span>
                <span class="guide-keys"><kbd>Ctrl</kbd><span class="guide-plus">+</span><kbd>S</kbd></span>
              </div>
              <div class="guide-item">
                <span class="guide-label">显示此帮助面板</span>
                <span class="guide-keys"><kbd>?</kbd><span class="guide-sep">/</span><kbd>Ctrl</kbd><span class="guide-plus">+</span><kbd>/</kbd></span>
              </div>
              <div class="guide-item">
                <span class="guide-label">关闭弹窗/图片预览</span>
                <span class="guide-keys"><kbd>ESC</kbd></span>
              </div>
            </div>
            <div class="guide-group">
              <div class="guide-group-title">拼图模式</div>
              <div class="guide-item">
                <span class="guide-label">多选元素</span>
                <span class="guide-keys"><kbd>Ctrl</kbd><span class="guide-plus">+</span><kbd>Click</kbd></span>
              </div>
              <div class="guide-item">
                <span class="guide-label">范围选择元素</span>
                <span class="guide-keys"><kbd>Shift</kbd><span class="guide-plus">+</span><kbd>Click</kbd></span>
              </div>
            </div>
            <div class="guide-group">
              <div class="guide-group-title">文件</div>
              <div class="guide-item">
                <span class="guide-label">快速添加文件到处理列表</span>
                <span class="guide-keys"><kbd>拖拽文件</kbd></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

const visible = ref(false);

function open() {
  visible.value = true;
  requestAnimationFrame(() => window.lucide?.createIcons());
}

function close() {
  visible.value = false;
}

function toggle() {
  if (visible.value) {
    close();
  } else {
    open();
  }
}

function onKeydown(e) {
  // ESC 关闭
  if (e.key === 'Escape' && visible.value) {
    e.preventDefault();
    close();
    return;
  }
  // ? 键触发（不区分 Shift 状态，因为 ? 本身就是 Shift+/）
  if (e.key === '?' && !e.ctrlKey && !e.metaKey && !e.altKey) {
    e.preventDefault();
    toggle();
    return;
  }
  // Ctrl+/ 触发
  if ((e.ctrlKey || e.metaKey) && !e.altKey && !e.shiftKey && e.key === '/') {
    e.preventDefault();
    toggle();
    return;
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown);
});

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown);
});
</script>

<style scoped>
.guide-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 4000;
  padding: 20px;
}

.guide-box {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 22px 26px;
  min-width: 380px;
  max-width: 560px;
  width: 100%;
  box-shadow: var(--shadow-lg);
  animation: guidePop 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes guidePop {
  from {
    opacity: 0;
    transform: scale(0.92) translateY(8px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

/* Transition: overlay fade */
.guide-fade-enter-active,
.guide-fade-leave-active {
  transition: opacity 0.2s ease;
}
.guide-fade-enter-from,
.guide-fade-leave-to {
  opacity: 0;
}

/* Header */
.guide-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.guide-head i[data-lucide] {
  width: 18px;
  height: 18px;
  color: var(--primary);
}

.guide-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  flex: 1;
}

.guide-close-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--panel);
  color: var(--text-3);
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}

.guide-close-btn:hover {
  background: var(--panel-2);
  color: var(--text);
  border-color: var(--border-strong);
}

.guide-close-btn i[data-lucide] {
  width: 14px;
  height: 14px;
}

/* Body */
.guide-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 20px;
}

/* Group */
.guide-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.guide-group-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 2px;
}

/* Item */
.guide-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 6px 0;
}

.guide-label {
  font-size: 13px;
  color: var(--text-2);
  line-height: 1.4;
  flex: 1;
  min-width: 0;
}

.guide-keys {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  flex-shrink: 0;
  white-space: nowrap;
}

.guide-plus {
  font-size: 11px;
  color: var(--text-4);
  margin: 0 1px;
}

.guide-sep {
  font-size: 11px;
  color: var(--text-4);
  margin: 0 2px;
}

/* kbd in component */
.guide-keys :deep(kbd) {
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 2px 6px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text);
  line-height: 1.5;
}

/* Responsive */
@media (max-width: 640px) {
  .guide-box {
    min-width: unset;
    max-width: 100%;
    padding: 18px 16px;
  }
  .guide-body {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>