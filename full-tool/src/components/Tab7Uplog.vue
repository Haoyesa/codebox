<template>
  <div ref="editorContainer" class="highmd-editor-root" :class="$attrs.class">
    <header class="topbar">
      <div class="brand"><div class="mark">H</div><div class="name">HighMD</div></div>
      <div class="nav-group">
        <button class="nav-btn" @click="toast.show('功能：新建笔记')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>新建笔记
        </button>
        <button class="nav-btn" @click="exportPNG(); setTimeout(() => toast.show('已生成卡片 PNG'), 100)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>导出
        </button>
      </div>
    </header>
    <main class="workspace">
      <aside class="pages-bar">
        <div
          v-for="(page, i) in pages"
          :key="i"
          class="page-thumb"
          :class="{ active: i === currentPage }"
          @click="switchPage(i)"
        >
          <span>{{ (page.title || `未命名 ${i + 1}`).slice(0, 14) }}</span>
        </div>
        <button class="page-add" title="添加页面" @click="addPage">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
      </aside>
      <section class="editor">
        <div class="editor-card">
          <div class="field-label">
            <span>标题</span>
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="label-info">显示</span>
              <div class="toggle" :class="{ off: !showTitle }" @click="toggleShowTitle"></div>
            </div>
          </div>
          <input class="title-input" placeholder="在此输入标题" v-model="titleValue" @input="onTitleInput" />
        </div>
        <div class="editor-card">
          <div class="field-label">
            <span>正文</span>
            <div style="display:flex;align-items:center;gap:8px;">
              <span class="label-info">自动分页 ①</span>
              <div class="toggle" :class="{ off: !autoPage }" @click="toggleAutoPage"></div>
            </div>
          </div>
          <div class="toolbar">
            <button class="tb-btn" title="撤销 (Ctrl+Z)" @click="undo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></button>
            <button class="tb-btn" title="重做 (Ctrl+Y)" @click="redo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 14 20 9 15 4"/><path d="M4 20v-7a4 4 0 0 1 4-4h12"/></svg></button>
            <div class="tb-sep"></div>
            <button class="tb-btn" @mousedown.prevent="execCmd('formatBlock', 'H1')">H1</button>
            <button class="tb-btn" @mousedown.prevent="execCmd('formatBlock', 'H2')">H2</button>
            <button class="tb-btn" @mousedown.prevent="execCmd('formatBlock', 'H3')">H3</button>
            <div class="tb-sep"></div>
            <button class="tb-btn" title="表情" @click="insertEmoji"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg></button>
            <button class="tb-btn" title="插入图片" @click="fileInputRef?.click()"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg></button>
            <button class="tb-btn" title="荧光标记" @click="insertMark"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l-6 6v3h3l6-6"/><path d="M22 5l-3-3-9 9 3 3 9-9z"/></svg></button>
            <button class="tb-btn" title="导出PNG" @click="exportPNG"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button>
            <label class="tb-check" title="html2canvas 模式：完整渲染富文本和图片（默认开启）"><input type="checkbox" v-model="useHtml2canvas" /> 富文本</label>
            <div class="tb-spacer"></div>
            <button class="tb-action" @click="smartLayout"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>智能排版</button>
          </div>
          <div class="editor-area" contenteditable="true" ref="editorAreaRef" @input="onEditorInput"></div>
        </div>
        <div class="import-grid" style="grid-template-columns:1fr;">
          <button class="import-card" @click="fileInputRef?.click()">
            <div class="import-icon upload"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></div>
            <span>导入 Markdown / 文本 / 图片</span>
          </button>
        </div>
      </section>
      <section class="preview">
        <div class="preview-header">
          <div class="left"><span>预览</span><span style="opacity:.4">·</span><span class="name">{{ tplName }}</span></div>
          <div class="ratio-group">
            <button class="ratio-btn" :class="{ active: ratio === '3-4' }" @click="setRatio('3-4')">3:4</button>
            <button class="ratio-btn" :class="{ active: ratio === '3-5' }" @click="setRatio('3-5')">3:5</button>
          </div>
        </div>
        <div class="preview-frame" :class="'r-' + ratio" ref="previewFrameRef">
          <div class="preview-stage" :class="currentTpl" :style="stageStyle" ref="previewStageRef">
            <div class="tpl-card" :style="cardStyle">
              <span class="stars">&#10022; &#10022; &#10022;</span>
              <span class="badge">{{ badgeText }}</span>
              <h1 :style="{ display: showTitle ? '' : 'none' }">{{ currentTitle }}</h1>
              <div class="body" v-html="currentBody"></div>
              <div class="footer"><span>HighMD</span><span>{{ pageIndicatorText }}</span></div>
            </div>
          </div>
        </div>
        <div class="page-indicator">{{ pageIndicatorText }}</div>
      </section>
      <aside class="template-lib">
        <div class="lib-tabs">
          <div class="lib-tab" :class="{ active: activeLibTab === 'tpl' }" @click="activeLibTab = 'tpl'">模板库</div>
          <div class="lib-tab" :class="{ active: activeLibTab === 'adj' }" @click="activeLibTab = 'adj'">调整</div>
        </div>
        <div class="lib-content">
          <template v-if="activeLibTab === 'tpl'">
            <div v-for="sec in sections" :key="sec.name" class="tpl-section">
              <h4>{{ sec.name }}</h4>
              <div class="tpl-row">
                <div
                  v-for="it in sec.items"
                  :key="it.id"
                  class="tpl-mini"
                  :class="[it.cls, { active: currentTpl === it.id }]"
                  @click="applyTemplate(it.id, it.cls, sec.name)"
                  :title="it.name"
                >
                  <div class="mini-title">{{ it.text }}</div>
                  <div class="mini-bar"></div>
                  <div class="mini-bar" style="width:80%"></div>
                  <div class="mini-bar" style="width:60%"></div>
                  <div class="mini-bar" style="width:70%"></div>
                  <div class="mini-bar" style="width:50%"></div>
                  <div class="mini-footer"><span>HighMD</span><span>1/1</span></div>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="adj-panel">
              <div class="adj-tabs">
                <div class="adj-tab" :class="{ active: adjustScope === 'current' }" @click="adjustScope = 'current'">当前卡片(组)属性</div>
                <div class="adj-tab" :class="{ active: adjustScope === 'global' }" @click="adjustScope = 'global'; toast.show('已切换到全局卡片属性')">全局卡片属性</div>
              </div>

              <div class="adj-row-2">
                <div class="adj-mini-card" :class="{ active: adjustSection === 'full' }" @click="adjustSection = 'full'">
                  <span class="adj-mini-icon">+</span>
                  <span>全文设置</span>
                </div>
                <div class="adj-mini-card" :class="{ active: adjustSection === 'tpl' }" @click="adjustSection = 'tpl'">
                  <span class="adj-mini-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg></span>
                  <span>样式模版</span>
                </div>
              </div>

              <div class="adj-section">
                <div class="adj-section-head">
                  <span>文字设置:</span>
                  <button class="adj-reset" @click="resetTextSettings">&#x21BA; 恢复默认值</button>
                </div>
                <div class="adj-block">
                  <div class="adj-field-label">标题:</div>
                  <div class="size-group">
                    <button v-for="sz in ['xs','sm','md','lg','xl']" :key="sz" class="size-btn" :class="{ active: settings.titleSize === sz }" @click="settings.titleSize = sz">{{ sizeLabelMap[sz] }}</button>
                  </div>
                  <div class="font-select-wrap">
                    <select class="font-select" v-model="settings.titleFont">
                      <option>平方</option>
                      <option>思源黑体</option>
                      <option>系统默认</option>
                      <option>衬线</option>
                    </select>
                  </div>
                </div>
                <div class="adj-block">
                  <div class="adj-field-label">正文:</div>
                  <div class="size-group">
                    <button v-for="sz in ['xs','sm','md','lg','xl']" :key="sz" class="size-btn" :class="{ active: settings.bodySize === sz }" @click="settings.bodySize = sz">{{ sizeLabelMap[sz] }}</button>
                  </div>
                  <div class="font-select-wrap">
                    <select class="font-select" v-model="settings.bodyFont">
                      <option>平方</option>
                      <option>思源黑体</option>
                      <option>系统默认</option>
                      <option>衬线</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="adj-section">
                <div class="adj-section-head">
                  <span>对齐与间距:</span>
                  <button class="adj-reset" @click="resetSpacingSettings">&#x21BA; 恢复默认值</button>
                </div>
                <div class="adj-block">
                  <div class="adj-row-flex">
                    <div class="align-group">
                      <button class="align-btn" :class="{ active: settings.bodyAlign === 'left' }" title="左对齐" @click="settings.bodyAlign = 'left'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg></button>
                      <button class="align-btn" :class="{ active: settings.bodyAlign === 'center' }" title="居中" @click="settings.bodyAlign = 'center'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg></button>
                      <button class="align-btn" :class="{ active: settings.bodyAlign === 'right' }" title="右对齐" @click="settings.bodyAlign = 'right'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="6" y1="18" x2="21" y2="18"/></svg></button>
                      <button class="align-btn" :class="{ active: settings.bodyAlign === 'justify' }" title="两端对齐" @click="settings.bodyAlign = 'justify'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg></button>
                    </div>
                    <div class="num-stepper">
                      <span class="step-icon" title="行高">&#x2261;</span>
                      <input type="number" v-model.number="settings.lineHeight" min="1" max="3" step="0.1" />
                      <div class="step-arrows"><button class="step-up" @click="adjustSetting('lineHeight', 0.1, 1, 3, 1)">&#x25B4;</button><button class="step-down" @click="adjustSetting('lineHeight', -0.1, 1, 3, 1)">&#x25BE;</button></div>
                    </div>
                  </div>
                  <div class="adj-row-flex">
                    <div class="num-stepper">
                      <span class="step-icon" title="段前距">&#x2191;</span>
                      <input type="number" v-model.number="settings.marginTop" min="0" max="50" step="1" />
                      <div class="step-arrows"><button class="step-up" @click="adjustSetting('marginTop', 1, 0, 50)">&#x25B4;</button><button class="step-down" @click="adjustSetting('marginTop', -1, 0, 50)">&#x25BE;</button></div>
                    </div>
                    <div class="num-stepper">
                      <span class="step-icon" title="段后距">&#x2193;</span>
                      <input type="number" v-model.number="settings.marginBottom" min="0" max="50" step="1" />
                      <div class="step-arrows"><button class="step-up" @click="adjustSetting('marginBottom', 1, 0, 50)">&#x25B4;</button><button class="step-down" @click="adjustSetting('marginBottom', -1, 0, 50)">&#x25BE;</button></div>
                    </div>
                  </div>
                  <div class="adj-row-flex">
                    <div class="num-stepper">
                      <span class="step-icon" title="左缩进">&#x2190;</span>
                      <input type="number" v-model.number="settings.paddingLeft" min="0" max="50" step="1" />
                      <div class="step-arrows"><button class="step-up" @click="adjustSetting('paddingLeft', 1, 0, 50)">&#x25B4;</button><button class="step-down" @click="adjustSetting('paddingLeft', -1, 0, 50)">&#x25BE;</button></div>
                    </div>
                    <div class="num-stepper">
                      <span class="step-icon" title="右缩进">&#x2192;</span>
                      <input type="number" v-model.number="settings.paddingRight" min="0" max="50" step="1" />
                      <div class="step-arrows"><button class="step-up" @click="adjustSetting('paddingRight', 1, 0, 50)">&#x25B4;</button><button class="step-down" @click="adjustSetting('paddingRight', -1, 0, 50)">&#x25BE;</button></div>
                    </div>
                  </div>
                  <div class="adj-row-flex">
                    <div class="num-stepper">
                      <span class="step-icon" title="首行缩进">&#x21B5;</span>
                      <input type="number" v-model.number="settings.textIndent" min="0" max="50" step="1" />
                      <div class="step-arrows"><button class="step-up" @click="adjustSetting('textIndent', 1, 0, 50)">&#x25B4;</button><button class="step-down" @click="adjustSetting('textIndent', -1, 0, 50)">&#x25BE;</button></div>
                    </div>
                    <div class="num-stepper">
                      <span class="step-icon" title="字间距">&#x2195;</span>
                      <input type="number" v-model.number="settings.lineSpacing" min="0" max="20" step="1" />
                      <div class="step-arrows"><button class="step-up" @click="adjustSetting('lineSpacing', 1, 0, 20)">&#x25B4;</button><button class="step-down" @click="adjustSetting('lineSpacing', -1, 0, 20)">&#x25BE;</button></div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="adj-section">
                <div class="adj-section-head">
                  <span>背景替换:</span>
                  <span class="bg-actions">
                    <button class="adj-link" @click="toast.show('请先上传图片再裁剪')">&#x29C9; 裁剪图片</button>
                    <button class="adj-link" @click="resetBg">&#x21BA; 恢复默认背景</button>
                  </span>
                </div>
                <div class="bg-upload">
                  <button class="bg-upload-btn" @click="bgFileInputRef?.click()">&#x2191; 上传图片</button>
                  <input type="file" ref="bgFileInputRef" accept="image/*" hidden @change="onBgFileChange" />
                </div>
              </div>
            </div>
          </template>
        </div>
      </aside>
    </main>

    <input type="file" ref="fileInputRef" accept="image/*,.md,.txt" hidden @change="onFileChange" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useToast } from '../composables/useToast.js';
