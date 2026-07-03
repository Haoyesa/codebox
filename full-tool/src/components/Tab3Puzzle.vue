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
          <div class="row" style="margin-top: 10px; gap: 6px; font-size: 12px;">
            <span class="muted" style="flex-shrink: 0;">宽</span><input type="number" v-model.number="canvas.width" min="50" max="4096" class="num" />
            <span class="muted" style="flex-shrink: 0;">高</span><input type="number" v-model.number="canvas.height" min="50" max="4096" class="num" />
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

        <!-- 批量操作 -->
        <div v-if="isMultiSelect" class="section-block batch-panel">
          <h4 class="section-title">
            <i data-lucide="layers"></i>批量操作
            <span class="tag tag-cyan" style="font-size:11px;margin-left:6px;">{{ selectedIds.length }} 个</span>
          </h4>
          <div class="batch-grid">
            <button class="btn btn-xs" @click="alignSelected('left')" title="左对齐">
              <i data-lucide="align-left"></i>
            </button>
            <button class="btn btn-xs" @click="alignSelected('hcenter')" title="水平居中">
              <i data-lucide="align-center"></i>
            </button>
            <button class="btn btn-xs" @click="alignSelected('right')" title="右对齐">
              <i data-lucide="align-right"></i>
            </button>
            <button class="btn btn-xs" @click="alignSelected('top')" title="上对齐">
              <i data-lucide="align-start-vertical"></i>
            </button>
            <button class="btn btn-xs" @click="alignSelected('vcenter')" title="垂直居中">
              <i data-lucide="align-center-vertical"></i>
            </button>
            <button class="btn btn-xs" @click="alignSelected('bottom')" title="下对齐">
              <i data-lucide="align-end-vertical"></i>
            </button>
          </div>
          <div class="row" style="gap: 6px; margin-top: 10px;">
            <button class="btn btn-xs" @click="resizeSelected('max')">统一最大</button>
            <button class="btn btn-xs" @click="resizeSelected('min')">统一最小</button>
            <button class="btn btn-xs" @click="resizeSelected('avg')">统一平均</button>
          </div>
          <button class="btn btn-xs btn-ghost btn-block" style="margin-top: 10px; color: var(--primary);" @click="removeSelected">
            <i data-lucide="trash-2"></i>删除选中
          </button>
        </div>

        <div class="section-block">
          <h4 class="section-title">文件操作</h4>
          <div class="row" style="gap: 6px; flex-wrap: wrap;">
            <button class="btn btn-sm" @click="addImageFolder">
              <i data-lucide="folder-plus"></i>添加图片文件夹
            </button>
            <button class="btn btn-sm" @click="pickOutput">输出目录</button>
          </div>
          <div class="muted path" style="margin-top: 8px; font-size: 12px;" :title="outputDir">
            {{ outputDir || '未设置' }}
          </div>

          <div v-if="imageFolders.length" class="img-folder-list" style="margin-top: 10px;">
            <div v-for="(f, i) in imageFolders" :key="f.id" class="img-folder-row">
              <span class="img-folder-idx mono">#{{ i + 1 }}</span>
              <span class="img-folder-path mono" :title="f.path">{{ f.path }}</span>
              <span class="muted mono" style="font-size: 11px;">{{ f.files.length }} 张</span>
              <button class="btn-icon" @click="removeImageFolder(f.id)" title="移除">
                <i data-lucide="x"></i>
              </button>
            </div>
            <button class="btn btn-sm btn-ghost btn-block" style="margin-top: 4px; font-size: 11px;" @click="clearImageFolders">清空全部图片文件夹</button>
          </div>
          <div v-else class="muted" style="margin-top: 10px; font-size: 12px;">
            单一模式：选 1 个文件夹循环；多文件夹模式：按顺序选多个文件夹，每张拼图依次取对应文件夹的第 r 张图（独立循环）。
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
            <button class="btn btn-sm btn-primary" @click="startGenerate" :disabled="!canGenerate || isGenerating">
              <i data-lucide="play"></i>{{ isGenerating ? '生成中 ' + genDone + '/' + genTotal : '开始生成' }}
            </button>
            <button v-if="isGenerating" class="btn btn-sm btn-warn" @click="cancelGenerate">停止</button>
          </div>
          <div class="muted" style="margin-top: 8px; font-size: 12px;">
            {{ isGenerating ? genStatus : templateHint }}
          </div>
          <div v-if="isGenerating" class="progress-bar" style="margin-top: 6px;">
            <div class="fill" :style="{ width: (genTotal ? (genDone / genTotal * 100) : 0) + '%' }"></div>
          </div>
        </div>
      </aside>

      <!-- 中心画布 -->
      <div class="puzzle-main">
        <div class="canvas-toolbar">
          <div class="row" style="gap: 8px;">
            <span class="template-pill" :class="{ dirty: isDirty }">
              {{ currentTemplate || '未选择模板' }}
              <span v-if="isDirty" class="pill-dot" title="有未保存的改动"></span>
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
            <div class="menu-anchor" ref="canvasMenuAnchorRef">
              <button class="btn-icon" @click="canvasMenu"><i data-lucide="more-horizontal"></i></button>
              <div v-if="canvasMenuOpen" class="menu-pop" @click.stop>
                <button class="menu-item" @click="fitToView"><i data-lucide="maximize-2"></i><span>适应窗口</span></button>
                <button class="menu-item" :disabled="!selectedId" @click="duplicateSelected"><i data-lucide="copy"></i><span>复制选中</span></button>
                <button class="menu-item" :disabled="!selectedId" @click="bringToFront"><i data-lucide="bring-to-front"></i><span>置于顶层</span></button>
                <button class="menu-item" :disabled="!selectedId" @click="sendToBack"><i data-lucide="send-to-back"></i><span>置于底层</span></button>
                <div class="menu-divider"></div>
                <button class="menu-item" @click="clearAllElements"><i data-lucide="trash-2"></i><span>清空画布</span></button>
                <div class="menu-divider"></div>
                <button class="menu-item" @click="exportTemplateJson"><i data-lucide="download"></i><span>导出 JSON</span></button>
                <button class="menu-item" @click="importTemplateJson"><i data-lucide="upload"></i><span>导入 JSON</span></button>
              </div>
            </div>
          </div>
        </div>

        <div class="canvas-stage" ref="stageRef" @wheel.prevent="onWheel" @mousedown.self="onStageClick">
          <div
          class="canvas-frame"
          :class="{ transparent: canvas.transparent, dragging: isDragging }"
          :style="frameStyle"
          @dragover.prevent="onDragOver"
          @dragleave="onDragLeave"
          @drop.prevent="onDrop"
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
              :class="['el-' + el.type, { selected: selectedId === el.id || selectedIds.includes(el.id) }]"
              :style="elStyle(el)"
              @mousedown.stop="startDrag($event, el)"
              @click.stop="select(el.id, $event)"
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
              <div class="hint-inner">
                <i data-lucide="layout-template"></i>
                <p class="hint-title">开始设计拼图模板</p>
                <p class="hint-sub">点击左侧「添加坑位」或「添加图片」</p>
              </div>
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
            <button class="btn btn-sm btn-ghost" @click="clearImageFolders">清空全部</button>
          </div>

          <!-- 批量重命名 -->
          <div v-if="images.length" class="rename-bar">
            <div class="row" style="gap: 8px; align-items: center;">
              <input v-model="renamePattern" placeholder="命名规则，如 product_{n}" class="rename-input" />
              <button class="btn btn-sm" @click="applyRename">应用重命名</button>
            </div>
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

    <!-- 预览弹窗 -->
    <Teleport to="body">
      <div v-if="showPreviewModal" class="modal-backdrop" @click.self="closePreview">
        <div class="modal modal-preview" role="dialog" aria-modal="true">
          <div class="modal-head">
            <h4 class="modal-title">预览</h4>
            <span class="muted" style="font-size: 12px;">单文件夹取首张，多文件夹按规则取第 0 张</span>
            <button class="btn-icon modal-close" @click="closePreview" title="关闭（ESC）"><i data-lucide="x"></i></button>
          </div>
          <div class="modal-body preview-body">
            <img v-if="previewUrl" :src="previewUrl" class="preview-img" alt="preview" />
          </div>
          <div class="modal-foot">
            <span class="muted mono" style="font-size: 11px;">{{ canvas.width }} × {{ canvas.height }}</span>
            <div class="row" style="gap: 8px;">
              <button class="btn btn-sm" @click="closePreview">关闭</button>
              <a v-if="previewUrl" :href="previewUrl" download="预览.png" class="btn btn-sm btn-primary">下载预览</a>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue';
