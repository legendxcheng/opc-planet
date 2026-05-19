# OpenAI Vector Store Provider Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the public runtime knowledge provider path with an OpenAI vector store capable provider while keeping `KnowledgeGateway` as the application retrieval boundary and preserving local fallback for public corpora.

**Architecture:** Extend the existing SQLite metadata layer with OpenAI vector store/file fields, add a dependency-free OpenAI platform client using `fetch`, implement an OpenAI vector store provider plus a runtime provider factory, and upgrade the existing knowledge corpus sync script into a manual OpenAI sync entrypoint for `opc-core`. The first slice uses raw OpenAI REST endpoints so no new package install is required.

**Tech Stack:** TypeScript, Node.js 22 `fetch`/`FormData`, Node.js `node:sqlite`, Vitest, Next.js App Router, existing `KnowledgeGateway`

---

## Source Spec

Design document:

- `docs/superpowers/specs/2026-05-19-openai-vector-store-knowledge-provider-design.md`

Official OpenAI docs used:

- Retrieval/vector store search: https://platform.openai.com/docs/guides/retrieval
- Vector stores API: https://platform.openai.com/docs/api-reference/vector-stores
- Vector store files API: https://platform.openai.com/docs/api-reference/vector-stores-files
- Files API: https://platform.openai.com/docs/api-reference/files

## Environment Decisions

Use these environment variables:

```text
OPENAI_VECTOR_STORE_API_KEY
OPENAI_VECTOR_STORE_BASE_URL
```

`OPENAI_VECTOR_STORE_BASE_URL` is optional and defaults to `https://api.openai.com/v1`.

Do not use `CODEX_API_KEY` or `CODEX_BASE_URL` for vector store calls. The Codex path may point at a Responses-compatible relay, while vector store management/search requires the platform API surface. Do not use generic `OPENAI_API_KEY` as a shared fallback.

## File Structure

Create:

- `web/src/openai/vector-store-client.ts`
  - Small raw REST client for OpenAI files, vector stores, vector store files, and vector store search.
- `web/src/knowledge-gateway/openai-vector-store-provider.ts`
  - Maps OpenAI search results into `NormalizedKnowledgeEvidence`.
- `web/src/knowledge-gateway/runtime-provider.ts`
  - Chooses OpenAI provider for `openai_vector_store` corpora and public local fallback when OpenAI is unavailable.
- `web/src/metadata/openai-corpus-sync.ts`
  - Rebuild-and-swap sync workflow for public repository corpora.
- `web/tests/openai/vector-store-client.test.ts`
- `web/tests/knowledge-gateway/openai-vector-store-provider.test.ts`
- `web/tests/knowledge-gateway/runtime-provider.test.ts`
- `web/tests/metadata/openai-corpus-sync.test.ts`

Modify:

- `web/package.json`
  - Add `knowledge:sync` script while preserving `sync:knowledge-corpora`.
- `web/scripts/sync-knowledge-corpora.ts`
  - Route `--provider openai` / `--corpus opc-core` into the OpenAI sync workflow.
- `web/src/metadata/types.ts`
  - Add OpenAI provider metadata fields.
- `web/src/metadata/metadata-repository.ts`
  - Add schema columns, migration guards, row mapping, update/upsert methods needed by sync.
- `web/src/metadata/metadata-seed.ts`
  - Keep default provider `local` for offline-safe initial boot unless `knowledge:sync` updates the database.
- `web/src/metadata/knowledge-corpus-sync.ts`
  - Preserve seed sync behavior while carrying new nullable fields.
- `web/src/knowledge-gateway/types.ts`
  - Add provider-level statuses and provider search result shape.
- `web/src/knowledge-gateway/local-provider.ts`
  - Return provider result objects instead of raw evidence arrays.
- `web/src/knowledge-gateway/knowledge-gateway.ts`
  - Propagate provider statuses and keep normalized evidence sorting/dedupe.
