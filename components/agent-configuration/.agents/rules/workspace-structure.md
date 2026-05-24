# Workspace Structure

## Folder Layout

| Folder | Purpose |
|--------|---------|
| `context/` | Standing background about Takis — identity, expertise, working style |
| `research/` | Synthesis and literature notes — one subfolder per topic |
| `projects/` | Code, scripts, notebooks, and concrete deliverables — one subfolder per initiative |
| `knowledge/` | Static reference Aaron can look up (tooling guides, design specs) |
| `prompts/` | Reusable prompt library for recurring research and analysis tasks |
| `claude.io/` | Aaron's working artifacts: `searches/` for skill outputs, `plans/` for planning outputs |
| `intel/` | Operational intelligence: `log.md` (decisions, append-only) + `learnings.md` (compressed rules, mutable) |
| `archive/` | Completed work and outdated context — moved here, never deleted |

## Context

The `context/` folder contains a single file: `my-information.md`. It is the persistent background Aaron loads for personalised tasks. Reference it in CLAUDE.md as `@context/my-information.md`.

**Contents of `my-information.md`:**
- Identity and preferred names
- Professional profile (role, domain, expertise)
- Technical interests and active learning agenda
- Working style preferences

**Update trigger:** Only when role, expertise, or fundamental working preferences change. This file is stable — not a session log.

## Projects Folder

Each active initiative gets a subfolder under `projects/`. Each subfolder must contain a `README.md` with:
- One-line project description
- Current status: `active` | `planning` | `on-hold`
- Key dates or deadlines
- Links to related `research/` material or `intel/log.md` entries

When a project ends → move the entire folder to `archive/projects/`. Never delete.

**What belongs in `projects/`:** Code, scripts, Jupyter notebooks, model outputs, configuration files — anything you'd run or ship, not just read.

## Knowledge Folder

Static reference material Aaron can look up when needed:

```
knowledge/
├── tooling/     ← Claude Code, MCP, skills, agents — guides and cheatsheets
└── specs/       ← Design documents from brainstorming sessions
```

**`tooling/`** holds guides, cheatsheets, and reference material about the AI tooling ecosystem (Claude Code, MCP servers, superpowers skills, agent patterns). The existing `docs/` content migrates here.

**`specs/`** holds design documents produced by brainstorming sessions — the spec written before an implementation plan. The brainstorming skill defaults to writing specs to `docs/superpowers/specs/`; this workspace overrides that to `knowledge/specs/`.

**What does NOT go here:** Synthesis of your own research work (→ `research/`), working session outputs (→ `claude.io/`), or reusable prompts (→ `prompts/`).

## Prompts Folder

Reusable prompt templates for recurring research and analysis tasks. Aaron consults this folder proactively — not just when explicitly asked.

**How Aaron uses `prompts/`:**
1. **Proactive suggestion**: When a task matches a known prompt type (explaining a paper, generating a study path, mapping a field), Aaron checks `prompts/` and offers the relevant template before proceeding.
2. **Execution**: When you invoke a prompt by name or accept the suggestion, Aaron reads the file and executes it faithfully.
3. **Output structure**: When producing research outputs (study paths, field maps), Aaron uses the matching prompt file as the structural template.

**Naming convention:** `{verb}-{topic}.md` (e.g., `explain-research-paper-three-pass.md`, `generate-study-path-from-papers.md`)

## claude.io Folder

Aaron's working artifacts — everything produced during a session that may be needed later.

```
claude.io/
├── searches/    ← outputs from skill runs (internet, youtube, zotero, tavily…)
├── plans/       ← planning outputs, task decompositions, prompt specifications
└── sessions/    ← end-of-session summaries for cross-session continuity
```

Files follow the naming convention from `output-persistence.md`: `{type}-{brief-description}-{YYYYMMDDHHmm}.md`

**`searches/`** holds skill-run outputs: internet searches, YouTube searches, Zotero lookups, Tavily results.

**`plans/`** holds planning outputs: task decompositions, implementation plans, optimised prompt specifications.

**`sessions/`** holds end-of-session summaries. These give future sessions a fast context ramp — read the most recent session file instead of replaying the full conversation history.

## Intel Folder

The `intel/` folder holds two files with opposite write disciplines:

### `intel/log.md` — Decision Log
Append-only. Never edit or delete past entries. Records choices made before acting, with reasoning preserved.

**What counts as a significant decision:** Tool or approach choices with meaningful alternatives, research direction pivots, architectural decisions in projects. Not every session detail.

**Format:**
```
[YYYY-MM-DD] DECISION: <what was decided> | REASONING: <why this over alternatives>
```

**Example:**
```
[2026-04-04] DECISION: Use conformal prediction for uncertainty quantification in replenishment model | REASONING: Distribution-free coverage guarantees suit the non-stationary demand patterns
```

### `intel/learnings.md` — Operational Learnings
Mutable. Compressed behavioral rules extracted from friction. Deduplicate, merge, evolve — keep high-signal only.

**Add an entry when:** a failure repeats, user repeats an instruction, a workaround is found, a tool limitation is hit, a better strategy is discovered, time was wasted due to a mistake.

**Format:** bullet list, each entry ≤15 words, one line, actionable, generalizable, no explanation.

**Quality filter before adding:** saves future time + reusable across tasks + specific enough to act on. If not → discard.

**Evolution:** merge similar entries, compress into higher-level rules, remove entries that haven't influenced any decision in several sessions.

## Archive

Never delete context files, project folders, or reference materials. Move to `archive/` instead.

```
archive/
├── projects/    ← completed project folders
├── context/     ← outdated context snapshots
└── knowledge/   ← superseded guides and specs
```

`intel/` files are not archived — `log.md` is append-only (history stays in-file), `learnings.md` evolves in-place.

**Why archive instead of delete:** Deleted context is permanently lost. Archived content can be retrieved when a project revives or historical context becomes relevant.

## Maintenance Cadence

- **When starting a task** → check `prompts/` for matching templates; check `intel/log.md` for related decisions; scan `intel/learnings.md` for relevant rules
- **When a project ends** → move folder from `projects/` to `archive/projects/`
- **After a significant decision** → append entry to `intel/log.md`
- **At session end** → review for learnings qualifying for `intel/learnings.md`; deduplicate and evolve existing entries if needed
- **When a knowledge guide becomes outdated** → move to `archive/knowledge/`, add updated version
- **When `my-information.md` needs updating** → edit it directly (no archive needed)
- **When a rule in `.claude/rules/` becomes obsolete** → suggest deletion to the user
