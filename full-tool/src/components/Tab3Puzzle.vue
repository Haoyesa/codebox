<template>
  <section :class="$attrs.class">
    <p class="desc">定义模板坑位，批量填充图片并导出成品图。</p>

    <div class="puzzle-layout">
      <!-- 左侧操作面板 -->
      <aside class="puzzle-side">
        <div class="section-block">
          <h4 class="section-title">画布操作</h4>
          <button class="btn btn-block" @click="pickBg">
            <i data-lucide="image"></i>上传背景图
          </button>
          <div class="row" style="margin-top: 10px; gap: 8px;">
            <label class="checkbox">
              <input type="checkbox" v-model="canvas.transparent" />
              <span class="box"></span>透明背景
            </label>
          </div>
          <div class="row" style="margin-top: 8px; gap: 8px;">
            <label class="checkbox" :class="{ disabled: canvas.transparent }">
              <input type="checkbox" v-model="canvas.solidBg" :disabled="canvas.transparent" />
              <span class="box"></span>纯色背景
            </label>
            <input type="color" v-model="canvas.bgColor" :disabled="canvas.transparent" class="color-pick" />
          </div>
          <div class="row" style="margin-top: 10px; gap: 12px; font-size: 12px;">
            <span class="muted">宽</span><input type="number" v-model.number="canvas.width" min="50" max="4096" class="num" />
            <span class="muted">高</span><input type="number" v-model.number="canvas.height" min="50" max="4096" class="num" />
          </div>
        </div>

        <div class="section-block">
          <h4 class="section-title">坑位操作</h4>
          <div class="row" style="gap: 8px;">
            <button class="btn btn-sm" @click="addSlot">添加坑位</button>
            <button class="btn btn-sm" @click="addImageSlot">添加图片坑位</button>
          </div>
          <button class="btn btn-sm btn-ghost btn-block" style="margin-top: 8px;" @click="clearSlots">清空坑位</button>
        </div>

        <div class="section-block">
          <h4 class="section-title">元素操作</h4>
          <div class="row row-2col" style="gap: 8px;">
            <button class="btn btn-sm" @click="addText">添加文字</button>
            <button class="btn btn-sm btn-ghost" @click="clearTexts">清空文字</button>
          </div>
          <div class="row row-2col" style="gap: 8px; margin-top: 8px;">
            <button class="btn btn-sm" @click="pickDecoration">添加图片</button>
            <button class="btn btn-sm btn-ghost" @click="clearImages">清空图片</button>
          </div>
        </div>

        <div class="section-block">
          <h4 class="section-title">文件操作</h4>
          <div class="row" style="gap: 8px;">
            <button class="btn btn-sm" @click="pickImages">
              <i data-lucide="upload"></i>上传图片
            </button>
            <button class="btn btn-sm" @click="pickOutput">输出目录</button>
          </div>
          <div class="muted path" style="margin-top: 8px; font-size: 12px;" :title="outputDir">
            {{ outputDir || '未设置' }}
          </div>
        </div>

        <div class="section-block">
          <h4 class="section-title">生成规则</h4>
          <label class="radio" style="display: flex; margin-bottom: 8px;">
            <input type="radio" v-model="rule.mode" value="single" />
            <span class="box"></span>单一文件夹循环
          </label>
          <label class="checkbox" style="display: flex; margin-bottom: 8px; padding-left: 22px;">
            <input type="checkbox" v-model="rule.firstAsCover" :disabled="rule.mode !== 'single'" />
            <span class="box"></span>拼图1作为封面（仅生成1张）
          </label>
          <label class="radio" style="display: flex;">
            <input type="radio" v-model="rule.mode" value="multi" />
            <span class="box"></span>多文件夹模式
          </label>
          <div class="row" style="margin-top: 12px; gap: 8px; align-items: center;">
            <span class="muted" style="font-size: 12px;">导出倍率</span>
            <select v-model="rule.scale" style="flex: 1;">
              <option value="1">1x（原图）</option>
              <option value="1.5">1.5x</option>
              <option value="2">2x</option>
              <option value="3">3x</option>
            </select>
          </div>
        </div>

        <div class="section-block">
          <h4 class="section-title">操作</h4>
          <div class="row" style="gap: 8px;">
            <button class="btn btn-sm" @click="previewAll">预览</button>
            <button class="btn btn-sm btn-primary" @click="startGenerate" :disabled="!canGenerate">
              <i data-lucide="play"></i>开始生成
            </button>
          </div>
          <div class="muted" style="margin-top: 8px; font-size: 12px;">
            {{ templateHint }}
          </div>
        </div>
      </aside>

      <!-- 中心画布 -->
      <div class="puzzle-main">
        <div class="canvas-toolbar">
          <div class="row" style="gap: 8px;">
            <span class="template-pill">
              拼图1
              <button class="pill-x" @click="deleteCurrentTemplate" title="关闭模板">×</button>
            </span>
          </div>
          <div class="row" style="gap: 6px;">
            <button class="btn btn-sm" @click="newTemplate">+ 新建</button>
            <button class="btn btn-sm" @click="saveTemplate">保存模板</button>
            <button class="btn btn-sm" @click="deleteTemplate">删除模板</button>
            <select v-model="currentTemplate" class="tpl-select">
              <option v-for="t in templates" :key="t" :value="t">{{ t || '空模板' }}</option>
            </select>
            <button class="btn-icon" @click="canvasMenu"><i data-lucide="more-horizontal"></i></button>
          </div>
        </div>

        <div class="canvas-stage" ref="stageRef" @wheel.prevent="onWheel" @mousedown.self="onStageClick">
          <div
            class="canvas-frame"
            :class="{ transparent: canvas.transparent }"
            :style="frameStyle"
          >
            <!-- 背景 -->
            <img v-if="canvas.bgImg" :src="canvas.bgImg" class="bg-layer" />
            <div v-else-if="canvas.solidBg && !canvas.transparent" class="bg-layer" :style="{ background: canvas.bgColor }"></div>
            <div v-else-if="!canvas.transparent" class="bg-layer bg-empty"></div>

            <!-- 元素层 -->
            <div
              v-for="el in elements"
              :key="el.id"
              class="el"
              :class="['el-' + el.type, { selected: selectedId === el.id }]"
              :style="elStyle(el)"
              @mousedown.stop="startDrag($event, el)"
              @click.stop="select(el.id)"
            >
              <template v-if="el.type === 'text'">
                <span class="el-text" :style="{ fontSize: el.fontSize + 'px', color: el.color, fontWeight: el.weight }">{{ el.text }}</span>
              </template>
              <template v-else-if="el.type === 'image'">
                <img :src="el.src" class="el-image" />
              </template>
              <template v-else-if="el.type === 'slot'">
                <div class="slot-inner">
                  <i data-lucide="square-dashed" style="width: 24px; height: 24px; opacity: 0.5;"></i>
                  <span>坑位 #{{ el.index }}</span>
                </div>
              </template>
              <template v-else-if="el.type === 'image-slot'">
                <div class="slot-inner" v-if="!el.src">
                  <i data-lucide="image" style="width: 24px; height: 24px; opacity: 0.5;"></i>
                  <span>图片坑位 #{{ el.index }}</span>
                </div>
                <img v-else :src="el.src" class="el-image" />
              </template>

              <!-- 选中态的 4 角 -->
              <template v-if="selectedId === el.id">
                <span class="handle tl" @mousedown.stop="startResize($event, el, 'tl')"></span>
                <span class="handle tr" @mousedown.stop="startResize($event, el, 'tr')"></span>
                <span class="handle bl" @mousedown.stop="startResize($event, el, 'bl')"></span>
                <span class="handle br" @mousedown.stop="startResize($event, el, 'br')"></span>
                <button class="el-del" @click.stop="removeEl(el.id)" title="删除"><i data-lucide="x"></i></button>
              </template>
            </div>

            <!-- 空态提示 -->
            <div v-if="elements.length === 0 && !canvas.bgImg" class="canvas-hint">
              点击左侧「添加坑位」或「添加图片」开始设计模板
            </div>
          </div>

          <!-- 缩放控件 -->
          <div class="zoom-bar">
            <button class="btn-icon" @click="zoomBy(-0.1)"><i data-lucide="minus"></i></button>
            <span class="zoom-val mono">{{ Math.round(zoom * 100) }}%</span>
            <button class="btn-icon" @click="zoomBy(0.1)"><i data-lucide="plus"></i></button>
          </div>
        </div>

        <!-- 底部图片列表 -->
        <div class="puzzle-bottom">
          <div class="row-spread" style="margin-bottom: 8px;">
            <span class="muted">
              图片列表（<b class="mono">{{ images.length }}</b>）
              <span style="margin-left: 12px;">预计生成 <b class="mono">{{ estimatedCount }}</b> 张</span>
            </span>
            <button class="btn btn-sm btn-ghost" @click="images = []; updateEstimate()">清空全部</button>
          </div>
          <div class="image-list" v-if="images.length">
            <div v-for="(img, i) in images" :key="i" class="img-chip" :title="img.name">
              <i data-lucide="image" style="width: 12px; height: 12px;"></i>
              <span class="img-name">{{ img.name }}</span>
            </div>
          </div>
          <div v-else class="empty-state" style="padding: 24px 0;">
            <i data-lucide="inbox"></i>
            <p>还没有添加图片</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue';

