<template>
  <section :class="$attrs.class">
    <p class="desc">上传背景图与叠图，拖动四个角点定位后导出高清合成图。</p>

    <div class="step-bar">
      <button
        v-for="n in [1, 2, 3]"
        :key="n"
        :class="['step', { active: step === n }]"
        @click="step = n"
      >
        <span class="step-num">{{ n }}</span>
        {{ ['上传底图', '上传叠图', '导出'][n - 1] }}
      </button>
    </div>

    <div class="step-status">
      {{ statusText }}
    </div>

    <div class="scn-grid">
      <!-- Canvas -->
      <div class="canvas-wrap" ref="canvasWrap" @wheel.prevent="onWheel" @click.self="onCanvasClick">
        <div class="canvas-empty" v-if="!baseImg" @click="pickBase">
          <i data-lucide="image"></i>
          <p class="drop-hint">点击上传底图（场景图）</p>
          <p class="drop-sub">支持 PNG / JPG / WebP</p>
        </div>
        <div class="canvas-inner" v-show="baseImg" ref="canvasInner">
          <canvas ref="baseCanvas" class="base-canvas"></canvas>
          <canvas ref="overlayCanvas" class="overlay-canvas"></canvas>
          <div
            v-for="corner in ['tl', 'tr', 'bl', 'br']"
            :key="corner"
            :class="['corner', corner, { hidden: !overlayImg }]"
            :data-corner="corner"
            :style="{ left: corners[corner][0] * 100 + '%', top: corners[corner][1] * 100 + '%' }"
            @mousedown.stop="startDrag(corner, $event)"
          ></div>
        </div>
      </div>

      <!-- Side panel -->
      <div class="card scn-side">
        <!-- Step 1 -->
        <div class="group" v-if="step === 1">
          <h4>底图设置</h4>
          <div v-if="baseImg" class="base-info">
            <span class="tag tag-green">{{ baseName }}</span>
            <span class="tag">{{ baseWidth }} x {{ baseHeight }}</span>
          </div>
          <button class="btn btn-block" @click="pickBase">
            <i data-lucide="upload"></i>
            {{ baseImg ? '更换底图' : '上传底图' }}
          </button>
          <button v-if="baseImg" class="btn btn-ghost btn-block btn-sm" @click="clearBase">
            <i data-lucide="x"></i>移除底图
          </button>
        </div>

        <!-- Step 2 -->
        <div class="group" v-if="step === 2">
          <h4>叠图设置</h4>
          <div v-if="overlayImg" class="overlay-info">
            <span class="tag tag-blue">{{ overlayName }}</span>
          </div>
          <button class="btn btn-block" @click="pickOverlay">
            <i data-lucide="layers"></i>
            {{ overlayImg ? '更换叠图' : '上传叠图' }}
          </button>
          <div class="divider"></div>
          <div class="setting-row">
            <span class="setting-label">不透明度</span>
            <span class="val">{{ opacity }}%</span>
          </div>
          <input type="range" v-model="opacity" min="0" max="100" @input="renderOverlay">
          <div class="divider"></div>
          <div class="setting-row"><span class="setting-label">混合模式</span></div>
          <select v-model="blendMode" @change="renderOverlay">
            <option value="normal">正常 (Normal)</option>
            <option value="multiply">正片叠底</option>
            <option value="screen">滤色</option>
            <option value="overlay">叠加</option>
            <option value="soft-light">柔光</option>
            <option value="hard-light">强光</option>
            <option value="color-dodge">颜色减淡</option>
            <option value="color-burn">颜色加深</option>
            <option value="darken">变暗</option>
            <option value="lighten">变亮</option>
          </select>
          <div class="divider"></div>
          <div class="setting-row">
            <span class="setting-label">透视变换</span>
            <label class="toggle">
              <input type="checkbox" v-model="perspectiveMode" @change="onPerspectiveModeChange">
              <span class="slider"></span>
            </label>
          </div>
          <div v-if="perspectiveMode" class="mode-hint">透视模式：叠图四个角精确对应底图位置</div>
          <div class="divider"></div>
          <div class="setting-row"><span class="setting-label">边角微调</span></div>
          <button class="btn btn-block btn-sm" @click="resetCorners">
            <i data-lucide="refresh-ccw"></i>重置四个角
          </button>
        </div>

        <!-- Step 3 -->
        <div class="group" v-if="step === 3">
          <h4>导出设置</h4>
          <div class="setting-row"><span class="setting-label">输出格式</span></div>
          <div class="format-chips">
            <button
              v-for="fmt in formats"
              :key="fmt"
              :class="['format-chip', { active: exportFormat === fmt }]"
              @click="exportFormat = fmt"
            >{{ fmt }}</button>
          </div>
          <div class="divider"></div>
          <div class="setting-row"><span class="setting-label">输出目录</span></div>
          <button class="btn btn-block" @click="pickOutputDir">
            <i data-lucide="folder-output"></i>
            {{ outputDir || '选择目录' }}
          </button>
          <div class="divider"></div>
          <div class="export-block">
            <button
              class="big"
              :disabled="!baseImg || !overlayImg || !outputDir || isExporting"
              @click="startExport"
            >
              <i data-lucide="download"></i>
              {{ isExporting ? '导出中 ' + exportProgress + '%' : '导出合成图' }}
            </button>
          </div>
        </div>

        <!-- Tips -->
        <div class="tip-card" style="margin-top:12px" v-if="step === 2 && overlayImg">
          <div class="tip-icon">i</div>
          <div class="tip-content">拖动四个角的圆点来定位叠图位置</div>
        </div>
      </div>
    </div>

    <input type="file" ref="baseInput" accept="image/*" style="display:none" @change="onBaseFile">
    <input type="file" ref="overlayInput" accept="image/*" multiple style="display:none" @change="onOverlayFile">
  </section>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue';
