import { constants as fsConstants } from 'node:fs'
import { access, mkdir } from 'node:fs/promises'
import path from 'node:path'

const FILENAME_LIMIT = 120

export async function pathExists(targetPath) {
  try {
    await access(targetPath, fsConstants.F_OK)
    return true
  } catch {
    return false
  }
}

export async function ensureDirectory(targetPath) {
  await mkdir(targetPath, { recursive: true })
}

export function sanitizeFileName(input, fallback = 'feishu-doc') {
  const cleaned = String(input ?? '')
    .normalize('NFKC')
    .replace(/[\u200B-\u200F\u202A-\u202E\u2060-\u206F\uFEFF]/g, '')
    .replace(/[<>:"/\\|?*\u0000-\u001F]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/[. ]+$/g, '')

  return (cleaned || fallback).slice(0, FILENAME_LIMIT)
}

export function resolveDocumentBaseName({ title, url }) {
  const normalizedTitle = String(title ?? '').replace(
    /\s*-\s*(Feishu Docs|飞书云文档)\s*$/i,
    '',
  )
  const titleCandidate = sanitizeFileName(normalizedTitle)

  if (titleCandidate && titleCandidate !== 'feishu-doc') {
    return titleCandidate
  }

  try {
    const parsed = new URL(url)
    const fallback = parsed.pathname.split('/').filter(Boolean).at(-1)
    return sanitizeFileName(fallback, 'feishu-doc')
  } catch {
    return 'feishu-doc'
  }
}

export async function uniqueMarkdownPath(outputDir, baseName) {
  await ensureDirectory(outputDir)

  const safeBaseName = sanitizeFileName(baseName)
  let suffix = 0

  while (true) {
    const fileName =
      suffix === 0 ? `${safeBaseName}.md` : `${safeBaseName}-${suffix}.md`
    const candidate = path.join(outputDir, fileName)

    if (!(await pathExists(candidate))) {
      return candidate
    }

    suffix++
  }
}