- `web/src/knowledge-gateway/index.ts`
  - Export the new provider and factory.
- `web/src/chat/public-chat-service.ts`
  - Use runtime provider factory instead of hard-coded local provider.
- `web/src/chat/public-agent.ts`
  - Use runtime provider factory for pre-retrieval evidence.
- `web/src/agents/knowledge-tool.ts`
  - Use runtime provider factory.
- Existing focused tests under `web/tests/metadata`, `web/tests/knowledge-gateway`, `web/tests/chat`, and `web/tests/agents`.

## Chunk 1: Metadata Fields

### Task 1: Extend Metadata Types

**Files:**

- Modify: `web/src/metadata/types.ts`
- Modify: `web/src/metadata/metadata-seed.ts`
- Test: existing TypeScript typecheck

- [ ] **Step 1: Update `CorpusProvider`**

Change:

```ts
export type CorpusProvider = "local";
```

to:

```ts
export type CorpusProvider = "local" | "openai_vector_store";
```

- [ ] **Step 2: Add corpus provider fields**

Add nullable fields to `CorpusRecord`:

```ts
providerVectorStoreId: string | null;
providerVectorStoreStatus: "pending" | "indexing" | "ready" | "failed" | null;
providerLastSyncedAt: string | null;
providerSyncError: string | null;
```

- [ ] **Step 3: Add document provider fields**

Add:

```ts
export type DocumentSourceOfTruth = "repo" | "object_storage";
export type ProviderFileStatus =
  | "pending"
  | "uploaded"
  | "indexing"
  | "ready"
  | "failed"
  | "deleted";
```

Extend `DocumentRecord` with:

```ts
sourceOfTruth: DocumentSourceOfTruth;
sourcePath: string | null;
contentHash: string | null;
providerFileId: string | null;
providerFileStatus: ProviderFileStatus | null;
providerLastSyncedAt: string | null;
providerSyncError: string | null;
```

- [ ] **Step 4: Update seed records**

In `web/src/metadata/metadata-seed.ts`, keep `opc-core` as:

```ts
provider: "local",
providerVectorStoreId: null,
providerVectorStoreStatus: null,
providerLastSyncedAt: null,
providerSyncError: null,
```

- [ ] **Step 5: Run typecheck**

Run:

```powershell
cd web
npm run typecheck
```

Expected: FAIL until repository mapping is updated in Task 2.

### Task 2: Extend SQLite Metadata Repository

**Files:**

- Modify: `web/src/metadata/metadata-repository.ts`
- Modify: `web/src/metadata/knowledge-corpus-sync.ts`
- Test: `web/tests/metadata/metadata-repository.test.ts`
- Test: `web/tests/metadata/knowledge-corpus-sync.test.ts`

- [ ] **Step 1: Add failing metadata tests**

Add assertions that a fresh repository exposes the new nullable corpus fields:

```ts
expect(repository.getCorpusById("opc-core")).toMatchObject({
  providerVectorStoreId: null,
  providerVectorStoreStatus: null,
  providerLastSyncedAt: null,
  providerSyncError: null,
});
```

Add a document insert/read test that verifies the new document fields persist.

- [ ] **Step 2: Add schema columns**

Add columns to `corpora`:

```sql
provider_vector_store_id TEXT,
provider_vector_store_status TEXT,
provider_last_synced_at TEXT,
provider_sync_error TEXT
```

Add columns to `documents`:

```sql
source_of_truth TEXT NOT NULL DEFAULT 'repo',
source_path TEXT,
content_hash TEXT,
provider_file_id TEXT,
provider_file_status TEXT,
provider_last_synced_at TEXT,
provider_sync_error TEXT
```

- [ ] **Step 3: Add migration guards**

Because `CREATE TABLE IF NOT EXISTS` does not add columns to existing SQLite files, add a helper that checks `PRAGMA table_info(table_name)` and runs `ALTER TABLE ... ADD COLUMN` only when missing.

