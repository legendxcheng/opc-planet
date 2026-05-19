---
title: Codex SDK 本地测试环境使用指南
type: guide
status: active
tags: [codex-sdk, agent, local-test]
created: 2026-05-12
updated: 2026-05-13
source: automation/codex-sdk-test
confidence: high
---

# Codex SDK 本地测试环境使用指南

## Summary

本指南记录当前仓库中 `@openai/codex-sdk` 的本地测试环境如何安装、配置、验证和排查问题。测试项目位于 `automation/codex-sdk-test/`，用于验证 Codex SDK 能否通过指定的 `baseUrl` 和 `apiKey` 发起真实 Codex agent 调用。

不要把真实 API key 提交到仓库。当前测试脚本如果临时写入了 key，应在提交前改回环境变量读取方式或移动到被 `.gitignore` 忽略的本地配置文件。

## 目录位置

- 测试项目：`automation/codex-sdk-test/`
- SDK 包：`@openai/codex-sdk`
- 关键脚本：
  - `smoke.mjs`：离线导入测试，不调用模型。
  - `configured-client.mjs`：构造带配置的 Codex client。
  - `ping.mjs`：发起一个最小真实调用，验证 `baseUrl` 和 `apiKey` 是否生效。

## 安装

在仓库根目录执行：

```powershell
cd E:\opc-planet\automation\codex-sdk-test
npm install
```

当前已安装版本记录在 `package-lock.json` 中。可以用下面命令查看：

```powershell
npm ls @openai/codex-sdk
```

## 推荐配置方式

优先使用环境变量，不要把真实 key 写进代码：

```powershell
$env:CODEX_API_KEY = "your-api-key"
$env:CODEX_BASE_URL = "https://your-compatible-endpoint/v1"
```

脚本也可以兼容 OpenAI 风格变量名：

```powershell
$env:OPENAI_API_KEY = "your-api-key"
$env:OPENAI_BASE_URL = "https://your-compatible-endpoint/v1"
```

Node 代码中的基础写法：

```javascript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex({
  apiKey: process.env.CODEX_API_KEY ?? process.env.OPENAI_API_KEY,
  baseUrl: process.env.CODEX_BASE_URL ?? process.env.OPENAI_BASE_URL,
});
```

## 当前环境的重要覆盖项

本机 `~/.codex/config.toml` 使用了自定义 provider：

```toml
model_provider = "codex"

[model_providers.codex]
base_url = "..."
```

在这种情况下，只传 SDK 的 `baseUrl` 可能不足以覆盖真实 Codex CLI 运行时的 provider 地址。当前测试中发现：`config-check` 能读到新的 `baseUrl`，但真实 `ping` 仍可能走 `~/.codex/config.toml` 里的旧 provider `base_url`。

解决方式是在 SDK 构造参数里同时覆盖 provider 配置：

```javascript
const codex = new Codex({
  apiKey,
  baseUrl,
  config: {
    model_providers: {
      codex: {
        base_url: baseUrl,
      },
    },
  },
});
```

这会把 Codex CLI 运行时的 `[model_providers.codex].base_url` 一并覆盖，确保真实请求走当前测试配置。

## 验证步骤

### 1. 离线导入测试

```powershell
cd E:\opc-planet\automation\codex-sdk-test
npm run smoke
```

成功时会看到类似输出：

```text
Codex SDK import ok: @openai/codex-sdk ^0.130.0
Codex export type: function
Codex instance ok: object
Codex thread ok: object
```

这个步骤只验证 SDK 包可导入、可构造 client 和 thread，不验证 API key。

### 2. 配置构造测试

```powershell
npm run config-check
```

成功时会看到类似输出：

```text
Configured Codex client ok.
baseUrl: https://your-compatible-endpoint/v1
thread type: object
```

这个步骤验证脚本读到了 `baseUrl` 并能构造 `Codex` client 和 thread，但仍不发起模型请求。

### 3. 真实调用测试

```powershell
npm run ping
```

`ping.mjs` 会发送一个最小请求：

```text
Reply with exactly: codex-sdk-ping-ok
```

成功时预期输出：

```text
codex-sdk-ping-ok
```

如果返回 `401 INVALID_API_KEY`，说明请求已经发到目标服务，但 key 不被接受。

如果返回 `429 Too Many Requests`，说明 `baseUrl` 和 key 至少已经进入目标服务鉴权/配额流程，当前失败原因是限流、额度或并发限制。

## 最小真实调用示例

```javascript
import { Codex } from "@openai/codex-sdk";
import { fileURLToPath } from "node:url";

const apiKey = process.env.CODEX_API_KEY ?? process.env.OPENAI_API_KEY;
const baseUrl = process.env.CODEX_BASE_URL ?? process.env.OPENAI_BASE_URL;

const codex = new Codex({
  apiKey,
  baseUrl,
  config: {
    model_providers: {
      codex: {
        base_url: baseUrl,
      },
    },
  },
});

const thread = codex.startThread({
  workingDirectory: fileURLToPath(new URL("../..", import.meta.url)),
  sandboxMode: "read-only",
  approvalPolicy: "never",
});

const turn = await thread.run("Reply with exactly: codex-sdk-ping-ok");
console.log(turn.finalResponse);
```

Windows 上不要用 `new URL(...).pathname` 直接作为 `workingDirectory`。它会生成 `/E:/...` 这类路径，Codex CLI 可能报 `os error 123`。应使用 `fileURLToPath(...)` 转换为 Windows 原生路径。

## 常见问题

### config-check 显示新 baseUrl，但 ping 仍请求旧地址

检查 `~/.codex/config.toml` 是否配置了 `model_provider` 和 `[model_providers.<name>].base_url`。如果当前 provider 是 `codex`，需要在 SDK 的 `config.model_providers.codex.base_url` 中显式覆盖。

### 401 INVALID_API_KEY

含义：请求到达了某个 API 服务，但该服务不接受当前 key。检查：

- key 是否属于当前 `baseUrl` 对应服务。
- key 是否带错前缀或复制不完整。
- 服务是否要求额外鉴权规则。

### 429 Too Many Requests

含义：请求已经到达服务并进入配额或限流逻辑。检查：

- 服务账号额度是否不足。
- 当前 key 是否有并发或速率限制。
- 代理服务是否对 `/responses` 路径有限制。

### Windows 路径错误 os error 123

使用：

```javascript
import { fileURLToPath } from "node:url";

const workingDirectory = fileURLToPath(new URL("../..", import.meta.url));
```

不要使用：

```javascript
new URL("../..", import.meta.url).pathname
```

## 提交前检查

提交或共享前执行：

```powershell
git diff -- automation/codex-sdk-test
```

确认没有真实 API key、token、cookie 或私密 endpoint 被提交。必要时把 `configured-client.mjs` 改回环境变量读取方式。
