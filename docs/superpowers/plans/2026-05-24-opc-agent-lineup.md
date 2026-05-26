# OPC Agent Lineup Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the generic demo agents in the website with an OPC-only agent lineup and keep the guide in sync.

**Architecture:** Keep the existing front-end multi-agent shell, but swap the catalog data from generic software roles to OPC method roles. The agent sidebar, history filter, and active agent card all consume the same shared catalog, so one data update plus a small docs update keeps the UI and guide aligned.

**Tech Stack:** Next.js App Router, TypeScript, React, Vitest, Markdown docs

---

### Task 1: Lock the OPC agent catalog with a regression test

**Files:**
- Create: `web/tests/chat/opc-agents.test.ts`

- [ ] **Step 1: Write the failing test**

```ts
import { describe, expect, it } from "vitest";
import { OPC_AGENTS, OPC_AGENT_CATEGORIES } from "@/chat/opc-agents";

describe("opc agent catalog", () => {
  it("exposes only OPC-related agents and categories", () => {
    expect(OPC_AGENT_CATEGORIES).not.toContain("开发助手");
    expect(OPC_AGENT_CATEGORIES).not.toContain("数据分析");
    expect(OPC_AGENT_CATEGORIES).not.toContain("内容创作");
    expect(OPC_AGENT_CATEGORIES).not.toContain("系统管理");
    expect(OPC_AGENTS.map((agent) => agent.id)).toEqual([
      "opc-orchestrator",
      "resource-audit",
      "niche-positioning",
      "value-proposition",
      "business-model",
      "mvp-validation",
      "conversion-loop",
      "asset-ops",
      "dashboard-review",
    ]);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && npm test -- web/tests/chat/opc-agents.test.ts`
Expected: FAIL because the OPC agent catalog does not exist yet.

### Task 2: Replace the demo agent catalog

**Files:**
- Create: `web/src/chat/opc-agents.ts`
- Modify: `web/src/chat/authenticated-chat-page.tsx`
- Modify: `web/src/chat/agent-sidebar.tsx`
- Modify: `web/src/chat/history-panel.tsx`
- Modify: `web/src/chat/agent-info-card.tsx`
- Delete: `web/src/chat/mock-agents.ts`

- [ ] **Step 1: Write minimal implementation**
- [ ] **Step 2: Run the focused test**

Run: `cd web && npm test -- web/tests/chat/opc-agents.test.ts`
Expected: PASS.

### Task 3: Update the website guide

**Files:**
- Modify: `docs/guide/website_core_code_guide.md`

- [ ] **Step 1: Rewrite the agent section so it describes the OPC-only lineup**
- [ ] **Step 2: Remove references to generic demo agents**

### Task 4: Verify the repo still passes the relevant checks

**Files:**
- None

- [ ] **Step 1: Run the targeted test file**
- [ ] **Step 2: Run TypeScript check for `web/`**

Run:
`cd web && npm run typecheck`

Expected: PASS.
