---
title: 知识库同步与 OpenAI Vector Store 上传指南
type: guide
status: active
tags: [knowledge-base, corpus, web, sync, openai, vector-store]
created: 2026-05-18
updated: 2026-05-19
source: internal-ops
confidence: high
---

# 知识库同步与 OpenAI Vector Store 上传指南

## Summary

本指南分两段：

1. `npm run sync:knowledge-corpora` 只刷新 `web/` 里的 corpus 配置和本地 metadata，不会把知识内容上传到 OpenAI。
2. `npm run knowledge:sync -- --corpus opc-core --provider openai` 会把选定 corpus 的源文件上传到 OpenAI Vector Store，交给 OpenAI 建立索引，供后续检索使用。

这份文档重点区分“本地配置同步”和“上传到 OpenAI”两件事。前者只是刷新哪些目录属于知识库；后者才是实际把文件交给 OpenAI 做解析、向量化和索引。

## 1. 本地 corpus 配置同步

`sync:knowledge-corpora` 会扫描这些顶层目录中的 Markdown 内容：

- `knowledge`
- `sources`
- `outputs`
- `agent/prompts`

如果某个目录当前没有可发现的 Markdown 文件，它不会进入最终 corpus 配置。

### 运行方式

在仓库根目录执行：

```powershell
cd web
npm run sync:knowledge-corpora
```

脚本会自动读取当前仓库状态，不需要手工维护 corpus 列表。

### 同步后会更新什么

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

### 什么时候需要重新同步

在这些场景下应该重新跑一次：

- 新增了知识文档
- 删除了知识文档
- 把知识内容移到新目录
- 想让网站识别新的知识目录
- 刷新 `web/` 里的默认 corpus 配置

### 验证

同步后建议检查三件事：

```powershell
cd web
npm run typecheck
npm test
```

如果只想快速确认同步结果，也可以直接看脚本输出里的 `corpora` 列表，确认目录集合是否符合预期。

### 常见问题

#### 同步后没有看到新目录

确认新目录里至少有 Markdown 文件。脚本只会收录实际有内容的目录。

#### 同步结果和预期不一致

检查你运行命令时所在的位置，应该从仓库根目录进入 `web/` 后执行同步命令。脚本以当前仓库状态为准，不会读取你脑中的计划目录。

#### 数据库文件看起来变了

这是正常的。`web/.data/opc-metadata.sqlite` 是网站工程使用的本地 metadata 数据库，同步时会一起刷新。

### 推荐工作流

以后每次整理完知识库，按这个顺序做：

1. 更新 `knowledge/`、`sources/`、`outputs/` 或 `agent/prompts/`
2. 运行 `cd web && npm run sync:knowledge-corpora`
3. 检查输出的 corpus 列表
4. 如有需要，再跑 `npm run typecheck` 和 `npm test`

## 2. OpenAI Vector Store 上传与索引

`knowledge:sync` 才是上传到 OpenAI 的步骤。它会把 `opc-core` 的源文件上传到 OpenAI Files，再 attach 到 vector store，由 OpenAI 完成解析、分块、向量化和索引。

### 环境变量

在 `web/.env` 中配置：

```env
OPENAI_VECTOR_STORE_API_KEY=...
OPENAI_VECTOR_STORE_BASE_URL=https://api.openai.com/v1
```

不要把 vector store 检索复用到 `CODEX_API_KEY` / `CODEX_BASE_URL`。Codex 生成答案和 OpenAI vector store 检索是两条独立通道。

### 推荐测试顺序

先刷新本地 corpus 目录配置：

```powershell
cd web
npm run sync:knowledge-corpora
```

再构建 OpenAI vector store：

```powershell
npm run knowledge:sync -- --corpus opc-core --provider openai
```

成功后会输出类似：

```json
{
  "status": "ok",
  "corpusId": "opc-core",
  "vectorStoreId": "vs_...",
  "documentsSynced": 123
}
```

### 验证 provider 状态

可以用 SQLite 直接检查 metadata：

```powershell
node --input-type=module -e "import { DatabaseSync } from 'node:sqlite'; const db = new DatabaseSync('.data/opc-metadata.sqlite'); console.log(db.prepare('SELECT id, provider, status, provider_vector_store_id, provider_vector_store_status, provider_last_synced_at FROM corpora WHERE id = ?').get('opc-core')); db.close();"
```

期望看到：

```text
provider: 'openai_vector_store'
status: 'ready'
provider_vector_store_id: 'vs_...'
provider_vector_store_status: 'ready'
```

### 验证检索结果

先做直接 provider smoke test，避免 UI 和答案生成混在一起：

```powershell
npx tsx -e "import { getDefaultMetadataRepository } from './src/metadata/metadata-repository'; import { createOpenAIVectorStoreClient } from './src/openai/vector-store-client'; import { createOpenAIVectorStoreProvider } from './src/knowledge-gateway/openai-vector-store-provider'; import { readPublicAgentEnv } from './src/chat/public-agent'; const repoRoot = process.cwd().replace(/\\/g, '/').replace(/\/web$/, ''); const env = readPublicAgentEnv(repoRoot); const repo = getDefaultMetadataRepository(); const corpus = repo.getCorpusById('opc-core'); if (!corpus) throw new Error('missing corpus'); const provider = createOpenAIVectorStoreProvider({ client: createOpenAIVectorStoreClient({ apiKey: env.OPENAI_VECTOR_STORE_API_KEY ?? '', baseUrl: env.OPENAI_VECTOR_STORE_BASE_URL }) }); const result = await provider.search({ corpus, query: '一人公司如何定价', limit: 3 }); console.log(JSON.stringify({ status: result.status, evidence: result.evidence.map((item) => ({ source: item.source, score: item.score, excerpt: item.excerpt.slice(0, 160) })) }, null, 2)); repo.close();"
```

期望：

- `status` 是 `ok`
- `evidence` 里有 1 条以上结果
- `source` 是本仓库路径，而不是 OpenAI 内部 file id

### 在 MVP 页面测试

启动网站：

```powershell
npm run dev
```

打开 `http://localhost:3000`，提问：

```text
一人公司如何定价？
```

期望页面返回答案，并带有 `knowledge/...` 或 `sources/...` 形式的引用路径。

注意：

- OpenAI 这里确实会收到你的知识文件，并维护它自己的索引副本。
- 公共 corpus 设计了本地 fallback。如果 OpenAI 检索失败，页面可能仍然用本地 Markdown 返回结果。
- 要确认 OpenAI provider 本身可用，应优先看上面的直接 provider smoke test。
