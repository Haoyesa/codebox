jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
  OPENID: 'test_openid',
  database: () => ({}),
  downloadFile: async () => ({ fileContent: Buffer.from('mock pdf content') }),
}));

jest.mock('../../cloudfunctions/_shared/hunyuan', () => ({
  getHunyuan: () => ({
    parseResume: async () => ({ data: { name: 'Test', education: [], work: [], projects: [], skills: [] } }),
  }),
  HunyuanError: class extends Error {},
}));

const { main } = require('../../cloudfunctions/parseResume');

describe('parseResume', () => {
  test('returns parsed structured data', async () => {
    const r = await main({ fileID: 'cloud://mock' }, {});
    expect(r.code).toBe(0);
    expect(r.data.data.name).toBe('Test');
  });

  test('rejects when no fileID', async () => {
    const r = await main({}, {});
    expect(r.code).toBe('BAD_REQUEST');
  });
});