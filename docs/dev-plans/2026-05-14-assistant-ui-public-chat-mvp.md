# Assistant-UI Public Chat MVP Implementation Plan

> **Status:** Completed and merged into the main `web/` worktree. The next active work is the Knowledge Gateway migration, which keeps the same browser chat contract while moving retrieval behind `KnowledgeGateway.search(...)`.

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a centered single-thread `assistant-ui` chat page to `web/` that first streams mock responses from `/api/chat`, then upgrades the same endpoint to a real OpenAI Agents SDK-backed public knowledge assistant.

**Architecture:** Keep the frontend contract stable by using `assistant-ui`'s data stream runtime from day one. The UI should always talk to `POST /api/chat`; phase A returns mock streamed text and fake citations, while phase C replaces only the backend implementation with OpenAI Agents SDK plus the existing local Markdown retrieval modules. Product-specific chat code should live under `web/src/chat/`, generated `assistant-ui` and `shadcn/ui` pieces should stay under `web/components/`, and the current knowledge-search code under `web/src/knowledge/` should remain reusable by the future agent backend.

**Tech Stack:** Next.js App Router, React 19, TypeScript, `assistant-ui`, `@assistant-ui/react-data-stream`, `assistant-stream`, Tailwind CSS, `shadcn/ui`, `@openai/agents`, `zod`, Vitest.

---

## Progress Update

- Verified on 2026-05-14 inside the assistant UI implementation worktree before merge:
  - `npm ls --depth=0`
  - `npm test`
  - `npm run build`
  - `npm run typecheck`
- Manual browser checks on `http://localhost:3025` confirmed:
  - centered single-thread homepage layout
  - no sidebar/history UI
  - `POST /api/chat` request flow from the page
  - send state transitioning to `Stop generating`
- Historical RED steps are marked complete where the corresponding tests and implementation now exist; this sync focused on current GREEN-state verification rather than re-introducing failing states.
- Current follow-up item:
  - the real OpenAI-backed manual path still cannot complete end-to-end in this environment because requests to `api.openai.com:443` time out

- Additional stabilization completed after the first status sync:
  - added route coverage for the non-mock public service path
  - changed SDK failure behavior to fall back to local public-corpus answers instead of surfacing raw runtime errors to end users
  - ported `.worktrees` TypeScript/Next watcher boundary protection from the main `web/` worktree
  - added `suppressHydrationWarning` coverage to the public chat root layout
  - added `app/icon.svg` to remove the dev `favicon` 404 noise
  - stabilized `typecheck` with `npx next typegen && npx tsc --noEmit --incremental false`

---

## Scope

- In scope:
  - Replace the current placeholder homepage with a single centered chat thread.
  - Use `assistant-ui` official UI primitives and generated thread components.
  - Introduce `Tailwind + shadcn/ui` because the chosen `assistant-ui` thread component depends on them.
  - Keep one stable route: `web/app/api/chat/route.ts`.
  - Phase A: stream deterministic mock responses for UI verification.
  - Phase C: replace the mock stream with an OpenAI Agents SDK-backed public knowledge answer path.

- Out of scope:
  - Sidebar thread list or persistent conversation history.
  - Authentication and per-user quotas.
  - Private corpora, uploads, or object storage.
  - Provider adapters other than the local retriever.
  - Full token accounting and billing tables.

## Reference Inputs

- Main architecture spec: `docs/dev-plans/2026-05-13-agent-knowledge-architecture.md`
- Current TS retrieval baseline:
  - `web/src/knowledge/search-local-knowledge.ts`
  - `web/src/agents/knowledge-tool.ts`
  - `web/tests/knowledge/search-local-knowledge.test.ts`
  - `web/tests/agents/knowledge-tool.test.ts`
- Official docs used for this plan:
  - `assistant-ui` CLI: https://www.assistant-ui.com/docs/cli
  - `assistant-ui` Thread component: https://www.assistant-ui.com/docs/ui/thread
  - `assistant-ui` Data Stream runtime: https://www.assistant-ui.com/docs/runtimes/custom/data-stream
  - Runtime layering reference: https://www.assistant-ui.com/docs/runtimes/concepts/architecture

## File Structure

The implementation should converge on these responsibilities:

- `web/app/page.tsx`
  - Home page entrypoint. Should become a thin wrapper that renders the chat experience, not a large component.
- `web/app/api/chat/route.ts`
  - Stable HTTP endpoint consumed by `useDataStreamRuntime({ api: "/api/chat" })`.
  - Phase A returns mock streamed answers.
  - Phase C delegates to an OpenAI Agents SDK chat service.
