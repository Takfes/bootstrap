# NotebookLM Research Planner: Prompt Library

Complete prompt templates for all analysis phases. All prompts open with: **"Read the anchor context note carefully before answering."**

---

## Phase 1: Orientation Prompts

### P1: Paper Briefings Table + Narrative

**Purpose:** Quick reference for all papers with consistent framing per anchor.

**Template:**

```
Read the anchor context note carefully before answering.

Given the anchor's research lens ("{{PROBLEM_STATEMENT}}") and core decision ("{{CORE_QUESTION}}"),
create a two-part briefing for each paper in the knowledge base:

### Part A: Briefing Table

Create a markdown table with these columns:
- **Label** (e.g., A1, A2, etc.)
- **Authors & Year**
- **Core Finding** (one sentence aligned to anchor)
- **Evidence Strength** (Strong/Medium/Weak based on methodology + sample size)
- **Direct Relevance to {{CORE_QUESTION}}** (High/Medium/Low)

### Part B: Narrative Summaries

For each paper, write 2-3 sentences answering:
1. What does this paper study, specifically?
2. How does it address or inform the anchor's core decision/constraint?
3. What is the key limitation or assumption that affects its relevance here?

Keep summaries under 100 words each. Prioritize applied papers or those with direct evidence.

Return the table, then the narratives in label order (A1, A2, A3, etc.).
```

---

### P2: Relevance Ranking — 3-Tier Grouping

**Purpose:** Stratify papers into decision-relevant tiers.

**Template:**

```
Read the anchor context note carefully before answering.

Re-read the anchor's constraints ("{{CONSTRAINTS}}") and success criteria ("{{SUCCESS_CRITERIA}}").

Group all papers into three tiers. Be explicit about why each paper lands in its tier.

**CORE PAPERS** (3-6 papers)
These directly address the {{CORE_QUESTION}} with empirical evidence or design precedent.
For each: 1 sentence explaining why it's core, plus one key claim that informs the decision.

**SUPPORTING PAPERS** (4-8 papers)
These provide context, validate assumptions, or explore adjacent methods the core papers depend on.
For each: Why is this important context? What assumption or technique does it ground?

**BACKGROUND PAPERS** (2-4 papers)
These provide foundational concepts or historical context but don't directly shape the decision.
For each: One sentence on what foundational concept it establishes.

Use the anchor's constraints as your sorting filter. A paper that seems foundational but violates
an operational constraint (e.g., requires daily retraining when you can only train weekly) moves down a tier.

End with: "For the next phase, focus analysis on {{N}} core papers."
```

---

## Phase 2: Thematic Cut Prompts (Parametric Template)

### P3-Pn: Thematic Cut Analysis (One per Dimension)

**Purpose:** Deep dive into one thematic dimension with structured sub-questions.

**Template:**

```
Read the anchor context note carefully before answering.

Analyze the papers through the lens of: **{{THEME}}**

This theme matters to the anchor because: {{THEME_JUSTIFICATION}}

### Part A: Five Analytic Questions

For each question below, scan the papers and provide:
- Which papers address this? (by label: A1, A2, etc.)
- What's the consensus or key debate?
- Any contradictions? How are they explained?

**Q1: {{SUB_QUESTION_1}}**
[Papers answer this:]

**Q2: {{SUB_QUESTION_2}}**
[Papers answer this:]

**Q3: {{SUB_QUESTION_3}}**
[Papers answer this:]

**Q4: {{SUB_QUESTION_4}}**
[Papers answer this:]

**Q5: {{SUB_QUESTION_5}}**
[Papers answer this:]

### Part B: Synthesis

**Synthesis Question:**
Across all five sub-questions, what is the unified insight for the anchor's core decision?
How would you apply this theme to {{CORE_QUESTION}}?

Provide a 3-4 sentence synthesis that directly informs a choice or trade-off.
```

---

## Phase 3: Synthesis Prompts

### P6: Composite Model/Framework Recipe

**Purpose:** Map papers to specific architectural or conceptual components.

**Template:**

