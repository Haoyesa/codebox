<template>
  <section class="page">
    <p class="desc">在图片上添加文字、水印，支持多种字体和样式。</p>

    <div class="text-layout">
      <!-- Canvas -->
      <div class="card canvas-card">
        <div class="row-spread" style="margin-bottom:12px">
          <h3 class="card-title" style="margin:0"><i data-lucide="type"></i>画布</h3>
          <div class="row" style="gap:8px">
            <button class="btn" @click="pickBg">
              <i data-lucide="image"></i>
              {{ bgImg ? '更换背景' : '添加背景图' }}
            </button>
            <button class="btn btn-ghost" @click="clearBg">
              <i data-lucide="x"></i>清除
            </button>
          </div>
        </div>
        <input type="file" ref="bgInput" accept="image/*" style="display:none" @change="onBg">

        <div class="text-canvas-wrap" ref="canvasWrap">
          <canvas ref="textCanvas" class="text-canvas" @click="onCanvasClick"></canvas>
          <div
            v-for="(txt, i) in texts"
            :key="i"
            class="text-overlay"
            :class="{ selected: selectedText === i }"
            :style="{
              left: txt.x + 'px',
              top: txt.y + 'px',
              fontSize: txt.fontSize + 'px',
              fontFamily: txt.fontFamily,
              color: txt.color,
              fontWeight: txt.bold ? 'bold' : 'normal',
              fontStyle: txt.italic ? 'italic' : 'normal',
              textShadow: txt.shadow ? '0 2px 8px rgba(0,0,0,.4)' : 'none',
              opacity: txt.opacity / 100,
              transform: txt.rotation ? `rotate(${txt.rotation}deg)` : 'none',
            }"
            @click.stop="selectedText = i"
            @mousedown.stop="startDragText(i, $event)"
          >{{ txt.content }}</div>
        </div>
      </div>

      <!-- Text panel -->
      <div class="card" style="grid-column: 2 / -1;">
        <h3 class="card-title"><i data-lucide="type"></i>文字</h3>

        <div class="text-input-wrap">
          <textarea
            v-model="currentText"
            placeholder="输入文字内容..."
            rows="2"
            @input="updateText"
          ></textarea>
        </div>

        <div class="divider"></div>

        <div class="setting-row">
          <label>字体</label>
          <select v-model="fontFamily" @change="updateText">
            <option value="Microsoft YaHei">微软雅黑</option>
            <option value="SimHei">黑体</option>
            <option value="SimSun">宋体</option>
            <option value="KaiTi">楷体</option>
            <option value="Arial">Arial</option>
            <option value="Georgia">Georgia</option>
            <option value="Impact">Impact</option>
          </select>
        </div>

        <div class="setting-row">
          <label>大小</label>
          <input type="number" v-model="fontSize" @input="updateText" min="8" max="500">
        </div>

        <div class="setting-row">
          <label>颜色</label>
          <input type="color" v-model="fontColor" @change="updateText">
        </div>

        <div class="style-btns">
          <button :class="['style-btn', { active: bold }]" @click="bold = !bold; updateText()">
            <b>B</b>
          </button>
          <button :class="['style-btn', { active: italic }]" @click="italic = !italic; updateText()">
            <i>I</i>
          </button>
          <button :class="['style-btn', { active: shadow }]" @click="shadow = !shadow; updateText()">
            <span style="font-size:11px">影</span>
          </button>
        </div>

        <div class="setting-row">
          <label>不透明度</label>
          <input type="range" v-model="textOpacity" min="0" max="100" @input="updateText">
          <span>{{ textOpacity }}%</span>
        </div>

        <div class="setting-row">
          <label>旋转</label>
          <input type="number" v-model="textRotation" @input="updateText" min="-180" max="180">
          <span>°</span>
        </div>

        <div class="divider"></div>

        <div class="row-spread">
          <button class="btn btn-primary" @click="addTextToList">
            <i data-lucide="plus"></i>添加文字
          </button>
          <button v-if="selectedText !== null" class="btn btn-ghost" @click="removeText(selectedText)">
            <i data-lucide="trash-2" style="width:14px;height:14px"></i>
          </button>
        </div>

        <!-- Text list -->
        <div class="text-list" v-if="texts.length > 0" style="margin-top:12px">
          <div
            v-for="(t, i) in texts"
            :key="i"
            :class="['text-item', { selected: selectedText === i }]"
            @click="selectedText = i; loadTextProps(t)"
          >
            <span>{{ t.content || '(空)' }}</span>
            <button @click.stop="removeText(i)">×</button>
          </div>
        </div>
      </div>

      <!-- Export -->
      <div class="card">
        <h3 class="card-title"><i data-lucide="download"></i>导出</h3>
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
          {{ outputDir || '选择目录' }}
        </button>
        <button
          class="btn btn-primary btn-block"
          :disabled="texts.length === 0 || !outputDir"
          @click="startExport"
        >
          <i data-lucide="download"></i>
          导出图片
        </button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { Type, Image, X, Plus, Trash2, Download, FolderOutput } from 'lucide-vue-next';

