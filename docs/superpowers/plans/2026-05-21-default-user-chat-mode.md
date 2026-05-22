# Default User Chat Mode Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove user-auth flows and run all chat/threads through a single default user while preserving the thread management UI.

**Architecture:** Keep the existing authenticated chat shell and thread persistence, but replace session-based identity with one fixed default user record. The public homepage should route directly into the chat experience, and the thread APIs should read/write against the default user instead of requiring `better-auth` session state.

**Tech Stack:** Next.js App Router, TypeScript, SQLite metadata repository, assistant-ui, Vitest.

---

## Chunk 1: Default User Identity

**Files:**
- Modify: `web/src/auth/session.ts`
- Modify: `web/src/metadata/metadata-repository.ts`
- Modify: `web/src/metadata/types.ts`
- Test: `web/tests/auth/auth-session.test.ts`
- Test: `web/tests/metadata/metadata-repository.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
expect(getDefaultChatUser(repository)).toMatchObject({
  id: "default-user",
  displayName: "Default User",
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm test -- tests/auth/auth-session.test.ts`
Expected: FAIL because the default-user helper does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Implement a default-user helper that creates or returns a single SQLite-backed user record and have chat code use it.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npm test -- tests/auth/auth-session.test.ts tests/metadata/metadata-repository.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/src/auth/session.ts web/src/metadata/metadata-repository.ts web/src/metadata/types.ts web/tests/auth/auth-session.test.ts web/tests/metadata/metadata-repository.test.ts
git commit -m "feat: add default chat user"
```

## Chunk 2: Remove Auth Gating

**Files:**
- Modify: `web/app/page.tsx`
- Modify: `web/app/chat/page.tsx`
- Delete: `web/app/api/auth/[...all]/route.ts`
- Delete: `web/app/sign-in/page.tsx`
- Delete: `web/app/sign-up/page.tsx`
- Delete: `web/src/auth/auth.ts`
- Delete: `web/src/auth/auth-client.ts`
- Delete: `web/src/auth/auth-form.tsx`
- Modify: `web/tests/app/auth-ui-layout.test.ts`
- Modify: `web/tests/app/authenticated-chat-layout.test.ts`
- Modify: `web/tests/app/public-chat-layout.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
expect(source).not.toContain("better-auth");
expect(source).not.toContain("/sign-in");
expect(source).not.toContain("/sign-up");
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm test -- tests/app/auth-ui-layout.test.ts tests/app/authenticated-chat-layout.test.ts`
Expected: FAIL until auth references are removed.

- [ ] **Step 3: Write minimal implementation**

Remove auth-specific pages/routes and make `/` and `/chat` use the default user path directly.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npm test -- tests/app/auth-ui-layout.test.ts tests/app/authenticated-chat-layout.test.ts tests/app/public-chat-layout.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/app/page.tsx web/app/chat/page.tsx web/app/api/auth/[...all]/route.ts web/app/sign-in/page.tsx web/app/sign-up/page.tsx web/src/auth/auth.ts web/src/auth/auth-client.ts web/src/auth/auth-form.tsx web/tests/app/auth-ui-layout.test.ts web/tests/app/authenticated-chat-layout.test.ts web/tests/app/public-chat-layout.test.ts
git commit -m "feat: remove auth gating from chat"
```

## Chunk 3: Public Chat Entry

**Files:**
- Modify: `web/app/page.tsx`
- Modify: `web/src/chat/public-chat-page.tsx`
- Modify: `web/tests/app/public-chat-layout.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
expect(source).toContain('viewer={null}');
expect(source).not.toContain("getOptionalSessionUser");
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm test -- tests/app/public-chat-layout.test.ts`
Expected: FAIL until the public page stops depending on session state.

- [ ] **Step 3: Write minimal implementation**

Keep the public homepage on the public chat shell with no viewer/session branch.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && npm test -- tests/app/public-chat-layout.test.ts`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/app/page.tsx web/src/chat/public-chat-page.tsx web/tests/app/public-chat-layout.test.ts
git commit -m "feat: simplify public chat entry"
```

## Chunk 4: Final Verification

**Files:**
- None

- [ ] **Step 1: Run the full verification**

Run: `cd web && npm run typecheck && npm test && npm run build`
Expected: all three commands exit 0.

- [ ] **Step 2: Smoke test the site**

Run the deployed site and confirm `/` loads the chat shell and `/chat` shows thread UI without login.

- [ ] **Step 3: Commit root docs if needed**

Update the dev plan to reflect that auth has been removed from the MVP slice.