import { useWorkspaceState } from '../composables/useWorkspaceState.js';
import html2canvas from 'html2canvas';

const editorContainer = ref(null);
const toast = useToast();
const ws = useWorkspaceState('highmd');
const useHtml2canvas = ref(true);

// === DOM Refs ===
const editorAreaRef = ref(null);
const previewStageRef = ref(null);
const previewFrameRef = ref(null);
const fileInputRef = ref(null);
const bgFileInputRef = ref(null);

// === 核心状态 ===
const pages = ref([{ title: 'HighMD：把想法装进卡片，让表达更精炼', html: '' }]);
const currentPage = ref(0);
const showTitle = ref(true);
const autoPage = ref(true);
const ratio = ref('3-5');
const currentTpl = ref('tpl-default');
const tplName = ref('简单格子');
const bgImage = ref('');
const activeLibTab = ref('tpl');
const adjustScope = ref('current');
const adjustSection = ref('full');
const titleValue = ref('HighMD：把想法装进卡片，让表达更精炼');

const settings = ref({
  titleSize: 'sm',
  bodySize: 'sm',
  titleFont: '平方',
  bodyFont: '平方',
  bodyAlign: 'left',
  lineHeight: 1.8,
  marginTop: 0,
  marginBottom: 0,
  paddingLeft: 0,
  paddingRight: 0,
  textIndent: 0,
  lineSpacing: 0,
});

