---
title: 边大娘FM B站视频来源索引
type: source-note
status: draft
tags: [bilibili, video-transcript, copywriting, one-person-company, career, self-media]
created: 2026-04-25
updated: 2026-04-26
source: https://space.bilibili.com/1900638792/upload/video
confidence: medium
---

# 边大娘FM B站视频来源索引

## Summary

本目录保存了 B 站 UP 主 `边大娘FM` 的公开视频字幕来源。通过仓库工具 `automation.extractors.bilibili_subtitle` 使用登录 Cookie 批量提取：共读取 59 个公开视频，成功下载 45 个字幕。复核时发现部分 B 站字幕正文与视频标题明显错配，因此本次只把“标题与正文匹配、且适合一人公司文案”的内容进入知识笔记：提问、模仿、逻辑表达、副业/创业风险、普通人赚钱预期管理；职场晋升、面试、领导管理等内容只在能转化为一人公司表达能力时引用。

## Source Files

- 原始字幕目录：`data/raw/bilibili/subtitles/1900638792/`
- 批量下载汇总：`data/raw/bilibili/subtitles/1900638792/creator-1900638792-summary.json`
- 字幕合集：`sources/videos/bilibili/biandaniang-fm/all-transcripts.md`
- 单篇字幕：同目录下 `001-*.md` 到 `045-*.md`

## Download Result

- Creator: `边大娘FM`
- MID: `1900638792`
- Total videos: 59
- Downloaded subtitles: 45
- Unavailable subtitles: 14
- Tool: `python -m automation.extractors.bilibili_subtitle --creator`

## Curated Knowledge Notes

- `knowledge/operations/copywriting-through-better-questions.md`
- `knowledge/operations/copywriting-by-ethical-imitation.md`
- `knowledge/strategy/side-business-risk-copywriting-for-one-person-company.md`
- `knowledge/operations/sales-oriented-explanation-for-one-person-company.md`

## Most Relevant Videos For One-Person Company Copywriting

### 001. 你赚不到钱是因为，不会问又不会抄

- BVID: `BV1yUQTBWEux`
- 适合沉淀：提问能力、客观问题、找对人问、如何拆解并模仿有效案例。
- 文案启发：把“我该不该做”改写成“这个场景下，哪些客观条件会影响成功率”。

### 002. 缺少执行力，是因为思考能力太差

- BVID: `BV1nWSgBHEGK`
- 适合沉淀：把过度思考改成定期复盘；把执行力问题写成问题拆解能力问题。
- 文案启发：不要用“自律/鸡血”切入，而要用“你没有把问题想清楚”切入。

### 008. 赚钱信息差，不会出现在网上

- BVID: `BV17QedzREno`
- 复核结果：标题与字幕正文明显错配，正文为生物/科普内容，不作为本次知识证据。

### 011. 普通人做自媒体还有机会吗？

- BVID: `BV1W18cziEJE`
- 复核结果：标题与字幕正文明显错配，正文不是自媒体主题，不作为本次知识证据。

### 015. 打工都不行的人，能创业吗？

- BVID: `BV1b6KnzMEF8`
- 适合沉淀：创业不是逃离打工的避难所；基础执行、沟通、交付能力仍然重要。
- 文案启发：一人公司文案要筛掉“逃避型创业”用户。

### 016. 自由职业真的让人更自由吗？

- BVID: `BV1AVMAzDE9S`
- 适合沉淀：自由职业的自由与约束；客户、现金流和自我管理压力。
- 文案启发：把自由职业写成经营责任，而不是纯自由生活方式。

### 019. 大厂裸辞、创业失败后，聊聊普通人创业有多难

- BVID: `BV1pCj2ztEHp`
- 适合沉淀：普通人创业风险、能力误判、现金流和心理预期。
- 文案启发：一人公司产品不要用“轻松创业”承诺获客。

### 031. 自媒体小白不要被“7天起号法”骗了

- BVID: `BV1iVZrYtEGg`
- 复核结果：标题与字幕正文明显错配，正文为手机测评内容，不作为本次知识证据。

### 036. 不要相信“副业能赚快钱”

- BVID: `BV1r1QPYJEGc`
- 适合沉淀：副业的前期投入、隐藏成本、风险筛选、长期积累。
- 文案启发：把副业写成“更高时薪背后的长期准备”，而不是快钱机会。

### 030. 汇报能力差 该怎么提升？

- BVID: `BV1gUfNYQE3F`
- 适合沉淀：结构化表达、让别人理解你做了什么、结论先行。
- 文案启发：产品文案也需要汇报能力：先给结论，再给证据和行动。

## Stable Themes Worth Keeping

### 好文案来自好问题

该来源反复强调“问错人、问错问题”会得到无效答案。对一人公司文案而言，写作前应先把主观问题改成客观问题，例如把“我适不适合做自媒体”改成“零经验小白做成自媒体需要哪些条件、周期和失败原因”。

### 模仿不是复制，而是拆结构

“会抄”不是照搬标题和话术，而是拆解对象：目标人群、场景、矛盾、论证顺序、例子和行动号召。适合一人公司的文案训练是：先抄结构，再换成自己的真实案例和交付边界。

### 一人公司文案要反速成

来源中关于自媒体、副业、创业的内容都反复反对“快钱”“7 天起号”“轻松自由”。这适合沉淀为一人公司文案原则：可信文案应承认成本、周期和失败风险。

### 表达能力是经营能力

提问、汇报、逻辑、拒绝、沟通等职场主题可以转化为一人公司能力：解释产品价值、筛选客户、管理预期、争取信任和复盘结果。

### 文案要切中对方利益点

来源中关于汇报能力的内容可以转化为销售文案原则：不要只讲自己做了什么、产品有什么功能，而要站在对方偏好和利益点上解释为什么这件事和他有关。

## Source Quality Issues

- 部分视频的 B 站字幕正文与标题明显错配，可能是平台字幕接口复用了错误字幕或返回了异常字幕轨道。
- 已确认错配且不作为证据的编号包括：`004`、`005`、`007`、`008`、`009`、`010`、`011`、`012`、`013`、`014`、`016`、`031`、`034`、`035`、`037`、`040`、`041`、`042`、`043`、`044`、`045`。
- 使用本来源时，不能只看标题；进入知识库前必须抽查正文开头和关键段落。

## Skipped Themes

- 纯职场面试、晋升、领导关系：除非能转化为一人公司表达能力，否则不进入文案知识。
- 性别、名媛、领导八卦等话题：不适合作为一人公司文案原则。
- 年薪、行业薪酬等具体判断：时效性强，不作为长期知识。
- 过度绝对化标题：如“99%”“不能靠”“不要相信”等，只保留背后的风险提醒。

## Processing Notes

- 原始字幕保留在 `data/raw/`，来源整理保留在 `sources/`，知识结论写入 `knowledge/`。
- 本来源更适合提炼“文案前的思考方式”，而不是直接复制成销售文案。
- 置信度为 `medium`：已有完整字幕来源，但仍是单一创作者观点，需要结合实际业务验证。




