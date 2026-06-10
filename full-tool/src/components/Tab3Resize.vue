<template>
  <section class="page">
    <p class="desc">批量调整图片尺寸，支持多种缩放模式和输出格式。</p>

    <div class="resize-layout">
      <!-- Left: file list & canvas -->
      <div class="resize-main">
        <!-- Drop zone -->
        <div
          class="drop-zone"
          :class="{ 'drag-over': isDragOver }"
          @dragover.prevent="isDragOver = true"
          @dragleave="isDragOver = false"
          @drop.prevent="onDrop"
          @click="pickFiles"
        >
          <input type="file" ref="fileInput" accept="image/*" multiple style="display:none" @change="onFiles">
          <div class="drop-zone-inner" v-if="images.length === 0">
            <i data-lucide="upload" style="width:40px;height:40px;opacity:.4"></i>
            <p>点击或拖拽上传图片</p>
            <span style="font-size:12px;color:var(--text-3)">支持 PNG / JPG / WEBP</span>
          </div>
          <div class="image-grid" v-else>
            <div v-for="(img, i) in images" :key="i" class="image-thumb" :class="{ selected: selected === i }" @click.stop="selected = i">
              <img :src="img.preview" alt="">
              <button class="thumb-remove" @click.stop="removeImage(i)">×</button>
              <div class="thumb-info">{{ img.name }}</div>
            </div>
            <div class="image-thumb add-more" @click.stop="pickFiles">
              <i data-lucide="plus" style="width:24px;height:24px;opacity:.4"></i>
              <span>添加</span>
            </div>
          </div>
        </div>

        <!-- Preview canvas -->
        <div class="preview-card card" v-if="selected !== null && images[selected]">
          <div class="card-title">
            <i data-lucide="image"></i>
            预览
          </div>
          <div class="preview-wrap">
            <canvas ref="previewCanvas" class="preview-canvas"></canvas>
          </div>
          <div class="preview-info">
            <span class="tag tag-green">{{ images[selected]?.name }}</span>
            <span class="tag">{{ originalSize.width }} × {{ originalSize.height }}</span>
            <span class="tag tag-amber">→ {{ outputSize.width }} × {{ outputSize.height }}</span>
          </div>
        </div>
      </div>

      <!-- Right: settings -->
      <div class="resize-side">
        <div class="card">
          <div class="card-section">
            <h3 class="card-title"><i data-lucide="maximize"></i> 输出尺寸</h3>

            <div class="size-mode-tabs">
              <button
                v-for="m in ['wh', 'scale', 'long']"
                :key="m"
                :class="['size-tab', { active: sizeMode === m }]"
                @click="sizeMode = m"
              >
                {{ { wh: '宽×高', scale: '缩放%', long: '长边' }[m] }}
              </button>
            </div>

            <!-- 宽×高 mode -->
            <div v-if="sizeMode === 'wh'" class="size-inputs">
              <div class="size-row">
                <label>宽度 px</label>
                <input type="number" v-model="outWidth" @input="onSizeChange" min="1" max="10000">
              </div>
              <div class="size-row">
                <label>高度 px</label>
                <input type="number" v-model="outHeight" @input="onSizeChange" min="1" max="10000">
              </div>
              <div class="checkbox" style="margin-top:8px">
                <input type="checkbox" v-model="keepRatio" id="keepRatio">
                <span class="box"></span>
                <label for="keepRatio" style="cursor:pointer">保持比例</label>
              </div>
            </div>

            <!-- 缩放 mode -->
            <div v-if="sizeMode === 'scale'" class="size-inputs">
              <div class="size-row">
                <label>缩放比例 %</label>
                <input type="number" v-model="scalePct" @input="onScaleChange" min="1" max="500">
              </div>
            </div>

            <!-- 长边模式 -->
            <div v-if="sizeMode === 'long'" class="size-inputs">
              <div class="size-row">
                <label>长边像素</label>
                <input type="number" v-model="longEdge" @input="onLongEdgeChange" min="1" max="20000">
              </div>
            </div>
          </div>

          <div class="divider"></div>

          <div class="card-section">
            <h3 class="card-title"><i data-lucide="image"></i> 输出格式</h3>
            <div class="format-chips">
              <button
                v-for="fmt in ['PNG', 'JPG', 'WEBP']"
                :key="fmt"
                :class="['format-chip', { active: format === fmt }]"
                @click="format = fmt"
              >{{ fmt }}</button>
            </div>
            <div v-if="format === 'JPG'" style="margin-top:8px">
              <label style="font-size:12px;color:var(--text-2)">质量</label>
              <input type="range" v-model="jpgQuality" min="10" max="100">
              <span style="font-size:12px;color:var(--text-2)">{{ jpgQuality }}%</span>
            </div>
          </div>

          <div class="divider"></div>

          <div class="card-section">
            <h3 class="card-title"><i data-lucide="folder"></i> 输出目录</h3>
            <button class="btn btn-block" @click="pickDir">
              <i data-lucide="folder-output"></i>
              {{ outputDir || '选择目录' }}
            </button>
          </div>
        </div>

        <!-- Action -->
        <button
          class="btn btn-primary btn-block"
          style="margin-top:12px"
          :disabled="images.length === 0 || !outputDir || isRunning"
          @click="startResize"
        >
          <i data-lucide="download"></i>
          {{ isRunning ? `处理中 ${doneCount}/${images.length}` : `开始处理 ${images.length} 张` }}
        </button>

        <div v-if="images.length > 0" class="status-row">
          <span class="meta">已选：<b>{{ images.length }}</b> 张</span>
          <button class="btn btn-ghost btn-sm" @click="clearAll">清空</button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue';