- `web/app/globals.css`
  - Tailwind base import and app-level theme tokens for the public chat page.
- `web/components/assistant-ui/thread.tsx`
  - Generated thread UI from `assistant-ui` CLI. Keep this close to upstream structure and only make controlled branding edits.
- `web/components/assistant-ui/*`
  - Other generated assistant-ui support components such as markdown text, attachments, reasoning, and tool fallback.
- `web/components/ui/*`
  - Generated `shadcn/ui` support components used by the thread.
- `web/lib/utils.ts`
  - `shadcn/ui` utility helpers.
- `web/src/chat/public-chat-page.tsx`
  - Product-owned page shell that wires runtime provider, heading copy, and centered layout around the generated thread.
- `web/src/chat/mock-chat-stream.ts`
  - Deterministic mock answer generator for phase A.
- `web/src/chat/mock-citations.ts`
  - Fake citation payloads and response-copy fixtures used by the mock route.
- `web/src/chat/data-stream-response.ts`
  - Helpers for building `assistant-stream` responses so the route body stays small.
- `web/src/chat/request-messages.ts`
  - Convert `assistant-ui` incoming request payloads into the internal format needed by the agent service.
- `web/src/chat/public-chat-service.ts`
  - Phase C orchestration entrypoint called by `route.ts`. Hides OpenAI Agents SDK details from the route.
- `web/src/chat/public-agent.ts`
  - Build the public knowledge agent and register the search tool.
- `web/src/corpora/public-corpora.ts`
  - Phase C public corpus definitions for the first agent slice.
- `web/tests/chat/mock-chat-stream.test.ts`
  - Tests for deterministic mock output.
- `web/tests/chat/api-chat-route.test.ts`
  - Route-level tests for request validation and data stream response behavior.
- `web/tests/chat/request-messages.test.ts`
  - Tests for assistant-ui request conversion before connecting to the real agent.
- `web/tests/chat/public-chat-service.test.ts`
  - Phase C tests for corpus selection and citation formatting.

## Delivery Strategy

Build this in two explicit phases under one stable UI contract:

1. Phase A: `assistant-ui` page + `/api/chat` mock stream.
2. Phase C: keep the same page and route, replace only the route internals with OpenAI Agents SDK plus the existing local public knowledge search.

Do not skip phase A. The main reason for phase A is to lock the UI contract, interaction model, and layout before any model/runtime debugging begins.

## Chunk 1: UI Foundation And Stable Chat Contract

### Task 1: Install `assistant-ui`, Tailwind, and `shadcn/ui` into the existing `web/` app

**Files:**
- Modify: `web/package.json`
- Modify: `web/app/globals.css`
- Create or update via CLI: `web/components/assistant-ui/thread.tsx`
- Create or update via CLI: `web/components/assistant-ui/markdown-text.tsx`
- Create or update via CLI: `web/components/ui/button.tsx`
- Create or update via CLI: `web/lib/utils.ts`
- Create or update via CLI: `web/components.json`
- Create or update via CLI: `web/postcss.config.mjs`

- [x] **Step 1: Record the current dependency baseline**

Run:

```bash
cd web
npm ls --depth=0
```

Expected: the current app dependency tree prints successfully so the post-init diff is easy to review.

- [x] **Step 2: Initialize `assistant-ui` in the existing project**

Run:

```bash
cd web
npx assistant-ui@latest init
```

Expected: the CLI detects the existing Next.js project, installs `assistant-ui` dependencies, and generates the default thread component plus required `shadcn/ui` support files.

- [x] **Step 3: Confirm Tailwind and generated component files exist**

Run:

```bash
cd web
Get-ChildItem components\\assistant-ui, components\\ui, lib, app | Out-String
```

Expected: generated assistant-ui/shadcn files are present and `app/globals.css` now includes the required Tailwind base.

- [x] **Step 4: Run typecheck immediately after generation**

Run:

```bash
cd web
npm run typecheck
```

Expected: PASS. If it fails, fix generation/config issues before touching product code.

- [ ] **Step 5: Commit the generated foundation separately**

```bash
git add web/package.json web/package-lock.json web/app/globals.css web/components web/lib web/components.json web/postcss.config.mjs
git commit -m "feat(web): initialize assistant-ui chat foundation"
```

### Task 2: Replace the placeholder homepage with the centered single-thread chat shell

**Files:**
- Create: `web/src/chat/public-chat-page.tsx`
- Modify: `web/app/page.tsx`
- Modify: `web/app/layout.tsx`
- Modify: `web/app/globals.css`
- Optionally adjust: `web/components/assistant-ui/thread.tsx`

