import type { Engine } from "./types";
import { perplexityEngine } from "./perplexity";
import { googleAioEngine } from "./googleAio";
import { chatgptEngine } from "./chatgpt";

const REGISTRY: Record<string, Engine> = {
  [perplexityEngine.name]: perplexityEngine,
  [googleAioEngine.name]: googleAioEngine,
  [chatgptEngine.name]: chatgptEngine,
};

export function getEngine(name: string): Engine | undefined {
  return REGISTRY[name];
}

export const ENGINE_NAMES = Object.keys(REGISTRY);
