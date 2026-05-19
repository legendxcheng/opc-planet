# Codex SDK Test

Small local smoke test for the TypeScript Codex SDK.

## Setup

```powershell
npm install
```

## Offline Smoke Test

```powershell
npm run smoke
```

This only verifies that `@openai/codex-sdk` can be imported locally.

## Base URL And API Key

The SDK supports constructor options:

```javascript
const codex = new Codex({
  apiKey: process.env.CODEX_API_KEY,
  baseUrl: process.env.CODEX_BASE_URL,
});
```

Local config check:

```powershell
$env:CODEX_API_KEY = "your-key"
$env:CODEX_BASE_URL = "https://your-compatible-endpoint/v1"
npm run config-check
```

The script also accepts `OPENAI_API_KEY` and `OPENAI_BASE_URL`.

## Real SDK Call

Real calls require the local Codex authentication or API configuration expected by the SDK:

```javascript
import { Codex } from "@openai/codex-sdk";

const codex = new Codex();
const thread = codex.startThread();
const turn = await thread.run("Summarize this repository structure.");

console.log(turn.finalResponse);
```
