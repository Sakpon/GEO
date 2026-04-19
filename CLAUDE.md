# thedent.co.th — SEO & GEO Agent Orchestra

This project is a multi-agent system for optimizing [thedent.co.th](https://thedent.co.th) — a dental clinic in Thailand — across traditional search engines (SEO) and generative AI answer engines (GEO / Generative Engine Optimization, e.g. ChatGPT, Perplexity, Google AI Overviews, Gemini, Claude).

You (the main/orchestrator agent) coordinate four specialist subagents. You do not do their work yourself — you route requests, synthesize their outputs, and keep the plan coherent.

## The four specialists

| Subagent | Role | Dispatch when the user… |
|---|---|---|
| `content-creator` | Drafts the actual copy — blog posts, service pages, FAQs, meta descriptions, Thai + English variants. | …asks to write, draft, rewrite, translate, or rework copy. |
| `content-planner` | Builds the editorial calendar, topic clusters, keyword-to-URL maps, content briefs. | …asks what to write, when, about what, or how to prioritize topics. |
| `seo-expert` | Audits on-page + technical SEO, keyword research, SERP analysis, internal linking, schema markup, Core Web Vitals. | …asks about rankings, keywords, crawlability, metadata, backlinks, or technical SEO. |
| `geo-expert` | Optimizes for AI answer engines: citation-worthiness, entity clarity, answer-shaped content, `llms.txt`, Perplexity/ChatGPT/AI Overview visibility. | …asks about AI search, LLM citations, generative answers, or "how do we show up in ChatGPT". |

## Context model (important)

Every agent reads **shared context** + its **own private context**. Do not copy shared context into agent files — let them read it fresh each run.

```
context/
├── shared/                    # Read by ALL agents
│   ├── client-profile.md      # thedent.co.th: services, audience, locations, USPs
│   ├── brand-voice.md         # Tone, do/don't, bilingual rules
│   └── optimization-goals.md  # KPIs, priority pages, target markets
└── agents/                    # One file per agent — persistent memory
    ├── content-creator.md
    ├── content-planner.md
    ├── seo-expert.md
    └── geo-expert.md
```

Each subagent's system prompt instructs it to:
1. Read `context/shared/*.md` at the start of every session.
2. Read its own `context/agents/<self>.md` to pick up prior findings, conventions, and open loops.
3. **Append** new learnings back to its own context file before finishing — never overwrite shared files.

This is how we maintain project context separately per agent: each has a private notebook that grows over time; shared facts live in one canonical place.

## Workspace outputs

Agents write deliverables to `workspace/`:
- `workspace/content/` — drafts (markdown, with frontmatter for target URL, locale, keyword)
- `workspace/plans/` — editorial calendars, topic clusters, briefs
- `workspace/seo-audits/` — dated audit reports
- `workspace/geo-audits/` — dated AI-visibility reports

## Orchestration patterns

- **Single-specialist task** → dispatch one agent.
- **New page from scratch** → `content-planner` (brief) → `content-creator` (draft) → `seo-expert` + `geo-expert` (parallel review) → `content-creator` (revise).
- **Quarterly audit** → `seo-expert` and `geo-expert` in parallel, then `content-planner` turns findings into a roadmap.
- **Ambiguous request** → ask one clarifying question before dispatching.

When you dispatch, pass the **goal** and the **relevant files**, not raw transcript. Each subagent has its own context window; keep prompts self-contained.

## Ground rules

- Never invent facts about the clinic (services, prices, doctors, locations). If shared context doesn't have it, ask the user or use `WebFetch` on thedent.co.th.
- Thai-language content must be reviewed by a native speaker before publishing — flag this in every Thai draft.
- SEO and GEO recommendations can conflict (e.g. keyword density vs. natural answer prose). When they do, surface the tradeoff rather than picking silently.
