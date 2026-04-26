import json
import re
from pathlib import Path

source_dir = Path('data/raw/bilibili/subtitles/275565632')
summary = json.loads((source_dir / 'summary.json').read_text(encoding='utf-8'))
out_dir = Path('sources/videos/bilibili/dontbesilent-liaozhuanqian')
out_dir.mkdir(parents=True, exist_ok=True)
combined_path = out_dir / 'all-transcripts.md'

def slugify(value: str, fallback: str) -> str:
    value = re.sub(r'[^0-9A-Za-z\u4e00-\u9fff]+', '-', value).strip('-')
    return (value[:60].strip('-') or fallback)

def yaml_escape(value):
    if value is None:
        return 'null'
    return json.dumps(str(value), ensure_ascii=False)

def read_text(path_value):
    if not path_value:
        return ''
    return Path(path_value).read_text(encoding='utf-8').strip()

combined_sections = []
count = 0
for index, result in enumerate(summary['results'], start=1):
    if result.get('status') != 'downloaded':
        continue
    text = read_text(result.get('text_path'))
    bvid = result['bvid']
    title = result.get('title') or bvid
    video_url = f'https://www.bilibili.com/video/{bvid}/'
    slug = slugify(title, bvid)
    md_path = out_dir / f'{index:03d}-{bvid}-{slug}.md'
    md = f'''---
title: {yaml_escape(title)}
type: source-note
status: draft
tags: [bilibili, video-transcript, dontbesilent-liaozhuanqian]
created: 2026-04-25
updated: 2026-04-25
source: {yaml_escape(video_url)}
confidence: medium
bvid: {yaml_escape(bvid)}
creator: "dontbesilent聊赚钱"
---

## Summary

B 站视频《{title}》的字幕文案整理版，已去除时间轴信息。

## Metadata

- Creator: dontbesilent聊赚钱
- BVID: {bvid}
- Source: {video_url}
- Subtitle language: {result.get('subtitle', {}).get('lan_doc') or '中文'}

## Transcript

{text}
'''
    md_path.write_text(md, encoding='utf-8')
    combined_sections.append(f'''## {index:03d}. {title}

- BVID: {bvid}
- Source: {video_url}

{text}
''')
    count += 1

combined = f'''---
title: "dontbesilent聊赚钱 B站视频字幕合集"
type: source-note
status: draft
tags: [bilibili, video-transcript, transcript-collection]
created: 2026-04-25
updated: 2026-04-25
source: "https://space.bilibili.com/275565632/upload/video"
confidence: medium
creator: "dontbesilent聊赚钱"
video_count: {count}
---

## Summary

这是 B 站 UP 主 dontbesilent聊赚钱 已成功下载字幕的 {count} 个视频文案合集，已去除字幕时间轴信息。每个视频也有独立 Markdown 文件保存在同一目录。

## Transcripts

''' + '\n---\n\n'.join(combined_sections)
combined_path.write_text(combined, encoding='utf-8')
print(json.dumps({'out_dir': str(out_dir), 'combined_path': str(combined_path), 'count': count}, ensure_ascii=False, indent=2))