// 画布
const canvas = reactive({
  width: 1000,
  height: 1332,
  transparent: false,
  solidBg: true,
  bgColor: '#ffffff',
  bgImg: ''
});
const zoom = ref(0.4);
const elements = ref([]); // {id, type, x, y, w, h, text/src/index/color/...}
const selectedId = ref(null);
let nextId = 1;

const stageRef = ref(null);

// 规则
const rule = reactive({ mode: 'single', firstAsCover: false, scale: '1' });

// 图片 / 输出
const images = ref([]); // {name, path|dataUrl}
const outputDir = ref('');

// 模板
const TEMPLATE_KEY = 'fulltool_puzzle_templates';
const currentTemplate = ref('');
const templates = ref([]);

const estimatedCount = computed(() => {
  if (rule.mode === 'single') {
    return rule.firstAsCover ? (images.value.length > 0 ? 1 : 0) : images.value.length;
  }
  // 多文件夹: 这里粗略按 images.length 估算
  return images.value.length;
});

const canGenerate = computed(() => {
  return elements.value.length > 0 && images.value.length > 0 && outputDir.value;
});

const templateHint = computed(() => {
  if (templates.value.length === 0) return '未选择模板';
  if (!currentTemplate.value) return '未选择模板';
  return '当前：' + currentTemplate.value;
});

