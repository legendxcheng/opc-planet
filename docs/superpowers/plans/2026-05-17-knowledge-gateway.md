# Knowledge Gateway Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce the first provider-neutral `KnowledgeGateway.search(...)` boundary in `web/` and move the current public chat runtime onto it without changing the browser chat contract.

**Architecture:** Keep the current local Markdown retriever as the only provider for this iteration, but stop calling it directly from chat and agent runtime code. Add static DB-shaped agent/corpus registries, a local provider adapter, normalized evidence output, and permission-ready corpus resolution behind the gateway. Preserve the current public-only assistant behavior while making the next private corpus and usage-accounting work additive.

**Tech Stack:** Next.js App Router, TypeScript, Vitest, `@openai/agents`, existing local Markdown retrieval modules under `web/src/knowledge/*`.

---

## Scope

In scope:

- Static registry abstractions for agents, corpora, and agent-to-corpus bindings.
- A `KnowledgeGateway.search(...)` API with public corpus resolution and private-corpus-ready permission checks.
- A local Markdown provider adapter that wraps `searchLocalKnowledge(...)`.
- Normalized evidence objects for citations.
- Refactor `public-chat-service`, `public-agent`, `knowledge-tool`, and `app/api/chat/route.ts` to use the gateway.
- Tests proving public-only behavior remains stable and denied/private/not-ready states are shaped consistently.
- README and plan status updates so docs no longer point to stale `.worktrees` paths.

Out of scope:

- Database migrations, Drizzle schema, or persistent metadata tables.
- User authentication and real private uploads.
- Token usage persistence.
- SQLite/Postgres full-text index.
- External provider adapters.

## Required Skills

- Use @superpowers:test-driven-development for implementation tasks.
- Use @superpowers:verification-before-completion before claiming the gateway work is done.
- Use @superpowers:receiving-code-review if review feedback arrives while executing this plan.

## Current Baseline

The current `web/` implementation already has:

- `web/app/api/chat/route.ts` as the stable `POST /api/chat` route.
- `web/src/chat/public-chat-service.ts` directly calling `searchLocalKnowledge(...)`.
- `web/src/chat/public-agent.ts` defining an OpenAI Agents SDK tool that directly calls `searchLocalKnowledge(...)`.
- `web/src/agents/knowledge-tool.ts` defining a separate local search tool that also directly calls `searchLocalKnowledge(...)`.
- `web/src/corpora/public-corpora.ts` as a public-only corpus list.
- `web/src/knowledge/search-local-knowledge.ts` as the current local Markdown search baseline.

Before executing, run:

```powershell
git status --short
git -C web status --short
```

Expected: the worktree may be dirty. Preserve unrelated changes. Do not revert user changes.

## File Structure

Create:

- `web/src/agents/agent-registry.ts`
  - Static agent metadata for the current public assistant.
- `web/src/corpora/corpus-registry.ts`
  - Static corpus metadata and lookup helpers. This replaces public-only config as the source of truth.
- `web/src/knowledge-gateway/types.ts`
  - Gateway request, result, evidence, registry, provider, and error-shape types.
- `web/src/knowledge-gateway/local-provider.ts`
  - Local provider adapter that maps corpus directories to `searchLocalKnowledge(...)`.
- `web/src/knowledge-gateway/knowledge-gateway.ts`
  - Permission-aware gateway orchestration.
- `web/src/knowledge-gateway/index.ts`
  - Public exports for gateway modules.
- `web/tests/agents/agent-registry.test.ts`
- `web/tests/corpora/corpus-registry.test.ts`
- `web/tests/knowledge-gateway/local-provider.test.ts`
- `web/tests/knowledge-gateway/knowledge-gateway.test.ts`

Modify:

- `web/src/corpora/public-corpora.ts`
  - Keep as a compatibility wrapper around the new registry until callers are migrated.
- `web/src/chat/public-chat-service.ts`
  - Replace direct corpus search with `KnowledgeGateway.search(...)`.
- `web/src/chat/public-agent.ts`
  - Replace direct local search inside the SDK tool with gateway calls.
- `web/src/agents/knowledge-tool.ts`
  - Replace direct local search with gateway calls for the generic tool path.
- `web/app/api/chat/route.ts`
  - Stop hard-coding `getPublicCorpusById("opc-core")`; pass `agentId` and `userId` into the chat service.
- `web/tests/chat/public-chat-service.test.ts`
- `web/tests/chat/api-chat-route.test.ts`
- `web/tests/agents/knowledge-tool.test.ts`
- `web/README.md`
- `docs/dev-plans/2026-05-14-assistant-ui-public-chat-mvp.md`
- `docs/dev-plans/2026-05-13-agent-knowledge-architecture.md`

## Naming Decisions

Use these ids consistently:

```ts
export const PUBLIC_ASSISTANT_AGENT_ID = "opc-public-assistant";
export const OPC_CORE_CORPUS_ID = "opc-core";
export const ANONYMOUS_PUBLIC_USER_ID = "anonymous-public";
```

Use these first-version result statuses:

```ts
export type KnowledgeGatewayStatus =
  | "ok"
  | "empty_query"
  | "access_denied"
  | "corpus_not_ready"
  | "agent_not_found"
  | "corpus_not_found";
```

Do not throw for normal request outcomes such as denied access or no matches. Return a typed status. Throw only for impossible programming errors.

## Chunk 1: Static Registry Foundation

### Task 1: Add Corpus Registry

**Files:**

- Create: `web/src/corpora/corpus-registry.ts`
- Modify: `web/src/corpora/public-corpora.ts`
- Test: `web/tests/corpora/corpus-registry.test.ts`

