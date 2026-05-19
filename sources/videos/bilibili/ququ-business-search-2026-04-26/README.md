---
title: 曲曲商业搜索字幕批次索引
type: source-note
status: draft
tags: [bilibili, business-literacy, sales, entrepreneurship, raw-transcripts]
created: 2026-04-26
updated: 2026-04-28
source: https://search.bilibili.com/all?keyword=%E6%9B%B2%E6%9B%B2%20%E5%95%86%E4%B8%9A
confidence: low
---

# 曲曲商业搜索字幕批次索引

## Summary

本批次来自 B 站搜索“曲曲 商业”的视频结果，目标是筛选与提升商业素养相关的视频标题，并提取已有字幕文案。原始字幕、metadata 和批次 summary 保存在 `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/`。

## Collection Status

- 搜索结果处理范围：第 1 页到第 50 页；部分页面被 B 站 412 风控拦截，其中第 49-50 页只有错误记录。
- 首轮已下载字幕文件：122 个 `.txt` 文件，其中第一页 15 个，后续批次 107 个。这个数字只表示文件已写入，不表示内容全部可用。
- 2026-04-28 补抓后，原始字幕目录共有 170 个 `.txt` 文件；其中新增缺失候选里只有 6 条通过校验，可作为来源摘要，其余多为 `mismatched_subtitle` 或仍不可用。
- 不可用原因包括：无字幕轨、字幕 metadata 中没有可下载 URL、搜索请求被 412 拦截。
- 第 46-50 页在用户中断前已有部分结果写入 `search-pages-46-50-summary.json`。

## Use Notes

- 这些文件是原始材料，不是 canonical knowledge。
- 多数字幕是 B 站 AI 字幕，可能有错字、断句错误、串轨或标题与字幕内容不一致。
- 搜索结果混入了非曲曲、泛娱乐、情感关系、数码产品等噪声；进入知识库的结论只使用主题高度一致的代表来源。
- 已发现多条标题和字幕内容明显错配，使用前必须先做有效性筛查。
- 任何强判断都应回到原始 `.txt` 和 `.metadata.json` 复核。

## Reviewed Representative Sources

| BV | Title | Raw transcript |
| --- | --- | --- |
| `BV1bTrPBbEmN` | 曲曲：赚钱是一门专业的学科，普通人想要赚钱就要贯通在销售中我有别人没有的商业逻辑来做交易 | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV1bTrPBbEmN-ai-zh.txt` |
| `BV17CXjBkEs6` | 曲曲：了解商业世界的游戏规则 | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV17CXjBkEs6-ai-zh.txt` |
| `BV1XBdBBKEpH` | 曲曲分享事业经：不要凭空创造一个商业模式 | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV1XBdBBKEpH-ai-zh.txt` |
| `BV11ExrzrEaz` | 曲曲干货赚钱靠的是想象力...商业认知商业思维 | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV11ExrzrEaz-ai-zh.txt` |
| `BV1y9ogBLETW` | 曲曲 销售要选择天花板高的行业 | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV1y9ogBLETW-ai-zh.txt` |
| `BV13LoXBGEwv` | 曲曲：大家一定要看一下我的金贵的事业哟，对你们从0到1跑通商业闭环非常有帮助 | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV13LoXBGEwv-ai-zh.txt` |
| `BV19TQMB3E1k` | 曲曲分享事业经：男人和女人做生意的逻辑不一样 | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV19TQMB3E1k-ai-zh.txt` |
| `BV1kvXzBjEpy` | 曲曲分享事业经：自媒体赚钱不要想着做个人IP | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV1kvXzBjEpy-ai-zh.txt` |
| `BV1xfo5BbEX8` | 曲曲：普通人想财富自由除了销售别无他法 | `data/raw/bilibili/subtitles/ququ-business-search-2026-04-26/BV1xfo5BbEX8-ai-zh.txt` |

## Known Mismatched Transcripts

这些文件的标题与字幕开头明显不一致，暂不用于知识结论。

| BV | Title | Observed transcript mismatch |
| --- | --- | --- |
| `BV1ukF7zmENK` | 曲曲讲商业，全程干货：AI产品没人用，你的流量不是冲着产品来的 | 字幕开头是汽车电池和泄压阀 |
| `BV1mp6KBAEZZ` | 曲曲分享事业经：找到产品的卖点才是销售的关键 | 字幕开头是手机镜头膜测评 |
| `BV1xM48zCEyP` | 想创业，首先商业逻辑要闭环 | 字幕开头是黄磊锅包肉 |
| `BV1We411q7C8` | 【曲曲大女人】销售是最小的创业模型 | 字幕开头是蚂蝗科普 |
| `BV1idcbzhEw5` | 曲曲：我的商业头脑严重被低估了！连麦拆解为何你的产品无人买？ | 字幕开头是“乌干达地主”段子 |
| `BV173PPzKEsB` | 曲曲：现金流生意一定要会算 ROI | 字幕开头是童话/陪侍段子 |
| `BV1MAD5BLEPE` | 曲曲：97 年女生月入几万却迷茫：流量比选品重要 100 倍 | 字幕开头是亲子沟通 |
| `BV1SV29YdE4z` | 曲曲讲述自己从零创业的历程... | 字幕开头是娱乐八卦叙述 |

## Derived Knowledge Notes

- `knowledge/operations/sales-as-smallest-business-loop.md`
- `knowledge/products/validated-business-model-before-innovation.md`
- `knowledge/customers/market-feedback-before-product-assumptions.md`
- `knowledge/strategy/choose-industry-by-ceiling-and-cashflow.md`
- `knowledge/products/traffic-must-serve-product-transaction.md`

## 2026-04-28 Redownload Update

刷新 B 站 Cookie 后重新补抓缺失候选，新增 6 条通过校验的字幕来源，摘要见 `2026-04-28-redownloaded-verified-transcripts.md`。新增材料主要补充“小流量高客单”“现金流优先”“通过销售靠近高支付能力客户”等主题。未通过校验的 `mismatched_subtitle` 不进入知识结论。