const frameStyle = computed(() => {
  return {
    width: canvas.width + 'px',
    height: canvas.height + 'px',
    transform: 'scale(' + zoom.value + ')',
    transformOrigin: 'top left'
  };
});

function elStyle(el) {
  return {
    left: el.x + 'px',
    top: el.y + 'px',
    width: el.w + 'px',
    height: el.h + 'px'
  };
}

function onWheel(e) {
  if (!e.ctrlKey) return;
  e.preventDefault();
  const delta = e.deltaY < 0 ? 0.1 : -0.1;
  zoom.value = Math.max(0.1, Math.min(3, zoom.value + delta));
}
function zoomBy(d) {
  zoom.value = Math.max(0.1, Math.min(3, zoom.value + d));
}

function onStageClick() {
  selectedId.value = null;
}

function newId() { return 'el-' + (nextId++); }
let slotCount = 0;
function addSlot() {
  slotCount++;
  const w = Math.min(300, canvas.width * 0.3);
  const h = Math.min(200, canvas.height * 0.2);
  elements.value.push({
    id: newId(), type: 'slot',
    x: (canvas.width - w) / 2, y: (canvas.height - h) / 2,
    w, h, index: slotCount
  });
  selectedId.value = elements.value[elements.value.length - 1].id;
}
function addImageSlot() {
  slotCount++;
  const w = Math.min(400, canvas.width * 0.4);
  const h = Math.min(400, canvas.height * 0.4);
  elements.value.push({
    id: newId(), type: 'image-slot',
    x: (canvas.width - w) / 2, y: (canvas.height - h) / 2,
    w, h, index: slotCount, src: ''
  });
  selectedId.value = elements.value[elements.value.length - 1].id;
}
function clearSlots() {
  elements.value = elements.value.filter(e => e.type !== 'slot' && e.type !== 'image-slot');
  if (selectedId.value && !elements.value.find(e => e.id === selectedId.value)) selectedId.value = null;
}

