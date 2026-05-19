#!/usr/bin/env node
import { chromium } from 'playwright'
import { writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { ensureExtensionCache } from './extension-cache.mjs'
import {
  ensureDirectory,
  pathExists,
  resolveDocumentBaseName,
  uniqueMarkdownPath,
} from './path-utils.mjs'
import { waitForCondition } from './wait-utils.mjs'

const scriptDir = path.dirname(fileURLToPath(import.meta.url))
const toolRoot = path.resolve(scriptDir, '..')
const repoRoot = path.resolve(toolRoot, '..', '..')

const defaultConverterRepo = path.resolve(repoRoot, 'temp/cloud-document-converter')
const defaultOutputDir = path.resolve(repoRoot, 'sources/dbs-feishu')
const defaultProfileDir = path.resolve(toolRoot, '.profile/chrome')
const defaultCacheDir = path.resolve(toolRoot, '.cache/extension')

function parseArgs(argv) {
  const args = argv.slice(2)
  const options = {
    url: '',
    outputDir: process.env.FEISHU_DOC_EXPORTER_OUTPUT_DIR ?? defaultOutputDir,
    converterRepo:
      process.env.FEISHU_DOC_EXPORTER_CONVERTER_REPO ?? defaultConverterRepo,
    profileDir: process.env.FEISHU_DOC_EXPORTER_PROFILE_DIR ?? defaultProfileDir,
    cacheDir: process.env.FEISHU_DOC_EXPORTER_CACHE_DIR ?? defaultCacheDir,
    chromePath: process.env.FEISHU_DOC_EXPORTER_CHROME ?? '',
    rebuildExtension: process.env.FEISHU_DOC_EXPORTER_REBUILD_EXTENSION === '1',
  }

  for (let i = 0; i < args.length; i++) {
    const arg = args[i]

    if (arg === '-h' || arg === '--help') {
      return { help: true }
    }

    if (arg.startsWith('--')) {
      const [flag, inlineValue] = arg.split('=', 2)
      let value = inlineValue

      if (value === undefined) {
        const next = args[i + 1]
        if (next && !next.startsWith('--')) {
          value = next
          i++
        } else {
          value = 'true'
        }
      }

      switch (flag) {
        case '--url':
          options.url = value
          break
        case '--output-dir':
          options.outputDir = value
          break
        case '--converter-repo':
          options.converterRepo = value
          break
        case '--profile-dir':
          options.profileDir = value
          break
        case '--cache-dir':
          options.cacheDir = value
          break
        case '--chrome-path':
          options.chromePath = value
          break
        case '--rebuild-extension':
          options.rebuildExtension = value !== 'false'
          break
        default:
          break
      }

      continue
    }

    if (!options.url) {
      options.url = arg
    }
  }

  return options
}

function printHelp() {
  console.log(
    [
      'Usage:',
      '  node tools/feishu-doc-exporter/src/export.mjs <feishu-url>',
      '',
      'Options:',
      '  --url <url>',
      '  --output-dir <dir>',
      '  --converter-repo <dir>',
      '  --profile-dir <dir>',
      '  --cache-dir <dir>',
      '  --chrome-path <exe>',
      '  --rebuild-extension',
    ].join('\n'),
  )
}

async function resolveChromeExecutable(chromePath) {
  const candidates = [
    chromePath,
    process.env.CHROME_PATH,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Users\\Administrator.DESKTOP-09JQGNK\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe',
  ].filter(Boolean)

  for (const candidate of candidates) {
    if (await pathExists(candidate)) {
      return candidate
    }
  }

  throw new Error(
    'Chrome was not found. Set FEISHU_DOC_EXPORTER_CHROME to the Chrome executable path.',
  )
}

async function readClipboardText(page) {
  for (let i = 0; i < 10; i++) {
    const text = await page.evaluate(async () => {
      try {
        return await navigator.clipboard.readText()
      } catch {
        return ''
      }
    })

    if (text.trim()) {
      return text
    }

    await page.waitForTimeout(250)
  }

  return ''
}

async function waitForDocumentReady(page) {
  await waitForCondition({
    check: async () =>
      await page.evaluate(() => {
        const pageMain = window.PageMain
        const root = pageMain?.blockManager?.rootBlockModel

        if (!root || !Array.isArray(root.children) || root.children.length === 0) {
          return false
        }

        return root.children.every(block => block?.snapshot?.type !== 'pending')
      }),
    initialDelayMs: 5_000,
    timeoutMs: 300_000,
    intervalMs: 1_000,
    onWaiting: () => {
      console.log(
        'Feishu is still loading document content. Waiting for the page to become ready...',
      )
    },
  })
}

async function readMarkdownFromPreviewWindow(context, triggerPreview) {
  const popupPromise = context.waitForEvent('page')
  await triggerPreview()
  const popup = await popupPromise

  await popup.waitForLoadState('domcontentloaded')
  await popup.waitForFunction(
    () =>
      document.title === 'Markdown Preview' &&
      (document.querySelector('pre')?.textContent?.trim()?.length ?? 0) > 0,
    undefined,
    { timeout: 30_000 },
  )

  const markdown = await popup.locator('pre').innerText()
  await popup.close().catch(() => {})

  return markdown
}

async function waitForManualLoginIfNeeded(copyButton) {
  await waitForCondition({
    check: async () => await copyButton.isVisible(),
    initialDelayMs: 15_000,
    timeoutMs: 300_000,
    intervalMs: 1_000,
    onWaiting: () => {
      console.log(
        'Chrome is open. If Feishu is not logged in yet, complete the login in the browser window. Export will continue automatically once the page is ready.',
      )
    },
  })
}

async function exportDocument(options) {
  const {
    url,
    outputDir,
    converterRepo,
    profileDir,
    cacheDir,
    chromePath,
    rebuildExtension,
  } = options

  if (!url) {
    throw new Error('Missing Feishu URL.')
  }

  const parsedUrl = new URL(url)
  const extensionDir = await ensureExtensionCache({
    converterRepo,
    cacheDir,
    rebuild: rebuildExtension,
    pnpmCommand: process.env.FEISHU_DOC_EXPORTER_PNPM ?? '',
  })
  await ensureDirectory(outputDir)
  await ensureDirectory(profileDir)

  const launchOptions = {
    headless: false,
    channel: chromePath ? undefined : 'chromium',
    args: [
      '--disable-popup-blocking',
      `--disable-extensions-except=${extensionDir}`,
      `--load-extension=${extensionDir}`,
    ],
  }

  if (chromePath) {
    launchOptions.executablePath = await resolveChromeExecutable(chromePath)
  }

  const context = await chromium.launchPersistentContext(
    profileDir,
    launchOptions,
  )

  try {
    await context.grantPermissions(['clipboard-read', 'clipboard-write'], {
      origin: parsedUrl.origin,
    })

    const page = await context.newPage()
    await page.goto(url, { waitUntil: 'domcontentloaded' })
    await page.bringToFront()
    await page.evaluate(() => window.focus())

    const copyButton = page.locator('[data-CDC-button-type="copy"]').first()
    const viewButton = page.locator('[data-CDC-button-type="view"]').first()
    await waitForManualLoginIfNeeded(copyButton)
    await waitForDocumentReady(page)

    await page.bringToFront()
    await page.evaluate(() => window.focus())
    let markdown = ''

    try {
      markdown = await readMarkdownFromPreviewWindow(context, async () => {
        await viewButton.click()
      })
    } catch {
      await copyButton.click()
      markdown = await readClipboardText(page)
    }

    if (!markdown.trim()) {
      throw new Error('Markdown export returned empty content.')
    }

    const title = await page.title()
    const baseName = resolveDocumentBaseName({ title, url })
    const filePath = await uniqueMarkdownPath(outputDir, baseName)

    await writeFile(
      filePath,
      markdown.endsWith('\n') ? markdown : `${markdown}\n`,
      'utf8',
    )

    console.log(`Saved Markdown to ${filePath}`)
  } finally {
    await context.close()
  }
}

async function main() {
  const args = parseArgs(process.argv)

  if (args.help) {
    printHelp()
    return
  }

  await exportDocument(args)
}

main().catch(error => {
  console.error(error instanceof Error ? error.message : String(error))
  process.exitCode = 1
})
