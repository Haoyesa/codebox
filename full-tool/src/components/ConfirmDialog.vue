<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div v-if="visible" class="confirm-overlay" @click.self="onCancel">
        <div class="confirm-box">
          <div class="confirm-head">
            <i data-lucide="alert-circle" v-if="type === 'warning'"></i>
            <i data-lucide="help-circle" v-else-if="type === 'confirm'"></i>
            <i data-lucide="info" v-else></i>
            <span class="confirm-title">{{ title }}</span>
          </div>
          <div class="confirm-body">{{ message }}</div>
          <div class="confirm-foot">
            <button class="btn btn-sm btn-ghost" @click="onCancel">{{ cancelText }}</button>
            <button :class="['btn', 'btn-sm', type === 'danger' ? 'btn-warn' : 'btn-primary']" @click="onConfirm">{{ confirmText }}</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue';

const visible = ref(false);
const title = ref('确认');
const message = ref('');
const type = ref('confirm'); // confirm | warning | danger
const confirmText = ref('确认');
const cancelText = ref('取消');
let resolveFn = null;
let rejectFn = null;

function open(options = {}) {
  title.value = options.title || '确认';
  message.value = options.message || '';
  type.value = options.type || 'confirm';
  confirmText.value = options.confirmText || '确认';
  cancelText.value = options.cancelText || '取消';
  visible.value = true;
  requestAnimationFrame(() => window.lucide?.createIcons());
  return new Promise((resolve, reject) => {
    resolveFn = resolve;
    rejectFn = reject;
  });
}

function onConfirm() {
  visible.value = false;
  resolveFn?.(true);
}

function onCancel() {
  visible.value = false;
  resolveFn?.(false);
}

defineExpose({ open });
</script>

<style scoped>
.confirm-overlay {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 3000;
  padding: 20px;
}
.confirm-box {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px 22px;
  min-width: 320px; max-width: 420px;
  box-shadow: var(--shadow-lg);
  animation: dialogPop .2s cubic-bezier(.34,1.56,.64,1);
}
@keyframes dialogPop {
  from { opacity: 0; transform: scale(0.92) translateY(8px); }
  to { opacity: 1; transform: none; }
}
.confirm-head {
  display: flex; align-items: center; gap: 8px;
  font-size: 15px; font-weight: 600;
  color: var(--text);
  margin-bottom: 10px;
}
.confirm-head i[data-lucide] {
  width: 18px; height: 18px;
  color: var(--primary);
}
.confirm-body {
  font-size: 13px; line-height: 1.6;
  color: var(--text-2);
  margin-bottom: 18px;
}
.confirm-foot {
  display: flex; justify-content: flex-end; gap: 10px;
}

/* Transition */
.dialog-fade-enter-active, .dialog-fade-leave-active {
  transition: opacity .2s ease;
}
.dialog-fade-enter-from, .dialog-fade-leave-to {
  opacity: 0;
}
</style>
