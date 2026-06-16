jest.mock('wx-server-sdk', () => {
  const data = { industries: [
    { _id: 'i1', code: 'internet', name: '互联网', jobs: [], companies: [], sort: 1 },
    { _id: 'i2', code: 'finance', name: '金融', jobs: [], companies: [], sort: 2 },
  ]};
  return {
    init: () => {},
    DYNAMIC_CURRENT_ENV: 'test-env',
    OPENID: 'test_openid',
    database: () => ({
      collection: (name) => ({
        where: () => ({ orderBy: () => ({ get: async () => ({ data: data[name] }) }) }),
        orderBy: () => ({ get: async () => ({ data: data[name] }) }),
        get: async () => ({ data: data[name] }),
      }),
    }),
  };
});

const { main } = require('../../cloudfunctions/listIndustries');

describe('listIndustries', () => {
  test('returns industries sorted by sort asc', async () => {
    const result = await main({}, {});
    expect(result.code).toBe(0);
    expect(result.data.list).toHaveLength(2);
    expect(result.data.list[0].code).toBe('internet');
  });
});