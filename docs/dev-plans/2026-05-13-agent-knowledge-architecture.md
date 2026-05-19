---
title: 多 Agent 公共与私有知识库架构设计
type: guide
status: draft
tags: [agent, rag, knowledge-base, architecture, openai-agents-sdk]
created: 2026-05-13
updated: 2026-05-19
source: conversation architecture design; current repository structure
confidence: medium-high
---

# 多 Agent 公共与私有知识库架构设计

## Summary

本设计用于未来把 OPC Planet 部署为服务器端多 Agent 知识库服务。核心原则是：OpenAI Agents SDK 只负责推理与工具调用；业务后端负责用户、Agent、权限、额度和知识库组合；原始首版检索建议基于云服务器本地保存的 Markdown 与本地索引，而不是默认依赖第三方托管知识库。

原始第一版推荐采用 `Knowledge Gateway + Local Retriever` 架构：业务层先统一封装本地 Markdown 检索与权限过滤，再为未来外部 provider 预留适配层。当前实现保留了这个 gateway 边界和本地 fallback，并已经把 OpenAI Vector Store 接入为第一个外部检索 provider。

截至 `2026-05-19`，公共聊天 MVP 已经跑通 `KnowledgeGateway.search(...)`，并补上了首个外部 provider：OpenAI Vector Store 作为可切换的检索适配层。也就是说，这份文档里原本写成“未来外部 provider”的部分，已经从概念进入到已实现的 follow-up slice。

首版生产技术栈统一采用 TypeScript / Node.js：网站、API Server、Knowledge Gateway、Local Retriever、OpenAI Agents SDK Runtime 和测试都优先在同一套 TypeScript 工程内实现。当前 Python 原型只作为行为参考和迁移输入，不作为生产运行时保留。这样可以减少双栈维护、部署和类型边界成本，也更适合后续接入 Next.js SaaS 框架。

在首版生产部署上，推荐把本机职责控制在 `Next.js 网站前端 + Node.js API Server + OpenAI Agents SDK Runtime + 轻量本地检索索引`。对 `4核 8G 5M` 云服务器，这种模式可支持 MVP 和低并发场景；但前提是静态资源尽量走 CDN，用户上传优先限制在轻量文本资料，避免应用服务器中转大文件和承担重型 OCR/向量化任务。

对 `2026-05-13` 原始 MVP 来说，边界很明确：一个网页里的单线程公共聊天，后端先通过 `KnowledgeGateway.search(...)` 检索仓库内公开 Markdown，再把 evidence 注入 Codex SDK prompt 生成回复，带引用和失败回退即可。用户认证、私有知识库、上传、完整用量计费和外部 provider 都属于原始 MVP 之后；其中 OpenAI Vector Store provider 已在 `2026-05-19` follow-up 中提前完成。

## MVP Boundary

### In Scope

- `web/` 中的单页公共聊天体验
- `POST /api/chat`
- Codex SDK TypeScript reply runtime for the current public chat path
- `KnowledgeGateway.search(...)`
- 仓库内公开 Markdown / 本地索引检索
- 引用、空查询处理、失败回退
- `typecheck` / `test` / `build` 通过

### Out Of Scope

- 用户注册、登录、鉴权
- 私有知识库
- 上传、抽取、索引任务
- `users` / `documents` / `ingestion_jobs`
- `agent_runs` / `agent_run_usage`
- 多 Agent 编排和权限体系
- 外部知识库 provider（原始 MVP 不含；OpenAI Vector Store 已作为 `2026-05-19` follow-up 完成）
- 向量库、OCR、rerank、大文件管道

注：上面的 MVP 边界记录的是 `2026-05-13` 的首版范围。`2026-05-19` 的 follow-up slice 已经提前实现 OpenAI Vector Store provider 和公共 corpus 上传索引流程，但私有上传、用户 quota、OCR、rerank 和产品化配置 UI 仍然不属于当前 MVP。

## Current Implementation Progress

截至 `2026-05-19`，`web/` 已经覆盖 public chat shell、Codex SDK 回复路径、Knowledge Gateway 基线、第一版数据库元数据层，以及首个 OpenAI Vector Store provider。当前仍不是完整的用户可配置知识库产品：还没有私有上传 UI、用户身份、quota 和产品化 corpus 管理界面；但公共 `opc-core` 已经可以通过 OpenAI Vector Store 托管检索副本运行。

- `web/` 已经是 Next.js App Router + TypeScript 主工程。
- Python 原型中的本地 Markdown 检索行为已经迁移到 `web/src/knowledge/*`，并由 Vitest 覆盖。
- `search_knowledge_base` 风格的工具注册和运行时错误格式化已经迁移到 `web/src/agents/*`。
- 首页已经从占位页升级为基于 `assistant-ui` 的单线程公共聊天界面。
- 稳定路由 `POST /api/chat` 已经存在，且前端通过 `useDataStreamRuntime` 访问它。
- 当前公共聊天回答路径已经具备：
  - mock stream 模式
  - 本地 public corpus 检索模式
  - OpenAI Vector Store public corpus 检索模式
  - Codex SDK 接入路径（`@openai/codex-sdk`）
  - 当 Codex / OpenAI runtime 不可达或超时时，自动回退到本地 public corpus 回答
- 当前 Codex SDK 路径已经可以通过 `.env` / `web/.env` 生效：
  - 生成回答使用 `CODEX_API_KEY` / `CODEX_BASE_URL`
  - Vector Store 检索使用 `OPENAI_VECTOR_STORE_API_KEY` / `OPENAI_VECTOR_STORE_BASE_URL`
  - relay 兼容地址需要以 `/v1` 结尾，因为 Codex SDK / CLI 会在 base URL 后请求 `/responses`
  - 支持 `CODEX_MODEL` 与 `CODEX_MODEL_REASONING_EFFORT`
