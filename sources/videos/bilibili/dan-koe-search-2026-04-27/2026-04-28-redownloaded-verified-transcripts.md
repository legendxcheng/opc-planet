---
title: Dan Koe 搜索补抓通过校验字幕摘要
type: source-note
status: draft
tags: [bilibili, video-transcript, dan-koe, one-person-company, focus, productized-self]
created: 2026-04-28
updated: 2026-04-28
source: data/interim/bilibili-redownload-audit-2026-04-28.json
author: multiple
published:
confidence: medium
---

# Dan Koe 搜索补抓通过校验字幕摘要

## Source

- Search batch: `data/raw/bilibili/search/dan-koe-2026-04-27/`
- Raw transcript directory: `data/raw/bilibili/subtitles/dan-koe-search-2026-04-27/`
- Redownload audit: `data/interim/bilibili-redownload-audit-2026-04-28.json`
- Filled-missing summary: `data/interim/bilibili-redownload-filled-missing-summary-2026-04-28.json`
- Collected: 2026-04-28

## Summary

2026-04-28 使用刷新后的 B 站 Cookie 重新补抓 Dan Koe 搜索候选。此前缺失的候选中，新增 3 条通过自动校验的字幕文本。它们不都直接讲“一人公司商业模式”，但可以补充一人公司经营中的两个底层约束：创始人注意力是最稀缺资源；未来个人业务会从静态信息产品，转向知识库、工具和 AI 辅助交付。

未通过校验的 `mismatched_subtitle` 不进入本摘要，也不作为知识结论来源。

## Verified Transcripts

| BVID | Title | Raw transcript | Primary use |
| --- | --- | --- | --- |
| `BV1xhimBPEQG` | 一人公司创业博主 Dan Koe:如果一切从零开始（在2026年）如何打造一人公司 | `data/raw/bilibili/subtitles/dan-koe-search-2026-04-27/BV1xhimBPEQG-ai-zh.txt` | 信息产品软件化、知识库与 AI 辅助交付 |
| `BV164GnzBEJ4` | 每天4小时深度工作，改变你的生活 | `data/raw/bilibili/subtitles/dan-koe-search-2026-04-27/BV164GnzBEJ4-zh-CN.txt` | 专注、少数优先事项、深度工作 |
| `BV19d9wBcEUn` | 每天独处 2-4 小时｜DanKoe 的百万富翁高效工作法 | `data/raw/bilibili/subtitles/dan-koe-search-2026-04-27/BV19d9wBcEUn-ai-zh.txt` | 专注不是工时崇拜，而是注意力投向 |

## Extracted Facts

- `BV1xhimBPEQG` 把个人业务描述为一个人同时承担营销、内容、销售和产品设计，并认为内容是思维片段，产品是解决问题过程的封装。
- `BV1xhimBPEQG` 认为传统信息产品会被 AI 和平台稀释，更可持续的方向是把知识组织成课程、帮助文档、练习、反馈、问答和工具系统。
- `BV164GnzBEJ4` 与 `BV19d9wBcEUn` 都把专注视为工作乘数，而不是把长时间工作本身视为结果。
- `BV19d9wBcEUn` 区分了构建期和维护期：构建新产品、服务或品牌需要前期投入；维护已建成系统可以压缩到更少但更高质量的工作块。

## Opinions / Interpretations

- 对一人公司而言，深度工作不是生产力话题，而是资源配置话题：创始人每天能用于高杠杆资产的连续注意力有限，必须减少低价值任务的占用。
- “每天 2-4 小时”不应被理解为承诺少工作，而应被改写为：先明确少数优先事项，再把连续注意力投向能沉淀资产的工作。
- 信息产品软件化适合本仓库的知识库方向：静态内容只是素材，真正的产品可能是知识库、Agent、提示词、练习、诊断和人类反馈的组合。

## Useful For

- `knowledge/strategy/productized-self-value-creator-for-one-person-company.md`
- `knowledge/strategy/execution-clarity-for-one-person-company.md`
- `knowledge/technology/ai-human-agent-workflow.md`

## Follow-up

- 对 `BV164GnzBEJ4` 与 `BV19d9wBcEUn` 做去重处理：两条内容主题高度相似，后续知识库只保留互补观点。
- 如果需要更高置信度，应交叉验证 Dan Koe 原 YouTube 标题和原英文字幕。
