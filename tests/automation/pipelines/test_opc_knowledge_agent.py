import tempfile
import unittest
from pathlib import Path

from automation.pipelines.opc_knowledge_agent import (
    build_agent,
    build_run_config,
    format_runtime_error,
    load_agent_config,
    search_knowledge_base_impl,
)


class KnowledgeSearchTests(unittest.TestCase):
    def test_search_knowledge_base_returns_ranked_markdown_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            note = root / "knowledge" / "strategy" / "asset.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                "# Asset\n\nKnowledge assets make a one-person company reusable.\n",
                encoding="utf-8",
            )

            results = search_knowledge_base_impl("knowledge assets", repo_root=root, limit=3)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["path"], "knowledge/strategy/asset.md")
        self.assertIn("Knowledge assets", results[0]["excerpt"])
        self.assertGreater(results[0]["score"], 0)

    def test_build_agent_registers_knowledge_search_tool(self) -> None:
        agent = build_agent()

        self.assertEqual(agent.name, "OPC Knowledge Agent")
        self.assertEqual(len(agent.tools), 1)
        self.assertEqual(agent.tools[0].name, "search_knowledge_base")

    def test_format_runtime_error_redacts_secret_like_values(self) -> None:
        message = format_runtime_error(
            "Incorrect API key provided: cr_24e2dabcdef292d. invalid_api_key"
        )

        self.assertIn("invalid_api_key", message)
        self.assertNotIn("cr_24e2dabcdef292d", message)
        self.assertIn("OPENAI_API_KEY", message)

    def test_load_agent_config_reads_local_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / "openai-agents.local.json"
            config_path.write_text(
                (
                    '{ "api_key": "test-key", "base_url": "https://example.test/v1", '
                    '"model": "gpt-test", "tracing_disabled": false }'
                ),
                encoding="utf-8",
            )

            config = load_agent_config(config_path)

        self.assertEqual(config["api_key"], "test-key")
        self.assertEqual(config["base_url"], "https://example.test/v1")
        self.assertEqual(config["model"], "gpt-test")
        self.assertIs(config["tracing_disabled"], False)

    def test_build_run_config_disables_tracing_by_default(self) -> None:
        run_config = build_run_config({"api_key": "test-key", "base_url": "https://example.test/v1"})

        self.assertIs(run_config.tracing_disabled, True)


if __name__ == "__main__":
    unittest.main()
