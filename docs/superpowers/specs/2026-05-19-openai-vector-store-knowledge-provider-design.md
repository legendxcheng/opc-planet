---
title: OpenAI Vector Store Knowledge Provider Design
type: design
status: draft
tags: [agent, knowledge-base, openai, vector-store, file-search, retrieval]
created: 2026-05-19
updated: 2026-05-19
source: conversation design; docs/dev-plans/2026-05-13-agent-knowledge-architecture.md; current web implementation
confidence: medium-high
---

# OpenAI Vector Store Knowledge Provider Design

## Summary

OPC Planet should keep `KnowledgeGateway` as the single runtime retrieval boundary and replace the current local Markdown provider with an OpenAI vector store provider. Each business corpus maps to exactly one OpenAI vector store. The source of truth stays under OPC control: public corpora come from repository Markdown/text files, and future private corpora come from OPC-managed storage. OpenAI vector stores are treated as managed retrieval copies, not canonical storage.

The first implementation slice should cover public corpus sync and runtime retrieval for `opc-core`. Private corpus support should be designed into the metadata model now, but full private upload UI and object-storage ingestion should come later.

## Current Baseline

The current public chat path already has the right boundary:

```text
web/app/api/chat/route.ts
  -> publicChatServiceWithAgent(...)
  -> runPublicAgent(...)
  -> KnowledgeGateway.search(...)
  -> local-provider.ts
  -> searchLocalKnowledge(...)
```

Relevant files:

- `web/src/knowledge-gateway/knowledge-gateway.ts`
- `web/src/knowledge-gateway/local-provider.ts`
- `web/src/knowledge-gateway/types.ts`
- `web/src/chat/public-agent.ts`
- `web/src/agents/knowledge-tool.ts`
- `web/src/metadata/metadata-repository.ts`
- `web/src/metadata/metadata-seed.ts`

The target design keeps this shape. The main change is provider implementation and corpus/document metadata, not the public chat API.

## Decision

Use this primary architecture:

```text
KnowledgeGateway
  -> OpenAI Vector Store Provider
      -> OpenAI vector store search
  -> normalized evidence
  -> Codex prompt evidence injection
```

Do not make the model directly call OpenAI `file_search` as the main runtime path in the first slice.

Reasons:

- `KnowledgeGateway` already owns agent/corpus resolution, permission checks, corpus readiness, and normalized evidence.
- Runtime answers should cite OPC source paths or object-storage source refs, not OpenAI internal file ids.
- Private corpus authorization must remain in the application layer, not in prompt behavior.
- Keeping provider replacement behind the gateway preserves future optional provider adapters.

Official OpenAI references:

- Retrieval and vector stores: https://platform.openai.com/docs/guides/retrieval
- File search tool: https://platform.openai.com/docs/guides/tools-file-search
- Vector store files API: https://platform.openai.com/docs/api-reference/vector-stores-files
- Pricing: https://platform.openai.com/pricing

## Ownership Model

OpenAI vector stores are not the source of truth.

Public corpus source of truth:

```text
repository Markdown/text files
  -> sync job
  -> OpenAI files/vector store
```

Private corpus source of truth:

```text
OPC-managed object storage or controlled file storage
  -> extraction/normalization job
  -> sync job
  -> OpenAI files/vector store
```

This matters because OpenAI stores uploaded files and generated retrieval indexes. OPC must still retain source files and metadata so a corpus can be rebuilt, audited, deleted, or migrated.

## Corpus Granularity

Use one OpenAI vector store per corpus.

Examples:

```text
opc-core                 -> vs_opc_core_...
user_123_private_default -> vs_user_123_private_default_...
pricing-advisor-core    -> vs_pricing_advisor_core_...
```

This is cleaner than one global vector store with filters because it makes permission boundaries, deletion, rebuilds, and usage attribution easier to reason about.

## Metadata Model

Extend the current SQLite metadata layer rather than replacing it.

### Corpora

Current `corpora` already stores:

```text
id
name
visibility
owner_type
owner_user_id
provider
status
local_directories_json
quota_bytes
used_bytes
```

Add fields:

```text
provider_vector_store_id TEXT
provider_vector_store_status TEXT
provider_last_synced_at TEXT
provider_sync_error TEXT
```

Provider values:

```text
local
openai_vector_store
```

