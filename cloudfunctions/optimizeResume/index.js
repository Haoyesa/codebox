// @created 2026-06-16 v0.1 - 调混元优化简历 + 评分(不写库,只返回结果)
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');
const { getHunyuan } = require('../_shared/hunyuan');
const { findTemplate } = require('../_shared/promptMatcher');
const { checkOptimized } = require('../_shared/security');

exports.main = async (event, context) => {
  try {
    const { resumeId, identity, industry, job, level } = event;
    if (!resumeId || !identity) return fail('BAD_REQUEST', 'resumeId / identity 必填');

    // 1. 读原版简历
    const resumeRes = await cloud.database().collection('resumes').doc(resumeId).get();
    const structuredResume = resumeRes.data && resumeRes.data.data;
    if (!structuredResume) return fail('NOT_FOUND', '简历不存在');

    // 2. 找最佳 Prompt 模板
    const tplRes = await cloud.database().collection('prompt_templates').where({ type: 'optimize' }).get();
    const tpl = findTemplate(tplRes.data, { type: 'optimize', identity, industry, level });
    if (!tpl) return fail('NO_TEMPLATE', '未找到匹配的 Prompt 模板');

    // 3. 调混元
    const adapter = getHunyuan();
    const result = await adapter.optimizeResume({
      structuredResume, identity, industry, level, job, promptTemplate: tpl.template,
    });

    // 4. 内容安全过滤
    const safe = await checkOptimized(result.optimized);
    if (safe.risk === 'Risky') return fail('CONTENT_RISKY', '内容包含敏感信息');

    return ok({
      optimized: result.optimized,
      score: result.score,
      suggestions: result.suggestions,
    });
  } catch (err) {
    console.error('[optimizeResume]', err);
    return fail(err.code || 'INTERNAL', err.message);
  }
};