- [ ] **Step 1: Write the failing corpus registry tests**

Create `web/tests/corpora/corpus-registry.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import {
  getCorpusById,
  listCorpora,
  listPublicCorpora,
  OPC_CORE_CORPUS_ID,
} from "@/corpora/corpus-registry";

describe("corpus registry", () => {
  it("exposes the existing opc-core corpus as ready local public metadata", () => {
    const corpus = getCorpusById(OPC_CORE_CORPUS_ID);

    expect(corpus).toMatchObject({
      id: "opc-core",
      name: "OPC 核心知识库",
      visibility: "public",
      ownerType: "system",
      ownerUserId: null,
      provider: "local",
      status: "ready",
    });
    expect(corpus.localDirectories).toEqual([
      "knowledge/strategy/opc",
      "knowledge/strategy",
      "knowledge/finance",
      "knowledge/operations",
      "knowledge/products",
    ]);
  });

  it("returns defensive copies so callers cannot mutate registry state", () => {
    const corpora = listCorpora();
    corpora[0]!.localDirectories.push("knowledge/legal");

    expect(getCorpusById(OPC_CORE_CORPUS_ID).localDirectories).not.toContain(
      "knowledge/legal",
    );
  });

  it("keeps public corpus compatibility helpers backed by the registry", () => {
    expect(listPublicCorpora().map((corpus) => corpus.id)).toEqual([
      OPC_CORE_CORPUS_ID,
    ]);
  });
});
```

- [ ] **Step 2: Run the failing test**

Run:

```powershell
cd web
npm test -- tests/corpora/corpus-registry.test.ts
```

Expected: FAIL because `corpus-registry.ts` does not exist yet.

- [ ] **Step 3: Implement `web/src/corpora/corpus-registry.ts`**

Use this shape:

```ts
export const OPC_CORE_CORPUS_ID = "opc-core";

export type CorpusVisibility = "public" | "private";
export type CorpusOwnerType = "system" | "user";
export type CorpusProvider = "local";
export type CorpusStatus = "creating" | "indexing" | "ready" | "failed" | "archived";

export interface CorpusRecord {
  id: string;
  name: string;
  visibility: CorpusVisibility;
  ownerType: CorpusOwnerType;
  ownerUserId: string | null;
  provider: CorpusProvider;
  status: CorpusStatus;
  localDirectories: string[];
  quotaBytes: number | null;
  usedBytes: number | null;
}

const CORPORA: CorpusRecord[] = [
  {
    id: OPC_CORE_CORPUS_ID,
    name: "OPC 核心知识库",
    visibility: "public",
    ownerType: "system",
    ownerUserId: null,
    provider: "local",
    status: "ready",
    localDirectories: [
      "knowledge/strategy/opc",
      "knowledge/strategy",
      "knowledge/finance",
      "knowledge/operations",
      "knowledge/products",
    ],
    quotaBytes: null,
    usedBytes: null,
  },
];

function cloneCorpus(corpus: CorpusRecord): CorpusRecord {
  return {
    ...corpus,
    localDirectories: [...corpus.localDirectories],
  };
}

export function listCorpora(): CorpusRecord[] {
  return CORPORA.map(cloneCorpus);
}

export function listPublicCorpora(): CorpusRecord[] {
  return CORPORA.filter((corpus) => corpus.visibility === "public").map(cloneCorpus);
}

export function getCorpusById(id: string): CorpusRecord {
  const corpus = CORPORA.find((entry) => entry.id === id);
  if (!corpus) {
    throw new Error(`Unknown corpus: ${id}`);
  }

  return cloneCorpus(corpus);
}
```

- [ ] **Step 4: Update the old public corpus wrapper**

Modify `web/src/corpora/public-corpora.ts` so existing imports keep working temporarily:

```ts
import {
  getCorpusById,
  listPublicCorpora as listPublicCorpusRecords,
  type CorpusRecord,
} from "./corpus-registry";

export interface PublicCorpus {
  id: string;
  name: string;
  directories: string[];
}

function toPublicCorpus(corpus: CorpusRecord): PublicCorpus {
  return {
    id: corpus.id,
    name: corpus.name,
    directories: [...corpus.localDirectories],
  };
}

export function listPublicCorpora(): PublicCorpus[] {
  return listPublicCorpusRecords().map(toPublicCorpus);
}

export function getPublicCorpusById(id: string): PublicCorpus {
  const corpus = getCorpusById(id);
  if (corpus.visibility !== "public") {
    throw new Error(`Corpus is not public: ${id}`);
  }

  return toPublicCorpus(corpus);
}
```

- [ ] **Step 5: Run focused tests**

Run:

```powershell
cd web
npm test -- tests/corpora/corpus-registry.test.ts tests/chat/public-chat-service.test.ts
```

Expected: PASS. Existing chat service tests should still pass through the compatibility wrapper.

- [ ] **Step 6: Commit corpus registry**

Run:

```powershell
git -C web add src/corpora/corpus-registry.ts src/corpora/public-corpora.ts tests/corpora/corpus-registry.test.ts
git -C web commit -m "feat(web): add static corpus registry"
```

### Task 2: Add Agent Registry

**Files:**

- Create: `web/src/agents/agent-registry.ts`
- Test: `web/tests/agents/agent-registry.test.ts`

- [ ] **Step 1: Write the failing agent registry tests**

Create `web/tests/agents/agent-registry.test.ts`:

