---
name: multi-output-content-planner
description: Strategic multi-output content planning and prompt optimization from any source type. Use when designing coherent document systems from research sources (YouTube videos, academic papers, web articles, PDFs, Google Drive docs). Gathers audience + purpose input once, designs deliverable plan with scoped outputs, generates optimized NotebookLM prompts, and provides real MCP execution strategy. Ideal for: (1) Training materials from video/document collections, (2) Research synthesis into knowledge systems, (3) Multi-format content for different stakeholders, (4) Rapid document generation from mixed sources.
---

# Multi-Output Content Planner

Strategic workflow for designing and optimizing multi-deliverable knowledge systems using NotebookLM with real MCP execution.

## Problem This Solves

When creating comprehensive content from multiple sources (20+ videos, research papers, documentation), ad-hoc deliverable planning leads to:
- Repeated user input across similar prompts
- Outputs that don't work together as a system
- Inefficient prompt optimization (per-file instead of strategic)
- Misaligned scopes and audiences

This skill provides a single upfront planning phase that designs a coherent deliverable system, then generates all necessary prompts with real MCP execution.

## Workflow Overview

```
User Input (once) → Plan Deliverables → Scope Each Output → Optimize Prompts → Load Sources → Execute & Monitor
```

### Phase 0: Notebook Preparation (2 minutes)

Create a NotebookLM notebook that will serve as the single source repository for all deliverables.

**MCP Execution:**

```python
# Create notebook once (all deliverables will reuse this)
notebook_create(title="[Topic/Project] - [Audience]")
# Returns: notebook_id
```

**Tool:** `mcp__notebooklm-mcp__notebook_create`

---

### Phase 1: Strategic Input (5 minutes)

Answer these 5 questions once:

**Core information:**
1. **Target Audience**: Who are the primary readers? (C-level, engineers, data scientists, multi-stakeholder, educational)
2. **Primary Purpose**: What should readers be able to do after? (business case, implementation, learning, decision-making)
3. **Detail Level**: How deep should explanations go? (executive, intermediate, deep technical)
4. **Number of Deliverables**: How many different outputs? (3-6 typically optimal)
5. **Key Success Metrics**: How do you measure if outputs work? (decision made, learned concept, implementation started)

### Phase 2: Deliverable Planning (10 minutes)

Select the appropriate plan from **DELIVERABLE_TEMPLATES.md** based on audience + purpose.

**Template examples:**
- C-Level + Business Case → Executive Briefing + Slide Deck + ROI Infographic
- Engineers + Implementation → Study Guide + Code Examples + Architecture Diagram
- Data Scientists + Methodology → Research Report + Performance Analysis + Use Case Study
- Multi-Stakeholder → Executive Summary + Technical Guide + Visual Overview + FAQ
- Educational + Foundation → Study Guide + Concept Explainer + Interactive Examples

**Validation Step:** If use case doesn't match any core template in DELIVERABLE_TEMPLATES.md, offer custom deliverable scaffolding with 3 guided questions:
1. What is the primary output format? (report, visual, interactive, reference)
2. What is the target depth level? (executive, intermediate, technical)
3. What decision or action should the reader take? (specific success metric)

Each plan includes:
- Specific deliverable types
- Purpose of each deliverable
- Target length/scope
- Success criteria

### Phase 3: Output Scoping (10 minutes)

For each deliverable, define:

1. **Target Reader**: Who specifically reads this? (C-suite, engineering team lead, individual engineer, etc.)
2. **Key Question Answered**: What specific question does this output answer?
3. **Success Definition**: How do you know this output works?
4. **Scope Boundaries**: What's in scope? What's out? (e.g., "explains concepts, not code")
5. **Constraints**: Any specific requirements? (length, format, tone, detail level)

Example scoping:

