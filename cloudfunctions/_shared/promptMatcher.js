// @created 2026-06-16 v0.1 - 按 (type, identity, industry, level) 匹配最佳 Prompt 模板
'use strict';

function scoreMatch(t, q) {
  let s = 0;
  if (t.industry === q.industry) s += 2;
  else if (t.industry !== '*') return -1;
  if (t.level === q.level) s += 1;
  else if (t.level !== '*') return -1;
  if (t.identity === q.identity) s += 4;
  else if (t.identity !== '*') return -1;
  return s;
}

function findTemplate(templates, query) {
  const { type, identity, industry, level } = query;
  const candidates = templates.filter(t => t.type === type);
  let best = null;
  let bestScore = -1;
  for (const t of candidates) {
    const s = scoreMatch(t, { identity, industry, level });
    if (s > bestScore) {
      best = t;
      bestScore = s;
    }
  }
  return best;
}

module.exports = { findTemplate };