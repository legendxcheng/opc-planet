# AGENTS.md

## Repository Purpose

This repository is a knowledge-first workspace for a one-person company. Durable knowledge is the primary asset. Code exists to support collection, cleanup, organization, export, and future Agent packaging of that knowledge base.

Default priorities:

1. Keep human-readable Markdown knowledge clean and easy to navigate.
2. Keep automation code separate from long-term knowledge.
3. Preserve sources and raw data so conclusions can be traced.
4. Keep the repository ready to become a knowledge-base Agent later.

## Directory Responsibilities

- `inbox/`: Temporary capture area for unprocessed notes, links, snippets, ideas, and rough drafts. Do not treat content here as canonical.
- `knowledge/`: Canonical long-term knowledge. Put curated, reusable Markdown notes here. Organize by business domain, not by file type.
- `sources/`: External source notes and raw reference records. Use this for web pages, books, papers, podcasts, and other materials that support knowledge claims.
- `outputs/`: Produced artifacts such as reports, briefs, playbooks, SOPs, and decision records intended for reuse or delivery.
- `automation/`: Code that supports crawling, extraction, normalization, ingestion, indexing, or export. Do not place canonical knowledge here.
- `data/`: Data generated or consumed by automation. Prefer `data/raw/` for untouched inputs, `data/interim/` for intermediate results, `data/processed/` for cleaned outputs, and `data/index/` for retrieval indexes.
- `agent/`: Future knowledge-base Agent materials, including profile, prompts, tool definitions, memory rules, and evaluation cases.
- `templates/`: Reusable Markdown templates. Prefer these when creating new notes, source records, decisions, playbooks, or Agent evals.
- `docs/`: Documentation about this repository itself, including directory rules, naming conventions, and implementation plans.
- `config/`: Configuration files for taxonomies, crawler targets, processing rules, or export settings.
- `archive/`: Old or inactive materials retained for historical reference.

## Where To Put New Work

- New durable business knowledge: `knowledge/<domain>/`.
- Unsorted notes or temporary captures: `inbox/`.
- Notes about an external article, book, paper, or podcast: `sources/<source-type>/`.
- Raw crawled files or downloaded source dumps: `data/raw/` or `sources/raw/`, depending on whether the file is a machine artifact or a human reference.
- Cleaned/generated datasets: `data/processed/`.
- Search, embedding, or retrieval indexes: `data/index/`.
- Crawler implementations: `automation/crawlers/`.
- Ingestion, cleaning, transformation, or export flows: `automation/pipelines/`.
- HTML/Markdown/PDF extraction helpers: `automation/extractors/`.
- Frontmatter, taxonomy, naming, or tag cleanup helpers: `automation/normalizers/`.
- Scheduling or task entrypoints: `automation/schedulers/`.
- Agent identity, boundaries, and tone: `agent/profile/`.
- Agent system or role prompts: `agent/prompts/`.
- Agent tool registry or retrieval policy: `agent/tools/`.
- Agent memory schema and canonical facts: `agent/memory/`.
- Agent evaluation cases and regression questions: `agent/evals/`.
- Repository process documentation: `docs/`.
- Reusable note formats: `templates/`.

## Knowledge Structure

Use these `knowledge/` domains unless there is a strong reason to add another:

- `knowledge/company/`: Mission, principles, one-person company model, operating constraints.
- `knowledge/strategy/`: Positioning, roadmap, moat, strategic choices.
- `knowledge/products/`: Ideas, specs, pricing, feedback.
- `knowledge/market/`: Competitors, trends, opportunities.
- `knowledge/customers/`: Personas, interviews, problems.
- `knowledge/operations/`: SOPs, workflows, checklists.
- `knowledge/finance/`: Revenue, costs, metrics.
- `knowledge/legal/`: Contracts, compliance, policies.
- `knowledge/technology/`: Tech stack, architecture, experiments.
- `knowledge/personal/`: Learning, reflections, productivity.

## File Naming

- Use lowercase kebab-case for folders and Markdown files: `pricing-strategy.md`.
- Use date prefixes for time-based notes: `2026-04-25-market-scan.md`.
- Use ADR-style names for decisions: `ADR-0001-use-markdown-as-source-of-truth.md`.
- Avoid spaces, punctuation-heavy names, and overly long file names.

## Markdown Frontmatter

For durable Markdown notes, prefer this frontmatter shape:

```yaml
---
title:
type: concept | source-note | decision | playbook | report
status: draft | active | archived
tags: []
created:
updated:
source:
confidence: low | medium | high
---
```

Use existing templates in `templates/` before inventing a new note format.

## Agent-Ready Writing Rules

- Start long-term notes with a short `Summary` section.
- Separate facts, interpretations, and next actions where possible.
- Include sources and confidence for important claims.
- Keep one file focused on one main topic.
- Prefer clear headings with searchable keywords.
- Do not mix raw scraped data with curated conclusions.

## Coding Guidance

- Keep automation code under `automation/` unless a future package structure is explicitly introduced.
- Keep generated data out of source files and under `data/`.
- Do not place API keys, cookies, credentials, or private tokens in the repository.
- If adding dependencies later, document setup and commands in `README.md` or an appropriate `automation/README.md` section.
- Prefer small, focused scripts and clear pipeline steps over monolithic crawlers.

## Before Adding New Top-Level Directories

Only add a new top-level directory if the existing structure cannot reasonably contain the work. Prefer updating `docs/directory-guide.md` and this file when adding or changing directory responsibilities.
