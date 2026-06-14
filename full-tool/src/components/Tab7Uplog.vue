<template>
  <section :class="$attrs.class" class="uplog-wrap">
    <p class="desc">UPlog 笔记编辑 | 卡片式内容排版与导出，HighMD 风格模板库与字号/对齐/间距精调。</p>
    <div class="uplog-frame">
      <iframe
        ref="frameRef"
        src="./uplog-editor/index.html"
        class="uplog-iframe"
        title="UPlog 笔记编辑"
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
.uplog-wrap {
  flex: 1;
  min-height: 0;
}
.uplog-wrap > .desc {
  flex: 0 0 auto;
  margin: 0 0 10px;
}
.uplog-frame {
  flex: 1 1 0;
  min-height: 0;
  min-width: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  background: #fff;
  box-shadow: var(--shadow);
}
.uplog-iframe {
  display: block;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>
