import type { Env } from "../types";
import type { Engine, EngineResult } from "./types";

interface PerplexityResponse {
  choices?: { message?: { content?: string } }[];
  citations?: string[];
  search_results?: { title?: string; url?: string }[];
}

/**
 * Phase-1 scaffold engine. Perplexity is the cleanest API to prove the full
 * pipeline (run → parse → store → aggregate) end-to-end. It is NOT the engine
 * we sell on — Thai usage is low — so never ship a Perplexity-only product.
 */
export const perplexityEngine: Engine = {
  name: "perplexity",

  async query(promptText: string, env: Env): Promise<EngineResult> {
    if (!env.PERPLEXITY_API_KEY) {
      return { ok: false, raw: "", error: "missing PERPLEXITY_API_KEY" };
    }

    let res: Response;
    try {
      res = await fetch("https://api.perplexity.ai/chat/completions", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.PERPLEXITY_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: "sonar",
          messages: [{ role: "user", content: promptText }],
        }),
      });
    } catch (e) {
      return { ok: false, raw: "", error: `network: ${(e as Error).message}` };
    }

    if (!res.ok) {
      const body = await res.text().catch(() => "");
      return { ok: false, raw: "", error: `perplexity ${res.status}: ${body.slice(0, 300)}` };
    }

    const data = (await res.json()) as PerplexityResponse;
    const answer = data.choices?.[0]?.message?.content ?? "";

    // Normalise sources so the parser can extract URL citations regardless of
    // which field Perplexity populates.
    const urls = new Set<string>();
    for (const u of data.citations ?? []) urls.add(u);
    for (const r of data.search_results ?? []) if (r.url) urls.add(r.url);

    const sources = urls.size
      ? "\n\nSOURCES:\n" + [...urls].map((u, i) => `[${i + 1}] ${u}`).join("\n")
      : "";

    return { ok: true, raw: answer + sources };
  },
};
