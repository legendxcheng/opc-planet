import json
from pathlib import Path

import pytest

from automation.extractors import bilibili_subtitle as bs


class FakeHttpClient:
    def __init__(self, responses):
        self.responses = responses
        self.requests = []

    def get_json(self, url):
        self.requests.append(url)
        try:
            return self.responses[url]
        except KeyError:  # pragma: no cover - easier diagnostics when tests fail
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
