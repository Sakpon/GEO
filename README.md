# thedent.co.th — SEO & GEO Agent Orchestra

A Claude Code subagent system that coordinates four specialists to optimize [thedent.co.th](https://thedent.co.th) — a Thailand-based dental clinic — for both traditional search (SEO) and generative answer engines (GEO: ChatGPT, Perplexity, Google AI Overviews, Gemini, Claude).

## The four agents

| Agent | Responsibility |
|---|---|
| `content-creator` | Writes the copy (TH + EN drafts, meta, FAQ, schema blurbs) |
| `content-planner` | Topic clusters, keyword-to-URL map, editorial calendar, briefs |
| `seo-expert` | Technical + on-page + local SEO audits and requirements |
| `geo-expert` | AI-engine visibility, citation bait, `llms.txt`, entity strategy |

A main (orchestrator) agent reads `CLAUDE.md` and dispatches to these four. It never does their work itself.

## Repository layout

```
.
├── CLAUDE.md                      # Orchestrator routing guide — read first
├── .claude/
│   └── agents/                    # One markdown file per subagent (system prompt)
│       ├── content-creator.md
│       ├── content-planner.md
│       ├── seo-expert.md
│       └── geo-expert.md
├── context/
│   ├── shared/                    # Canonical project context — all agents read
│   │   ├── client-profile.md      # thedent.co.th: services, audience, locations
│   │   ├── brand-voice.md         # Tone, bilingual rules, compliance
│   │   └── optimization-goals.md  # KPIs, priority clusters, targets
│   └── agents/                    # Private per-agent notebooks (persistent memory)
│       ├── content-creator.md
│       ├── content-planner.md
│       ├── seo-expert.md
│       └── geo-expert.md
└── workspace/                     # Agent deliverables
    ├── content/                   # Drafts (by locale and slug)
    ├── plans/                     # Calendars, briefs, cluster maps
    ├── seo-audits/                # Dated SEO audit reports
    └── geo-audits/                # Dated GEO audit reports
```

## How context is maintained separately per agent

The design separates **shared facts** from **per-agent memory**:

- `context/shared/*.md` — single source of truth for client facts. Agents read these every session. Only humans edit these files.
- `context/agents/<agent>.md` — each agent's private notebook. The agent appends new learnings (terminology decisions, audit findings, tracked queries, keyword maps) at the end of every session. No agent writes to another's notebook.

This gives each specialist a long-running memory without polluting others' context windows or risking conflicting edits to the client profile.

## Usage

In Claude Code, inside this repo, just ask the orchestrator in natural language:

```
"Plan the content roadmap for the dental implants pillar."
  → dispatches to content-planner

"Write a Thai blog post on Invisalign recovery using the brief in workspace/plans/briefs/invisalign-recovery.md."
  → dispatches to content-creator

"Audit the homepage for SEO issues."
  → dispatches to seo-expert

"Check which clinics ChatGPT and Perplexity cite for 'veneers in Bangkok'."
  → dispatches to geo-expert

"Draft a full new service page for dental implants end-to-end."
  → chains planner → creator → seo + geo in parallel → creator revise
```

## Before first serious use

1. Verify `context/shared/client-profile.md` against the live site — confirm services, branches, doctor names, differentiators.
2. Confirm the priority cluster order in `context/shared/optimization-goals.md` with the client.
3. Provide Search Console + GA4 access to the SEO agent (noted in its notebook as pending).
4. Decide the AI-bot access posture with the client (default in `context/agents/geo-expert.md` is to allow major answer-engine bots).

## Design principles

- **Single responsibility per agent.** Planner plans, creator writes, auditors audit. They hand structured artifacts to each other.
- **Shared facts, private memory.** Every agent reads the same client profile; each has its own growing notebook.
- **Append, don't overwrite.** Notebooks grow. Shared context is edited deliberately by humans.
- **Surface conflicts.** When SEO and GEO disagree, the answer is to flag the tradeoff to the orchestrator, not pick silently.
- **Never invent clinical facts.** Unknown service details get a `<!-- CONFIRM: ... -->` marker, not a guess.
