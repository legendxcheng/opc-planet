---
title: Website Core Code Guide
type: guide
status: active
tags: [web, nextjs, workspace, chat, knowledge-gateway, assistant-ui]
created: 2026-05-22
updated: 2026-05-24
source: internal-code-review
confidence: high
---

# OPC Website Core Code Guide

## Summary

`web/` is the active website runtime. The latest architecture is workspace-first:

- `/` and `/workspace` redirect to `/workspace/dashboard`.
- `/chat` is a compatibility redirect to `/workspace/diagnosis`.
- The public chat shell still exists as a reusable component, but it is no longer the homepage.
- Core runtime layers are: Next.js App Router, workspace shell, `assistant-ui` chat, SQLite metadata, `KnowledgeGateway`, and provider adapters.

Canonical knowledge still lives outside `web/` in `knowledge/`, `sources/`, `outputs/`, and `agent/prompts/`. `web/` reads, syncs, searches, and presents that content, but it is not the source of truth for long-term knowledge.

## Current Route Map

```text
/                               -> /workspace/dashboard
/workspace                      -> /workspace/dashboard
/workspace/dashboard            -> dashboard
/workspace/diagnosis            -> authenticated chat workspace
/chat                           -> /workspace/diagnosis?threadId=...
/api/public-chat                -> threadless public answer stream
/api/chat                       -> thread-aware answer stream
/api/chat/threads               -> list/create threads
/api/chat/threads/[threadId]    -> get/patch/delete thread
/api/chat/threads/[threadId]/messages -> thread history
```

There is no visible sign-in/sign-up route in the current tree. The runtime uses `getDefaultChatUser()` and the `default-user` profile as the current identity stub.

## Directory Map

```text
web/
  app/                 App Router pages and API routes
  components/          Shared UI, including assistant-ui primitives
  src/                 Product logic and runtime modules
  scripts/             Sync and maintenance entrypoints
  tests/               Vitest coverage
  .data/               Local SQLite metadata database
```

Main ownership inside `src/`:

- `src/chat/`: public and authenticated chat composition, thread adapters, data-stream helpers, the OPC-only agent catalog, and the OpenAI Agents runtime bridge.
- `src/workspace/`: workspace navigation, shell, header, sidebar state, and placeholder-page reuse.
- `src/metadata/`: SQLite schema, repository, and seed records.
- `src/knowledge-gateway/`: permission-aware retrieval boundary and provider routing.
- `src/openai/` and `src/fastgpt/`: provider clients.
- `src/auth/session.ts`: default-user profile helper.

## Workspace Shell

The workspace shell is the current product frame for all `/workspace/*` pages.

Key files:

- `app/workspace/layout.tsx`
- `src/workspace/workspace-layout.tsx`
- `src/workspace/workspace-sidebar.tsx`
- `src/workspace/workspace-header.tsx`
- `src/workspace/workspace-navigation.ts`
- `src/workspace/placeholder-page.tsx`

Behavior:

- `WorkspaceLayout` wraps every workspace route.
- `workspace-navigation.ts` is the single source of truth for the left nav.
- Sidebar collapse is persisted with Zustand in `workspace-store.ts`.
- `dashboard` and `diagnosis` are the only real workspace pages today.
- `opportunities`, `workshop`, `knowledge`, `assets`, `mentors`, and `account` are placeholder pages built from `PlaceholderPage`.

Current workspace nav:

1. 总控台 -> `/workspace/dashboard`
2. 一人企业诊断 -> `/workspace/diagnosis`
3. 机会雷达 -> `/workspace/opportunities`
4. 方法论工作坊 -> `/workspace/workshop`
5. 知识库 -> `/workspace/knowledge`
6. 资产库 -> `/workspace/assets`
7. 商业智库 -> `/workspace/mentors`
8. 账户与用量 -> `/workspace/account`

## Chat Runtime

The chat UI is split into a reusable public shell and the authenticated workspace shell.

### Public shell

- `src/chat/public-chat-page.tsx` renders `assistant-ui` against `POST /api/public-chat`.
- It is reusable, but the current homepage does not mount it.
- `app/api/public-chat/route.ts` is threadless and does not persist conversations.
- Public requests always use `agentId = opc-public-assistant` and `userId = null`.

### Workspace shell

- `app/workspace/diagnosis/page.tsx` loads the current user, resolves or creates a thread, and renders `AuthenticatedChatPage`.
- `src/chat/authenticated-chat-page.tsx` composes:
  - `AssistantRuntimeProvider`
  - `useRemoteThreadListRuntime(...)`
  - `useDataStreamRuntime({ api: "/api/chat", protocol: "data-stream" })`
  - `MultiAgentChatLayout`
  - `AgentSidebar`
  - `AgentInfoCard`
  - `HistoryPanel`
  - shared `Thread`
