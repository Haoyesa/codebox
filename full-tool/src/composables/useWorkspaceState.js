/**
 * 工作区状态恢复 — 轻量级自动保存/恢复
 * 用法：在组件 onMounted 时 restore，onBeforeUnmount 时 save
 */

const PREFIX = 'fulltool_ws_';

export function useWorkspaceState(tabId) {
  const key = PREFIX + tabId;

  function save(stateObj) {
    try {
      localStorage.setItem(key, JSON.stringify({
        _t: Date.now(),
        data: stateObj
      }));
    } catch (_) {}
  }

  function restore() {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      return parsed.data || null;
    } catch (_) { return null; }
  }

  function clear() {
    try { localStorage.removeItem(key); } catch (_) {}
  }

  return { save, restore, clear };
}
