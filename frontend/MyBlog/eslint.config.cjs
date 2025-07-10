const pluginVue = require('eslint-plugin-vue');

// 简单的基础配置
module.exports = [
  // 全局忽略
  {
    ignores: ['**/dist/**', '**/dist-ssr/**', '**/coverage/**']
  },
  // JavaScript文件的基本规则
  {
    files: ['**/*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module'
    },
    rules: {
      'semi': 'error',
      'prefer-const': 'error'
    }
  },
  // Vue文件的配置
  {
    files: ['**/*.vue'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parser: require('vue-eslint-parser'),
      parserOptions: {
        parser: {
          js: require('espree')
        },
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    },
    plugins: {
      vue: pluginVue
    },
    rules: {
      ...pluginVue.configs.base.rules,
      'vue/comment-directive': 'off', // 禁用注释指令检查
      'semi': 'error',
      'prefer-const': 'error'
    }
  }
]