- `ChatLocationSync` keeps `?threadId=` in sync with the active thread.
- `useChatThreadListAdapter()` maps assistant-ui thread CRUD to `/api/chat/threads*`.
- `ChatThreadHistoryProvider` loads persisted messages into assistant-ui history.

### OPC Agent Catalog

The left Agent sidebar is driven by `src/chat/opc-agents.ts`.

Current lineup:

1. `OPC 总编排`
2. `OPC 资源盘点`
3. `OPC 利基定位`
4. `OPC 价值主张`
5. `OPC 商业模式与 MVP`
6. `OPC 转化闭环`
7. `OPC 资产沉淀`
8. `OPC 经营复盘`

This catalog is presentation-only; actual reply routing still comes from thread metadata (`agentId`, `selectedPrivateCorpusId`) and the metadata registry.

### Shared thread component

`components/assistant-ui/thread.tsx` is the shared message composer and renderer for both public and workspace chat.

- It keeps linear history only.
- Copy and export-to-Markdown are kept.
- Branching, edit, and regeneration affordances are intentionally absent.
- It renders reasoning, tool groups, tool fallback, markdown, and source citations.

## Message Flow

Public route:

```text
Thread UI
  -> POST /api/public-chat
  -> normalize conversation messages
  -> publicChatServiceWithAgent(...)
  -> publicChatService(...) fallback search
  -> KnowledgeGateway.search(...)
  -> runtime provider (local / fastgpt / openai_vector_store)
  -> citations
  -> assistant-stream response
```

Workspace route:

```text
Thread UI
  -> POST /api/chat
  -> validate threadId
  -> load default-user + thread ownership
  -> persist user message
  -> update thread title / lastMessageAt
  -> publicChatServiceWithAgent(...)
  -> persist assistant message
  -> assistant-stream response
```

`publicChatServiceWithAgent(...)` is the main orchestration point:

- It first runs gateway retrieval to produce fallback evidence.
- If an OpenAI Agents connection exists, it tries `@openai/agents`.
- If the upstream relay returns `Upstream gateway error`, it retries with evidence injected.
- It records `agent_runs` and `agent_run_usage` when the agent path succeeds.
- If the agent path is unavailable or fails, it falls back to the local evidence answer.

## Metadata and Knowledge Layer

`src/metadata/metadata-repository.ts` owns the SQLite schema and repository.

Tables currently in the schema:

- `agents`
- `corpora`
- `agent_corpora`
- `users`
- `chat_threads`
- `chat_messages`
- `documents`
- `ingestion_jobs`
- `agent_runs`
- `agent_run_usage`

Seed data lives in `src/metadata/metadata-seed.ts`:

- `opc-public-assistant`
- `opc-core`

Current seed facts:

- `opc-core` is the public corpus.
- It points at `knowledge/`, `sources/`, `outputs/`, and `agent/prompts/`.
- The seed corpus is configured for `fastgpt`, with local fallback available when the provider is missing or unavailable.

`KnowledgeGateway` is the access-control boundary:

- It rejects empty queries.
- It validates agent existence and status.
- It validates corpus existence, readiness, and ownership.
- It supports public corpora and user-owned private corpora.
- It returns normalized evidence:

```ts
{
  corpusId,
  documentId,
  chunkId,
  title,
  source,
  score,
  excerpt,
}
```

Provider routing is environment-driven:

- `local` -> repo Markdown search
- `fastgpt` -> FastGPT dataset search
- `openai_vector_store` -> OpenAI vector-store search

Public corpora can fall back to local Markdown when external provider access is missing or fails. Private corpora do not fall back locally.

## Config and Ops

Main runtime entrypoints:

- `npm run dev`
- `npm run typecheck`
- `npm test`
- `npm run build`
- `npm run sync:knowledge-corpora`
- `npm run knowledge:sync -- --provider fastgpt`

Useful environment families:

- `OPENAI_AGENTS_*`
- `FASTGPT_*`
- `OPENAI_VECTOR_STORE_*`
- `OPC_METADATA_DB_PATH`

## Current Implementation Notes

- Root layout sets `lang="zh-CN"` and suppresses hydration warnings.
- `/` and `/workspace` are redirect-only entrypoints.
- `dashboard` is a real page; the rest of the workspace modules are placeholders for now.
- `chat/request-messages.ts` extracts the latest user text and normalizes conversation turns.
- `chat/data-stream-response.ts` emits `assistant-stream` responses and source citations.
- `web/components/ui/*` holds shared UI primitives; `web/components/assistant-ui/*` wraps assistant-ui primitives.
- `web/app/globals.css` owns the shell-level layout classes for public chat, authenticated chat, and workspace chrome.

## Working Rule

If you change routes, metadata contracts, or provider behavior, update the relevant tests in `web/tests/` and rerun the affected typecheck/test path before assuming the architecture note is still correct.
