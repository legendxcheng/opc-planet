---
title: OPC 阶段操作手册
type: playbook
status: active
tags: [opc, workflow, operations, playbook]
created: 2026-04-25
updated: 2026-04-25
source: .codex/skills
confidence: high
---

# OPC 阶段操作手册

## Summary

这份手册把 OPC Skills 的执行知识整理成可复用流程。使用时按阶段推进，每一步先确认输入，再按问题顺序收集信息，最后输出文件并更新状态。

## 00 总编排

### Goal

判断用户当前处于哪个 OPC 阶段，恢复历史进度，选择合适 Skill，并防止跳步。

### Use When

- 新会话开始。
- 用户想从零梳理一人企业。
- 用户要求继续上一次 OPC 流程。
- 用户直接跳到某个阶段但缺少上游产物。

### Key Actions

- 读取 `opc-doc/` 或本仓库对应输出目录。
- 判断用户熟悉度：直通模式或教学模式。
- 说明当前阶段、缺失输入和下一步。
- 调用对应阶段 Skill。

### Output

- 当前阶段判断。
- 下一步行动。
- 状态回写。

## 01 资源盘点

### Goal

建立创始人可调用资源的事实底图。

### Categories

- 经验：做过什么，踩过什么坑。
- 人群：熟悉哪些人，理解哪些场景。
- 能力：技能、方法、判断力和执行能力。
- 关系：可信任联系人、合作方、潜在推荐源。
- 渠道：已有账号、社群、私域、线下入口。
- 资产：内容、模板、工具、代码、案例、数据。
- 约束：时间、现金、精力、家庭、地域、合规。
- 硬边界：明确不做、不能做、不愿牺牲的事项。

### Process

- 第一阶段：广泛扫描 8 类资源。
- 第二阶段：对关键资源追问可用部分、使用方式、成本和限制。

### Output

- `inventory.md`
- `scorecard.json`

## 02 利基定位

### Goal

找到最适合一人企业切入的细分市场。

### Framework

- 新杠杆：AI、自动化、内容分发、软件、社群、众包等新能力。
- 边界变动：行业规则、平台、成本结构、客户行为或供需关系变化。
- 独有资源：创始人的经验、人群理解、信任关系、渠道和资产。

### Opportunity Score

候选方向应从至少 6 个维度评估：需求强度、付费意愿、可触达性、资源匹配、差异化、验证成本。

### Output

- `three-ring-analysis.md`
- `candidates.md`
- `target-segment.json`
- `positioning-statement.md`

## 03 价值主张

### Goal

把目标客群的任务、痛点、收益转化成可理解、可比较、可选择的价值表达。

### Framework

- Jobs：客户真正要完成的任务。
- Pains：现有方案中的风险、麻烦、损失和焦虑。
- Gains：客户期待的结果、收益、身份和确定性。
- Pain Relievers：产品如何减少痛点。
- Gain Creators：产品如何创造收益。

### Output

- `value-proposition-canvas.md`
- `messaging.md`
- `segment-vp-matrix.md`

## 04 商业模式设计

### Goal

把价值主张转化成可收费、可交付、可验证的商业模式。

### Key Questions

- 谁是目标客户？
- 最痛的问题是什么？
- 方案如何交付？
- 客户从哪里来？
- 如何收费？
- 成本结构是什么？
- 哪些指标代表进展？
- 不公平优势是什么？
- 最大风险假设是什么？

### Output

- `lean-canvas.md`
- `business-model-canvas-lite.md`
- `risky-assumptions.md`
- `pricing-notes.md`

## 06 MVP 设计

### Goal

设计最小验证路径，优先验证最高风险假设。

### Principles

- MVP 不是最小产品，而是最小有效验证。
- 优先验证付费、触达、交付或效果中风险最高的一项。
- 明确成功标准、失败标准、时间盒和交付边界。

### Output

- `mvp-spec.md`
- `experiment-plan.md`
- `human-ai-split.md`

## 07 转化闭环

### Goal

设计从触达到留资、承接、成交和复访的完整路径。

### Loop

- 触达：内容、社群、私域、推荐、搜索等入口。
- 留资：表单、私信、预约、问卷、低价诊断等机制。
- 承接：筛选、诊断、报价、交付说明。
- 成交：付款、确认边界、开始交付。
- 复访：案例、反馈、推荐、复购或升级。

### Output

- `conversion-path.md`
- `channel-strategy.md`
- `content-plan.md`

## 08 资产沉淀

### Goal

把运营中的重复成果沉淀为复利资产。

### Asset Types

- 内容资产：文章、案例、短视频脚本、FAQ。
- 交付资产：模板、清单、报告结构、SOP。
- 产品资产：工具、自动化脚本、轻量软件。
- 渠道资产：私域池、社群、邮件列表、平台账号。
- 知识资产：方法论、决策记录、复盘库。

### Output

- 资产清单。
- 资产优先级。
- 下一步沉淀动作。

## 09 经营复盘

### Goal

通过轻量指标和瓶颈判断，确定下一周期唯一优先事项。

### Review Questions

- 当前最真实的瓶颈是什么？
- 是触达不足、转化不足、交付过重、复购不足，还是战略选择错误？
- 哪个动作最能改善下一周期？
- 是否需要止损、收缩或换方向？

### Output

- 复盘记录。
- 瓶颈假设。
- 下一周期唯一优先重点。

## Evidence

- `.codex/skills/opc-orchestrator/SKILL.md`
- `.codex/skills/opc-resource-audit/SKILL.md`
- `.codex/skills/opc-niche-positioning/SKILL.md`
- `.codex/skills/opc-value-proposition/SKILL.md`
- `.codex/skills/opc-business-model-design/SKILL.md`
- `.codex/skills/opc-mvp-designer/SKILL.md`
- `.codex/skills/opc-conversion-loop/SKILL.md`
- `.codex/skills/opc-asset-ops/SKILL.md`
- `.codex/skills/opc-dashboard-review/SKILL.md`
