---
title: 方糖 OPC 技能集网页抽取
source: https://opc-skills.ft07.com/
collected: 2026-04-25
collector: Codex
status: partial-web-extract
confidence: medium
---

# 方糖 OPC 技能集网页抽取

## 抓取说明

- 本地 `Invoke-WebRequest` 受沙箱网络限制，无法直接连接目标站点和 GitHub API。
- 本文件依据可访问的网页检索/打开结果抽取，保留原始结构与关键文本，作为后续整理的可追溯原料。
- 原始目标站点：`https://opc-skills.ft07.com/`
- 关联仓库/方法论：`https://github.com/easychen/opc-methodology`

## 站点定位

- 名称：方糖 OPC 技能集。
- 副标题：《一人企业方法论》的可执行版本。
- 核心描述：9 个 Agent Skill 组成的完整方法论，从资源盘点到转化闭环，帮助把已有能力重新组织成轻资产、可验证、可复用的个人业务系统。

## 方法论流程

- 总体结构：线性阶段确保不跳步、不走弯路；触发阶段在需要时启用。
- 执行顺序：`01 → 07` 线性执行，`08 / 09` 在实际运营中按需触发。
- `00` 是总编排层，用于判断当前阶段与用户模式、组织整体流程、管控阶段边界，并在新会话恢复进度。

## Skill 一览

| 编号 | 名称 | Skill | 类型 | 站点描述 |
| --- | --- | --- | --- | --- |
| 00 | 总编排 | `/opc-orchestrator` | 编排层 | 判断当前阶段与用户模式，组织整体流程，管控阶段边界。每次新会话自动恢复上次进度。 |
| 01 | 资源盘点 | `/opc-resource-audit` | 线性阶段 | 按经验、人群、能力、关系、渠道、资产、约束、硬性边界 8 个类别，确认手上到底有什么。 |
| 02 | 利基定位 | `/opc-niche-positioning` | 线性阶段 | 通过“三环合一”框架发现细分市场：新杠杆 × 边界变动 × 资源匹配，用 6 维机会评分筛选。 |
| 03 | 价值主张 | `/opc-value-proposition` | 线性阶段 | 拆解目标客群的 Jobs / Pains / Gains，生成多个价值主张版本供对比选择。 |
| 04 | 商业模式设计 | `/opc-business-model-design` | 线性阶段 | 拆解 Lean Canvas 核心模块，确定收费结构与收入路径，识别最高风险假设。 |
| 06 | MVP 设计 | `/opc-mvp-designer` | 线性阶段 | 确定最优先验证的假设、最小验证形式、成功标准与交付边界；不追求产品完整度，只追求假设验证。 |
| 07 | 转化闭环 | `/opc-conversion-loop` | 线性阶段 | 设计从触达到承接到成交的完整路径，包括渠道策略、内容触达方式和承接机制。 |
| 08 | 资产沉淀 | `/opc-asset-ops` | 条件触发 | 识别运营中可沉淀的可复用成果，规划资产优先级；支持多次触发，每次带日期标记。 |
| 09 | 经营复盘 | `/opc-dashboard-review` | 条件触发 | 判断当前最真实的瓶颈，确认下一周期唯一优先重点；运营卡住或定期回顾时触发。 |

## 阶段产出文档

| 阶段 | 产出 | 文件名 |
| --- | --- | --- |
| 01 资源盘点 | 8 类资源的完整盘点：经验、人群、能力、关系、渠道、资产、约束、硬性边界。 | `inventory.md`, `scorecard.json` |
| 02 利基定位 | 新杠杆 × 边界变动 × 资源匹配的重叠区分析，识别最强切入点。 | `three-ring-analysis.md` |
| 02 利基定位 | 3 个候选方向的 6 维机会评分对比，含风险点分析和最终选择。 | `candidates.md`, `target-segment.json` |
| 02 利基定位 | 一段话说清楚：为谁、解决什么、为什么你、为什么现在。 | `positioning-statement.md` |
| 03 价值主张 | Jobs / Pains / Gains 完整拆解，以及对应的 Pain Relievers 和 Gain Creators。 | `value-proposition-canvas.md` |
| 03 价值主张 | 3 个候选版本对比，含选择原因和最终确认的双核心型表述。 | `messaging.md`, `segment-vp-matrix.md` |
| 04 商业模式 | 9 个 Lean Canvas 模块，含问题、方案、渠道、收入、关键指标和不公平优势。 | `lean-canvas.md`, `business-model-canvas-lite.md` |
| 04 商业模式 | 需要优先验证的核心假设清单，是 MVP 阶段的验证目标来源。 | `risky-assumptions.md`, `pricing-notes.md` |
| 06 MVP 设计 | 混合版验证路径：1 单校准 + 2 单真实验证，含成功标准和交付边界。 | `mvp-spec.md`, `experiment-plan.md`, `human-ai-split.md` |
| 07 转化闭环 | 私域主路径 + 小红书辅路径的完整转化闭环，含表单承接和成交机制。 | `conversion-path.md`, `channel-strategy.md`, `content-plan.md` |

