# Knowledge Base Scaffold Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an initial knowledge-first repository scaffold for a one-person company, with automation and future Agent packaging kept as first-class but supporting concerns.

**Architecture:** Markdown remains the source of truth for durable knowledge. Code and generated data are separated into automation and data directories. Agent-related prompts, memory rules, tools, and evaluations live under `agent/` so future retrieval and tool-calling work can be added without reorganizing the knowledge base.

**Tech Stack:** Markdown, Git, optional Python/Node automation later.

---

## Chunk 1: Repository Scaffold

### Task 1: Create directory skeleton

**Files:**
- Create: `inbox/.gitkeep`
- Create: `knowledge/**/.gitkeep`
- Create: `sources/**/.gitkeep`
- Create: `outputs/**/.gitkeep`
- Create: `agent/**/.gitkeep`
- Create: `automation/**/.gitkeep`
- Create: `data/**/.gitkeep`
- Create: `templates/.gitkeep`
- Create: `config/.gitkeep`
- Create: `archive/.gitkeep`

- [ ] **Step 1: Create directories with placeholders**

Create all planned top-level and second-level directories using `.gitkeep` placeholders where no README is needed yet.

- [ ] **Step 2: Verify tree**

Run: `Get-ChildItem -Recurse -Directory | Select-Object FullName`
Expected: the knowledge, sources, outputs, agent, automation, data, templates, docs, config, and archive directories exist.

### Task 2: Add repository guide

**Files:**
- Create: `README.md`
- Create: `docs/directory-guide.md`
- Create: `docs/naming-conventions.md`

- [ ] **Step 1: Write README**

Include purpose, structure, daily workflow, and Agent-ready principles.

- [ ] **Step 2: Write directory guide**

Explain what belongs in each major directory.

- [ ] **Step 3: Write naming conventions**

Define file naming, dates, statuses, and frontmatter expectations.

### Task 3: Add reusable templates

**Files:**
- Create: `templates/knowledge-note.md`
- Create: `templates/source-note.md`
- Create: `templates/decision-record.md`
- Create: `templates/playbook.md`
- Create: `templates/agent-eval-case.md`

- [ ] **Step 1: Create knowledge note template**

Add frontmatter and sections for durable knowledge.

- [ ] **Step 2: Create source and output templates**

Add source note, decision record, and playbook formats.

- [ ] **Step 3: Create Agent evaluation template**

Add question, context, expected behavior, and failure modes.

### Task 4: Add ignore rules

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Add generated-data ignores**

Ignore caches, virtual environments, build outputs, logs, and generated indexes while preserving `.gitkeep` placeholders.

- [ ] **Step 2: Verify Git status**

Run: `git status --short`
Expected: only intentional scaffold files appear.