// === 模板库数据 ===
const sections = [
  { name: '简单格子', items: [{ id: 'tpl-default', cls: 'tpl-default', name: '白色简约', text: 'HighMD 让表达更精炼' }, { id: 'tpl-mint', cls: 'tpl-mint', name: '清新薄荷', text: 'HighMD 让表达更精炼' }, { id: 'tpl-peach', cls: 'tpl-peach', name: '蜜桃暖意', text: 'HighMD 让表达更精炼' }] },
  { name: '智启新时代-日签版', items: [{ id: 'tpl-cream', cls: 'tpl-cream', name: '日签·米黄', text: 'DAY 06 智启' }, { id: 'tpl-amber', cls: 'tpl-amber', name: '日签·琥珀', text: 'DAY 06 智启' }, { id: 'tpl-sky', cls: 'tpl-sky', name: '日签·晴空', text: 'DAY 06 智启' }] },
  { name: '智启新时代', items: [{ id: 'tpl-dark', cls: 'tpl-dark', name: '极简深色', text: '智启新时代' }, { id: 'tpl-lavender', cls: 'tpl-lavender', name: '知性紫调', text: '智启新时代' }, { id: 'tpl-rose', cls: 'tpl-rose', name: '玫瑰宣言', text: '智启新时代' }] },
  { name: '咖啡慢生活', items: [{ id: 'tpl-coffee', cls: 'tpl-coffee', name: '晨光咖啡', text: '一杯咖啡 慢度时光' }, { id: 'tpl-pink', cls: 'tpl-pink', name: '玫瑰拿铁', text: '一杯咖啡 慢度时光' }, { id: 'tpl-mint2', cls: 'tpl-mint', name: '薄荷冰咖', text: '一杯咖啡 慢度时光' }] }
];

// === 常量映射 ===
const sizeLabelMap = { xs: '最小', sm: '小', md: '中', lg: '大', xl: '最大' };
const sizeMapTitle = { xs: '16px', sm: '21px', md: '26px', lg: '32px', xl: '40px' };
const sizeMapBody = { xs: '11px', sm: '12.5px', md: '14px', lg: '16px', xl: '20px' };
const fontMap = {
  '平方': '-apple-system,"PingFang SC","Microsoft YaHei",sans-serif',
  '思源黑体': '"Source Han Sans CN","Noto Sans SC",sans-serif',
  '系统默认': '-apple-system,BlinkMacSystemFont,sans-serif',
  '衬线': 'Georgia,"Times New Roman",serif'
};

// === Computed ===
const currentTitle = computed(() => pages.value[currentPage.value]?.title || 'HighMD：把想法装进卡片，让表达更精炼');
const currentBody = computed(() => pages.value[currentPage.value]?.html || '');
const pageIndicatorText = computed(() => `${currentPage.value + 1}/${pages.value.length}`);

const badgeText = computed(() => {
  if (tplName.value.includes('日签')) return '日签 · DAY 06';
  if (tplName.value.includes('咖啡')) return '一杯咖啡 · 慢度时光';
  if (tplName.value.includes('智启')) return '智启 · 新时代';
  return 'HighMD · 灵感笔记';
});

const cardStyle = computed(() => ({
  '--title-size': sizeMapTitle[settings.value.titleSize] || '21px',
  '--body-size': sizeMapBody[settings.value.bodySize] || '12.5px',
  '--title-font': fontMap[settings.value.titleFont] || fontMap['平方'],
  '--body-font': fontMap[settings.value.bodyFont] || fontMap['平方'],
  '--body-align': settings.value.bodyAlign,
  '--line-height': String(settings.value.lineHeight),
  '--p-mt': settings.value.marginTop + 'px',
  '--p-mb': settings.value.marginBottom + 'px',
  '--p-pl': settings.value.paddingLeft + 'px',
  '--p-pr': settings.value.paddingRight + 'px',
  '--p-indent': settings.value.textIndent + 'px',
  '--p-spacing': settings.value.lineSpacing + 'px',
}));

const stageStyle = computed(() => {
  if (!bgImage.value) return {};
  return {
    backgroundImage: `url(${bgImage.value})`,
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  };
});

// === 辅助函数 ===
function escapeHtml(str) {
  if (typeof str !== 'string') return '';
  const el = document.createElement('div');
  el.textContent = str;
  return el.innerHTML;
}

function switchPage(index) {
  // 保存当前页状态
  if (editorAreaRef.value) {
    pages.value[currentPage.value].html = editorAreaRef.value.innerHTML;
  }
  pages.value[currentPage.value].title = titleValue.value;
  currentPage.value = index;
  refreshPage();
}

function refreshPage() {
  const p = pages.value[currentPage.value];
  titleValue.value = p.title || '';
  if (editorAreaRef.value) {
    editorAreaRef.value.innerHTML = p.html || '';
  }
}

function addPage() {
  // 保存当前页
  if (editorAreaRef.value) {
    pages.value[currentPage.value].html = editorAreaRef.value.innerHTML;
  }
  pages.value[currentPage.value].title = titleValue.value;
  pages.value.push({ title: `新页面 ${pages.value.length + 1}`, html: '' });
  currentPage.value = pages.value.length - 1;
  refreshPage();
  toast.show('已添加新页面');
}

function applyTemplate(id, cls, name) {
  currentTpl.value = id;
  tplName.value = name;
}

function setRatio(r) {
  ratio.value = r;
}

function toggleShowTitle() {
  showTitle.value = !showTitle.value;
}

function toggleAutoPage() {
  autoPage.value = !autoPage.value;
  toast.show(autoPage.value ? '已开启自动分页' : '已关闭自动分页');
}

function execCmd(command, value = null) {
  const el = editorAreaRef.value;
  if (!el) return;
  document.execCommand(command, false, value);
  el.dispatchEvent(new Event('input'));
}

function onEditorInput() {
  const html = editorAreaRef.value?.innerHTML || '';
  pages.value[currentPage.value].html = html;
}

function onTitleInput() {
  pages.value[currentPage.value].title = titleValue.value;
}

function insertEmoji() {
  const em = ['😊', '✨', '🎉', '💡', '📌', '🚀', '🌈', '☕', '🌸', '🔥', '👍', '💪', '🌟', '🍀', '🎯', '✏️'];
  const c = em[Math.floor(Math.random() * em.length)];
  document.execCommand('insertText', false, c);
  editorAreaRef.value?.dispatchEvent(new Event('input'));
}