- 当前 Codex SDK 子进程已经使用隔离的 `CODEX_HOME` 和最小化环境变量，避免本机 Codex CLI 用户 hooks 污染 JSON stdout。
- 当前 `web/` 已经存在数据库支持的公共 metadata 层：`web/src/metadata/metadata-repository.ts`。
- 当前默认 metadata 存储为本地 SQLite：`.data/opc-metadata.sqlite`，可由 `OPC_METADATA_DB_PATH` 覆盖。
- 当前公共 corpus seed 已集中到 `web/src/metadata/metadata-seed.ts`，`web/src/corpora/public-corpora.ts` 只保留为兼容 wrapper。
- 当前公共 Agent seed 也已集中到 `web/src/metadata/metadata-seed.ts`，`web/src/agents/agent-registry.ts` 为兼容 wrapper。
- `KnowledgeGateway.search(...)` 已经成为公共聊天路径的运行时检索入口：
  - `web/src/chat/public-chat-service.ts` 通过 gateway 检索证据并生成 citation。
  - `web/src/chat/public-agent.ts` 先通过 gateway 搜索公共知识，再把标准化 evidence 注入 Codex prompt。
  - `web/src/agents/knowledge-tool.ts` 的 generic tool 返回 gateway result JSON。
  - `web/app/api/chat/route.ts` 传入 `agentId` 和 `userId`，不再直接选择具体 corpus。
- 当前检索 provider 已经从硬编码本地 adapter 改为 runtime provider factory：
  - `web/src/knowledge-gateway/local-provider.ts` 保留为 public fallback。
  - `web/src/knowledge-gateway/openai-vector-store-provider.ts` 是首个外部 provider。
  - `web/src/knowledge-gateway/runtime-provider.ts` 按 corpus provider 和环境变量选择 OpenAI 或本地 fallback。
  - public corpus 在 OpenAI 未配置或失败时可以回退本地 Markdown；private corpus 不做本地 fallback。
- 当前 evidence 已标准化为 `{ corpusId, documentId, chunkId, title, source, score, excerpt }`。
- 当前 metadata SQLite schema 已经覆盖：
  - `agents`
  - `corpora`
  - `agent_corpora`
  - `users`
  - `documents`
  - `ingestion_jobs`
  - `agent_runs`
  - `agent_run_usage`
- 当前 Codex SDK 路径已经接入第一版运行记录：
  - SDK 路径被尝试时会写入 `agent_runs`。
  - SDK 成功返回且能解析 usage 时会写入 `agent_run_usage`。
  - `search_tool_calls` 当前表示本地 gateway evidence 预检索次数，不是 Codex 模型侧 tool call。
  - 当前 cost 字段先写入 `0`，等待后续引入可维护的模型价格表。
- 当前 OpenAI Vector Store 同步路径已经落地：
  - `web/scripts/sync-knowledge-corpora.ts` 同时支持本地 seed sync 和 `--provider openai`。
  - `web/src/metadata/openai-corpus-sync.ts` 会创建 vector store、上传 Markdown 文件、attach provider attributes、等待索引完成，并把 provider state 写回 SQLite。
  - `web/src/openai/vector-store-client.ts` 使用 OpenAI platform REST API，不走模型侧 `file_search` tool。
  - `docs/guide/knowledge-corpus-sync-guide.md` 已明确区分本地 corpus 配置同步和上传到 OpenAI Vector Store。
  - 真实 MVP smoke 已完成：`opc-core` 已同步到一个 OpenAI vector store，`258` 个文档完成 provider sync。
- 当前 `/api/chat` 已通过真实 Codex SDK smoke：服务端返回 HTTP 200、`x-vercel-ai-data-stream: v1`，body 为 Vercel AI data stream，前端 answer text 可见。
- 当前 WebUI 可见性问题已修复：`web/app/globals.css` 不再用全局 `p { color: var(--muted); }` 把 assistant answer 文本压得过浅。
- 当前 private corpus 还没有 UI、上传和真实用户记录，但 metadata/provider 设计已经支持 future private corpus 使用同一 OpenAI Vector Store 模型；gateway 已经有 private owner 权限校验、`access_denied`、`corpus_not_ready` 等 typed status。
- 当前 `web/` 已经合并了基础工程稳定性修复：
  - `.worktrees` TypeScript/Next watcher 边界隔离
  - 根布局 `suppressHydrationWarning`
  - `next typegen` 驱动的稳定 typecheck
- 当前 `web/` 已经验证通过：
  - `npm run typecheck`
  - `npm test`
  - `npm run build`

这意味着本架构文档中的前三个工程里程碑已经完成：TypeScript public-chat MVP 已落地，Knowledge Gateway 边界已落地，公共 agent/corpus metadata 的首版数据库持久化也已落地。`usage-accounting-and-expanded-metadata` 也已经开始进入主线：运行记录与 token usage 的首版持久化已经接入 Codex SDK 路径。随后补上的 OpenAI Vector Store provider 则把“外部检索适配层”从设计变成了可运行实现。下一阶段重点不再是“是否要引入 gateway”或“是否把静态 registry 入库”，而是把知识库配置补齐：上传、文档 ingestion 状态、真实用户身份、quota、可维护成本估算、私有 corpus、以及后续更多 provider 或本地 FTS/BM25 的组合。

## Long-Term Goals

下面这些是长期目标，不是 MVP 必须项。

