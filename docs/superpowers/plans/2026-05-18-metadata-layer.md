# Database Metadata Layer Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move public agent and corpus metadata out of static arrays and into a SQLite-backed metadata repository while keeping current chat behavior unchanged.

**Architecture:** Add a small server-only metadata layer under `web/src/metadata/` that owns SQLite initialization, seed data, and read APIs for agents and corpora. Keep the existing `agent-registry` and `corpus-registry` modules as thin wrappers so the rest of the app continues to call the same public functions.

**Tech Stack:** TypeScript, Node.js `node:sqlite`, Vitest, Next.js server modules

---

### Task 1: Metadata repository tests

**Files:**
- Create: `web/tests/metadata/metadata-repository.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
it("seeds the default public agent and corpus into sqlite", () => {
  const repository = createMetadataRepository({ databasePath: tempPath });

  expect(repository.listAgents()).toHaveLength(1);
  expect(repository.listCorpora()).toHaveLength(1);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm test tests/metadata/metadata-repository.test.ts -v`
Expected: FAIL because the metadata repository module does not exist yet.

- [ ] **Step 3: Write minimal implementation**

- [ ] **Step 4: Run test to verify it passes**

- [ ] **Step 5: Commit**

### Task 2: SQLite metadata repository

**Files:**
- Create: `web/src/metadata/metadata-repository.ts`
- Create: `web/src/metadata/metadata-seed.ts`
- Modify: `web/src/agents/agent-registry.ts`
- Modify: `web/src/corpora/corpus-registry.ts`

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write minimal implementation**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

### Task 3: Registry compatibility verification

**Files:**
- Modify: `web/tests/agents/agent-registry.test.ts`
- Modify: `web/tests/corpora/corpus-registry.test.ts`

- [ ] **Step 1: Write the failing test**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Write minimal implementation**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

### Task 4: Web runtime verification

**Files:**
- Verify: `web/src/chat/public-chat-service.ts`
- Verify: `web/app/api/chat/route.ts`

- [ ] **Step 1: Run targeted tests**
- [ ] **Step 2: Run typecheck**
- [ ] **Step 3: Run build**
- [ ] **Step 4: Fix any regressions**