| Deliverable | Target Reader | Key Question | Success | Scope | Constraints |
|---|---|---|---|---|---|
| Executive Briefing | VP Engineering | Should we adopt agents? | Can make go/no-go decision | Overview only, no code | 1,500 words max, business language |
| Study Guide | Senior Engineers | How do agents work? | Can design agent implementation | Complete technical depth | 5,000+ words, cite sources |
| Infographic | All audiences | How do components relate? | Understand ecosystem structure | Architecture relationships | Single page, visual-first |

### Phase 4: Prompt Optimization (15 minutes)

Generate customized NotebookLM prompts using **PROMPT_TEMPLATES.md**:

1. Find the matching template for each deliverable type
2. Fill in placeholders from Phase 3 scoping (note: placeholders use `{{PLACEHOLDER}}` syntax)
3. Add custom constraints from your scoping session
4. Test prompt: Does it clearly specify success criteria?

**Prompt quality checklist:**
- ✓ Clear role defined (who is the AI acting as?)
- ✓ Success criteria explicit (what does "done" look like?)
- ✓ Constraints included (what should be avoided?)
- ✓ Format specified (how should output be structured?)
- ✓ Length/scope boundaries clear (how much detail?)

### Phase 1.5: Source Loading (15-25 minutes) — NEW

After strategic input and template selection, load ALL sources into the notebook created in Phase 0. This step processes sources once, allowing all deliverables to reuse them.

**Source Types Supported:**
- YouTube videos → `mcp__notebooklm-mcp__source_add` with `type=url`
- Web articles → `mcp__notebooklm-mcp__source_add` with `type=url`
- Google Drive documents → `mcp__notebooklm-mcp__source_add` with `type=drive`
- PDFs → `mcp__notebooklm-mcp__source_add` with `type=file`
- Pasted text/papers → `mcp__notebooklm-mcp__source_add` with `type=text`

**MCP Execution Pattern:**

```python
# Add sources in parallel (sources processed once, reused for all outputs)
# YouTube/Web URLs
source_add(
  notebook_id=notebook_id,
  source_type="url",
  url="https://youtube.com/watch?v=...",
  wait=True
) × N videos/articles

# Google Drive documents
source_add(
  notebook_id=notebook_id,
  source_type="drive",
  document_id="[doc_id]",
  doc_type="doc|slides|sheets",
  wait=True
) × N documents

# PDF files
source_add(
  notebook_id=notebook_id,
  source_type="file",
  file_path="/path/to/file.pdf",
  wait=True
) × N PDFs

# Pasted text/research papers
source_add(
  notebook_id=notebook_id,
  source_type="text",
  text="[pasted content]",
  title="[Source Title]"
) × N text sources
```

**Tools:**
- `mcp__notebooklm-mcp__source_add` (supports url, text, drive, file types)

---

### Phase 5: Output Generation & Execution (35-50 minutes)

Once sources are loaded, launch all outputs simultaneously using optimized prompts from Phase 4.

**MCP Execution for Artifact Creation:**

```python
# Create each artifact type with custom prompt from Phase 4
# All artifacts reuse the same notebook with all sources

# Report/Study Guide
studio_create(
  notebook_id=notebook_id,
  artifact_type="report",
  report_format="Briefing Doc|Study Guide|Blog Post|Create Your Own",
  custom_prompt="{{optimized-prompt-from-phase-4}}",
  confirm=True
) × [num_reports]

# Slide Deck
studio_create(
  notebook_id=notebook_id,
  artifact_type="slide_deck",
  slide_format="detailed_deck|presenter_slides",
  custom_prompt="{{optimized-prompt-from-phase-4}}",
  confirm=True
) × [num_decks]

# Video Overview
studio_create(
  notebook_id=notebook_id,
  artifact_type="video",
  video_format="explainer|brief",
  visual_style="auto_select|classic|whiteboard|kawaii|anime|watercolor|retro_print|heritage|paper_craft",
  custom_prompt="{{optimized-prompt-from-phase-4}}",
  confirm=True
) × [num_videos]

# Infographic
studio_create(
  notebook_id=notebook_id,
  artifact_type="infographic",
  orientation="landscape|portrait|square",
  custom_prompt="{{optimized-prompt-from-phase-4}}",
  confirm=True
) × [num_infographics]

# Quiz/Assessment
studio_create(
  notebook_id=notebook_id,
  artifact_type="quiz",
  question_count=10,
  difficulty="easy|medium|hard",
  confirm=True
)

# Flashcards
studio_create(
  notebook_id=notebook_id,
  artifact_type="flashcards",
  difficulty="easy|medium|hard",
  confirm=True
)

# Mind Map
studio_create(
  notebook_id=notebook_id,
  artifact_type="mind_map",
  title="[Concept Overview]",
  confirm=True
)

# Data Table
studio_create(
  notebook_id=notebook_id,
  artifact_type="data_table",
  description="{{structured-data-description}}",
  confirm=True
)
```