import html2canvas from 'html2canvas';
import { getExt, getMimeFromPath, safeOutputDir } from '../utils/file.js';
import { yieldToMain } from '../utils/format.js';
import { useSettings } from '../composables/useSettings.js';
import { useToast } from '../composables/useToast.js';

const toast = useToast();

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
const selectedIds = ref([]); // 多选数组
const isMultiSelect = computed(() => selectedIds.value.length > 0);
let nextId = 1;

const stageRef = ref(null);

// 规则
const rule = reactive({ mode: 'single', firstAsCover: false, scale: '1' });

// 图片 / 输出
// imageFolders is the source of truth; `images` is a flat computed used by the UI.
const imageFolders = ref([]); // {id, path, recursive, files: [{name, path}]}
let folderId = 1;
const images = computed(() => {
  const out = [];
  imageFolders.value.forEach((f, idx) => {
    f.files.forEach(file => out.push({ ...file, folderIdx: idx, folderId: f.id }));
  });
  return out;
});
const outputDir = ref('');

// preview modal state
const previewUrl = ref('');
const showPreviewModal = ref(false);

// canvas menu state
const canvasMenuOpen = ref(false);
const isDragging = ref(false);

// generation state
const isGenerating = ref(false);
const abortGen = ref(false);
const genDone = ref(0);
const genTotal = ref(0);
const genStatus = ref('');

// 模板 (names list + per-name data)
const TEMPLATE_KEY = 'fulltool_puzzle_templates';
const TEMPLATE_DATA_KEY = 'fulltool_puzzle_template_data';
const currentTemplate = ref('');
const templates = ref([]);
// JSON snapshot of the current template's last persisted state. Drives isDirty and
// lets us auto-save the outgoing template when the user switches via the dropdown.
const lastSavedSnapshot = ref('');
// Used to anchor the more-horizontal dropdown so click-outside-to-close works.
const canvasMenuAnchorRef = ref(null);

// 批量重命名
const renamePattern = ref('');

function serializeCurrent() {
  return JSON.stringify({
    canvas: {
      width: canvas.width,
      height: canvas.height,
      transparent: canvas.transparent,
      solidBg: canvas.solidBg,
      bgColor: canvas.bgColor
    },
    elements: elements.value.map(e => {
      const c = { ...e };
      if (c.type === 'image-slot' || c.type === 'image') c.src = '';
      return c;
    })
  });
}

function loadAllTemplateData() {
  try { return JSON.parse(localStorage.getItem(TEMPLATE_DATA_KEY) || '{}'); } catch (_) { return {}; }
}
function persistAllTemplateData(map) {
  try { localStorage.setItem(TEMPLATE_DATA_KEY, JSON.stringify(map)); } catch (_) {}
}

