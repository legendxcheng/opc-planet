---
title: 知识库同步指南
type: guide
status: active
tags: [knowledge-base, corpus, web, sync]
created: 2026-05-18
updated: 2026-05-18
source: internal-ops
confidence: high
---

# 知识库同步指南

## Summary

本指南说明如何把当前仓库里的知识目录同步成 `web/` 里的 corpus 配置。同步脚本会以当前仓库内容为准，自动发现可用知识目录，并把结果写回网站工程使用的 metadata seed 和本地数据库。

这不是知识内容本身的迁移，只是把“哪些目录属于知识库”这层配置刷新到网站工程中。

## 同步范围

当前脚本会扫描这些顶层目录中的 Markdown 内容：

- `knowledge`
- `sources`
- `outputs`
- `agent/prompts`

如果某个目录当前没有可发现的 Markdown 文件，它不会进入最终 corpus 配置。

## 运行方式

在仓库根目录执行：

```powershell
cd web
npm run sync:knowledge-corpora
```

脚本会自动读取当前仓库状态，不需要手工维护 corpus 列表。

## 同步后会更新什么

同步会写入两个位置：

- `web/src/metadata/metadata-seed.ts`
- `web/.data/opc-metadata.sqlite`

这意味着：

1. 网站工程里的默认 corpus seed 会刷新。
2. 本地 metadata 数据库里的 corpus 记录也会同步更新。

脚本完成后会输出类似下面的 JSON：

```json
{
  "status": "ok",
  "corpora": [
    {
      "id": "opc-core",
      "name": "OPC 核心知识库",
      "directories": ["knowledge", "sources", "outputs", "agent/prompts"]
    }
  ]
}
```

## 什么时候需要重新同步

在这些场景下应该重新跑一次：

- 新增了知识文档
- 删除了知识文档
- 把知识内容移到新目录
- 想让网站识别新的知识目录
- 刷新 `web/` 里的默认 corpus 配置

## 验证

同步后建议检查三件事：

```powershell
cd web
npm run typecheck
npm test
```

如果只想快速确认同步结果，也可以直接看脚本输出里的 `corpora` 列表，确认目录集合是否符合预期。

## 常见问题

### 同步后没有看到新目录

确认新目录里至少有 Markdown 文件。脚本只会收录实际有内容的目录。

### 同步结果和预期不一致

检查你运行命令时所在的位置，应该从仓库根目录进入 `web/` 后执行同步命令。脚本以当前仓库状态为准，不会读取你脑中的计划目录。

### 数据库文件看起来变了

这是正常的。`web/.data/opc-metadata.sqlite` 是网站工程使用的本地 metadata 数据库，同步时会一起刷新。

## 推荐工作流

以后每次整理完知识库，按这个顺序做：

1. 更新 `knowledge/`、`sources/`、`outputs/` 或 `agent/prompts/`
2. 运行 `cd web && npm run sync:knowledge-corpora`
3. 检查输出的 corpus 列表
4. 如有需要，再跑 `npm run typecheck` 和 `npm test`

