<template>
  <section class="page">
    <p class="desc">在图片上添加文字、水印，支持多种字体和样式。</p>
    <div class="empty-state">
      <i data-lucide="type"></i>
      <p>文字工具功能开发中</p>
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