const bgInput = ref(null);
const textCanvas = ref(null);
const canvasWrap = ref(null);

const bgImg = ref(null);
const texts = ref([]);
const selectedText = ref(null);

// Current text props
const currentText = ref('文字示例');
const fontFamily = ref('Microsoft YaHei');
const fontSize = ref(48);
const fontColor = ref('#000000');
const bold = ref(false);
const italic = ref(false);
const shadow = ref(false);
const textOpacity = ref(100);
const textRotation = ref(0);
const format = ref('PNG');
const outputDir = ref('');

// Drag state
let dragTextIdx = null;
let dragStartX = 0, dragStartY = 0;
let dragStartXText = 0, dragStartYText = 0;

function pickBg() { bgInput.value?.click(); }
function clearBg() { bgImg.value = null; render(); }

function onBg(e) {
  const file = e.target.files?.[0];
  if (!file) return;
  const url = URL.createObjectURL(file);
  const img = new Image();
  img.onload = () => { bgImg.value = img; render(); };
  img.src = url;
  e.target.value = '';
}

function render() {
  if (!textCanvas.value) return;
  const canvas = textCanvas.value;
  const ctx = canvas.getContext('2d');
  canvas.width = bgImg.value?.width || 800;
  canvas.height = bgImg.value?.height || 600;
  ctx.fillStyle = '#ffffff';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  if (bgImg.value) ctx.drawImage(bgImg.value, 0, 0);
}

function updateText() {
  if (selectedText.value === null) return;
  Object.assign(texts.value[selectedText.value], {
    content: currentText.value,
    fontFamily: fontFamily.value,
    fontSize: fontSize.value,
    color: fontColor.value,
    bold: bold.value,
    italic: italic.value,
    shadow: shadow.value,
    opacity: textOpacity.value,
    rotation: textRotation.value,
  });
}

function addTextToList() {
  if (!currentText.value.trim()) return;
  texts.value.push({
    content: currentText.value,
    x: 100, y: 100,
    fontFamily: fontFamily.value,
    fontSize: fontSize.value,
    color: fontColor.value,
    bold: bold.value,
    italic: italic.value,
    shadow: shadow.value,
    opacity: textOpacity.value,
    rotation: textRotation.value,
  });
  selectedText.value = texts.value.length - 1;
  window.showToast?.('文字已添加', 'success');
}

function loadTextProps(t) {
  currentText.value = t.content;
  fontFamily.value = t.fontFamily;
  fontSize.value = t.fontSize;
  fontColor.value = t.color;
  bold.value = t.bold;
  italic.value = t.italic;
  shadow.value = t.shadow;
  textOpacity.value = t.opacity;
  textRotation.value = t.rotation;
}

function removeText(i) {
  texts.value.splice(i, 1);
  if (selectedText.value === i) selectedText.value = null;
  else if (selectedText.value > i) selectedText.value--;
}

function onCanvasClick() {
  selectedText.value = null;
}

function startDragText(i, e) {
  selectedText.value = i;
  loadTextProps(texts.value[i]);
  dragTextIdx = i;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  dragStartXText = texts.value[i].x;
  dragStartYText = texts.value[i].y;
  window.addEventListener('mousemove', onDragText);
  window.addEventListener('mouseup', stopDragText);
}

function onDragText(e) {
  if (dragTextIdx === null) return;
  const dx = e.clientX - dragStartX;
  const dy = e.clientY - dragStartY;
  texts.value[dragTextIdx].x = Math.max(0, dragStartXText + dx);
  texts.value[dragTextIdx].y = Math.max(0, dragStartYText + dy);
}

