import type { Engine, EngineResult } from "./types";

/**
 * Phase 3 (P0 — first real-usage engine). Google AI Overview is scraped via
 * Cloudflare Browser Rendering / Playwright; the parsed text then flows through
 * the SAME pipeline as Perplexity. Stubbed here so the registry and data model
 * are engine-agnostic from day one.
 *
 * Open question (spec §15): Browser Rendering vs a separate Playwright container,
 * and how to normalise "cited" (AIO link) across engines.
 */
export const googleAioEngine: Engine = {
  name: "google_aio",
  async query(): Promise<EngineResult> {
    return { ok: false, raw: "", error: "engine_not_implemented: google_aio (Phase 3)" };
  },
};
