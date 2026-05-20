---
title: Authenticated Multi-Thread Chat Design
type: design
status: draft
tags: [chat, auth, assistant-ui, better-auth, nextjs, sqlite]
created: 2026-05-20
updated: 2026-05-20
source: conversation design; current web implementation; assistant-ui docs; better-auth docs
confidence: medium-high
---

# Authenticated Multi-Thread Chat Design

## Summary

The next product slice should turn the current single-thread public chat into an authenticated multi-thread chat application. The MVP after this design should let a signed-in user create, revisit, rename, archive, and delete chat threads, while keeping the existing answer path intact:

```text
thread-aware UI
  -> authenticated chat route
  -> KnowledgeGateway.search(...)
  -> OpenAI Agents SDK or evidence-injected fallback
```

This slice should not attempt to solve private uploads, quota enforcement, or branch-aware message trees yet. The goal is narrower: establish a reliable user identity layer and a durable per-user thread/message model that future private corpus selection, usage limits, and billing can attach to.

## Current Baseline

Current runtime shape in `web/`:

```text
page.tsx
  -> src/chat/public-chat-page.tsx
  -> useDataStreamRuntime({ api: "/api/chat", protocol: "data-stream" })
  -> app/api/chat/route.ts
  -> publicChatServiceWithAgent(...)
  -> KnowledgeGateway.search(...)
```

What already exists:

- public single-thread chat on `/`
- SQLite metadata repository in `web/src/metadata/metadata-repository.ts`
- business `users` table
- `agent_runs` and `agent_run_usage` tables
- `KnowledgeGateway` access boundary
- OpenAI Agents SDK path plus evidence-injection fallback

What is still missing:

- login/session handling
- stable authenticated user identity in the UI layer
- thread list persistence
- per-thread message persistence
- history-aware chat routing
- product UI for switching between old conversations

## Decision

Use this route:

```text
assistant-ui
  + better-auth
  + server-backed thread list adapter
  + server-backed thread history adapter
  + existing KnowledgeGateway and publicChatServiceWithAgent
```

Specific choices:

1. Keep `assistant-ui` as the chat UI foundation. Do not replace it with a full product fork.
2. Use `better-auth` for sign-in, session, and auth middleware.
3. Keep the existing `users` table as the product-owned business profile table.
4. Add `chat_threads` and `chat_messages` tables to the existing SQLite metadata database.
5. Make `agent_runs.conversation_id` store the thread id so usage and thread history can be joined later.
6. First authenticated chat slice supports linear history only. Do not preserve branch trees in this phase.

## Why This Route

This is the best fit for the current codebase because:

- `assistant-ui` is already integrated and does not need to be replaced.
- `KnowledgeGateway` already gives the answer path a stable service boundary.
- `users`, `agent_runs`, and quota-related fields already exist in the metadata database.
- `better-auth` gives a cleaner long-term fit for private corpus ownership and plan limits than treating auth as a purely frontend concern.

Alternatives not chosen:

- Full product fork such as LibreChat or Open WebUI: too much structural replacement for the current stack.
- Direct adoption of `vercel/chatbot`: useful as a reference, but its runtime is not aligned with the current `KnowledgeGateway -> Agents SDK` answer path.
- Auth-only first, threads later: leaves the main user workflow unfinished and forces another invasive pass across the same routes and UI.

## Auth Model

Use `better-auth` for authentication tables and session handling.

Recommended auth tables:

```text
user
session
account
verification
```

Keep the existing metadata `users` table for business-owned state:

```text
users
  id
  display_name
  status
  private_storage_quota_bytes
  monthly_token_limit
  monthly_cost_limit_usd
  created_at
  updated_at
```

Rules:

- `better-auth.user.id` is the canonical identity id.
- `users.id` mirrors the same id one-to-one.
- On sign-up or first successful sign-in, ensure a `users` row exists.
- `display_name` is initialized from auth profile data and can later diverge if product profile editing is added.

This avoids rewriting all existing business foreign keys while keeping authentication concerns inside the auth library.

## Database Model

Add two new business tables to the existing SQLite metadata database.

### `chat_threads`

```text
id TEXT PRIMARY KEY
user_id TEXT NOT NULL
agent_id TEXT NOT NULL
selected_private_corpus_id TEXT
title TEXT
status TEXT NOT NULL            -- regular | archived
created_at TEXT NOT NULL
updated_at TEXT NOT NULL
last_message_at TEXT
```

Notes:

- `user_id` references `users(id)`.
- `agent_id` references `agents(id)`.
- `selected_private_corpus_id` is nullable and reserved for the next private corpus phase.
- `title` is nullable until the first user message exists.

### `chat_messages`

```text
id TEXT PRIMARY KEY
thread_id TEXT NOT NULL
agent_run_id TEXT
role TEXT NOT NULL              -- user | assistant
content_json TEXT NOT NULL
created_at TEXT NOT NULL
```

Notes:

- `thread_id` references `chat_threads(id)`.
- `agent_run_id` references `agent_runs(id)` and is nullable for user messages.
- `content_json` stores the product-owned message payload needed to rebuild UI history.
- The first slice stores a linear transcript. No `parent_id` tree is persisted yet.

### Relationship To Existing Usage Tables

Each assistant response that reaches the model path should:

