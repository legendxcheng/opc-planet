# Web Git Release Deploy Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a repeatable Git-based deployment path for the `web/` Next.js project to the existing Ubuntu cloud server.

**Architecture:** The local operator script connects over SSH, prepares a release under `/srv/opc-website/releases/<timestamp>-<commit>`, checks out the requested Git ref from the `opc-website` repository, installs dependencies, runs verification, builds Next.js, switches the `current` symlink, writes a systemd unit and Nginx reverse proxy when requested, and restarts the service. Runtime secrets and SQLite metadata live under `/srv/opc-website/shared`.

**Tech Stack:** PowerShell, OpenSSH, Git, npm, Next.js, systemd, Nginx.

---

### Task 1: Static Checks

**Files:**
- Create: `tests/tools/test-web-deploy-script.ps1`

- [ ] **Step 1: Write failing static checks**

Create a PowerShell test that asserts `tools/deploy-web.ps1` exists and contains the required deployment boundaries: SSH invocation, Git checkout, npm verification, systemd restart, Nginx config, shared env path, and SQLite metadata path.

- [ ] **Step 2: Run test to verify it fails**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File tests/tools/test-web-deploy-script.ps1`

Expected: FAIL because `tools/deploy-web.ps1` does not exist yet.

### Task 2: Deployment Script

**Files:**
- Create: `tools/deploy-web.ps1`

- [ ] **Step 1: Implement deploy script**

The script accepts `-HostName`, `-User`, `-KeyPath`, `-RepoUrl`, `-Ref`, `-AppRoot`, `-Port`, `-Domain`, `-SkipTests`, `-SkipBuild`, and `-SetupServer`. It sends a bash deployment program to the server through SSH and executes it with environment variables.

- [ ] **Step 2: Run static checks**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File tests/tools/test-web-deploy-script.ps1`

Expected: PASS.

### Task 3: Deployment Guide

**Files:**
- Create: `docs/guide/web-git-deploy-guide.md`

- [ ] **Step 1: Document operator workflow**

Document first-time server setup, required env file, normal deploy, rollback, logs, and why Docker is deferred.

- [ ] **Step 2: Verify docs mention the existing SSH guide**

Run: `rg -n "ssh-cloud-server-login-guide|deploy-web.ps1|systemctl|journalctl|rollback|Docker" docs/guide/web-git-deploy-guide.md`

Expected: all key terms are present.

### Task 4: Final Verification

**Files:**
- Verify: `tools/deploy-web.ps1`
- Verify: `tests/tools/test-web-deploy-script.ps1`
- Verify: `docs/guide/web-git-deploy-guide.md`

- [ ] **Step 1: Parse PowerShell files**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -Command "[scriptblock]::Create((Get-Content -Raw 'tools/deploy-web.ps1')) > $null; [scriptblock]::Create((Get-Content -Raw 'tests/tools/test-web-deploy-script.ps1')) > $null"`

Expected: exit 0.

- [ ] **Step 2: Run static checks**

Run: `powershell -NoProfile -ExecutionPolicy Bypass -File tests/tools/test-web-deploy-script.ps1`

Expected: exit 0.

- [ ] **Step 3: Inspect git diff**

Run: `git diff -- tools/deploy-web.ps1 tests/tools/test-web-deploy-script.ps1 docs/guide/web-git-deploy-guide.md docs/superpowers/plans/2026-05-19-web-git-release-deploy.md`

Expected: only the planned deployment files are changed.
