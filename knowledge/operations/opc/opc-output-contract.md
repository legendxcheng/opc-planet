---
title: OPC 输出文件契约
type: concept
status: active
tags: [opc, outputs, file-contract, operations]
created: 2026-04-25
updated: 2026-04-25
source: .codex/skills/opc-orchestrator/references/file-contract.md
confidence: high
---

# OPC 输出文件契约

## Summary

OPC 的价值来自阶段化产物，而不只是对话。每个阶段都应生成可追踪文件，作为下游分析的输入和未来 Agent 的记忆基础。

## Recommended Directory

本仓库推荐使用：

- `outputs/opc-doc/00-orchestration/`
- `outputs/opc-doc/01-resource-audit/`
- `outputs/opc-doc/02-niche-positioning/`
- `outputs/opc-doc/03-value-proposition/`
- `outputs/opc-doc/04-business-model/`
- `outputs/opc-doc/06-mvp/`
- `outputs/opc-doc/07-conversion-loop/`
- `outputs/opc-doc/08-asset-ops/`
- `outputs/opc-doc/09-dashboard-review/`

## Stage Files

| 阶段 | 必要文件 | 用途 |
| --- | --- | --- |
| 01 资源盘点 | `inventory.md` | 人类可读的资源事实底图。 |
| 01 资源盘点 | `scorecard.json` | 机器可读的资源评分和结构化字段。 |
| 02 利基定位 | `three-ring-analysis.md` | 新杠杆、边界变动、资源匹配的交集分析。 |
| 02 利基定位 | `candidates.md` | 候选细分方向与评分对比。 |
| 02 利基定位 | `target-segment.json` | 选定目标客群的结构化信息。 |
| 02 利基定位 | `positioning-statement.md` | 一句话定位。 |
| 03 价值主张 | `value-proposition-canvas.md` | Jobs / Pains / Gains 与方案匹配。 |
| 03 价值主张 | `messaging.md` | 对外表达、标题、卖点和版本选择。 |
| 03 价值主张 | `segment-vp-matrix.md` | 客群与价值主张矩阵。 |
| 04 商业模式 | `lean-canvas.md` | 商业模式核心模块。 |
| 04 商业模式 | `business-model-canvas-lite.md` | 简化商业模式画布。 |
| 04 商业模式 | `risky-assumptions.md` | 最需要验证的假设清单。 |
| 04 商业模式 | `pricing-notes.md` | 收费结构和价格判断。 |
| 06 MVP | `mvp-spec.md` | 最小验证方案。 |
| 06 MVP | `experiment-plan.md` | 实验步骤、周期和成功标准。 |
| 06 MVP | `human-ai-split.md` | 人工与 AI/自动化分工。 |
| 07 转化闭环 | `conversion-path.md` | 从触达到成交的主路径。 |
| 07 转化闭环 | `channel-strategy.md` | 渠道选择和主辅路径。 |
| 07 转化闭环 | `content-plan.md` | 内容触达计划。 |

## File Quality Rules

- 每个文件必须能被下游阶段直接读取。
- 事实、解释、假设和下一步要分开写。
- 重要判断要保留理由和证据来源。
- 用户未确认的内容标记为假设或草案。
- JSON 文件用于结构化状态，Markdown 文件用于人类理解。

## Evidence

- `.codex/skills/opc-orchestrator/references/file-contract.md`
- `.codex/skills/opc-orchestrator/references/stage-map.md`
