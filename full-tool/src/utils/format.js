/**
 * Pad number with leading zeros
 * @param {number} n
 * @param {number} width
 * @returns {string}
 */
export function pad(n, width = 2) {
  return String(n).padStart(width, '0');
}

/**
 * Format current time as HH:MM:SS
 * @returns {string}
 */
export function timeStr() {
  return new Date().toTimeString().slice(0, 8);
}

/**
 * Sanitize a string for use as filename
 * @param {string} s
 * @param {number} maxLen
 * @returns {string}
 */
export function sanitizeFilename(s, maxLen = 60) {
  return (s || '').replace(/[\\/:*?"<>|]/g, '_').slice(0, maxLen);
}

/**
 * Simple debounce helper
 * @param {Function} fn
 * @param {number} ms
 * @returns {Function}
 */
export function debounce(fn, ms = 300) {
  let t = null;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), ms);
  };
}

/**
 * Yield control back to the event loop
 * @returns {Promise<void>}
 */
export function yieldToMain() {
  return new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
}
