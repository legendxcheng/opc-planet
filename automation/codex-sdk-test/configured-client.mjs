import { Codex } from "@openai/codex-sdk";
import { fileURLToPath, pathToFileURL } from "node:url";

const apiKey = process.env.CODEX_API_KEY ?? process.env.OPENAI_API_KEY;
const baseUrl = process.env.CODEX_BASE_URL ?? process.env.OPENAI_BASE_URL;

export { apiKey, baseUrl };

if (!apiKey) {
  throw new Error("Set CODEX_API_KEY or OPENAI_API_KEY before running this script.");
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
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
  });

  console.log("Configured Codex client ok.");
  console.log(`baseUrl: ${baseUrl ?? "(default)"}`);
  console.log(`thread type: ${typeof thread}`);
}
