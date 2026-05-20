---
title: 知识库同步与 FastGPT / OpenAI Provider 指南
type: guide
status: active
tags: [knowledge-base, corpus, web, sync, fastgpt, openai, vector-store]
created: 2026-05-18
updated: 2026-05-20
source: internal-ops
confidence: high
---

# 知识库同步与 FastGPT / OpenAI Provider 指南

## Summary

本指南分两段：

1. `npm run sync:knowledge-corpora` 刷新 `web/` 里的 corpus 配置和本地 metadata。默认公共 corpus provider 是 `fastgpt`，但内容仍以仓库 Markdown 为源头。
2. `npm run knowledge:sync -- --corpus opc-core --provider fastgpt` 把本地 Markdown 上传/更新到 FastGPT dataset，并把本地 metadata 中的 `opc-core` provider 切到 FastGPT。FastGPT 只做检索，最终回答仍由 OpenAI Agents SDK 基于 evidence 生成。
3. `npm run knowledge:sync -- --corpus opc-core --provider openai` 仍保留为 OpenAI Vector Store 实验/直连 OpenAI provider 路径。

这份文档重点区分三件事：本地 corpus 配置、FastGPT dataset 上传、OpenAI Vector Store 上传。当前推荐生产检索路径是 FastGPT provider 加本地 Markdown fallback，不是 OpenAI Vector Store。

## 1. 本地 corpus 配置同步

`sync:knowledge-corpora` 会扫描这些顶层目录中的 Markdown 内容：

- `knowledge`
- `sources`
- `outputs`
- `agent/prompts`

如果某个目录当前没有可发现的 Markdown 文件，它不会进入最终 corpus 配置。

当前 `opc-core` 还会默认排除一个超大转录文件，避免单文件占满 FastGPT 容量：

- `sources/videos/bilibili/dontbesilent-liaozhuanqian/all-transcripts.md`

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
3. 默认 seed 中 `opc-core` 的 provider 是 `fastgpt`。如果已有数据库里是其他 provider，普通 seed 同步不会覆盖已有 provider 状态；需要显式运行 FastGPT provider 同步命令。

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

## 2. FastGPT Dataset 上传与 Provider 同步

FastGPT dataset 仍需要先在 FastGPT 控制台中创建。创建后，把 dataset id 写入 `.env`，脚本会把 `opc-core` 对应的仓库 Markdown 上传到这个 dataset，并把本地 metadata 切到 FastGPT provider。

当前同步语义已经改为“以仓库 Markdown 为源头做文件级增量同步”，不是每次全量重建。脚本会基于 `sourcePath + contentHash(SHA-256)` 判断差异：

- 新文件：上传到 FastGPT
- 内容变更：删除旧 collection，再上传新版本
- 内容未变：跳过，不重复上传
- 本地已删除文件：删除 FastGPT 对应 collection，并清理本地 metadata 记录

如果本地 metadata 里记录的旧 collection id 在 FastGPT 远端已经不存在，脚本会跳过这类脏状态并继续同步，不会因为这一个异常中断整次上传。第一次从 OpenAI 或本地 provider 切换到 FastGPT 时，脚本仍然不会删除 FastGPT 控制台中手工创建但未被本地 metadata 记录的内容。

需要注意的是，当前实现不是事务式回滚：

- 如果同步过程中某个文件上传失败，之前已经成功上传的增量会保留
- 同步会在第一个失败处停止
- 如果这次同步包含“内容变更”的文件，旧 collection 可能已经先删掉，而新版本还没来得及上传完成，因此远端 dataset 会处于“部分更新完成”的状态

这对 MVP 是可接受的，但它不是严格一致性的批处理。

### 环境变量

在 `web/.env` 中配置：

```env
FASTGPT_API_KEY=...
FASTGPT_BASE_URL=https://cloud.fastgpt.cn/api
FASTGPT_OPC_CORE_DATASET_ID=...
FASTGPT_TRAINING_TYPE=chunk
FASTGPT_CHUNK_SIZE=512
```

可选：

```env
FASTGPT_DATASET_ID=
FASTGPT_CHUNK_SPLITTER=
FASTGPT_QA_PROMPT=
FASTGPT_SEARCH_MODE=embedding
FASTGPT_TOKEN_LIMIT=5000
FASTGPT_SIMILARITY=
FASTGPT_USING_RERANK=
FASTGPT_DATASET_IDS=opc-core=dataset_x
```

