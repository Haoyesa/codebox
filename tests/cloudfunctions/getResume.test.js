jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
  OPENID: 'test_openid',
  database: () => ({
    collection: () => ({
      doc: () => ({ get: async () => ({ data: { _id: 'r1', data: { name: 'X' } } }) }),
    }),
  }),
}));

const { main } = require('../../cloudfunctions/getResume');

describe('getResume', () => {
  test('returns resume by id', async () => {
    const r = await main({ id: 'r1' }, {});
    expect(r.code).toBe(0);
    expect(r.data.resume.data.name).toBe('X');
  });

  test('rejects missing id', async () => {
    const r = await main({}, {});
    expect(r.code).toBe('BAD_REQUEST');
  });
});