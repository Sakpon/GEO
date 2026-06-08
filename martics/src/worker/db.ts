import type { Brand, Competitor, Env, Prompt } from "./types";
import { safeJSON } from "./util";

interface BrandRow {
  id: string;
  client_id: string;
  name: string;
  domain: string;
  aliases_json: string;
  competitors_json: string;
  created_at: string;
}

function hydrateBrand(row: BrandRow): Brand {
  return {
    id: row.id,
    client_id: row.client_id,
    name: row.name,
    domain: row.domain,
    aliases: safeJSON<string[]>(row.aliases_json, []),
    competitors: safeJSON<Competitor[]>(row.competitors_json, []),
    created_at: row.created_at,
  };
}

export async function getBrand(env: Env, brandId: string): Promise<Brand | null> {
  const row = await env.DB.prepare("SELECT * FROM brands WHERE id = ?")
    .bind(brandId)
    .first<BrandRow>();
  return row ? hydrateBrand(row) : null;
}

export async function listActivePrompts(env: Env, brandId: string): Promise<Prompt[]> {
  const { results } = await env.DB.prepare(
    "SELECT * FROM prompts WHERE brand_id = ? AND active = 1 ORDER BY created_at",
  )
    .bind(brandId)
    .all<Prompt>();
  return results ?? [];
}

export async function getPrompt(env: Env, promptId: string): Promise<Prompt | null> {
  return env.DB.prepare("SELECT * FROM prompts WHERE id = ?")
    .bind(promptId)
    .first<Prompt>();
}

/** Every brand that has at least one active prompt — drives the daily cron. */
export async function listBrandsWithActivePrompts(env: Env): Promise<Brand[]> {
  const { results } = await env.DB.prepare(
    `SELECT DISTINCT b.* FROM brands b
       JOIN prompts p ON p.brand_id = b.id
      WHERE p.active = 1`,
  ).all<BrandRow>();
  return (results ?? []).map(hydrateBrand);
}