- 支持多个 Agent，每个 Agent 使用不同的公共知识库组合。
- 支持每个用户上传并长期保存自己的私有知识库。
- 支持每个 Agent 的最终知识组件为：某些公共知识库 + 某个用户私有知识库。
- 对用户私有知识库做容量限制、文件限制、预处理和状态管理。
- 保证用户只能检索自己有权限访问的私有知识库。
- 统计每个用户的模型 token 用量，并支持按用户、Agent、会话和时间窗口汇总成本。
- 在中国大陆访问足够快，并尽量降低项目冷启动阶段的固定服务器成本。
- 保持知识库引擎可替换，避免被单一厂商锁死。

## MVP Non-Goals

- 第一版不自研完整向量数据库、Embedding 调度和文档解析系统。
- 第一版不要求所有知识库引擎能力完全一致。
- 第一版不把 OpenAI Agents SDK 当作知识库权限系统。
- 第一版不让 Agent 通过 prompt 自行决定可访问的数据范围。

## Recommended Architecture

```text
Browser
  -> CDN / Static Asset Cache
  -> Next.js / Node.js API Server
      -> Auth / User / Quota
      -> Agent Registry
      -> Corpus Registry
      -> Upload Manager
          -> Object Storage
      -> Knowledge Gateway
          -> Local Markdown Retriever / Local Search Index
          -> Optional Provider Adapter: Aliyun / FastGPT / Dify / Tencent
      -> OpenAI Agents SDK TypeScript Runtime
          -> tool: search_knowledge
```

### Current Repository Baseline

The repository no longer only contains a Python prototype. As of `2026-05-14`, the first TypeScript production slice already exists in `web/`, and the Python implementation should now be treated mainly as historical reference rather than the active milestone target.

- `automation/pipelines/opc_knowledge_agent.py` already exposes a local `search_knowledge_base` function tool for OpenAI Agents SDK.
- The original prototype searches Markdown under `knowledge/`, `sources/`, `outputs/`, and `agent/prompts/`.
- `automation/README-openai-agents-smoke.md` already documents offline local search and a real SDK call path.
- `tests/automation/pipelines/test_opc_knowledge_agent.py` already covers basic ranked Markdown retrieval and tool registration.
- `web/src/knowledge/*` now contains the migrated TypeScript retrieval baseline.
- `web/tests/knowledge/search-local-knowledge.test.ts` and `web/tests/agents/knowledge-tool.test.ts` already cover the migrated behavior.
- `web/src/chat/*`, `web/src/corpora/public-corpora.ts`, and `web/app/api/chat/route.ts` already provide a public-chat MVP on top of that retrieval baseline.

This changes the milestone sequencing:

1. The “translate retrieval behavior into TypeScript and preserve tests” milestone is done.
2. The first permission-aware `KnowledgeGateway.search(...)` boundary is now implemented in `web/src/knowledge-gateway/*`.
3. The first database-backed metadata slice for `agents`, `corpora`, and `agent_corpora` is now implemented in `web/src/metadata/*`.
4. The first run persistence and token-usage persistence slice is now implemented for Codex SDK calls; the remaining gap is productized upload, ingestion state, quota, pricing summaries, and real user/private-corpus flows.
5. The next retrieval-adjacent upgrade should focus on upload/ingestion state, quota/accounting, and private corpus boundaries before adding external adapters beyond the current OpenAI Vector Store path.

### TypeScript-First Stack Decision

Production code should converge on one TypeScript stack:

- `Next.js App Router + TypeScript` for website, dashboard, API routes, and server actions where appropriate.
- `@openai/agents` for the OpenAI Agents SDK runtime in Node.js.
- `PostgreSQL + Drizzle ORM` for users, agents, corpora, documents, ingestion jobs, agent runs, and usage accounting.
- `Postgres full-text search` for the first production local index when using managed Postgres; `SQLite FTS5` remains acceptable for local/offline prototypes or single-node file-based indexing.
- `Vitest` for unit and integration tests that replace Python unittest coverage for production logic.
- `tsx` for local TypeScript scripts, smoke tests, index rebuild jobs, and one-off automation entrypoints.

The initial production repository layout should be explicit about this boundary:

```text
web/
  app/
  src/
    agents/
    knowledge/
    corpora/
    usage/
    config/
  tests/
```

Python scripts that support non-production knowledge collection, such as existing Bilibili extraction tools, may be migrated later. They should not block the production Agent architecture unless they become part of the live ingestion path.

### Current TypeScript Runtime Slice In `web/`

The current merged `web/` app already maps to part of the intended architecture:

```text
web/
  app/
    page.tsx                  -> public chat homepage
    api/chat/route.ts         -> stable chat entrypoint
  src/
    knowledge/                -> local Markdown retriever
    knowledge-gateway/        -> permission-aware retrieval boundary and provider adapter
    metadata/                 -> SQLite-backed metadata repository and seed data
    agents/                   -> tool descriptors and runtime error shaping
    agents/agent-registry.ts  -> compatibility wrapper over metadata repository
    corpora/                  -> corpus registry plus public wrapper
    chat/                     -> request normalization, mock mode, public agent path
    config/                   -> Next.js worktree/watch safeguards
  tests/
    knowledge/
    agents/
    chat/
    app/
    config/
```

What is implemented today:

- public-only corpus answering
- local Markdown search with corpus-aware directory constraints
- assistant-ui based browser shell
- Codex SDK integration path for the public agent
- gateway evidence, from local fallback or OpenAI Vector Store, injected into the Codex prompt before generation
- graceful fallback to local retrieval when the OpenAI runtime path fails
- SQLite-backed metadata repository for `opc-public-assistant` and `opc-core`
- empty SQLite metadata tables for `users`, `documents`, `ingestion_jobs`, `agent_runs`, and `agent_run_usage`
- first `agent_runs` / `agent_run_usage` persistence for attempted Codex SDK calls
- compatibility registry wrappers that keep existing call sites stable
- `KnowledgeGateway.search(...)` as the single retrieval entrypoint for the public chat runtime
- normalized gateway evidence and typed non-exception outcomes for empty query, denied access, missing corpus, missing agent, and not-ready corpus
- OpenAI Vector Store retrieval as the first external provider behind the gateway
- manual public corpus sync to OpenAI Vector Store, including provider IDs and file-level provider state

