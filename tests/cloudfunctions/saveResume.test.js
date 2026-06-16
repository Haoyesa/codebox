jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
  OPENID: 'test_openid',
  database: () => ({
    collection: () => ({
      doc: (id) => ({
        update: async (data) => ({ _id: id, data }),
      }),
      add: async (data) => ({ _id: 'new_id_1', data }),
    }),
  }),
}));

jest.mock('../../cloudfunctions/_shared/security', () => ({
  checkOptimized: async () => ({ risk: 'Pass' }),
}));

const { main } = require('../../cloudfunctions/saveResume');

describe('saveResume', () => {
  test('creates new resume when no id', async () => {
    const r = await main({ source: 'manual', data: { name: 'X' } }, {});
    expect(r.code).toBe(0);
    expect(r.data.resumeId).toBe('new_id_1');
  });

  test('updates existing resume with optimized fields', async () => {
    const r = await main({
      id: 'r1', source: 'word', data: { name: 'X' },
      optimized: { name: 'X+' },
      score: { match: 80, completeness: 80, professional: 80, quantified: 80, total: 80 },
      suggestions: ['s1'],
    }, {});
    expect(r.code).toBe(0);
    expect(r.data.resumeId).toBe('r1');
  });

  test('rejects missing required fields', async () => {
    const r = await main({ data: { name: 'X' } }, {});
    expect(r.code).toBe('BAD_REQUEST');
  });
});