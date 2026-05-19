from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

from agents import Agent, RunConfig, Runner, function_tool
from agents.models.multi_provider import MultiProvider


REPO_ROOT = Path(__file__).resolve().parents[2]
SEARCH_DIRS = ("knowledge", "sources", "outputs", "agent/prompts")
MAX_FILE_CHARS = 120_000
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "openai-agents.local.json"


def _query_terms(query: str) -> list[str]:
    terms = re.findall(r"[\w\u4e00-\u9fff]+", query.lower())
    return [term for term in terms if len(term) > 1]


def _iter_markdown_files(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for directory in SEARCH_DIRS:
        base = repo_root / directory
        if base.exists():
            files.extend(path for path in base.rglob("*.md") if path.is_file())
    return files


def _build_excerpt(text: str, terms: list[str], width: int = 360) -> str:
    lower = text.lower()
    positions = [lower.find(term) for term in terms if lower.find(term) >= 0]
    start = max(min(positions) - width // 3, 0) if positions else 0
    excerpt = text[start : start + width].replace("\r\n", "\n").replace("\n", " ")
    return re.sub(r"\s+", " ", excerpt).strip()


def search_knowledge_base_impl(
    query: str,
    *,
    repo_root: Path = REPO_ROOT,
    limit: int = 6,
) -> list[dict[str, Any]]:
    """Search curated repository Markdown and return ranked source snippets."""
    terms = _query_terms(query)
    if not terms:
        return []

    matches: list[dict[str, Any]] = []
    for path in _iter_markdown_files(repo_root):
        try:
            text = path.read_text(encoding="utf-8")[:MAX_FILE_CHARS]
        except UnicodeDecodeError:
            continue

        lower = text.lower()
        score = sum(lower.count(term) for term in terms)
        if score <= 0:
            continue

        rel_path = path.relative_to(repo_root).as_posix()
        matches.append(
            {
                "path": rel_path,
                "score": score,
                "excerpt": _build_excerpt(text, terms),
            }
        )

    matches.sort(key=lambda item: (-item["score"], item["path"]))
    return matches[:limit]


@function_tool
def search_knowledge_base(query: str, limit: int = 6) -> str:
    """Search the local OPC knowledge base Markdown files for relevant evidence."""
    safe_limit = min(max(limit, 1), 10)
    results = search_knowledge_base_impl(query, limit=safe_limit)
    return json.dumps(results, ensure_ascii=False, indent=2)


def build_agent() -> Agent:
    return Agent(
        name="OPC Knowledge Agent",
        instructions=(
            "You answer questions about this one-person company knowledge base. "
            "Use search_knowledge_base before answering factual questions. "
            "Base answers on returned evidence, cite source paths, and say when "
            "the repository does not contain enough evidence."
        ),
        tools=[search_knowledge_base],
    )


def load_agent_config(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    config: dict[str, Any] = {}
    if config_path.exists():
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"Agent config must be a JSON object: {config_path}")
        for key in ("api_key", "base_url", "model"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                config[key] = value.strip()
        tracing_disabled = raw.get("tracing_disabled")
        if isinstance(tracing_disabled, bool):
            config["tracing_disabled"] = tracing_disabled

    env_map = {
        "api_key": ("OPENAI_API_KEY",),
        "base_url": ("OPENAI_BASE_URL", "OPENAI_API_BASE"),
        "model": ("OPENAI_MODEL",),
    }
    for key, env_names in env_map.items():
        if key in config:
            continue
        for env_name in env_names:
            value = os.getenv(env_name)
            if value:
                config[key] = value.strip()
                break

    return config


def build_run_config(config: dict[str, Any]) -> RunConfig:
    provider = MultiProvider(
        openai_api_key=config.get("api_key"),
        openai_base_url=config.get("base_url"),
    )
    return RunConfig(
        model=config.get("model"),
        model_provider=provider,
        tracing_disabled=config.get("tracing_disabled", True),
        workflow_name="OPC Knowledge Agent",
    )


def format_runtime_error(error: BaseException | str) -> str:
    message = str(error)
    message = re.sub(r"\b(?:sk|cr)_[A-Za-z0-9_\-]{8,}\b", "[redacted-api-key]", message)
    if "invalid_api_key" in message or "Incorrect API key" in message:
        return (
            "OpenAI Agents SDK call failed: invalid_api_key. "
            "Set a valid OPENAI_API_KEY for the OpenAI API endpoint."
        )
    return f"OpenAI Agents SDK call failed: {message}"


def run_question(question: str, config: dict[str, Any] | None = None) -> str:
    resolved_config = config if config is not None else load_agent_config()
    agent = build_agent()
    result = Runner.run_sync(agent, question, run_config=build_run_config(resolved_config))
    return result.final_output


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask the OPC knowledge base via OpenAI Agents SDK.")
    parser.add_argument("question", nargs="+", help="Question to ask the knowledge-base agent.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to local JSON config with api_key, base_url, and optional model.",
    )
    parser.add_argument(
        "--offline-search-only",
        action="store_true",
        help="Only run local Markdown search and print JSON; no OpenAI API call.",
    )
    args = parser.parse_args()

    question = " ".join(args.question)
    if args.offline_search_only:
        print(json.dumps(search_knowledge_base_impl(question), ensure_ascii=False, indent=2))
        return

    config = load_agent_config(args.config)
    if not config.get("api_key"):
        raise SystemExit(
            f"api_key is required. Set it in {args.config} or OPENAI_API_KEY."
        )

    try:
        print(run_question(question, config))
    except Exception as exc:
        raise SystemExit(format_runtime_error(exc)) from None


if __name__ == "__main__":
    main()