What is still missing relative to the target architecture:

- authenticated users
- private corpora
- runtime upload and ingestion flows that populate document metadata tables
- quota enforcement and usage summary queries
- maintained model pricing table for non-zero cost estimates
- persistent local index beyond direct file scan

### First Production Deployment Profile

推荐首版生产环境按以下假设设计：

- 单台 `4核 8G 5M` 云服务器运行 Web/API 层、Agent Runtime 和轻量本地检索索引。
- 首版公共知识主要来自仓库内 Markdown；用户私有知识优先支持 `.md` 与 `.txt`，再逐步扩展到可抽取文本的格式。
- 静态前端资源由 CDN 或对象存储分发，尽量不要全部由源站直接出流量。
- 上传链路优先采用浏览器直传对象存储；应用服务器负责鉴权、签名、状态登记、文本抽取任务和索引更新。
- Metadata DB、对象存储、短信/邮件、日志监控等能力优先使用托管服务；如需自托管，也应保持轻量。

推荐拓扑：

```text
Browser
  -> CDN / Static Asset Cache
  -> Next.js / Node.js API Server + OpenAI Agents SDK TypeScript Runtime
      -> Managed Metadata DB
      -> Object Storage
      -> Local Markdown / Processed Text Store
      -> Local Search Index
      -> OpenAI Vector Store / Optional External Knowledge Provider
      -> OpenAI API
```

### Feasibility Of `4C8G5M`

在不自托管重型知识库组件、且首版仅做轻量文本检索的前提下，`4核 8G` 的 CPU 和内存通常足够支撑：

- 网站前端 SSR/轻量 API
- 鉴权、权限校验、配额校验
- OpenAI Agents SDK TypeScript 编排、工具调用、会话状态桥接
- 轻量异步任务，例如上传登记、文本抽取、索引更新、用量入库

这个配置更适合：

- MVP 或早期生产环境
- 低并发文本问答
- 用户上传频率较低
- 知识源以 Markdown 和轻量文本为主
- 主要成本发生在模型调用和已接入的 OpenAI Vector Store API / storage，而不是自托管重型 RAG 或额外知识库订阅

这个配置不适合与以下组件同机部署：

- Dify 全套自托管组件
- FastGPT 全套自托管组件
- RAGFlow 或其他重型文档解析/向量检索栈
- 大规模 OCR、文件解析、embedding worker
- 语音实时 Agent、转码、图像处理等高 IO/高 CPU 任务

### Why `5M` Bandwidth Is The First Bottleneck

`5 Mbps` 出口带宽理论上约为 `0.625 MB/s`。这意味着：

- 文本型聊天和流式回答通常可接受。
- 多个用户同时打开页面时，如果静态资源全部由源站输出，首屏速度会明显下降。
- 如果上传文件需要先传到应用服务器，再做中转或全文解析，带宽会被快速占满，用户体验会明显恶化。

因此第一版应把带宽优化视为比 CPU 优化更高优先级的问题。

### Responsibility Split

| Layer | Responsibility |
| --- | --- |
| CDN / Static Asset Cache | 分发前端静态资源，降低源站带宽与首屏压力 |
| Next.js / Node.js API Server | 用户认证、Agent 选择、额度校验、上传入口、会话入口 |
| Agent Registry | 记录每个 Agent 的 prompt、模型、可用公共知识库 |
| Corpus Registry | 记录公共/私有知识库、owner、provider、storage/index 引用、状态 |
| Knowledge Gateway | 统一检索接口、权限过滤、本地/外部结果合并、citation 标准化 |
| Local Retriever | 基于 Markdown、抽取文本或本地索引执行检索 |
| Provider Adapter | 外部适配层；当前已接入 OpenAI Vector Store，后续可适配阿里云、FastGPT、Dify、腾讯云 |
| OpenAI Agents SDK TypeScript Runtime | 调用 `search_knowledge` 工具，根据证据生成回答 |
| Usage Accounting | 记录每次 Agent run 的模型 token、工具调用和估算成本 |
| Object Storage | 保存用户上传原文件、抽取文本和处理产物 |
| Metadata DB | 保存业务元数据、权限、配额、预处理任务状态 |

## Core Data Model

### Agent

```text
agents
- id
- name
- status
- prompt_ref
- model
- default_public_corpus_ids
- created_at
- updated_at
```

Agent 不直接存文件路径。它只声明可以使用哪些公共 corpus。

### Corpus

```text
corpora
- id
- name
- visibility: public | private
- owner_type: system | user
- owner_user_id
- provider: tencent | aliyun | dify | fastgpt | local
- provider_dataset_id
- local_storage_ref
- local_index_ref
- status: creating | indexing | ready | failed | archived
- quota_bytes
- used_bytes
- created_at
- updated_at
```

公共知识库和用户私有知识库都统一建模为 corpus。差异通过 `visibility`、`owner_type` 和权限规则表达。

### Agent Corpus Binding

```text
agent_corpora
- agent_id
- corpus_id
- role: public_base | optional_public
- priority
```

不同 Agent 可以绑定不同公共知识库。例如：

```text
opc-orchestrator -> opc-core
pricing-advisor -> opc-core + finance-core
copywriting-advisor -> opc-core + copywriting-core
```

### Document And Ingestion Job

