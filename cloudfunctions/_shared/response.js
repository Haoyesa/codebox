// @created 2026-06-16 v0.1 - 统一云函数响应包装
'use strict';

function ok(data) {
  return { code: 0, message: 'ok', data };
}

function fail(code, message) {
  return { code, message, data: null };
}

// 云函数既可能直接 return 对象,也可能返回 { code, message, data }。
// 客户端调用 wx.cloud.callFunction 后拿到的是云函数 return 的对象本身;
// 旧代码可能直接抛错,这里统一归一化。
function normalize(raw) {
  if (raw == null) {
    return fail('INTERNAL', 'empty response');
  }
  if (typeof raw === 'object' && 'code' in raw && 'message' in raw) {
    return raw;
  }
  if (typeof raw === 'string') {
    return fail('INTERNAL', raw);
  }
  return fail('INTERNAL', 'unexpected response');
}

module.exports = { ok, fail, normalize };