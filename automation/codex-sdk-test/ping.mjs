import { Codex } from "@openai/codex-sdk";
import { fileURLToPath } from "node:url";
import { apiKey, baseUrl } from "./configured-client.mjs";

if (!apiKey) {
  throw new Error("Set CODEX_API_KEY or OPENAI_API_KEY before running this script.");
}

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

console.error(`ping baseUrl: ${baseUrl ?? "(default)"}`);
console.error("ping apiKey source: configured-client.mjs");
console.error(`ping apiKey length: ${apiKey.length}`);

const thread = codex.startThread({
  workingDirectory: fileURLToPath(new URL("../..", import.meta.url)),
  sandboxMode: "read-only",
  approvalPolicy: "never",
});

const turn = await thread.run("Reply with exactly: codex-sdk-ping-ok");
console.log(turn.finalResponse);