```text
documents
- id
- corpus_id
- original_filename
- storage_uri
- mime_type
- byte_size
- status: uploaded | extracting | normalized | indexed | failed
- provider_document_id
- created_at
- updated_at

ingestion_jobs
- id
- document_id
- corpus_id
- job_type
- status
- error_message
- started_at
- finished_at
```

### Token Usage And Cost Accounting

每次用户问答都必须记录模型 token 用量。统计粒度至少覆盖：

```text
agent_runs
- id
- user_id
- agent_id
- conversation_id
- selected_private_corpus_id
- model
- reasoning_effort
- status: succeeded | failed | cancelled
- started_at
- finished_at

agent_run_usage
- id
- run_id
- user_id
- agent_id
- model
- requests
- input_tokens
- output_tokens
- total_tokens
- cached_input_tokens
- reasoning_tokens
- estimated_model_cost_usd
- search_tool_calls
- file_search_tool_calls
- estimated_tool_cost_usd
- created_at
```

OpenAI Agents SDK run 完成后，应从 TypeScript SDK 返回的 run result / context usage 信息读取用量并写入 `agent_run_usage`。至少保存 `input_tokens`、`output_tokens`、`total_tokens`、`cached_tokens`、`reasoning_tokens` 和 `requests`。如果后续使用 File Search、外部 RAG、rerank 或其他付费工具，工具调用次数和费用应独立记录，不能只依赖模型 token 估算总成本。

用户额度和成本看板应基于 Usage Accounting 汇总，而不是从日志中临时解析。推荐支持这些查询：

```text
- user daily/monthly token usage
- user daily/monthly estimated cost
- agent-level token usage by model
- conversation-level token usage
- high-cost runs for audit
```

第一版可以只做美元估算字段，价格表由后端配置维护。价格表更新时不重写历史 token 记录；如需重新估算成本，基于原始 token 字段重新计算。

## Knowledge Composition Rule

每次问答请求显式传入：

```text
user_id
agent_id
selected_private_corpus_id
question
```

后端解析可检索范围：

```text
allowed_corpora =
  agent.default_public_corpus_ids
  + selected_private_corpus_id if owner_user_id == user_id
```

Agent 只能通过后端提供的 `search_knowledge` 工具检索这些 corpus。私有知识库权限必须在后端和 Knowledge Gateway 校验，不能交给模型或 prompt。

## Upload And Preprocessing Flow

首版默认采用本地知识路径，而不是“上传即进入外部托管知识库”。

```text
1. User requests an upload session
2. API Server validates auth, file size, type and user quota
3. API Server returns a signed upload URL
4. Browser uploads the original file directly to Object Storage
5. Document row is created or confirmed as uploaded
6. Ingestion job is queued
7. Worker extracts or normalizes text into `data/processed/` or another managed text store
8. Local retriever updates search index or searchable text manifest
9. Corpus/document status is updated
10. Only ready corpora are used in retrieval
```

公共 repo corpus 的 OpenAI Vector Store 同步已经补上 provider 上传、`provider_file_id` 和外部索引状态同步逻辑。这里描述的用户上传流程仍未完成：私有文件上传、对象存储、抽取/归一化、quota 和用户级 ingestion job 还需要后续实现。

### Quota Rules

First-version recommended limits:

- Free user total private storage: 50-100 MB
- Single private corpus: 20-50 MB
- Single file: 2-10 MB
- Supported file types first: `.md`, `.txt`
- Optional second batch: `.pdf`, `.docx` only after text extraction quality is acceptable
- Unsupported or failed files remain visible with failed reason, but cannot be searched.

Quota must be checked before upload and again after text extraction if normalized text size expands significantly.

### Bandwidth-Aware Upload Guidance

当源站出口仅为 `5M` 时，上传策略应额外考虑网络瓶颈：

- 默认使用浏览器直传对象存储。
- 单文件上限建议在产品冷启动阶段更保守，优先落在 `2-10 MB`。
- 如果服务器需要参与文本抽取，前端应明确告知“上传中”和“知识库处理中”是两个不同阶段。
- 大文件批量导入、媒体类文件和需要 OCR 的文件应延后到更高带宽或独立 worker 阶段。

## Retrieval Flow

```text
User question
  -> OpenAI Agents SDK TypeScript Runtime
      -> search_knowledge(query)
          -> Knowledge Gateway
              -> resolve allowed corpora
              -> search local Markdown / processed text / local index
              -> optionally call provider retrieval APIs
              -> merge results
              -> dedupe by document/chunk
              -> optional rerank
              -> return normalized evidence
      -> final answer with citations
```

After the Agent run completes, the API Server records usage:

```text
OpenAI Agents SDK run usage
  -> Usage Accounting
      -> persist per-run token usage
      -> estimate model cost by configured pricing table
      -> aggregate by user_id / agent_id / conversation_id
      -> enforce quota or trigger alerts when needed
```

Normalized evidence format:

```json
[
  {
    "corpus_id": "opc-core",
    "document_id": "doc_123",
    "chunk_id": "chunk_456",
    "title": "OPC Methodology Overview",
    "source": "knowledge/strategy/opc/opc-methodology-overview.md",
    "score": 0.82,
    "excerpt": "..."
  }
]
```

The answer layer should cite normalized `source` plus document title. It should not expose raw provider internals unless needed for debugging.

### Local Retrieval Evolution Path

To keep scope under control, local retrieval should evolve in stages:

1. Stage 0: repository-wide Markdown scan with basic scoring.
2. Stage 1: corpus-aware filtering, standardized citations, and permission-aware result shaping.
3. Stage 2: lightweight local index, such as SQLite FTS5 or BM25, with incremental rebuild support.
4. Stage 3: optional rerank layer for top-K local results if benchmark queries show recall is acceptable but ordering is weak.
5. Stage 4: external provider adapter when local retrieval quality, file-format complexity, or corpus volume makes it necessary.