`FASTGPT_TOKEN_LIMIT` 对应 FastGPT `searchTest.limit`，含义是检索返回内容的 token 预算，不是返回条数。`KnowledgeGateway` 仍会用自己的 `limit` 控制最终 evidence 条数。

`FASTGPT_API_KEY` 需要有 dataset 写入权限。`FASTGPT_OPC_CORE_DATASET_ID` 是当前推荐配置；`FASTGPT_DATASET_ID` 只是没有 corpus-specific id 时的 fallback。

补充说明：

- `FASTGPT_BASE_URL` 如果用 FastGPT 云服务，应该配置成 `https://cloud.fastgpt.cn/api`
- `FASTGPT_DATASET_IDS` 只用于运行时检索 provider 的 corpusId -> datasetId 映射，不用于 `knowledge:sync` 上传脚本
- `knowledge:sync` 上传脚本读取顺序是：`FASTGPT_<CORPUS_ID>_DATASET_ID` -> `FASTGPT_OPC_CORE_DATASET_ID` -> `FASTGPT_DATASET_ID`
- `FASTGPT_DATASET_IDS` 在运行时检索里支持 `opc-core=dataset_x` 和 `opc-core:dataset_x` 两种写法，但文档建议统一用 `=`

### 上传/更新 provider

```powershell
cd web
npm run knowledge:sync -- --corpus opc-core --provider fastgpt
```

成功后会输出类似：

```json
{
  "status": "ok",
  "corpusId": "opc-core",
  "datasetId": "dataset_x",
  "documentsSynced": 123
}
```

`documentsSynced` 表示这次实际发生上传的文件数，不是 corpus 总文件数。未变化而被跳过的文件不会计入这里。

### 容量不足时的表现

如果 FastGPT 返回 `datasetSizeNotEnough`，含义是 dataset 总容量不足，不是“文件数超过上限”。

当前脚本在这种情况下会：

1. 停在当前失败文件
2. 保留这次同步前面已经成功完成的增量上传
3. 不自动回滚之前成功的上传

这意味着：

- 对“只新增少量文件”的场景，容量不足通常只会让新增停在中间，已有可检索内容仍可继续用
- 对“更新已有文件”的场景，如果旧版本已经删掉而新版本没传完，远端 dataset 可能暂时少掉这部分内容

如果需要继续扩容后再同步，直接重新运行同一个命令即可，脚本会再次按差异继续处理。

### 验证 provider 状态

```powershell
node --input-type=module -e "import { DatabaseSync } from 'node:sqlite'; const db = new DatabaseSync('.data/opc-metadata.sqlite'); console.log(db.prepare('SELECT id, provider, status, provider_vector_store_id, provider_vector_store_status, provider_last_synced_at FROM corpora WHERE id = ?').get('opc-core')); db.close();"
```

期望看到：

```text
provider: 'fastgpt'
status: 'ready'
provider_vector_store_id: '<FastGPT dataset id>'
provider_vector_store_status: 'ready'
```

注：字段名仍叫 `provider_vector_store_id` 是历史兼容命名；FastGPT 路径里这里存的是 dataset id。

### 直接检索 smoke

```powershell
npx tsx -e "import { getDefaultMetadataRepository } from './src/metadata/metadata-repository'; import { createFastGPTDatasetClient } from './src/fastgpt/dataset-client'; import { createFastGPTProvider } from './src/knowledge-gateway/fastgpt-provider'; const repo = getDefaultMetadataRepository(); const corpus = repo.getCorpusById('opc-core'); if (!corpus) throw new Error('missing corpus'); const provider = createFastGPTProvider({ client: createFastGPTDatasetClient({ apiKey: process.env.FASTGPT_API_KEY ?? '', baseUrl: process.env.FASTGPT_BASE_URL }) }); const result = await provider.search({ corpus, query: '一人公司如何定价', limit: 3 }); console.log(JSON.stringify({ status: result.status, evidence: result.evidence.map((item) => ({ source: item.source, score: item.score, excerpt: item.excerpt.slice(0, 160) })) }, null, 2)); repo.close();"
```

期望：

- `status` 是 `ok`
- `evidence` 里有 1 条以上结果
- `source` 能帮助定位来源文档；脚本上传时会在 metadata 中写入仓库相对路径

## 3. OpenAI Vector Store 上传与索引

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
