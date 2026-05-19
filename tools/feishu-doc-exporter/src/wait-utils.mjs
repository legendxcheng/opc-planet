function sleep(ms) {
  return new Promise(resolve => {
    setTimeout(resolve, ms)
  })
}

export async function waitForCondition({
  check,
  initialDelayMs = 15_000,
  timeoutMs = 300_000,
  intervalMs = 1_000,
  onWaiting = () => {},
}) {
  const startedAt = Date.now()
  let waitingAnnounced = false

  while (Date.now() - startedAt < timeoutMs) {
    if (await check()) {
      return
    }

    if (!waitingAnnounced && Date.now() - startedAt >= initialDelayMs) {
      waitingAnnounced = true
      onWaiting()
    }

    await sleep(intervalMs)
  }

  throw new Error(`Timed out after ${timeoutMs}ms while waiting for the page to become ready.`)
}