const estimatedCount = computed(() => {
  if (imageFolders.value.length === 0) return 0;
  if (rule.mode === 'single') {
    const n = imageFolders.value[0].files.length;
    return rule.firstAsCover ? (n > 0 ? 1 : 0) : n;
  }
  return imageFolders.value.reduce((m, f) => Math.max(m, f.files.length), 0);
});

const canGenerate = computed(() => {
  return elements.value.length > 0 && images.value.length > 0 && outputDir.value;
});

const templateHint = computed(() => {
  if (templates.value.length === 0) return '未选择模板';
  if (!currentTemplate.value) return '未选择模板';
  return '当前：' + currentTemplate.value;
});

// True when the current canvas/elements differ from the last persisted snapshot.
const isDirty = computed(() => {
  if (!currentTemplate.value) return elements.value.length > 0;
  return serializeCurrent() !== lastSavedSnapshot.value;
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
  selectedIds.value = [];
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
    toast.show('请在 Electron 版本中添加装饰图', 'warn');
    return;
  }
  const r = await window.electronAPI.openFiles({ filters: [{ name: '图片', extensions: ['png', 'jpg', 'jpeg', 'webp', 'svg'] }] });
  if (r.canceled || !r.filePaths.length) return;
  const filePath = r.filePaths[0];
  try {
    const fr = await window.electronAPI.readFile(filePath);
    if (!fr.success) throw new Error(fr.error);
    const mime = getMimeFromPath(filePath);
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
    toast.show('读取图片失败：' + err.message, 'error');
  }
}
function clearImages() {
  elements.value = elements.value.filter(e => e.type !== 'image');
}

// Drag & drop images onto canvas
function onDragOver(e) {
  e.preventDefault();
  isDragging.value = true;
}
function onDragLeave(e) {
  if (!e.currentTarget.contains(e.relatedTarget)) {
    isDragging.value = false;
  }
}
async function onDrop(e) {
  e.preventDefault();
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (!files || files.length === 0) return;

  const imgExts = ['png', 'jpg', 'jpeg', 'webp', 'svg', 'gif', 'bmp'];
  let addedCount = 0;

  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    if (!imgExts.includes(ext)) continue;

    try {
      let url;
      if (window.electronAPI && file.path) {
        const fr = await window.electronAPI.readFile(file.path);
        if (!fr.success) throw new Error(fr.error);
        const mime = getMimeFromPath(file.path);
        const blob = new Blob([fr.data], { type: mime });
        url = URL.createObjectURL(blob);
      } else {
        url = await new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.onerror = reject;
          reader.readAsDataURL(file);
        });
      }

      const img = new Image();
      await new Promise((resolve, reject) => {
        img.onload = resolve;
        img.onerror = reject;
        img.src = url;
      });

      const maxW = canvas.width * 0.4;
      const maxH = canvas.height * 0.3;
      const ratio = Math.min(maxW / img.width, maxH / img.height, 1);
      elements.value.push({
        id: newId(),
        type: 'image',
        src: url,
        x: 40 + addedCount * 20,
        y: 40 + addedCount * 20,
        w: img.width * ratio,
        h: img.height * ratio
      });
      addedCount++;
    } catch (err) {
      console.error('Drop image failed:', err);
      toast.show('添加图片失败：' + file.name, 'error');
    }
  }

  if (addedCount > 0) {
    const last = elements.value[elements.value.length - 1];
    selectedId.value = last.id;
    toast.show(`已添加 ${addedCount} 张图片`, 'success');
  }
}

function select(id, event) {
  if (event && (event.ctrlKey || event.metaKey)) {
    // Ctrl/Cmd + 点击：切换多选
    const arr = selectedIds.value.slice();
    const idx = arr.indexOf(id);
    if (idx >= 0) arr.splice(idx, 1);
    else arr.push(id);
    selectedIds.value = arr;
    selectedId.value = id;
  } else if (event && event.shiftKey && selectedId.value) {
    // Shift + 点击：范围选择（基于 elements 数组顺序）
    const ids = elements.value.map(e => e.id);
    const from = ids.indexOf(selectedId.value);
    const to = ids.indexOf(id);
    if (from !== -1 && to !== -1) {
      const start = Math.min(from, to);
      const end = Math.max(from, to);
      const arr = selectedIds.value.slice();
      for (let i = start; i <= end; i++) {
        if (!arr.includes(ids[i])) arr.push(ids[i]);
      }
      selectedIds.value = arr;
      selectedId.value = id;
    }
  } else {
    // 普通点击：单选，清空多选
    selectedId.value = id;
    selectedIds.value = [];
  }
}
function removeEl(id) {
  elements.value = elements.value.filter(e => e.id !== id);
  if (selectedId.value === id) selectedId.value = null;
  selectedIds.value = selectedIds.value.filter(x => x !== id);
}

// 批量删除
async function removeSelected() {
  const ids = selectedIds.value;
  if (ids.length === 0) return;
  if (!(await window.appConfirm({ title: '删除确认', message: `确定删除选中的 ${ids.length} 个元素？`, type: 'warning' }))) return;
  elements.value = elements.value.filter(e => !ids.includes(e.id));
  selectedIds.value = [];
  selectedId.value = null;
}

