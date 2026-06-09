<template>
  <section class="page">
    <p class="desc">上传背景图与叠图，定位后导出高清合成图。</p>
    <div class="empty-state">
      <i data-lucide="image"></i>
      <p>场景化排版功能开发中</p>
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