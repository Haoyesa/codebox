jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
  OPENID: 'test_openid',
  database: () => ({
    collection: () => ({
      where: () => ({ get: async () => ({ data: [] }) }),
      get: async () => ({ data: [] }),
    }),
  }),
}));

const { main } = require('../../cloudfunctions/listPromptTemplates');

describe('listPromptTemplates', () => {
  test('returns empty list when no templates', async () => {
    const r = await main({ adminToken: 'x' }, {});
    expect(r.code).toBe(0);
    expect(r.data.list).toEqual([]);
  });
});