// 批量对齐
function alignSelected(direction) {
  const targets = elements.value.filter(e => selectedIds.value.includes(e.id));
  if (targets.length < 2) { toast.show('请至少选中 2 个元素', 'warn'); return; }
  switch (direction) {
    case 'left': {
      const min = Math.min(...targets.map(e => e.x));
      targets.forEach(e => e.x = min);
      break;
    }
    case 'right': {
      const max = Math.max(...targets.map(e => e.x + e.w));
      targets.forEach(e => e.x = max - e.w);
      break;
    }
    case 'top': {
      const min = Math.min(...targets.map(e => e.y));
      targets.forEach(e => e.y = min);
      break;
    }
    case 'bottom': {
      const max = Math.max(...targets.map(e => e.y + e.h));
      targets.forEach(e => e.y = max - e.h);
      break;
    }
    case 'hcenter': {
      const min = Math.min(...targets.map(e => e.x));
      const max = Math.max(...targets.map(e => e.x + e.w));
      const center = (min + max) / 2;
      targets.forEach(e => e.x = center - e.w / 2);
      break;
    }
    case 'vcenter': {
      const min = Math.min(...targets.map(e => e.y));
      const max = Math.max(...targets.map(e => e.y + e.h));
      const center = (min + max) / 2;
      targets.forEach(e => e.y = center - e.h / 2);
      break;
    }
  }
  toast.show('对齐完成', 'success');
}

// 批量统一尺寸
function resizeSelected(mode) {
  const targets = elements.value.filter(e => selectedIds.value.includes(e.id));
  if (targets.length < 2) { toast.show('请至少选中 2 个元素', 'warn'); return; }
  if (mode === 'max') {
    const maxW = Math.max(...targets.map(e => e.w));
    const maxH = Math.max(...targets.map(e => e.h));
    targets.forEach(e => { e.w = maxW; e.h = maxH; });
  } else if (mode === 'min') {
    const minW = Math.min(...targets.map(e => e.w));
    const minH = Math.min(...targets.map(e => e.h));
    targets.forEach(e => { e.w = minW; e.h = minH; });
  } else if (mode === 'avg') {
    const avgW = Math.round(targets.reduce((s, e) => s + e.w, 0) / targets.length);
    const avgH = Math.round(targets.reduce((s, e) => s + e.h, 0) / targets.length);
    targets.forEach(e => { e.w = avgW; e.h = avgH; });
  }
  toast.show('尺寸已统一', 'success');
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
    toast.show('请在 Electron 版本中使用', 'warn');
    return;
  }
  const r = await window.electronAPI.openFiles({ filters: [{ name: '图片', extensions: ['png', 'jpg', 'jpeg', 'webp'] }] });
  if (r.canceled || !r.filePaths.length) return;
  const filePath = r.filePaths[0];
  const fr = await window.electronAPI.readFile(filePath);
  if (!fr.success) { toast.show(fr.error, 'error'); return; }
  const mime = getMimeFromPath(filePath);
  const blob = new Blob([fr.data], { type: mime });
  if (canvas.bgImg) try { URL.revokeObjectURL(canvas.bgImg); } catch (_) {}
  canvas.bgImg = URL.createObjectURL(blob);
}

async function addImageFolder() {
  if (!window.electronAPI) {
    toast.show('请在 Electron 版本中使用', 'warn');
    return;
  }
  if (rule.mode === 'single' && imageFolders.value.length >= 1) {
    toast.show('单一文件夹模式：只能添加 1 个文件夹，请先清空', 'warn');
    return;
  }
  const r = await window.electronAPI.openDirectory();
  if (r.canceled || !r.filePaths.length) return;
  await loadImageFolder(r.filePaths[0], true);
}

async function loadImageFolder(dirPath, recursive) {
  const r = await window.electronAPI.readDir(dirPath, {
    recursive,
    extensions: ['png', 'jpg', 'jpeg', 'webp', 'gif', 'bmp']
  });
  if (!r.success) { toast.show(r.error, 'error'); return; }
  const sorted = r.files.slice().sort((a, b) => a.localeCompare(b, 'zh-Hans-CN', { numeric: true }));
  const sep = dirPath.includes('\\') ? '\\' : '/';
  const base = dirPath.replace(/[\\/]+$/, '');
  imageFolders.value.push({
    id: folderId++,
    path: dirPath,
    recursive,
    files: sorted.map(name => ({ name, path: base + sep + name }))
  });
  toast.show('已添加：' + sorted.length + ' 张图片', 'success');
}

function removeImageFolder(id) {
  imageFolders.value = imageFolders.value.filter(f => f.id !== id);
}

async function clearImageFolders() {
  imageFolders.value = [];
}

async function pickOutput() {
  if (!window.electronAPI) {
    toast.show('请在 Electron 版本中使用', 'warn');
    return;
  }
  const r = await window.electronAPI.selectOutputDir();
  if (r.canceled || !r.filePaths.length) return;
  outputDir.value = r.filePaths[0];
}

function updateEstimate() { /* computed handles it */ }

// Watch for template changes to load the saved state.
watch(currentTemplate, (name) => { if (name) loadTemplate(name); });
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
  if (templates.value.includes(name)) {
    toast.show('已存在同名模板', 'warn'); return;
  }
  templates.value.push(name);
  persistTemplates();
  // Start with a clean canvas; nothing to restore yet.
  elements.value = [];
  canvas.bgImg = '';
  currentTemplate.value = name;
  toast.show('已创建模板：' + name, 'success');
}
function saveTemplate() {
  if (!currentTemplate.value) { toast.show('请先选择或新建模板', 'warn'); return; }
  // Persist canvas dims + bg color/transparent flag (not the bgImg blob URL, which dies on reload).
  const snapshot = {
    canvas: {
      width: canvas.width,
      height: canvas.height,
      transparent: canvas.transparent,
      solidBg: canvas.solidBg,
      bgColor: canvas.bgColor
    },
    // Strip image-slot srcs (blob URLs do not survive a reload).
    elements: elements.value.map(e => {
      const c = { ...e };
      if (c.type === 'image-slot' || c.type === 'image') c.src = '';
      return c;
    })
  };
  const all = loadAllTemplateData();
  all[currentTemplate.value] = snapshot;
  persistAllTemplateData(all);
  lastSavedSnapshot.value = serializeCurrent();
  toast.show('已保存：' + currentTemplate.value, 'success');
}