defineOptions({ inheritAttrs: false });
import { Upload, Layers, Download, RefreshCcw, X, Image, FolderOutput } from 'lucide-vue-next';
import { useSettings } from '../composables/useSettings.js';

const formats = ['PNG', 'JPG', 'WEBP'];

const step = ref(1);
const canvasWrap = ref(null);
const canvasInner = ref(null);
const baseCanvas = ref(null);
const overlayCanvas = ref(null);
const baseInput = ref(null);
const overlayInput = ref(null);

const baseImg = ref(null);
const overlayImg = ref(null);
const baseName = ref('');
const overlayName = ref('');
const baseWidth = ref(0);
const baseHeight = ref(0);

// ObjectURL refs for cleanup
const baseImgUrl = ref('');
const overlayImgUrl = ref('');

const opacity = ref(100);
const blendMode = ref('normal');
const exportFormat = ref('PNG');
const perspectiveMode = ref(false);

const corners = reactive({
  tl: [0.1, 0.1],
  tr: [0.9, 0.1],
  bl: [0.1, 0.9],
  br: [0.9, 0.9]
});

// corners in absolute pixels (base image coordinates), used when perspectiveMode=true
const cornersAbs = reactive({
  tl: [0, 0],
  tr: [0, 0],
  bl: [0, 0],
  br: [0, 0]
});

let dragCorner = null;
let dragStartX = 0;
let dragStartY = 0;
let dragStartCorners = null;
const zoom = ref(1);

const outputDir = ref('');
const isExporting = ref(false);
const exportProgress = ref(0);

const statusText = ref('第1步：上传一张场景图作为底图');

const statusMap = {
  1: '第1步：上传一张场景图作为底图',
  2: '第2步：上传叠图并拖动角点定位',
  3: '第3步：设置输出目录并导出'
};

function renderBase() {
  if (!baseCanvas.value || !baseImg.value) return;
  const c = baseCanvas.value;
  c.width = baseImg.value.width;
  c.height = baseImg.value.height;
  c.getContext('2d').drawImage(baseImg.value, 0, 0);
  updateZoom();
}

