<template>
  <section :class="$attrs.class">
    <p class="desc">配置应用全局设置和偏好选项。</p>

    <div class="settings-layout">
      <div class="card" style="grid-column: 1 / -1;">
        <h3 class="card-title"><i data-lucide="folder"></i> 路径设置</h3>
        <div class="setting-row">
          <span class="setting-label">默认输出目录</span>
          <div class="path-row">
            <input type="text" v-model="settings.defaultOutputDir" placeholder="留空=使用桌面" style="flex:1">
            <button class="btn btn-sm" @click="pickOutputDir">
              <i data-lucide="folder-open"></i>浏览
            </button>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="card-title"><i data-lucide="palette"></i> 外观</h3>
        <div class="setting-row">
          <span class="setting-label">主题</span>
          <div class="theme-btns">
            <button
              v-for="t in ['light', 'dark']"
              :key="t"
              :class="['theme-btn', { active: settings.theme === t }]"
              @click="setTheme(t)"
            >
              {{ { light: '浅色', dark: '深色' }[t] }}
            </button>
          </div>
        </div>
       <div class="setting-row">
          <span class="setting-label">主题色</span>
          <div class="color-swatches">
            <button
              v-for="c in colorOptions"
              :key="c.value"
              :class="['color-swatch', { active: settings.accentColor === c.value }]"
              :style="{ background: c.value }"
              :title="c.label"
              @click="setAccentColor(c.value)"
            ></button>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="card-title"><i data-lucide="image"></i> 图片默认值</h3>
        <div class="setting-row">
          <span class="setting-label">默认格式</span>
          <select v-model="settings.defaultFormat" @change="saveSettings">
            <option value="PNG">PNG</option>
            <option value="JPG">JPG</option>
            <option value="WEBP">WEBP</option>
          </select>
        </div>
        <div class="setting-row">
          <span class="setting-label">默认质量</span>
          <div class="row">
            <input type="range" v-model="settings.defaultQuality" min="50" max="100" @input="saveSettings" style="flex:1">
            <span style="font-size:12px;color:var(--text-2);width:36px">{{ settings.defaultQuality }}%</span>
          </div>
        </div>
        <div class="setting-row">
          <span class="setting-label">默认缩放</span>
          <select v-model="settings.defaultScale" @change="saveSettings">
            <option value="1">1x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2x</option>
            <option value="3">3x</option>
            <option value="4">4x</option>
          </select>
        </div>
      </div>

      <div class="card">
        <h3 class="card-title"><i data-lucide="trash-2"></i> 缓存</h3>
        <div class="setting-row">
          <span class="setting-label">浏览器缓存</span>
          <button class="btn btn-sm" @click="clearCache">
            <i data-lucide="trash-2" style="width:14px;height:14px"></i>清除缓存
          </button>
        </div>
        <p style="font-size:11px;color:var(--text-3);margin:4px 0 0">清除浏览器临时缓存，不影响已保存的文件。</p>
      </div>

      <div class="card">
        <h3 class="card-title"><i data-lucide="info"></i> 关于</h3>
        <div style="font-size:13px;color:var(--text-2);line-height:1.8;">
          <p><b>商品图工坊 · Full</b></p>
          <p>版本 1.0.0</p>
          <p style="margin-top:8px;">基于 Electron + Vue3 构建的桌面应用。</p>
          <p style="margin-top:8px;font-size:12px;color:var(--text-3)">
            支持文档导出、场景排版、图片缩放、拼接、文字工具、批量重命名。
          </p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue';
import { Folder, Palette, Image, Trash2, Info, FolderOpen } from 'lucide-vue-next';

defineOptions({ inheritAttrs: false });

const STORAGE_KEY = 'fulltool_settings';

const colorOptions = [
  { label: '红色', value: '#ef4444' },
  { label: '橙色', value: '#f97316' },
  { label: '黄色', value: '#eab308' },
  { label: '绿色', value: '#22c55e' },
  { label: '蓝色', value: '#3b82f6' },
  { label: '紫色', value: '#8b5cf6' },
  { label: '粉色', value: '#ec4899' },
];

const defaults = {
  theme: 'light',
  accentColor: '#ef4444',
  defaultOutputDir: '',
  defaultFormat: 'PNG',
  defaultQuality: 90,
  defaultScale: '1'
};

const settings = reactive({ ...defaults });

function loadSettings() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      Object.assign(settings, JSON.parse(stored));
    }
  } catch (e) {}
  applyTheme();
}

function saveSettings() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...settings }));
  window.showToast?.('设置已保存', 'success');
}

function setTheme(t) {
  settings.theme = t;
  applyTheme();
  saveSettings();
}

function setAccentColor(c) {
  settings.accentColor = c;
  document.documentElement.style.setProperty('--primary', c);
  saveSettings();
}

function applyTheme() {
  if (settings.theme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
  } else {
    document.documentElement.removeAttribute('data-theme');
  }
  document.documentElement.style.setProperty('--primary', settings.accentColor);
}

async function pickOutputDir() {
  if (window.electronAPI) {
    const r = await window.electronAPI.selectOutputDir();
    if (!r.canceled && r.filePaths[0]) {
      settings.defaultOutputDir = r.filePaths[0];
      saveSettings();
    }
  } else {
    const d = prompt('默认输出目录路径');
    if (d) {
      settings.defaultOutputDir = d;
      saveSettings();
    }
  }
}

function clearCache() {
  // Clear blobs and object URLs
  if (window.localStorage) {
    const keys = Object.keys(localStorage).filter(k => k.startsWith('blob:') || k === STORAGE_KEY);
    // Don't clear STORAGE_KEY
  }
  // Clear all blob URLs
  if (window.__blobUrls) {
    window.__blobUrls.forEach(url => URL.revokeObjectURL(url));
    window.__blobUrls = [];
  }
  window.showToast?.('缓存已清除', 'success');
}

onMounted(async () => {
  loadSettings();
  await nextTick();
  window.lucide?.createIcons();
});
</script>

<style scoped>
.settings-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  max-width: 800px;
}

.setting-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.setting-row:last-child { margin-bottom: 0; }
.setting-label { font-size: 13px; color: var(--text-2); min-width: 90px; flex-shrink: 0; }

.path-row { display: flex; gap: 6px; flex: 1; }

.theme-btns { display: flex; gap: 4px; }
.theme-btn {
  padding: 5px 14px; border: 1px solid var(--border); background: #fff;
  border-radius: 6px; font-size: 12px; cursor: pointer; transition: all .15s;
}
.theme-btn:hover { background: #f3f4f6; }
.theme-btn.active { background: var(--primary-soft); color: var(--primary); border-color: #fecaca; }

.color-swatches { display: flex; gap: 6px; flex-wrap: wrap; }
.color-swatch {
  width: 24px; height: 24px; border-radius: 50%; border: 2px solid transparent;
  cursor: pointer; transition: all .15s;
}
.color-swatch:hover { transform: scale(1.15); }
.color-swatch.active { border-color: var(--text); box-shadow: 0 0 0 2px #fff, 0 0 0 4px currentColor; }

@media (max-width: 768px) {
  .settings-layout { grid-template-columns: 1fr; }
}
</style>