function insertMark() {
  document.execCommand('hiliteColor', false, '#fff3a3');
  toast.show('已开启荧光笔');
}

function undo() {
  document.execCommand('undo');
  editorAreaRef.value?.dispatchEvent(new Event('input'));
}

function redo() {
  document.execCommand('redo');
  editorAreaRef.value?.dispatchEvent(new Event('input'));
}

function smartLayout() {
  const el = editorAreaRef.value;
  if (!el) return;
  const lines = (el.innerText || '').split(/\n+/).filter(Boolean);
  if (lines.length > 1) {
    el.innerHTML = lines.map(l => l.length > 30 ? `<h2>${escapeHtml(l)}</h2><p>` : `<p>${escapeHtml(l)}</p>`).join('');
    el.dispatchEvent(new Event('input'));
    toast.show('已应用智能排版');
  } else {
    toast.show('正文较短，无需排版');
  }
}

function onFileChange(e) {
  const f = e.target.files[0];
  if (!f) return;
  if (f.type.startsWith('image/')) {
    const r = new FileReader();
    r.onload = ev => {
      const img = `<img src="${ev.target.result}" style="max-width:100%;border-radius:6px;margin:6px 0;">`;
      document.execCommand('insertHTML', false, img);
      editorAreaRef.value?.dispatchEvent(new Event('input'));
      toast.show('已插入图片');
    };
    r.readAsDataURL(f);
  } else {
    const r = new FileReader();
    r.onload = ev => {
      const html = '<p>' + escapeHtml(ev.target.result || '').replace(/\n/g, '</p><p>') + '</p>';
      if (editorAreaRef.value) {
        editorAreaRef.value.innerHTML = html;
        editorAreaRef.value.dispatchEvent(new Event('input'));
      }
      toast.show('已导入 ' + f.name);
    };
    r.readAsText(f);
  }
  e.target.value = '';
}

function onBgFileChange(e) {
  const f = e.target.files[0];
  if (!f) return;
  const r = new FileReader();
  r.onload = ev => {
    bgImage.value = ev.target.result;
    toast.show('已替换背景');
  };
  r.readAsDataURL(f);
  e.target.value = '';
}

function resetBg() {
  bgImage.value = '';
  toast.show('已恢复默认背景');
}

function adjustSetting(key, delta, min, max, decimals = 0) {
  let v = settings.value[key] + delta;
  if (min !== undefined) v = Math.max(min, v);
  if (max !== undefined) v = Math.min(max, v);
  if (decimals > 0) {
    const f = Math.pow(10, decimals);
    v = Math.round(v * f) / f;
  }
  settings.value[key] = v;
}

function resetTextSettings() {
  settings.value.titleSize = 'sm';
  settings.value.bodySize = 'sm';
  settings.value.titleFont = '平方';
  settings.value.bodyFont = '平方';
  toast.show('文字已恢复默认');
}

function resetSpacingSettings() {
  settings.value.bodyAlign = 'left';
  settings.value.lineHeight = 1.8;
  settings.value.marginTop = 0;
  settings.value.marginBottom = 0;
  settings.value.paddingLeft = 0;
  settings.value.paddingRight = 0;
  settings.value.textIndent = 0;
  settings.value.lineSpacing = 0;
  toast.show('间距已恢复默认');
}

function exportPNG() {
  const node = previewFrameRef.value;
  if (!node) return;
  const w = node.offsetWidth, h = node.offsetHeight, scale = 2;

  if (useHtml2canvas.value) {
    const stage = previewStageRef.value;
    const bgColor = getComputedStyle(document.body).backgroundColor;
    html2canvas(stage, { backgroundColor: bgColor, scale: 2 }).then(canvas => {
      canvas.toBlob(blob => {
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = 'HighMD-' + Date.now() + '.png';
        link.href = url;
        link.click();
        window.open(url, '_blank');
        toast.show('已导出卡片 PNG');
        setTimeout(() => URL.revokeObjectURL(url), 5000);
      }, 'image/png');
    }).catch(err => {
      toast.show('导出失败，请重试');
      console.error('html2canvas error:', err);
    });
    return;
  }

  // 手动绘制路径（原有逻辑）
  const canvas = document.createElement('canvas');
  canvas.width = w * scale;
  canvas.height = h * scale;
  const ctx = canvas.getContext('2d');
  ctx.scale(scale, scale);
  const stage = previewStageRef.value;
  const bg = getComputedStyle(stage).backgroundColor;
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, w, h);
  ctx.fillStyle = getComputedStyle(stage).color;
  ctx.textBaseline = 'top';
  const padL = 22, padR = 22, padT = 28, innerW = w - padL - padR;
  const titleEl = stage.querySelector('h1');
  const bodyEl = stage.querySelector('.body');
  const badgeEl = stage.querySelector('.badge');
  const footerEl = stage.querySelector('.footer');
  const family = getComputedStyle(stage).fontFamily;
  let y = padT;
  if (badgeEl) {
    ctx.font = '600 10px ' + family;
    const txt = badgeEl.textContent;
    const tw = ctx.measureText(txt).width + 14;
    ctx.fillStyle = 'rgba(0,0,0,0.08)';
    ctx.fillRect(padL, y, tw, 16);
    ctx.fillStyle = getComputedStyle(stage).color;
    ctx.fillText(txt, padL + 7, y + 3);
    y += 28;
  }
  if (titleEl) {
    ctx.font = '800 21px ' + family;
    wrapText(ctx, titleEl.textContent, innerW).forEach(line => {
      ctx.fillText(line, padL, y);
      y += 28;
    });
    y += 8;
  }
  if (bodyEl) {
    ctx.font = '12.5px ' + family;
    const bodyLines = wrapText(ctx, bodyEl.innerText || '', innerW);
    const maxLines = Math.floor((h - y - 30) / 22);
    bodyLines.slice(0, maxLines).forEach(line => {
      ctx.fillText(line, padL, y);
      y += 22;
    });
  }
  if (footerEl) {
    ctx.font = '10px ' + family;
    ctx.fillStyle = 'rgba(0,0,0,0.4)';
    const footText = (footerEl.textContent || '').replace(/\s+/g, ' ').trim();
    const fparts = footText.split(/\s+/);
    ctx.fillText(fparts[0] || '', padL, h - 22);
    if (fparts.length > 1) {
      const last = fparts[fparts.length - 1];
      ctx.fillText(last, w - padR - ctx.measureText(last).width, h - 22);
    }
  }
  const link = document.createElement('a');
  link.download = 'HighMD-' + Date.now() + '.png';
  link.href = canvas.toDataURL('image/png');
  link.click();
  toast.show('已导出卡片 PNG');
}

function wrapText(ctx, text, maxWidth) {
  const out = [];
  (text || '').split(/\n/).forEach(line => {
    if (!line.trim()) {
      out.push('');
      return;
    }
    let cur = '';
    for (const ch of line) {
      if (ctx.measureText(cur + ch).width > maxWidth && cur) {
        out.push(cur);
        cur = ch;
      } else {
        cur += ch;
      }
    }
    if (cur) out.push(cur);
  });
  return out;
}

