# Bilibili Subtitle Extractor

Download existing Bilibili subtitle tracks for a single video. This extractor checks the video metadata API, then the player subtitle API, then downloads the first subtitle JSON when a track is available.

## Usage

```powershell
python -m automation.extractors.bilibili_subtitle BV1VGQHBLEMn --check-only
python -m automation.extractors.bilibili_subtitle https://www.bilibili.com/video/BV1VGQHBLEMn/ --output-dir data/raw/bilibili/subtitles
```

## Login Cookie

Some videos only expose subtitle metadata to logged-in users. If needed, provide a local cookie without committing it:

```powershell
$env:BILIBILI_COOKIE = 'SESSDATA=...; bili_jct=...; DedeUserID=...'
python -m automation.extractors.bilibili_subtitle BV1VGQHBLEMn --check-only
```

Or use a local ignored file outside the repository or in `.env.local`-managed workflow:

```powershell
python -m automation.extractors.bilibili_subtitle BV1VGQHBLEMn --cookie-file C:\Users\YOU\.bilibili-cookie.txt
```

Do not place API keys, cookies, or account credentials in committed files.

## Outputs

When a subtitle is available, files are written to `data/raw/bilibili/subtitles/` by default:

- `<BV>-<lang>.raw.json`: original Bilibili subtitle payload.
- `<BV>-<lang>.txt`: readable text, one subtitle segment per line.
- `<BV>-<lang>.metadata.json`: video and subtitle metadata.

If no subtitle is available, the command exits with code `2` and prints a structured reason such as `no_subtitle_tracks` or `login_required_or_unavailable`.
