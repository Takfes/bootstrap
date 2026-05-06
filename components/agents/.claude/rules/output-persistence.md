# Output Persistence

## Save-Before-You-Close Protocol
After executing any search skill or producing a plan / task decomposition, always ask the user whether the result should be saved to disk before closing the task.

**Offer to save when the output is:**
- A search result with more than 3–4 distinct findings
- A plan, task breakdown, or decision tree
- A research summary the user may want to reference later
- Any structured output that took significant effort to produce

**Do not offer to save:** Trivial lookups, one-liner answers, content that is already stored elsewhere.

## File Naming Convention
- **Pattern:** `{type}-{brief-description}-{YYYYMMDDHHmm}.md`
- Lowercase with hyphens; description 3–5 words; datetime in `YYYYMMDDHHmm` format; `.md` for all outputs.

**Subfolder routing inside `claude.io/`:**

| Output type | Subfolder | Prefix |
|-------------|-----------|--------|
| Skill-run search results (internet, YouTube, Zotero, Tavily…) | `claude.io/searches/` | skill name (e.g. `youtube-`, `zotero-`, `internet-`, `tavily-`) |
| Plans, task decompositions, prompt specifications | `claude.io/plans/` | `planning-` |
| Research summaries | `claude.io/plans/` | `research-` |
| Session summaries | `claude.io/sessions/` | `session-` |

**Examples:**
- `claude.io/searches/youtube-search-claude-code-mcp-202602081553.md`
- `claude.io/searches/zotero-search-agentic-frameworks-202602071230.md`
- `claude.io/plans/planning-optimize-skills-zotero-search-202602061800.md`
- `claude.io/sessions/session-workspace-restructure-202604050900.md`

## Saved File Structure
Every saved output should start with a header block so it is self-contained when read later:

```markdown
# [Title]

**Date:** YYYY-MM-DD HH:MM
**Query / Task:** [what was asked or searched]
**Source:** [skill name, tool, or origin]

---

[content]
```

## Formatting Requirements
Outputs should be human-readable and grep-friendly: use markdown headers, bullet points, and datetime stamps so files are searchable from the terminal without opening them.

## Session Summaries

At the end of every substantive session, offer to write a session summary to `claude.io/sessions/`. Filename: `session-{brief-description}-{YYYYMMDDHHmm}.md`.

**Format:**
```markdown
# Session Summary — [Topic]

**Date:** YYYY-MM-DD HH:MM
**Duration:** [rough estimate]
**Focus:** [one-line summary of what was worked on]

## What Was Done
[Bullet list of concrete outputs produced this session]

## Decisions Made
[Any significant decisions — link or copy to intel/log.md if they warrant logging]

## Open Threads
[Things discussed but not resolved; next steps if any were identified]

## Files Created or Modified
[List of file paths touched this session]
```

**When to offer:** After any session involving research synthesis, planning, brainstorming, or structural changes to the workspace. Not after trivial lookups or single-question exchanges.

## Working with Prepared Prompts
When executing a pre-prepared plan that contains specific prompts or instructions:

1. **Use verbatim** — Extract and use exact text. Do not paraphrase, abbreviate, or improve prepared prompts. They are specification inputs, not templates.
2. **Distinguish operation types** — Query/Ask (pose a question, receive a response) and Generate/Create (submit a prompt for artifact generation) are fundamentally different workflows; clarify which applies before executing.
3. **Treat specs as immutable** — Pre-prepared plans, checklists, and prompts are the input. Your role is execution. If changes seem warranted, ask first.
4. **Verify before submission** — Confirm the exact text matches the source document before sending to any external tool or API.