```
Read the anchor context note carefully before answering.

Using the anchor's target architecture ("{{ARCHITECTURE}}") and the thematic analyses you've completed,
create a "Recipe" mapping papers to architecture components.

For each component in the architecture:

**Component: {{NAME}} (Purpose: {{PURPOSE}})**

Papers that inform this component: [List by label + one-line reason]
- {{PAPER_LABEL}}: Why this paper belongs here

Key design choice from papers: [What do the papers collectively tell you to do?]

Recommended approach: {{RECOMMENDATION}}

Risk or trade-off: {{RISK}}

---

End with a summary table:

| Architecture Component | Primary Papers | Secondary Support | Key Design Choice |
|---|---|---|---|
| {{COMPONENT_1}} | {{LABELS}} | {{LABELS}} | {{CHOICE}} |
| {{COMPONENT_2}} | {{LABELS}} | {{LABELS}} | {{CHOICE}} |

This recipe should make it clear: "To build {{COMPONENT_X}}, we rely on {{PAPERS}} and should {{RECOMMENDATION}}."
```

---

### P7: Gap Analysis — What Papers Don't Cover

**Purpose:** Identify missing pieces; guide future research or prototyping.

**Template:**

```
Read the anchor context note carefully before answering.

Re-read the anchor's core decision ("{{CORE_QUESTION}}") and success criteria ("{{SUCCESS_CRITERIA}}").

For each gap below, state:
1. The gap (what's missing from the literature?)
2. Which papers come closest? Why do they fall short?
3. How would you fill this gap empirically or in design?

### Gap 1: {{GAP_DESCRIPTION}}
Papers that address this partially: {{LABELS}} — but they [limitation]
How to fill: {{APPROACH}}

### Gap 2: {{GAP_DESCRIPTION}}
Papers that address this partially: {{LABELS}} — but they [limitation]
How to fill: {{APPROACH}}

### Gap 3: {{GAP_DESCRIPTION}}
Papers that address this partially: {{LABELS}} — but they [limitation]
How to fill: {{APPROACH}}

### Gap 4: {{GAP_DESCRIPTION}}
Papers that address this partially: {{LABELS}} — but they [limitation]
How to fill: {{APPROACH}}

### Gap 5: {{GAP_DESCRIPTION}}
Papers that address this partially: {{LABELS}} — but they [limitation]
How to fill: {{APPROACH}}

End with: "These gaps suggest the following experimental priorities or design decisions should
be validated with [specific empirical work or prototyping]."
```

---

### P8: Data & Implementation Checklist

**Purpose:** Translate literature into practical requirements.

**Template:**

```
Read the anchor context note carefully before answering.

Create an implementation checklist grounded in the papers. Organize by category:

### Data Requirements
- What data would papers suggest you need? (features, granularity, history depth, etc.)
- Which papers justify each requirement? (reference by label)
- [5-8 bullet points with paper citations]

### Model / Algorithm Decisions
- What algorithms or techniques do papers recommend for your constraints?
- Any trade-offs or alternatives papers discuss?
- [5-8 bullet points with paper citations]

### Validation & Testing
- How should you measure success, per the papers?
- Any benchmarks or evaluation protocols papers establish?
- [3-5 bullet points with paper citations]

### Operational / Timeline Considerations
- Do papers discuss deployment cadence, retraining frequency, or cold-start handling?
- Any gotchas or failure modes to anticipate?
- [3-5 bullet points with paper citations]

### Known Unknowns / Paper Gaps
- What did papers NOT address that you'll need to figure out experimentally?
- [2-3 bullet points linking to Gap Analysis, above]

End with: "To move forward, prioritize the [N] highest-impact items from the list above,
then validate against the papers' evidence before committing to implementation."
```

---

## Phase 4: Deliverable Prompts (Optional)

Use these only if user wants slide decks, reports, or other formatted outputs from the research synthesis.

### P_deck_align: Alignment Slide Deck (Any Audience)

**Purpose:** Single deck that works across stakeholder groups.

**Template:**

