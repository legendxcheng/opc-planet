"""Download existing Bilibili subtitle tracks for one video.

Credentials are intentionally not stored by this module. Provide cookies through
BILIBILI_COOKIE or a local file path when running the CLI.
"""

from __future__ import annotations

import argparse
import hashlib
import time
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib import request
from urllib.parse import urlencode, urlsplit, urlunsplit

BVID_RE = re.compile(r"BV[0-9A-Za-z]{10}")
MID_RE = re.compile(r"space\.bilibili\.com/(\d+)|^(\d+)$")
DEFAULT_OUTPUT_DIR = Path("data/raw/bilibili/subtitles")
DEFAULT_PAGE_SIZE = 30
WBI_MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]


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

def extract_mid(value: str) -> str:
    match = MID_RE.search(value.strip())
    if not match:
        raise ValueError(f"No Bilibili member id found in: {value!r}")
    return match.group(1) or match.group(2)

def view_api_url(bvid: str) -> str:
    return f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
def nav_api_url() -> str:
    return "https://api.bilibili.com/x/web-interface/nav"


def extract_wbi_key(url: str) -> str:
    path = urlsplit(url).path
    filename = path.rsplit("/", 1)[-1]
    return filename.split(".", 1)[0]


def wbi_mixin_key(img_key: str, sub_key: str) -> str:
    raw_key = img_key + sub_key
    return "".join(raw_key[index] for index in WBI_MIXIN_KEY_ENC_TAB)[:32]


def wbi_signed_url(
    base_url: str,
    params: dict[str, Any],
    img_key: str,
    sub_key: str,
    timestamp: int | None = None,
) -> str:
    signed_params = {key: value for key, value in params.items() if value is not None}
    signed_params["wts"] = int(timestamp if timestamp is not None else time.time())
    mixin_key = wbi_mixin_key(img_key, sub_key)
    query = urlencode(sorted(signed_params.items()))
    signed_params["w_rid"] = hashlib.md5((query + mixin_key).encode("utf-8")).hexdigest()
    return base_url + "?" + urlencode(sorted(signed_params.items()))


def fetch_wbi_keys(client: Any) -> tuple[str, str]:
    payload = client.get_json(nav_api_url())
    _require_ok(payload, "nav")
    wbi_img = ((payload.get("data") or {}).get("wbi_img") or {})
    img_url = wbi_img.get("img_url")
    sub_url = wbi_img.get("sub_url")
    if not img_url or not sub_url:
        raise RuntimeError("Bilibili nav API did not return WBI image keys")
    return extract_wbi_key(str(img_url)), extract_wbi_key(str(sub_url))

def creator_videos_api_url(
    mid: str,
    page: int,
    page_size: int = DEFAULT_PAGE_SIZE,
    img_key: str | None = None,
    sub_key: str | None = None,
    timestamp: int | None = None,
) -> str:
    base_url = "https://api.bilibili.com/x/space/wbi/arc/search"
    params = {"mid": mid, "pn": page, "ps": page_size, "tid": 0, "order": "pubdate", "platform": "web"}
    if img_key and sub_key:
        return wbi_signed_url(base_url, params, img_key, sub_key, timestamp=timestamp)
    return base_url + "?" + urlencode(params)

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

def fetch_creator_videos(value: str, client: Any | None = None, page_size: int = DEFAULT_PAGE_SIZE) -> list[dict[str, Any]]:
    mid = extract_mid(value)
    http = client or HttpClient(cookie=load_cookie())
    img_key, sub_key = fetch_wbi_keys(http)
    videos: list[dict[str, Any]] = []
    page = 1
    total: int | None = None
    while True:
        payload = http.get_json(creator_videos_api_url(mid, page, page_size, img_key=img_key, sub_key=sub_key))
        _require_ok(payload, "creator videos")
        data = payload.get("data") or {}
        page_data = data.get("page") or {}
        if total is None:
            total_value = page_data.get("count")
            total = int(total_value) if total_value is not None else None
        batch = ((data.get("list") or {}).get("vlist") or [])
        videos.extend(batch)
        if not batch:
            break
        if total is not None and len(videos) >= total:
            break
        page += 1
    return videos


