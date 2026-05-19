import { spawn } from 'node:child_process'
import { cp, mkdir, rm } from 'node:fs/promises'
import path from 'node:path'

import { commandExists, resolvePnpmRunner } from './package-manager.mjs'
import { pathExists } from './path-utils.mjs'

function run(command, args, cwd) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd,
      stdio: 'inherit',
      shell: process.platform === 'win32',
    })

    child.once('error', reject)
    child.once('exit', (code, signal) => {
      if (code === 0) {
        resolve()
        return
      }

      reject(
        new Error(
          `Command failed: ${command} ${args.join(' ')}${signal ? ` (signal ${signal})` : ''}${code !== null ? ` (exit ${code})` : ''}`,
        ),
      )
    })
  })
}

export async function ensureExtensionCache({
  converterRepo,
  cacheDir,
  rebuild = false,
  pnpmCommand = '',
}) {
  const builtExtensionDir = path.join(
    converterRepo,
    'apps/chrome-extension/dist',
  )
  const cachedManifest = path.join(cacheDir, 'manifest.json')

  if (!rebuild && (await pathExists(cachedManifest))) {
    return cacheDir
  }

  if (!(await pathExists(converterRepo))) {
    throw new Error(
      `Converter repository not found: ${converterRepo}. Set FEISHU_DOC_EXPORTER_CONVERTER_REPO to a valid cloud-document-converter checkout.`,
    )
  }

  const pnpmRunner = resolvePnpmRunner({
    preferredCommand: pnpmCommand,
    hasPnpm: commandExists('pnpm'),
    hasCorepack: commandExists('corepack'),
  })

  if (!(await pathExists(path.join(converterRepo, 'node_modules')))) {
    await run(
      pnpmRunner.command,
      [...pnpmRunner.argsPrefix, 'install'],
      converterRepo,
    )
  }

  await run(
    pnpmRunner.command,
    [...pnpmRunner.argsPrefix, '--filter', '@dolphin/chrome-extension', 'build'],
    converterRepo,
  )

  await rm(cacheDir, { recursive: true, force: true })
  await mkdir(cacheDir, { recursive: true })
  await cp(builtExtensionDir, cacheDir, { recursive: true })

  return cacheDir
}
