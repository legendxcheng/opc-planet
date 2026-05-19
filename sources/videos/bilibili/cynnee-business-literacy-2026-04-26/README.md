---
title: Cynnee赚钱说商业素养字幕批次索引
type: source-note
status: draft
tags: [bilibili, business-literacy, content-business, monetization, raw-transcripts]
created: 2026-04-26
updated: 2026-04-26
source: https://space.bilibili.com/702276086/upload/video
author: Cynnee赚钱说
published:
confidence: low
---

# Cynnee赚钱说商业素养字幕批次索引

## Summary

本批次来自 B 站 UP 主 `Cynnee赚钱说` 的投稿页，目标是按标题筛选与“提升商业素养”相关的视频，并提取已有字幕文案。原始字幕、metadata、标题筛选记录和批次 summary 保存在 `data/raw/bilibili/subtitles/702276086/`。

## Collection Status

- 投稿总数：212
- 标题筛选为商业素养相关：192
- 已成功提取字幕文案：190
- 未提取：2
  - `BV1xRB6BHEbE`《你对产品的理解力趋近于零》：`no_subtitle_tracks`
  - `BV1gDtYzvE83`《24小时破局：如何构建高价值感》：B 站详情接口返回 `-404`

## Raw Files

- Raw directory: `data/raw/bilibili/subtitles/702276086/`
- Title analysis: `data/raw/bilibili/subtitles/702276086/creator-702276086-title-analysis.json`
- Batch summary: `data/raw/bilibili/subtitles/702276086/creator-702276086-business-literacy-summary.json`
- Extraction helper: `temp/extract_702276086_business_literacy.py`

## Use Notes

- 这些文件是原始材料，不是 canonical knowledge。
- 多数字幕是 B 站 AI 字幕，存在错字、断句错误、字幕缺失、标题与正文错配等问题。
- 本批次进入知识库的结论只使用已抽读且正文与标题主题一致的代表来源。
- 来源观点带有强烈表达风格和营销化语气，知识库笔记已降噪为可复用原则，不直接继承夸张口号。
- 任何强判断都应回到原始 `.txt` 和 `.metadata.json` 复核。

## Reviewed Representative Sources

| BV | Title | Raw transcript |
| --- | --- | --- |
| `BV1FMmyBkEqN` | 满足市场上这5类需求，你不可能不赚钱 | `data/raw/bilibili/subtitles/702276086/BV1FMmyBkEqN-ai-zh.txt` |
| `BV1cExvzEEa7` | 如果重新创业，我会从“销转系统”开始 | `data/raw/bilibili/subtitles/702276086/BV1cExvzEEa7-ai-zh.txt` |
| `BV1fg8kz6EGg` | 你的内容必须是你的产品 | `data/raw/bilibili/subtitles/702276086/BV1fg8kz6EGg-ai-zh.txt` |
| `BV1YChBzxEcZ` | 你的产品定价，决定了你生意的“命格” | `data/raw/bilibili/subtitles/702276086/BV1YChBzxEcZ-ai-zh.txt` |
| `BV1gwhwzUEti` | 低价是最昂贵的陷阱 | `data/raw/bilibili/subtitles/702276086/BV1gwhwzUEti-ai-zh.txt` |
| `BV12a2iBFEQJ` | 你的业务正在“假性盈利”：为什么高毛利、高复购反而正在拖垮你？ | `data/raw/bilibili/subtitles/702276086/BV12a2iBFEQJ-ai-zh.txt` |
| `BV1UaWNzuEDw` | 大流量=低转化，真正的变现必定是细分垂直内容 | `data/raw/bilibili/subtitles/702276086/BV1UaWNzuEDw-ai-zh.txt` |
| `BV15ASqBSEXo` | 停止你的商业创新，99%的利润来自于“像素级复制” | `data/raw/bilibili/subtitles/702276086/BV15ASqBSEXo-ai-zh.txt` |
| `BV13N25BuEKG` | 机会的第一性原理是趋势 | `data/raw/bilibili/subtitles/702276086/BV13N25BuEKG-ai-zh.txt` |

## Known Mismatched Or Weak Transcripts

这些文件的标题与字幕开头明显不一致，或字幕过短、只有音乐/段子内容，暂不用于知识结论。

| BV | Title | Observed issue |
| --- | --- | --- |
| `BV13n8bz4EMn` | 你的产品不是你的生意 | 字幕正文为歌曲/武侠台词，和标题不一致 |
| `BV1riAAzKEzy` | 完美交付是普通创业者最愚蠢的自杀行为 | 字幕正文为个人兴趣与才华叙述，和标题不一致 |
| `BV12qveBfEkp` | 听平台的话，做平台认可的好视频 | 字幕几乎只有音乐标记 |
| `BV1cnenzFEZg` | 销售的终极形态不是说服购买，而是诊断 | 字幕正文为卖瓜段子，和标题不一致 |
| `BV13vSbBdEZw` | 新手创业第一步：彻底忘记“用户需求”，先找到你的“提款机对标” | 字幕过短且无商业正文 |
| `BV15sY9zrEJ1` | 再打磨产品你也赚不到钱，去设计一个无法拒绝的承诺 | 字幕过短且无商业正文 |
| `BV1ApMXzoEDZ` | AI不会取代你 但它会让你变得廉价 | 字幕过短且无商业正文 |

## Derived Knowledge Notes

- `knowledge/customers/hidden-customer-demand-before-surface-need.md`
- `knowledge/operations/sales-conversion-system-as-business-validation.md`
- `knowledge/products/content-and-product-should-share-one-value-path.md`
- `knowledge/finance/pricing-as-customer-filter.md`
- `knowledge/finance/profit-system-before-single-metric.md`
