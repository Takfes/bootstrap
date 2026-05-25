# Research Anchor Document

## Research Context & Framing

This anchor document establishes the interpretive lens for all subsequent analysis of the paper collection. Every query to NotebookLM begins by referencing this anchor to ensure consistency and focus.

**Section Structure:** Required sections (below) must be completed. Optional sections enhance focus but aren't mandatory.

---

## REQUIRED SECTIONS

The following sections must be completed for every anchor document. They form the core research lens.

### Problem Statement / Research Lens [REQUIRED]

**Define the core challenge or perspective that frames this research:**

What specific problem, decision, or question motivates this literature review?

*Example (Applied):* "We're building a real-time inventory replenishment system for retail chains with 200+ stores. Papers must inform architectural decisions about: demand forecasting accuracy, optimization timing (batch vs. continuous), and robustness to supply disruptions."

*Example (Pure Literature Review):* "Systematic review of conformal prediction methods for time series: understanding when and why uncertainty quantification improves downstream decision-making."

**Your lens:**
[FILL IN: 2-3 sentences describing your core research question or applied problem]

---

### Core Decision or Design Question [REQUIRED]

**What specific decision or architectural choice must this literature inform?**

The papers in this collection exist to answer this central question. Every thematic cut and synthesis prompt will anchor back to it.

*Example:* "Should we use multi-model ensemble forecasting or single large-scale model, and which papers provide empirical evidence?"

*Example:* "How do we design a composable agentic system where skills can be combined dynamically without central orchestration?"

**Your question:**
[FILL IN: A single, specific question the papers must address]

---

### Success Criteria [REQUIRED]

**How will you know this literature review succeeded?**

Define measurable outcomes or decision-readiness indicators.

*Example:*
- Criteria 1: "Can rank 3+ ensemble methods by expected accuracy improvement (with confidence intervals from papers)"
- Criteria 2: "Can design a 6-component system with clear paper-to-component mappings"
- Criteria 3: "Can identify 2-3 critical gaps and propose empirical validation plan"

**Your success criteria:**
[FILL IN: 3-5 bullets describing what "done" looks like]

---

## OPTIONAL / APPLIED SECTIONS

Use these sections if applicable to your research. They add precision for applied projects but aren't required for pure literature reviews.

### Domain Constraints & Context [OPTIONAL]

**What operational, technical, or domain-specific constraints shape interpretation?**

These constraints determine relevance tiers and scope boundaries for every analysis. (Leave blank for pure literature reviews.)

*Example:*
- Constraint 1: "We must make weekly forecasts for 50+ SKUs with <15 min inference time per run"
- Constraint 2: "Our supply chain has significant lead times (3-14 days), so we need both point estimates and uncertainty bounds"
- Constraint 3: "We can retrain models weekly but not daily"

**Your constraints:**
[FILL IN: 3-5 bullets describing operational limits, domain norms, or technical requirements; or "N/A"]

---

### Model / Framework Architecture [OPTIONAL]

**If applying this research to a specific system, describe the target architecture:**

(Leave as "N/A for pure literature review" if this is a pure synthesis project.)

*Example:*
```
┌─────────────────────────────────────┐
│ Input Layer (Demand Signals)        │
├─────────────────────────────────────┤
│ Feature Engineering                 │
├─────────────────────────────────────┤
│ Forecasting Module (Ensemble or SLM)│
├─────────────────────────────────────┤
│ Optimization Layer (Replenishment)  │
├─────────────────────────────────────┤
│ Output: Order Quantity & Timing     │
└─────────────────────────────────────┘
```

**Your architecture or N/A:**
[FILL IN: ASCII diagram or bullet-point description of target system]

---

### Applied Setting [OPTIONAL]

**If this research informs a real or near-future project, describe the setting:**

(Omit for pure literature reviews.)

*Example:*
- **Organization:** Fortune 500 retail chain, 250+ stores across North America
- **Timeline:** 6 weeks from research kickoff to architecture decision
- **Team:** 1 ML engineer, 1 supply chain analyst, 1 product manager
- **Success metric:** Reduce total inventory holding costs by 8-12% while maintaining 96% in-stock rate

**Your setting:**
[FILL IN: Organization, timeline, team, business/research metric; or "N/A"]

---

## Notes for Analysis [OPTIONAL]

**Any additional context for NotebookLM?**

*Example:*
- "Focus on recent methods (2020+) but don't dismiss classical approaches that cite new comparisons"
- "We care about implementation feasibility, not just theoretical optimality"
- "Emphasize papers with real operational data or case studies, not just simulations"

**Your notes:**
[FILL IN: Any special guidance or anti-patterns to highlight; or "None"]