Keep `local_directories_json` for public corpora even after runtime retrieval moves to OpenAI. For public corpora, this remains the source input for sync jobs.

### Documents

Current `documents` already stores:

```text
id
corpus_id
original_filename
storage_uri
mime_type
byte_size
status
provider_document_id
created_at
updated_at
```

Add fields:

```text
source_of_truth TEXT
source_path TEXT
content_hash TEXT
provider_file_id TEXT
provider_file_status TEXT
provider_last_synced_at TEXT
provider_sync_error TEXT
```

`source_of_truth` values:

```text
repo
object_storage
```

For public corpus files, `source_path` should be a repository-relative path such as `knowledge/strategy/opc/...md`. For private files, it should be an object-storage URI or another stable OPC-owned source reference.

### Ingestion Jobs

Use `ingestion_jobs.job_type` for both extraction and provider sync work.

Recommended job types:

```text
extract_document
sync_to_openai
rebuild_corpus
delete_provider_file
delete_provider_vector_store
```

Job states should remain compact:

```text
queued
running
succeeded
failed
```

## Status Model

Recommended `corpora.status` transitions:

```text
creating -> indexing -> ready
creating -> indexing -> failed
ready -> indexing -> ready
ready -> indexing -> failed
```

Recommended `documents.status` transitions:

```text
uploaded -> extracting -> normalized -> indexing -> indexed
uploaded -> extracting -> failed
uploaded -> indexing -> failed
indexed -> deleted
```

Recommended provider file states:

```text
pending
uploaded
indexing
ready
failed
deleted
```

`KnowledgeGateway` should only retrieve from corpora with `status = ready`.

## Public Corpus Sync

First slice should provide a manual sync command:

```bash
cd web
npm run knowledge:sync -- --corpus opc-core
```

The command should:

1. Load corpus metadata.
2. Confirm `provider = openai_vector_store`.
3. Read allowed source directories from `localDirectories`.
4. Scan `.md` and `.txt` files only.
5. Compute a content hash for each source file.
6. Create a new OpenAI vector store for the corpus rebuild.
7. Upload files to OpenAI.
8. Attach uploaded files to the vector store.
9. Wait for indexing completion.
10. Write `provider_vector_store_id` to `corpora`.
11. Write document rows with `content_hash`, `source_path`, and `provider_file_id`.
12. Mark the corpus `ready` only after indexing succeeds.

Use rebuild-and-swap for the first version:

```text
current vector store remains serving traffic
  -> build new vector store
  -> wait until new store is ready
  -> swap corpora.provider_vector_store_id
  -> mark old store for cleanup
```

This avoids breaking live retrieval during a failed rebuild.

## Private Corpus Design

Private corpus should use the same provider model:

```text
one private corpus -> one OpenAI vector store
```

The first private slice does not need UI, but metadata should support it:

- `visibility = private`
- `owner_type = user`
- `owner_user_id = <user id>`
- `provider = openai_vector_store`
- `provider_vector_store_id = <OpenAI vector store id>`
- documents use `source_of_truth = object_storage`

Authorization remains in `KnowledgeGateway`:

```text
private corpus is searchable only when corpus.owner_user_id == request.userId
```

Private corpora should not use local Markdown fallback because their source files may not exist on the app server.

## Runtime Retrieval

The runtime should keep this flow:

```text
user question
  -> KnowledgeGateway.search(...)
  -> resolve public corpus bindings and selected private corpus
  -> permission and readiness checks
  -> OpenAI vector store provider search
  -> normalized evidence
  -> answer generation with citations
```

Provider creation should move behind a small factory so call sites do not hard-code local retrieval:

```ts
createKnowledgeGateway({
  registry,
  provider: createRuntimeKnowledgeProvider({ repoRoot, env }),
});
```

The factory can choose:

```text
openai_vector_store provider when configured and corpus provider matches
local provider fallback for public local corpora
```

## Evidence Mapping

Keep the current normalized evidence format:

```ts
interface NormalizedKnowledgeEvidence {
  corpusId: string;
  documentId: string;
  chunkId: string;
  title: string;
  source: string;
  score: number;
  excerpt: string;
}
```

OpenAI search results should map into OPC evidence:

```text
corpusId   -> current corpus id
documentId -> local documents.id when available, otherwise provider file id
chunkId    -> provider result id or provider file id plus chunk index
title      -> document title or original filename
source     -> local source_path or storage_uri
score      -> provider score
excerpt    -> provider text
```

