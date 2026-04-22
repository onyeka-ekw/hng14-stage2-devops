module.exports = {
  env: {
    browser: true,
    commonjs: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
  ],
  parserOptions: {
    ecmaVersion: 12,
    sourceType: 'commonjs',
  },
  rules: {
    'no-unused-vars': 'error',
    'no-console': 'off',
    'prefer-const': 'error',
    'no-var': 'error',
  },
  globals: {
    'process': 'readonly',
    '__dirname': 'readonly',
  },
};
