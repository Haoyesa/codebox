jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
  OPENID: 'test_openid',
  database: () => ({
    collection: () => {
      const col = {
        where: () => col,
        orderBy: () => col,
        skip: () => col,
        limit: () => ({ get: async () => ({ data: [{ _id: 'r1', data: { name: 'X' } }] }) }),
        get: async () => ({ data: [{ _id: 'r1', data: { name: 'X' } }] }),
        count: async () => ({ total: 1 }),
      };
      return col;
    },
  }),
}));

const { main } = require('../../cloudfunctions/listResumes');

describe('listResumes', () => {
  test('returns paginated list', async () => {
    const r = await main({ page: 1, pageSize: 10 }, {});
    expect(r.code).toBe(0);
    expect(r.data.list).toHaveLength(1);
    expect(r.data.total).toBe(1);
  });
});