import { Upload, Maximize, Image, Download, FolderOutput, Plus } from 'lucide-vue-next';

const fileInput = ref(null);
const previewCanvas = ref(null);
const images = ref([]);
const selected = ref(null);
const isDragOver = ref(false);

// Size settings
const sizeMode = ref('wh');
const outWidth = ref(800);
const outHeight = ref(600);
const scalePct = ref(100);
const longEdge = ref(2000);
const keepRatio = ref(true);

// Format
const format = ref('PNG');
const jpgQuality = ref(90);

// Output
const outputDir = ref('');
const isRunning = ref(false);
const doneCount = ref(0);

const originalSize = reactive({ width: 0, height: 0 });
const outputSize = computed(() => {
  if (!selected.value && selected.value !== 0) return { width: 0, height: 0 };
  const img = images.value[selected.value];
  if (!img) return { width: 0, height: 0 };
  if (sizeMode.value === 'wh') return { width: outWidth.value, height: outHeight.value };
  if (sizeMode.value === 'scale') {
    return {
      width: Math.round(img.naturalWidth * scalePct.value / 100),
      height: Math.round(img.naturalHeight * scalePct.value / 100)
    };
  }
  if (sizeMode.value === 'long') {
    const longer = Math.max(img.naturalWidth, img.naturalHeight);
    const ratio = longEdge.value / longer;
    return {
      width: Math.round(img.naturalWidth * ratio),
      height: Math.round(img.naturalHeight * ratio)
    };
  }
  return { width: 0, height: 0 };
});

function pickFiles() { fileInput.value?.click(); }

function onFiles(e) {
  const files = Array.from(e.target.files || []);
  addFiles(files);
  e.target.value = '';
}

function onDrop(e) {
  isDragOver.value = false;
  const files = Array.from(e.dataTransfer?.files || []);
  addFiles(files.filter(f => f.type.startsWith('image/')));
}

function addFiles(files) {
  files.forEach(file => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      images.value.push({
        name: file.name,
        file,
        preview: url,
        naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight,
        width: img.naturalWidth,
        height: img.naturalHeight
      });
      if (images.value.length === 1) selected.value = 0;
      nextTick(renderPreview);
    };
    img.src = url;
  });
}

function removeImage(i) {
  images.value.splice(i, 1);
  if (selected.value >= images.value.length) selected.value = Math.max(0, images.value.length - 1);
  nextTick(renderPreview);
}

function clearAll() {
  images.value = [];
  selected.value = null;
}

function onSizeChange() {
  if (!keepRatio.value || !selected.value) return;
  const img = images.value[selected.value];
  if (!img) return;
  const ratio = img.naturalHeight / img.naturalWidth;
  outHeight.value = Math.round(outWidth.value * ratio);
  renderPreview();
}

function onScaleChange() {
  if (!selected.value) return;
  const img = images.value[selected.value];
  if (!img) return;
  outWidth.value = Math.round(img.naturalWidth * scalePct.value / 100);
  outHeight.value = Math.round(img.naturalHeight * scalePct.value / 100);
  renderPreview();
}

function onLongEdgeChange() {
  if (!selected.value) return;
  const img = images.value[selected.value];
  if (!img) return;
  const longer = Math.max(img.naturalWidth, img.naturalHeight);
  const ratio = longEdge.value / longer;
  outWidth.value = Math.round(img.naturalWidth * ratio);
  outHeight.value = Math.round(img.naturalHeight * ratio);
  renderPreview();
}

function renderPreview() {
  if (selected.value === null || !previewCanvas.value) return;
  const img = images.value[selected.value];
  if (!img) return;
  const canvas = previewCanvas.value;
  const ctx = canvas.getContext('2d');
  canvas.width = outputSize.value.width;
  canvas.height = outputSize.value.height;
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
  originalSize.width = img.naturalWidth;
  originalSize.height = img.naturalHeight;
}

watch(selected, () => nextTick(renderPreview));
watch([outWidth, outHeight, scalePct, longEdge, sizeMode], () => {
  if (sizeMode.value !== 'wh') return;
  nextTick(renderPreview);
});

async function pickDir() {
  if (!window.electronAPI) {
    const d = prompt('输出目录（浏览器模式请输入路径）');
    if (d) outputDir.value = d;
    return;
  }
  const r = await window.electronAPI.selectOutputDir();
  if (!r.canceled && r.filePaths[0]) outputDir.value = r.filePaths[0];
}