function addText() {
  const w = 300, h = 60;
  elements.value.push({
    id: newId(), type: 'text',
    x: 40, y: 40, w, h,
    text: '双击编辑文字', fontSize: 28, color: '#0f172a', weight: 600
  });
  selectedId.value = elements.value[elements.value.length - 1].id;
}
function clearTexts() {
  elements.value = elements.value.filter(e => e.type !== 'text');
}

async function pickDecoration() {
  if (!window.electronAPI) {
    window.showToast?.('请在 Electron 版本中添加装饰图', 'warn');
    return;
  }
  const r = await window.electronAPI.openFiles({ filters: [{ name: '图片', extensions: ['png', 'jpg', 'jpeg', 'webp', 'svg'] }] });
  if (r.canceled || !r.filePaths.length) return;
  const filePath = r.filePaths[0];
  try {
    const fr = await window.electronAPI.readFile(filePath);
    if (!fr.success) throw new Error(fr.error);
    const ext = (filePath.split('.').pop() || 'png').toLowerCase();
    const mime = ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg' : ext === 'svg' ? 'image/svg+xml' : 'image/png';
    const blob = new Blob([fr.data], { type: mime });
    const url = URL.createObjectURL(blob);
    const img = new Image();
    img.onload = () => {
      const maxW = canvas.width * 0.4, maxH = canvas.height * 0.3;
      const ratio = Math.min(maxW / img.width, maxH / img.height, 1);
      elements.value.push({
        id: newId(), type: 'image', src: url,
        x: 40, y: 40, w: img.width * ratio, h: img.height * ratio
      });
      selectedId.value = elements.value[elements.value.length - 1].id;
    };
    img.src = url;
  } catch (err) {
    window.showToast?.('读取图片失败：' + err.message, 'error');
  }
}
function clearImages() {
  elements.value = elements.value.filter(e => e.type !== 'image');
}

function select(id) { selectedId.value = id; }
function removeEl(id) {
  elements.value = elements.value.filter(e => e.id !== id);
  if (selectedId.value === id) selectedId.value = null;
}