1. create an `agent_runs` row with `conversation_id = thread_id`
2. create or update one assistant `chat_messages` row
3. write `agent_run_usage` as today when usage is available

This preserves a clean join path:

```text
user
  -> chat_threads
  -> chat_messages
  -> agent_runs
  -> agent_run_usage
```

## Linear History Constraint

The current UI exposes `edit`, `reload`, and branch navigation. Those controls imply tree-shaped history.

Do not support that in the first authenticated multi-thread slice.

For this phase:

- keep message history linear
- remove or hide branch-picker UI
- remove or hide assistant reload
- remove or hide user edit

Reason:

- a tree-aware persistence model is materially more complex
- it would slow down the core goal of getting per-user threads working
- it is easier to add branch-aware persistence later than to ship a half-correct tree model now

## Thread Title Strategy

Use deterministic title generation in the first slice.

Rule:

- after the first user message is stored, derive `chat_threads.title` from that message
- trim whitespace
- collapse newlines
- truncate to a reasonable short length such as 40 to 60 visible characters

Do not spend an extra model call on title generation in this slice.

This keeps thread creation fast and avoids extra token cost before plan tiers and usage limits exist.

## API Surface

### Auth

Add standard `better-auth` route handling under:

```text
web/app/api/auth/[...all]/route.ts
```

### Thread APIs

Add product-owned thread APIs:

```text
GET    /api/chat/threads
POST   /api/chat/threads
GET    /api/chat/threads/[threadId]
PATCH  /api/chat/threads/[threadId]
DELETE /api/chat/threads/[threadId]
GET    /api/chat/threads/[threadId]/messages
```

Behavior:

- all routes require a valid session
- all routes operate only on threads owned by the signed-in user
- `GET /messages` returns the normalized stored transcript for the selected thread
- `PATCH /[threadId]` supports rename and archive/unarchive

### Chat API

Upgrade `POST /api/chat` into a thread-aware authenticated route.

Required request additions:

```json
{
  "threadId": "thread-123",
  "messages": [...]
}
```

Behavior:

- require a valid session
- verify `threadId` belongs to the current user
- normalize incoming messages as today
- persist newly submitted user message
- call `publicChatServiceWithAgent` with `userId = session.user.id`
- persist assistant reply and link it to the created `agent_run`
- return the same data-stream response format the frontend already expects

## UI Structure

Use a two-pane authenticated chat app.

### Route Layout

Recommended first authenticated route:

```text
/chat
```

Keep the current public single-thread page on `/` for now. This reduces rollout risk and preserves the public demo path while the authenticated experience stabilizes.

### UI Regions

Authenticated `/chat` should contain:

- left sidebar: thread list, new thread action, archived toggle if desired
- main pane: current chat thread
- lightweight user menu for sign out

### User Flows

Required flows:

1. sign in
2. land in `/chat`
3. create a new empty thread
4. send first message
5. thread title appears automatically
6. switch to another thread
7. revisit old messages
8. rename, archive, or delete a thread

The UI should feel like a working app, not a public demo with auth added on top.

## assistant-ui Integration

The thread UI should stay on `assistant-ui`, but stop being a single free-floating runtime.

Target shape:

```text
server-backed RemoteThreadListAdapter
  + RuntimeAdapterProvider(history)
  + existing thread component
```

The frontend should provide:

- a remote thread list adapter backed by `/api/chat/threads`
- a remote thread history adapter backed by `/api/chat/threads/[threadId]/messages`
- a thread-scoped runtime that posts to `/api/chat` with the active `threadId`

The current `data-stream` response contract should remain intact.

## Route Protection

Apply auth checks at three layers:

1. page-level redirect for authenticated-only routes such as `/chat`
2. API-level session validation for `/api/chat` and `/api/chat/threads/*`
3. ownership validation before reading or mutating any thread or message rows

The page redirect improves UX. The API checks remain mandatory.

## Migration Strategy

Implement in this order:

1. add auth
2. add thread/message schema
3. add thread APIs
4. upgrade `/api/chat` to authenticated thread-aware mode
5. add authenticated chat page with sidebar and thread switching
6. disable branch/edit/reload controls for this slice

Keep the public `/` experience alive until the authenticated `/chat` path passes smoke and regression tests.

## Testing Strategy

Add tests for:

- auth session resolution helpers
- `users` profile auto-provisioning on sign-in
- thread ownership checks
- thread CRUD APIs
- message load and append behavior
- `/api/chat` rejecting missing or foreign-owned `threadId`
- `/api/chat` persisting user and assistant transcript records
- `agent_runs.conversation_id` storing the thread id
- thread list UI behavior with mocked adapters

Also re-run:

- `npm run typecheck`
- `npm test`
- `npm run build`

## Non-Goals

Do not include these in the first authenticated multi-thread slice:

- private corpus upload UI
- quota enforcement
- billing pages
- branch-aware message trees
- model-generated thread titles
- multiple private corpora selection in the chat UI
- root-route redesign

## Open Questions

- Should archived threads stay visible in the main list by default, or move behind a filter?
- Should deleting a thread be soft-delete first, or immediate delete for the first slice?
- Should anonymous public chat remain permanently available on `/`, or only during migration?
- At what point should the current SQLite metadata layer move to Drizzle/Postgres for production multi-user traffic?
