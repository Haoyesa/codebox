// 模拟 wx-server-sdk 注入的 context
function mockContext({ openid } = {}) {
  return {
    OPENID: openid,
    userInfo: { openId: openid },
  };
}

jest.mock('../../../cloudfunctions/_shared/config', () => ({
  ADMIN_USERNAME: 'admin',
  ADMIN_PASSWORD: 'testpass',
  ADMIN_TOKEN_SECRET: 'test-secret-32-chars-1234567890abc',
  ADMIN_TOKEN_TTL: 7200,
}));

const { authUser, authAdmin, signAdminToken, verifyAdminToken } =
  require('../../../cloudfunctions/_shared/auth');

describe('authUser', () => {
  test('returns openid from context', () => {
    expect(authUser(mockContext({ openid: 'oABC' }))).toBe('oABC');
  });

  test('throws when no openid', () => {
    expect(() => authUser({})).toThrow(/openid/);
  });
});

describe('admin token', () => {
  test('signs and verifies a valid token', () => {
    const tok = signAdminToken('admin', Date.now() + 60000);
    expect(verifyAdminToken(tok).username).toBe('admin');
  });

  test('rejects tampered token', () => {
    const tok = signAdminToken('admin', Date.now() + 60000);
    const tampered = tok.slice(0, -3) + 'xxx';
    expect(() => verifyAdminToken(tampered)).toThrow(/signature/i);
  });

  test('rejects expired token', () => {
    const tok = signAdminToken('admin', Date.now() - 1000);
    expect(() => verifyAdminToken(tok)).toThrow(/expired/i);
  });
});

describe('authAdmin', () => {
  test('passes with valid token', () => {
    const tok = signAdminToken('admin', Date.now() + 60000);
    expect(authAdmin({ adminToken: tok }).username).toBe('admin');
  });

  test('throws without token', () => {
    expect(() => authAdmin({})).toThrow(/token/i);
  });
});