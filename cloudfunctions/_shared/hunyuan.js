// @created 2026-06-16 v0.1 - 混元大模型统一 adapter
// mock 模式:返回硬编码样例数据,供本地开发
// live 模式:调用腾讯云混元 SDK(待补,需安装 tencentcloud-sdk-nodejs)
'use strict';

const { HUNYUAN_MODE, HUNYUAN_SECRET_ID, HUNYUAN_SECRET_KEY, HUNYUAN_REGION } = require('./config');

class HunyuanError extends Error {
  constructor(message, code) {
    super(message);
    this.code = code || 'HUNYUAN_ERROR';
  }
}

// ---------- Mock 实现 ----------

const MOCK_RESUME = {
  name: '张三',
  phone: '138****0001',
  email: 'zhangsan@example.com',
  education: [
    { school: '清华大学', major: '计算机科学与技术', degree: '本科', startDate: '2018-09', endDate: '2022-06' }
  ],
  work: [
    { company: '字节跳动', title: '前端工程师', startDate: '2022-07', endDate: '至今',
      description: '负责抖音 Web 端性能优化,核心页面 FCP 从 2.1s 降至 1.3s;主导微前端框架落地,接入 12 个子应用。' }
  ],
  projects: [
    { name: '电商运营中后台', role: '前端负责人', period: '2023-03 ~ 2023-12',
      description: '基于 qiankun 微前端方案重构,12 个子应用独立部署,首屏从 3.2s 降至 1.2s。' }
  ],
  skills: ['JavaScript', 'TypeScript', 'React', 'Vue', 'Webpack', 'Node.js']
};

class MockAdapter {
  async parseResume({ fileBuffer, mimeType, filename }) {
    await this._delay();
    return { data: JSON.parse(JSON.stringify(MOCK_RESUME)) };
  }

  async optimizeResume({ structuredResume, identity, industry, level, job, promptTemplate }) {
    await this._delay();
    const optimized = JSON.parse(JSON.stringify(structuredResume));
    // mock 改动:把第一条工作经历的描述改写得更"STAR"
    if (optimized.work && optimized.work[0]) {
      optimized.work[0].description = `[优化版] 在抖音 Web 端性能优化项目中,针对 FCP 2.1s 的痛点(S),主导核心链路重构(T),通过路由级 code-splitting + 预加载策略(A),将 FCP 降至 1.3s,业务转化率提升 8%(R)。面向 ${job || '目标岗位'} 调整关键词。`;
    }
    return {
      optimized,
      score: { match: 82, completeness: 88, professional: 85, quantified: 78, total: 83 },
      suggestions: [
        '第一条工作经历建议补充团队规模与协作模式',
        '项目经历缺少技术选型理由,建议在描述中加入 1-2 句架构权衡',
        '技能列表可按"熟练/了解"分级,提升招聘方筛选效率'
      ]
    };
  }

  _delay() {
    const ms = 800 + Math.floor(Math.random() * 700);
    return new Promise(r => setTimeout(r, ms));
  }
}

// ---------- Live 实现(占位) ----------
// 真实接入时:
//   1) cd cloudfunctions/_shared && npm init -y && npm i tencentcloud-sdk-nodejs
//   2) 取消下面注释,实现 _liveParse / _liveOptimize
//   3) 失败重试 1 次;超时 20s

class LiveAdapter {
  constructor({ secretId, secretKey, region }) {
    this.secretId = secretId;
    this.secretKey = secretKey;
    this.region = region;
  }

  async parseResume(args) {
    throw new HunyuanError('live mode not yet implemented — see comments in hunyuan.js', 'NOT_IMPLEMENTED');
  }

  async optimizeResume(args) {
    throw new HunyuanError('live mode not yet implemented — see comments in hunyuan.js', 'NOT_IMPLEMENTED');
  }
}

// ---------- 工厂 ----------

let _cached = null;

function getHunyuan() {
  if (_cached) return _cached;
  if (HUNYUAN_MODE === 'live') {
    if (!HUNYUAN_SECRET_ID || !HUNYUAN_SECRET_KEY) {
      throw new HunyuanError('HUNYUAN_MODE=live but credentials missing', 'CONFIG_ERROR');
    }
    _cached = new LiveAdapter({ secretId: HUNYUAN_SECRET_ID, secretKey: HUNYUAN_SECRET_KEY, region: HUNYUAN_REGION });
  } else {
    _cached = new MockAdapter();
  }
  return _cached;
}

// 测试时可重置
function _resetForTest() { _cached = null; }

module.exports = { getHunyuan, _resetForTest, HunyuanError, MockAdapter, LiveAdapter };