// @created 2026-06-16 v0.1 - 新增/更新简历(含 raw + 可选 optimized)
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });
const { ok, fail } = require('../_shared/response');
const { checkOptimized } = require('../_shared/security');

exports.main = async (event, context) => {
  try {
    const { id, source, fileID = '', data, identity, targetIndustry, targetJob, targetLevel, optimized = null, score = null, suggestions = [] } = event;
    if (!source || !data) return fail('BAD_REQUEST', 'source / data 必填');

    if (optimized) {
      const safe = await checkOptimized(optimized);
      if (safe.risk === 'Risky') return fail('CONTENT_RISKY', '内容包含敏感信息');
    }

    const db = cloud.database();
    const now = Date.now();
    if (id) {
      await db.collection('resumes').doc(id).update({
        data: { source, fileID, data, identity, targetIndustry, targetJob, targetLevel, optimized, score, suggestions, updatedAt: now },
      });
      return ok({ resumeId: id });
    } else {
      const res = await db.collection('resumes').add({
        data: { _openid: cloud.OPENID, source, fileID, data, identity, targetIndustry, targetJob, targetLevel, optimized, score, suggestions, createdAt: now, updatedAt: now },
      });
      return ok({ resumeId: res._id });
    }
  } catch (err) {
    console.error('[saveResume]', err);
    return fail(err.code || 'INTERNAL', err.message);
  }
};