- [ ] **Step 4: Update row interfaces, SQL selects, mappers, clone helpers**

Update:

- `CorpusRow`
- `DocumentRow`
- `LIST_CORPORA_SQL`
- `LIST_PUBLIC_CORPORA_SQL`
- `GET_CORPUS_SQL`
- `LIST_DOCUMENTS_SQL`
- `GET_DOCUMENT_SQL`
- `toCorpusRecord`
- `toDocumentRecord`
- `cloneCorpus`

- [ ] **Step 5: Add sync repository methods**

Add methods to `MetadataRepository`:

```ts
updateCorpusProviderState(input: {
  id: string;
  provider: CorpusProvider;
  status: CorpusStatus;
  providerVectorStoreId: string | null;
  providerVectorStoreStatus: CorpusRecord["providerVectorStoreStatus"];
  providerLastSyncedAt: string | null;
  providerSyncError: string | null;
}): CorpusRecord;

upsertDocument(input: DocumentInsert): DocumentRecord;
```

Use these in the future sync workflow. Keep existing `insertDocument`.

- [ ] **Step 6: Update `knowledge-corpus-sync.ts`**

Make seed SQL include the new nullable corpus columns so seed sync does not erase existing column compatibility. Do not force `provider = openai_vector_store` from seed sync.

- [ ] **Step 7: Run focused metadata tests**

Run:

```powershell
cd web
npm test -- tests/metadata/metadata-repository.test.ts tests/metadata/knowledge-corpus-sync.test.ts
```

Expected: PASS.

## Chunk 2: Provider Contracts And OpenAI Search

### Task 3: Add Provider Status Shape

**Files:**

- Modify: `web/src/knowledge-gateway/types.ts`
- Modify: `web/src/knowledge-gateway/local-provider.ts`
- Modify: `web/src/knowledge-gateway/knowledge-gateway.ts`
- Test: `web/tests/knowledge-gateway/knowledge-gateway.test.ts`
- Test: `web/tests/knowledge-gateway/local-provider.test.ts`

- [ ] **Step 1: Extend gateway statuses**

Add:

```ts
| "provider_unconfigured"
| "provider_unavailable"
| "provider_error"
```

- [ ] **Step 2: Change provider return type**

Add:

```ts
export interface KnowledgeProviderSearchResult {
  status: "ok" | "provider_unconfigured" | "provider_unavailable" | "provider_error";
  evidence: NormalizedKnowledgeEvidence[];
  message?: string;
}
```

Change `KnowledgeProvider.search(...)` to return `Promise<KnowledgeProviderSearchResult>`.

- [ ] **Step 3: Update local provider**

Local provider should return:

```ts
{ status: "ok", evidence }
```

- [ ] **Step 4: Update gateway orchestration**

Collect provider results per corpus. If any result has non-`ok` status and no evidence, return that status unless other searched corpora already produced evidence. Preserve existing `ok` sorting/dedupe behavior.

- [ ] **Step 5: Run focused gateway tests**

Run:

```powershell
cd web
npm test -- tests/knowledge-gateway/knowledge-gateway.test.ts tests/knowledge-gateway/local-provider.test.ts
```

Expected: PASS.

### Task 4: Add OpenAI Vector Store Client

**Files:**

- Create: `web/src/openai/vector-store-client.ts`
- Test: `web/tests/openai/vector-store-client.test.ts`

- [ ] **Step 1: Write tests with mocked `fetch`**

Test:

- missing API key is rejected by caller config, not by request construction
- `searchVectorStore(...)` sends `POST /vector_stores/{id}/search`
- `searchVectorStore(...)` includes `query` and `max_num_results`
- response JSON is returned as typed data

- [ ] **Step 2: Implement raw REST client**

Create a client around injected `fetch`:

```ts
export interface OpenAIVectorStoreClientOptions {
  apiKey: string;
  baseUrl?: string;
  fetchImpl?: typeof fetch;
}
```

Implement:

