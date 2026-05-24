---
name: notion-scrum-board
description: Use when managing the AI agent operations board in Notion — logging new tasks for agent dispatch, retrieving backlog, changing task status, recommending dispatch candidates, or updating any task property. Trigger on any mention of: logging a task, the backlog, what to dispatch, what's ready, launchpad, agent queue, or task prioritisation.
---

# Notion Agent Operations Board

Reference skill for an AI-agent task board in Notion. Every task represents work intended for an autonomous AI agent — not human work items.

## Default Database

**Database:** Claude (📲)
**ID:** `35c0c6d6-81e1-80d9-b994-f1d67618be18`

Use this ID in all API calls. Do not ask the user for it.

---

## Accessing the Notion API — Step-by-Step

Use the first available path. Try them in order; skip to the next if the previous fails.

### Path 1 — Native MCP tools (preferred)

Native `mcp__notion__*` tools are available when the Notion MCP server is registered in `~/.claude/settings.json`. They appear in the session's deferred tool list. Use `ToolSearch` to load a tool's schema before calling it.

**Check:** Can you see `mcp__notion__API-post-page` in the available tools list? If yes, use Path 1.

**Load the schema first:**
```
ToolSearch({ query: "select:mcp__notion__API-post-page" })
```

**Create a task:**
```
mcp__notion__API-post-page({
  "parent": {"type": "database_id", "database_id": "35c0c6d6-81e1-80d9-b994-f1d67618be18"},
  "properties": {
    "Name":        {"title":        [{"type": "text", "text": {"content": "🔌 Enable Tavily MCP for research workflows"}}]},
    "Status":      {"select":       {"name": "Backlog"}},
    "Priority":    {"select":       {"name": "P2 – Medium"}},
    "Effort":      {"select":       {"name": "M"}},
    "Task Type":   {"multi_select": [{"name": "tooling-config"}]},
    "Description": {"rich_text":    [{"type": "text", "text": {"content": "Configure the Tavily MCP server and validate it works in a research workflow end-to-end."}}]},
    "Creation Date": {"date": {"start": "YYYY-MM-DD"}}
  }
})
```

**Query the backlog:**
```
ToolSearch({ query: "select:mcp__notion__API-query-data-source" })

mcp__notion__API-query-data-source({
  "datasource_id": "35c0c6d6-81e1-80d9-b994-f1d67618be18",
  "filter": {"property": "Status", "select": {"equals": "Backlog"}},
  "sorts": [{"property": "Priority", "direction": "ascending"}]
})
```

**Update a task:**
```
ToolSearch({ query: "select:mcp__notion__API-patch-page" })

mcp__notion__API-patch-page({
  "id": "<page_id>",
  "properties": {
    "Status": {"select": {"name": "In Progress"}},
    "Assign": {"rich_text": [{"type": "text", "text": {"content": "python-pro"}}]}
  }
})
```

---

### Path 2 — mcp-cli (fallback)

Use when native MCP tools are not available. Requires the `mcp-cli` binary in PATH.

**Create a task:**
```bash
mcp-cli call notion API-post-page '{
  "parent": {"type": "database_id", "database_id": "35c0c6d6-81e1-80d9-b994-f1d67618be18"},
  "properties": {
    "Name":        {"title":        [{"type": "text", "text": {"content": "🔌 Enable Tavily MCP for research workflows"}}]},
    "Status":      {"select":       {"name": "Backlog"}},
    "Priority":    {"select":       {"name": "P2 – Medium"}},
    "Effort":      {"select":       {"name": "M"}},
    "Task Type":   {"multi_select": [{"name": "tooling-config"}]},
    "Description": {"rich_text":    [{"type": "text", "text": {"content": "Configure the Tavily MCP server and validate it works in a research workflow."}}]}
  }
}'
```

**Query the backlog:**
```bash
mcp-cli call notion API-query-data-source '{
  "datasource_id": "35c0c6d6-81e1-80d9-b994-f1d67618be18",
  "filter": {"property": "Status", "select": {"equals": "Backlog"}},
  "sorts": [{"property": "Priority", "direction": "ascending"}]
}'
```

**Update a task:**
```bash
mcp-cli call notion API-patch-page '{
  "id": "<page_id>",
  "properties": {
    "Status": {"select": {"name": "In Progress"}},
    "Assign": {"rich_text": [{"type": "text", "text": {"content": "python-pro"}}]}
  }
}'
```