// === 自动保存：监听状态变化 ===
watch([pages, currentPage, showTitle, autoPage, ratio, currentTpl, tplName, settings], () => {
  try {
    const p = pages.value[currentPage.value];
    if (editorAreaRef.value) p.html = editorAreaRef.value.innerHTML;
    p.title = titleValue.value;
    ws.save({
      pages: pages.value.map(pg => ({ title: pg.title, html: pg.html })),
      currentPage: currentPage.value,
      showTitle: showTitle.value,
      autoPage: autoPage.value,
      ratio: ratio.value,
      currentTpl: currentTpl.value,
      tplName: tplName.value,
    });
  } catch (_) { /* ignore */ }
}, { deep: true });

onMounted(() => {
  // 恢复工作区状态
  try {
    const saved = ws.restore();
    if (saved && saved.pages && saved.pages.length) {
      pages.value = saved.pages.map(p => ({ title: p.title || '', html: p.html || '' }));
      currentPage.value = Math.min(saved.currentPage || 0, pages.value.length - 1);
      showTitle.value = saved.showTitle !== false;
      autoPage.value = saved.autoPage !== false;
      ratio.value = saved.ratio || '3-5';
      currentTpl.value = saved.currentTpl || 'tpl-default';
      tplName.value = saved.tplName || '简单格子';
      refreshPage();
    }
  } catch (_) { /* ignore */ }
});

onBeforeUnmount(() => {
  // 保存状态
  try {
    const p = pages.value[currentPage.value];
    if (editorAreaRef.value) p.html = editorAreaRef.value.innerHTML;
    p.title = titleValue.value;
    ws.save({
      pages: pages.value.map(pg => ({ title: pg.title, html: pg.html })),
      currentPage: currentPage.value,
      showTitle: showTitle.value,
      autoPage: autoPage.value,
      ratio: ratio.value,
      currentTpl: currentTpl.value,
      tplName: tplName.value,
    });
  } catch (_) { /* ignore */ }
});
</script>

<style>