The original recommendation was to move from Stage 0 to Stage 2 before adding a managed external knowledge-base dependency. The `2026-05-19` follow-up deliberately pulled one external provider forward for MVP validation: OpenAI Vector Store is now available behind `KnowledgeGateway`, while local retrieval remains the public fallback path.

## Provider Strategy

### Original Recommended First Choice: Local Markdown Retrieval

The original first production path for this project was local Markdown retrieval on the application server. This still matters as the public fallback path because it matches the current repository shape, keeps the canonical knowledge in human-readable files, and avoids making every retrieval depend on managed knowledge-base capacity, vector storage, or provider-side retrieval calls.

This path is especially suitable when:

- most public knowledge already lives in repository Markdown
- private knowledge volume is still small
- acceptable quality can be achieved with keyword search, BM25, SQLite FTS5, or another lightweight local index
- the main goal is validating product flow rather than maximizing semantic retrieval quality on day one

### Why Not Default To OpenAI File Search First

OpenAI File Search is a valid managed option, but it should not be the default first step for this project. It requires uploading files into OpenAI-managed vector stores and adds storage plus tool-call costs on top of model token costs. As of `2026-05-13`, the official pricing shows `File search` at `$2.50 / 1,000 calls` and `Vector storage` at `$0.10 / GB / day` after the first `1 GB`.

The implemented `2026-05-19` path does not use model-side OpenAI `file_search` as the main retrieval path. It uploads files to OpenAI Vector Store, calls the Vector Store search API from the application layer, normalizes evidence in `KnowledgeGateway`, and then injects evidence into the Codex prompt.

Official references:

- https://developers.openai.com/api/docs/guides/tools-file-search
- https://developers.openai.com/api/docs/pricing

### Additional External Upgrade Option: Aliyun Bailian Knowledge Base

Aliyun Bailian remains a plausible additional external adapter if local retrieval plus OpenAI Vector Store becomes insufficient and a provider-neutral gateway is already in place. It has knowledge-base APIs and retrieval APIs, but its managed knowledge-base model is not free-form pure pay-as-you-go for arbitrary long-tail private corpora. It is better treated as a second-stage managed engine for selected corpora than as the default base layer for every user corpus.

Official references:

- https://help.aliyun.com/zh/model-studio/rag-knowledge-base-api-guide
- https://help.aliyun.com/zh/model-studio/api-bailian-2023-12-29-retrieve
- https://help.aliyun.com/zh/model-studio/billing-for-knowledge-base

### FastGPT Cloud

FastGPT Cloud is a good shortcut if the main priority becomes fast delivery, built-in management UI, and lower development effort. It is more plan-based than granular usage-based, so it is often better as a product acceleration option than as the foundational low-fixed-cost retrieval layer.

Official references:

- https://fastgpt.io/zh/price
- https://doc.fastgpt.io/en/openapi

### Dify

Dify is useful when the product needs a mature workflow UI, knowledge-base console, and integrated app platform. It should be treated as an external platform choice rather than as the default storage and retrieval substrate for this repository.

Official references:

- https://dify.ai/pricing
- https://docs.dify.ai/

### Tencent Cloud ADP Knowledge Base

Tencent Cloud ADP knowledge base should not be treated as the default first external adapter for this architecture. The current product shape is closer to an application-centric managed platform with subscription-style billing than to a low-fixed-cost, corpus-composable retrieval substrate for many user private corpora.

Official references:

- https://cloud.tencent.com/document/product/1759/127342
- https://cloud.tencent.com/document/product/1759/105105

### Deployment Rule For This Project

If the first production machine is only `4核 8G 5M`, then Dify, FastGPT, RAGFlow and similar platforms should be treated as external services or deployed on separate infrastructure. The application server for OPC Planet should remain thin and stateless enough to scale independently later.

## Why Use A Knowledge Gateway

The Knowledge Gateway avoids coupling product logic to either a local retriever implementation or any external provider.

It owns:

- user and corpus permission checks
- agent-to-public-corpus resolution
- selected private corpus validation
- local path and local index resolution
- provider selection
- provider API retries and timeout handling
- result normalization
- citation formatting
- provider failover or migration later

The OpenAI Agents SDK TypeScript runtime only sees a narrow tool surface:

```ts
const searchKnowledge = tool({
  name: "search_knowledge",
  description: "Search allowed public and private knowledge corpora.",
  parameters: z.object({
    query: z.string(),
  }),
  execute: async ({ query }, context) => {
    return knowledgeGateway.search({
      userId: context.userId,
      agentId: context.agentId,
      privateCorpusId: context.privateCorpusId,
      query,
    });
  },
});
```

## Public Corpus Layout For This Repository

Current repository content can be split into public corpora:

```text
opc-core
  - knowledge/strategy/opc/
  - knowledge/operations/opc/
  - sources/skill-sources/opc-methodology/

opc-strategy
  - knowledge/strategy/
  - outputs/briefs/

opc-product-and-market
  - knowledge/products/
  - knowledge/market/
  - outputs/reports/

opc-content-and-sales
  - knowledge/operations/
  - knowledge/customers/
  - sources/videos/bilibili/
```

These are logical corpora. Their actual mapping may point to local directories, local index segments, or provider dataset IDs, and should be stored in the Metadata DB or local config rather than hard-coded into Agent prompts.

Current implementation note:

- The merged runtime currently uses a smaller seeded public slice in `web/src/metadata/metadata-seed.ts`:
  - `knowledge/strategy/opc`
  - `knowledge/strategy`
  - `knowledge/finance`
  - `knowledge/operations`
  - `knowledge/products`
