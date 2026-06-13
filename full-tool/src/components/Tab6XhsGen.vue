<template>
  <section :class="$attrs.class" class="xhsgen-wrap">
    <p class="desc">小红书爆款素材生成器 · 批量生成原创图文，一键导出 PNG / JPG / PDF / SVG。</p>
    <div class="xhsgen-frame">
      <iframe
        ref="frameRef"
        src="./xhs-generator/index.html"
        class="xhsgen-iframe"
        title="小红书爆款素材生成器"
        referrerpolicy="no-referrer"
        allow="clipboard-read; clipboard-write"
      />
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

// Wrap the standalone xhs-generator/index.html via iframe. The file lives under
// full-tool/public/xhs-generator/ so Vite serves it at the same origin — that
// keeps the embedded page's localStorage (settings, decorations) shared with
// the iframe when run inside Electron's file:// origin.
const frameRef = ref(null);

function onLoad() {
  // Touch ref so the linter doesn't flag it; the iframe handles its own bootstrapping.
  void frameRef.value;
}

onMounted(() => {
  const el = frameRef.value;
  if (el) el.addEventListener('load', onLoad);
});

onBeforeUnmount(() => {
  const el = frameRef.value;
  if (el) el.removeEventListener('load', onLoad);
});
</script>

<style scoped>
.xhsgen-wrap {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}
.xhsgen-wrap > .desc {
  flex: 0 0 auto;
  margin: 0 0 10px;
}
.xhsgen-frame {
  flex: 1 1 auto;
  min-height: 720px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: #fff;
  box-shadow: var(--shadow);
}
.xhsgen-iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>