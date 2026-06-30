<template>
  <section :class="$attrs.class" class="highmd-wrap">
    <p class="desc">HighMD 笔记编辑 | 卡片式内容排版与导出，HighMD 风格模板库与字号/对齐/间距精调。</p>
    <div class="highmd-frame">
      <iframe
        ref="frameRef"
        src="./uplog-editor/index.html"
        class="highmd-iframe"
        title="HighMD 笔记编辑"
        referrerpolicy="no-referrer"
        allow="clipboard-read; clipboard-write"
      />
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';

// Wrap the standalone uplog-editor/index.html via iframe. The file lives under
// full-tool/public/uplog-editor/ so Vite serves it at the same origin - that
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
.highmd-wrap {
  flex: 1;
  min-height: 0;
}
.highmd-wrap > .desc {
  flex: 0 0 auto;
  margin: 0 0 10px;
}
.highmd-frame {
  flex: 1 1 0;
  min-height: 0;
  min-width: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: #fff;
  box-shadow: var(--shadow);
}
.highmd-iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>
