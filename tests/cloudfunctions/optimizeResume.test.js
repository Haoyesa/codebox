jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
  OPENID: 'test_openid',
  database: () => ({
    collection: () => ({
      where: () => ({ get: async () => ({ data: [
        { type: 'optimize', identity: 'social', industry: '*', level: '*', template: 'TPL' }
      ] }) }),
      doc: () => ({ get: async () => ({ data: { data: { name: 'X' } } }) }),
    }),
  }),
}));

jest.mock('../../cloudfunctions/_shared/hunyuan', () => ({
  getHunyuan: () => ({
    optimizeResume: async ({ promptTemplate }) => ({
      optimized: { name: 'X' },
      score: { match: 80, completeness: 80, professional: 80, quantified: 80, total: 80 },
      suggestions: ['s1'],
      _usedTemplate: promptTemplate,
    }),
  }),
  HunyuanError: class extends Error {},
}));

const { main } = require('../../cloudfunctions/optimizeResume');

describe('optimizeResume', () => {
  test('returns optimized + score', async () => {
    const r = await main({ resumeId: 'r1', identity: 'social', industry: 'internet', job: 'frontend', level: 'mid' }, {});
    expect(r.code).toBe(0);
    expect(r.data.optimized.name).toBe('X');
    expect(r.data.score.total).toBe(80);
  });
});