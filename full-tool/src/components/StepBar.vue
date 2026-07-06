<template>
  <div class="step-bar-global">
    <div v-for="(s, i) in steps" :key="i" :class="['step-global', { active: current >= i }]">
      <span class="step-num-global">{{ i + 1 }}</span>{{ s }}
    </div>
  </div>
</template>

<script setup>
defineProps({ steps: Array, current: Number });
</script>

<style scoped>
.step-bar-global { display: flex; gap: 10px; justify-content: center; padding: 0 0 16px; }
.step-global {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 8px 16px;
  border: 1px solid var(--border);
  background: var(--panel);
  color: var(--text-2);
  border-radius: 999px;
  font-size: 13px; font-weight: 500;
  transition: all .2s;
}
.step-global:hover { color: var(--text); border-color: var(--border-strong); }
.step-global.active {
  color: var(--primary);
  border-color: var(--primary);
  background: var(--primary-soft);
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.08), 0 0 18px -2px var(--primary-glow);
}
.step-num-global {
  display: inline-flex; align-items: center; justify-content: center;
  width: 20px; height: 20px;
  border-radius: 50%;
  background: var(--panel-3);
  color: var(--text-2);
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 600;
}
.step-global.active .step-num-global { background: var(--primary); color: #fff; }
</style>