function renderOverlay() {
  if (!overlayCanvas.value || !overlayImg.value) return;
  const c = overlayCanvas.value;
  const ctx = c.getContext('2d');
  ctx.clearRect(0, 0, c.width, c.height);
  ctx.globalAlpha = opacity.value / 100;
  ctx.globalCompositeOperation = blendMode.value;
  if (perspectiveMode.value && baseImg.value) {
    let srcQuad = {
      tl: [0, 0], tr: [overlayImg.value.naturalWidth, 0],
      bl: [0, overlayImg.value.naturalHeight], br: [overlayImg.value.naturalWidth, overlayImg.value.naturalHeight]
    };
    warpImage(overlayImg.value, overlayCanvas.value, srcQuad, cornersAbs, opacity.value, blendMode.value);
  } else {
    ctx.drawImage(overlayImg.value, 0, 0, c.width, c.height);
  }
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
}

function updateOverlayCanvasSize() {
  if (!overlayCanvas.value || !canvasWrap.value) return;
  let w, h;
  if (perspectiveMode.value && baseImg.value) {
    w = baseImg.value.width;
    h = baseImg.value.height;
  } else {
    w = canvasWrap.value.offsetWidth;
    h = canvasWrap.value.offsetHeight;
  }
  overlayCanvas.value.width = w;
  overlayCanvas.value.height = h;
}

function updateZoom() {
  if (!canvasInner.value) return;
  canvasInner.value.style.transform = 'scale(' + zoom.value + ')';
  canvasInner.value.style.transformOrigin = 'center center';
}

function updateCornerPositions() {
  if (!overlayCanvas.value) return;
  const c = overlayCanvas.value;
  const w = c.width;
  const h = c.height;
  ['tl', 'tr', 'bl', 'br'].forEach(function(k) {
    const el = c.parentElement ? c.parentElement.querySelector('[data-corner="' + k + '"]') : null;
    if (!el) return;
    let px, py;
    if (perspectiveMode.value) {
      px = cornersAbs[k][0];
      py = cornersAbs[k][1];
    } else {
      px = corners[k][0] * w;
      py = corners[k][1] * h;
    }
    el.style.left = px + 'px';
    el.style.top = py + 'px';
  });
}

// Compute 3x3 homography matrix from 4 source points to 4 dest points
// Returns array [a,b,c,d,e,f,g,h] representing the 3x3 matrix:
// | a d g |
//   | b e h |
//   | c f 1 |
// Maps: dst(u,v,1) = H * src(x,y,1)
function computeHomography(src, dst) {
  let sx = src.tl[0], sy = src.tl[1], dx = dst.tl[0], dy = dst.tl[1];
  let tx = src.tr[0], ty = src.tr[1], dx2 = dst.tr[0], dy2 = dst.tr[1];
  let bx = src.bl[0], by = src.bl[1], dx3 = dst.bl[0], dy3 = dst.bl[1];
  let rx = src.br[0], ry = src.br[1], dx4 = dst.br[0], dy4 = dst.br[1];

  // Build 8x8 matrix (simplified construction)
  let m = [
    [-sx,-sy,-1, 0, 0, 0, sx*dx, sy*dx, dx],
    [0, 0, 0,-sx,-sy,-1, sx*dy, sy*dy, dy],
    [-tx,-ty,-1, 0, 0, 0, tx*dx2, ty*dx2, dx2],
    [0, 0, 0,-tx,-ty,-1, tx*dy2, ty*dy2, dy2],
    [-bx,-by,-1, 0, 0, 0, bx*dx3, by*dx3, dx3],
    [0, 0, 0,-bx,-by,-1, bx*dy3, by*dy3, dy3],
    [-rx,-ry,-1, 0, 0, 0, rx*dx4, ry*dx4, dx4],
    [0, 0, 0,-rx,-ry,-1, rx*dy4, ry*dy4, dy4]
  ];

  // Gaussian elimination to solve for h[0..7] (h[8]=1)
  let h = [0,0,0,0,0,0,0,0,1];
  for (let i = 0; i < 8; i++) {
    let pivot = i;
    for (let k = i + 1; k < 8; k++) {
      if (Math.abs(m[k][i]) > Math.abs(m[pivot][i])) pivot = k;
    }
    let tmp = m[i]; m[i] = m[pivot]; m[pivot] = tmp;
    tmp = h[i]; h[i] = h[pivot]; h[pivot] = tmp;
    let div = m[i][i];
    if (Math.abs(div) < 1e-10) { h[i] = 1; continue; }
    for (let j = i; j < 9; j++) m[i][j] /= div;
    h[i] /= div;
    for (let k = 0; k < 8; k++) {
      if (k !== i) {
        let factor = m[k][i];
        for (let j = i; j < 9; j++) m[k][j] -= factor * m[i][j];
        h[k] -= factor * h[i];
      }
    }
  }
  return h; // [a,b,c,d,e,f,g,h, 1]
}

