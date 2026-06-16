const { ok, fail, normalize } = require('../../../cloudfunctions/_shared/response');

describe('response helpers', () => {
  test('ok wraps data with code 0', () => {
    expect(ok({ a: 1 })).toEqual({ code: 0, message: 'ok', data: { a: 1 } });
  });

  test('fail with string code', () => {
    expect(fail('PARSE_FAIL', '简历解析失败')).toEqual({
      code: 'PARSE_FAIL', message: '简历解析失败', data: null
    });
  });

  test('normalize unwraps cloud function raw return', () => {
    expect(normalize(ok({ x: 1 }))).toEqual({ code: 0, message: 'ok', data: { x: 1 } });
    expect(normalize({ code: 'X', message: 'err', data: null })).toEqual({ code: 'X', message: 'err', data: null });
    expect(normalize(null)).toEqual({ code: 'INTERNAL', message: 'empty response', data: null });
    expect(normalize('plain string')).toEqual({ code: 'INTERNAL', message: 'plain string', data: null });
  });
});
