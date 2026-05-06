---
name: organize-skills
description: |
  Organize and catalog Claude Code skills as a searchable browser UI. Use this whenever you need to understand, document, or share the available skills landscape — whether to create a skills reference, understand what skills exist, or maintain documentation for your team. Scans .claude/skills (or a custom location), proposes 1–3 categorization frameworks, and generates a self-contained HTML file with real-time search, category filters, and copy-to-clipboard. Trigger on: "organize my skills", "skills catalog", "skills browser", "what skills do I have", "document my skills", or any request to create a reference guide of available Claude Code skills.
compatibility:
  required_tools: [Read, Write, Bash, AskUserQuestion]
---

# organize-skills

Generate a searchable browser UI cataloging your Claude Code skills by category.

## Workflow

### Step 1 — Discover Skills

Scan `.claude/skills/` relative to the project root. For each subdirectory, read its `SKILL.md` and extract:
- **name** — the directory name
- **description** — from the YAML frontmatter `description:` field (strip pipe `|`, leading/trailing whitespace, and quoted wrappers `"..."`)
- **category** — assigned in Step 3 based on the chosen framework

If `.claude/skills/` is empty or missing, ask the user to specify an alternative path before continuing.

Run the scan with:
```bash
ls /path/to/.claude/skills/
```
Then read each `SKILL.md` frontmatter to extract name + description.

### Step 2 — Propose Frameworks

Examine the skill set and propose the appropriate number of frameworks (1–3). Default to proposing all three unless the skill set is too small or homogeneous to warrant it.

Present the frameworks clearly before asking:

**Framework A — Workflow-Based** ("What are you doing?")
Groups by primary activity: Git & Version Control, Research & Synthesis, Writing & Documentation, Design & Presentation, Code Quality, API & Integration Development, Execution & Workflow Management, System Setup, etc.
Best for: "I'm coding/researching/writing — which skills help?"

**Framework B — Domain-Based** ("What are you building?")
Groups by technology domain or output type: Documents & Content, Presentations & Design, Python Ecosystem, AI/Agents, APIs & Infrastructure, Research & Learning, Git & Collaboration, etc.
Best for: "I work in domain X — show me relevant tools."

**Framework C — Capability Layer** ("How do you want to work?")
Groups by operational depth and Claude Code integration: System & Environment Setup, Planning & Decision Making, Execution & Workflow, Development Practices, Git Workflows, Code Quality, Research, Content Creation, Integration & Tooling.
Best for: "I want to improve how I work systematically."

### Step 3 — Ask User Preferences

Ask three things in one interaction:

1. **Framework(s):** Which of the proposed frameworks do they want? (one, multiple, or all)
2. **Output location:** Where to save `skills-catalog.html`? Default: project root (`.`)

No need to ask about format — output is always a single HTML file.

### Step 4 — Categorize Skills

Using the selected framework(s), assign each skill a `category`. If multiple frameworks are selected, choose the most useful single category per skill — the one that best represents its primary use case. (The HTML UI does not support multiple category systems simultaneously; pick the best fit.)

Apply the categorization thoughtfully — don't force-fit. If a skill spans multiple categories, assign it to the category where a user would most likely look for it.

### Step 5 — Build the Skills JSON

Construct an array of skill objects:

```json
[
  {
    "name": "skill-name",
    "description": "One clean sentence summarizing what the skill does and when to use it.",
    "category": "Category Name"
  }
]
```

**Description hygiene:**
- Strip YAML quoting artifacts (`"..."`, `|`, leading whitespace)
- Truncate to the first 1–2 sentences if the description is very long (keep it under ~200 chars)
- Remove triggering metadata ("Use when user says X") — keep only the functional description

### Step 6 — Generate the HTML

Read the template from:
```
{skill_base_dir}/assets/template.html
```

Replace the two placeholders exactly as shown:
- `__SKILLS_JSON__` → the JSON array from Step 5 (no surrounding quotes — it's a JS literal)
- `__META_JSON__` → a metadata object:

```json
{"generated": "YYYY-MM-DD", "framework": "Framework Name", "total": 43}
```

Write the result to `{output_location}/skills-catalog.html`.

If a file already exists at that path, ask the user whether to overwrite before writing.

### Step 7 — Confirm & Suggest Next Steps

Tell the user:
- Where the file was saved (absolute path)
- How to open it (`open skills-catalog.html` on macOS, or equivalent)
- That pressing `/` in the browser focuses search
- Offer to re-run with a different framework if they want to compare

---

## Output

A single file: `skills-catalog.html` — a self-contained browser app with:

- **Real-time search** across skill names and descriptions (keyboard shortcut: `/`)
- **Category tabs** — one per category in the selected framework
- **Skill cards** — name, description, category badge, copy-to-clipboard (`/skill-name`)
- **Live result count** while searching

Dark developer-tool aesthetic. No server required — open directly in any browser.

---

## Troubleshooting

**Skills directory not found:** Ask user to specify an alternative path.

**SKILL.md missing in a subdirectory:** Skip that skill, note it in the confirmation message.

**Template not found:** The template lives at `{skill_base_dir}/assets/template.html`. The `{skill_base_dir}` is the base directory reported when this skill loads. If it's missing, report the error and stop — do not attempt to generate HTML without it.

**Output file conflict:** Always ask before overwriting.
