import json
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from pathlib import Path

import pytest

from automation.extractors import bilibili_subtitle as bs



def canonical_test_url(url):
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query) if key not in {"w_rid", "wts"}]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(sorted(query)), ""))

class FakeHttpClient:
    def __init__(self, responses):
        self.responses = responses
        self.requests = []

    def get_json(self, url):
        self.requests.append(url)
        try:
            return self.responses[url]
        except KeyError:  # pragma: no cover - easier diagnostics when tests fail
            canonical_url = canonical_test_url(url)
            for response_url, response in self.responses.items():
                if canonical_test_url(response_url) == canonical_url:
                    return response
            raise AssertionError(f"unexpected url: {url}")


def test_extracts_bvid_from_url_and_plain_id():
    assert bs.extract_bvid("BV1VGQHBLEMn") == "BV1VGQHBLEMn"
    assert bs.extract_bvid("https://www.bilibili.com/video/BV1VGQHBLEMn/?spm_id_from=x") == "BV1VGQHBLEMn"


@pytest.mark.parametrize("value", ["", "https://example.com/nope", "av123456"])
def test_extract_bvid_rejects_missing_bv(value):
    with pytest.raises(ValueError):
        bs.extract_bvid(value)


def test_fetch_subtitle_tracks_reports_unavailable_when_player_has_no_tracks():
    bvid = "BV1VGQHBLEMn"
    cid = 37538696170
    client = FakeHttpClient(
        {
            bs.nav_api_url(): {"code": 0, "data": {"wbi_img": {"img_url": "https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png", "sub_url": "https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png"}}},
            bs.view_api_url(bvid): {"code": 0, "data": {"title": "Example", "cid": cid, "owner": {"name": "UP"}}},
            bs.player_api_url(bvid, cid): {
                "code": 0,
                "data": {"need_login_subtitle": True, "subtitle": {"subtitles": []}},
            },
        }
    )

    result = bs.fetch_subtitle_info(bvid, client=client)

    assert result.status == "unavailable"
    assert result.reason == "login_required_or_unavailable"
    assert result.bvid == bvid
    assert result.cid == cid
    assert result.title == "Example"


def test_downloads_subtitle_json_and_writes_text(tmp_path):
    bvid = "BV1TEST12345"
    cid = 100
    subtitle_url = "https://aisubtitle.hdslb.com/bfs/ai_subtitle/example.json"
    client = FakeHttpClient(
        {
            bs.nav_api_url(): {"code": 0, "data": {"wbi_img": {"img_url": "https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png", "sub_url": "https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png"}}},
            bs.view_api_url(bvid): {"code": 0, "data": {"title": "测试 标题", "cid": cid, "owner": {"name": "测试UP"}}},
            bs.player_api_url(bvid, cid): {
                "code": 0,
                "data": {
                    "need_login_subtitle": False,
                    "subtitle": {
                        "subtitles": [
                            {"lan": "zh-CN", "lan_doc": "中文", "subtitle_url": "//aisubtitle.hdslb.com/bfs/ai_subtitle/example.json"}
                        ]
                    },
                },
            },
            subtitle_url: {"body": [{"from": 0.0, "to": 1.2, "content": "第一句"}, {"from": 1.2, "to": 2.0, "content": "第二句"}]},
        }
    )

    result = bs.download_first_subtitle(bvid, output_dir=tmp_path, client=client)

    assert result.status == "downloaded"
    assert result.text_path is not None
    assert result.raw_subtitle_path is not None
    assert result.metadata_path is not None
    assert Path(result.text_path).read_text(encoding="utf-8") == "第一句\n第二句\n"
    metadata = json.loads(Path(result.metadata_path).read_text(encoding="utf-8"))
    assert metadata["bvid"] == bvid
    assert metadata["subtitle"]["lan"] == "zh-CN"
    assert metadata["validation_status"] == "passed"