## 安装与启动信息

- 重要提示：如果不是第一次运行，清空对话目录下的 `opc-doc` 目录，否则会载入上一次的数据。
- 安装总编排：`npx skills add https://github.com/easychen/opc-methodology/skills/opc-orchestrator`
- 安装阶段 Skill：
  - `npx skills add https://github.com/easychen/opc-methodology/skills/opc-resource-audit`
  - `npx skills add https://github.com/easychen/opc-methodology/skills/opc-niche-positioning`
  - `npx skills add https://github.com/easychen/opc-methodology/skills/opc-value-proposition`
  - `npx skills add https://github.com/easychen/opc-methodology/skills/opc-business-model-design`
  - `npx skills add https://github.com/easychen/opc-methodology/skills/opc-mvp-designer`
  - `npx skills add https://github.com/easychen/opc-methodology/skills/opc-conversion-loop`
  - `npx skills add https://github.com/easychen/opc-methodology/skills/opc-asset-ops`
  - `npx skills add https://github.com/easychen/opc-methodology/skills/opc-dashboard-review`
- Claude Code 启动：`/opc-orchestrator`
- Codex 启动：`@opc-orchestrator`
- 单模块示例：`@opc-niche-positioning 分析Todo 产品的利基市场`

## 案例结构摘录

- 案例人物：林夏，29 岁，二线城市室内全案设计师，6 年从业经验，在行业寒冬下从零搭建一人企业。
- 开局校准：确认用户对 OPC 方法论熟悉度，选择“直通模式”或解释模式。
- 资源盘点示例：渠道资源、关系资源、可复用资产、约束与硬性边界。
- 利基定位示例：候选方向包括报价防坑陪跑、自装/清包翻车救火、预算内高颜值平替设计；推荐前端防坑切入、后端承接平替设计。
- 价值主张示例：降风险型、结果型、双核心型；最终选择“双核心型”。
- 商业模式示例：前端报价体检/防坑报告，后端预算内高颜值平替设计包、节点排雷包/施工交底图，渠道为微信私域暗线 + 小红书明线。
- MVP 示例：1 单校准 + 2 单真实验证；成功标准包括单客耗时、拒绝非标需求能力和工作时间边界。
- 转化闭环示例：私域主路径 + 小红书辅路径；用表单承接而非直接私聊，以过滤白嫖并预收集信息。

## 关联方法论文档索引

ContextQMD 显示 `easychen/opc-methodology` 有 1 个版本、29 个页面，包含：

- 《一人企业方法论》V2.1
- 底层逻辑：资产和被动收入
- 产品构建：从零构建软件产品或服务
- 内容池和自动化能力
- 众包能力
- 一人企业的定义
- 优势发现：副产品优势
- 用户池和触达能力
- 风险评控：管理和利用不确定性
- 竞争策略：不竞争策略
- One Person Enterprise Does Not Equal One Person Business
- 思考工具：《一人企业画布》和《一人企业月报》
- 新版方法论概述
- 产品池和支付能力
- 赛道选择：一人企业如何选择赛道
- 搭建一人企业基础设施
- 底层逻辑：滚雪球和链式传播
- 风险评控：从副业开始
- 竞争策略：结构化优势
- 理想的一人企业基础设施
- 底层逻辑：为什么规模化是可能的
- 底层逻辑：为什么以小博大是可能的