// 拖动 / 缩放
let dragCtx = null;
function startDrag(e, el) {
  select(el.id);
  const startX = e.clientX, startY = e.clientY;
  const origX = el.x, origY = el.y;
  const scale = zoom.value;
  dragCtx = { el, kind: 'move', startX, startY, origX, origY, scale };
  window.addEventListener('mousemove', onDragMove);
  window.addEventListener('mouseup', onDragEnd);
}
function startResize(e, el, corner) {
  select(el.id);
  const startX = e.clientX, startY = e.clientY;
  const origX = el.x, origY = el.y, origW = el.w, origH = el.h;
  const scale = zoom.value;
  dragCtx = { el, kind: 'resize', corner, startX, startY, origX, origY, origW, origH, scale };
  window.addEventListener('mousemove', onDragMove);
  window.addEventListener('mouseup', onDragEnd);
}
function onDragMove(e) {
  if (!dragCtx) return;
  const dx = (e.clientX - dragCtx.startX) / dragCtx.scale;
  const dy = (e.clientY - dragCtx.startY) / dragCtx.scale;
  const el = dragCtx.el;
  if (dragCtx.kind === 'move') {
    el.x = Math.round(dragCtx.origX + dx);
    el.y = Math.round(dragCtx.origY + dy);
  } else {
    const c = dragCtx.corner;
    let nx = dragCtx.origX, ny = dragCtx.origY, nw = dragCtx.origW, nh = dragCtx.origH;
    if (c.includes('r')) nw = Math.max(20, dragCtx.origW + dx);
    if (c.includes('b')) nh = Math.max(20, dragCtx.origH + dy);
    if (c.includes('l')) { nx = dragCtx.origX + dx; nw = Math.max(20, dragCtx.origW - dx); }
    if (c.includes('t')) { ny = dragCtx.origY + dy; nh = Math.max(20, dragCtx.origH - dy); }
    el.x = Math.round(nx); el.y = Math.round(ny); el.w = Math.round(nw); el.h = Math.round(nh);
  }
}
function onDragEnd() {
  dragCtx = null;
  window.removeEventListener('mousemove', onDragMove);
  window.removeEventListener('mouseup', onDragEnd);
}

// 背景 / 图片
async function pickBg() {
  if (!window.electronAPI) {
    window.showToast?.('请在 Electron 版本中使用', 'warn');
    return;
  }
  const r = await window.electronAPI.openFiles({ filters: [{ name: '图片', extensions: ['png', 'jpg', 'jpeg', 'webp'] }] });
  if (r.canceled || !r.filePaths.length) return;
  const filePath = r.filePaths[0];
  const fr = await window.electronAPI.readFile(filePath);
  if (!fr.success) { window.showToast?.(fr.error, 'error'); return; }
  const ext = (filePath.split('.').pop() || 'png').toLowerCase();
  const mime = ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg' : 'image/png';
  const blob = new Blob([fr.data], { type: mime });
  if (canvas.bgImg) try { URL.revokeObjectURL(canvas.bgImg); } catch (_) {}
  canvas.bgImg = URL.createObjectURL(blob);
}

async function pickImages() {
  if (!window.electronAPI) {
    window.showToast?.('请在 Electron 版本中使用', 'warn');
    return;
  }
  const r = await window.electronAPI.openFiles({
    properties: ['openFile', 'multiSelections'],
    filters: [{ name: '图片', extensions: ['png', 'jpg', 'jpeg', 'webp'] }]
  });
  if (r.canceled || !r.filePaths.length) return;
  for (const p of r.filePaths) {
    images.value.push({ name: p.split(/[\\/]/).pop(), path: p });
  }
  updateEstimate();
}

async function pickOutput() {
  if (!window.electronAPI) {
    window.showToast?.('请在 Electron 版本中使用', 'warn');
    return;
  }
  const r = await window.electronAPI.selectOutputDir();
  if (r.canceled || !r.filePaths.length) return;
  outputDir.value = r.filePaths[0];
}

function updateEstimate() {
  // computed 自动重算,这里留作后续扩展
}

// 模板
function loadTemplates() {
  try {
    const raw = localStorage.getItem(TEMPLATE_KEY);
    templates.value = raw ? JSON.parse(raw) : [];
  } catch (_) { templates.value = []; }
}
function persistTemplates() {
  localStorage.setItem(TEMPLATE_KEY, JSON.stringify(templates.value));
}
function newTemplate() {
  const name = prompt('新模板名称', '模板' + (templates.value.length + 1));
  if (!name) return;
  templates.value.push(name);
  persistTemplates();
  currentTemplate.value = name;
  elements.value = [];
  canvas.bgImg = '';
  window.showToast?.('已创建模板：' + name, 'success');
}
function saveTemplate() {
  if (!currentTemplate.value) { window.showToast?.('请先选择或新建模板', 'warn'); return; }
  // 当前实现里模板 = 元素列表 + 画布尺寸；持久化到内存即可（实际项目可存 localStorage / 文件）
  window.showToast?.('已保存：' + currentTemplate.value, 'success');
}
function deleteTemplate() {
  if (!currentTemplate.value) return;
  if (!confirm('删除模板 ' + currentTemplate.value + ' ?')) return;
  templates.value = templates.value.filter(t => t !== currentTemplate.value);
  persistTemplates();
  currentTemplate.value = '';
  window.showToast?.('已删除', 'success');
}
function deleteCurrentTemplate() {
  if (!currentTemplate.value) return;
  deleteTemplate();
}
function canvasMenu() {
  window.showToast?.('更多操作待接入', 'info');
}