- `web/src/metadata/metadata-repository.ts` persists that seed into SQLite tables and exposes read APIs for runtime use.
- The same metadata repository now also creates `users`, `documents`, `ingestion_jobs`, `agent_runs`, and `agent_run_usage` tables.
- `web/src/corpora/corpus-registry.ts` and `web/src/agents/agent-registry.ts` are now compatibility wrappers over that repository.
- `web/src/corpora/public-corpora.ts` remains a compatibility wrapper so older callers can still use `{ id, name, directories }`.

This is acceptable for the current public chat MVP. The next architecture step should exercise the new metadata tables through real upload, ingestion, quota, and usage-summary flows while keeping `/api/chat` and `KnowledgeGateway.search(...)` stable.

## First-Version Implementation Plan

### Phase A: Already Completed In `web/`

1. Create the TypeScript production workspace in `web/`, using Next.js App Router and a typed test setup.
2. Install and validate `@openai/agents`, `zod`, `vitest`, and the current frontend/runtime dependencies needed for the public chat MVP.
3. Port `automation/pipelines/opc_knowledge_agent.py` behavior into TypeScript as a local Markdown retriever module.
4. Port the core ranked retrieval and tool registration tests into Vitest.
5. Move repository-wide path selection into explicit public corpus definitions for the current MVP slice.
6. Add a stable `POST /api/chat` path and a browser-facing public assistant UI.

### Phase B: Knowledge Gateway Boundary

Completed in the 2026-05-17 gateway migration:

1. Create static corpus registry config for public corpora and future private-corpus-ready metadata.
2. Add static agent metadata for the public assistant.
3. Implement `KnowledgeGateway.search(...)` with the TypeScript local Markdown retriever as provider `local`.
4. Refactor `web/app/api/chat/route.ts`, `web/src/chat/public-chat-service.ts`, `web/src/chat/public-agent.ts`, and `web/src/agents/knowledge-tool.ts` so they call the gateway, not corpus-specific retrieval helpers directly.
5. Standardize normalized evidence output, citations, and corpus-level permission filtering behind the gateway boundary.
6. Add unit coverage for:
   - public corpus registry
   - public assistant registry
   - local provider evidence normalization
   - public + selected private corpus resolution
   - private corpus access denied
   - corpus not ready
   - empty query

### Phase C: Metadata Layer

Completed in the 2026-05-18 metadata migration:

1. Introduce `web/src/metadata/*` as a server-side metadata boundary.
2. Add SQLite-backed persistence for default public `agents`, `corpora`, and `agent_corpora`.
3. Keep `web/src/agents/agent-registry.ts` and `web/src/corpora/corpus-registry.ts` as compatibility wrappers so existing runtime call sites remain stable.
4. Keep `KnowledgeGateway.search(...)` and `/api/chat` behavior unchanged while swapping metadata reads away from in-memory arrays.
5. Add regression coverage for:
   - default public metadata seed
   - reopening the same SQLite file without duplicate seed rows
   - defensive copies from repository list/get APIs

First follow-up slice after Phase C:

1. `users`, `documents`, `ingestion_jobs`, `agent_runs`, and `agent_run_usage` tables now exist in the SQLite metadata repository.
2. The Codex SDK path now records `agent_runs` rows, and successful SDK runs record token counts in `agent_run_usage` when usage can be parsed.
3. The public chat route can now call Codex SDK with `.env` configured `CODEX_API_KEY` / `CODEX_BASE_URL` values, while OpenAI Vector Store retrieval uses separate `OPENAI_VECTOR_STORE_API_KEY` / `OPENAI_VECTOR_STORE_BASE_URL` values. The route streams the generated answer back to the WebUI.

Still remaining after this first follow-up slice:

1. Connect real upload / ingestion flows to `documents` and `ingestion_jobs`.
2. Add user identity, quota enforcement, usage summaries, and a maintained pricing table for cost estimates.
3. Replace the current seeded public Markdown corpus configuration with a product-facing knowledge-base configuration path.
4. Add local FTS/BM25 or another persistent local index when benchmark queries show the direct file scan is not enough.
5. Add eval cases for:
   - public-only answer
   - public + private answer
   - private corpus access denied
   - private corpus not ready
   - uploaded document too large
   - local index returns the same or better top results than naive directory scan for key benchmark queries
   - per-user token usage is recorded after a successful Agent run
   - failed Agent run records status and any available partial usage

### Phase D: Retrieval And Provider Upgrades

1. Upgrade local retrieval from directory scan to Postgres full-text search or another lightweight index, and store index artifacts outside canonical knowledge directories.
2. Add a provider adapter interface:

```text
create_corpus
upload_document
get_document_status
retrieve
delete_document
delete_corpus
```

3. Keep OpenAI Agents SDK TypeScript runtime thin: continue calling `KnowledgeGateway.search` and record run usage after each run.
4. Completed on `2026-05-19`: the first external adapter is now implemented as OpenAI Vector Store retrieval, with manual corpus sync and runtime provider selection in `web/`. Additional external adapters, if needed later, should still reuse this interface. Future external test priority should be:
   - Aliyun Bailian
   - FastGPT Cloud
   - Dify
   - Tencent Cloud ADP

## Operational Risks