- [x] **Step 1: Create the product-owned chat page shell**

Implement `web/src/chat/public-chat-page.tsx` as a client component that:

- uses `AssistantRuntimeProvider`
- uses `useDataStreamRuntime({ api: "/api/chat" })`
- wraps the generated `<Thread />`
- applies the centered single-thread layout chosen during brainstorming
- includes product copy such as:
  - eyebrow: `OPC Planet`
  - heading: `Ask the public knowledge base`
  - short helper text for what can be asked

- [x] **Step 2: Replace the placeholder homepage**

Modify `web/app/page.tsx` so it only renders `<PublicChatPage />`.

- [x] **Step 3: Update root metadata**

Modify `web/app/layout.tsx` metadata so the browser title and description describe the public knowledge assistant, not the temporary workspace foundation page.

- [x] **Step 4: Adjust global theme tokens for the new chat page**

Keep the current warm editorial palette unless it clashes with generated thread styles. Avoid a generic grey SaaS look.

- [x] **Step 5: Verify the page builds**

Run:

```bash
cd web
npm run build
```

Expected: PASS and the Next.js app compiles the new page without route/runtime errors.

- [x] **Step 6: Manual browser smoke-check**

Run:

```bash
cd web
npm run dev
```

Expected: the home page shows the centered single-thread chat layout with no sidebar and no right-rail.

- [ ] **Step 7: Commit the page shell**

```bash
git add web/app/page.tsx web/app/layout.tsx web/app/globals.css web/src/chat/public-chat-page.tsx web/components/assistant-ui/thread.tsx
git commit -m "feat(web): add centered public chat page shell"
```

### Task 3: Add the stable `/api/chat` mock stream route

**Files:**
- Create: `web/app/api/chat/route.ts`
- Create: `web/src/chat/mock-chat-stream.ts`
- Create: `web/src/chat/mock-citations.ts`
- Create: `web/src/chat/data-stream-response.ts`
- Test: `web/tests/chat/mock-chat-stream.test.ts`
- Test: `web/tests/chat/api-chat-route.test.ts`

- [x] **Step 1: Write the failing mock stream tests**

Add tests that verify:

- the mock stream returns a deterministic answer for a known user prompt
- the route rejects malformed JSON or missing messages with a `400`-class response
- the route returns a streaming response object on a valid request

- [x] **Step 2: Run the new tests to confirm failure**

Run:

```bash
cd web
npm test -- --runInBand tests/chat/mock-chat-stream.test.ts tests/chat/api-chat-route.test.ts
```

Expected: FAIL because the route and mock stream helpers do not exist yet.

- [x] **Step 3: Implement the mock response helpers**

`web/src/chat/mock-chat-stream.ts` should:

- inspect the latest user message text
- return one of a few deterministic canned answers
- include a small fake citation block in the answer text for UI verification

`web/src/chat/data-stream-response.ts` should:

- centralize `assistant-stream` response creation
- expose a helper that appends text chunks in timed or chunked sequence so the UI visibly streams

- [x] **Step 4: Implement `POST /api/chat`**

`web/app/api/chat/route.ts` should:

- parse the standard `assistant-ui` request body
- validate that at least one message exists
- call the mock stream helper
- emit a valid assistant data stream response

- [x] **Step 5: Re-run the focused tests**

Run:

```bash
cd web
npm test -- --runInBand tests/chat/mock-chat-stream.test.ts tests/chat/api-chat-route.test.ts
```

Expected: PASS.

- [x] **Step 6: Manual stream verification**

With `npm run dev` still running, ask a few questions in the browser UI and confirm:

- the assistant text streams rather than appearing in one flush
- the send button disables during a request
- cancellation or repeat-send does not hard-crash the page

- [ ] **Step 7: Commit the stable mock contract**

```bash
git add web/app/api/chat/route.ts web/src/chat/mock-chat-stream.ts web/src/chat/mock-citations.ts web/src/chat/data-stream-response.ts web/tests/chat/mock-chat-stream.test.ts web/tests/chat/api-chat-route.test.ts
git commit -m "feat(web): add mock assistant-ui chat stream route"
```

## Chunk 2: Swap The Mock Route To OpenAI Agents SDK

### Task 4: Install real backend runtime dependencies without changing the UI contract

**Files:**
- Modify: `web/package.json`
- Modify: `web/package-lock.json`
- Create if missing: `web/src/corpora/public-corpora.ts`
- Create if missing: `web/src/chat/request-messages.ts`
- Test: `web/tests/chat/request-messages.test.ts`