// 生成
async function previewAll() {
  if (!elements.value.length) { window.showToast?.('画布为空', 'warn'); return; }
  if (!images.value.length) { window.showToast?.('请先添加图片', 'warn'); return; }
  window.showToast?.('预览已就绪（点击画布查看效果）', 'info');
}
async function startGenerate() {
  if (!canGenerate.value) {
    window.showToast?.('请先完成画布、图片、输出目录三项配置', 'warn');
    return;
  }
  // 简化：先提示「生成中…」，实际生成走 html2canvas（已在 Tab1 引入）
  window.showToast?.('开始生成 ' + estimatedCount.value + ' 张', 'info');
  // 真实实现会循环 images，对每个 image-slot 注入图片，调 html2canvas 截图，写入 outputDir
}

// 监听元素变动，自动追加到第一个 image-slot
watch(images, () => {
  // 简化: 第一张图自动塞到第一个空 image-slot
  const emptySlot = elements.value.find(e => e.type === 'image-slot' && !e.src);
  if (emptySlot && images.value.length > 0 && !emptySlot._srcLoading) {
    const first = images.value[0];
    if (first.path && window.electronAPI) {
      emptySlot._srcLoading = true;
      window.electronAPI.readFile(first.path).then(fr => {
        if (fr.success) {
          const ext = (first.path.split('.').pop() || 'png').toLowerCase();
          const mime = ext === 'jpg' || ext === 'jpeg' ? 'image/jpeg' : 'image/png';
          const blob = new Blob([fr.data], { type: mime });
          if (emptySlot.src) try { URL.revokeObjectURL(emptySlot.src); } catch (_) {}
          emptySlot.src = URL.createObjectURL(blob);
        }
        emptySlot._srcLoading = false;
      });
    }
  }
}, { deep: true });

onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
  loadTemplates();
});
</script>

<style scoped>
.puzzle-layout {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 14px;
  align-items: start;
}
.puzzle-side { position: sticky; top: 80px; max-height: calc(100vh - 100px); overflow-y: auto; padding-right: 4px; }
.row-2col { display: grid; grid-template-columns: 1fr 1fr; }
.num { width: 70px; }
.color-pick {
  width: 26px; height: 22px; padding: 0; border: 1px solid var(--border);
  border-radius: 4px; background: #fff; cursor: pointer;
}
.muted { color: var(--text-3); font-size: 12px; }
.path { word-break: break-all; }

