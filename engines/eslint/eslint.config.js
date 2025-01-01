import stylisticJs from '@stylistic/eslint-plugin-js';
import js from '@eslint/js';

const general_rules = {
    'curly': 'error',
    'comma-spacing': ['error', { 'before': false, 'after': true }],
    'prefer-arrow-callback': 'error',
    '@stylistic/js/quotes': ['error', 'single'],
    '@stylistic/js/linebreak-style': ['error', 'unix'],
    '@stylistic/js/semi': 'error',
    '@stylistic/js/indent': ['error', 'tab'],
    '@stylistic/js/brace-style': ['error', '1tbs'],
    '@stylistic/js/operator-linebreak': ['error', 'before'],
    '@stylistic/js/max-len': ['error', { code: 100, comments: 200 }],
    '@stylistic/js/no-trailing-spaces': 'error',
    '@stylistic/js/no-mixed-operators': 'error',
    '@stylistic/js/no-extra-parens': ['error', 'all', { 'nestedBinaryExpressions': false }],
    '@stylistic/js/comma-dangle': ['error', 'only-multiline'],
    '@stylistic/js/eol-last': 'error',
    '@stylistic/js/no-multiple-empty-lines': ['error', { 'max': 2, maxEOF: 0, maxBOF: 0 }],
    '@stylistic/js/spaced-comment': ['error', 'always'],
    '@stylistic/js/space-in-parens': ['error', 'never'],
    '@stylistic/js/block-spacing': ['error', 'always'],
    '@stylistic/js/function-call-spacing': ['error', 'never'],
    '@stylistic/js/space-before-function-paren': ['error', 'never'],
    '@stylistic/js/keyword-spacing': ['error', { 'before': true, 'after': true }],
    '@stylistic/js/no-extra-semi': 'error',
    '@stylistic/js/no-multi-spaces': 'error',
    '@stylistic/js/padded-blocks': ['error', 'never'],
}

// eslint.config.js
export default [
    {
        plugins: {
            '@stylistic/js': stylisticJs,
        },
        rules: {
            ...js.configs.recommended.rules,
            ...general_rules,
            // overwrites
            'prefer-arrow-callback': 'off',
            '@stylistic/js/brace-style': ['error', 'allman'],
            '@stylistic/js/spaced-comment': ['error', 'always', { line: {markers: ['!']}}],
        },
        languageOptions: {
            sourceType: 'script',
            ecmaVersion: 3,
            globals: {
                'dnsDomainIs': 'readonly',
                'shExpMatch': 'readonly',
                'isInNet': 'readonly',
                'isPlainHostName': 'readonly',
                'convert_addr': 'readonly',
                'myIpAddress': 'readonly',
            }
        }
    },
];