```ts
createVectorStore(input)
uploadFile(input)
attachFileToVectorStore(input)
retrieveVectorStore(id)
searchVectorStore(input)
```

Use `OPENAI_VECTOR_STORE_API_KEY` and `OPENAI_VECTOR_STORE_BASE_URL` with default base URL `https://api.openai.com/v1`.

- [ ] **Step 3: Run client tests**

Run:

```powershell
cd web
npm test -- tests/openai/vector-store-client.test.ts
```

Expected: PASS.

### Task 5: Add OpenAI Vector Store Provider

**Files:**

- Create: `web/src/knowledge-gateway/openai-vector-store-provider.ts`
- Modify: `web/src/knowledge-gateway/index.ts`
- Test: `web/tests/knowledge-gateway/openai-vector-store-provider.test.ts`

- [ ] **Step 1: Write provider mapping tests**

Mock an OpenAI search page:

```ts
{
  data: [
    {
      file_id: "file_123",
      filename: "pricing.md",
      score: 0.91,
      attributes: {
        document_id: "doc-1",
        source: "knowledge/finance/pricing.md",
        title: "Pricing",
      },
      content: [{ type: "text", text: "Pricing filters customers." }],
    },
  ],
}
```

Assert provider evidence maps to:

```ts
{
  corpusId: "opc-core",
  documentId: "doc-1",
  source: "knowledge/finance/pricing.md",
  score: 0.91,
  excerpt: "Pricing filters customers.",
}
```

- [ ] **Step 2: Implement provider**

Rules:

- If corpus provider is not `openai_vector_store`, return `{ status: "ok", evidence: [] }`.
- If API key is missing, return `provider_unconfigured`.
- If vector store id is missing, return `provider_unconfigured`.
- On network/API error, return `provider_error`.
- Map returned chunks into `NormalizedKnowledgeEvidence`.

- [ ] **Step 3: Export provider**

Update `web/src/knowledge-gateway/index.ts`.

- [ ] **Step 4: Run provider tests**

Run:

```powershell
cd web
npm test -- tests/knowledge-gateway/openai-vector-store-provider.test.ts
```

Expected: PASS.

### Task 6: Add Runtime Provider Factory

**Files:**

- Create: `web/src/knowledge-gateway/runtime-provider.ts`
- Modify: `web/src/knowledge-gateway/index.ts`
- Test: `web/tests/knowledge-gateway/runtime-provider.test.ts`

- [ ] **Step 1: Write factory tests**

Test:

- local corpus uses local provider
- OpenAI corpus with key and vector store id uses OpenAI provider
- OpenAI public corpus without key falls back to local provider
- OpenAI private corpus without key returns `provider_unconfigured`

- [ ] **Step 2: Implement factory**

Create:

```ts
createRuntimeKnowledgeProvider({
  repoRoot,
  env,
  fetchImpl,
})
```

It should compose local and OpenAI providers by corpus:

```text
local -> local provider
openai_vector_store -> OpenAI provider
openai_vector_store + public + OpenAI unconfigured -> local fallback
openai_vector_store + private + OpenAI unconfigured -> provider_unconfigured
```

- [ ] **Step 3: Run runtime provider tests**

Run:

```powershell
cd web
npm test -- tests/knowledge-gateway/runtime-provider.test.ts
```

Expected: PASS.

## Chunk 3: Public Corpus Sync

### Task 7: Add Public OpenAI Sync Workflow

**Files:**

- Create: `web/src/metadata/openai-corpus-sync.ts`
- Modify: `web/scripts/sync-knowledge-corpora.ts`
- Modify: `web/package.json`
- Test: `web/tests/metadata/openai-corpus-sync.test.ts`

- [ ] **Step 1: Write sync tests using fake OpenAI client**

Use a temporary repository with one Markdown file. Assert:

- source files are discovered from `corpus.localDirectories`
- content hash is recorded
- vector store id is written to corpus provider state
- document rows are upserted with `sourceOfTruth = "repo"` and `providerFileId`
- failed indexing does not mark corpus ready

