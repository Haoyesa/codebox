/**
 * Extract file extension from path (lowercase, no dot)
 * @param {string} filePath
 * @returns {string}
 */
export function getExt(filePath) {
  if (!filePath) return '';
  const base = filePath.split(/[\\/]/).pop() || '';
  const dot = base.lastIndexOf('.');
  return dot >= 0 ? base.slice(dot + 1).toLowerCase() : '';
}

/**
 * Get MIME type from file extension
 * @param {string} filePath
 * @returns {string}
 */
export function getMimeFromPath(filePath) {
  const ext = getExt(filePath);
  if (ext === 'jpg' || ext === 'jpeg') return 'image/jpeg';
  if (ext === 'png') return 'image/png';
  if (ext === 'webp') return 'image/webp';
  if (ext === 'gif') return 'image/gif';
  if (ext === 'svg') return 'image/svg+xml';
  if (ext === 'bmp') return 'image/bmp';
  if (ext === 'pdf') return 'application/pdf';
  return 'application/octet-stream';
}

/**
 * Get basename from file path
 * @param {string} filePath
 * @returns {string}
 */
export function getBasename(filePath) {
  if (!filePath) return '';
  return filePath.split(/[\\/]/).pop() || '';
}

/**
 * Format byte size to human-readable string
 * @param {number} bytes
 * @returns {string}
 */
export function formatSize(bytes) {
  if (!bytes) return '';
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Truncate a long path for display
 * @param {string} p
 * @param {number} maxLen
 * @returns {string}
 */
export function truncatePath(p, maxLen = 30) {
  if (!p) return '';
  if (p.length <= maxLen) return p;
  return '...' + p.slice(-(maxLen - 3));
}

/**
 * Normalize directory separator to forward slash
 * @param {string} p
 * @returns {string}
 */
export function normalizePath(p) {
  return String(p || '').replace(/\\/g, '/');
}

/**
 * Build safe output path (strip trailing separators)
 * @param {string} dir
 * @returns {string}
 */
export function safeOutputDir(dir) {
  return String(dir || '').replace(/[\\/]+$/, '');
}
