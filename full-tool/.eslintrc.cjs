module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
    es2022: true
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended'
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  rules: {
    'no-var': 'error',
    'prefer-const': 'warn',
    'vue/multi-word-component-names': 'off',
    'vue/no-v-html': 'off',
    'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-console': 'off'
  },
  globals: {
    window: 'readonly',
    document: 'readonly',
    console: 'readonly',
    fetch: 'readonly',
    Blob: 'readonly',
    FileReader: 'readonly',
    URL: 'readonly',
    ResizeObserver: 'readonly',
    requestAnimationFrame: 'readonly'
  }
};
