---
title: OPC 方法论作为一人公司建盘骨架
type: concept
status: active
tags: [opc, strategy, one-person-company, agent-workflow]
created: 2026-04-25
updated: 2026-04-25
source: sources/web/2026-04-25-opc-skills-ft07.md
confidence: medium
---

# OPC 方法论作为一人公司建盘骨架

## Summary

OPC 方法论可以作为本知识库的一人公司“建盘操作系统”：先盘清资源，再选择利基，随后定义价值主张、商业模式、MVP 和转化闭环，最后在运营期持续沉淀资产并复盘瓶颈。它最适合被改造成 Agent 工作流，而不是只当作静态战略笔记。

## Key Points

- `00` 总编排保证不跳步：先判断当前阶段、用户模式和已有产物，再进入下一步。
- `01-07` 是建盘主链路：资源 → 利基 → 价值 → 商模 → MVP → 转化。
- `08-09` 是运营触发模块：资产沉淀与经营复盘，不替代早期主链路。
- 每个阶段都应输出结构化文件，让知识库能够追踪决策、假设、证据和下一步行动。
- 对一人公司而言，OPC 的关键约束是轻资产、可验证、可复用，而不是扩大组织规模。

## Details

### 阶段边界

| 阶段 | 核心问题 | 本仓库推荐落点 |
| --- | --- | --- |
| 00 总编排 | 现在处在哪个阶段？是否已有上次产物？ | `agent/prompts/`, `outputs/opc-doc/README.md` |
| 01 资源盘点 | 我手上到底有什么？不能做什么？ | `outputs/opc-doc/01-resource-audit/` |
| 02 利基定位 | 哪个细分机会同时匹配市场变化和自身资源？ | `outputs/opc-doc/02-niche-positioning/` |
| 03 价值主张 | 为谁解决什么痛点，带来什么收益？ | `outputs/opc-doc/03-value-proposition/` |
| 04 商业模式 | 如何收费、交付、获客，最高风险假设是什么？ | `outputs/opc-doc/04-business-model/` |
| 06 MVP 设计 | 先验证哪个假设，用什么最小形式验证？ | `outputs/opc-doc/06-mvp/` |
| 07 转化闭环 | 从触达到成交的路径如何跑通？ | `outputs/opc-doc/07-conversion-loop/` |
| 08 资产沉淀 | 哪些交付、内容、流程能复用？ | `knowledge/operations/`, `outputs/playbooks/` |
| 09 经营复盘 | 当前唯一瓶颈是什么，下一周期只抓什么？ | `outputs/reports/`, `knowledge/strategy/` |

### 本地化原则

- 保留 OPC 的顺序和产物纪律，但把输出放进本仓库既有目录。
- 任何判断都要回链到 `sources/`、`knowledge/` 或 `outputs/` 的证据文件。
- 重要假设要进入 MVP 或复盘文件，不要只留在对话中。
- 资产沉淀优先进入 `knowledge/operations/`、`templates/` 或 `agent/`，方便未来 Agent 复用。

## Evidence

- 方糖 OPC 技能集页面列出 9 个 Skill、主链路和触发模块。
- 页面给出的案例显示，OPC 用“资源盘点 → 利基定位 → 价值主张 → 商业模式 → MVP → 转化闭环”的顺序推进，并在每一步生成结构化产物。
- ContextQMD 索引显示 `easychen/opc-methodology` 还有更完整的底层方法论文档，可作为后续补充来源。

## Links

- Source note: `sources/web/2026-04-25-opc-skills-ft07.md`
- Raw extract: `data/raw/opc-skills-site/opc-skills-ft07-extracted.md`
- Original site: `https://opc-skills.ft07.com/`
- Related repository: `https://github.com/easychen/opc-methodology`

## Next Actions

- 用 `agent/prompts/opc-orchestrator-local.md` 启动本仓库的第一轮 OPC 建盘。
- 网络恢复后补抓 `easychen/opc-methodology/skills` 下每个 Skill 的完整说明。
- 创建 `outputs/opc-doc/` 并按阶段生成第一批实际业务产物。