- [x] **Step 1: Add backend dependencies**

Run:

```bash
cd web
npm install @openai/agents zod assistant-stream
```

Expected: packages install cleanly and no generated frontend components are overwritten.

- [x] **Step 2: Write the failing request-conversion tests**

`web/tests/chat/request-messages.test.ts` should verify conversion of assistant-ui request messages into the internal representation used by the public agent service, especially:

- latest user message extraction
- preservation of prior user/assistant turns
- graceful handling of empty or malformed content arrays

- [x] **Step 3: Run the focused tests to confirm failure**

Run:

```bash
cd web
npm test -- --runInBand tests/chat/request-messages.test.ts
```

Expected: FAIL because the conversion helper does not exist yet.

- [x] **Step 4: Implement request conversion and corpus definitions**

`web/src/chat/request-messages.ts` should normalize the inbound `messages` payload.

`web/src/corpora/public-corpora.ts` should define the first public corpus map for this slice, likely starting with one corpus such as `opc-core` pointing at the minimum directories needed for good answers.

- [x] **Step 5: Re-run focused tests and typecheck**

Run:

```bash
cd web
npm test -- --runInBand tests/chat/request-messages.test.ts
npm run typecheck
```

Expected: PASS.

- [ ] **Step 6: Commit dependency and conversion prep**

```bash
git add web/package.json web/package-lock.json web/src/chat/request-messages.ts web/src/corpora/public-corpora.ts web/tests/chat/request-messages.test.ts
git commit -m "feat(web): prepare public chat backend inputs"
```

### Task 5: Build the public knowledge agent service on top of the current local retrieval baseline

**Files:**
- Create: `web/src/chat/public-agent.ts`
- Create: `web/src/chat/public-chat-service.ts`
- Modify or reuse: `web/src/agents/knowledge-tool.ts`
- Modify or reuse: `web/src/knowledge/search-local-knowledge.ts`
- Test: `web/tests/chat/public-chat-service.test.ts`
- Test: `web/tests/agents/knowledge-tool.test.ts`

- [x] **Step 1: Write the failing public service tests**

Add tests that verify:

- the public chat service only uses configured public corpora paths
- the service returns normalized citation data for matching results
- empty-search situations return a safe fallback response instead of throwing

- [x] **Step 2: Run the focused tests to confirm failure**

Run:

```bash
cd web
npm test -- --runInBand tests/chat/public-chat-service.test.ts tests/agents/knowledge-tool.test.ts
```

Expected: FAIL because the public chat service and/or corpus-aware tool wiring are incomplete.

- [x] **Step 3: Implement a single public agent slice**

`web/src/chat/public-agent.ts` should:

- build one public knowledge agent for this MVP
- register a search tool backed by the current local Markdown retrieval modules
- keep the tool contract narrow and public-only

`web/src/chat/public-chat-service.ts` should:

- accept normalized request messages
- run the public agent
- return final answer text plus normalized citations

Do not add private corpus logic in this task.

- [x] **Step 4: Re-run focused tests**

Run:

```bash
cd web
npm test -- --runInBand tests/chat/public-chat-service.test.ts tests/agents/knowledge-tool.test.ts
```

Expected: PASS.

- [x] **Step 5: Manual non-UI smoke check**

Add a temporary script or direct test invocation only if needed to verify the agent service can answer one known prompt from repository content before reconnecting the route.

- [ ] **Step 6: Commit the agent service**

```bash
git add web/src/chat/public-agent.ts web/src/chat/public-chat-service.ts web/src/agents/knowledge-tool.ts web/src/knowledge/search-local-knowledge.ts web/tests/chat/public-chat-service.test.ts web/tests/agents/knowledge-tool.test.ts
git commit -m "feat(web): add public knowledge chat service"
```

### Task 6: Swap `/api/chat` from mock mode to the real public agent backend

**Files:**
- Modify: `web/app/api/chat/route.ts`
- Modify: `web/src/chat/data-stream-response.ts`
- Modify: `web/src/chat/public-chat-service.ts`
- Test: `web/tests/chat/api-chat-route.test.ts`

- [x] **Step 1: Extend route tests for the real backend path**

Add assertions that:

- the route now calls the public chat service instead of the mock helper
- successful answers stream back through the same response protocol
- service failures become controlled error messages rather than framework stack traces

- [x] **Step 2: Run the route tests to confirm failure**

Run:

```bash
cd web
npm test -- --runInBand tests/chat/api-chat-route.test.ts
```

Expected: FAIL because the route still points at the mock implementation.