// Apply homography warp: draw srcImg onto dstCanvas mapping srcQuad -> dstQuad
function warpImage(srcImg, dstCanvas, srcQuad, dstQuad, globalAlpha, compositeOp) {
  let ow = srcImg.naturalWidth || srcImg.width;
  let oh = srcImg.naturalHeight || srcImg.height;
  let dw = dstCanvas.width;
  let dh = dstCanvas.height;

  let H = computeHomography(srcQuad, dstQuad);

  // Render to offscreen canvas first (so putImageData doesn't clobber dst content)
  let warpCanvas = document.createElement('canvas');
  warpCanvas.width = dw; warpCanvas.height = dh;
  let warpCtx = warpCanvas.getContext('2d');
  let warpData = warpCtx.createImageData(dw, dh);
  let data = warpData.data;

  // Source image data
  let srcCanvas = document.createElement('canvas');
  srcCanvas.width = ow; srcCanvas.height = oh;
  let srcCtx = srcCanvas.getContext('2d');
  srcCtx.drawImage(srcImg, 0, 0);
  let srcData = srcCtx.getImageData(0, 0, ow, oh).data;

  let _a = H[0], _b = H[1], _c = H[2], _d = H[3], _e = H[4], _f = H[5], _g = H[6], _h = H[7];

  for (let y = 0; y < dh; y++) {
    for (let x = 0; x < dw; x++) {
      let d = 1 / (_g * x + _h * y + 1);
      let sx = (_a * x + _d * y + _c) * d;
      let sy = (_b * x + _e * y + _f) * d;

      let idx = (y * dw + x) * 4;
      if (sx < 0 || sy < 0 || sx >= ow - 1 || sy >= oh - 1) {
        data[idx+3] = 0;
        continue;
      }

      let x0 = Math.floor(sx), y0 = Math.floor(sy);
      let x1 = Math.min(x0 + 1, ow - 1), y1 = Math.min(y0 + 1, oh - 1);
      let fx = sx - x0, fy = sy - y0;

      let sidx00 = (y0 * ow + x0) * 4;
      let sidx10 = (y0 * ow + x1) * 4;
      let sidx01 = (y1 * ow + x0) * 4;
      let sidx11 = (y1 * ow + x1) * 4;

      data[idx]   = srcData[sidx00]   + (srcData[sidx10]   - srcData[sidx00])   * fx + (srcData[sidx01]   - srcData[sidx00])   * fy + (srcData[sidx11]   - srcData[sidx01]   - srcData[sidx10]   + srcData[sidx00])   * fx * fy;
      data[idx+1] = srcData[sidx00+1] + (srcData[sidx10+1] - srcData[sidx00+1]) * fx + (srcData[sidx01+1] - srcData[sidx00+1]) * fy + (srcData[sidx11+1] - srcData[sidx01+1] - srcData[sidx10+1] + srcData[sidx00+1]) * fx * fy;
      data[idx+2] = srcData[sidx00+2] + (srcData[sidx10+2] - srcData[sidx00+2]) * fx + (srcData[sidx01+2] - srcData[sidx00+2]) * fy + (srcData[sidx11+2] - srcData[sidx01+2] - srcData[sidx10+2] + srcData[sidx00+2]) * fx * fy;
      data[idx+3] = srcData[sidx00+3];
    }
  }

  warpCtx.putImageData(warpData, 0, 0);

  // Now draw warped result onto dstCanvas using standard compositing
  let ctx = dstCanvas.getContext('2d');
  ctx.globalAlpha = (globalAlpha !== undefined ? globalAlpha : 100) / 100;
  ctx.globalCompositeOperation = (compositeOp || 'source-over');
  ctx.drawImage(warpCanvas, 0, 0);
  ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'source-over';
}