---

### Path 3 — REST (last resort)

Use when neither MCP path is available. Requires `NOTION_API_TOKEN` env var and `curl`.

**Create a task:**
```bash
curl -s -X POST "https://api.notion.com/v1/pages" \
  -H "Authorization: Bearer $NOTION_API_TOKEN" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json" \
  -d '{
    "parent": {"database_id": "35c0c6d6-81e1-80d9-b994-f1d67618be18"},
    "properties": {
      "Name":        {"title":        [{"text": {"content": "🔌 Enable Tavily MCP for research workflows"}}]},
      "Status":      {"select":       {"name": "Backlog"}},
      "Priority":    {"select":       {"name": "P2 – Medium"}},
      "Effort":      {"select":       {"name": "M"}},
      "Task Type":   {"multi_select": [{"name": "tooling-config"}]},
      "Description": {"rich_text":    [{"text": {"content": "Configure the Tavily MCP server and validate it works in a research workflow."}}]}
    }
  }' | jq '{id: .id, title: .properties.Name.title[0].text.content}'
```

See `references/notion-queries.md` for full REST query patterns.

---

## Database Schema

| Property | Notion type | Required | Notes |
|----------|-------------|----------|-------|
| `Name` | title | **yes** | Task title — see naming convention |
| `Status` | select | **yes** | Board column — see vocabulary |
| `Priority` | select | **yes** | Dispatch ranking — see vocabulary |
| `Effort` | select | **yes** | Size estimate — see vocabulary |
| `Task Type` | multi_select | **yes** | Agent routing — see vocabulary |
| `Description` | rich_text | **yes** | Clear enough for an agent to act on without follow-up |
| `Assign` | rich_text | no | Agent or subagent name once dispatched |
| `Comments` | rich_text | no | Growing field: spec notes, agent analysis, blockers — always append, never overwrite |
| `Link` | url | no | Reference URL |
| `Deadline` | date | no | Target completion date |
| `Creation Date` | date | no | Recorded at creation |

## Task Title Convention

Format: **[Emoji] [Action Verb] [Object] [Context]**

- Start with an imperative verb: `Enable`, `Build`, `Add`, `Configure`, `Research`, `Implement`, `Integrate`, `Migrate`, `Audit`, `Create`, `Refactor`
- 4–8 words excluding emoji
- No filler: "Add X" not "Add the X" or "Task to add X"
- Specific enough to understand at a glance

**Good:** `🔌 Enable Tavily MCP for research workflows` · `💻 Implement replenishment forecasting model` · `🔬 Research conformal prediction approaches`
**Bad:** `MCP task` · `Work on forecasting` · `Set up the Tavily server thing`

### Emoji Selection

Scan the title and description for the best match. Pick the most specific fit — if nothing maps clearly, omit the emoji entirely.

| Emoji | Use when title/description contains… |
|-------|--------------------------------------|
| 🔌 | MCP server, API integration, plugin, connect, endpoint |
| 🧠 | memory, knowledge graph, RAG, embeddings, graph |
| 🤖 | agent, subagent, AI system, LLM, automation |
| ✨ | skill, prompt template, instruction, SKILL.md |
| 💻 | Python, script, code, implement, notebook, function |
| 🔬 | research, survey, literature, synthesis, field map |
| 📈 | forecast, model, prediction, ML, training, demand |
| ⚙️ | config, settings, setup, tooling (general) |

If multiple emojis compete equally → omit.

## Mandatory Pre-flight Checklist

Before creating any task, confirm every required field is filled. Do not create the task until all five are present:

- [ ] **Name** — follows convention; emoji applied if applicable
- [ ] **Priority** — one of the four values below
- [ ] **Effort** — one of the six values below
- [ ] **Task Type** — at least one value selected
- [ ] **Description** — substantive; an agent could act on it

Ask for all missing fields in a single message, not one by one.

## Controlled Vocabulary

### Status

| Value | Meaning |
|-------|---------|
| `Backlog` | Captured; not yet cleared for dispatch |
| `Launchpad` | Reviewed and confirmed — awaiting dispatch |
| `In Progress` | Agent actively working |
| `Review` | Agent work complete; human must review |
| `Done ✨` | Human-closed. **Agent must never set this.** |

### Priority

| Value | When to use |
|-------|-------------|
| `P0 – Critical` | Blocking or time-sensitive; dispatch immediately |
| `P1 – High` | Important; target next dispatch window. Also use when user interest is high. |
| `P2 – Medium` | Normal backlog |
| `P3 – Low` | Nice-to-have; no urgency |

