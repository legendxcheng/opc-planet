# Authenticated Multi-Thread Chat Foundation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add authenticated, per-user multi-thread chat on top of the current public assistant stack without changing the existing `KnowledgeGateway` answer path.

**Architecture:** Keep `assistant-ui` and the current `/api/chat` streaming contract, add `better-auth` for session handling, extend the SQLite metadata database with `chat_threads` and `chat_messages`, and introduce thread-aware APIs plus a new authenticated `/chat` app shell. The first slice keeps history linear and disables branch-aware controls.

**Tech Stack:** Next.js App Router, TypeScript, `assistant-ui`, `better-auth`, Node.js `node:sqlite`, Vitest

---

### Task 1: Add auth foundation and business-profile provisioning

**Files:**
- Create: `web/src/auth/auth.ts`
- Create: `web/src/auth/session.ts`
- Create: `web/app/api/auth/[...all]/route.ts`
- Create: `web/tests/auth/auth-session.test.ts`
- Modify: `web/package.json`
- Modify: `web/README.md`

- [ ] **Step 1: Write the failing tests**

```ts
it("returns null when no authenticated session exists", async () => {
  expect(await getOptionalSessionUser()).toBeNull();
});

it("creates a product profile row for a newly signed-in auth user", async () => {
  const user = await ensureBusinessUserProfile({
    id: "user-1",
    name: "Alice",
  });

  expect(user.id).toBe("user-1");
  expect(user.displayName).toBe("Alice");
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd web && npm test tests/auth/auth-session.test.ts -v`
Expected: FAIL because the auth modules do not exist yet.

- [ ] **Step 3: Add dependencies and minimal auth implementation**

Implement:

- `better-auth` configuration in `src/auth/auth.ts`
- session/user helpers in `src/auth/session.ts`
- a route handler under `app/api/auth/[...all]/route.ts`
- business-profile provisioning that inserts into the existing `users` table on first sign-in

- [ ] **Step 4: Re-run the targeted tests**

Run: `cd web && npm test tests/auth/auth-session.test.ts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/package.json web/README.md web/src/auth web/app/api/auth web/tests/auth
git commit -m "feat: add better-auth foundation"
```

### Task 2: Extend the metadata layer with chat threads and messages

**Files:**
- Modify: `web/src/metadata/types.ts`
- Modify: `web/src/metadata/metadata-repository.ts`
- Modify: `web/tests/metadata/metadata-repository.test.ts`

- [ ] **Step 1: Write the failing tests**

```ts
it("persists chat threads scoped to a user", () => {
  const thread = repository.insertChatThread({
    userId: "user-1",
    agentId: "opc-public-assistant",
    selectedPrivateCorpusId: null,
    title: null,
    status: "regular",
    lastMessageAt: null,
  });

  expect(repository.listChatThreadsByUserId("user-1")).toEqual([thread]);
});

it("stores linear chat messages for a thread", () => {
  const message = repository.insertChatMessage({
    threadId: "thread-1",
    agentRunId: null,
    role: "user",
    contentJson: JSON.stringify({ text: "hello" }),
  });

  expect(repository.listChatMessagesByThreadId("thread-1")[0]?.id).toBe(message.id);
});
```

- [ ] **Step 2: Run the metadata tests to verify they fail**

Run: `cd web && npm test tests/metadata/metadata-repository.test.ts -v`
Expected: FAIL because chat thread/message methods and schema do not exist yet.

- [ ] **Step 3: Add the schema and repository methods**

Implement:

- `ChatThreadRecord`, `ChatMessageRecord`, and insert types in `types.ts`
- `chat_threads` and `chat_messages` tables in `metadata-repository.ts`
- list/get/insert/update/delete methods for threads
- list/insert methods for messages

Keep `agent_runs.conversation_id` untouched for now; later tasks will start writing thread ids into it.

- [ ] **Step 4: Re-run the metadata tests**

