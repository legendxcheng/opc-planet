---
name: extract-bilibili-transcripts
description: Extract transcript text from Bilibili videos using this repository's automation.extractors.bilibili_subtitle tool. Use when Codex needs to download existing Bilibili subtitle tracks as plain text from a BV video URL/id or from a creator space URL/mid, check subtitle availability, handle local Bilibili cookies safely, store raw subtitle outputs under data/raw/bilibili/subtitles, or prepare downloaded transcripts for sources/videos/bilibili.
---

# Extract Bilibili Transcripts

## Overview

Use the repository tool `automation.extractors.bilibili_subtitle` to download Bilibili subtitle text. It does not download video files, bypass access controls, or generate subtitles for videos that have no subtitle track.

Keep credentials out of the repository. Use a local cookie file such as `C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt` only when needed.

## Workflow

1. Confirm the user supplied either a BV video id/URL or a creator space URL/mid.
2. Prefer `--check-only` first for a single video when availability is uncertain.
3. Run the extractor from the repository root with `python -m automation.extractors.bilibili_subtitle`.
4. Write raw outputs under `data/raw/bilibili/subtitles/`, usually `data/raw/bilibili/subtitles/<mid>/` for creator batches.
5. Summarize download status from command output or the creator summary JSON.
6. If the user wants curated source notes, convert only downloaded `.txt` files into `sources/videos/bilibili/<creator-slug>/`; keep raw JSON in `data/raw/`.

## Single Video

Check whether subtitles are available:

```powershell
python -m automation.extractors.bilibili_subtitle BV1xxxxxxxxx `
  --check-only `
  --cookie-file C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt
```

Download transcript text:

```powershell
python -m automation.extractors.bilibili_subtitle BV1xxxxxxxxx `
  --cookie-file C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt `
  --output-dir data/raw/bilibili/subtitles/<target>
```

The successful output includes:

- `<BV>-<lang>.raw.json`: original Bilibili subtitle payload.
- `<BV>-<lang>.txt`: transcript text, one subtitle segment per line.
- `<BV>-<lang>.metadata.json`: video and subtitle metadata.

## Creator Batch

Use creator mode for an UP creator page or member id:

```powershell
python -m automation.extractors.bilibili_subtitle https://space.bilibili.com/<mid>/upload/video `
  --creator `
  --cookie-file C:\Users\Administrator.DESKTOP-09JQGNK\.codex\memories\bilibili_cookie.txt `
  --output-dir data/raw/bilibili/subtitles/<mid> `
  --summary-path data/raw/bilibili/subtitles/<mid>/creator-<mid>-summary.json `
  --page-size 30
```

Inspect the summary:

```powershell
$summary = Get-Content -Raw data/raw/bilibili/subtitles/<mid>/creator-<mid>-summary.json | ConvertFrom-Json
"total=$($summary.total) downloaded=$($summary.downloaded) unavailable=$($summary.unavailable) error=$($summary.error)"
$summary.results | Select-Object bvid,title,status,reason,text_path | Format-Table -AutoSize
```

## Status Handling

- `downloaded`: transcript text was written successfully.
- `no_subtitle_tracks`: the video exposes no subtitle track.
- `login_required_or_unavailable`: retry with a valid local cookie file if the video should be public and subtitled.
- `subtitle_url_missing`: Bilibili returned subtitle metadata without a downloadable URL.
- `error`: report the exception and preserve the summary for later retries.

## Repository Rules

- Do not put cookies, API keys, or account credentials in committed files.
- Do not treat `data/raw/` as canonical knowledge; it is source material.
- Put curated Bilibili source records in `sources/videos/bilibili/<creator-slug>/`.
- Put durable conclusions derived from transcripts in `knowledge/<domain>/`, with source links back to `sources/videos/bilibili/...`.
- Keep generated temporary conversion scripts in `temp/` unless they are promoted into `automation/`.
