<template>
  <section class="page">
    <p class="desc">将多张图片拼接成一张，支持横排、竖排、网格排列。</p>

    <div class="combine-layout">
      <!-- Image list -->
      <div class="card" style="grid-column: 1 / -1;">
        <div class="row-spread" style="margin-bottom:12px">
          <h3 class="card-title" style="margin:0">
            <i data-lucide="layers"></i>
            图片列表 ({{ images.length }})
          </h3>
          <div class="row" style="gap:8px">
            <button class="btn" @click="addImages">
              <i data-lucide="plus"></i>添加图片
            </button>
            <button class="btn btn-ghost" @click="images = []; renderCombine()">
              <i data-lucide="trash-2"></i>清空
            </button>
          </div>
        </div>
        <input type="file" ref="fileInput" accept="image/*" multiple style="display:none" @change="onFiles">

        <div class="img-list" v-if="images.length > 0">
          <div v-for="(img, i) in images" :key="i" class="img-item">
            <img :src="img.preview" alt="">
            <span class="img-name">{{ img.name }}</span>
            <button class="btn btn-icon" @click="images.splice(i, 1); renderCombine()">
              <i data-lucide="x" style="width:14px;height:14px"></i>
            </button>
          </div>
        </div>
        <div v-else class="empty-state">
          <i data-lucide="image" style="width:32px;height:32px"></i>
          <p>暂无图片，请先添加</p>
        </div>
      </div>

      <!-- Settings -->
      <div class="card">
        <h3 class="card-title"><i data-lucide="layout"></i>排列方式</h3>
        <div class="layout-tabs">
          <button
            v-for="l in ['row', 'col', 'grid']"
            :key="l"
            :class="['layout-tab', { active: layout === l }]"
            @click="layout = l; renderCombine()"
          >
            {{ { row: '横排', col: '竖排', grid: '网格' }[l] }}
          </button>
        </div>

        <div v-if="layout === 'grid'" class="grid-settings">
          <div class="setting-row">
            <label>列数</label>
            <input type="number" v-model="gridCols" @input="renderCombine" min="1" max="10">
          </div>
        </div>

        <div class="divider"></div>

        <div class="setting-row">
          <label>边距 px</label>
          <input type="number" v-model="gap" @input="renderCombine" min="0" max="100">
        </div>
        <div class="setting-row">
          <label>背景色</label>
          <input type="color" v-model="bgColor" @input="renderCombine">
        </div>

        <div class="divider"></div>

        <div class="setting-row">
          <label>输出尺寸</label>
        </div>
        <div class="size-inputs">
          <input type="number" v-model="outW" @input="renderCombine" placeholder="宽" min="100">
          <span>×</span>
          <input type="number" v-model="outH" @input="renderCombine" placeholder="高" min="100">
        </div>
        <div class="checkbox" style="margin-top:8px">
          <input type="checkbox" v-model="autoSize" @change="renderCombine" id="autoSizeCheck">
          <span class="box"></span>
          <label for="autoSizeCheck" style="cursor:pointer;font-size:12px;color:var(--text-2)">自动尺寸（拼接后自适应）</label>
        </div>
      </div>

      <!-- Preview -->
      <div class="card">
        <h3 class="card-title"><i data-lucide="eye"></i>预览</h3>
        <div class="preview-stage" ref="previewStage">
          <canvas ref="previewCanvas" class="combine-canvas"></canvas>
        </div>
        <div v-if="images.length > 0" class="preview-info">
          <span class="tag tag-green">{{ canvasW }} × {{ canvasH }}</span>
          <span class="tag">{{ images.length }} 张</span>
        </div>
      </div>

      <!-- Export -->
      <div class="card">
        <h3 class="card-title"><i data-lucide="download"></i> 导出</h3>
        <div class="format-chips">
          <button
            v-for="fmt in ['PNG', 'JPG', 'WEBP']"
            :key="fmt"
            :class="['format-chip', { active: format === fmt }]"
            @click="format = fmt"
          >{{ fmt }}</button>
        </div>
        <div class="divider"></div>
        <button class="btn btn-block" @click="pickDir" style="margin-bottom:8px">
          <i data-lucide="folder-output"></i>
          {{ outputDir || '选择输出目录' }}
        </button>
        <button
          class="btn btn-primary btn-block"
          :disabled="images.length < 2 || !outputDir"
          @click="startExport"
        >
          <i data-lucide="download"></i>
          导出拼接图
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick, watch } from 'vue';
import { Layers, Plus, Trash2, Layout, Eye, Download, X } from 'lucide-vue-next';

const fileInput = ref(null);
const previewCanvas = ref(null);
const previewStage = ref(null);

const images = ref([]);
const layout = ref('grid');
const gridCols = ref(3);
const gap = ref(10);
const bgColor = ref('#ffffff');
const outW = ref(1200);
const outH = ref(800);
const autoSize = ref(true);
const format = ref('PNG');
const outputDir = ref('');

const canvasW = ref(0);
const canvasH = ref(0);

function addImages() { fileInput.value?.click(); }
function onFiles(e) {
  const files = Array.from(e.target.files || []);
  files.forEach(f => {
    const url = URL.createObjectURL(f);
    const img = new Image();
    img.onload = () => {
      images.value.push({ name: f.name, file: f, preview: url, w: img.naturalWidth, h: img.naturalHeight });
      renderCombine();
    };
    img.src = url;
  });
  e.target.value = '';
}