def download_creator_subtitles(
    value: str,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    client: Any | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
    summary_path: str | Path | None = None,
) -> dict[str, Any]:
    http = client or HttpClient(cookie=load_cookie())
    videos = fetch_creator_videos(value, client=http, page_size=page_size)
    results: list[DownloadResult] = []
    for video in videos:
        bvid = video.get("bvid")
        if not bvid:
            continue
        try:
            results.append(download_first_subtitle(str(bvid), output_dir=output_dir, client=http))
        except Exception as exc:  # continue batch and record per-video failure
            results.append(
                DownloadResult(
                    bvid=str(bvid),
                    cid=None,
                    title=video.get("title"),
                    owner_name=None,
                    status="error",
                    reason=f"{type(exc).__name__}: {exc}",
                )
            )
    final_summary_path = Path(summary_path) if summary_path else Path(output_dir) / f"creator-{extract_mid(value)}-summary.json"
    return summarize_download_results(results, final_summary_path, videos=videos, mid=extract_mid(value))


def summarize_download_results(
    results: list[DownloadResult],
    summary_path: str | Path,
    videos: list[dict[str, Any]] | None = None,
    mid: str | None = None,
) -> dict[str, Any]:
    summary = {
        "mid": mid,
        "total": len(results),
        "downloaded": sum(1 for result in results if result.status == "downloaded"),
        "available": sum(1 for result in results if result.status == "available"),
        "unavailable": sum(1 for result in results if result.status == "unavailable"),
        "error": sum(1 for result in results if result.status == "error"),
        "videos": videos or [],
        "results": [asdict(result) for result in results],
    }
    path = Path(summary_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary

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
        subtitle=redact_subtitle_metadata(subtitle),
        raw_subtitle_path=str(raw_path),
        text_path=str(text_path),
        metadata_path=str(metadata_path),
    )
    metadata_path.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    return result

def redact_subtitle_metadata(subtitle: dict[str, Any]) -> dict[str, Any]:
    redacted = dict(subtitle)
    for key in ("subtitle_url", "url"):
        value = redacted.get(key)
        if isinstance(value, str):
            redacted[key] = strip_url_query(value)
    return redacted


def strip_url_query(value: str) -> str:
    normalized = normalize_subtitle_url(value)
    parts = urlsplit(normalized)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))

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

def clean_cookie(value: str) -> str:
    return value.lstrip("\ufeff").strip()

def load_cookie(cookie_file: str | Path | None = None) -> str | None:
    env_cookie = os.environ.get("BILIBILI_COOKIE")
    if env_cookie:
        return clean_cookie(env_cookie)
    path_value = cookie_file or os.environ.get("BILIBILI_COOKIE_FILE")
    if not path_value:
        return None
    path = Path(path_value).expanduser()
    if not path.exists():
        return None
    return clean_cookie(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Download existing Bilibili subtitle tracks for one BV video.")
    parser.add_argument("video", help="BV id or Bilibili video URL")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Directory for raw/text/metadata outputs")
    parser.add_argument("--cookie-file", help="Local cookie file path; never commit this file")
    parser.add_argument("--check-only", action="store_true", help="Only check subtitle availability")
    parser.add_argument("--creator", action="store_true", help="Treat input as a creator space URL/member id and download all upload subtitles")
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE, help="Creator upload page size")
    parser.add_argument("--summary-path", help="Path for creator batch summary JSON")
    args = parser.parse_args(argv)

    client = HttpClient(cookie=load_cookie(args.cookie_file))
    if args.creator:
        summary = download_creator_subtitles(args.video, output_dir=args.output_dir, client=client, page_size=args.page_size, summary_path=args.summary_path)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0 if summary.get("error") == 0 else 1

    if args.check_only:
        info = fetch_subtitle_info(args.video, client=client)
        print(json.dumps(asdict(info), ensure_ascii=False, indent=2))
        return 0 if info.status == "available" else 2

    result = download_first_subtitle(args.video, output_dir=args.output_dir, client=client)
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0 if result.status == "downloaded" else 2


if __name__ == "__main__":
    raise SystemExit(main())