function stopDragText() {
  dragTextIdx = null;
  window.removeEventListener('mousemove', onDragText);
  window.removeEventListener('mouseup', stopDragText);
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
  if (!textCanvas.value) return;
  render();

  const canvas = textCanvas.value;
  const ctx = canvas.getContext('2d');

  for (const txt of texts.value) {
    ctx.save();
    ctx.globalAlpha = txt.opacity / 100;
    ctx.font = `${txt.bold ? 'bold' : ''} ${txt.italic ? 'italic' : ''} ${txt.fontSize}px ${txt.fontFamily}`;
    ctx.fillStyle = txt.color;
    if (txt.shadow) {
      ctx.shadowColor = 'rgba(0,0,0,0.4)';
      ctx.shadowBlur = 8;
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;
    }
    if (txt.rotation) {
      ctx.translate(txt.x + ctx.measureText(txt.content).width / 2, txt.y + txt.fontSize / 2);
      ctx.rotate(txt.rotation * Math.PI / 180);
      ctx.translate(-(txt.x + ctx.measureText(txt.content).width / 2), -(txt.y + txt.fontSize / 2));
    }
    ctx.fillText(txt.content, txt.x, txt.y + txt.fontSize);
    ctx.restore();
  }

  const mime = format.value === 'JPG' ? 'image/jpeg' : format.value === 'WEBP' ? 'image/webp' : 'image/png';
  const q = format.value === 'JPG' ? 0.92 : undefined;
  const blob = await new Promise(r => canvas.toBlob(r, mime, q));
  const name = `文字图_${Date.now()}.${format.value.toLowerCase()}`;

  if (window.electronAPI) {
    const buf = await blob.arrayBuffer();
    await window.electronAPI.writeFile(outputDir.value + '/' + name, Array.from(new Uint8Array(buf)));
  } else {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = name;
    a.click(); URL.revokeObjectURL(url);
  }
  window.showToast?.('导出完成！', 'success');
}

onMounted(() => {
  nextTick(() => {
    render();
    window.lucide?.createIcons();
  });
});
</script>

<style scoped>
.text-layout {
  display: grid; grid-template-columns: 1fr 300px; gap: 12px;
}
.canvas-card { grid-column: 1; }

.text-canvas-wrap {
  position: relative; background: #f9fafb; border-radius: 8px;
  overflow: hidden; min-height: 400px; cursor: crosshair;
}
.text-canvas { display: block; width: 100%; }

.text-overlay {
  position: absolute; cursor: move; user-select: none; white-space: pre;
  line-height: 1.2;
}
.text-overlay.selected {
  outline: 2px dashed var(--primary);
  outline-offset: 4px;
}

.text-input-wrap textarea {
  width: 100%; padding: 8px; border: 1px solid var(--border);
  border-radius: 8px; resize: vertical; font-family: inherit; font-size: 14px;
}

.setting-row {
  display: flex; align-items: center; gap: 8px; margin-bottom: 8px;
}
.setting-row label { font-size: 12px; color: var(--text-2); min-width: 50px; }
.setting-row input[type=number] { width: 60px; }
.setting-row input[type=color] { width: 32px; height: 32px; border: 1px solid var(--border); border-radius: 4px; padding: 0; cursor: pointer; }
.setting-row span { font-size: 12px; color: var(--text-2); min-width: 36px; }

.style-btns { display: flex; gap: 6px; margin-bottom: 12px; }
.style-btn {
  width: 32px; height: 32px; border: 1px solid var(--border); border-radius: 6px;
  background: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all .15s; font-size: 14px;
}
.style-btn:hover { background: #f3f4f6; }
.style-btn.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.text-list { display: flex; flex-direction: column; gap: 4px; }
.text-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 6px 8px; background: #f3f4f6; border-radius: 6px; font-size: 12px;
  cursor: pointer; transition: all .15s;
}
.text-item:hover { background: #e5e7eb; }
.text-item.selected { background: var(--primary-soft); color: var(--primary); }
.text-item button { background: none; border: none; cursor: pointer; color: var(--text-3); font-size: 16px; }

.format-chips { display: flex; gap: 6px; margin-bottom: 12px; }
.format-chip {
  padding: 4px 12px; border-radius: 6px; border: 1px solid var(--border);
  background: #fff; font-size: 12px; font-weight: 500; cursor: pointer; transition: all .15s;
}
.format-chip:hover { border-color: var(--primary-2); }
.format-chip.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.divider { height: 1px; background: var(--border-2); margin: 12px 0; }

@media (max-width: 900px) {
  .text-layout { grid-template-columns: 1fr; }
}
</style>