<template>
  <span class="pulse-dot" :class="color"></span>
</template>

<script setup>
defineProps({ color: { type: String, default: 'var(--primary)' } });
</script>