```ts
import { describe, expect, it } from "vitest";

import {
  getAgentById,
  listAgents,
  PUBLIC_ASSISTANT_AGENT_ID,
} from "@/agents/agent-registry";
import { OPC_CORE_CORPUS_ID } from "@/corpora/corpus-registry";

describe("agent registry", () => {
  it("defines the public assistant and its default public corpora", () => {
    const agent = getAgentById(PUBLIC_ASSISTANT_AGENT_ID);

    expect(agent).toMatchObject({
      id: "opc-public-assistant",
      name: "OPC 公共知识助手",
      status: "active",
      model: "gpt-4.1-mini",
    });
    expect(agent.defaultPublicCorpusIds).toEqual([OPC_CORE_CORPUS_ID]);
  });

  it("returns defensive copies", () => {
    const agents = listAgents();
    agents[0]!.defaultPublicCorpusIds.push("other");

    expect(getAgentById(PUBLIC_ASSISTANT_AGENT_ID).defaultPublicCorpusIds).toEqual([
      OPC_CORE_CORPUS_ID,
    ]);
  });
});
```

- [ ] **Step 2: Run the failing test**

Run:

```powershell
cd web
npm test -- tests/agents/agent-registry.test.ts
```

Expected: FAIL because `agent-registry.ts` does not exist yet.

- [ ] **Step 3: Implement `web/src/agents/agent-registry.ts`**

Use this shape:

```ts
import { OPC_CORE_CORPUS_ID } from "@/corpora/corpus-registry";

export const PUBLIC_ASSISTANT_AGENT_ID = "opc-public-assistant";

export type AgentStatus = "active" | "archived";

export interface AgentRecord {
  id: string;
  name: string;
  status: AgentStatus;
  model: string;
  defaultPublicCorpusIds: string[];
}

const AGENTS: AgentRecord[] = [
  {
    id: PUBLIC_ASSISTANT_AGENT_ID,
    name: "OPC 公共知识助手",
    status: "active",
    model: "gpt-4.1-mini",
    defaultPublicCorpusIds: [OPC_CORE_CORPUS_ID],
  },
];

function cloneAgent(agent: AgentRecord): AgentRecord {
  return {
    ...agent,
    defaultPublicCorpusIds: [...agent.defaultPublicCorpusIds],
  };
}

export function listAgents(): AgentRecord[] {
  return AGENTS.map(cloneAgent);
}

export function getAgentById(id: string): AgentRecord {
  const agent = AGENTS.find((entry) => entry.id === id);
  if (!agent) {
    throw new Error(`Unknown agent: ${id}`);
  }

  return cloneAgent(agent);
}
```

- [ ] **Step 4: Run focused registry tests**

Run:

```powershell
cd web
npm test -- tests/agents/agent-registry.test.ts tests/corpora/corpus-registry.test.ts
```

Expected: PASS.

- [ ] **Step 5: Commit agent registry**

Run:

```powershell
git -C web add src/agents/agent-registry.ts tests/agents/agent-registry.test.ts
git -C web commit -m "feat(web): add public assistant registry"
```

## Chunk 2: Gateway Types And Local Provider

### Task 3: Define Gateway Types

**Files:**

- Create: `web/src/knowledge-gateway/types.ts`
- Create: `web/src/knowledge-gateway/index.ts`

- [ ] **Step 1: Create gateway type definitions**

Create `web/src/knowledge-gateway/types.ts`:

```ts
import type { AgentRecord } from "@/agents/agent-registry";
import type { CorpusRecord } from "@/corpora/corpus-registry";

export type KnowledgeGatewayStatus =
  | "ok"
  | "empty_query"
  | "access_denied"
  | "corpus_not_ready"
  | "agent_not_found"
  | "corpus_not_found";

export interface NormalizedKnowledgeEvidence {
  corpusId: string;
  documentId: string;
  chunkId: string;
  title: string;
  source: string;
  score: number;
  excerpt: string;
}

export interface KnowledgeGatewaySearchRequest {
  userId: string | null;
  agentId: string;
  selectedPrivateCorpusId?: string | null;
  query: string;
  limit?: number;
}

export interface KnowledgeGatewaySearchResult {
  status: KnowledgeGatewayStatus;
  evidence: NormalizedKnowledgeEvidence[];
  message?: string;
}

export interface KnowledgeRegistry {
  getAgentById(id: string): AgentRecord | null;
  getCorpusById(id: string): CorpusRecord | null;
}

export interface KnowledgeProviderSearchRequest {
  corpus: CorpusRecord;
  query: string;
  limit: number;
}

export interface KnowledgeProvider {
  search(request: KnowledgeProviderSearchRequest): Promise<NormalizedKnowledgeEvidence[]>;
}
```

- [ ] **Step 2: Create public exports**

Create `web/src/knowledge-gateway/index.ts`:

```ts
export type {
  KnowledgeGatewaySearchRequest,
  KnowledgeGatewaySearchResult,
  KnowledgeGatewayStatus,
  KnowledgeProvider,
  KnowledgeProviderSearchRequest,
  KnowledgeRegistry,
  NormalizedKnowledgeEvidence,
} from "./types";
```

- [ ] **Step 3: Run typecheck**

Run:

```powershell
cd web
npm run typecheck
```

Expected: PASS.

- [ ] **Step 4: Commit gateway types**

Run:

```powershell
git -C web add src/knowledge-gateway/types.ts src/knowledge-gateway/index.ts
git -C web commit -m "feat(web): define knowledge gateway contracts"
```

### Task 4: Add Local Provider Adapter

**Files:**