function resetCorners() {
  corners.tl = [0.1, 0.1];
  corners.tr = [0.9, 0.1];
  corners.bl = [0.1, 0.9];
  corners.br = [0.9, 0.9];
  if (baseImg.value) {
    cornersAbs.tl = [0, 0];
    cornersAbs.tr = [baseImg.value.width, 0];
    cornersAbs.bl = [0, baseImg.value.height];
    cornersAbs.br = [baseImg.value.width, baseImg.value.height];
  }
  renderOverlay();
  nextTick(updateCornerPositions);
}

function startDrag(corner, e) {
  dragCorner = corner;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  if (perspectiveMode.value) {
    dragStartCorners = [cornersAbs[corner][0], cornersAbs[corner][1]];
  } else {
    dragStartCorners = [corners[corner][0], corners[corner][1]];
  }
  window.addEventListener('mousemove', onDrag);
  window.addEventListener('mouseup', stopDrag);
}

function onDrag(e) {
  if (!dragCorner) return;
  const dx = e.clientX - dragStartX;
  const dy = e.clientY - dragStartY;
  const wrap = canvasWrap.value;
  if (!wrap) return;
  const scale = zoom.value;
  if (perspectiveMode.value) {
    let w = baseImg.value ? baseImg.value.width : wrap.offsetWidth;
    let h = baseImg.value ? baseImg.value.height : wrap.offsetHeight;
    let nx = dragStartCorners[0] + dx / scale;
    let ny = dragStartCorners[1] + dy / scale;
    cornersAbs[dragCorner][0] = Math.max(0, Math.min(w, nx));
    cornersAbs[dragCorner][1] = Math.max(0, Math.min(h, ny));
  } else {
    let nx2 = dragStartCorners[0] + dx / (wrap.offsetWidth * scale);
    let ny2 = dragStartCorners[1] + dy / (wrap.offsetHeight * scale);
    corners[dragCorner][0] = Math.max(0, Math.min(1, nx2));
    corners[dragCorner][1] = Math.max(0, Math.min(1, ny2));
  }
  renderOverlay();
  nextTick(updateCornerPositions);
}

function stopDrag() {
  dragCorner = null;
  window.removeEventListener('mousemove', onDrag);
  window.removeEventListener('mouseup', stopDrag);
}

function onPerspectiveModeChange() {
  if (perspectiveMode.value && baseImg.value) {
    // Convert ratio corners to absolute pixels
    cornersAbs.tl = [corners.tl[0] * baseImg.value.width, corners.tl[1] * baseImg.value.height];
    cornersAbs.tr = [corners.tr[0] * baseImg.value.width, corners.tr[1] * baseImg.value.height];
    cornersAbs.bl = [corners.bl[0] * baseImg.value.width, corners.bl[1] * baseImg.value.height];
    cornersAbs.br = [corners.br[0] * baseImg.value.width, corners.br[1] * baseImg.value.height];
  } else if (!perspectiveMode.value && baseImg.value) {
    // Convert absolute pixels back to ratio corners
    corners.tl = [cornersAbs.tl[0] / baseImg.value.width, cornersAbs.tl[1] / baseImg.value.height];
    corners.tr = [cornersAbs.tr[0] / baseImg.value.width, cornersAbs.tr[1] / baseImg.value.height];
    corners.bl = [cornersAbs.bl[0] / baseImg.value.width, cornersAbs.bl[1] / baseImg.value.height];
    corners.br = [cornersAbs.br[0] / baseImg.value.width, cornersAbs.br[1] / baseImg.value.height];
  }
  nextTick(function() {
    updateOverlayCanvasSize();
    renderOverlay();
    nextTick(updateCornerPositions);
  });
}