function loadTemplate(name) {
  if (!name) return;
  // Auto-persist the outgoing template's current state if it has unsaved changes,
  // so the user can always revert by re-selecting the template from the dropdown.
  const outgoingName = currentTemplate.value;
  if (outgoingName && outgoingName !== name && templates.value.includes(outgoingName)) {
    const outgoingJson = serializeCurrent();
    if (outgoingJson !== lastSavedSnapshot.value) {
      const all = loadAllTemplateData();
      all[outgoingName] = JSON.parse(outgoingJson);
      persistAllTemplateData(all);
    }
  }
  // Hard reset first so we don't leak blob URLs from the previous template.
  for (const el of elements.value) {
    if ((el.type === 'image-slot' || el.type === 'image') && el.src) {
      try { URL.revokeObjectURL(el.src); } catch (_) {}
    }
  }
  elements.value = [];
  canvas.bgImg = '';
  selectedId.value = null;
  slotCount = 0;
  const all = loadAllTemplateData();
  const snap = all[name];
  if (snap && snap.canvas) Object.assign(canvas, snap.canvas);
  if (snap && Array.isArray(snap.elements)) {
    elements.value = snap.elements;
    for (const el of elements.value) {
      if (el.type === 'slot' || el.type === 'image-slot') {
        if (typeof el.index === 'number' && el.index > slotCount) slotCount = el.index;
      }
    }
  }
  // Reset baseline so the dirty dot clears after a switch.
  lastSavedSnapshot.value = serializeCurrent();
}
async function deleteTemplate() {
  if (!currentTemplate.value) return;
  if (!(await window.appConfirm({ title: '删除模板', message: '删除模板 ' + currentTemplate.value + ' ?', type: 'warning' }))) return;
  const name = currentTemplate.value;
  templates.value = templates.value.filter(t => t !== name);
  persistTemplates();
  const all = loadAllTemplateData();
  delete all[name];
  persistAllTemplateData(all);
  currentTemplate.value = '';
  toast.show('已删除', 'success');
}
function deleteCurrentTemplate() {
  if (!currentTemplate.value) return;
  deleteTemplate();
}
function canvasMenu() {
  canvasMenuOpen.value = !canvasMenuOpen.value;
  if (canvasMenuOpen.value) {
    // Defer so the click that opened the menu doesn't immediately close it.
    setTimeout(() => document.addEventListener('mousedown', onDocClickCloseMenu, true), 0);
  } else {
    document.removeEventListener('mousedown', onDocClickCloseMenu, true);
  }
}
function onDocClickCloseMenu(e) {
  if (!canvasMenuOpen.value) return;
  const anchor = canvasMenuAnchorRef.value;
  if (anchor && !anchor.contains(e.target)) closeCanvasMenu();
}
function onKeydown(e) {
  if (e.key === 'Escape' && showPreviewModal.value) closePreview();
}
function closeCanvasMenu() {
  canvasMenuOpen.value = false;
  document.removeEventListener('mousedown', onDocClickCloseMenu, true);
}

async function clearAllElements() {
  if (elements.value.length === 0) return;
  if (!(await window.appConfirm({ title: '清空画布', message: '清空画布上所有元素？此操作不影响模板本身。', type: 'warning' }))) return;
  for (const el of elements.value) {
    if ((el.type === 'image-slot' || el.type === 'image') && el.src) {
      try { URL.revokeObjectURL(el.src); } catch (_) {}
    }
  }
  elements.value = [];
  selectedId.value = null;
  closeCanvasMenu();
}

function fitToView() {
  const stage = stageRef.value;
  if (!stage) return;
  const padding = 80;
  const sw = stage.clientWidth - padding;
  const sh = stage.clientHeight - padding;
  if (sw <= 0 || sh <= 0) return;
  const z = Math.max(0.1, Math.min(2, Math.min(sw / canvas.width, sh / canvas.height)));
  zoom.value = z;
  closeCanvasMenu();
}

function duplicateSelected() {
  if (!selectedId.value) return;
  const idx = elements.value.findIndex(e => e.id === selectedId.value);
  if (idx < 0) return;
  const src = elements.value[idx];
  const copy = { ...src, id: newId(), x: src.x + 20, y: src.y + 20 };
  if (src.type === 'slot' || src.type === 'image-slot') {
    copy.index = ++slotCount;
  }
  elements.value.push(copy);
  selectedId.value = copy.id;
  closeCanvasMenu();
}

function bringToFront() {
  if (!selectedId.value) return;
  const idx = elements.value.findIndex(e => e.id === selectedId.value);
  if (idx < 0 || idx === elements.value.length - 1) return;
  const [el] = elements.value.splice(idx, 1);
  elements.value.push(el);
  closeCanvasMenu();
}

function sendToBack() {
  if (!selectedId.value) return;
  const idx = elements.value.findIndex(e => e.id === selectedId.value);
  if (idx <= 0) return;
  const [el] = elements.value.splice(idx, 1);
  elements.value.unshift(el);
  closeCanvasMenu();
}

