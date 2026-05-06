---
name: research-synthesis-planner
description: Systematically explore academic paper collections using NotebookLM with structured prompting and MCP execution. Use when you have a collection of research papers and want to generate an anchor document, orientation analysis, thematic deep-dives, synthesis, and gap analysis. Creates a NotebookLM notebook via MCP, loads sources, saves anchor as a pinned note, and optionally executes all analysis prompts. Distinct from multi-output-content-planner—this skill focuses on the analytical research phase itself, not on generating output artifacts.
---

# Research Synthesis Planner

Systematically extract, cross-reference, and synthesize knowledge from academic papers through structured prompting with NotebookLM.

## Problem This Solves

When exploring a paper collection with NotebookLM, users often:
- Ask ad-hoc questions without a coherent analytical framework
- Miss cross-paper patterns or contradictions
- Generate tangential outputs instead of decision-informing insights
- Repeat context in every prompt, leading to inefficiency

This skill provides a **structured exploration methodology** that:
1. Anchors all analysis to a clear research lens and decision
2. Sequences prompts from orientation → thematic analysis → synthesis
3. Produces cumulative outputs where each phase builds on prior results
4. Generates a complete, numbered prompt sequence ready to paste into NotebookLM

**This is not about producing final deliverables (slides, reports).** This is about *systematically thinking through* a paper collection to answer a specific research question.

---

## Workflow Overview

```
Phase 0: Create NotebookLM Notebook + Load Sources via MCP (~5 min)
    ↓
Phase 1: Gather Context (2 rounds, ~10 min) [USER CONFIRMS TO PROCEED]
    ↓
Phase 2: Build Anchor Document (~5 min) [USER APPROVES ANCHOR]
    ↓
Phase 3: Generate Prompt Sequence (~10 min) [USER CONFIRMS TO PROCEED]
    ↓
Phase 4: Execute or Save (~2-90 min)
    - Option A: Execute prompts now via NotebookLM MCP (1-2 hours in-session)
    - Option B: Save planning document to disk for manual use later
```

**MCP Tools Used:**
- `mcp__notebooklm-mcp__notebook_create` — Create session notebook
- `mcp__notebooklm-mcp__source_add` — Load papers into notebook
- `mcp__notebooklm-mcp__note` — Save anchor as pinned note
- `mcp__notebooklm-mcp__notebook_query` — Execute prompts (Phase 4 only if Option A)

---

## Phase 0: Create NotebookLM Notebook + Load Sources via MCP

### Step 1: Create Notebook

Before gathering research context, create a dedicated NotebookLM notebook for this research session using:

**Tool:** `mcp__notebooklm-mcp__notebook_create`

Create a new notebook with a descriptive title (e.g., "Research: {{TOPIC}}", "Literature Review: {{DOMAIN}}").

**Result:** Returns `notebook_id` for use in subsequent MCP calls.

### Step 2: Add Paper Sources to Notebook

For each paper source the user provides, add it to the notebook:

**Tool:** `mcp__notebooklm-mcp__source_add` (for each paper)

Supported source types:
- `source_type=url` — Web-hosted PDFs or paper repositories
- `source_type=file` — Local PDF files (user provides file path)
- `source_type=text` — Pasted paper text/abstracts

**Parameters:**
- `notebook_id` — from Phase 0 Step 1
- `source_type` — url, file, or text
- `url` — full URL (for type=url)
- `file_path` — absolute path (for type=file)
- `text` — paper content (for type=text)
- `wait=True` — wait for source processing before returning

**Note:** Sources are indexed asynchronously. Wait for completion before Phase 1.

### Example Phase 0 Execution

```
User provides 3 papers:
  1. PDF on local disk: /Users/.../paper1.pdf
  2. arXiv link: https://arxiv.org/pdf/2024.xxxxx.pdf
  3. Pasted abstract text

Execution:
  → notebook_create(title="Research: Agentic Systems")
  ← notebook_id = "nb_xyz123"

  → source_add(notebook_id="nb_xyz123", source_type="file", file_path="/Users/.../paper1.pdf", wait=True)
  → source_add(notebook_id="nb_xyz123", source_type="url", url="https://arxiv.org/pdf/2024.xxxxx.pdf", wait=True)
  → source_add(notebook_id="nb_xyz123", source_type="text", text="[abstract text]", wait=True)

  ← All sources indexed and ready
```

---

## Phase 1: Gather Research Context

### Round 1: Core Information (All Together)

Ask these three questions in a single round to avoid overwhelming the user:

**Question 1: Research Topic & Domain**
> What's your research topic or paper collection focused on?
> Examples: "Conformal prediction methods for time series", "Agentic AI system design", "Inventory replenishment algorithms"