- Create: `web/src/knowledge-gateway/local-provider.ts`
- Modify: `web/src/knowledge-gateway/index.ts`
- Test: `web/tests/knowledge-gateway/local-provider.test.ts`

- [ ] **Step 1: Write the failing local provider tests**

Create `web/tests/knowledge-gateway/local-provider.test.ts`:

```ts
import { mkdtemp, mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { tmpdir } from "node:os";
import { describe, expect, it } from "vitest";

import { createLocalKnowledgeProvider } from "@/knowledge-gateway/local-provider";
import type { CorpusRecord } from "@/corpora/corpus-registry";

function corpus(overrides: Partial<CorpusRecord> = {}): CorpusRecord {
  return {
    id: "test-corpus",
    name: "Test Corpus",
    visibility: "public",
    ownerType: "system",
    ownerUserId: null,
    provider: "local",
    status: "ready",
    localDirectories: ["knowledge/strategy"],
    quotaBytes: null,
    usedBytes: null,
    ...overrides,
  };
}

describe("local knowledge provider", () => {
  it("normalizes local markdown results into gateway evidence", async () => {
    const root = await mkdtemp(join(tmpdir(), "opc-gateway-"));
    const noteDir = join(root, "knowledge", "strategy");
    await mkdir(noteDir, { recursive: true });
    await writeFile(
      join(noteDir, "pricing-filter.md"),
      "# Pricing Filter\n\nPricing filters customers and expectations.\n",
      "utf8",
    );

    const provider = createLocalKnowledgeProvider({ repoRoot: root });
    const evidence = await provider.search({
      corpus: corpus(),
      query: "pricing filter",
      limit: 3,
    });

    expect(evidence).toHaveLength(1);
    expect(evidence[0]).toMatchObject({
      corpusId: "test-corpus",
      documentId: "knowledge/strategy/pricing-filter.md",
      chunkId: "knowledge/strategy/pricing-filter.md#local",
      title: "pricing-filter",
      source: "knowledge/strategy/pricing-filter.md",
    });
    expect(evidence[0]!.score).toBeGreaterThan(0);
  });

  it("returns no evidence for non-local corpora", async () => {
    const provider = createLocalKnowledgeProvider({ repoRoot: "E:/opc-planet" });

    const evidence = await provider.search({
      corpus: corpus({ provider: "local" }),
      query: "zzqv unmatched phrase 90210",
      limit: 3,
    });

    expect(evidence).toEqual([]);
  });
});
```

- [ ] **Step 2: Run the failing test**

Run:

```powershell
cd web
npm test -- tests/knowledge-gateway/local-provider.test.ts
```

Expected: FAIL because `local-provider.ts` does not exist yet.

- [ ] **Step 3: Implement local provider**

Create `web/src/knowledge-gateway/local-provider.ts`:

```ts
import { searchLocalKnowledge } from "@/knowledge";
import type { CorpusRecord } from "@/corpora/corpus-registry";
import type {
  KnowledgeProvider,
  KnowledgeProviderSearchRequest,
  NormalizedKnowledgeEvidence,
} from "./types";

export interface LocalKnowledgeProviderOptions {
  repoRoot: string;
}

function titleFromSource(source: string): string {
  return source.split("/").at(-1)?.replace(/\.md$/i, "") ?? source;
}

function toEvidence(
  corpus: CorpusRecord,
  result: Awaited<ReturnType<typeof searchLocalKnowledge>>[number],
): NormalizedKnowledgeEvidence {
  return {
    corpusId: corpus.id,
    documentId: result.path,
    chunkId: `${result.path}#local`,
    title: titleFromSource(result.path),
    source: result.path,
    score: result.score,
    excerpt: result.excerpt,
  };
}

export function createLocalKnowledgeProvider(
  options: LocalKnowledgeProviderOptions,
): KnowledgeProvider {
  return {
    async search(request: KnowledgeProviderSearchRequest) {
      if (request.corpus.provider !== "local") {
        return [];
      }

      const results = await searchLocalKnowledge(request.query, {
        repoRoot: options.repoRoot,
        limit: request.limit,
        searchDirectories: request.corpus.localDirectories,
      });

      return results.map((result) => toEvidence(request.corpus, result));
    },
  };
}
```

- [ ] **Step 4: Export the local provider**

Modify `web/src/knowledge-gateway/index.ts`:

```ts
export { createLocalKnowledgeProvider } from "./local-provider";
```

- [ ] **Step 5: Run focused tests**

Run:

```powershell
cd web
npm test -- tests/knowledge-gateway/local-provider.test.ts tests/knowledge/search-local-knowledge.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit local provider**

Run:

```powershell
git -C web add src/knowledge-gateway/local-provider.ts src/knowledge-gateway/index.ts tests/knowledge-gateway/local-provider.test.ts
git -C web commit -m "feat(web): add local knowledge provider adapter"
```

## Chunk 3: Permission-Aware Gateway

### Task 5: Implement `KnowledgeGateway.search`

**Files:**

- Create: `web/src/knowledge-gateway/knowledge-gateway.ts`
- Modify: `web/src/knowledge-gateway/index.ts`
- Test: `web/tests/knowledge-gateway/knowledge-gateway.test.ts`

- [ ] **Step 1: Write gateway orchestration tests**

Create `web/tests/knowledge-gateway/knowledge-gateway.test.ts`:

```ts
import { describe, expect, it, vi } from "vitest";

import { createKnowledgeGateway } from "@/knowledge-gateway/knowledge-gateway";
import type {
  KnowledgeProvider,
  KnowledgeRegistry,
  NormalizedKnowledgeEvidence,
} from "@/knowledge-gateway";
import type { AgentRecord } from "@/agents/agent-registry";
import type { CorpusRecord } from "@/corpora/corpus-registry";

const publicCorpus: CorpusRecord = {
  id: "opc-core",
  name: "OPC Core",
  visibility: "public",
  ownerType: "system",
  ownerUserId: null,
  provider: "local",
  status: "ready",
  localDirectories: ["knowledge/strategy"],
  quotaBytes: null,
  usedBytes: null,
};

const privateCorpus: CorpusRecord = {
  id: "private-1",
  name: "Private",
  visibility: "private",
  ownerType: "user",
  ownerUserId: "user-1",
  provider: "local",
  status: "ready",
  localDirectories: ["data/processed/private-1"],
  quotaBytes: 100,
  usedBytes: 50,
};

const agent: AgentRecord = {
  id: "agent-1",
  name: "Agent",
  status: "active",
  model: "gpt-4.1-mini",
  defaultPublicCorpusIds: ["opc-core"],
};

function registry(corpora: CorpusRecord[] = [publicCorpus]): KnowledgeRegistry {
  return {
    getAgentById: (id) => (id === agent.id ? agent : null),
    getCorpusById: (id) => corpora.find((corpus) => corpus.id === id) ?? null,
  };
}

function evidence(source: string, corpusId = "opc-core"): NormalizedKnowledgeEvidence {
  return {
    corpusId,
    documentId: source,
    chunkId: `${source}#local`,
    title: source,
    source,
    score: 2,
    excerpt: "matched evidence",
  };
}

describe("knowledge gateway", () => {
  it("searches the public corpora bound to the agent", async () => {
    const provider: KnowledgeProvider = {
      search: vi.fn().mockResolvedValue([evidence("knowledge/strategy/pricing.md")]),
    };
    const gateway = createKnowledgeGateway({ registry: registry(), provider });

    const result = await gateway.search({
      userId: null,
      agentId: "agent-1",
      query: "pricing",
      limit: 4,
    });

    expect(result.status).toBe("ok");
    expect(result.evidence).toHaveLength(1);
    expect(provider.search).toHaveBeenCalledWith({
      corpus: publicCorpus,
      query: "pricing",
      limit: 4,
    });
  });

  it("adds a selected private corpus only for the owner", async () => {
    const provider: KnowledgeProvider = {
      search: vi
        .fn()
        .mockResolvedValueOnce([evidence("knowledge/strategy/pricing.md")])
        .mockResolvedValueOnce([evidence("private.md", "private-1")]),
    };
    const gateway = createKnowledgeGateway({
      registry: registry([publicCorpus, privateCorpus]),
      provider,
    });

    const result = await gateway.search({
      userId: "user-1",
      agentId: "agent-1",
      selectedPrivateCorpusId: "private-1",
      query: "pricing",
    });

    expect(result.status).toBe("ok");
    expect(result.evidence.map((item) => item.corpusId)).toEqual([
      "opc-core",
      "private-1",
    ]);
  });

  it("denies selected private corpus access for non-owners", async () => {
    const gateway = createKnowledgeGateway({
      registry: registry([publicCorpus, privateCorpus]),
      provider: { search: vi.fn() },
    });

    const result = await gateway.search({
      userId: "user-2",
      agentId: "agent-1",
      selectedPrivateCorpusId: "private-1",
      query: "pricing",
    });

    expect(result.status).toBe("access_denied");
    expect(result.evidence).toEqual([]);
  });

  it("does not search archived or failed corpora", async () => {
    const gateway = createKnowledgeGateway({
      registry: registry([{ ...publicCorpus, status: "failed" }]),
      provider: { search: vi.fn() },
    });

    const result = await gateway.search({
      userId: null,
      agentId: "agent-1",
      query: "pricing",
    });

    expect(result.status).toBe("corpus_not_ready");
    expect(result.evidence).toEqual([]);
  });

  it("returns empty_query for queries without searchable text", async () => {
    const gateway = createKnowledgeGateway({
      registry: registry(),
      provider: { search: vi.fn() },
    });

    const result = await gateway.search({
      userId: null,
      agentId: "agent-1",
      query: "  ",
    });

    expect(result.status).toBe("empty_query");
    expect(result.evidence).toEqual([]);
  });
});
```

- [ ] **Step 2: Run the failing gateway tests**

Run:

```powershell
cd web
npm test -- tests/knowledge-gateway/knowledge-gateway.test.ts
```

Expected: FAIL because `knowledge-gateway.ts` does not exist yet.

- [ ] **Step 3: Implement `web/src/knowledge-gateway/knowledge-gateway.ts`**

Use this behavior:

```ts
import type { CorpusRecord } from "@/corpora/corpus-registry";
import type {
  KnowledgeGatewaySearchRequest,
  KnowledgeGatewaySearchResult,
  KnowledgeProvider,
  KnowledgeRegistry,
  NormalizedKnowledgeEvidence,
} from "./types";

export interface KnowledgeGatewayOptions {
  registry: KnowledgeRegistry;
  provider: KnowledgeProvider;
}

export interface KnowledgeGateway {
  search(request: KnowledgeGatewaySearchRequest): Promise<KnowledgeGatewaySearchResult>;
}

function result(
  status: KnowledgeGatewaySearchResult["status"],
  evidence: NormalizedKnowledgeEvidence[] = [],
  message?: string,
): KnowledgeGatewaySearchResult {
  return { status, evidence, ...(message ? { message } : {}) };
}