```
Read the anchor context note carefully before answering.

Create a slide deck (8-10 slides, PowerPoint format or markdown slides) on:
**{{ DELIVERABLE_TITLE }}**

This deck should serve: {{ STAKEHOLDER_DESCRIPTION }}

### Slide-by-Slide Guidance

1. **Title Slide**
   - Title: {{ DECK_TITLE }}
   - Subtitle: {{ RESEARCH_LENS_ONELINER }}

2. **Research Question**
   - State the anchor's core decision
   - Show the constraints or context

3. **Approach**
   - How many papers? What time range?
   - What themes did you analyze?

4. **Key Finding 1: {{ THEME_1 }}**
   - One major insight per theme slide
   - Use paper labels (A1, A2) in speaker notes
   - Suggest one data viz or diagram

5. **Key Finding 2: {{ THEME_2 }}**
   - [Repeat structure]

6. **Key Finding 3: {{ THEME_3 }}**
   - [Repeat structure]

7. **Framework / Recommendation**
   - Show the composite model or architecture
   - Map 2-3 core papers to key components
   - Speaker notes: one sentence per component explaining the paper evidence

8. **Gaps & Future Work**
   - 3 critical gaps
   - One-sentence mitigation for each
   - Speaker notes: which papers almost addressed this?

9. **Conclusion & Next Steps**
   - Restate the core decision and how literature informs it
   - 2-3 immediate actions

### Tone & Constraints
- Tone: {{ TONE_DESCRIPTION }} (e.g., "professional but accessible")
- Citations: Minimal on slides; full details in speaker notes using {{PAPER_LABEL}} format
- Visuals: Suggest diagrams, tables, or comparison matrices where helpful

Return a deck outline or full markdown slide deck with speaker notes.
```

---

## Prompt Library Index

| Prompt ID | Phase | Purpose | Key Output |
|-----------|-------|---------|-----------|
| P1 | Orientation | Paper briefings | Table + narrative summaries |
| P2 | Orientation | Relevance ranking | 3-tier grouping of papers |
| P3-Pn | Thematic Cuts | Deep-dive analysis | One per user-chosen dimension |
| P6 | Synthesis | Architecture mapping | Recipe: paper → component |
| P7 | Synthesis | Gap analysis | 5 critical gaps + mitigation |
| P8 | Synthesis | Implementation | Practical checklist |
| P_deck_align | Deliverables (opt) | Multi-audience deck | Slide outline + speaker notes |

---

## Using This Library

### Choosing Prompts

1. **Always start with P1 + P2** (orientation — 5 minutes each)
2. **Add P3-Pn for each thematic dimension** (usually 3-5 prompts)
3. **Then P6 + P7 + P8** (synthesis — 10 minutes each)
4. **Add deck prompts only if user requests formatted outputs**

### Customization Rules

- Replace `{{PLACEHOLDER}}` with specific content from anchor
- Keep opening line: *"Read the anchor context note carefully before answering."*
- Adapt sub-questions (P3-Pn) to match user's chosen themes
- For gaps (P7), list 5-6 gaps specific to their domain

### Order Matters

Execute prompts in this sequence:
1. P1 (paper briefings)
2. P2 (relevance ranking)
3. P3, P4, P5... (thematic cuts, one per dimension)
4. P6 (framework recipe)
5. P7 (gap analysis)
6. P8 (checklist)
7. Deck prompts last (if requested)

Each prompt assumes prior prompts have been completed and creates artifacts that feed into subsequent prompts.

---

## Common Customizations

### For Machine Learning / AI Research
- Sub-Q1: "What does this paper claim about generalization or robustness?"
- Sub-Q2: "How do papers handle data scarcity or distribution shift?"
- Sub-Q3: "What trade-offs exist between accuracy, speed, and interpretability?"

### For Systems / Architecture Research
- Sub-Q1: "How does this paper scale as load increases?"
- Sub-Q2: "What are the fault tolerance or availability assumptions?"
- Sub-Q3: "How does the design handle heterogeneous components or environments?"

### For Operations Research / Supply Chain
- Sub-Q1: "What time horizons (hours, days, weeks) do papers optimize over?"
- Sub-Q2: "How do papers handle uncertainty or stochastic elements?"
- Sub-Q3: "What trade-offs exist between solution quality and computational cost?"
