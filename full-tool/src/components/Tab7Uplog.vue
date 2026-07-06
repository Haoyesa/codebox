<template>
  <div ref="editorContainer" class="highmd-editor-root" :class="$attrs.class">
<header class="topbar">
  <div class="brand"><div class="mark">H</div><div class="name">HighMD</div></div>
  <div class="nav-group">
    <button class="nav-btn" data-act="new"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>新建笔记</button>
    <button class="nav-btn" data-act="export"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>导出</button>
  </div>
</header>
<main class="workspace">
  <aside class="pages-bar" id="pagesBar">
    <div class="page-thumb active" data-page="0"><span>HighMD<br/>让表达更精炼</span></div>
    <button class="page-add" id="addPage" title="添加页面"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></button>
  </aside>
  <section class="editor">
    <div class="editor-card">
      <div class="field-label"><span>标题</span><div style="display:flex;align-items:center;gap:8px;"><span class="label-info">显示</span><div class="toggle" id="titleToggle"></div></div></div>
      <input class="title-input" id="titleInput" placeholder="在此输入标题" value="HighMD：把想法装进卡片，让表达更精炼" />
    </div>
    <div class="editor-card">
      <div class="field-label"><span>正文</span><div style="display:flex;align-items:center;gap:8px;"><span class="label-info">自动分页 ①</span><div class="toggle" id="pageToggle"></div></div></div>
      <div class="toolbar">
        <button class="tb-btn" id="undoBtn" title="撤销 (Ctrl+Z)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 14 4 9 9 4"/><path d="M20 20v-7a4 4 0 0 0-4-4H4"/></svg></button>
        <button class="tb-btn" id="redoBtn" title="重做 (Ctrl+Y)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 14 20 9 15 4"/><path d="M4 20v-7a4 4 0 0 1 4-4h12"/></svg></button>
        <div class="tb-sep"></div>
        <button class="tb-btn" data-cmd="h1">H1</button>
        <button class="tb-btn" data-cmd="h2">H2</button>
        <button class="tb-btn" data-cmd="h3">H3</button>
        <div class="tb-sep"></div>
        <button class="tb-btn" id="emojiBtn" title="表情"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg></button>
        <button class="tb-btn" id="imgBtn" title="插入图片"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg></button>
        <button class="tb-btn" id="markBtn" title="荧光标记"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l-6 6v3h3l6-6"/><path d="M22 5l-3-3-9 9 3 3 9-9z"/></svg></button>
        <button class="tb-btn" id="downloadBtn" title="导出PNG"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg></button>
        <label class="tb-check" title="html2canvas 模式：完整渲染富文本和图片（默认开启）"><input type="checkbox" v-model="useHtml2canvas" /> 富文本</label>
        <div class="tb-spacer"></div>
        <button class="tb-action" data-act="layout"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>智能排版</button>
      </div>
      <div class="editor-area" id="editorArea" contenteditable="true"></div>
    </div>
    <div class="import-grid" style="grid-template-columns:1fr;">
      <button class="import-card" data-import="local"><div class="import-icon upload"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></div><span>导入 Markdown / 文本 / 图片</span></button>
    </div>
  </section>
  <section class="preview">
    <div class="preview-header">
      <div class="left"><span>预览</span><span style="opacity:.4">·</span><span class="name" id="tplName">简单格子</span></div>
      <div class="ratio-group">
        <button class="ratio-btn" data-ratio="3-4">3:4</button>
        <button class="ratio-btn active" data-ratio="3-5">3:5</button>
      </div>
    </div>
    <div class="preview-frame r-3-5" id="previewFrame">
      <div class="preview-stage tpl-default" id="previewStage">
        <div class="tpl-card">
          <span class="stars">✦ ✦ ✦</span>
          <span class="badge" id="prevBadge">HighMD · 灵感笔记</span>
          <h1 id="prevTitle">HighMD：把想法装进卡片，让表达更精炼</h1>
          <div class="body" id="prevBody"></div>
          <div class="footer"><span>HighMD</span><span id="prevPage">1/1</span></div>
        </div>
      </div>
    </div>
    <div class="page-indicator" id="pageIndicator">1/1</div>
  </section>
  <aside class="template-lib">
    <div class="lib-tabs">
      <div class="lib-tab active" data-tab="tpl">模板库</div>
      <div class="lib-tab" data-tab="adj">调整</div>
    </div>
    <div class="lib-content" id="libContent"></div>
  </aside>