.highmd-editor-root{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;font-size:14px;color:var(--text);background:var(--bg);-webkit-font-smoothing:antialiased}
.highmd-editor-root .topbar{height:52px;background:var(--panel);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 18px;position:sticky;top:0;z-index:50;backdrop-filter:saturate(150%) blur(8px)}
.highmd-editor-root .brand{display:flex;align-items:center;gap:10px;font-weight:700}
.highmd-editor-root .brand .mark{width:32px;height:32px;background:linear-gradient(135deg,var(--primary) 0%,var(--primary-2) 100%);color:#fff;border-radius:10px;display:grid;place-items:center;font-size:12px;font-weight:800;letter-spacing:-.5px;box-shadow:0 2px 8px var(--primary-glow)}
.highmd-editor-root .brand .name{font-size:16px;letter-spacing:-.3px;background:linear-gradient(90deg,var(--text) 0%,var(--text-2) 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.highmd-editor-root .brand .name span{font-weight:400;opacity:.5;font-size:12px;margin-left:4px;-webkit-text-fill-color:var(--text-3)}
.highmd-editor-root .nav-group{display:flex;align-items:center;gap:6px;margin-left:16px;background:var(--panel-2);padding:4px;border-radius:10px;border:1px solid var(--border)}
.highmd-editor-root .nav-btn{height:32px;padding:0 14px;border-radius:8px;display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--text-2);border:0;background:transparent;transition:all .15s;white-space:nowrap;font-weight:500}
.highmd-editor-root .nav-btn:hover{color:var(--text);background:var(--panel-2)}
.highmd-editor-root .nav-btn.primary{background:linear-gradient(180deg,var(--primary) 0%,var(--primary-2) 100%);color:#fff;box-shadow:0 2px 8px var(--primary-glow),0 0 0 1px rgba(255,255,255,.06) inset}
.highmd-editor-root .nav-btn.primary:hover{background:linear-gradient(180deg,var(--primary-2) 0%,#be123c 100%);box-shadow:0 4px 14px var(--primary-glow)}
.highmd-editor-root .nav-btn svg{width:14px;height:14px}
.highmd-editor-root .topbar .spacer{flex:1}
.highmd-editor-root .right-nav{display:flex;align-items:center;gap:18px;font-size:13px;color:var(--text-2)}
.highmd-editor-root .right-nav a{transition:color .15s}
.highmd-editor-root .right-nav a:hover{color:var(--text)}
.highmd-editor-root .right-nav .invite{color:#e62e3f;display:inline-flex;align-items:center;gap:4px}
.highmd-editor-root .vip-btn{height:32px;padding:0 14px;background:linear-gradient(95deg,#22C7B4 0%,var(--primary) 100%);color:#fff;font-weight:600;border-radius:8px;display:inline-flex;align-items:center;gap:4px;box-shadow:0 2px 6px rgba(255,138,61,.3);font-size:13px}
.highmd-editor-root .vip-btn:hover{filter:brightness(1.05)}
.highmd-editor-root .login-link{font-weight:500;color:var(--text)}
.highmd-editor-root .workspace{display:grid;grid-template-columns:72px 1fr 1fr 300px;height:calc(100vh - 52px)}
.highmd-editor-root .pages-bar{background:var(--panel);border-right:1px solid var(--border);display:flex;flex-direction:column;align-items:center;padding:14px 0;gap:10px;overflow-y:auto}
.highmd-editor-root .page-thumb{width:58px;height:78px;border:1.5px dashed var(--border-strong);border-radius:4px;background:var(--panel);display:grid;place-items:center;font-size:9px;color:var(--text-3);cursor:pointer;position:relative;padding:6px 4px;text-align:center;line-height:1.2;transition:all .15s;flex-shrink:0;overflow:hidden;word-break:break-all}
.highmd-editor-root .page-thumb:hover{border-color:var(--text-3)}
.highmd-editor-root .page-thumb.active{border:1.5px solid var(--primary);border-style:solid}
.highmd-editor-root .page-thumb.active::after{content:"";position:absolute;bottom:0;left:0;right:0;height:3px;background:var(--primary);border-radius:0 0 3px 3px}
.highmd-editor-root .page-add{width:56px;height:56px;border:1px solid var(--border);border-radius:6px;display:grid;place-items:center;color:var(--text-3);transition:all .15s;flex-shrink:0}
.highmd-editor-root .page-add:hover{color:var(--text);border-color:var(--border-strong);background:var(--panel-2)}
.highmd-editor-root .pages-bar .spacer{flex:1}
.highmd-editor-root .collapse-btn{font-size:12px;color:var(--text-3);display:inline-flex;align-items:center;gap:4px;padding:8px 12px;flex-shrink:0}
.highmd-editor-root .collapse-btn:hover{color:var(--text)}
.highmd-editor-root .editor{background:var(--bg);padding:20px 28px 28px;display:flex;flex-direction:column;gap:14px;overflow-y:auto}
.highmd-editor-root .editor-card{background:var(--panel);border-radius:var(--radius-lg);padding:20px 24px;box-shadow:var(--shadow-sm);border:1px solid var(--border);position:relative;overflow:hidden}
.highmd-editor-root .editor-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,var(--primary) 0%,var(--neon-cyan) 100%);border-radius:var(--radius-lg) var(--radius-lg) 0 0}
.highmd-editor-root .field-label{display:flex;align-items:center;justify-content:space-between;font-size:13px;font-weight:600;color:var(--text);margin-bottom:10px}
.highmd-editor-root .field-label .label-info{color:var(--text-3);font-weight:400;font-size:12px}
.highmd-editor-root .title-input{width:100%;height:42px;padding:0 14px;border:1px solid var(--border);border-radius:8px;font-size:15px;transition:border-color .15s;background:var(--panel)}
.highmd-editor-root .title-input:focus{border-color:var(--primary)}
.highmd-editor-root .toolbar{display:flex;align-items:center;gap:2px;padding:6px 0;border-bottom:1px solid var(--border);margin-bottom:12px;flex-wrap:wrap}
.highmd-editor-root .tb-btn{height:30px;min-width:30px;padding:0 8px;border-radius:6px;display:inline-flex;align-items:center;justify-content:center;gap:4px;color:var(--text-2);font-size:13px;font-weight:500;transition:all .15s}
.highmd-editor-root .tb-btn:hover{background:var(--panel-2);color:var(--text)}
.highmd-editor-root .tb-btn.active{background:var(--primary);color:#fff}
.highmd-editor-root .tb-btn svg{width:15px;height:15px}
.highmd-editor-root .tb-sep{width:1px;height:16px;background:var(--border);margin:0 6px;align-self:center}
.highmd-editor-root .tb-check{display:inline-flex;align-items:center;gap:3px;font-size:11px;color:var(--text-2);cursor:pointer;white-space:nowrap;user-select:none;padding:0 4px;height:30px}
.highmd-editor-root .tb-check input[type=checkbox]{accent-color:var(--primary);cursor:pointer;margin:0}
.highmd-editor-root .tb-spacer{flex:1}
.highmd-editor-root .tb-action{font-size:12px;color:var(--text-2);display:inline-flex;align-items:center;gap:4px;padding:0 8px;height:30px;border-radius:6px;transition:all .15s}
.highmd-editor-root .tb-action:hover{color:var(--text);background:var(--panel-2)}
.highmd-editor-root .tb-action svg{width:13px;height:13px}
.highmd-editor-root .editor-area{min-height:260px;padding:6px 4px;font-size:15px;line-height:1.85;color:var(--text-2);outline:none}
.highmd-editor-root .editor-area:empty::before{content:"创作从这里开始";color:var(--text-3)}
.highmd-editor-root .editor-area h1{font-size:22px;font-weight:700;color:var(--text);margin:12px 0 6px}
.highmd-editor-root .editor-area h2{font-size:18px;font-weight:700;color:var(--text);margin:10px 0 4px}
.highmd-editor-root .editor-area h3{font-size:16px;font-weight:600;color:var(--text);margin:8px 0 4px}
.highmd-editor-root .toggle{width:32px;height:18px;background:var(--primary);border-radius:999px;position:relative;cursor:pointer;transition:background .15s;flex-shrink:0}
.highmd-editor-root .toggle::after{content:"";position:absolute;top:2px;left:16px;width:14px;height:14px;background:var(--panel);border-radius:50%;transition:left .15s;box-shadow:0 1px 2px rgba(0,0,0,.2)}
.highmd-editor-root .toggle.off{background:var(--border)}
.highmd-editor-root .toggle.off::after{left:2px}
.highmd-editor-root .import-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.highmd-editor-root .import-card{background:linear-gradient(180deg,var(--panel) 0%,var(--panel-2) 100%);border:1.5px dashed var(--border);border-radius:var(--radius-lg);padding:22px 16px;text-align:center;display:flex;flex-direction:column;align-items:center;gap:10px;transition:all .2s;cursor:pointer}
.highmd-editor-root .import-card:hover{border-color:var(--primary);border-style:solid;transform:translateY(-2px);box-shadow:var(--shadow-lg);background:var(--panel)}
.highmd-editor-root .import-icon{width:38px;height:38px;border-radius:50%;display:grid;place-items:center;color:#fff}
.highmd-editor-root .import-icon svg{width:18px;height:18px}
.highmd-editor-root .import-icon.wechat{background:#07c160}
.highmd-editor-root .import-icon.feishu{background:#3370ff}
.highmd-editor-root .import-icon.notion{background:#000}
.highmd-editor-root .import-icon.upload{background:var(--primary-soft);color:var(--primary);border:1.5px dashed var(--primary)}
.highmd-editor-root .import-card span{font-size:12px;color:var(--text-2)}
.highmd-editor-root .preview{background:var(--bg);padding:20px 24px 28px;display:flex;flex-direction:column;align-items:center;gap:12px;overflow-y:auto}
.highmd-editor-root .preview-header{width:100%;display:flex;align-items:center;justify-content:space-between;font-size:13px;color:var(--text-2)}
.highmd-editor-root .preview-header .left{display:flex;align-items:center;gap:6px}
.highmd-editor-root .preview-header .name{color:var(--text);font-weight:600}
.highmd-editor-root .ratio-group{display:flex;gap:4px;background:var(--border);border-radius:7px;padding:2px}
.highmd-editor-root .ratio-btn{height:24px;min-width:34px;padding:0 8px;border-radius:5px;font-size:12px;color:var(--text-2);font-weight:500;transition:all .15s}
.highmd-editor-root .ratio-btn:hover{color:var(--text)}
.highmd-editor-root .ratio-btn.active{background:var(--primary);color:#fff}
.highmd-editor-root .preview-frame{width:100%;max-width:340px;aspect-ratio:3 / 5;border:1.5px dashed var(--border);border-radius:10px;background:var(--panel);position:relative;overflow:hidden;transition:aspect-ratio .25s}
.highmd-editor-root .preview-frame.r-3-4{aspect-ratio:3 / 4}
.highmd-editor-root .preview-stage{position:absolute;inset:6px;border-radius:6px;overflow:hidden;display:flex;flex-direction:column;padding:28px 22px 22px;font-family:"PingFang SC","Microsoft YaHei",-apple-system,sans-serif;transition:background .25s,color .25s}
.highmd-editor-root .page-indicator{font-size:12px;color:var(--text-3)}
.highmd-editor-root .tpl-default{background:#fff;color:var(--primary)}
.highmd-editor-root .tpl-mint{background:#d8eed6;color:#1a4d2a}
.highmd-editor-root .tpl-peach{background:#fde0d0;color:#6b3220}
.highmd-editor-root .tpl-cream{background:#fdf3e1;color:#5c3a1f}
.highmd-editor-root .tpl-dark{background:#1e293b;color:#f5f5f5}
.highmd-editor-root .tpl-lavender{background:#e8e2f5;color:#3a2d5e}
.highmd-editor-root .tpl-sky{background:#d8ecf7;color:#1a3a55}
.highmd-editor-root .tpl-pink{background:#fbd9e2;color:#6b1f3a}
.highmd-editor-root .tpl-rose{background:#f5d4cc;color:#5a2218}
.highmd-editor-root .tpl-amber{background:#ffe6b3;color:#4d3208}
.highmd-editor-root .tpl-coffee{background:#efe2d2;color:#4a2f1c}
.highmd-editor-root .tpl-card{--title-size:21px;--body-size:12.5px;--title-font:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;--body-font:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;--body-align:left;--line-height:1.8;--p-mt:0px;--p-mb:0px;--p-pl:0px;--p-pr:0px;--p-indent:0px;--p-spacing:0px;position:relative;height:100%;display:flex;flex-direction:column}
.highmd-editor-root .tpl-card .stars{position:absolute;top:0;right:0;font-size:12px;opacity:.35;letter-spacing:2px}
.highmd-editor-root .tpl-card .badge{font-size:10px;padding:2px 7px;border-radius:3px;display:inline-block;align-self:flex-start;margin-bottom:12px;background:rgba(0,0,0,.08);font-weight:600;letter-spacing:.5px}
.highmd-editor-root .tpl-card h1{font-size:var(--title-size);line-height:1.4;font-weight:800;margin-bottom:12px;letter-spacing:-.3px;font-family:var(--title-font);text-align:var(--body-align)}
.highmd-editor-root .tpl-card .body{font-size:var(--body-size);line-height:var(--line-height);opacity:.88;flex:1;overflow:hidden;font-family:var(--body-font);text-align:var(--body-align);letter-spacing:var(--p-spacing)}
.highmd-editor-root .tpl-card .body p{margin:var(--p-mt) 0 var(--p-mb) 0;padding-left:var(--p-pl);padding-right:var(--p-pr);text-indent:var(--p-indent)}
.highmd-editor-root .tpl-card .body h1,.highmd-editor-root .tpl-card .body h2,.highmd-editor-root .tpl-card .body h3{font-size:inherit;line-height:inherit;margin:0 0 4px 0;font-weight:700}
.highmd-editor-root .tpl-card .footer{font-size:10px;opacity:.4;margin-top:10px;display:flex;justify-content:space-between;align-items:center;border-top:1px solid currentColor;padding-top:8px}
.highmd-editor-root .template-lib{background:linear-gradient(180deg,var(--panel-2) 0%,var(--panel) 100%);border-left:1px solid var(--border);display:flex;flex-direction:column;overflow:hidden}
.highmd-editor-root .lib-tabs{display:flex;align-items:center;gap:28px;padding:16px 20px 12px;font-size:15px;border-bottom:1px solid var(--border);background:linear-gradient(180deg,var(--panel) 0%,var(--panel-2) 100%)}
.highmd-editor-root .lib-tab{position:relative;font-weight:600;color:var(--text-3);cursor:pointer;padding-bottom:6px;transition:color .15s}
.highmd-editor-root .lib-tab:hover{color:var(--text-2)}
.highmd-editor-root .lib-tab.active{color:var(--text)}
.highmd-editor-root .lib-tab.active::after{content:"";position:absolute;bottom:-1px;left:50%;transform:translateX(-50%);width:18px;height:2px;background:var(--primary);border-radius:2px}
.highmd-editor-root .lib-content{flex:1;overflow-y:auto;padding:14px 14px 24px}
.highmd-editor-root .tpl-section{margin-bottom:18px}
.highmd-editor-root .tpl-section h4{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:var(--text);margin-bottom:10px;padding:0 4px}
.highmd-editor-root .vip-tag{background:var(--primary);color:#ffd57a;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;letter-spacing:.5px}
.highmd-editor-root .tpl-row{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.highmd-editor-root .tpl-mini{aspect-ratio:3 / 4;border-radius:4px;border:1px solid rgba(0,0,0,.06);padding:7px 5px;overflow:hidden;cursor:pointer;transition:all .15s;position:relative;font-family:"PingFang SC","Microsoft YaHei",sans-serif}
.highmd-editor-root .tpl-mini:hover{transform:translateY(-1px);box-shadow:0 4px 10px rgba(0,0,0,.1)}
.highmd-editor-root .tpl-mini.active{box-shadow:0 0 0 2px var(--primary)}
.highmd-editor-root .tpl-mini .mini-title{font-weight:700;font-size:7px;margin-bottom:3px;line-height:1.3}
.highmd-editor-root .tpl-mini .mini-bar{height:1.2px;background:currentColor;opacity:.25;margin:2px 0}
.highmd-editor-root .tpl-mini .mini-footer{position:absolute;bottom:4px;left:5px;right:5px;font-size:5px;opacity:.5;display:flex;justify-content:space-between}
.highmd-editor-root .adj-panel{padding:4px 4px 24px}
.highmd-editor-root .adj-card{background:var(--panel);border:1px solid rgba(0,0,0,.06);border-radius:8px;padding:14px;margin-bottom:12px}
.highmd-editor-root .adj-row{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px;font-size:13px;color:var(--text-2)}
.highmd-editor-root .adj-row:last-child{margin-bottom:0}
.highmd-editor-root .adj-row input[type=range]{width:55%;accent-color:var(--primary)}
.highmd-editor-root .adj-row select{padding:4px 8px;border:1px solid var(--border);border-radius:4px;font-size:12px;background:var(--panel)}
.highmd-editor-root .adj-row .color-swatch{width:22px;height:22px;border-radius:50%;border:1px solid var(--border);cursor:pointer}
.highmd-editor-root .adj-tabs{display:flex;background:var(--panel-2);border-radius:8px;padding:3px;gap:2px;margin-bottom:12px}
.highmd-editor-root .adj-tab{flex:1;text-align:center;font-size:12.5px;padding:7px 4px;border-radius:6px;color:var(--text-2);cursor:pointer;transition:all .15s;font-weight:500;white-space:nowrap}
.highmd-editor-root .adj-tab:hover:not(.active){color:var(--text)}
.highmd-editor-root .adj-tab.active{background:var(--panel);color:var(--text);box-shadow:0 1px 2px rgba(0,0,0,.06);font-weight:600}
.highmd-editor-root .adj-row-2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.highmd-editor-root .adj-mini-card{background:var(--panel);border:1px solid rgba(0,0,0,.06);border-radius:8px;padding:11px 10px;display:flex;align-items:center;gap:6px;font-size:13px;font-weight:500;color:var(--text);cursor:pointer;position:relative;transition:all .15s}
.highmd-editor-root .adj-mini-card:hover{border-color:rgba(0,0,0,.18)}
.highmd-editor-root .adj-mini-card.active{box-shadow:inset 0 -2px 0 var(--primary);border-color:rgba(15,118,110,.35)}
.highmd-editor-root .adj-mini-card.vip-disabled{opacity:.7;cursor:not-allowed}
.highmd-editor-root .adj-mini-card .adj-mini-icon{color:var(--primary);font-size:16px;font-weight:700;width:16px;display:inline-flex;align-items:center;justify-content:center}
.highmd-editor-root .adj-mini-card .vip-tag{margin-left:auto;background:#111;color:#ffd57a;font-size:9px;font-weight:700;padding:1px 4px;border-radius:3px;letter-spacing:.5px}
.highmd-editor-root .adj-mini-card .adj-mini-icon svg{width:14px;height:14px}
.highmd-editor-root .adj-section{margin-bottom:14px}
.highmd-editor-root .adj-section-head{display:flex;align-items:center;gap:10px;margin-bottom:8px;font-size:13px;font-weight:600;color:var(--text);min-height:24px}
.highmd-editor-root .adj-section-head>span:first-child{font-weight:600}
.highmd-editor-root .adj-reset{margin-left:auto;font-size:12px;color:var(--text-3);display:inline-flex;align-items:center;gap:3px;background:none;border:0;cursor:pointer;font-weight:400}
.highmd-editor-root .adj-reset:hover{color:var(--primary)}
.highmd-editor-root .adj-link{font-size:12px;color:var(--text-2);display:inline-flex;align-items:center;gap:3px;background:none;border:0;cursor:pointer;font-weight:400}
.highmd-editor-root .adj-link:hover{color:var(--primary)}
.highmd-editor-root .adj-section-head .vip-tag.inline{background:#111;color:#ffd57a;font-size:9px;font-weight:700;padding:1px 5px;border-radius:3px;letter-spacing:.5px}
.highmd-editor-root .adj-section-head .bg-actions{margin-left:auto;display:flex;gap:10px}
.highmd-editor-root .adj-block{background:var(--panel);border:1px solid rgba(0,0,0,.06);border-radius:8px;padding:12px 14px;margin-bottom:8px}
.highmd-editor-root .adj-block:last-child{margin-bottom:0}
.highmd-editor-root .adj-field-label{font-size:12.5px;color:var(--text-2);margin:6px 0 6px;font-weight:500}
.highmd-editor-root .adj-field-label:first-child{margin-top:0}
.highmd-editor-root .size-group{display:flex;background:var(--panel-2);border-radius:6px;padding:2px;margin-bottom:8px}
.highmd-editor-root .size-btn{flex:1;font-size:12px;padding:6px 2px;border-radius:4px;color:var(--text-2);font-weight:500;transition:all .15s}
.highmd-editor-root .size-btn:hover{color:var(--text)}
.highmd-editor-root .size-btn.active{background:var(--primary);color:#fff}
.highmd-editor-root .font-select-wrap{position:relative}
.highmd-editor-root .font-select{width:100%;padding:8px 30px 8px 12px;border:1px solid var(--border);border-radius:6px;font-size:13px;background:var(--panel);appearance:none;-webkit-appearance:none;cursor:pointer;color:var(--text);font-family:inherit}
.highmd-editor-root .font-select:focus{outline:none;border-color:var(--primary)}
.highmd-editor-root .font-select-wrap::after{content:"\25BE";position:absolute;right:12px;top:50%;transform:translateY(-50%);pointer-events:none;color:var(--text-2);font-size:11px}
.highmd-editor-root .align-group{display:flex;background:var(--panel-2);border-radius:6px;padding:2px;flex:1;gap:0}
.highmd-editor-root .align-btn{flex:1;display:flex;align-items:center;justify-content:center;padding:7px;border-radius:4px;color:var(--text-2);transition:all .15s;background:transparent}
.highmd-editor-root .align-btn:hover{color:var(--text)}
.highmd-editor-root .align-btn.active{background:#FFC53D;color:#111}
.highmd-editor-root .align-btn svg{width:16px;height:16px}
.highmd-editor-root .num-stepper{display:flex;align-items:center;background:var(--panel);border:1px solid var(--border);border-radius:6px;padding:0 4px 0 8px;flex:1;height:32px;gap:6px;min-width:0}
.highmd-editor-root .num-stepper .step-icon{color:var(--text-2);font-size:12px;flex-shrink:0;display:inline-flex;align-items:center;justify-content:center;width:16px;line-height:1}
.highmd-editor-root .num-stepper input{flex:1;border:0;text-align:right;font-size:13px;font-weight:500;min-width:0;width:100%;background:transparent;color:var(--text);padding:0;-moz-appearance:textfield;font-family:inherit}
.highmd-editor-root .num-stepper input::-webkit-outer-spin-button,.num-stepper input::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.highmd-editor-root .num-stepper input:focus{outline:none}
.highmd-editor-root .step-arrows{display:flex;flex-direction:column;border-left:1px solid var(--border);padding-left:3px;flex-shrink:0}
.highmd-editor-root .step-up,.step-down{width:14px;height:13px;display:flex;align-items:center;justify-content:center;color:var(--text-2);font-size:8px;line-height:1;background:transparent}
.highmd-editor-root .step-up:hover,.step-down:hover{color:var(--primary)}
.highmd-editor-root .adj-row-flex{display:flex;gap:8px;margin-bottom:8px}
.highmd-editor-root .adj-row-flex:last-child{margin-bottom:0}
.highmd-editor-root .bg-upload{background:linear-gradient(180deg,#2c3a4a 0%,#1c2735 100%);border-radius:8px;height:100px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden;border:1px solid rgba(0,0,0,.06)}
.highmd-editor-root .bg-upload::before{content:"";position:absolute;inset:0;background-image:linear-gradient(45deg,rgba(255,255,255,.04) 25%,transparent 25%),linear-gradient(-45deg,rgba(255,255,255,.04) 25%,transparent 25%);background-size:18px 18px}
.highmd-editor-root .bg-upload-btn{background:var(--panel);color:var(--text);font-size:13px;font-weight:500;padding:8px 18px;border-radius:6px;z-index:1;display:inline-flex;align-items:center;gap:5px;transition:all .15s;border:1px solid var(--border)}
.highmd-editor-root .bg-upload-btn:hover{background:var(--panel-2);box-shadow:0 2px 6px rgba(0,0,0,.15)}
@media (max-width:1280px){.highmd-editor-root .workspace{grid-template-columns:68px 1fr 1fr 260px}.highmd-editor-root .editor{padding:18px 20px 22px}.highmd-editor-root .preview{padding:18px 16px 22px}}
@media (max-width:1024px){.highmd-editor-root .workspace{grid-template-columns:68px 1fr 260px}.highmd-editor-root .preview{display:none}}
@media (max-width:720px){.highmd-editor-root .workspace{grid-template-columns:56px 1fr}.highmd-editor-root .template-lib{display:none}.highmd-editor-root .nav-group{gap:4px}}
.highmd-editor-root .lib-content::-webkit-scrollbar,.highmd-editor-root .editor::-webkit-scrollbar,.highmd-editor-root .preview::-webkit-scrollbar,.highmd-editor-root .pages-bar::-webkit-scrollbar{width:6px}
.highmd-editor-root .lib-content::-webkit-scrollbar-thumb,.highmd-editor-root .editor::-webkit-scrollbar-thumb,.highmd-editor-root .preview::-webkit-scrollbar-thumb,.highmd-editor-root .pages-bar::-webkit-scrollbar-thumb{background:rgba(0,0,0,.1);border-radius:3px}

</style>