function uniqueEvidence(items: NormalizedKnowledgeEvidence[]): NormalizedKnowledgeEvidence[] {
  const seen = new Set<string>();
  const unique: NormalizedKnowledgeEvidence[] = [];

  for (const item of items) {
    const key = `${item.corpusId}:${item.chunkId}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    unique.push(item);
  }

  return unique;
}

function canUsePrivateCorpus(userId: string | null, corpus: CorpusRecord): boolean {
  return (
    corpus.visibility === "private" &&
    corpus.ownerType === "user" &&
    corpus.ownerUserId !== null &&
    corpus.ownerUserId === userId
  );
}

export function createKnowledgeGateway(options: KnowledgeGatewayOptions): KnowledgeGateway {
  return {
    async search(request) {
      const query = request.query.trim();
      if (!query) {
        return result("empty_query", [], "Query is empty.");
      }

      const agent = options.registry.getAgentById(request.agentId);
      if (!agent || agent.status !== "active") {
        return result("agent_not_found", [], `Agent not found: ${request.agentId}`);
      }

      const corpusIds = [...agent.defaultPublicCorpusIds];
      if (request.selectedPrivateCorpusId) {
        corpusIds.push(request.selectedPrivateCorpusId);
      }

      const corpora: CorpusRecord[] = [];
      for (const corpusId of corpusIds) {
        const corpus = options.registry.getCorpusById(corpusId);
        if (!corpus) {
          return result("corpus_not_found", [], `Corpus not found: ${corpusId}`);
        }

        if (corpus.visibility === "private" && !canUsePrivateCorpus(request.userId, corpus)) {
          return result("access_denied", [], `Access denied for corpus: ${corpusId}`);
        }

        if (corpus.status !== "ready") {
          return result("corpus_not_ready", [], `Corpus is not ready: ${corpusId}`);
        }

        corpora.push(corpus);
      }

      const perCorpusLimit = request.limit ?? 6;
      const evidence = (
        await Promise.all(
          corpora.map((corpus) =>
            options.provider.search({
              corpus,
              query,
              limit: perCorpusLimit,
            }),
          ),
        )
      ).flat();

      return result(
        "ok",
        uniqueEvidence(evidence)
          .sort((left, right) => right.score - left.score || left.source.localeCompare(right.source))
          .slice(0, request.limit ?? 6),
      );
    },
  };
}
```

- [ ] **Step 4: Export gateway factory**

Modify `web/src/knowledge-gateway/index.ts`:

```ts
export { createKnowledgeGateway, type KnowledgeGateway } from "./knowledge-gateway";
```

- [ ] **Step 5: Run gateway tests**

Run:

```powershell
cd web
npm test -- tests/knowledge-gateway/knowledge-gateway.test.ts tests/knowledge-gateway/local-provider.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit gateway orchestration**

Run:

```powershell
git -C web add src/knowledge-gateway/knowledge-gateway.ts src/knowledge-gateway/index.ts tests/knowledge-gateway/knowledge-gateway.test.ts
git -C web commit -m "feat(web): add permission-aware knowledge gateway"
```

## Chunk 4: Move Runtime Code Onto The Gateway

### Task 6: Refactor Public Chat Service

**Files:**

- Modify: `web/src/chat/public-chat-service.ts`
- Test: `web/tests/chat/public-chat-service.test.ts`

- [ ] **Step 1: Update public chat service tests first**

Change tests to stop passing `corpus: getPublicCorpusById("opc-core")`. They should pass `agentId: PUBLIC_ASSISTANT_AGENT_ID` and assert citations are sourced from gateway evidence.

Expected options shape:

```ts
{
  repoRoot: "E:/opc-planet",
  agentId: PUBLIC_ASSISTANT_AGENT_ID,
  userId: null,
}
```

Add this assertion to the matching public results test:

```ts
expect(reply.citations[0]).toMatchObject({
  id: "citation-1",
  path: expect.stringMatching(/^knowledge\//),
});
```

- [ ] **Step 2: Run the focused test to confirm failure**

Run:

```powershell
cd web
npm test -- tests/chat/public-chat-service.test.ts
```

Expected: FAIL because service options still require `corpus`.

- [ ] **Step 3: Refactor `public-chat-service.ts`**

Replace `PublicChatServiceOptions` with:

```ts
export interface PublicChatServiceOptions {
  repoRoot: string;
  agentId: string;
  userId: string | null;
  selectedPrivateCorpusId?: string | null;
}
```

Build the default gateway inside the service:

```ts
import { getAgentById } from "@/agents/agent-registry";
import { getCorpusById } from "@/corpora/corpus-registry";
import {
  createKnowledgeGateway,
  createLocalKnowledgeProvider,
  type KnowledgeRegistry,
  type NormalizedKnowledgeEvidence,
} from "@/knowledge-gateway";

const DEFAULT_REGISTRY: KnowledgeRegistry = {
  getAgentById: (id) => {
    try {
      return getAgentById(id);
    } catch {
      return null;
    }
  },
  getCorpusById: (id) => {
    try {
      return getCorpusById(id);
    } catch {
      return null;
    }
  },
};
```

Convert gateway evidence to existing `MockCitation` shape:

```ts
function toCitation(evidence: NormalizedKnowledgeEvidence, index: number): MockCitation {
  return {
    id: `citation-${index + 1}`,
    title: evidence.title,
    path: evidence.source,
    snippet: evidence.excerpt,
  };
}
```

Call gateway:

```ts
const gateway = createKnowledgeGateway({
  registry: DEFAULT_REGISTRY,
  provider: createLocalKnowledgeProvider({ repoRoot: options.repoRoot }),
});
const result = await gateway.search({
  userId: options.userId,
  agentId: options.agentId,
  selectedPrivateCorpusId: options.selectedPrivateCorpusId,
  query: latestUserMessage.content,
  limit: 4,
});
```

Return fallback when `result.status !== "ok"` or `result.evidence.length === 0`.

- [ ] **Step 4: Update SDK fallback path**

Keep `publicChatServiceWithAgent(...)` fallback-first behavior, but pass `{ repoRoot, agentId, userId, selectedPrivateCorpusId }` into `runPublicAgent(...)`.

- [ ] **Step 5: Run focused tests**

Run:

```powershell
cd web
npm test -- tests/chat/public-chat-service.test.ts tests/knowledge-gateway/knowledge-gateway.test.ts
```

Expected: PASS.

- [ ] **Step 6: Commit chat service migration**

Run:

```powershell
git -C web add src/chat/public-chat-service.ts tests/chat/public-chat-service.test.ts
git -C web commit -m "feat(web): route public chat service through knowledge gateway"
```

### Task 7: Refactor Public Agent Tool

**Files:**

- Modify: `web/src/chat/public-agent.ts`
- Test: `web/tests/chat/public-chat-service.test.ts`

- [ ] **Step 1: Update `PublicAgentContext`**

Change context from `{ repoRoot, corpus }` to:

```ts
export interface PublicAgentContext {
  repoRoot: string;
  agentId: string;
  userId: string | null;
  selectedPrivateCorpusId?: string | null;
}
```

- [ ] **Step 2: Replace direct local search in the SDK tool**

Inside the `search_public_knowledge` tool, create the same default registry and local provider used by `public-chat-service.ts`, or extract a small shared helper if duplication becomes noisy.

The execute path should call:

```ts
const gateway = createKnowledgeGateway({
  registry: DEFAULT_REGISTRY,
  provider: createLocalKnowledgeProvider({ repoRoot: typedContext.repoRoot }),
});

const result = await gateway.search({
  userId: typedContext.userId,
  agentId: typedContext.agentId,
  selectedPrivateCorpusId: typedContext.selectedPrivateCorpusId,
  query: input.query,
  limit: input.limit ?? 4,
});

return JSON.stringify(result, null, 2);
```

- [ ] **Step 3: Run focused tests**

Run:

```powershell
cd web
npm test -- tests/chat/public-chat-service.test.ts
```

Expected: PASS. Existing tests mock `runPublicAgent`, so this catches type and import breakage.

- [ ] **Step 4: Run typecheck**

Run:

```powershell
cd web
npm run typecheck
```

Expected: PASS.

- [ ] **Step 5: Commit public agent migration**

Run:

```powershell
git -C web add src/chat/public-agent.ts
git -C web commit -m "feat(web): route public agent tool through knowledge gateway"
```

### Task 8: Refactor Generic Knowledge Tool

**Files:**

- Modify: `web/src/agents/knowledge-tool.ts`
- Test: `web/tests/agents/knowledge-tool.test.ts`

- [ ] **Step 1: Update generic tool tests**

Extend `web/tests/agents/knowledge-tool.test.ts` with an execution test:

```ts
it("executes through the knowledge gateway contract", async () => {
  const [tool] = buildKnowledgeTools();

  const payload = await tool!.execute(
    { query: "pricing filter", limit: 2 },
    {
      repoRoot: "E:/opc-planet",
      agentId: "opc-public-assistant",
      userId: null,
    },
  );

  const result = JSON.parse(payload) as { status: string; evidence: unknown[] };

  expect(result.status).toBe("ok");
  expect(result.evidence.length).toBeGreaterThan(0);
});
```

- [ ] **Step 2: Run the focused test to confirm failure**

Run:

```powershell
cd web
npm test -- tests/agents/knowledge-tool.test.ts
```

Expected: FAIL because `KnowledgeToolContext` lacks `agentId` and `userId`.

- [ ] **Step 3: Modify `web/src/agents/knowledge-tool.ts`**

Update context:

```ts
export interface KnowledgeToolContext {
  repoRoot: string;
  agentId: string;
  userId: string | null;
  selectedPrivateCorpusId?: string | null;
}
```

Replace direct `searchLocalKnowledge(...)` with `createKnowledgeGateway(...)` and `createLocalKnowledgeProvider(...)`. Return the full gateway result JSON, not only raw evidence:

```ts
return JSON.stringify(result, null, 2);
```

- [ ] **Step 4: Run focused tests**

Run:

```powershell
cd web
npm test -- tests/agents/knowledge-tool.test.ts tests/knowledge-gateway/knowledge-gateway.test.ts
```

Expected: PASS.

- [ ] **Step 5: Commit generic tool migration**

Run:

```powershell
git -C web add src/agents/knowledge-tool.ts tests/agents/knowledge-tool.test.ts
git -C web commit -m "feat(web): route knowledge tool through gateway"
```

### Task 9: Refactor `/api/chat` Route To Use Agent Identity

**Files:**

- Modify: `web/app/api/chat/route.ts`
- Test: `web/tests/chat/api-chat-route.test.ts`

- [ ] **Step 1: Update route import and service call expectation**

Modify `web/app/api/chat/route.ts` to import:

```ts
import { PUBLIC_ASSISTANT_AGENT_ID } from "@/agents/agent-registry";
```

Remove:

```ts
import { getPublicCorpusById } from "@/corpora/public-corpora";
```

Call service with:

```ts
const reply = await publicChatServiceWithAgent(
  {
    repoRoot,
    agentId: PUBLIC_ASSISTANT_AGENT_ID,
    userId: null,
  },
  normalizedMessages,
);
```

- [ ] **Step 2: Run route tests**

Run:

```powershell
cd web
npm test -- tests/chat/api-chat-route.test.ts
```

Expected: PASS. The public chat route should still stream the same response protocol.

- [ ] **Step 3: Run broader chat tests**

Run:

```powershell
cd web
npm test -- tests/chat/api-chat-route.test.ts tests/chat/public-chat-service.test.ts tests/agents/knowledge-tool.test.ts
```

Expected: PASS.

- [ ] **Step 4: Commit route migration**

Run:

```powershell
git -C web add app/api/chat/route.ts tests/chat/api-chat-route.test.ts
git -C web commit -m "feat(web): use public assistant identity in chat route"
```

## Chunk 5: Documentation And Verification

### Task 10: Document Gateway Runtime

**Files:**

- Modify: `web/README.md`
- Modify: `docs/dev-plans/2026-05-14-assistant-ui-public-chat-mvp.md`
- Modify: `docs/dev-plans/2026-05-13-agent-knowledge-architecture.md`

- [ ] **Step 1: Fix stale `.worktrees` links in `web/README.md`**

Replace links like:

```md
/E:/opc-planet/web/.worktrees/assistant-ui-public-chat-mvp/app/api/chat/route.ts
```

with current main worktree links:

```md
/E:/opc-planet/web/app/api/chat/route.ts
```

- [ ] **Step 2: Add Knowledge Gateway runtime notes to `web/README.md`**

Add a short section:

```md
## Knowledge Gateway

- Public chat resolves an agent id first: `opc-public-assistant`.
- Agent metadata lives in `src/agents/agent-registry.ts`.
- Corpus metadata lives in `src/corpora/corpus-registry.ts`.
- Runtime retrieval goes through `src/knowledge-gateway/knowledge-gateway.ts`.
- The current provider is local Markdown search through `src/knowledge-gateway/local-provider.ts`.
- Normalized evidence uses `{ corpusId, documentId, chunkId, title, source, score, excerpt }`.
```

- [ ] **Step 3: Update the MVP plan status**

In `docs/dev-plans/2026-05-14-assistant-ui-public-chat-mvp.md`, change the status note so it says the MVP was merged into the main `web/` worktree, and that the next active work is the Knowledge Gateway migration.

- [ ] **Step 4: Update the architecture progress note**

In `docs/dev-plans/2026-05-13-agent-knowledge-architecture.md`, update the progress section after the migration to say:

```md
- `KnowledgeGateway.search(...)` is now the runtime retrieval entrypoint for the public chat path.
- The registry is still static config, not a database-backed metadata layer.
```

- [ ] **Step 5: Run docs grep**

Run:

```powershell
rg -n "\.worktrees/assistant-ui-public-chat-mvp|not merged|not yet committed" web/README.md docs/dev-plans/2026-05-14-assistant-ui-public-chat-mvp.md docs/dev-plans/2026-05-13-agent-knowledge-architecture.md
```

Expected: no stale matches that still describe the current state incorrectly.

- [ ] **Step 6: Commit docs**

Run:

```powershell
git add web/README.md docs/dev-plans/2026-05-14-assistant-ui-public-chat-mvp.md docs/dev-plans/2026-05-13-agent-knowledge-architecture.md
git commit -m "docs: document knowledge gateway runtime path"
```

### Task 11: Final Verification

**Files:**

- No code files unless verification exposes a bug.

- [ ] **Step 1: Run full `web` verification**

Run:

```powershell
cd web
npm run typecheck
npm test
npm run build
```

Expected: all three commands PASS.

- [ ] **Step 2: Run manual public route smoke test**

Run dev server:

```powershell
cd web
npm run dev
```

Open the shown local URL and ask:

```text
How should a one-person company think about pricing?
```

Expected:

- Home page remains a single centered `assistant-ui` thread.
- `POST /api/chat` returns a streamed answer.
- With no `OPENAI_API_KEY`, response falls back to local public knowledge.
- No sidebar or history UI appears.

- [ ] **Step 3: Capture final git status**

Run:

```powershell
git status --short
git -C web status --short
```

Expected: only unrelated pre-existing repository changes remain. Gateway implementation changes should be committed in `web/`.

## Acceptance Criteria

The implementation is complete when:

- `web/src/chat/public-chat-service.ts` does not import `searchLocalKnowledge`.
- `web/src/chat/public-agent.ts` does not import `searchLocalKnowledge`.
- `web/src/agents/knowledge-tool.ts` does not import `searchLocalKnowledge`.
- `web/app/api/chat/route.ts` passes `agentId` and `userId` into the service instead of a concrete corpus object.
- `KnowledgeGateway.search(...)` returns normalized evidence with `corpusId`, `documentId`, `chunkId`, `title`, `source`, `score`, and `excerpt`.
- Access denial and not-ready corpus cases are typed results, not uncaught exceptions.
- Existing public chat behavior still passes route and service tests.
- `npm run typecheck`, `npm test`, and `npm run build` pass in `web/`.

## Follow-Up Plan After This One

Do not add these in this gateway iteration unless the user explicitly expands scope:

- Database-backed `agents`, `corpora`, `documents`, and `ingestion_jobs`.
- `agent_runs` and `agent_run_usage` persistence.
- Private upload flow.
- Local FTS/BM25 index.
- External provider adapter.

The next plan after this should be `usage-accounting-and-static-metadata-to-db`, because the gateway boundary will make usage and metadata persistence easier to add without changing the public chat route again.
