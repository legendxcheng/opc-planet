# Naming Conventions

## 文件和目录

- 目录名使用小写短横线：`customer-research/`。
- Markdown 文件使用小写短横线：`pricing-strategy.md`。
- 日期型文件使用 `YYYY-MM-DD-topic.md`：`2026-04-25-market-scan.md`。
- 决策记录使用 `ADR-0001-topic.md`。
- 避免使用空格、中文标点和过长文件名。

## Frontmatter

长期知识笔记建议包含：

```yaml
title:
type: concept | source-note | decision | playbook | report
status: draft | active | archived
tags: []
created:
updated:
source:
confidence: low | medium | high
```

## 状态

- `draft`：草稿，尚未验证或整理完整。
- `active`：当前有效，可被引用。
- `archived`：过时内容，仅保留历史记录。

## 类型

- `concept`：稳定概念、原则、模型。
- `source-note`：来源笔记或资料摘录。
- `decision`：决策记录。
- `playbook`：可重复执行的方法、SOP、清单。
- `report`：面向阅读或交付的综合材料。

## Agent 友好写法

- 每篇笔记开头写 `Summary`，用 1-3 句话说明结论。
- 事实、判断和行动建议尽量分开。
- 重要结论标注来源和置信度。
- 一个文件只解决一个主要问题。
- 标题和小标题尽量使用可检索关键词。