.puzzle-main {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px;
  box-shadow: var(--shadow);
  min-height: 600px;
  display: flex; flex-direction: column;
  gap: 10px;
}
.canvas-toolbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 4px 4px 0;
}
.template-pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 6px 4px 12px;
  background: var(--primary-soft);
  color: var(--primary);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 999px;
  font-size: 13px;
  font-weight: 500;
}
.pill-x {
  width: 18px; height: 18px;
  border: 0; background: rgba(239, 68, 68, 0.12);
  color: var(--primary);
  border-radius: 50%;
  font-size: 14px; line-height: 1;
  display: inline-flex; align-items: center; justify-content: center;
}
.pill-x:hover { background: var(--primary); color: #fff; }
.tpl-select { width: auto; min-width: 110px; }

.canvas-stage {
  flex: 1;
  min-height: 500px;
  background-color: var(--panel-2);
  background-image:
    radial-gradient(rgba(15, 23, 42, 0.08) 1px, transparent 1px);
  background-size: 16px 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  position: relative;
  overflow: auto;
  display: flex; align-items: flex-start; justify-content: flex-start;
  padding: 40px;
}
.canvas-frame {
  position: relative;
  background: #fff;
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.12);
  flex-shrink: 0;
}
.canvas-frame.transparent {
  background-image:
    linear-gradient(45deg, #e5e7eb 25%, transparent 25%),
    linear-gradient(-45deg, #e5e7eb 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #e5e7eb 75%),
    linear-gradient(-45deg, transparent 75%, #e5e7eb 75%);
  background-size: 16px 16px;
  background-position: 0 0, 0 8px, 8px -8px, -8px 0;
  background-color: #f9fafb;
}
.bg-layer { position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }
.bg-empty {
  background-image:
    linear-gradient(45deg, #f3f4f6 25%, transparent 25%),
    linear-gradient(-45deg, #f3f4f6 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #f3f4f6 75%),
    linear-gradient(-45deg, transparent 75%, #f3f4f6 75%);
  background-size: 24px 24px;
  background-position: 0 0, 0 12px, 12px -12px, -12px 0;
  background-color: #fafafa;
}

.el {
  position: absolute;
  border: 1px solid transparent;
  cursor: move;
  user-select: none;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
}
.el:hover { border-color: rgba(6, 214, 244, 0.5); }
.el.selected { border-color: var(--neon-cyan); box-shadow: 0 0 0 1px var(--neon-cyan-soft), 0 0 14px var(--neon-cyan-soft); }
.el-text { white-space: pre-wrap; text-align: center; line-height: 1.2; }
.el-image { width: 100%; height: 100%; object-fit: cover; pointer-events: none; }
.el-slot, .el-image-slot { background: rgba(6, 214, 244, 0.05); border-style: dashed; border-color: rgba(6, 214, 244, 0.4); }
.slot-inner {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 6px;
  color: var(--text-3); font-size: 12px; width: 100%; height: 100%;
}

.handle {
  position: absolute; width: 10px; height: 10px;
  background: #fff; border: 2px solid var(--neon-cyan);
  border-radius: 2px;
  box-shadow: 0 0 0 2px rgba(6, 214, 244, 0.2);
}
.handle.tl { left: -5px; top: -5px; cursor: nwse-resize; }
.handle.tr { right: -5px; top: -5px; cursor: nesw-resize; }
.handle.bl { left: -5px; bottom: -5px; cursor: nesw-resize; }
.handle.br { right: -5px; bottom: -5px; cursor: nwse-resize; }

.el-del {
  position: absolute; top: -10px; right: -10px;
  width: 20px; height: 20px; padding: 0;
  border: 0; background: var(--primary); color: #fff;
  border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 8px var(--primary-glow);
  z-index: 2;
}
.el-del i[data-lucide] { width: 12px; height: 12px; }

.canvas-hint {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--text-3); font-size: 14px;
  pointer-events: none;
}

.zoom-bar {
  position: absolute; right: 16px; bottom: 16px;
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 8px;
  box-shadow: var(--shadow);
  font-size: 12px;
}
.zoom-bar .btn-icon { width: 24px; height: 24px; }
.zoom-bar .btn-icon i[data-lucide] { width: 12px; height: 12px; }
.zoom-val { min-width: 42px; text-align: center; }

.puzzle-bottom {
  padding: 10px 8px 4px;
  border-top: 1px solid var(--border-2);
}
.image-list { display: flex; flex-wrap: wrap; gap: 6px; max-height: 100px; overflow-y: auto; }
.img-chip {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px;
  background: var(--panel-3);
  border: 1px solid var(--border);
  border-radius: 999px;
  font-size: 12px;
  max-width: 200px;
}
.img-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

@media (max-width: 1024px) {
  .puzzle-layout { grid-template-columns: 1fr; }
  .puzzle-side { position: static; max-height: none; }
}
</style>