async function exportTemplateJson() {
  const data = {
    name: currentTemplate.value || 'untitled',
    canvas: {
      width: canvas.width, height: canvas.height,
      transparent: canvas.transparent, solidBg: canvas.solidBg, bgColor: canvas.bgColor
    },
    elements: elements.value.map(e => { const c = { ...e }; if (c.type === 'image-slot' || c.type === 'image') c.src = ''; return c; })
  };
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = (data.name || 'template') + '.json'; a.click();
  URL.revokeObjectURL(url);
  toast.show('已导出 JSON', 'success');
  closeCanvasMenu();
}

async function importTemplateJson() {
  if (!window.electronAPI) {
    const inp = document.createElement('input');
    inp.type = 'file'; inp.accept = 'application/json';
    inp.onchange = () => {
      const f = inp.files && inp.files[0];
      if (!f) return;
      const reader = new FileReader();
      reader.onload = () => applyTemplateJson(String(reader.result));
      reader.readAsText(f);
    };
    inp.click();
    return;
  }
  const r = await window.electronAPI.openFiles({ filters: [{ name: 'JSON', extensions: ['json'] }] });
  if (r.canceled || !r.filePaths.length) return;
  const fr = await window.electronAPI.readFile(r.filePaths[0]);
  if (!fr.success) { toast.show(fr.error, 'error'); return; }
  applyTemplateJson(new TextDecoder('utf-8').decode(new Uint8Array(fr.data)));
  closeCanvasMenu();
}

function applyTemplateJson(text) {
  try {
    const data = JSON.parse(text);
    if (data.canvas) Object.assign(canvas, data.canvas);
    if (Array.isArray(data.elements)) {
      elements.value = data.elements.map(e => {
        const c = { ...e }; c.id = newId();
        if (c.type === 'image-slot' || c.type === 'image') c.src = '';
        return c;
      });
      slotCount = elements.value.reduce((m, e) => (e.type === 'image-slot' || e.type === 'slot') ? Math.max(m, e.index || 0) : m, 0);
      toast.show('已导入 JSON', 'success');
    }
  } catch (e) {
    toast.show('JSON 解析失败：' + e.message, 'error');
  }
}

// 生成
async function previewAll() {
  if (!elements.value.length) { toast.show('画布为空', 'warn'); return; }
  if (imageFolders.value.length === 0 || imageFolders.value[0].files.length === 0) {
    toast.show('请先添加图片文件夹', 'warn'); return;
  }
  const frame = document.querySelector('.canvas-frame');
  if (!frame) return;
  // Fill every image-slot with the first folder's first image (r=0). Multi-folder preview
  // uses each folder's index-0 image for the matching slot.
  const slots = elements.value.filter(e => e.type === 'image-slot');
  const savedZoom = zoom.value;
  const prevSrcs = new Map(slots.map(s => [s.id, s.src]));
  try {
    for (let i = 0; i < slots.length; i++) {
      const folder = rule.mode === 'single'
        ? imageFolders.value[0]
        : (imageFolders.value[Math.min(i, imageFolders.value.length - 1)] || imageFolders.value[0]);
      if (!folder || !folder.files.length) continue;
      const f = folder.files[0];
      const fr = await window.electronAPI.readFile(f.path);
      if (!fr.success) continue;
      const mime = getMimeFromPath(f.path);
      const blob = new Blob([fr.data], { type: mime });
      const url = URL.createObjectURL(blob);
      await new Promise((resolve, reject) => {
        const probe = new Image(); probe.onload = resolve; probe.onerror = reject; probe.src = url;
      });
      if (slots[i].src) try { URL.revokeObjectURL(slots[i].src); } catch (_) {}
      slots[i].src = url;
    }
    zoom.value = 1;
    await nextTick();
    await yieldToMain();
    const out = await html2canvas(frame, {
      backgroundColor: canvas.transparent ? null : (canvas.solidBg ? canvas.bgColor : '#ffffff'),
      scale: 1, logging: false, useCORS: true, allowTaint: true
    });
    const blob = await new Promise(r => out.toBlob(r, 'image/png'));
    if (previewUrl.value) try { URL.revokeObjectURL(previewUrl.value); } catch (_) {}
    previewUrl.value = URL.createObjectURL(blob);
    showPreviewModal.value = true;
  } catch (err) {
    toast.show('预览失败：' + err.message, 'error');
  } finally {
    for (const slot of slots) {
      const prev = prevSrcs.get(slot.id);
      if (slot.src && slot.src !== prev) try { URL.revokeObjectURL(slot.src); } catch (_) {}
      slot.src = prev || '';
    }
    zoom.value = savedZoom;
  }
}