**Tools:**
- `mcp__notebooklm-mcp__studio_create` (artifact_type: audio, video, report, slide_deck, infographic, flashcards, quiz, data_table, mind_map)
- `mcp__notebooklm-mcp__studio_status` (poll loop for completion)

**Step 5B: Monitor & Collect (5-10 minutes)**

```python
# Poll for completion of all artifacts
status = studio_status(notebook_id)
# Check each artifact:
# - artifact_id, title, type
# - status: "completed" | "in_progress" | "failed"
# - url: link to view/download (when complete)

# Once complete, download or share artifacts
# download_artifact(artifact_type="report", output_path="...")
# or share via NotebookLM public link
```

**Tools:**
- `mcp__notebooklm-mcp__studio_status` (check artifact status and collect URLs)
- `mcp__notebooklm-mcp__download_artifact` (retrieve completed artifacts)

---

## Phase 5 Iteration Guidance — NEW

If an output misses the mark, use this decision tree to refine:

**Problem:** Output doesn't meet success criteria

**Option A: Regenerate with Refined Prompt**
- Identify what's missing (tone, depth, structure, content)
- Rewrite custom prompt with specific constraints
- Call `studio_create` with updated prompt + same notebook
- Best for: Output structure is right, but content needs adjustment

**Option B: Redefine Scope**
- Revisit Phase 3 scoping table for this deliverable
- Update target reader, key question, or constraints
- Revise custom prompt to reflect new scope
- Call `studio_create` with refined prompt
- Best for: Initial scope was misaligned with actual need

**Option C: Add Source**
- If output reveals missing context or perspective
- Add new source via `source_add` to the notebook
- Regenerate artifact to incorporate new source
- Best for: Sources were incomplete, need additional context

---

## Cross-Reference

**If starting from academic papers:** Use `/research-synthesis-planner` first to systematically organize, cut, and extract insights from paper collections. Then bring structured research into `multi-output-content-planner` for publication planning.

---

## Key Design Principles

### Principle 1: Single Strategic Input
Gather audience, purpose, detail level, and success metrics once upfront. This information informs all subsequent deliverable planning and scoping. No per-deliverable re-asking.

### Principle 2: Predetermined Templates
Don't design deliverables from scratch. Use predefined templates that map audience + purpose to specific deliverable combinations proven to work together.

### Principle 3: Explicit Scoping
Each deliverable has clear boundaries:
- Target reader (who specifically?)
- Key question answered (what problem?)
- Success criteria (how do we know it works?)
- Scope boundaries (in/out of scope)

This prevents scope creep and misalignment.

### Principle 4: Prompt as Blueprint
Optimized prompts are the "blueprint" for output generation. They encode all the scoping decisions, constraints, and success criteria. Quality prompts → quality outputs.

### Principle 5: Parallel Execution
All outputs are independent and can generate simultaneously from the same source notebook. No need to wait or re-process sources.

### Principle 6: Real MCP Execution
All notebook operations use actual NotebookLM MCP tools, enabling seamless integration with Claude Code and eliminating manual UI steps.

## Example: Complete Planning Session

