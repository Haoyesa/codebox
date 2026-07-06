/**
 * 统一日志工具，输出到 console 同时派发事件供日志面板收集。
 * 使用方式：import { logger } from '../composables/useLogger.js'
 */
export const logger = {
  info(msg, ...args) { console.log('[App]', msg, ...args); },
  warn(msg, ...args) { console.warn('[App]', msg, ...args); },
  error(msg, ...args) { console.error('[App]', msg, ...args); }
};

/**
 * 防抖：延迟执行，在最后一次调用后等待 delay 毫秒再触发
 * @param {Function} fn - 要防抖的函数
 * @param {number} delay - 延迟毫秒数，默认 200
 * @returns {Function} 防抖后的函数
 */
export function debounce(fn, delay = 200) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

/**
 * 节流：固定间隔执行，interval 毫秒内最多执行一次
 * @param {Function} fn - 要节流的函数
 * @param {number} interval - 间隔毫秒数，默认 100
 * @returns {Function} 节流后的函数
 */
export function throttle(fn, interval = 100) {
  let last = 0;
  return function(...args) {
    const now = Date.now();
    if (now - last >= interval) {
      last = now;
      fn.apply(this, args);
    }
  };
}