Run: `cd web && npm test tests/metadata/metadata-repository.test.ts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/metadata/types.ts web/src/metadata/metadata-repository.ts web/tests/metadata/metadata-repository.test.ts
git commit -m "feat: add chat thread persistence"
```

### Task 3: Add a server-side thread service and thread APIs

**Files:**
- Create: `web/src/chat/chat-thread-service.ts`
- Create: `web/src/chat/thread-title.ts`
- Create: `web/app/api/chat/threads/route.ts`
- Create: `web/app/api/chat/threads/[threadId]/route.ts`
- Create: `web/app/api/chat/threads/[threadId]/messages/route.ts`
- Create: `web/tests/chat/api-chat-threads-route.test.ts`

- [ ] **Step 1: Write the failing API tests**

```ts
it("returns only the signed-in user's threads", async () => {
  const response = await GET_threads_as("user-1");
  expect(response.status).toBe(200);
  expect(await response.json()).toMatchObject({
    threads: [{ userId: "user-1" }],
  });
});

it("rejects access to another user's thread", async () => {
  const response = await GET_thread_as("user-2", "thread-owned-by-user-1");
  expect(response.status).toBe(404);
});
```

- [ ] **Step 2: Run the targeted route tests**

Run: `cd web && npm test tests/chat/api-chat-threads-route.test.ts -v`
Expected: FAIL because the thread routes and service do not exist yet.

- [ ] **Step 3: Implement the service and routes**

Implement:

- thread CRUD methods in `chat-thread-service.ts`
- deterministic first-message title generation in `thread-title.ts`
- authenticated route handlers for thread list, thread detail, and thread messages
- ownership checks against `session.user.id`

- [ ] **Step 4: Re-run the targeted tests**

Run: `cd web && npm test tests/chat/api-chat-threads-route.test.ts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/src/chat/chat-thread-service.ts web/src/chat/thread-title.ts web/app/api/chat/threads web/tests/chat/api-chat-threads-route.test.ts
git commit -m "feat: add thread management api"
```

### Task 4: Make `/api/chat` authenticated and thread-aware

**Files:**
- Modify: `web/app/api/chat/route.ts`
- Modify: `web/src/chat/public-chat-service.ts`
- Modify: `web/tests/chat/api-chat-route.test.ts`
- Modify: `web/tests/chat/public-chat-service.test.ts`

- [ ] **Step 1: Write the failing chat-route tests**

```ts
it("rejects requests without a session", async () => {
  const response = await POST_chat({ threadId: "thread-1", messages });
  expect(response.status).toBe(401);
});

it("stores the active thread id in the created agent run", async () => {
  await POST_chat_as("user-1", { threadId: "thread-1", messages });
  expect(repository.listAgentRuns()[0]?.conversationId).toBe("thread-1");
});
```

- [ ] **Step 2: Run the targeted chat tests**

Run: `cd web && npm test tests/chat/api-chat-route.test.ts tests/chat/public-chat-service.test.ts -v`
Expected: FAIL because `/api/chat` is still public and thread-unaware.

- [ ] **Step 3: Implement the route upgrade**

Implement:

- session validation in `/api/chat`
- `threadId` request validation and ownership checks
- persistence of the latest user message before generation
- assistant reply persistence after generation
- `userId = session.user.id` and `conversationId = threadId` passed into the current service path

- [ ] **Step 4: Re-run the targeted chat tests**

Run: `cd web && npm test tests/chat/api-chat-route.test.ts tests/chat/public-chat-service.test.ts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/app/api/chat/route.ts web/src/chat/public-chat-service.ts web/tests/chat/api-chat-route.test.ts web/tests/chat/public-chat-service.test.ts
git commit -m "feat: persist authenticated chat runs by thread"
```

### Task 5: Build the authenticated `/chat` application shell