function closePreview() {
  if (previewUrl.value) try { URL.revokeObjectURL(previewUrl.value); } catch (_) {}
  previewUrl.value = '';
  showPreviewModal.value = false;
}
async function startGenerate() {
  if (!canGenerate.value) {
    toast.show('请先完成模板、图片文件夹、输出目录三项配置', 'warn');
    return;
  }
  const total = estimatedCount.value;
  if (total === 0) { toast.show('没有可生成的图片', 'warn'); return; }

  const slots = elements.value.filter(e => e.type === 'image-slot');
  if (rule.mode === 'multi' && slots.length === 0) {
    toast.show('多文件夹模式：模板里没有图片坑位', 'warn'); return;
  }

  const frame = document.querySelector('.canvas-frame');
  if (!frame) { toast.show('画布节点未找到', 'error'); return; }

  const savedZoom = zoom.value;
  isGenerating.value = true;
  abortGen.value = false;
  genDone.value = 0;
  genTotal.value = total;
  genStatus.value = '准备中…';

  const prevSrcs = new Map(slots.map(s => [s.id, s.src]));

  try {
    zoom.value = 1;
    await nextTick();

    for (let r = 0; r < total; r++) {
      if (abortGen.value) break;
      genStatus.value = `生成 ${r + 1} / ${total}`;

      for (let i = 0; i < slots.length; i++) {
        const slot = slots[i];
        let chosen = null;
        if (rule.mode === 'single') {
          const f = imageFolders.value[0];
          if (f && f.files.length) chosen = f.files[r % f.files.length];
        } else {
          const f = imageFolders.value[Math.min(i, imageFolders.value.length - 1)];
          if (f && f.files.length) chosen = f.files[r % f.files.length];
        }
        if (chosen) {
          const fr = await window.electronAPI.readFile(chosen.path);
          if (fr.success) {
            const mime = getMimeFromPath(chosen.path);
            const blob = new Blob([fr.data], { type: mime });
            const url = URL.createObjectURL(blob);
            await new Promise((resolve, reject) => {
              const probe = new Image();
              probe.onload = resolve; probe.onerror = reject;
              probe.src = url;
            });
            if (slot.src) try { URL.revokeObjectURL(slot.src); } catch (_) {}
            slot.src = url;
          }
        } else {
          if (slot.src) try { URL.revokeObjectURL(slot.src); } catch (_) {}
          slot.src = '';
        }
      }

      await nextTick();
      await yieldToMain();

      const out = await html2canvas(frame, {
        backgroundColor: canvas.transparent ? null : (canvas.solidBg ? canvas.bgColor : '#ffffff'),
        scale: Number(rule.scale) || 1,
        logging: false,
        useCORS: true,
        allowTaint: true
      });
      const blob = await new Promise(r => out.toBlob(r, 'image/png'));
      const ab = await blob.arrayBuffer();
      const idx = String(r + 1).padStart(3, '0');
      const name = `拼图_${idx}.png`;
      await window.electronAPI.writeFile(safeOutputDir(outputDir.value) + '/' + name, new Uint8Array(ab));
      genDone.value = r + 1;

      // Yield every 5 iterations to keep UI responsive
      if (r % 5 === 4) await yieldToMain();
    }
  } catch (err) {
    toast.show('生成失败：' + err.message, 'error');
  } finally {
    for (const slot of slots) {
      const prev = prevSrcs.get(slot.id);
      if (slot.src && slot.src !== prev) try { URL.revokeObjectURL(slot.src); } catch (_) {}
      slot.src = prev || '';
    }
    zoom.value = savedZoom;
    isGenerating.value = false;
    const wasAbort = abortGen.value;
    abortGen.value = false;
    genStatus.value = wasAbort ? `已停止（${genDone.value} / ${total}）` : `完成 ${genDone.value} 张`;
    toast.show(genStatus.value, wasAbort ? 'warn' : 'success');
  }
}

function cancelGenerate() { abortGen.value = true; genStatus.value = '正在停止…'; }

function applyRename() {
  const pattern = renamePattern.value.trim();
  if (!pattern) { toast.show('请输入命名规则', 'warn'); return; }
  if (imageFolders.value.length === 0) { toast.show('没有可重命名的图片', 'warn'); return; }

  let n = 1;
  const regex = /\{n(?::(\d+))?\}/g;

  for (const folder of imageFolders.value) {
    for (const file of folder.files) {
      file.name = pattern.replace(regex, (_match, pad) => {
        const num = String(n);
        if (pad) {
          const width = parseInt(pad, 10);
          return num.padStart(width, '0');
        }
        return num;
      });
      n++;
    }
  }
  toast.show('重命名完成', 'success');
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
          const mime = getMimeFromPath(first.path);
          const blob = new Blob([fr.data], { type: mime });
          if (emptySlot.src) try { URL.revokeObjectURL(emptySlot.src); } catch (_) {}
          emptySlot.src = URL.createObjectURL(blob);
        }
        emptySlot._srcLoading = false;
      }).catch(err => {
        emptySlot._srcLoading = false;
        toast.show('读取文件失败: ' + err.message, 'error');
      });
    }
  }
}, { deep: true });

onMounted(async () => {
  await nextTick();
  window.lucide?.createIcons();
  loadTemplates();
  document.addEventListener('keydown', onKeydown);
  // Load default output dir from settings
  const defaultOut = useSettings().get('outputDir');
  if (defaultOut && !outputDir.value) {
    outputDir.value = defaultOut;
  }
});
</script>

<style scoped>
.puzzle-layout {
  display: grid;
  grid-template-columns: 230px 1fr;
  gap: 14px;
  align-items: start;
  min-width: 0;
}
.puzzle-side { position: sticky; top: 80px; max-height: calc(100vh - 100px); overflow-y: auto; overflow-x: hidden; padding-right: 2px; }
.row-2col { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.num { width: 100%; min-width: 0; }
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
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
}
.canvas-frame.dragging {
  border: 2px dashed var(--neon-cyan);
  background: var(--neon-cyan-soft);
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
  border: 1.5px solid transparent;
  cursor: move;
  user-select: none;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  transition: border-color .15s, box-shadow .15s;
}
.el:hover { border-color: rgba(6, 214, 244, 0.5); }
.el.selected {
  border-color: var(--neon-cyan);
  box-shadow: 0 0 0 2px var(--neon-cyan-soft), 0 0 20px rgba(6, 214, 244, 0.25);
  z-index: 10;
}
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
  border-radius: 3px;
  box-shadow: 0 0 0 2px rgba(6, 214, 244, 0.2), 0 2px 6px rgba(6, 214, 244, 0.3);
  transition: transform .1s, box-shadow .1s;
}
.handle:hover {
  transform: scale(1.2);
  box-shadow: 0 0 0 3px rgba(6, 214, 244, 0.3), 0 2px 8px rgba(6, 214, 244, 0.4);
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
  pointer-events: none;
  z-index: 5;
}
.hint-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 28px 36px;
  background: rgba(255, 255, 255, 0.85);
  border: 1.5px dashed var(--border-strong);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(4px);
}
.hint-inner i[data-lucide] {
  width: 32px; height: 32px;
  color: var(--text-4);
}
.hint-title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-2);
}
.hint-sub {
  margin: 0;
  font-size: 12px;
  color: var(--text-3);
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

.batch-panel {
  background: var(--panel-2);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 10px;
  animation: batchIn .2s ease;
}
@keyframes batchIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: none; }
}
.batch-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}
.batch-grid .btn-xs,
.batch-panel .btn-xs {
  padding: 4px 6px;
  font-size: 11px;
  border-radius: 6px;
  min-height: 26px;
  justify-content: center;
}
.batch-grid .btn-xs i[data-lucide] {
  width: 13px; height: 13px;
}

