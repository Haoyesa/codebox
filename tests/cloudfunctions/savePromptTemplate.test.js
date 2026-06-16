jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
  OPENID: 'test_openid',
  database: () => ({
    collection: () => ({
      doc: (id) => ({
        get: async () => ({ data: { _id: id, version: 1 } }),
        update: async (data) => ({ _id: id, data }),
      }),
      add: async (data) => ({ _id: 'new_1', data }),
    }),
  }),
}));

const { main } = require('../../cloudfunctions/savePromptTemplate');

describe('savePromptTemplate', () => {
  test('updates existing template and bumps version', async () => {
    const r = await main({
      adminToken: 'x',
      id: 't1', type: 'optimize', identity: 'social', industry: 'internet', level: 'mid',
      template: 'new template', variables: ['x'],
    }, {});
    expect(r.code).toBe(0);
    expect(r.data.id).toBe('t1');
  });

  test('creates new template when no id', async () => {
    const r = await main({
      adminToken: 'x',
      type: 'optimize', identity: 'social', industry: '*', level: '*',
      template: 'abc', variables: [],
    }, {});
    expect(r.code).toBe(0);
    expect(r.data.id).toBe('new_1');
  });

  test('rejects missing required fields', async () => {
    const r = await main({ adminToken: 'x' }, {});
    expect(r.code).toBe('BAD_REQUEST');
  });
});