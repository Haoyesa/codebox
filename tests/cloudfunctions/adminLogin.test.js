jest.mock('wx-server-sdk', () => ({
  init: () => {},
  DYNAMIC_CURRENT_ENV: 'test-env',
}));

jest.mock('../../cloudfunctions/_shared/config', () => ({
  ADMIN_USERNAME: 'admin',
  ADMIN_PASSWORD: 'testpass',
  ADMIN_TOKEN_SECRET: 'test-secret-32-chars-1234567890abc',
  ADMIN_TOKEN_TTL: 7200,
}));

const { main } = require('../../cloudfunctions/adminLogin');
const { verifyAdminToken } = require('../../cloudfunctions/_shared/auth');

describe('adminLogin', () => {
  test('returns token + exp for correct credentials', async () => {
    const r = await main({ username: 'admin', password: 'testpass' });
    expect(r.code).toBe(0);
    expect(typeof r.data.token).toBe('string');
    expect(r.data.token.length).toBeGreaterThan(0);
    expect(typeof r.data.exp).toBe('number');
    expect(r.data.exp).toBeGreaterThan(Date.now());
    expect(verifyAdminToken(r.data.token).username).toBe('admin');
  });

  test('rejects wrong password', async () => {
    const r = await main({ username: 'admin', password: 'wrong' });
    expect(r.code).toBe('AUTH_FAIL');
  });

  test('rejects wrong username', async () => {
    const r = await main({ username: 'hacker', password: 'testpass' });
    expect(r.code).toBe('AUTH_FAIL');
  });

  test('rejects missing username', async () => {
    const r = await main({ password: 'testpass' });
    expect(r.code).toBe('AUTH_FAIL');
  });

  test('rejects missing password', async () => {
    const r = await main({ username: 'admin' });
    expect(r.code).toBe('AUTH_FAIL');
  });
});