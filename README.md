# OPC Planet Knowledge Base

这是一个面向一人公司的知识库仓库。它采用“知识库优先 + 工具辅助”的结构：长期知识以 Markdown 形式沉淀，爬虫和整理代码服务于采集、清洗、归档和未来 Agent 化。

## 核心原则

- 人先能读，机器也能读。
- `knowledge/` 是长期可信知识，不放未经整理的临时材料。
- `inbox/` 可以暂存混乱输入，但要定期清理。
- `sources/` 和 `data/raw/` 保留来源与原始材料，不直接当作结论。
- `automation/` 只放辅助知识生产的代码。
- `agent/` 为未来知识库 Agent 预留提示词、工具、记忆和评测。

## 目录概览

```text
inbox/       临时收集箱
knowledge/   长期知识库
sources/     外部来源和原始资料记录
outputs/     报告、SOP、决策等加工产物
agent/       未来知识库 Agent 的配置与评测
automation/  爬虫、清洗、整理和导出代码
data/        自动化流程产生的数据
templates/   Markdown 模板
docs/        仓库自身说明
config/      配置文件
archive/     过时但保留的内容
```

## 日常工作流

1. 把临时材料放入 `inbox/`。
2. 将来源型内容整理到 `sources/`。
3. 提炼稳定结论到 `knowledge/`。
4. 将可交付结果放入 `outputs/`。
5. 用 `automation/` 中的脚本减少重复整理工作。
6. 为未来 Agent 能力，在 `agent/evals/` 中持续补充问答评测。

## 推荐入口

- 目录说明：`docs/directory-guide.md`
- 命名规范：`docs/naming-conventions.md`
- 知识笔记模板：`templates/knowledge-note.md`
- 决策记录模板：`templates/decision-record.md`
- Agent 评测模板：`templates/agent-eval-case.md`
