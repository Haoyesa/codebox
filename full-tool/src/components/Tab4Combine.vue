<template>
  <section class="page">
    <p class="desc">将多张图片拼接成一张，支持横排、竖排、网格排列。</p>
    <div class="empty-state">
      <i data-lucide="layers"></i>
      <p>图片拼接功能开发中</p>
      <span style="font-size:12px;color:var(--text-3);margin-top:8px;">敬请期待</span>
    </div>
  </section>
</template>

<script setup>
import { onMounted, nextTick } from 'vue';
onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
});
</script>