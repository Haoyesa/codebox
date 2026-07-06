<template>
  <div class="empty-state" :style="minHeight ? { minHeight } : {}" :class="{ compact }">
    <i :data-lucide="icon || 'inbox'"></i>
    <p>{{ title }}</p>
    <p v-if="subtitle" style="font-size:12px;margin-top:4px;color:var(--text-3)">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({ icon: String, title: String, subtitle: String, minHeight: String, compact: Boolean });
</script>
