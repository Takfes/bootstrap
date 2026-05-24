---
name: organize-agents
description: |
  Organize and catalog Claude Code agents as a searchable browser UI. Use this whenever you need to understand, document, or share the available agents landscape — whether to create an agent reference, understand what agents exist, or onboard teammates. Scans .claude/agents (or a custom location), proposes 1–3 categorization frameworks, and generates a self-contained HTML file with real-time search, category filters, and agent detail cards showing tools and model. Trigger on: "organize my agents", "agents catalog", "agents browser", "what agents do I have", "document my agents", or any request to create a reference guide of available Claude Code agents.
compatibility:
  required_tools: [Read, Write, Bash, AskUserQuestion]
---

# organize-agents

Generate a searchable browser UI cataloging your Claude Code agents by category.

## Workflow

### Step 1 — Discover Agents

Scan `.claude/agents/` relative to the project root. For each `.md` file found, parse the YAML frontmatter and extract:
- **name** — from the `name:` field (or derive from the filename without extension if missing)
- **description** — from the `description:` field (strip pipe `|`, leading/trailing whitespace, and quoted wrappers `"..."`)
- **tools** — from the `tools:` field (raw comma-separated string)
- **model** — from the `model:` field (e.g. `sonnet`, `opus`, `haiku`)

If `.claude/agents/` is empty or missing, ask the user to specify an alternative path before continuing.

Run the scan with:
```bash
ls /path/to/.claude/agents/
```
Then read each `.md` file to extract frontmatter fields.

### Step 2 — Propose Frameworks

Examine the agent roster and propose the appropriate number of frameworks (1–3). Default to proposing all three unless the roster is too small or homogeneous to warrant it.

Present the frameworks clearly before asking:

**Framework A — Domain-Based** ("What area does this agent work in?")
Groups by professional domain: Software Engineering, Data & Analysis, Infrastructure & Ops, Research & Intelligence, Documentation & Communication, Product & Strategy, etc.
Best for: "I need help with X domain — which agents cover it?"

**Framework B — Role-Based** ("What role does this agent play?")
Groups by kind of work: Builder (creates things), Reviewer (evaluates things), Researcher (finds/synthesises information), Operator (manages systems), Communicator (writes/explains).
Best for: "I know what kind of help I need — who plays that role?"

**Framework C — Capability-Based** ("What tools and access does this agent have?")
Groups by tool set: Web-enabled (has WebFetch/WebSearch), Code-execution (has Bash), Read-only (no write tools), Full-access (all tools), etc.
Best for: "I need an agent with specific permissions or tool access."

### Step 3 — Ask User Preferences

Ask two things in one interaction:

1. **Framework:** Which of the proposed frameworks do they want?
2. **Output location:** Where to save `agents-catalog.html`? Default: project root (`.`)

### Step 4 — Categorize Agents

Using the selected framework, assign each agent a `category`. Apply thoughtfully — if an agent spans multiple categories, assign it to the one where a user would most likely look for it.

### Step 5 — Build the Agents JSON

Construct an array of agent objects:

```json
[
  {
    "name": "python-pro",
    "description": "Build type-safe, production-ready Python code for web APIs and complex applications.",
    "category": "Software Engineering",
    "tools": "Read, Write, Edit, Bash, Glob, Grep",
    "model": "sonnet"
  }
]
```

**Description hygiene:**
- Strip YAML quoting artifacts (`"..."`, `|`, leading whitespace)
- Truncate to the first 1–2 sentences if very long (keep it under ~200 chars)
- Remove triggering metadata ("Use when user says X") — keep only the functional description

**Tools hygiene:** Use the raw comma-separated string from frontmatter. If missing, use `"unspecified"`.

**Model hygiene:** Use the raw value from frontmatter. If missing, use `"default"`.

### Step 6 — Generate the HTML

Read the template from:
```
{skill_base_dir}/assets/template.html
```

Replace the two placeholders exactly as shown:
- `__AGENTS_JSON__` → the JSON array from Step 5 (no surrounding quotes — it's a JS literal)
- `__META_JSON__` → a metadata object:

```json
{"generated": "YYYY-MM-DD", "framework": "Framework Name", "total": 17}
```

Write the result to `{output_location}/agents-catalog.html`.

If a file already exists at that path, ask the user whether to overwrite before writing.

### Step 7 — Confirm & Suggest Next Steps

Tell the user:
- Where the file was saved (absolute path)
- How to open it (`open agents-catalog.html` on macOS, or equivalent)
- That pressing `/` in the browser focuses search
- Offer to re-run with a different framework if they want to compare

---

## Output

A single file: `agents-catalog.html` — a self-contained browser app with:

- **Real-time search** across agent names, descriptions, and tools (keyboard shortcut: `/`)
- **Category tabs** — one per category in the selected framework
- **Agent cards** — name, description, tools line, model badge, category badge, copy-to-clipboard (`@agent-name`)
- **Live result count** while searching

Dark developer-tool aesthetic, cyan accent colour. No server required — open directly in any browser.

---

## Troubleshooting

**Agents directory not found:** Ask user to specify an alternative path.

**Missing frontmatter fields:** Use defaults — `tools: "unspecified"`, `model: "default"`. Note the gap in the confirmation message.

**Template not found:** The template lives at `{skill_base_dir}/assets/template.html`. If it's missing, report the error and stop — do not attempt to generate HTML without it.

**Output file conflict:** Always ask before overwriting.