**User Input (Phase 1):**
- Audience: Mixed (C-level executives + engineering teams)
- Purpose: Decide whether to adopt + implement Claude agents
- Detail Level: Executive summaries + technical depth
- Deliverables: 4
- Success: Decision made by exec team, implementation path clear for engineers

**Deliverable Plan (Phase 2 - selected from core templates):**
1. Executive Briefing (1,500 words, business case)
2. Study Guide (5,000+ words, technical depth)
3. Ecosystem Infographic (single-page visual)
4. FAQ Document (common questions from all audiences)

**Scoping (Phase 3):**

| Deliverable | Target | Key Question | Success | Scope |
|---|---|---|---|---|
| Executive Briefing | C-level (CFO, VP Eng) | ROI + Implementation Timeline? | Budget approved, pilot planned | Value prop only, no code |
| Study Guide | Senior Engineers | How to design agents? | Can architect solution | Complete technical depth |
| Infographic | All audiences | How do components fit together? | Understand relationships | Architecture diagram |
| FAQ | All audiences | What about [common concern]? | Questions answered | Common concerns addressed |

**Prompts (Phase 4):**
- Each prompt customized with specific scoping decisions
- Constraints tailored to target reader
- Success criteria embedded in prompt

**Result:** 4 complementary outputs delivered via real MCP execution in ~45 minutes, each precisely scoped for its audience.

## Reference Files

**See these files for detailed information:**

- **[DELIVERABLE_TEMPLATES.md](references/DELIVERABLE_TEMPLATES.md)** - 8 core templates for audience + purpose combinations. Use to select your deliverable mix.

- **[PROMPT_TEMPLATES.md](references/PROMPT_TEMPLATES.md)** - Prompt templates for each deliverable type with standardized {{PLACEHOLDER}} syntax.

## Example Usage

**User asks:** "I have 20 YouTube videos about Claude agents and want to create learning materials."

**Skill workflow:**

1. **Phase 0 - Prep:**
   - Create notebook via `mcp__notebooklm-mcp__notebook_create`

2. **Phase 1 - Strategic Input:**
   - Ask 5 core questions about audience, purpose, success metrics

3. **Phase 2 - Plan:**
   - Use MULTI_STAKEHOLDER + ENGINEERS templates
   - Select: Executive Briefing, Study Guide, Video Overview, Slide Deck

4. **Phase 3 - Scope:**
   - Briefing: C-level, "Should we adopt?", 1,500 words, business language
   - Guide: Engineers, "How to implement?", 5,000+ words, technical depth
   - Video: Both, "Tutorial walkthrough", 10-15 min, step-by-step
   - Deck: C-level, "Business case", 10 slides, minimal text

5. **Phase 4 - Prompts:**
   - Extract templates from PROMPT_TEMPLATES.md
   - Customize with {{PLACEHOLDER}} syntax for Phase 3 scope
   - Save prompts for execution

6. **Phase 1.5 - Load Sources:**
   - Add 20 video URLs via `mcp__notebooklm-mcp__source_add` (type=url)
   - Wait for all sources to load in notebook

7. **Phase 5 - Execute:**
   - Call `mcp__notebooklm-mcp__studio_create` for each of 4 artifacts with custom prompts
   - Poll `mcp__notebooklm-mcp__studio_status` for completion
   - Collect results

**Outcome:** Coherent 4-output system, each precisely scoped for its audience, delivered in ~1 hour (including planning + execution via real MCP).

## Tips for Success

### Planning Phase
- Be specific about target audience (not "engineers" but "senior engineers designing systems")
- Define success upfront (what decision/action should result?)
- Use templates—don't reinvent deliverable plans
- Scope is king—clear boundaries prevent misalignment

### Execution Phase
- All sources go into one notebook (processed once via Phase 1.5)
- All outputs launch in parallel (no waiting)
- Use custom_prompt parameter with {{PLACEHOLDER}} syntax
- Save the plan document for reference and future iterations

### Iteration
- Use the Phase 5 decision tree if output misses mark
- Choose: (a) refine prompt, (b) redefine scope, (c) add source
- Document what changed and why for future reference