- [ ] **Step 2: Implement file discovery and hashing**

Use existing `discoverMarkdownFiles(...)`. Accept `.md` first; add `.txt` only if existing discovery helper already supports it without widening too much.

- [ ] **Step 3: Implement rebuild-and-swap**

Flow:

```text
create vector store
upload each file
attach each file with attributes
poll vector store until completed or failed
write corpus provider state
upsert document rows
```

Attributes attached to vector store files:

```ts
{
  corpus_id,
  document_id,
  source,
  title,
  content_hash,
}
```

- [ ] **Step 4: Update script interface**

Support:

```powershell
cd web
npm run knowledge:sync -- --corpus opc-core --provider openai
```

Keep existing seed behavior under:

```powershell
npm run sync:knowledge-corpora
```

- [ ] **Step 5: Run sync tests**

Run:

```powershell
cd web
npm test -- tests/metadata/openai-corpus-sync.test.ts tests/metadata/knowledge-corpus-sync.test.ts
```

Expected: PASS.

## Chunk 4: Runtime Wiring

### Task 8: Replace Hard-Coded Local Provider In Runtime

**Files:**

- Modify: `web/src/chat/public-chat-service.ts`
- Modify: `web/src/chat/public-agent.ts`
- Modify: `web/src/agents/knowledge-tool.ts`
- Test: `web/tests/chat/public-chat-service.test.ts`
- Test: `web/tests/chat/public-agent-codex.test.ts`
- Test: `web/tests/agents/knowledge-tool.test.ts`

- [ ] **Step 1: Replace provider construction**

Change each runtime path from:

```ts
createLocalKnowledgeProvider({ repoRoot })
```

to:

```ts
createRuntimeKnowledgeProvider({
  repoRoot,
  env: readPublicAgentEnv(repoRoot) or process.env,
})
```

Do not change `/api/chat` request/response shape.

- [ ] **Step 2: Update tool description**

Change the generic tool description from local Markdown specific language to provider-neutral language:

```text
检索当前 Agent 允许访问的 OPC 知识库证据。
```

- [ ] **Step 3: Run focused runtime tests**

Run:

```powershell
cd web
npm test -- tests/chat/public-chat-service.test.ts tests/chat/public-agent-codex.test.ts tests/agents/knowledge-tool.test.ts
```

Expected: PASS.

## Chunk 5: Verification

### Task 9: Full Verification

**Files:**

- No new files unless tests expose bugs.

- [ ] **Step 1: Run direct import guard**

Run:

```powershell
cd web
rg -n "createLocalKnowledgeProvider" src/chat src/agents app
```

Expected: no runtime chat/tool call sites should hard-code local provider construction.

- [ ] **Step 2: Run full checks**

Run:

```powershell
cd web
npm run typecheck
npm test
npm run build
```

Expected: all pass.

- [ ] **Step 3: Optional real sync smoke**

Only run with a real `OPENAI_VECTOR_STORE_API_KEY`:

```powershell
cd web
npm run knowledge:sync -- --corpus opc-core --provider openai
```

Expected:

- command creates or updates one vector store for `opc-core`
- local metadata has `providerVectorStoreId`
- runtime search uses OpenAI when configured
- public local fallback still works when key is absent

## Acceptance Criteria

- `KnowledgeGateway` remains the only runtime retrieval boundary.
- `CorpusProvider` supports `openai_vector_store`.
- Metadata persists OpenAI vector store and file ids.
- Public corpus sync can rebuild `opc-core` into an OpenAI vector store with mocked tests.
- Runtime uses `createRuntimeKnowledgeProvider`.
- Public corpora can fall back to local search when OpenAI is unconfigured.
- Private corpora do not local fallback when OpenAI is unconfigured.
- No model-side `file_search` tool is introduced in this slice.
- `npm run typecheck`, `npm test`, and `npm run build` pass in `web/`.
