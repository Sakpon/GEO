import Anthropic from "@anthropic-ai/sdk";
import type { Brand, Env, ParseResult } from "./types";
import { domainOf } from "./util";

// Structured-output schema mirrors the parser contract (spec §9). Using
// output_config.format guarantees valid JSON — no ```json fence-stripping.
// brand_position uses 0 for "not mentioned" (nullable unions are avoided for
// schema portability); we convert 0 -> null after parsing.
const PARSE_SCHEMA = {
  type: "object",
  additionalProperties: false,
  properties: {
    brand_mentioned: { type: "boolean" },
    brand_url_cited: { type: "boolean" },
    brand_position: {
      type: "integer",
      description: "1 = brand mentioned first; 0 = not mentioned",
    },
    cited_brands: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          name: { type: "string" },
          position: { type: "integer" },
        },
        required: ["name", "position"],
      },
    },
    cited_urls: {
      type: "array",
      items: {
        type: "object",
        additionalProperties: false,
        properties: {
          url: { type: "string" },
          domain: { type: "string" },
          owner: { type: "string", enum: ["brand", "competitor", "other"] },
        },
        required: ["url", "domain", "owner"],
      },
    },
  },
  required: ["brand_mentioned", "brand_url_cited", "brand_position", "cited_brands", "cited_urls"],
} as const;

function systemPrompt(brand: Brand): string {
  const competitors = brand.competitors
    .map((c) => {
      const aliases = (c.aliases ?? []).join(", ");
      return `- ${c.name}${c.domain ? ` (${c.domain})` : ""}${aliases ? ` [aliases: ${aliases}]` : ""}`;
    })
    .join("\n");

  return `You analyse an AI assistant's answer to a Thai-language search query and extract brand mentions and URL citations. Respond ONLY via the structured output schema.

TARGET BRAND:
- Name: ${brand.name}
- Domain: ${brand.domain}
- Aliases (count any of these as the brand): ${brand.aliases.join(", ") || "(none)"}

COMPETITORS:
${competitors || "(none provided)"}

RULES:
- brand_mentioned: true if the target brand (by name OR any alias) appears anywhere in the answer text.
- brand_position: the 1-based ordinal of the target brand among all brands/businesses mentioned in the answer (1 = mentioned first). Use 0 if the brand is not mentioned.
- brand_url_cited: true only if a URL on the brand's own domain appears in the sources/links.
- cited_brands: every distinct brand/business named in the answer, each with its 1-based mention position. Match Thai aliases to the canonical competitor/brand name (e.g. "เดอะ เดนท์" -> "The Dent").
- cited_urls: every URL in the answer or its sources. Set owner="brand" if the URL's domain matches the target brand's domain, "competitor" if it matches a competitor domain, otherwise "other".
- Be precise. Do not invent brands or URLs that are not present.`;
}

export async function parseResponse(
  env: Env,
  brand: Brand,
  rawResponse: string,
): Promise<ParseResult> {
  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });

  const message = await client.messages.create({
    model: env.PARSER_MODEL || "claude-sonnet-4-6",
    max_tokens: 2048,
    system: systemPrompt(brand),
    messages: [
      {
        role: "user",
        content: `AI ANSWER TO ANALYSE:\n\n${rawResponse}`,
      },
    ],
    output_config: { format: { type: "json_schema", schema: PARSE_SCHEMA } },
  } as Anthropic.MessageCreateParamsNonStreaming);

  const text = message.content.find((b) => b.type === "text");
  if (!text || text.type !== "text") {
    throw new Error("parser returned no text block");
  }

  const parsed = JSON.parse(text.text) as ParseResult & { brand_position: number };

  // Normalise: backfill domains, clamp position 0 -> null.
  return {
    brand_mentioned: !!parsed.brand_mentioned,
    brand_url_cited: !!parsed.brand_url_cited,
    brand_position: parsed.brand_position && parsed.brand_position > 0 ? parsed.brand_position : null,
    cited_brands: Array.isArray(parsed.cited_brands) ? parsed.cited_brands : [],
    cited_urls: (Array.isArray(parsed.cited_urls) ? parsed.cited_urls : []).map((u) => ({
      ...u,
      domain: u.domain || domainOf(u.url),
    })),
  };
}
