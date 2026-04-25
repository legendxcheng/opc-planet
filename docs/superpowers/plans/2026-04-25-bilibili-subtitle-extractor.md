# Bilibili Subtitle Extractor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a small reusable extractor that checks and downloads existing Bilibili subtitle tracks for a BV video while keeping credentials out of the repository.

**Architecture:** A standard-library Python module under `automation/extractors/` parses BV IDs, queries Bilibili view/player APIs, downloads subtitle JSON, and writes raw plus readable outputs. Tests use fake HTTP responses so behavior is verified without network or login.

**Tech Stack:** Python standard library, pytest for tests, Bilibili public/player APIs, optional local Cookie via environment variable or ignored local file.

---

## Chunk 1: Extractor Core

### Task 1: Parser and HTTP seam

**Files:**
- Create: `automation/extractors/bilibili_subtitle.py`
- Test: `tests/automation/extractors/test_bilibili_subtitle.py`

- [ ] Write failing tests for BV parsing and API orchestration.
- [ ] Run focused pytest and confirm failures.
- [ ] Implement parser, API client seam, and status model.
- [ ] Run focused pytest and confirm pass.

### Task 2: Subtitle persistence and CLI

**Files:**
- Modify: `automation/extractors/bilibili_subtitle.py`
- Create: `automation/extractors/README.md`

- [ ] Write failing tests for JSON/TXT output.
- [ ] Implement subtitle body parsing and safe output names.
- [ ] Add CLI usage docs and credential safety notes.
- [ ] Run focused pytest and a live check when network is available.
