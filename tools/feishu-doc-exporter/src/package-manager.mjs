import { spawnSync } from 'node:child_process'

export function resolvePnpmRunner({
  preferredCommand,
  hasPnpm,
  hasCorepack,
}) {
  if (preferredCommand) {
    return {
      command: preferredCommand,
      argsPrefix: [],
    }
  }

  if (hasPnpm) {
    return {
      command: 'pnpm',
      argsPrefix: [],
    }
  }

  if (hasCorepack) {
    return {
      command: 'corepack',
      argsPrefix: ['pnpm'],
    }
  }

  throw new Error(
    'Neither pnpm nor corepack is available. Install one of them or set FEISHU_DOC_EXPORTER_PNPM.',
  )
}

export function commandExists(command) {
  const resolver = process.platform === 'win32' ? 'where.exe' : 'which'
  const result = spawnSync(resolver, [command], {
    stdio: 'ignore',
    shell: process.platform === 'win32',
  })

  return result.status === 0
}
