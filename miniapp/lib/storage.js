// @created 2026-06-16 v0.1 - 本地存储封装
function set(key, val) {
  try { wx.setStorageSync(key, val); } catch (e) { console.error('storage.set', key, e); }
}
function get(key, def) {
  if (def === undefined) def = null;
  try { const v = wx.getStorageSync(key); return v === '' ? def : v; } catch (e) { return def; }
}
function remove(key) { try { wx.removeStorageSync(key); } catch (e) {} }

module.exports = { set, get, remove };