function onWheel(e) {
  const delta = e.deltaY > 0 ? -0.1 : 0.1;
  zoom.value = Math.max(0.25, Math.min(3, zoom.value + delta));
  updateZoom();
}

function onCanvasClick(e) {
  if (e.target === canvasWrap.value || (e.target.classList && e.target.classList.contains('canvas-empty'))) {
    if (step.value === 1) pickBase();
  }
}

function pickBase() { baseInput.value && baseInput.value.click(); }
function pickOverlay() { overlayInput.value && overlayInput.value.click(); }

function onBaseFile(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  baseName.value = file.name;
  if (baseImgUrl.value) { URL.revokeObjectURL(baseImgUrl.value); baseImgUrl.value = ''; }
  const url = URL.createObjectURL(file);
  baseImgUrl.value = url;
  const img = new window.Image();
  img.onload = function() {
    baseImg.value = img;
    baseWidth.value = img.width;
    baseHeight.value = img.height;
    step.value = 2;
    statusText.value = statusMap[2];

    // Initialize cornersAbs in perspective mode
    if (perspectiveMode.value) {
      cornersAbs.tl = [0, 0];
      cornersAbs.tr = [img.width, 0];
      cornersAbs.bl = [0, img.height];
      cornersAbs.br = [img.width, img.height];
    }

    renderBase();
    nextTick(function() {
      updateOverlayCanvasSize();
      renderOverlay();
      nextTick(updateCornerPositions);
    });
    window.showToast && window.showToast('底图已加载', 'success');
  };
  img.onerror = function() {
    window.showToast && window.showToast('底图加载失败', 'error');
  };
  img.src = url;
}

function onOverlayFile(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;
  overlayName.value = file.name;
  if (overlayImgUrl.value) { URL.revokeObjectURL(overlayImgUrl.value); overlayImgUrl.value = ''; }
  const url = URL.createObjectURL(file);
  overlayImgUrl.value = url;
  const img = new window.Image();
  img.onload = function() {
    overlayImg.value = img;
    updateOverlayCanvasSize();
    renderOverlay();
    nextTick(updateCornerPositions);
    step.value = 3;
    statusText.value = statusMap[3];
    window.showToast && window.showToast('叠图已加载', 'success');
  };
  img.onerror = function() {
    window.showToast && window.showToast('叠图加载失败', 'error');
  };
  img.src = url;
}

function clearBase() {
  // clear base only - keep overlay (and the placement state we built for it)
  baseImg.value = null;
  baseName.value = '';
  baseWidth.value = 0;
  baseHeight.value = 0;
  step.value = 1;
  statusText.value = statusMap[1];
}

function clearOverlay() {
  overlayImg.value = null;
  overlayName.value = '';
}

async function pickOutputDir() {
  if (!window.electronAPI) {
    let d = prompt('输出目录');
    if (d) outputDir.value = d;
    return;
  }
  let r = await window.electronAPI.selectOutputDir();
  if (!r.canceled && r.filePaths[0]) {
    outputDir.value = r.filePaths[0];
  }
}

