"""Download existing Bilibili subtitle tracks for one video.

Credentials are intentionally not stored by this module. Provide cookies through
BILIBILI_COOKIE or a local file path when running the CLI.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib import request

BVID_RE = re.compile(r"BV[0-9A-Za-z]{10}")
DEFAULT_OUTPUT_DIR = Path("data/raw/bilibili/subtitles")


@dataclass
class SubtitleInfo:
    bvid: str
    cid: int | None
    title: str | None
    owner_name: str | None
    status: str
    reason: str | None = None
    need_login_subtitle: bool | None = None
    subtitles: list[dict[str, Any]] | None = None


@dataclass
class DownloadResult:
    bvid: str
    cid: int | None
    title: str | None
    owner_name: str | None
    status: str
    reason: str | None = None
    subtitle: dict[str, Any] | None = None
    raw_subtitle_path: str | None = None
    text_path: str | None = None
    metadata_path: str | None = None


class HttpClient:
    def __init__(self, cookie: str | None = None) -> None:
        self.cookie = cookie

    def get_json(self, url: str) -> dict[str, Any]:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.bilibili.com/",
        }
        if self.cookie:
            headers["Cookie"] = self.cookie
        req = request.Request(url, headers=headers)
        with request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))


def extract_bvid(value: str) -> str:
    match = BVID_RE.search(value.strip())
    if not match:
        raise ValueError(f"No BV id found in: {value!r}")
    return match.group(0)


def view_api_url(bvid: str) -> str:
    return f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"


def player_api_url(bvid: str, cid: int) -> str:
    return f"https://api.bilibili.com/x/player/v2?bvid={bvid}&cid={cid}"


def normalize_subtitle_url(url: str) -> str:
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://"):
        return "https://" + url[len("http://") :]
    return url


def _require_ok(payload: dict[str, Any], context: str) -> None:
    if payload.get("code") != 0:
        raise RuntimeError(f"Bilibili {context} API failed: {payload.get('code')} {payload.get('message')}")


def fetch_subtitle_info(value: str, client: Any | None = None) -> SubtitleInfo:
    bvid = extract_bvid(value)
    http = client or HttpClient(cookie=load_cookie())
    view_payload = http.get_json(view_api_url(bvid))
    _require_ok(view_payload, "view")
    view_data = view_payload.get("data") or {}
    cid = view_data.get("cid")
    if cid is None:
        raise RuntimeError(f"Bilibili view API did not return cid for {bvid}")

    player_payload = http.get_json(player_api_url(bvid, int(cid)))
    _require_ok(player_payload, "player")
    player_data = player_payload.get("data") or {}
    subtitle_data = player_data.get("subtitle") or {}
    subtitles = subtitle_data.get("subtitles") or subtitle_data.get("list") or []
    need_login_subtitle = bool(player_data.get("need_login_subtitle"))

    if not subtitles:
        reason = "login_required_or_unavailable" if need_login_subtitle else "no_subtitle_tracks"
        return SubtitleInfo(
            bvid=bvid,
            cid=int(cid),
            title=view_data.get("title"),
            owner_name=(view_data.get("owner") or {}).get("name"),
            status="unavailable",
            reason=reason,
            need_login_subtitle=need_login_subtitle,
            subtitles=[],
        )

    return SubtitleInfo(
        bvid=bvid,
        cid=int(cid),
        title=view_data.get("title"),
        owner_name=(view_data.get("owner") or {}).get("name"),
        status="available",
        need_login_subtitle=need_login_subtitle,
        subtitles=subtitles,
    )


def download_first_subtitle(value: str, output_dir: str | Path = DEFAULT_OUTPUT_DIR, client: Any | None = None) -> DownloadResult:
    http = client or HttpClient(cookie=load_cookie())
    info = fetch_subtitle_info(value, client=http)
    if info.status != "available" or not info.subtitles:
        return DownloadResult(
            bvid=info.bvid,
            cid=info.cid,
            title=info.title,
            owner_name=info.owner_name,
            status=info.status,
            reason=info.reason,
        )

    subtitle = info.subtitles[0]
    subtitle_url = normalize_subtitle_url(str(subtitle.get("subtitle_url") or subtitle.get("url") or ""))
    if not subtitle_url:
        return DownloadResult(
            bvid=info.bvid,
            cid=info.cid,
            title=info.title,
            owner_name=info.owner_name,
            status="unavailable",
            reason="subtitle_url_missing",
            subtitle=subtitle,
        )

    subtitle_payload = http.get_json(subtitle_url)
    base_dir = Path(output_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    lan = sanitize_filename(str(subtitle.get("lan") or "unknown"))
    stem = f"{info.bvid}-{lan}"
    raw_path = base_dir / f"{stem}.raw.json"
    text_path = base_dir / f"{stem}.txt"
    metadata_path = base_dir / f"{stem}.metadata.json"

    raw_path.write_text(json.dumps(subtitle_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    text_path.write_text(subtitle_payload_to_text(subtitle_payload), encoding="utf-8")

    result = DownloadResult(
        bvid=info.bvid,
        cid=info.cid,
        title=info.title,
        owner_name=info.owner_name,
        status="downloaded",
        subtitle=subtitle,
        raw_subtitle_path=str(raw_path),
        text_path=str(text_path),
        metadata_path=str(metadata_path),
    )
    metadata_path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def subtitle_payload_to_text(payload: dict[str, Any]) -> str:
    lines = []
    for item in payload.get("body") or []:
        content = str(item.get("content") or "").strip()
        if content:
            lines.append(content)
    return "\n".join(lines) + ("\n" if lines else "")


def sanitize_filename(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z._-]+", "-", value).strip("-._")
    return value or "unknown"


def load_cookie(cookie_file: str | Path | None = None) -> str | None:
    env_cookie = os.environ.get("BILIBILI_COOKIE")
    if env_cookie:
        return env_cookie.strip()
    path_value = cookie_file or os.environ.get("BILIBILI_COOKIE_FILE")
    if not path_value:
        return None
    path = Path(path_value).expanduser()
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download existing Bilibili subtitle tracks for one BV video.")
    parser.add_argument("video", help="BV id or Bilibili video URL")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for raw/text/metadata outputs")
    parser.add_argument("--cookie-file", help="Local cookie file path; never commit this file")
    parser.add_argument("--check-only", action="store_true", help="Only check subtitle availability")
    args = parser.parse_args(argv)

    client = HttpClient(cookie=load_cookie(args.cookie_file))
    if args.check_only:
        info = fetch_subtitle_info(args.video, client=client)
        print(json.dumps(asdict(info), ensure_ascii=False, indent=2))
        return 0 if info.status == "available" else 2

    result = download_first_subtitle(args.video, output_dir=args.output_dir, client=client)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0 if result.status == "downloaded" else 2


if __name__ == "__main__":
    raise SystemExit(main())