def test_download_marks_short_subtitle_as_needs_review(tmp_path):
    bvid = "BV1TEST12345"
    cid = 100
    subtitle_url = "https://aisubtitle.hdslb.com/bfs/ai_subtitle/short.json"
    client = FakeHttpClient(
        {
            bs.view_api_url(bvid): {"code": 0, "data": {"title": "Justin Welsh 一人公司", "duration": 3600, "cid": cid, "owner": {"name": "测试UP"}}},
            bs.player_api_url(bvid, cid): {
                "code": 0,
                "data": {
                    "need_login_subtitle": False,
                    "subtitle": {
                        "subtitles": [
                            {"lan": "ai-zh", "id_str": "sub-1", "subtitle_url": subtitle_url}
                        ]
                    },
                },
            },
            subtitle_url: {"body": [{"from": 0.0, "to": 120.0, "content": "Justin Welsh 访谈"}]},
        }
    )

    result = bs.download_first_subtitle(bvid, output_dir=tmp_path, client=client)

    assert result.status == "needs_review"
    assert "subtitle_covers_too_little_video" in result.validation_warnings
    metadata = json.loads(Path(result.metadata_path).read_text(encoding="utf-8"))
    assert metadata["validation_status"] == "needs_review"
    assert metadata["validation_metrics"]["coverage_ratio"] == pytest.approx(120 / 3600)


def test_download_marks_topic_mismatch_as_mismatched_subtitle(tmp_path):
    bvid = "BV1TEST12345"
    cid = 100
    subtitle_url = "https://aisubtitle.hdslb.com/bfs/ai_subtitle/mismatch.json"
    client = FakeHttpClient(
        {
            bs.view_api_url(bvid): {"code": 0, "data": {"title": "Justin Welsh 一人公司 创作者业务", "duration": 900, "cid": cid, "owner": {"name": "测试UP"}}},
            bs.player_api_url(bvid, cid): {
                "code": 0,
                "data": {
                    "need_login_subtitle": False,
                    "subtitle": {
                        "subtitles": [
                            {"lan": "ai-zh", "id_str": "sub-2", "subtitle_url": subtitle_url}
                        ]
                    },
                },
            },
            subtitle_url: {"body": [{"from": 0.0, "to": 850.0, "content": "蔡徐坤 代言 品牌 娱乐 明星 粉丝 舆情"}]},
        }
    )

    result = bs.download_first_subtitle(bvid, output_dir=tmp_path, client=client)

    assert result.status == "mismatched_subtitle"
    assert "subtitle_text_does_not_match_video_title" in result.validation_warnings
    assert Path(result.text_path).exists()


