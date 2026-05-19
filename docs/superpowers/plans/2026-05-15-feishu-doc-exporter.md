# Feishu Doc Exporter Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local CLI that opens Chrome, reuses a persistent Feishu login, exports one Feishu document URL to Markdown, and saves it under `sources/dbs-feishu/`.

**Architecture:** Keep the tool isolated under `tools/feishu-doc-exporter/`. The CLI will ensure the cloud-document-converter extension is built into a local cache, launch a persistent Chrome profile with that unpacked extension loaded, wait for the page-level copy action, read clipboard Markdown, and write a uniquely named `.md` file to the target source directory.

**Tech Stack:** Node.js, `playwright-core`, the existing `cloud-document-converter` extension source in `temp/cloud-document-converter/`, Chrome on Windows.

---

### Task 1: Scaffold the tool package

**Files:**
- Create: `tools/feishu-doc-exporter/package.json`
- Create: `tools/feishu-doc-exporter/.gitignore`
- Create: `tools/feishu-doc-exporter/README.md`
- Modify: `docs/directory-guide.md`
- Modify: `README.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Add the new tool directory docs and package manifest**
- [ ] **Step 2: Confirm the repo guide mentions `tools/`**

### Task 2: Implement export flow

**Files:**
- Create: `tools/feishu-doc-exporter/src/export.mjs`
- Create: `tools/feishu-doc-exporter/src/extension-cache.mjs`
- Create: `tools/feishu-doc-exporter/src/path-utils.mjs`

- [ ] **Step 1: Write the CLI and helper modules**
- [ ] **Step 2: Verify the script can resolve Chrome, build or reuse the extension, and save Markdown to `sources/dbs-feishu/`**

### Task 3: Add lightweight verification

**Files:**
- Create: `tools/feishu-doc-exporter/test/path-utils.test.mjs`

- [ ] **Step 1: Add a focused unit test for filename sanitization and de-duplication**
- [ ] **Step 2: Run the test and the CLI help path**
- [ ] **Step 3: Confirm the exported file lands in the requested folder**