The user-facing answer should cite `source`, not OpenAI internal ids.

## Fallback Rules

Use conservative fallback:

```text
OpenAI provider succeeds
  -> use OpenAI evidence

OpenAI provider unavailable and corpus is public with local source directories
  -> fallback to local Markdown search

OpenAI provider unavailable and corpus is private
  -> return provider unavailable or corpus not ready
```

This keeps public chat resilient while avoiding misleading private search behavior.

## Gateway Statuses

Extend `KnowledgeGatewayStatus` with provider-level typed outcomes:

```text
provider_unconfigured
provider_unavailable
provider_error
```

These statuses should represent normal operational outcomes, not thrown exceptions.

Existing statuses stay:

```text
ok
empty_query
access_denied
corpus_not_ready
agent_not_found
corpus_not_found
```

## Usage And Cost Accounting

The current `agent_run_usage` table already has:

```text
search_tool_calls
file_search_tool_calls
estimated_tool_cost_usd
```

Clarify semantics before implementation:

- `search_tool_calls`: application-side knowledge searches through `KnowledgeGateway`
- `file_search_tool_calls`: model-side OpenAI `file_search` tool calls, if used later
- `estimated_tool_cost_usd`: provider search cost estimate, when pricing data is configured

For this design, runtime vector store search is application-side retrieval, not a model-side `file_search` call. Avoid counting it as model-side `file_search`.

## Implementation Phases

### Phase 1: Public OpenAI Provider

Goal: `opc-core` can be manually synced to OpenAI vector store and runtime retrieval can use OpenAI evidence through `KnowledgeGateway`.

Scope:

- Extend metadata types and schema.
- Add `openai_vector_store` provider type.
- Add OpenAI provider module.
- Add provider factory.
- Add public corpus sync command.
- Update `public-agent.ts` and `knowledge-tool.ts` to use the provider factory.
- Keep local fallback for public corpus only.

Validation:

```bash
cd web
npm run knowledge:sync -- --corpus opc-core
npm test
npm run typecheck
npm run build
```

Expected:

- OpenAI vector store returns evidence for `opc-core`.
- Answer citations still use OPC source paths.
- If OpenAI provider is unavailable, public corpus can fall back to local Markdown search.

### Phase 2: Private Corpus Metadata Skeleton

Goal: private corpus records can use the same OpenAI vector store model without a full UI.

Scope:

- Create private corpus metadata APIs or repository methods.
- Create one vector store per private corpus.
- Record `source_of_truth = object_storage`.
- Preserve owner-based access checks in `KnowledgeGateway`.

Validation:

- User A cannot search User B's private corpus.
- Private corpus without ready status is not searchable.
- Private corpus without vector store id returns a typed provider status.

### Phase 3: Incremental Sync And Cost Controls

Goal: reduce rebuild cost and improve operational visibility.

Scope:

- File hash diff.
- Upload only new or changed files.
- Delete provider files for deleted source files.
- Track provider storage estimates where available.
- Estimate vector store search cost when pricing config is present.

Validation:

- Unchanged files are not re-uploaded.
- Deleted files stop appearing in retrieval.
- Failed sync does not switch runtime vector store.
- Usage summaries distinguish model token usage from provider search usage.

## Test Plan

Add tests for:

- metadata schema defaults and new field persistence
- provider result to `NormalizedKnowledgeEvidence` mapping
- public OpenAI provider happy path with mocked OpenAI client
- provider unconfigured status
- public fallback to local provider
- no private fallback to local provider
- access denied for private corpus owned by another user
- sync job writes corpus and document provider ids
- failed rebuild does not switch active vector store id

## Non-Goals For The First Slice

- Full private upload UI
- Object storage integration
- Incremental sync
- Provider-side deletion UI
- Model-side `file_search` tool invocation
- Replacing `KnowledgeGateway`
- Replacing the current public chat route

## Open Questions

- Should old vector stores be deleted immediately after a successful rebuild, or retained for a short rollback window?
- Should public corpus sync be triggered manually only, or later by deployment automation?
- What is the first private corpus quota: 50 MB, 100 MB, or another number?
- Should private corpus have one default corpus per user, or multiple project-level corpora?
- Should source file content be uploaded exactly as Markdown/text, or normalized into generated `.txt` files before upload?