async function startResize() {
  if (!images.value.length || !outputDir.value) return;
  isRunning.value = true;
  doneCount.value = 0;

  for (let i = 0; i < images.value.length; i++) {
    const img = images.value[i];
    const canvas = document.createElement('canvas');
    let w, h;
    if (sizeMode.value === 'wh') { w = outWidth.value; h = outHeight.value; }
    else if (sizeMode.value === 'scale') {
      w = Math.round(img.naturalWidth * scalePct.value / 100);
      h = Math.round(img.naturalHeight * scalePct.value / 100);
    } else {
      const longer = Math.max(img.naturalWidth, img.naturalHeight);
      const ratio = longEdge.value / longer;
      w = Math.round(img.naturalWidth * ratio);
      h = Math.round(img.naturalHeight * ratio);
    }
    canvas.width = w; canvas.height = h;
    canvas.getContext('2d').drawImage(img, 0, 0, w, h);

    const mime = format.value === 'JPG' ? 'image/jpeg' : format.value === 'WEBP' ? 'image/webp' : 'image/png';
    const q = format.value === 'JPG' ? jpgQuality.value / 100 : undefined;
    const blob = await new Promise(r => canvas.toBlob(r, mime, q));
    const buf = await blob.arrayBuffer();

    if (window.electronAPI) {
      const ext = format.value.toLowerCase();
      const name = img.name.replace(/\.[^.]+$/, '') + `_${w}x${h}.${ext}`;
      await window.electronAPI.writeFile(outputDir.value + '/' + name, Array.from(new Uint8Array(buf)));
    } else {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = img.name.replace(/\.[^.]+$/, '') + `_${w}x${h}.${ext}`;
      a.click(); URL.revokeObjectURL(url);
    }
    doneCount.value++;
  }

  isRunning.value = false;
  window.showToast?.(`处理完成 ${doneCount.value} 张图片`, 'success');
}

onMounted(() => nextTick(() => window.lucide?.createIcons()));
</script>

<style scoped>
.resize-layout {
  display: grid; grid-template-columns: 1fr 280px; gap: 16px;
}
.resize-main { display: flex; flex-direction: column; gap: 12px; }
.resize-side { display: flex; flex-direction: column; gap: 0; }

.drop-zone {
  background: #fff; border: 2px dashed var(--border); border-radius: var(--radius);
  min-height: 300px; position: relative; cursor: pointer;
  transition: border-color .15s, background .15s;
}
.drop-zone.drag-over { border-color: var(--primary); background: var(--primary-soft); }
.drop-zone-inner {
  position: absolute; inset: 0; display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 8px; color: var(--text-3);
}
.drop-zone-inner p { margin: 0; font-size: 14px; }

.image-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  gap: 8px; padding: 12px; align-content: start;
}
.image-thumb {
  position: relative; aspect-ratio: 1; border-radius: 8px; overflow: hidden;
  border: 2px solid transparent; cursor: pointer; transition: all .15s;
}
.image-thumb:hover { border-color: var(--primary-2); }
.image-thumb.selected { border-color: var(--primary); }
.image-thumb img { width: 100%; height: 100%; object-fit: cover; }
.thumb-remove {
  position: absolute; top: 2px; right: 4px; width: 18px; height: 18px;
  background: rgba(0,0,0,.5); color: #fff; border: 0; border-radius: 50%;
  font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.thumb-info {
  position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,.5);
  color: #fff; font-size: 10px; padding: 2px 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.add-more {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  background: #f9fafb; color: var(--text-3); gap: 4px;
}
.add-more span { font-size: 11px; }

.preview-card { flex: 1; }
.preview-wrap {
  display: flex; align-items: center; justify-content: center;
  min-height: 120px; background: #f9fafb; border-radius: 8px; overflow: hidden;
}
.preview-canvas { max-width: 100%; max-height: 200px; object-fit: contain; }
.preview-info { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }

.size-mode-tabs { display: flex; gap: 4px; margin-bottom: 12px; }
.size-tab {
  flex: 1; padding: 6px; border: 1px solid var(--border); background: #fff;
  border-radius: 6px; font-size: 12px; cursor: pointer; transition: all .15s;
}
.size-tab.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.size-inputs { display: flex; flex-direction: column; gap: 8px; }
.size-row { display: flex; align-items: center; gap: 8px; }
.size-row label { font-size: 12px; color: var(--text-2); width: 70px; }
.size-row input { flex: 1; }

.format-chips { display: flex; gap: 6px; }
.format-chip {
  padding: 4px 12px; border-radius: 6px; border: 1px solid var(--border);
  background: #fff; font-size: 12px; font-weight: 500; cursor: pointer; transition: all .15s;
}
.format-chip:hover { border-color: var(--primary-2); }
.format-chip.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.status-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-top: 8px; font-size: 12px; color: var(--text-2);
}

.divider { height: 1px; background: var(--border-2); margin: 12px 0; }

@media (max-width: 900px) {
  .resize-layout { grid-template-columns: 1fr; }
}
</style>