**Question 2: Applied Problem or Pure Literature Review?**
> Are you exploring this for a **specific applied problem** (if so, what?), or a **pure literature review** (if so, what's your research question)?
>
> Examples (applied): "Building a real-time inventory system for 200+ stores"
> Examples (pure): "Understanding when uncertainty quantification improves decision-making"

**Question 3: Paper Collection Status**
> How many papers do you have? Are they already organized/tiered, or is this a raw collection?
> (If tiered: "Yes, I've marked A-tier (core), B-tier (supporting), C-tier (background)" or similar)

---

### Gate 1: Phase 1 → Phase 2 Confirmation

After gathering both rounds of context, ask:

> **Ready to build the anchor document?** I'll compile your research lens, core decision, constraints, and success criteria into a structured anchor. This anchor will guide all subsequent analysis.
>
> Proceed? (Yes/No)

Wait for explicit user confirmation before proceeding to Phase 2.

---

### Round 2: Thematic Dimensions & Deliverables (After Round 1)

Based on their Round 1 answers, ask:

**Question 4: Thematic Dimensions**
> What 3-5 **thematic dimensions** do you want to analyze through? Think of these as different analytical lenses on your papers.
>
> **To help, here are domain-specific examples for your topic ({{DOMAIN}}):**
>
> [Generate 2-3 example theme sets based on their domain—see reference/thematic-cut-patterns.md for domain examples]
>
> Example 1 for {{DOMAIN}}: [THEME_EXAMPLE_1], [THEME_EXAMPLE_2], [THEME_EXAMPLE_3]
> Example 2 for {{DOMAIN}}: [THEME_EXAMPLE_1], [THEME_EXAMPLE_2], [THEME_EXAMPLE_3]
>
> Or propose your own themes. **If unsure, I can suggest themes based on your anchor.**

**Question 5: Desired End Outputs**
> After completing the research analysis, do you want to:
> - [ ] Just the research synthesis and insights (recommended—focus on research phase)
> - [ ] Slide decks from the synthesis (use `nblm-deliverables` after this skill)
> - [ ] Reports or other formatted outputs (use `nblm-deliverables` after this skill)

(Note: Indicate that deliverable generation is a separate skill if they choose option B or C.)

---

## Phase 2: Build Anchor Document

### Step 1: Construct Anchor from User Input

Using `references/anchor-template.md`, fill in:
- **Problem Statement / Research Lens** (from user's Round 1 applied problem or research question)
- **Core Decision or Design Question** (derived from their focus)
- **Domain Constraints** (from their applied problem, if present)
- **Model / Framework Architecture** (if applicable; "N/A for pure literature review" otherwise)
- **Success Criteria** (derived from their goals)
- **Applied Setting** (if applicable; org, timeline, team)

### Step 2: Present Anchor for Approval

Show the constructed anchor document to the user and ask:

> **Review this anchor document.** It will be saved as a pinned note in your NotebookLM notebook, used by every subsequent prompt.
>
> Does this capture your research lens correctly? Any changes?
>
> (If changes: "What should I adjust?")
> (If approved: "Great. I'll save this as an anchor note in your notebook.")

Wait for explicit user approval before proceeding to Step 3.

### Step 3: Save Anchor as Pinned Note via MCP

Once approved, save the anchor to the notebook as a typed note using:

**Tool:** `mcp__notebooklm-mcp__note`

**Parameters:**
- `notebook_id` — from Phase 0 Step 1
- `action` — "create"
- `note_title` — "ANCHOR: {{TOPIC}}"
- `note_text` — full anchor document (Problem Statement + Core Decision + Domain Constraints + Architecture + Success Criteria + Applied Setting)
- `tags` — ["anchor", "research-lens", "pinned"]

**Note:** This creates a persistent typed note that all subsequent queries will reference.

### Gate 2: Phase 2 → Phase 3 Confirmation

After anchor is saved, ask:

> **Anchor saved to notebook.** Now I'll generate the complete prompt sequence (P1-P8) that you can execute in NotebookLM.
>
> Proceed to Phase 3? (Yes/No)

Wait for explicit user confirmation before proceeding to Phase 3.

---

## Phase 3: Generate Prompt Sequence

### Step 1: Construct Prompt Library

Using `references/prompt-library.md`, generate **all prompts** with placeholders filled:

**Orientation Phase:**
- **P1: Paper Briefings** (table + narratives)
- **P2: Relevance Ranking** (3-tier grouping)

**Thematic Cuts Phase:**
- **P3, P4, P5, ...** (one per user-chosen dimension)
  - Use the parametric template from prompt-library.md
  - Fill in: {{THEME}}, {{THEME_JUSTIFICATION}}, {{SUB_QUESTION_1-5}}, {{CORE_QUESTION}}

**Synthesis Phase:**
- **P6: Composite Framework Recipe** (if architecture present)
- **P7: Gap Analysis** (5-6 specific gaps)
- **P8: Implementation Checklist** (data, algorithms, operations)

**Optional Deliverable Prompts (if user selected slides/reports):**
- **P_deck_align: Alignment Slide Deck** (if requested; use multi-output-content-planner for full output generation)

### Step 2: Verify Prompt Count

Display a summary:

```
PROMPT SEQUENCE SUMMARY:
- P1-P2: Orientation (2 prompts)
- P3-P5: Thematic Cuts ({{N}} prompts, one per dimension)
- P6-P8: Synthesis (3 prompts)
- [Optional: P_deck: Deliverable (1 prompt if requested)]

Total: {{N}} prompts ready to execute in NotebookLM

Estimated time in NotebookLM: 1-2 hours
```

---

## Phase 4: Execute or Save

### Step 1: Offer Execution Choice

After generating the complete prompt sequence (P1-P8), offer the user two options:

**Option A: Execute Now via NotebookLM MCP (1-2 hours in-session)**

Use `mcp__notebooklm-mcp__notebook_query` to loop through each prompt:

```
For each prompt in sequence (P1 → P2 → P3 → ... → P8):
  → notebook_query(
      notebook_id = "nb_xyz123",
      query = "[Full prompt text]"
    )
  ← Receive response, display to user
  → Ask user to confirm before proceeding to next prompt
```

**Option B: Save Planning Document to Disk (for manual use)**

Compile into a markdown file and save to `/claude.io/` with timestamp.

### Step 2: Execute Prompts (If Option A Selected)

If user chooses Option A, execute sequentially:

**Tool:** `mcp__notebooklm-mcp__notebook_query`

**Parameters:**
- `notebook_id` — from Phase 0 Step 1
- `query` — full prompt text (P1, P2, P3, etc.)
- `conversation_id` — (optional) reuse if continuing prior session

**Flow:**
1. Execute P1: Paper Briefings
2. Wait for response; display to user
3. Ask: "Continue to P2?"
4. If yes, execute P2: Relevance Ranking
5. Continue through P3-P8 (or until user stops)

**Note:** Each prompt builds on prior responses. Don't skip ahead.

### Step 3 (Option B): Compile Planning Document

Assemble into a single `.md` file with these sections:

```
# Research Exploration Plan: {{TOPIC}}

## Anchor Document

[Full anchor document—ready to copy/paste]

## Phase 0: NotebookLM Setup Checklist

- [ ] Create new NotebookLM notebook (name: "{{TOPIC}}")
- [ ] Upload or add all {{N}} papers
- [ ] Organize sources or apply tier labels if available (A1, A2, etc.)
- [ ] Create a **Typed Note** titled "ANCHOR: {{TOPIC}}"
- [ ] Paste the anchor document (above) into this note
- [ ] Pin or star this note for easy reference

## Prompt Sequence

### P1: Paper Briefings Table + Narrative

[Full prompt text]

### P2: Relevance Ranking — 3-Tier Grouping

[Full prompt text]

### P3: {{THEME_1}} — Thematic Cut

[Full prompt text]

### P4: {{THEME_2}} — Thematic Cut

[Full prompt text]

[... continue for all prompts ...]

### P8: Implementation Checklist

[Full prompt text]

## Execution Guide

1. Copy the ANCHOR section above into NotebookLM as a **Typed Note**
2. For each prompt (P1, P2, P3, ...), paste into NotebookLM and wait for response
3. Review each response; extract key insights
4. Proceed to the next prompt (prompts build on each other)
5. After P8, you'll have comprehensive synthesis ready for decisions or deliverables

## Notes

- Each prompt assumes prior prompts are complete
- Allow 10-15 min per prompt for NotebookLM to respond
- Save NotebookLM responses as you go (optional: export to markdown for reference)

---

Generated: {{TIMESTAMP}}
Topic: {{TOPIC}}
```

### Step 2: Ask User Before Saving

> Would you like me to save this planning document to disk?
>
> File: `/claude.io/planning-notebooklm-research-{{TOPIC_SLUG}}-{{YYYYMMDDHHmm}}.md`
>
> (If yes: "Saving...")
> (If no: "I'll display it here, but won't save to disk.")

If user approves, save the file using the naming convention from project CLAUDE.md:
- **Format:** `planning-notebooklm-research-{topic}-{YYYYMMDDHHmm}.md`
- **Location:** `/claude.io/`

---

## Reference Materials in Skill

This skill uses three reference files:

### `references/anchor-template.md`
Structured template for building the anchor document. Includes:
- Problem Statement / Research Lens
- Core Decision or Design Question
- Domain Constraints
- Model / Framework Architecture
- Success Criteria
- Applied Setting

### `references/prompt-library.md`
Complete prompt templates for all 8+ prompts:
- P1-P2: Orientation prompts
- P3-Pn: Thematic cut prompts (parametric template)
- P6-P8: Synthesis prompts
- P_deck: Optional deliverable prompts

All templates use `{{PLACEHOLDER}}` syntax for easy customization.

### `references/thematic-cut-patterns.md`
Guidance on choosing 3-5 thematic dimensions for any domain:
- The 5+1 structure (five sub-questions + one synthesis question)
- Domain-specific theme examples (ML, Systems, Optimization, Social Science)
- Anti-patterns to avoid (overly broad, overlapping, single-paper themes)
- Validation checklist for chosen themes

---

## Key Design Principles Encoded

1. **Anchor-first framing:** Every prompt cites the anchor. No generic descriptions.
2. **Wide-to-narrow funnel:** Orientation → Thematic cuts → Synthesis, in that order.
3. **Thematic cuts use 5+1 structure:** 5 targeted sub-questions + 1 synthesis question per dimension.
4. **Cumulative outputs:** Each prompt produces something carried into the next (P6 recipe → gap analysis → checklist).
5. **Paper citation discipline:** Outputs reference papers by label (A1, A2, etc.) throughout.
6. **Synthesis before deliverables:** Complete the analytical phase (P1-P8) before generating reports/slides.

---

## Relationship to Other Skills

**`multi-output-content-planner`** (sibling skill)
- **Use that skill if:** You want to generate slide decks, reports, infographics, or other formatted outputs *after* completing research synthesis.
- **Use this skill if:** You want to *systematically explore* papers and generate a research insights plan.
- **Workflow:** Run *this* skill first (planning + MCP execution), then *multi-output-content-planner* second (if outputs needed).

**`zotero-search`** (prerequisite)
- Use to find and collect papers before invoking this skill.

---

## Checklist for Skill Execution

- [ ] Round 1: Gathered research topic, problem/lens, paper count
- [ ] Round 2: Gathered 3-5 thematic dimensions + desired outputs
- [ ] Built anchor document with all sections
- [ ] User approved anchor before proceeding
- [ ] Generated complete prompt sequence (P1-Pn)
- [ ] Compiled planning document with setup checklist + all prompts
- [ ] Asked user before saving to `/claude.io/`
- [ ] Confirmed file saved with correct timestamp

---

## Example Output

For a user researching "Conformal Prediction for Time Series," the skill would produce:

```
File: /claude.io/planning-notebooklm-research-conformal-prediction-time-series-202602241800.md

Contents:
├── ANCHOR DOCUMENT (filled)
│   ├── Problem: "Building a decision system where uncertainty bounds are more important than point predictions"
│   ├── Core Question: "When and why does conformal prediction improve forecast-driven decisions?"
│   ├── Constraints: "Must retrain weekly, need calibrated 80% prediction intervals"
│   ├── Architecture: [Diagram showing demand prediction → interval generation → decision]
│   └── Success Criteria: "Can map 3+ papers to architecture components, identify 2-3 critical gaps"
│
├── PHASE 0 SETUP CHECKLIST
│   ├── [ ] Upload papers (12 papers total)
│   ├── [ ] Create "ANCHOR: Conformal Prediction" typed note
│   ├── [ ] Paste anchor document
│
├── PROMPT SEQUENCE
│   ├── P1: Paper Briefings (table + narratives)
│   ├── P2: Relevance Ranking (3-tier grouping)
│   ├── P3: Conformal Methods Fundamentals
│   ├── P4: Time-Series Specific Challenges
│   ├── P5: Practical Coverage Guarantees
│   ├── P6: Composite Framework Recipe
│   ├── P7: Gap Analysis (5 gaps identified)
│   └── P8: Implementation Checklist (data, algorithms, operations)
│
└── EXECUTION GUIDE (step-by-step)
```

---

## What Comes Next

After running this skill:

1. **Copy the planning document** to your NotebookLM instance
2. **Execute prompts in order** (P1 → P2 → P3 → ... → P8)
3. **Review NotebookLM responses** and extract key insights
4. **If you want deliverables** (slides, reports), use `multi-output-content-planner` with the synthesis results
5. **If you want decisions**, use the Gap Analysis (P7) and Checklist (P8) to guide next steps

---

## Notes

- This skill is **framework and planning focused**—it doesn't execute NotebookLM prompts for you (you run those manually in the NotebookLM interface).
- The output is a **planning document**, not a research result. The research happens when you paste prompts into NotebookLM.
- If you want to generate deliverables *after* this research phase, use `nblm-deliverables`.
- This skill is especially effective for **applied research** (informing decisions) and **literature reviews** with clear organizational lenses.
