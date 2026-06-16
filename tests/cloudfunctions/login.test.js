jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
  OPENID: 'oTEST_123',
  database: () => ({
    collection: () => ({
      where: () => ({ count: async () => ({ total: 0 }), get: async () => ({ data: [] }) }),
      add: async (data) => ({ _id: 'u1', data }),
    }),
  }),
}));

const { main } = require('../../cloudfunctions/login');

describe('login', () => {
  test('returns token + openid for new user', async () => {
    const r = await main({ code: 'mock_code' }, {});
    expect(r.code).toBe(0);
    expect(r.data.openid).toBe('oTEST_123');
    expect(r.data.token).toBe('oTEST_123');
    expect(r.data.isNewUser).toBe(true);
  });

  test('rejects when no code', async () => {
    const r = await main({}, {});
    expect(r.code).toBe('BAD_REQUEST');
  });
});