| Risk | Mitigation |
| --- | --- |
| Provider lock-in | Use Knowledge Gateway and adapter interface |
| Private data leakage | Permission check before every retrieval; never trust prompt |
| Cost spike from uploads | Quota before upload, file type limits, ingestion job limits |
| Cost spike from model usage | Per-user token accounting, monthly caps, high-cost run alerts |
| `5M` bandwidth saturation | Use CDN for static assets; use browser direct upload; avoid large-file relay through API Server |
| Retrieval misses semantic matches | Start with benchmark queries; keep local fallback; upgrade local FTS/BM25, tune OpenAI Vector Store sync/search, or add rerank/additional provider only when needed |
| Single-server overload from self-hosted RAG | Keep Dify/FastGPT/RAGFlow off the MVP application server |
| Retrieval quality inconsistent across providers | Normalize evidence format and keep eval set |
| Upload says ready but retrieval misses content | Store ingestion states and index versions; add smoke retrieval after indexing |
| Provider outage | Return graceful "knowledge search unavailable" error; keep adapter-level retry |

## Open Questions

- What benchmark query set should define “local retrieval is good enough” for the first release?
- What is the first user quota tier: 50 MB, 100 MB, or another number?
- Should users have exactly one private corpus by default, or multiple project-level corpora?
- Should private corpus deletion be immediate, soft-deleted, or delayed for recovery?
- Should public corpora be rebuilt from this Git repository automatically on each release?
- What are the first per-user monthly token and estimated-cost limits for each plan tier?
- At what private corpus volume or retrieval failure rate should the system introduce additional external providers beyond OpenAI Vector Store?
- At what traffic or upload threshold should the application server be upgraded from `5M` to `10M+` bandwidth?

## Post-MVP Next Step

Do not spend the next iteration redoing the TypeScript foundation work. That layer already exists in `web/`.

Do not spend the next iteration rebuilding the provider-neutral `Knowledge Gateway` boundary either. That boundary now exists in `web/src/knowledge-gateway/*`, the public chat runtime is already using it, and the first external retrieval adapter is now in place.

The recommended next implementation slice is `upload-ingestion-and-quota-boundaries`:

1. connect upload registration to `documents`
2. connect extraction / indexing state to `ingestion_jobs`
3. add user identity and quota checks before upload or private corpus selection
4. add usage summary queries and a maintained model-pricing table for cost estimates
5. only after usage and document-ingestion metadata boundaries are exercised by runtime code, invest in private uploads, larger local indexes, or additional external knowledge provider adapters beyond the OpenAI Vector Store path

## Acceptance Checklist For Current Gateway Slice

Use this checklist to accept the 2026-05-17 Knowledge Gateway migration.

### Code-Level Acceptance

Run these from the repository root:

```powershell
cd web
npm run typecheck
npm test
npm run build
```

Expected:

- `npm run typecheck` exits 0 after `next typegen`.
- `npm test` exits 0; current expected coverage is 21 test files and 72 tests.
- `npm run build` exits 0 and includes the dynamic `/api/chat` route in the Next.js build output.

Run this direct-import guard:

```powershell
rg -n "createLocalKnowledgeProvider" src/chat src/agents app
```

Expected:

- No matches. Runtime chat and agent code should not hard-code the local Markdown provider directly.

Inspect these files:

- `web/src/knowledge-gateway/knowledge-gateway.ts`
- `web/src/knowledge-gateway/local-provider.ts`
- `web/src/agents/agent-registry.ts`
- `web/src/corpora/corpus-registry.ts`
- `web/app/api/chat/route.ts`

Expected:

- `KnowledgeGateway.search(...)` returns typed statuses rather than throwing for normal outcomes.
- Evidence includes `corpusId`, `documentId`, `chunkId`, `title`, `source`, `score`, and `excerpt`.
- `/api/chat` passes `agentId: "opc-public-assistant"` and `userId: null` into the service.

### Browser Smoke Acceptance

Run:

```powershell
cd web
npm run dev -- --port 3026
```

Open `http://localhost:3026` and ask:

```text
How should a one-person company think about pricing?
```

Expected:

- The home page remains a single centered assistant thread.
- No sidebar or history UI appears.
- The request goes to `POST /api/chat`.
- With `CODEX_API_KEY` unset, the answer uses the evidence fallback path rather than Codex generation.
- With `CODEX_API_KEY` and `CODEX_BASE_URL` pointing at a Responses-compatible `/v1` endpoint, the answer is generated through Codex SDK.
- Vector Store retrieval is controlled separately by `OPENAI_VECTOR_STORE_API_KEY`, `OPENAI_VECTOR_STORE_BASE_URL`, and corpus metadata provider state.
- Server logs should not contain `Codex SDK 调用失败`.
- The WebUI should visibly render the assistant answer text.
- The response is not the forced mock answer unless `PUBLIC_CHAT_FORCE_MOCK=1` is set.
- The streamed answer includes evidence-backed content and citations.

Optional direct route smoke:

```powershell
$body = @{
  messages = @(
    @{
      role = "user"
      content = @(
        @{
          type = "text"
          text = "How should a one-person company think about pricing?"
        }
      )
    }
  )
} | ConvertTo-Json -Depth 8

Invoke-WebRequest -Uri "http://localhost:3026/api/chat" -Method POST -ContentType "application/json" -Body $body
```

Expected:

- HTTP status is 200.
- Response header `x-vercel-ai-data-stream` is `v1`.
- With Codex credentials configured, response body contains Vercel AI data-stream frames for a Codex-generated answer.
- Without Codex credentials configured, response body contains the local-evidence fallback answer path.
- Response body must not contain a framework stack trace.

### Known Non-Acceptance Items

Do not block this gateway slice on these items; they are explicitly next-phase work:

- real authenticated users
- real private corpus upload UI
- product-facing knowledge-base configuration and corpus selection UI
- upload / extraction / indexing flows that populate `documents` and `ingestion_jobs`
- quota enforcement and usage summary queries
- maintained model pricing table for non-zero cost estimates
- local FTS/BM25 index
- additional external provider adapters beyond the OpenAI Vector Store path
