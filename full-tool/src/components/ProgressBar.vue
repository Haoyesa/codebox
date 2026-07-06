<template>
  <div class="progress-bar" :class="{ slim }">
    <div class="progress-fill" :style="{ width: percent + '%' }"></div>
  </div>
  <div v-if="showText" class="progress-text">{{ text }}</div>
</template>

<script setup>
defineProps({ percent: Number, text: String, showText: Boolean, slim: Boolean });
</script>

<style scoped>
.progress-bar.slim { height: 4px; }
.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--primary-2), var(--neon-cyan));
  background-size: 200% 100%;
  border-radius: 999px;
  transition: width .3s ease;
  animation: progressShine 2.4s linear infinite;
  box-shadow: 0 0 8px var(--primary-glow);
}
@keyframes progressShine {
  0% { background-position: 0% 0; }
  100% { background-position: 200% 0; }
}
.progress-text {
  font-size: 12px;
  color: var(--text-2);
  margin-top: 6px;
  display: flex;
  justify-content: space-between;
}
</style>
