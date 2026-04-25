---
title: 方糖 OPC 技能集
type: source-note
status: active
tags: [opc, one-person-company, agent-skills, methodology]
created: 2026-04-25
updated: 2026-04-25
source: https://opc-skills.ft07.com/
author: 方糖 / easychen
published:
confidence: medium
---

# 方糖 OPC 技能集

## Source

- URL / Citation: `https://opc-skills.ft07.com/`
- Related repository: `https://github.com/easychen/opc-methodology`
- Collected: 2026-04-25
- Raw extract: `data/raw/opc-skills-site/opc-skills-ft07-extracted.md`

## Summary

这是“一人企业方法论”的 Agent Skill 化版本。它把一人企业从资源盘点到转化闭环的建盘过程拆成 9 个可调用 Skill，其中 `00` 负责总编排，`01-07` 负责线性建盘，`08-09` 用于运营中的资产沉淀和经营复盘。

## Highlights

- 方法论核心目标不是做大团队，而是把个人已有能力组织成轻资产、可验证、可复用的业务系统。
- 线性建盘链路是：资源盘点 → 利基定位 → 价值主张 → 商业模式 → MVP 设计 → 转化闭环。
- 利基定位采用“三环合一”：新杠杆 × 边界变动 × 资源匹配，再用 6 维机会评分筛选。
- MVP 设计强调验证假设而非追求完整产品，成功标准应包含交付边界和反非标能力。
- 转化闭环强调从触达、承接到成交的完整路径，并用表单等机制过滤低质量咨询。
- 资产沉淀和经营复盘是运营期触发模块，不应在建盘早期替代核心链路。

## Extracted Facts

- `opc-orchestrator` 是必装总编排 Skill，用于阶段判断、流程组织和会话进度恢复。
- 资源盘点包含 8 类：经验、人群、能力、关系、渠道、资产、约束、硬性边界。
- 商业模式阶段使用 Lean Canvas，并要求识别最高风险假设。
- MVP 阶段常见产出包括 `mvp-spec.md`、`experiment-plan.md`、`human-ai-split.md`。
- 转化闭环阶段常见产出包括 `conversion-path.md`、`channel-strategy.md`、`content-plan.md`。

## Opinions / Interpretations

- OPC 适合本仓库作为“一人公司知识库 Agent”的经营设计骨架：它能把战略、产品、市场、客户、运营与 Agent 工作流串起来。
- 对本仓库而言，最值得复用的是阶段边界、产出文件清单和“不要跳步”的编排纪律，而不是照搬所有 Skill 实现。
- 当前仓库已有 `knowledge/`、`sources/`、`outputs/`、`agent/` 等目录，天然适合承接 OPC 产物。

## Useful For

- 设计一人公司从能力盘点到首个可验证产品的执行流程。
- 规范未来知识库 Agent 的提问顺序、阶段边界和产出文件。
- 将临时想法转化为可复用的业务资产和复盘机制。

## Follow-up

- 在网络可用时直接克隆或下载 `easychen/opc-methodology` 的 `skills/` 目录，补全每个 Skill 的 `SKILL.md` 细节。
- 基于本仓库业务实际创建 `outputs/opc-doc/` 的首轮建盘产物。