async function startExport() {
  if (!baseImg.value || !overlayImg.value || !outputDir.value) return;
  isExporting.value = true;
  exportProgress.value = 0;

  try {
    let canvas = document.createElement('canvas');
    canvas.width = baseImg.value.width;
    canvas.height = baseImg.value.height;
    let ctx = canvas.getContext('2d');
    ctx.drawImage(baseImg.value, 0, 0);

    ctx.globalAlpha = opacity.value / 100;
    ctx.globalCompositeOperation = blendMode.value;

    if (perspectiveMode.value) {
      let srcQuad = {
        tl: [0, 0], tr: [overlayImg.value.naturalWidth, 0],
        bl: [0, overlayImg.value.naturalHeight], br: [overlayImg.value.naturalWidth, overlayImg.value.naturalHeight]
      };
      warpImage(overlayImg.value, canvas, srcQuad, cornersAbs, opacity.value, blendMode.value);
    } else {
      let wrap = canvasWrap.value;
      if (!wrap) throw new Error('Canvas not found');
      let xs = [corners.tl[0], corners.tr[0], corners.bl[0], corners.br[0]];
      let ys = [corners.tl[1], corners.tr[1], corners.bl[1], corners.br[1]];
      let minX = Math.min.apply(null, xs) * wrap.offsetWidth;
      let maxX = Math.max.apply(null, xs) * wrap.offsetWidth;
      let minY = Math.min.apply(null, ys) * wrap.offsetHeight;
      let maxY = Math.max.apply(null, ys) * wrap.offsetHeight;
      let sx = minX * (baseImg.value.width / wrap.offsetWidth);
      let sy = minY * (baseImg.value.height / wrap.offsetHeight);
      let sw = (maxX - minX) * (baseImg.value.width / wrap.offsetWidth);
      let sh = (maxY - minY) * (baseImg.value.height / wrap.offsetHeight);
      ctx.drawImage(overlayImg.value, sx, sy, sw, sh);
    }

    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';

    let mimeMap = { PNG: 'image/png', JPG: 'image/jpeg', WEBP: 'image/webp' };
    let mime = mimeMap[exportFormat.value] || 'image/png';
    let quality = exportFormat.value === 'JPG' ? 0.92 : undefined;

    canvas.toBlob(async function(blob) {
      if (!blob) {
        window.showToast && window.showToast('导出失败', 'error');
        isExporting.value = false;
        return;
      }
      exportProgress.value = 50;
      let name = '合成图_' + Date.now() + '.' + exportFormat.value.toLowerCase();
      if (window.electronAPI) {
        let buf = await blob.arrayBuffer();
        await window.electronAPI.writeFile(outputDir.value + '/' + name, Array.from(new Uint8Array(buf)));
      } else {
        let url = URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = name;
        a.click();
        URL.revokeObjectURL(url);
      }
      exportProgress.value = 100;
      isExporting.value = false;
      window.showToast && window.showToast('导出完成', 'success');
    }, mime, quality);
  } catch(err) {
    isExporting.value = false;
    window.showToast && window.showToast('导出失败', 'error');
  }
}

let ro = null;

onMounted(function() {
  nextTick(function() { window.lucide && window.lucide.createIcons(); });
  // Load default output dir from settings
  const defaultOut = useSettings().get('outputDir');
  if (defaultOut && !outputDir.value) {
    outputDir.value = defaultOut;
  }
  if (canvasWrap.value) {
    ro = new ResizeObserver(function() {
      if (overlayImg.value) {
        updateOverlayCanvasSize();
        renderOverlay();
        nextTick(updateCornerPositions);
      }
    });
    ro.observe(canvasWrap.value);
  }
});

onUnmounted(function() {
  ro && ro.disconnect();
  window.removeEventListener('mousemove', onDrag);
  window.removeEventListener('mouseup', stopDrag);
  if (baseImgUrl.value) { URL.revokeObjectURL(baseImgUrl.value); baseImgUrl.value = ''; }
  if (overlayImgUrl.value) { URL.revokeObjectURL(overlayImgUrl.value); overlayImgUrl.value = ''; }
});
</script>

