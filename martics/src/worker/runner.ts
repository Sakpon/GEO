import { getEngine } from "./engines";
import { parseResponse } from "./parser";
import { runsPerCycle, type Brand, type Env, type Prompt } from "./types";
import { newId, nowISO } from "./util";

export interface RunSummary {
  prompt_id: string;
  engine: string;
  ok: number;
  failed: number;
}

/**
 * Run one prompt against one engine N times, parse each response, and persist a
 * row per run. A failed engine call or parse is recorded as status='failed' and
 * does NOT abort the cycle (spec acceptance criteria).
 */
export async function runPromptEngine(
  env: Env,
  brand: Brand,
  prompt: Prompt,
  engineName: string,
): Promise<RunSummary> {
  const engine = getEngine(engineName);
  const n = runsPerCycle(env);
  const summary: RunSummary = { prompt_id: prompt.id, engine: engineName, ok: 0, failed: 0 };

  for (let i = 0; i < n; i++) {
    const id = newId();
    const runAt = nowISO();

    if (!engine) {
      await insertFailed(env, id, prompt.id, engineName, i, `unknown engine: ${engineName}`, runAt);
      summary.failed++;
      continue;
    }

    try {
      const result = await engine.query(prompt.text_th, env);
      if (!result.ok) {
        await insertFailed(env, id, prompt.id, engineName, i, result.error ?? "engine error", runAt, result.raw);
        summary.failed++;
        continue;
      }

      const parsed = await parseResponse(env, brand, result.raw);
      await env.DB.prepare(
        `INSERT INTO runs
           (id, prompt_id, engine, run_index, status, raw_response,
            brand_mentioned, brand_url_cited, brand_position,
            cited_brands_json, cited_urls_json, run_at)
         VALUES (?, ?, ?, ?, 'ok', ?, ?, ?, ?, ?, ?, ?)`,
      )
        .bind(
          id,
          prompt.id,
          engineName,
          i,
          result.raw,
          parsed.brand_mentioned ? 1 : 0,
          parsed.brand_url_cited ? 1 : 0,
          parsed.brand_position,
          JSON.stringify(parsed.cited_brands),
          JSON.stringify(parsed.cited_urls),
          runAt,
        )
        .run();
      summary.ok++;
    } catch (e) {
      await insertFailed(env, id, prompt.id, engineName, i, (e as Error).message, runAt);
      summary.failed++;
    }
  }

  return summary;
}

async function insertFailed(
  env: Env,
  id: string,
  promptId: string,
  engine: string,
  index: number,
  error: string,
  runAt: string,
  raw = "",
): Promise<void> {
  await env.DB.prepare(
    `INSERT INTO runs (id, prompt_id, engine, run_index, status, error, raw_response, run_at)
     VALUES (?, ?, ?, ?, 'failed', ?, ?, ?)`,
  )
    .bind(id, promptId, engine, index, error.slice(0, 500), raw, runAt)
    .run();
}