@media (max-width: 1024px) {
  .puzzle-layout { grid-template-columns: 1fr; }
  .puzzle-side { position: static; max-height: none; overflow-x: visible; }
}
  .img-folder-list { display: flex; flex-direction: column; gap: 4px; overflow: hidden; }
  .img-folder-row {
    display: flex; align-items: center; gap: 6px;
    padding: 4px 6px; background: var(--panel-2);
    border: 1px solid var(--border); border-radius: 6px;
    min-width: 0;
  }
  .img-folder-idx {
    display: inline-flex; align-items: center; justify-content: center;
    min-width: 24px; height: 20px;
    background: var(--neon-cyan-soft); color: #0369a1;
    border-radius: 4px; font-size: 11px; font-weight: 600; flex-shrink: 0;
  }
  .img-folder-path {
    flex: 1; min-width: 0; font-size: 11px; color: var(--text-2);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .progress-bar { height: 4px; background: var(--panel-3); border-radius: 2px; overflow: hidden; }
  .progress-bar .fill {
    height: 100%;
    background: linear-gradient(90deg, var(--neon-cyan), var(--primary));
    transition: width 0.2s;
  }

/* ============================================================
   模板 dirty 指示
   ============================================================ */
.template-pill.dirty {
  background: var(--warn-soft);
  color: var(--warn-deep);
  border-color: #fde68a;
}
.pill-dot {
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--warn);
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.18);
  flex-shrink: 0;
}

/* ============================================================
   画布更多操作下拉菜单
   ============================================================ */
.menu-anchor { position: relative; display: inline-flex; }
.menu-pop {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 168px;
  padding: 4px;
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  z-index: 30;
  display: flex; flex-direction: column;
  gap: 1px;
}
.menu-item {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 10px;
  font-size: 13px;
  color: var(--text);
  background: transparent;
  border: 0;
  border-radius: 6px;
  text-align: left;
  cursor: pointer;
  transition: background 0.1s;
  width: 100%;
}
.menu-item:hover:not(:disabled) { background: var(--panel-3); }
.menu-item:disabled { color: var(--text-4); cursor: not-allowed; }
.menu-item i[data-lucide] { width: 14px; height: 14px; color: var(--text-3); flex-shrink: 0; }
.menu-item span { line-height: 1; }
.menu-divider {
  height: 1px;
  background: var(--border-2);
  margin: 4px 2px;
}

/* ============================================================
   预览弹窗
   ============================================================ */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  z-index: 200;
  display: flex; align-items: center; justify-content: center;
  padding: 24px;
  animation: tab3-fade-in 0.15s ease-out;
}
.modal {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.25);
  display: flex; flex-direction: column;
  max-height: calc(100vh - 48px);
  overflow: hidden;
  animation: tab3-pop-in 0.18s ease-out;
}
.modal-preview { width: min(720px, 100%); }
.modal-head {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-2);
}
.modal-title { margin: 0; font-size: 15px; font-weight: 600; }
.modal-head .muted { flex: 1; min-width: 0; }
.modal-close { margin-left: auto; }
.modal-body {
  padding: 16px;
  overflow: auto;
  flex: 1;
}
.preview-body {
  display: flex; align-items: center; justify-content: center;
  background: var(--panel-2);
  min-height: 240px;
  max-height: 70vh;
  background-image:
    linear-gradient(45deg, #eef0f3 25%, transparent 25%),
    linear-gradient(-45deg, #eef0f3 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #eef0f3 75%),
    linear-gradient(-45deg, transparent 75%, #eef0f3 75%);
  background-size: 16px 16px;
  background-position: 0 0, 0 8px, 8px -8px, -8px 0;
}
.preview-img {
  max-width: 100%;
  max-height: 70vh;
  object-fit: contain;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.12);
}
.modal-foot {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  border-top: 1px solid var(--border-2);
}
@keyframes tab3-fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes tab3-pop-in {
  from { opacity: 0; transform: scale(0.96) translateY(4px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

/* ============================================================
   批量重命名
   ============================================================ */
.rename-bar {
  margin-bottom: 10px;
}
.rename-input {
  flex: 1;
  min-width: 0;
  padding: 5px 10px;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  font-size: 12px;
  background: var(--panel);
  color: var(--text);
  transition: border-color 0.15s, box-shadow 0.15s;
}
.rename-input:focus {
  outline: none;
  border-color: var(--neon-cyan);
  box-shadow: 0 0 0 2px var(--neon-cyan-soft);
}
.rename-input::placeholder {
  color: var(--text-4);
}</style>