**Files:**
- Create: `web/app/chat/page.tsx`
- Create: `web/src/chat/authenticated-chat-page.tsx`
- Create: `web/src/chat/chat-sidebar.tsx`
- Create: `web/src/chat/chat-thread-list-adapter.tsx`
- Create: `web/src/chat/chat-thread-history-adapter.tsx`
- Create: `web/tests/app/authenticated-chat-layout.test.ts`
- Modify: `web/app/globals.css`

- [ ] **Step 1: Write the failing UI test**

```ts
it("renders a sidebar and thread pane on the authenticated chat route", async () => {
  const source = await readAppPage("/chat");
  expect(source).toContain("chat-sidebar");
  expect(source).toContain("chat-thread-pane");
});
```

- [ ] **Step 2: Run the targeted layout test**

Run: `cd web && npm test tests/app/authenticated-chat-layout.test.ts -v`
Expected: FAIL because the `/chat` route and authenticated shell do not exist yet.

- [ ] **Step 3: Implement the app shell and remote adapters**

Implement:

- `/chat` page that requires a session and renders the app shell
- sidebar UI for thread creation and switching
- `assistant-ui` remote thread list adapter backed by `/api/chat/threads`
- `assistant-ui` history adapter backed by `/api/chat/threads/[threadId]/messages`
- thread-scoped runtime posting to `/api/chat` with `threadId`

- [ ] **Step 4: Re-run the targeted layout test**

Run: `cd web && npm test tests/app/authenticated-chat-layout.test.ts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/app/chat/page.tsx web/src/chat/authenticated-chat-page.tsx web/src/chat/chat-sidebar.tsx web/src/chat/chat-thread-list-adapter.tsx web/src/chat/chat-thread-history-adapter.tsx web/tests/app/authenticated-chat-layout.test.ts web/app/globals.css
git commit -m "feat: add authenticated multi-thread chat shell"
```

### Task 6: Remove unsupported branch-oriented controls for this slice

**Files:**
- Modify: `web/components/assistant-ui/thread.tsx`
- Modify: `web/tests/app/public-chat-layout.test.ts`

- [ ] **Step 1: Write the failing UI assertions**

```ts
it("does not render branch or edit controls in authenticated chat mode", () => {
  expect(renderedThread).not.toContain("aui_user_branch-picker");
  expect(renderedThread).not.toContain("重新生成");
});
```

- [ ] **Step 2: Run the targeted tests**

Run: `cd web && npm test tests/app/public-chat-layout.test.ts -v`
Expected: FAIL because the thread component still renders edit/reload/branch controls.

- [ ] **Step 3: Simplify the thread controls**

Implement:

- remove or gate branch picker, user edit, and assistant reload controls
- keep copy and export controls
- keep the thread component visually aligned with the existing design language

- [ ] **Step 4: Re-run the targeted tests**

Run: `cd web && npm test tests/app/public-chat-layout.test.ts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add web/components/assistant-ui/thread.tsx web/tests/app/public-chat-layout.test.ts
git commit -m "feat: simplify thread controls for linear history"
```

### Task 7: End-to-end verification

**Files:**
- Verify: `web/README.md`
- Verify: `docs/dev-plans/2026-05-13-agent-knowledge-architecture.md`

- [ ] **Step 1: Run the full automated checks**

Run: `cd web && npm run typecheck`
Expected: PASS

Run: `cd web && npm test`
Expected: PASS

Run: `cd web && npm run build`
Expected: PASS

- [ ] **Step 2: Smoke the authenticated flow locally**

Run: `cd web && npm run dev -- --port 3026`

Verify manually:

- sign in succeeds
- `/chat` loads
- creating a thread works
- refreshing the page preserves the selected thread history
- switching threads shows the correct transcript
- `/api/chat` still streams an answer

- [ ] **Step 3: Update docs**

Document:

- required auth env vars
- how `/chat` differs from the public `/` page
- the current linear-history limitation

- [ ] **Step 4: Commit**

```bash
git add web/README.md docs/dev-plans/2026-05-13-agent-knowledge-architecture.md
git commit -m "docs: document authenticated multi-thread chat foundation"
```
