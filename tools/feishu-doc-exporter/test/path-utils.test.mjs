import assert from 'node:assert/strict'
import test from 'node:test'

import {
  resolveDocumentBaseName,
  sanitizeFileName,
} from '../src/path-utils.mjs'

test('sanitizeFileName removes invalid Windows characters', () => {
  assert.equal(
    sanitizeFileName('  a<b>c:d/e\\f|g?h*i  '),
    'a b c d e f g h i',
  )
})

test('sanitizeFileName removes zero-width characters', () => {
  assert.equal(
    sanitizeFileName('\u200B\u200E标题\u2060名字'),
    '标题名字',
  )
})

test('resolveDocumentBaseName prefers the title', () => {
  assert.equal(
    resolveDocumentBaseName({
      title: 'Feishu: Spec / Draft',
      url: 'https://my.feishu.cn/wiki/abc123',
    }),
    'Feishu Spec Draft',
  )
})

test('resolveDocumentBaseName strips the Feishu title suffix', () => {
  assert.equal(
    resolveDocumentBaseName({
      title: '增长方法论 - Feishu Docs',
      url: 'https://my.feishu.cn/wiki/abc123',
    }),
    '增长方法论',
  )
})

test('resolveDocumentBaseName falls back to the URL slug', () => {
  assert.equal(
    resolveDocumentBaseName({
      title: '',
      url: 'https://my.feishu.cn/wiki/abc123',
    }),
    'abc123',
  )
})
