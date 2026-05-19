import { Codex } from "@openai/codex-sdk";
import pkg from "./package.json" with { type: "json" };

const codex = new Codex();
const thread = codex.startThread();

console.log(`Codex SDK import ok: @openai/codex-sdk ${pkg.dependencies["@openai/codex-sdk"]}`);
console.log(`Codex export type: ${typeof Codex}`);
console.log(`Codex instance ok: ${typeof codex}`);
console.log(`Codex thread ok: ${typeof thread}`);
