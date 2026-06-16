jest.mock('wx-server-sdk', () => {
  const calls = { update: [], add: [] };
  return {
    init: () => {},
    DYNAMIC_CURRENT_ENV: 'test-env',
    database: () => ({
      collection: () => ({
        doc: (id) => ({
          update: async (data) => { calls.update.push({ id, data }); return { _id: id }; },
        }),
        add: async (data) => { calls.add.push(data); return { _id: 'new_' + calls.add.length }; },
      }),
    }),
    __getCalls: () => calls,
  };
});

const { main } = require('../../cloudfunctions/saveIndustry');
const cloud = require('wx-server-sdk');

describe('saveIndustry (admin)', () => {
  test('updates existing industry', async () => {
    const r = await main({
      adminToken: 'ignored-in-test',
      id: 'i1', code: 'internet', name: '互联网', jobs: [], companies: [],
    }, {});
    expect(r.code).toBe(0);
    expect(cloud.__getCalls().update[0].id).toBe('i1');
  });

  test('creates new industry when no id', async () => {
    const r = await main({
      adminToken: 'ignored-in-test',
      code: 'new', name: '新行业', jobs: [], companies: [],
    }, {});
    expect(r.code).toBe(0);
    expect(cloud.__getCalls().add).toHaveLength(1);
  });

  test('rejects missing required fields', async () => {
    const r = await main({ adminToken: 'ignored-in-test' }, {});
    expect(r.code).toBe('BAD_REQUEST');
  });
});