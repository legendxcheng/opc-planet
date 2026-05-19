# OpenAI Agents SDK Smoke Test

This repository has a local `.venv` with `openai-agents` installed for quick experimentation.

## Offline Smoke Test

```powershell
.\.venv\Scripts\python.exe automation\smoke_openai_agents.py
```

This only verifies that the Python Agents SDK can be imported and an `Agent` can be constructed.

## Real Agent Call

Real calls require `OPENAI_API_KEY` in the environment. Keep keys outside the repository, for example in a local shell session or ignored `.env` file.

You can also use an ignored local JSON config:

```powershell
Copy-Item config\openai-agents.example.json config\openai-agents.local.json
```

Then edit `config\openai-agents.local.json`:

```json
{
  "api_key": "your-api-key",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-5.2",
  "tracing_disabled": true
}
```

## OPC Knowledge Agent

`automation/pipelines/opc_knowledge_agent.py` builds a minimal OpenAI Agents SDK agent with one local tool:

- `search_knowledge_base(query, limit)`: searches Markdown under `knowledge/`, `sources/`, `outputs/`, and `agent/prompts/`, then returns JSON snippets with source paths.

Offline local search, no API key required:

```powershell
.\.venv\Scripts\python.exe -m automation.pipelines.opc_knowledge_agent --offline-search-only "一人公司 知识资产"
```

Real Agents SDK call:

```powershell
.\.venv\Scripts\python.exe -m automation.pipelines.opc_knowledge_agent "一人公司为什么要把知识资产化？"
```

Focused offline tests:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.automation.pipelines.test_opc_knowledge_agent
```