function renderCombine() {
  if (!previewCanvas.value || images.value.length === 0) return;
  const canvas = previewCanvas.value;
  const ctx = canvas.getContext('2d');

  if (autoSize.value) {
    // Calculate auto size based on layout
    if (layout.value === 'row') {
      const maxH = Math.max(...images.value.map(i => i.h));
      const totalW = images.value.reduce((s, i) => s + i.w, 0) + gap.value * (images.value.length - 1);
      canvas.width = totalW; canvas.height = maxH;
    } else if (layout.value === 'col') {
      const maxW = Math.max(...images.value.map(i => i.w));
      const totalH = images.value.reduce((s, i) => s + i.h, 0) + gap.value * (images.value.length - 1);
      canvas.width = maxW; canvas.height = totalH;
    } else {
      const cols = gridCols.value;
      const rows = Math.ceil(images.value.length / cols);
      const cellW = Math.max(...images.value.map(i => i.w));
      const cellH = Math.max(...images.value.map(i => i.h));
      canvas.width = cellW * cols + gap.value * (cols - 1);
      canvas.height = cellH * rows + gap.value * (rows - 1);
    }
  } else {
    canvas.width = outW.value; canvas.height = outH.value;
  }

  canvasW.value = canvas.width;
  canvasH.value = canvas.height;

  ctx.fillStyle = bgColor.value;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  const imgEls = images.value.map(imgData => {
    const img = new Image();
    img.src = imgData.preview;
    return new Promise(resolve => { img.onload = () => resolve(img); });
  });

  Promise.all(imgEls).then(imgs => {
    if (layout.value === 'row') {
      let x = 0;
      imgs.forEach((img, i) => {
        const h = images.value[i].h;
        const scale = canvas.height / h;
        const w = images.value[i].w * scale;
        ctx.drawImage(img, x, 0, w, canvas.height);
        x += w + gap.value;
      });
    } else if (layout.value === 'col') {
      let y = 0;
      imgs.forEach((img, i) => {
        const w = images.value[i].w;
        const scale = canvas.width / w;
        const h = images.value[i].h * scale;
        ctx.drawImage(img, 0, y, canvas.width, h);
        y += h + gap.value;
      });
    } else {
      const cols = gridCols.value;
      const cellW = canvas.width / cols;
      const cellH = canvas.height / Math.ceil(images.value.length / cols);
      imgs.forEach((img, i) => {
        const col = i % cols;
        const row = Math.floor(i / cols);
        const sx = col * cellW + gap.value / 2;
        const sy = row * cellH + gap.value / 2;
        const sw = cellW - gap.value;
        const sh = cellH - gap.value;
        ctx.drawImage(img, sx, sy, sw, sh);
      });
    }
  });
}

async function pickDir() {
  if (!window.electronAPI) {
    const d = prompt('输出目录');
    if (d) outputDir.value = d;
    return;
  }
  const r = await window.electronAPI.selectOutputDir();
  if (!r.canceled && r.filePaths[0]) outputDir.value = r.filePaths[0];
}

async function startExport() {
  if (!previewCanvas.value || !outputDir.value) return;
  const canvas = previewCanvas.value;
  const mime = format.value === 'JPG' ? 'image/jpeg' : format.value === 'WEBP' ? 'image/webp' : 'image/png';
  const q = format.value === 'JPG' ? 0.92 : undefined;
  const blob = await new Promise(r => canvas.toBlob(r, mime, q));
  const buf = await blob.arrayBuffer();
  const name = `拼接图_${Date.now()}.${format.value.toLowerCase()}`;

  if (window.electronAPI) {
    await window.electronAPI.writeFile(outputDir.value + '/' + name, Array.from(new Uint8Array(buf)));
  } else {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    a.click(); URL.revokeObjectURL(url);
  }
  window.showToast?.('导出完成！', 'success');
}

onMounted(() => nextTick(() => window.lucide?.createIcons()));
watch(images, () => { nextTick(renderCombine); }, { deep: true });
</script>

<style scoped>
.combine-layout {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;
}

.img-list { display: flex; flex-wrap: wrap; gap: 8px; }
.img-item {
  display: flex; align-items: center; gap: 6px;
  padding: 4px 8px; background: #f3f4f6; border-radius: 6px;
  font-size: 12px;
}
.img-item img { width: 32px; height: 32px; object-fit: cover; border-radius: 4px; }
.img-name { max-width: 80px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.layout-tabs { display: flex; gap: 4px; margin-bottom: 12px; }
.layout-tab {
  flex: 1; padding: 6px; border: 1px solid var(--border); background: #fff;
  border-radius: 6px; font-size: 12px; cursor: pointer; transition: all .15s;
}
.layout-tab.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.grid-settings { margin-top: 8px; }
.setting-row { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.setting-row label { font-size: 12px; color: var(--text-2); min-width: 60px; }
.setting-row input[type=number] { width: 60px; }

.size-inputs { display: flex; align-items: center; gap: 8px; }
.size-inputs input { width: 80px; }
.size-inputs span { color: var(--text-3); }

.preview-stage {
  background: #f9fafb; border-radius: 8px; overflow: auto;
  min-height: 200px; display: flex; align-items: center; justify-content: center;
}
.combine-canvas { max-width: 100%; }
.preview-info { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }

.format-chips { display: flex; gap: 6px; margin-bottom: 12px; }
.format-chip {
  padding: 4px 12px; border-radius: 6px; border: 1px solid var(--border);
  background: #fff; font-size: 12px; font-weight: 500; cursor: pointer; transition: all .15s;
}
.format-chip:hover { border-color: var(--primary-2); }
.format-chip.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.divider { height: 1px; background: var(--border-2); margin: 12px 0; }

@media (max-width: 900px) {
  .combine-layout { grid-template-columns: 1fr; }
}
</style>