def test_download_marks_reused_ai_subtitle_id_as_mismatched(tmp_path):
    existing_dir = tmp_path / "existing"
    existing_dir.mkdir()
    (existing_dir / "other.metadata.json").write_text(
        json.dumps(
            {
                "bvid": "BV1OTHER9999",
                "subtitle": {"id_str": "reused-ai-id", "lan": "ai-zh", "type": 1, "ai_status": 2},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "current"
    bvid = "BV1TEST12345"
    cid = 100
    subtitle_url = "https://aisubtitle.hdslb.com/bfs/ai_subtitle/reused.json"
    client = FakeHttpClient(
        {
            bs.view_api_url(bvid): {"code": 0, "data": {"title": "Justin Welsh 一人公司", "duration": 300, "cid": cid, "owner": {"name": "测试UP"}}},
            bs.player_api_url(bvid, cid): {
                "code": 0,
                "data": {
                    "need_login_subtitle": False,
                    "subtitle": {
                        "subtitles": [
                            {"lan": "ai-zh", "id_str": "reused-ai-id", "type": 1, "ai_status": 2, "subtitle_url": subtitle_url}
                        ]
                    },
                },
            },
            subtitle_url: {"body": [{"from": 0.0, "to": 280.0, "content": "Justin Welsh 一人公司 内容 产品"}]},
        }
    )

    result = bs.download_first_subtitle(
        bvid,
        output_dir=out_dir,
        client=client,
        validation_metadata_roots=[existing_dir],
    )

    assert result.status == "mismatched_subtitle"
    assert "ai_subtitle_id_reused_by_other_video" in result.validation_warnings
    assert result.validation_metrics["reused_subtitle_bvids"] == ["BV1OTHER9999"]


def test_load_cookie_strips_utf8_bom(tmp_path, monkeypatch):
    monkeypatch.delenv("BILIBILI_COOKIE", raising=False)
    cookie_file = tmp_path / "cookie.txt"
    cookie_file.write_text("\ufeffSESSDATA=abc; bili_jct=def\n", encoding="utf-8")

    assert bs.load_cookie(cookie_file) == "SESSDATA=abc; bili_jct=def"


def test_creator_video_list_paginates_until_all_videos():
    mid = "275565632"
    client = FakeHttpClient(
        {
            bs.nav_api_url(): {"code": 0, "data": {"wbi_img": {"img_url": "https://i0.hdslb.com/bfs/wbi/7cd084941338484aae1ad9425b84077c.png", "sub_url": "https://i0.hdslb.com/bfs/wbi/4932caff0ff746eab6f01bf08b70ac45.png"}}},
            bs.creator_videos_api_url(mid, 1, 2): {
                "code": 0,
                "data": {"page": {"count": 3}, "list": {"vlist": [{"bvid": "BV1AAAA11111", "title": "A"}, {"bvid": "BV1BBBB22222", "title": "B"}]}},
            },
            bs.creator_videos_api_url(mid, 2, 2): {
                "code": 0,
                "data": {"page": {"count": 3}, "list": {"vlist": [{"bvid": "BV1CCCC33333", "title": "C"}]}},
            },
        }
    )

    videos = bs.fetch_creator_videos(mid, client=client, page_size=2)

    assert [video["bvid"] for video in videos] == ["BV1AAAA11111", "BV1BBBB22222", "BV1CCCC33333"]


def test_extract_mid_from_space_url():
    assert bs.extract_mid("https://space.bilibili.com/275565632/upload/video") == "275565632"
    assert bs.extract_mid("275565632") == "275565632"


def test_batch_download_summarizes_downloaded_and_unavailable(tmp_path):
    results = [
        bs.DownloadResult(bvid="BV1AAAA11111", cid=1, title="A", owner_name="UP", status="downloaded"),
        bs.DownloadResult(bvid="BV1BBBB22222", cid=2, title="B", owner_name="UP", status="unavailable", reason="no_subtitle_tracks"),
        bs.DownloadResult(bvid="BV1CCCC33333", cid=3, title="C", owner_name="UP", status="needs_review"),
        bs.DownloadResult(bvid="BV1DDDD44444", cid=4, title="D", owner_name="UP", status="mismatched_subtitle"),
    ]

    summary = bs.summarize_download_results(results, tmp_path / "summary.json")

    assert summary["total"] == 4
    assert summary["downloaded"] == 1
    assert summary["unavailable"] == 1
    assert summary["needs_review"] == 1
    assert summary["mismatched_subtitle"] == 1
    assert (tmp_path / "summary.json").exists()


def test_wbi_signed_url_adds_timestamp_and_signature():
    url = bs.wbi_signed_url(
        "https://api.bilibili.com/x/space/wbi/arc/search",
        {"mid": "275565632", "pn": 1, "ps": 30},
        "7cd084941338484aae1ad9425b84077c",
        "4932caff0ff746eab6f01bf08b70ac45",
        timestamp=1777110000,
    )

    assert "wts=1777110000" in url
    assert "w_rid=" in url
    assert "mid=275565632" in url
    assert "pn=1" in url


def test_creator_video_api_url_can_be_signed():
    url = bs.creator_videos_api_url(
        "275565632",
        1,
        30,
        img_key="7cd084941338484aae1ad9425b84077c",
        sub_key="4932caff0ff746eab6f01bf08b70ac45",
        timestamp=1777110000,
    )

    assert url.startswith("https://api.bilibili.com/x/space/wbi/arc/search?")
    assert "w_rid=" in url



