import type { Engine, EngineResult } from "./types";

/**
 * Phase 4 (P0 — highest Thai usage, hardest, riskiest). Scrapes the consumer
 * ChatGPT app. Risk surface (spec §15): login wall, bot detection, grey-area
 * ToS, per-account answer variance. Must exist before selling to thedent.
 * Stubbed so it slots into the registry without touching the pipeline.
 */
export const chatgptEngine: Engine = {
  name: "chatgpt",
  async query(): Promise<EngineResult> {
    return { ok: false, raw: "", error: "engine_not_implemented: chatgpt (Phase 4)" };
  },
};