<style scoped>
.step-bar {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-bottom: 12px;
}
.step {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: all .18s;
  font-size: 13px;
  position: relative;
}
.step:hover { background: var(--panel-2); transform: translateY(-1px); box-shadow: var(--shadow-sm); }
.step:active { transform: scale(0.995) translateY(0); }
.step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  background: var(--panel-3);
  color: var(--text);
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  transition: all .18s;
}
.step.active { color: var(--primary); background: var(--primary-soft); border-color: var(--primary-soft); box-shadow: 0 0 0 1px rgba(239,68,68,0.1) inset, 0 2px 8px -2px var(--primary-glow); }
.step.active .step-num { background: linear-gradient(135deg, var(--primary) 0%, var(--primary-2) 100%); color: #fff; box-shadow: 0 2px 6px var(--primary-glow); }
.step-status { margin-bottom: 16px; font-size: 12px; color: var(--text-2); padding: 0 4px; }

.scn-grid {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: 16px;
}
.canvas-wrap {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 10px;
  min-height: 520px;
  position: relative;
  overflow: hidden;
  cursor: crosshair;
  background-image: radial-gradient(var(--border) 1px, transparent 1px);
  background-size: 18px 18px;
  background-position: -9px -9px;
}
.canvas-empty {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-3);
  cursor: pointer;
  transition: background .2s;
  border-radius: 10px;
}
.canvas-empty:hover { background: var(--panel-2); }
.canvas-empty i[data-lucide] {
  width: 36px; height: 36px;
  color: var(--text-4);
  transition: color .2s, transform .2s;
}
.canvas-empty:hover i[data-lucide] { color: var(--text-3); transform: scale(1.05); }
.canvas-empty .drop-hint {
  margin: 0;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-2);
}
.canvas-empty .drop-sub {
  margin: 0;
  font-size: 12px;
  color: var(--text-3);
}
.canvas-inner {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.base-canvas, .overlay-canvas {
  position: absolute;
  top: 0;
  left: 0;
}
.overlay-canvas { pointer-events: none; }
.corner {
  position: absolute;
  width: 14px;
  height: 14px;
  background: var(--panel);
  border: 2px solid var(--primary);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  cursor: grab;
  z-index: 10;
}
.corner:active { cursor: grabbing; }
.corner.hidden { display: none; }
.corner.tl { cursor: nw-resize; }
.corner.tr { cursor: ne-resize; }
.corner.bl { cursor: sw-resize; }
.corner.br { cursor: se-resize; }

.scn-side .group { padding: 0; }
.scn-side .group + .group {
  border-top: 1px solid var(--border);
  margin-top: 14px;
  padding-top: 14px;
}
.scn-side .group h4 { margin: 0 0 10px; font-size: 13px; font-weight: 600; }
.base-info, .overlay-info { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.setting-row .setting-label { font-size: 13px; color: var(--text-2); }
.setting-row .val { font-size: 13px; color: var(--primary); font-weight: 500; }

.format-chips { display: flex; gap: 6px; margin-bottom: 12px; }
.format-chip {
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--panel);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.format-chip:hover { border-color: var(--primary-2); }
.format-chip.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.export-block { margin-top: 8px; }
.big {
  width: 100%;
  padding: 12px 18px;
  background: linear-gradient(180deg, var(--primary) 0%, var(--primary-2) 100%);
  color: #fff;
  border: 0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 14px var(--primary-glow);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: filter 0.15s;
}
.big:hover:not(:disabled) { filter: brightness(1.05); }
.big:disabled { opacity: 0.5; cursor: not-allowed; }

.tip-card {
  display: flex;
  gap: 10px;
  padding: 12px 14px;
}
.tip-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
}
.tip-content { font-size: 12px; color: var(--text-2); line-height: 1.6; }

.divider { height: 1px; background: var(--border-2); margin: 12px 0; }

.toggle {
  position: relative; display: inline-flex; align-items: center;
  cursor: pointer;
}
.toggle input { display: none; }
.toggle .slider {
  width: 36px; height: 20px; border-radius: 10px;
  background: var(--border-strong); position: relative;
  transition: background .2s;
}
.toggle .slider::after {
  content: ''; position: absolute;
  width: 16px; height: 16px; border-radius: 50%;
  background: #fff; top: 2px; left: 2px;
  transition: transform .2s;
  box-shadow: 0 1px 3px rgba(0,0,0,.2);
}
.toggle input:checked + .slider { background: var(--primary); }
.toggle input:checked + .slider::after { transform: translateX(16px); }

.mode-hint {
  font-size: 11px; color: var(--primary); margin-top: 4px;
  line-height: 1.4;
}

@media (max-width: 900px) {
  .scn-grid { grid-template-columns: 1fr; }
}
</style>