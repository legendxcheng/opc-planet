import assert from 'node:assert/strict'
import test from 'node:test'

import { resolvePnpmRunner } from '../src/package-manager.mjs'

test('resolvePnpmRunner prefers pnpm when it is available', () => {
  assert.deepEqual(
    resolvePnpmRunner({
      hasPnpm: true,
      hasCorepack: true,
    }),
    {
      command: 'pnpm',
      argsPrefix: [],
    },
  )
})

test('resolvePnpmRunner falls back to corepack pnpm when pnpm is unavailable', () => {
  assert.deepEqual(
    resolvePnpmRunner({
      hasPnpm: false,
      hasCorepack: true,
    }),
    {
      command: 'corepack',
      argsPrefix: ['pnpm'],
    },
  )
})

test('resolvePnpmRunner throws when neither pnpm nor corepack exists', () => {
  assert.throws(
    () =>
      resolvePnpmRunner({
        hasPnpm: false,
        hasCorepack: false,
      }),
    /Neither pnpm nor corepack is available/,
  )
})
