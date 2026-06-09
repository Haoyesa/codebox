<template>
  <section class="page">
    <p class="desc">批量调整图片尺寸，支持多种缩放模式和输出格式。</p>
    <div class="empty-state">
      <i data-lucide="expand"></i>
      <p>图片缩放功能开发中</p>
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