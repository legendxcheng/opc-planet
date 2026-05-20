# OpenAI Agents Runtime Migration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the public chat legacy Codex SDK runtime with a real OpenAI Agents SDK runtime that uses instructions and a Knowledge Gateway-backed tool to answer from the knowledge base.

**Architecture:** Keep `/api/chat`, `publicChatServiceWithAgent`, `KnowledgeGateway`, metadata usage recording, and the browser stream contract stable. Change only the model runtime in `web/src/chat/public-agent.ts`: build an `Agent` with durable instructions, register a function tool that calls `KnowledgeGateway.search(...)`, and run it through `@openai/agents`.

**Tech Stack:** Next.js App Router, TypeScript, Vitest, `@openai/agents`, `zod`, existing Knowledge Gateway and SQLite metadata.

---

## Task 1: Add Failing Runtime Test

**Files:**
- Modify: `web/tests/chat/public-agent-openai-agents.test.ts`
- Modify later: `web/src/chat/public-agent.ts`

- [x] Write a test that mocks `@openai/agents` and asserts `runPublicAgent(...)` constructs an `Agent` with `instructions`, registers `search_knowledge_base`, and calls `Runner.run(...)`.
- [x] Run the focused test and verify it fails because the current implementation still uses the legacy Codex SDK runtime.

## Task 2: Install And Wire Agents SDK

**Files:**
- Modify: `web/package.json`
- Modify: `web/package-lock.json`
- Modify: `web/src/chat/public-agent.ts`

- [x] Install `@openai/agents`.
- [x] Replace legacy Codex SDK imports and connection helpers with Agents SDK equivalents.
- [x] Build a Knowledge Gateway tool that returns normalized gateway JSON.
- [x] Build public assistant instructions that require using the tool for factual knowledge-base questions, citing sources, and saying when evidence is insufficient.
- [x] Preserve usage metrics and `searchToolCalls`.

## Task 3: Update Docs And Tests

**Files:**
- Modify: `web/README.md`
- Modify: `web/.env.example`
- Modify: `web/tests/chat/public-chat-service.test.ts`
- Modify: `web/tests/agents/knowledge-tool.test.ts` if needed

- [x] Rename runtime docs from the legacy SDK to OpenAI Agents SDK where they describe the public chat runtime.
- [x] Keep environment variables compatible where possible, or document the new preferred variables clearly.
- [x] Run focused tests.

## Task 4: Verify

- [x] Run `cd web; npm run typecheck`.
- [x] Run `cd web; npm test`.
- [x] Run `cd web; npm run build`.