</main>


    <input type="file" id="fileInput" accept="image/*,.md,.txt" hidden />
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useToast } from '../composables/useToast.js';
import { useWorkspaceState } from '../composables/useWorkspaceState.js';
import html2canvas from 'html2canvas';

const editorContainer = ref(null);
const toast = useToast();
const ws = useWorkspaceState('highmd');
const useHtml2canvas = ref(true);

onMounted(() => {
  const container = editorContainer.value;
  if (!container) return;

  function escapeHtml(str) {
    if (typeof str !== 'string') return '';
    const el = document.createElement('div');
    el.textContent = str;
    return el.innerHTML;
  }

const $=s=>container.querySelector(s);
  const $$=s=>Array.from(Array.from(container.querySelectorAll(s)));
  const state={pages:[{title:'HighMD：把想法装进卡片，让表达更精炼',html:''}],currentPage:0,showTitle:true,autoPage:true,ratio:'3-5',currentTpl:'tpl-default',tplName:'简单格子'};
  const titleInput=$('#titleInput'),editorArea=$('#editorArea'),prevTitle=$('#prevTitle'),prevBody=$('#prevBody'),prevPage=$('#prevPage'),pageIndicator=$('#pageIndicator'),prevBadge=$('#prevBadge'),previewStage=$('#previewStage'),previewFrame=$('#previewFrame'),tplNameEl=$('#tplName'),libContent=$('#libContent'),toast=$('#toast'),pagesBar=$('#pagesBar');
  const sections=[
    {name:'简单格子',items:[{id:'tpl-default',cls:'tpl-default',name:'白色简约',text:'HighMD 让表达更精炼'},{id:'tpl-mint',cls:'tpl-mint',name:'清新薄荷',text:'HighMD 让表达更精炼'},{id:'tpl-peach',cls:'tpl-peach',name:'蜜桃暖意',text:'HighMD 让表达更精炼'}]},
    {name:'智启新时代-日签版',items:[{id:'tpl-cream',cls:'tpl-cream',name:'日签·米黄',text:'DAY 06 智启'},{id:'tpl-amber',cls:'tpl-amber',name:'日签·琥珀',text:'DAY 06 智启'},{id:'tpl-sky',cls:'tpl-sky',name:'日签·晴空',text:'DAY 06 智启'}]},
    {name:'智启新时代',items:[{id:'tpl-dark',cls:'tpl-dark',name:'极简深色',text:'智启新时代'},{id:'tpl-lavender',cls:'tpl-lavender',name:'知性紫调',text:'智启新时代'},{id:'tpl-rose',cls:'tpl-rose',name:'玫瑰宣言',text:'智启新时代'}]},
    {name:'咖啡慢生活',items:[{id:'tpl-coffee',cls:'tpl-coffee',name:'晨光咖啡',text:'一杯咖啡 慢度时光'},{id:'tpl-pink',cls:'tpl-pink',name:'玫瑰拿铁',text:'一杯咖啡 慢度时光'},{id:'tpl-mint2',cls:'tpl-mint',name:'薄荷冰咖',text:'一杯咖啡 慢度时光'}]}
  ];
  function renderLibrary(){
    libContent.innerHTML=sections.map(sec=>'<div class="tpl-section"><h4>'+sec.name+'</h4><div class="tpl-row">'+sec.items.map(it=>'<div class="tpl-mini '+it.cls+(state.currentTpl===it.id?' active':'')+'" data-tpl="'+it.id+'" data-cls="'+it.cls+'" data-section="'+sec.name+'" data-text="'+it.text+'" title="'+it.name+'"><div class="mini-title">'+it.text+'</div><div class="mini-bar"></div><div class="mini-bar" style="width:80%"></div><div class="mini-bar" style="width:60%"></div><div class="mini-bar" style="width:70%"></div><div class="mini-bar" style="width:50%"></div><div class="mini-footer"><span>HighMD</span><span>1/1</span></div></div>').join('')+'</div></div>').join('');
  }
  function renderAdjust(){
    libContent.innerHTML = `
      <div class="adj-panel">
        <div class="adj-tabs">
          <div class="adj-tab active" data-scope="current">当前卡片(组)属性</div>
          <div class="adj-tab" data-scope="global">全局卡片属性</div>
        </div>

        <div class="adj-row-2">
          <div class="adj-mini-card active" data-section="full">
            <span class="adj-mini-icon">+</span>
            <span>全文设置</span>
          </div>
          <div class="adj-mini-card" data-section="tpl">
            <span class="adj-mini-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg></span>
            <span>样式模版</span>
          </div>
        </div>

        <div class="adj-section">
          <div class="adj-section-head">
            <span>文字设置:</span>
            <button class="adj-reset" data-reset="text">\u21BA 恢复默认值</button>
          </div>
          <div class="adj-block">
            <div class="adj-field-label">标题:</div>
            <div class="size-group" data-target="title">
              <button class="size-btn" data-size="xs">最小</button>
              <button class="size-btn active" data-size="sm">小</button>
              <button class="size-btn" data-size="md">中</button>
              <button class="size-btn" data-size="lg">大</button>
              <button class="size-btn" data-size="xl">最大</button>
            </div>
            <div class="font-select-wrap">
              <select class="font-select" data-target="title">
                <option>平方</option>
                <option>思源黑体</option>
                <option>系统默认</option>
                <option>衬线</option>
              </select>
            </div>
          </div>
          <div class="adj-block">
            <div class="adj-field-label">正文:</div>
            <div class="size-group" data-target="body">
              <button class="size-btn" data-size="xs">最小</button>
              <button class="size-btn active" data-size="sm">小</button>
              <button class="size-btn" data-size="md">中</button>
              <button class="size-btn" data-size="lg">大</button>
              <button class="size-btn" data-size="xl">最大</button>
            </div>
            <div class="font-select-wrap">
              <select class="font-select" data-target="body">
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
            <button class="adj-reset" data-reset="spacing">\u21BA 恢复默认值</button>
          </div>
          <div class="adj-block">
            <div class="adj-row-flex">
              <div class="align-group" data-target="align">
                <button class="align-btn active" data-align="left" title="左对齐"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="15" y2="12"/><line x1="3" y1="18" x2="18" y2="18"/></svg></button>
                <button class="align-btn" data-align="center" title="居中"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg></button>
                <button class="align-btn" data-align="right" title="右对齐"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="9" y1="12" x2="21" y2="12"/><line x1="6" y1="18" x2="21" y2="18"/></svg></button>
                <button class="align-btn" data-align="justify" title="两端对齐"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg></button>
              </div>
              <div class="num-stepper" data-target="lineHeight">
                <span class="step-icon" title="行高">\u2261</span>
                <input type="number" value="1.8" min="1" max="3" step="0.1" />
                <div class="step-arrows"><button class="step-up">\u25B4</button><button class="step-down">\u25BE</button></div>
              </div>
            </div>
            <div class="adj-row-flex">
              <div class="num-stepper" data-target="marginTop">
                <span class="step-icon" title="段前距">\u2191</span>
                <input type="number" value="0" min="0" max="50" step="1" />
                <div class="step-arrows"><button class="step-up">\u25B4</button><button class="step-down">\u25BE</button></div>
              </div>
              <div class="num-stepper" data-target="marginBottom">
                <span class="step-icon" title="段后距">\u2193</span>
                <input type="number" value="0" min="0" max="50" step="1" />
                <div class="step-arrows"><button class="step-up">\u25B4</button><button class="step-down">\u25BE</button></div>
              </div>
            </div>
            <div class="adj-row-flex">
              <div class="num-stepper" data-target="paddingLeft">
                <span class="step-icon" title="左缩进">\u2190</span>
                <input type="number" value="0" min="0" max="50" step="1" />
                <div class="step-arrows"><button class="step-up">\u25B4</button><button class="step-down">\u25BE</button></div>
              </div>
              <div class="num-stepper" data-target="paddingRight">
                <span class="step-icon" title="右缩进">\u2192</span>
                <input type="number" value="0" min="0" max="50" step="1" />
                <div class="step-arrows"><button class="step-up">\u25B4</button><button class="step-down">\u25BE</button></div>
              </div>
            </div>
            <div class="adj-row-flex">
              <div class="num-stepper" data-target="textIndent">
                <span class="step-icon" title="首行缩进">\u21B5</span>
                <input type="number" value="0" min="0" max="50" step="1" />
                <div class="step-arrows"><button class="step-up">\u25B4</button><button class="step-down">\u25BE</button></div>
              </div>
              <div class="num-stepper" data-target="lineSpacing">
                <span class="step-icon" title="字间距">\u2195</span>
                <input type="number" value="0" min="0" max="20" step="1" />
                <div class="step-arrows"><button class="step-up">\u25B4</button><button class="step-down">\u25BE</button></div>
              </div>
            </div>
          </div>
        </div>

        <div class="adj-section">
          <div class="adj-section-head">
            <span>背景替换:</span>
            <span class="bg-actions">
              <button class="adj-link" data-act="crop">\u29C9 裁剪图片</button>
              <button class="adj-link" data-act="resetbg">\u21BA 恢复默认背景</button>
            </span>
          </div>
          <div class="bg-upload">
            <button class="bg-upload-btn" id="bgUploadBtn">\u2191 上传图片</button>
            <input type="file" id="bgFileInput" accept="image/*" hidden />
          </div>
        </div>
      </div>
    `;
    bindAdjust();
  }

  function bindAdjust(){
    const stage = $('#previewStage');
    const card = stage.querySelector('.tpl-card');

    $$('.size-group').forEach(group => {
      const target = group.dataset.target;
      const prop = target === 'title' ? '--title-size' : '--body-size';
      const sizeMap = {
        title: { xs:'16px', sm:'21px', md:'26px', lg:'32px', xl:'40px' },
        body:  { xs:'11px', sm:'12.5px', md:'14px', lg:'16px', xl:'20px' }
      };
      group.querySelectorAll('.size-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          card.style.setProperty(prop, sizeMap[target][btn.dataset.size]);
          group.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
        });
      });
    });

    $$('.font-select').forEach(sel => {
      sel.addEventListener('change', () => {
        const target = sel.dataset.target;
        const prop = target === 'title' ? '--title-font' : '--body-font';
        const fontMap = {
          '\u5e73\u65b9':'-apple-system,"PingFang SC","Microsoft YaHei",sans-serif',
          '\u601d\u6e90\u9ed1\u4f53':'"Source Han Sans CN","Noto Sans SC",sans-serif',
          '\u7cfb\u7edf\u9ed8\u8ba4':'-apple-system,BlinkMacSystemFont,sans-serif',
          '\u886c\u7ebf':'Georgia,"Times New Roman",serif'
        };
        card.style.setProperty(prop, fontMap[sel.value] || fontMap['\u5e73\u65b9']);
      });
    });

    $$('.align-group').forEach(group => {
      group.querySelectorAll('.align-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          card.style.setProperty('--body-align', btn.dataset.align);
          group.querySelectorAll('.align-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
        });
      });
    });

    const propMap = {
      lineHeight:'--line-height', marginTop:'--p-mt', marginBottom:'--p-mb',
      paddingLeft:'--p-pl', paddingRight:'--p-pr', textIndent:'--p-indent',
      lineSpacing:'--p-spacing'
    };
    $$('.num-stepper').forEach(stepper => {
      const target = stepper.dataset.target;
      const prop = propMap[target];
      const input = stepper.querySelector('input');
      const decimals = (input.step && input.step.includes('.')) ? input.step.split('.')[1].length : 0;
      const apply = () => {
        const v = parseFloat(input.value);
        if (isNaN(v)) return;
        let suffix = 'px';
        if (target === 'lineHeight') suffix = '';
        card.style.setProperty(prop, v + suffix);
      };
      const setVal = (v) => {
        const f = Math.pow(10, decimals);
        input.value = String(Math.round(v * f) / f);
        apply();
      };
      input.addEventListener('input', apply);
      input.addEventListener('blur', () => { if (decimals > 0) setVal(parseFloat(input.value) || 0); });
      stepper.querySelector('.step-up').addEventListener('click', () => {
        const step = parseFloat(input.step) || 1;
        setVal((parseFloat(input.value) || 0) + step);
      });
      stepper.querySelector('.step-down').addEventListener('click', () => {
        const step = parseFloat(input.step) || 1;
        setVal((parseFloat(input.value) || 0) - step);
      });
    });

    $$('.adj-reset').forEach(btn => {
      btn.addEventListener('click', () => {
        const kind = btn.dataset.reset;
        if (kind === 'text') {
          ['--title-size','--body-size','--title-font','--body-font'].forEach(p => card.style.removeProperty(p));
          $$('.size-btn').forEach(b => b.classList.remove('active'));
          $$('.size-btn[data-size="sm"]').forEach(b => b.classList.add('active'));
          $$('.font-select').forEach(s => s.selectedIndex = 0);
          toast.show('文字已恢复默认');
        } else if (kind === 'spacing') {
          ['--body-align','--line-height','--p-mt','--p-mb','--p-pl','--p-pr','--p-indent','--p-spacing'].forEach(p => card.style.removeProperty(p));
          $$('.align-btn').forEach(b => b.classList.remove('active'));
          $$('.align-btn[data-align="left"]').forEach(b => b.classList.add('active'));
          const defaults = { lineHeight:'1.8', marginTop:0, marginBottom:0, paddingLeft:0, paddingRight:0, textIndent:0, lineSpacing:0 };
          $$('.num-stepper').forEach(s => { const t = s.dataset.target; if (defaults[t] !== undefined) s.querySelector('input').value = defaults[t]; });
          toast.show('间距已恢复默认');
        }
      });
    });

    $$('.adj-tab').forEach(t => {
      t.addEventListener('click', () => {
        $$('.adj-tab').forEach(x => x.classList.remove('active'));
        t.classList.add('active');
        if (t.dataset.scope === 'global') toast.show('已切换到全局卡片属性');
      });
    });

    $$('.adj-mini-card').forEach(c => {
      c.addEventListener('click', () => {
        $$('.adj-mini-card').forEach(x => x.classList.remove('active'));
        c.classList.add('active');
      });
    });

    const cropBtn = libContent.querySelector('[data-act="crop"]');
    if (cropBtn) cropBtn.addEventListener('click', () => toast.show('\u8bf7\u5148\u4e0a\u4f20\u56fe\u7247\u518d\u88c1\u526a'));
    const resetBgBtn = libContent.querySelector('[data-act="resetbg"]');
    if (resetBgBtn) resetBgBtn.addEventListener('click', () => {
      stage.style.backgroundImage = '';
      stage.style.backgroundSize = '';
      stage.style.backgroundPosition = '';
      toast.show('\u5df2\u6062\u590d\u9ed8\u8ba4\u80cc\u666f');
    });

    const bgBtn = $('#bgUploadBtn');
    const bgInput = $('#bgFileInput');
    if (bgBtn && bgInput) {
      bgBtn.addEventListener('click', () => bgInput.click());
      bgInput.addEventListener('change', e => {
        const f = e.target.files[0]; if (!f) return;
        const r = new FileReader();
        r.onload = ev => {
          stage.style.backgroundImage = 'url(' + ev.target.result + ')';
          stage.style.backgroundSize = 'cover';
          stage.style.backgroundPosition = 'center';
          toast.show('\u5df2\u66ff\u6362\u80cc\u666f');
        };
        r.readAsDataURL(f);
        e.target.value = '';
      });
    }
  }
  function applyTemplate(id,cls,name){
    state.currentTpl=id;state.tplName=name;tplNameEl.textContent=name;previewStage.className='preview-stage '+cls;prevBadge.textContent=(name.indexOf('日签')>-1?'日签 · DAY 06':name.indexOf('咖啡')>-1?'一杯咖啡 · 慢度时光':name.indexOf('智启')>-1?'智启 · 新时代':'HighMD · 灵感笔记');$$('.tpl-mini').forEach(m=>m.classList.remove('active'));const t=container.querySelector('.tpl-mini[data-tpl="'+id+'"]');if(t)t.classList.add('active');
  }
  renderLibrary();applyTemplate('tpl-default','tpl-default','简单格子');
  libContent.addEventListener('click',e=>{const t=e.target.closest('.tpl-mini');if(!t)return;applyTemplate(t.dataset.tpl,t.dataset.cls,t.dataset.section);toast.show('已应用：'+t.title);});
  $$('.lib-tab').forEach(t=>t.addEventListener('click',()=>{$$('.lib-tab').forEach(x=>x.classList.remove('active'));t.classList.add('active');if(t.dataset.tab==='adj')renderAdjust();else renderLibrary();}));
  titleInput.addEventListener('input',()=>{state.pages[state.currentPage].title=titleInput.value;prevTitle.textContent=titleInput.value||'HighMD：把想法装进卡片，让表达更精炼';updateThumb();});
  editorArea.addEventListener('input',()=>{state.pages[state.currentPage].html=editorArea.innerHTML;prevBody.innerHTML=editorArea.innerHTML;});
  $('#titleToggle').addEventListener('click',e=>{state.showTitle=!state.showTitle;e.currentTarget.classList.toggle('off',!state.showTitle);prevTitle.style.display=state.showTitle?'':'none';});
  $('#pageToggle').addEventListener('click',e=>{state.autoPage=!state.autoPage;e.currentTarget.classList.toggle('off',!state.autoPage);toast.show(state.autoPage?'已开启自动分页':'已关闭自动分页');});
  $$('.ratio-btn').forEach(btn=>btn.addEventListener('click',()=>{$$('.ratio-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');state.ratio=btn.dataset.ratio;previewFrame.classList.toggle('r-3-4',state.ratio==='3-4');}));
  $$('.tb-btn[data-cmd]').forEach(btn=>btn.addEventListener('mousedown',e=>{e.preventDefault();document.execCommand('formatBlock',false,btn.dataset.cmd.toUpperCase());editorArea.dispatchEvent(new Event('input'));}));
  $('#emojiBtn').addEventListener('click',()=>{const em=['😊','✨','🎉','💡','📌','🚀','🌈','☕','🌸','🔥','👍','💪','🌟','🍀','🎯','✏️'];const c=em[Math.floor(Math.random()*em.length)];document.execCommand('insertText',false,c);editorArea.dispatchEvent(new Event('input'));});
  $('#imgBtn').addEventListener('click',()=>$('#fileInput').click());
  $('#fileInput').addEventListener('change',e=>{const f=e.target.files[0];if(!f)return;if(f.type.startsWith('image/')){const r=new FileReader();r.onload=ev=>{const img='<img src="'+ev.target.result+'" style="max-width:100%;border-radius:6px;margin:6px 0;">';document.execCommand('insertHTML',false,img);editorArea.dispatchEvent(new Event('input'));toast.show('已插入图片');};r.readAsDataURL(f);}else{const r=new FileReader();r.onload=ev=>{editorArea.innerHTML='<p>'+escapeHtml(ev.target.result||'').replace(/\n/g,'</p><p>')+'</p>';editorArea.dispatchEvent(new Event('input'));toast.show('已导入 '+f.name);};r.readAsText(f);}e.target.value='';});
  $('#markBtn').addEventListener('click',()=>{document.execCommand('hiliteColor',false,'#fff3a3');toast.show('已开启荧光笔');});
  $('#downloadBtn').addEventListener('click',exportPNG);
  $('#undoBtn').addEventListener('click',()=>{document.execCommand('undo');editorArea.dispatchEvent(new Event('input'));});
  $('#redoBtn').addEventListener('click',()=>{document.execCommand('redo');editorArea.dispatchEvent(new Event('input'));});
  function renderPages(){const add=$('#addPage');pagesBar.innerHTML='';state.pages.forEach((p,i)=>{const t=document.createElement('div');t.className='page-thumb'+(i===state.currentPage?' active':'');t.dataset.page=i;const txt=(p.title||('未命名 '+(i+1))).slice(0,14);t.innerHTML='<span>'+escapeHtml(txt).replace(/[\r\n]/g,'<br>')+'</span>';t.addEventListener('click',()=>{state.currentPage=i;refreshPage();renderPages();});pagesBar.appendChild(t);});pagesBar.appendChild(add);}
  function updateThumb(){const t=pagesBar.querySelector('.page-thumb[data-page="'+state.currentPage+'"]');if(t){const tx=state.pages[state.currentPage].title||'未命名';t.innerHTML='<span>'+escapeHtml(tx.slice(0,14)).replace(/[\r\n]/g,'<br>')+'</span>';}}
  function refreshPage(){const p=state.pages[state.currentPage];titleInput.value=p.title;editorArea.innerHTML=p.html||'';prevTitle.textContent=p.title||'HighMD：把想法装进卡片，让表达更精炼';prevBody.innerHTML=p.html||'';prevTitle.style.display=state.showTitle?'':'none';}
  $('#addPage').addEventListener('click',()=>{state.pages.push({title:'新页面 '+(state.pages.length+1),html:''});state.currentPage=state.pages.length-1;refreshPage();renderPages();toast.show('已添加新页面');});
  $$('.import-card').forEach(c=>c.addEventListener('click',()=>{if(c.dataset.import==='local'){$('#fileInput').click();}}));
  $$('.nav-btn').forEach(b=>b.addEventListener('click',()=>{const t=b.textContent.trim();if(t.indexOf('导出')>-1){exportPNG();setTimeout(()=>toast.show('已生成卡片 PNG'),100);}else{toast.show('功能：'+t);}}));
  $$('.tb-action').forEach(a=>a.addEventListener('click',()=>{if(a.dataset.act==='layout'){const lines=(editorArea.innerText||'').split(/\n+/).filter(Boolean);if(lines.length>1){editorArea.innerHTML=lines.map(l=>l.length>30?'<h2>'+escapeHtml(l)+'</h2><p>':'<p>'+escapeHtml(l)+'</p>').join('');editorArea.dispatchEvent(new Event('input'));toast.show('已应用智能排版');}else{toast.show('正文较短，无需排版');}}}));
  function exportPNG() {
    const node = $('#previewFrame');
    const w = node.offsetWidth, h = node.offsetHeight, scale = 2;

    if (useHtml2canvas.value) {
      // html2canvas 路径：完整渲染富文本、嵌入图片、背景图片
      const stage = node.querySelector('.preview-stage');
      const bgColor = getComputedStyle(document.body).backgroundColor;
      html2canvas(stage, { backgroundColor: bgColor, scale: 2 }).then(canvas => {
        canvas.toBlob(blob => {
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.download = 'HighMD-' + Date.now() + '.png';
          link.href = url;
          link.click();
          // 打开图片预览
          window.open(url, '_blank');
          toast.show('已导出卡片 PNG');
          // 延迟释放 blob URL
          setTimeout(() => URL.revokeObjectURL(url), 5000);
        }, 'image/png');
      }).catch(err => {
        toast.show('导出失败，请重试');
        logger.error('html2canvas error:', err);
      });
      return;
    }

    // 手动绘制路径（原有逻辑）
    const canvas = document.createElement('canvas');
    canvas.width = w * scale;
    canvas.height = h * scale;
    const ctx = canvas.getContext('2d');
    ctx.scale(scale, scale);
    const stage = node.querySelector('.preview-stage');
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
  function wrapText(ctx,text,maxWidth){const out=[];(text||'').split(/\n/).forEach(line=>{if(!line.trim()){out.push('');return;}let cur='';for(const ch of line){if(ctx.measureText(cur+ch).width>maxWidth&&cur){out.push(cur);cur=ch;}else{cur+=ch;}}if(cur)out.push(cur);});return out;}
  let toastTimer;function showToast(msg){clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.show(msg),0);}
  renderPages();prevTitle.textContent=state.pages[0].title;prevBadge.textContent='HighMD · 灵感笔记';

  // 恢复工作区状态
  try {
    const saved = ws.restore();
    if (saved && saved.pages && saved.pages.length) {
      state.pages = saved.pages.map(p => ({ title: p.title || '', html: p.html || '' }));
      state.currentPage = Math.min(saved.currentPage || 0, state.pages.length - 1);
      state.showTitle = saved.showTitle !== false;
      state.autoPage = saved.autoPage !== false;
      state.ratio = saved.ratio || '3-5';
      state.currentTpl = saved.currentTpl || 'tpl-default';
      state.tplName = saved.tplName || '简单格子';
      refreshPage();
      renderPages();
      // 恢复模板选中状态
      previewStage.className = 'preview-stage ' + state.currentTpl;
      tplNameEl.textContent = state.tplName;
      // 恢复比例按钮
      $$('.ratio-btn').forEach(b => b.classList.toggle('active', b.dataset.ratio === state.ratio));
      previewFrame.className = 'preview-frame r-' + state.ratio;
    }
  } catch (_) {}

  // 自动保存：每 10 秒保存一次
  const autoSaveTimer = setInterval(() => {
    try {
      state.pages[state.currentPage].html = editorArea.innerHTML;
      state.pages[state.currentPage].title = titleInput.value;
      ws.save({
        pages: state.pages.map(p => ({ title: p.title, html: p.html })),
        currentPage: state.currentPage,
        showTitle: state.showTitle,
        autoPage: state.autoPage,
        ratio: state.ratio,
        currentTpl: state.currentTpl,
        tplName: state.tplName
      });
    } catch (_) {}
  }, 10000);

  // 暴露 timer 以便清理
  container._autoSaveTimer = autoSaveTimer;

});

onBeforeUnmount(() => {
  const container = editorContainer.value;
  // 保存状态
  try {
    state.pages[state.currentPage].html = $('#editorArea').innerHTML;
    state.pages[state.currentPage].title = $('#titleInput').value;
    ws.save({
      pages: state.pages.map(p => ({ title: p.title, html: p.html })),
      currentPage: state.currentPage,
      showTitle: state.showTitle,
      autoPage: state.autoPage,
      ratio: state.ratio,
      currentTpl: state.currentTpl,
      tplName: state.tplName
    });
  } catch (_) {}
  // 清理 timer
  if (container && container._autoSaveTimer) {
    clearInterval(container._autoSaveTimer);
  }
  if (container) {
    const clone = container.cloneNode(false);
    container.parentNode?.replaceChild(clone, container);
  }
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
