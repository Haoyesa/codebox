<template>
  <section class="page">
    <p class="desc">配置应用全局设置和偏好选项。</p>
    <div class="card" style="max-width:600px;">
      <div class="card-section">
        <h3 class="card-title"><i data-lucide="folder"></i> LibreOffice 配置</h3>
        <div class="setting-row">
          <span class="setting-label">安装路径</span>
          <span style="font-size:13px;color:var(--text-2);">自动检测</span>
        </div>
        <p style="font-size:12px;color:var(--text-3);margin:0;">
          本工具自动查找系统中的 LibreOffice 安装路径。
        </p>
      </div>
      <div class="divider"></div>
      <div class="card-section">
        <h3 class="card-title"><i data-lucide="info"></i> 关于</h3>
        <div style="font-size:13px;color:var(--text-2);line-height:1.8;">
          <p><b>商品图工坊 · Full</b></p>
          <p>版本 1.0.0</p>
          <p style="margin-top:8px;">基于 Electron + Vue3 构建的桌面应用。</p>
        </div>
      </div>
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

<style scoped>
.setting-row {
  display: grid; grid-template-columns: auto 1fr;
  gap: 12px; align-items: center; margin-bottom: 8px;
}
.setting-label { font-size: 13px; color: var(--text-2); }
</style>