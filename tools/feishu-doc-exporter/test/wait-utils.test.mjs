import assert from 'node:assert/strict'
import test from 'node:test'

import { waitForCondition } from '../src/wait-utils.mjs'

test('waitForCondition keeps polling after the initial delay without terminal input', async () => {
  let checks = 0
  let waitingNotices = 0

  await waitForCondition({
    check: async () => {
      checks++
      return checks >= 4
    },
    initialDelayMs: 20,
    timeoutMs: 200,
    intervalMs: 10,
    onWaiting: () => {
      waitingNotices++
    },
  })

  assert.ok(checks >= 4)
  assert.equal(waitingNotices, 1)
})

test('waitForCondition throws after the full timeout', async () => {
  await assert.rejects(
    () =>
      waitForCondition({
        check: async () => false,
        initialDelayMs: 10,
        timeoutMs: 50,
        intervalMs: 10,
      }),
    /Timed out/,
  )
})