- [x] **Step 3: Replace the mock implementation behind the existing route**

Keep `POST /api/chat` stable. The only change should be:

- parse request
- normalize messages
- call `publicChatService`
- stream answer text and citations back through the same `assistant-stream` helper

If the route still needs a feature flag for mock mode during development, isolate that flag in one small branch near the top of the route.

- [x] **Step 4: Re-run the route tests**

Run:

```bash
cd web
npm test -- --runInBand tests/chat/api-chat-route.test.ts
```

Expected: PASS.

- [x] **Step 5: Run full project verification**

Run:

```bash
cd web
npm run typecheck
npm test
npm run build
```

Expected: all three commands PASS.

- [ ] **Step 6: Manual browser verification against the real backend**

In the browser:

- ask a question known to match `knowledge/strategy/opc/`
- confirm the response is no longer canned mock copy
- confirm the page still uses the same centered single-thread layout
- confirm no sidebar/history UI has appeared

- [ ] **Step 7: Commit the real backend swap**

```bash
git add web/app/api/chat/route.ts web/src/chat/data-stream-response.ts web/src/chat/public-chat-service.ts web/tests/chat/api-chat-route.test.ts
git commit -m "feat(web): connect public chat route to openai agents sdk"
```

## Chunk 3: Stabilization And Cleanup

### Task 7: Remove mock-only leftovers and document the slice

**Files:**
- Modify or delete: `web/src/chat/mock-chat-stream.ts`
- Modify or delete: `web/src/chat/mock-citations.ts`
- Modify: `web/README.md`
- Optionally create: `web/docs/public-chat-mvp.md`

- [x] **Step 1: Decide whether mock mode remains as a dev flag**

If mock mode is still useful for local UI work without API keys, keep it behind a small explicit switch. If not, delete the mock helpers.

- [x] **Step 2: Document the final run path**

Document:

- required environment variables for OpenAI Agents SDK
- how `assistant-ui` talks to `/api/chat`
- where public corpus definitions live
- how to run typecheck, tests, and build

- [ ] **Step 3: Run final verification**

Run:

```bash
cd web
npm run typecheck
npm test
npm run build
```

Expected: PASS after cleanup.

- [ ] **Step 4: Commit documentation and cleanup**

```bash
git add web/README.md web/src/chat/mock-chat-stream.ts web/src/chat/mock-citations.ts web/docs/public-chat-mvp.md
git commit -m "docs(web): document public chat mvp workflow"
```

## Acceptance Criteria

The plan is complete when all of these are true:

- The home page is a single centered `assistant-ui` thread, not the old placeholder panel.
- The page talks to `POST /api/chat` through `useDataStreamRuntime`.
- Phase A can be verified with a mock stream without changing the page implementation.
- Phase C swaps only the route internals and still uses the same page/runtime contract.
- The real backend can answer from repository public knowledge using the existing TypeScript local retrieval baseline.
- `npm run typecheck`, `npm test`, and `npm run build` all pass in `web/`.

## Current Acceptance Snapshot

- Satisfied inside the dedicated `assistant-ui` worktree:
  - the homepage is a centered single-thread `assistant-ui` chat page
  - the page talks to `POST /api/chat` through `useDataStreamRuntime`
  - mock helpers, public corpora, request normalization, and the route swap all exist
  - current worktree verification commands pass
  - browser verification confirms the route falls back to local public-corpus answers when the OpenAI SDK times out
- Remaining limitation:
  - real OpenAI-backed browser verification is still blocked by outbound timeout

## Risks And Guardrails

- Do not let generated `assistant-ui` code swallow product layout decisions.
  - Keep branding/layout wrappers in `web/src/chat/public-chat-page.tsx`, not buried inside generated primitives.
- Do not build sidebar/history now.
  - That would drag in persistence concerns before the public answer loop is stable.
- Do not jump directly from current placeholder UI to OpenAI Agents SDK without phase A.
  - The debugging surface becomes too wide: UI, stream protocol, route parsing, model behavior, and retrieval all change at once.
- Do not widen public corpora early.
  - Start with the minimum corpus set needed for a convincing demo and expand after benchmark queries exist.

## Recommended Execution Order

Run the chunks exactly in this order:

1. Chunk 1, Task 1-3
2. Chunk 2, Task 4-6
3. Chunk 3, Task 7

The hard checkpoint is after Task 3. If the mock page is not clean and stable, do not proceed to OpenAI Agents SDK integration.

## Handoff

Plan updated after merge. Continue with the Knowledge Gateway migration as the active backend architecture follow-up.