### Effort

| Value | Approximate time |
|-------|-----------------|
| `XS` | ~30 min |
| `S` | ~2 h |
| `M` | ~4 h (half-day) |
| `L` | ~1 day |
| `XL` | 2–3 days |
| `Epic` | Needs decomposition before dispatch |

### Task Type (multi-select)

| Value | Dispatches to |
|-------|--------------|
| `create-skill` | skill-creator agent |
| `coding` | python-pro agent |
| `tooling-config` | general-purpose agent |
| `research` | research-analyst agent |
| `create-agent` | agent-development skill |

---

## One-Shot Task Examples

These are complete, correct task definitions. Use them as the reference pattern when filling mandatory fields.

### Example 1 — Research task

```
Name:        🔬 Research Conformal Prediction for Demand Forecasting
Status:      Backlog
Priority:    P2 – Medium
Effort:      M
Task Type:   research
Description: Survey conformal prediction methods applicable to non-stationary retail
             demand data. Focus on: (1) distribution-free coverage guarantees,
             (2) implementations compatible with scikit-learn pipelines,
             (3) empirical benchmarks vs. quantile regression.
             Deliverable: a structured synthesis note saved to research/forecasting/.
Creation Date: 2026-05-10
```

### Example 2 — Skill creation task

```
Name:        ✨ Build Agentic Trend Radar Skill
Status:      Backlog
Priority:    P1 – High
Effort:      L
Task Type:   create-skill, research, tooling-config
Description: Build a reusable skill that surfaces hot and emerging trends in the
             agentic AI space. Sources to integrate:
             • TikTok: crawl trending AI/agent content via browser automation
             • Perplexity: deep research queries via search-perplexity skill
             • Trendshift.io: monitor trending GitHub repos in the agentic/LLM space
             • last30days skill: aggregated signal from Reddit, HN, Polymarket
             Deliverable: an agentic-trend-radar skill runnable on demand or on schedule,
             producing a curated digest of what's new and hot.
Link:        https://trendshift.io/
Creation Date: 2026-05-10
```

### Example 3 — Tooling / config task

```
Name:        🔌 Enable Tavily MCP for Research Workflows
Status:      Backlog
Priority:    P2 – Medium
Effort:      S
Task Type:   tooling-config
Description: Register the Tavily MCP server in ~/.claude/settings.json under mcpServers.
             Validate that mcp__tavily-remote-mcp__tavily_search is callable from a
             Claude Code session. Document the working config in knowledge/tooling/tavily-mcp.md.
Creation Date: 2026-05-10
```

---

## Dispatch Recommendation

**Step 1 — Query:** `Status = Backlog`, sorted by Priority ascending.
**Step 2 — Filter out:** `Effort = Epic` (offer decomposition). Tasks with empty or vague `Description` (offer to improve).
**Step 3 — Rank ties:** Priority → Effort (prefer smaller at equal priority).
**Step 4 — Return top 1–3**, each with: Title · Priority · Effort · Task Type + one-line rationale.
**Step 5 — Confirm** before any state change: *"Move these to Launchpad?"*

## Updating a Task

Only include properties you want to change. When moving to In Progress, write the agent name to `Assign`:
```
"Status": {"select": {"name": "In Progress"}},
"Assign": {"rich_text": [{"text": {"content": "python-pro"}}]}
```

To update `Comments`: fetch the current value first, then PATCH with the full appended text.

## Status Transitions

| From | To | Trigger |
|------|----|---------|
| `Backlog` | `Launchpad` | User confirms dispatch candidate |
| `Launchpad` | `In Progress` | User confirms dispatch; set `Assign` |
| `In Progress` | `Review` | Agent reports completion |
| `Review` | `Done ✨` | **Human only — agent never sets Done** |

Backward transitions: ask why, record reason in `Comments`.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Creating a task with empty `Description` | Required — ask the user |
| Recommending an `Epic` task | Offer decomposition first |
| Setting `Status = Done ✨` | Human-only — refuse |
| Overwriting `Comments` | Fetch current value, append, then PATCH |
| Inventing Task Type values | Use vocabulary; propose additions to this skill |
| Skipping pre-flight check | Always confirm all 5 required fields before creating |
| Using `skill-creation` as Task Type | Correct value is `create-skill` |
