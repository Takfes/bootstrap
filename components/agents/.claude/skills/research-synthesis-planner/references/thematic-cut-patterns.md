# Thematic Cut Patterns: Designing Analytic Lenses for Your Domain

This guide helps you identify 3-5 thematic dimensions for your research collection. Each dimension becomes one prompt (P3, P4, P5, etc.) that analyzes papers through a specific analytical lens.

---

## Core Principle: The 5+1 Structure

Every thematic cut prompt uses this structure:

**Five Analytic Sub-Questions** → answerable by scanning papers
- Q1: [Specific aspect of the theme]
- Q2: [Complementary aspect]
- Q3: [Contradiction or trade-off]
- Q4: [Evidence or validation]
- Q5: [Practical implication or gotcha]

**One Synthesis Question** → ties all five back to the anchor's core decision
- "Across all five sub-questions, what is the unified insight?"

This structure ensures each thematic cut produces both granular analysis (Q1-Q5) and strategic synthesis (Q6).

---

## How to Choose Your Themes

### Rule 1: Align with Design or Decision Components

If your anchor architecture has 4-5 major components, create one theme per component.

**Example: Inventory Replenishment System**
```
Architecture Components:
├── Demand Forecasting
├── Supply Chain Modeling
├── Optimization Engine
├── Deployment & Adaptation
└── Uncertainty Quantification

Themes (One per Component):
├── THEME 1: Forecasting accuracy and methodology
├── THEME 2: How papers model supply disruptions and lead times
├── THEME 3: Optimization objectives and algorithms
├── THEME 4: Real-world deployment and continuous learning
└── THEME 5: Uncertainty quantification and robustness
```

### Rule 2: Or Align with Core Research Questions

If your research is exploratory (not system design), organize around research sub-questions.

**Example: Conformal Prediction for Time Series**
```
Core Research Question:
"How does uncertainty quantification improve decision-making in time-series applications?"

Sub-Themes:
├── THEME 1: Fundamentals — what is conformal prediction and why does it work?
├── THEME 2: Time-series specific challenges (non-exchangeability, temporal dependence)
├── THEME 3: Practical coverage guarantees in offline + online settings
├── THEME 4: Downstream decision-making (how better uncertainty → better choices?)
└── THEME 5: Applications and real-world validation
```

### Rule 3: Avoid Over-Fragmentation

- **Too few themes** (<3): You miss key dimensions; synthesis feels shallow.
- **Too many themes** (>7): Too granular; users get decision fatigue and redundant insights.
- **Ideal range**: 3-5 themes.

### Rule 4: Themes Should Not Overlap

Each theme should address a distinct analytical lens. If two themes answer the same questions, merge them.

❌ **Bad:** THEME 1 = "Accuracy" | THEME 2 = "Model accuracy and calibration"
✓ **Good:** THEME 1 = "Accuracy metrics and evaluation" | THEME 2 = "Calibration and uncertainty"

---

## Theme Design Patterns by Domain

### Pattern 1: Machine Learning / Predictive Modeling

Typical themes:

1. **Data & Features**
   - Q1: What data do papers assume? (scope, granularity, history depth)
   - Q2: How do papers handle feature engineering?
   - Q3: Trade-offs: raw features vs. engineered features?
   - Q4: Evidence: do papers compare?
   - Q5: Practical gotcha: missing data or data quality issues?

2. **Model Architecture & Algorithm Selection**
   - Q1: What model types do papers recommend for your domain?
   - Q2: How do papers compare accuracy vs. interpretability?
   - Q3: Trade-offs: simpler models vs. deep/complex?
   - Q4: Evidence: which models win in benchmark comparisons?
   - Q5: Practical gotcha: cold-start, scalability, or interpretability limits?

3. **Generalization & Robustness**
   - Q1: How do papers evaluate generalization? (cross-validation, hold-out, time-based split?)
   - Q2: What robustness tests do papers run?
   - Q3: Trade-off: tight training perf vs. robust generalization?
   - Q4: Evidence: realistic failure modes papers document?
   - Q5: Practical gotcha: distribution shift or domain adaptation?

4. **Training & Deployment Cadence**
   - Q1: How often do papers retrain or update models?
   - Q2: Cold-start or warm-start handling?
   - Q3: Trade-off: batch retraining vs. online/incremental updates?
   - Q4: Evidence: production systems papers describe?
   - Q5: Practical gotcha: model staleness, concept drift, or resource constraints?

5. **Uncertainty & Confidence**
   - Q1: How do papers quantify uncertainty? (Bayesian, ensemble, conformal, etc.)
   - Q2: Why does uncertainty matter for decisions in this domain?
   - Q3: Trade-off: cheaper uncertainty estimates vs. rigorous guarantees?
   - Q4: Evidence: how well do uncertainty estimates calibrate in practice?
   - Q5: Practical gotcha: user overconfidence in point estimates?

### Pattern 2: Operations Research / Optimization

Typical themes:

1. **Problem Formulation & Scope**
   - Q1: What objective functions do papers optimize?
   - Q2: What constraints do papers enforce?
   - Q3: Trade-off: exact solutions vs. heuristics?
   - Q4: Evidence: real problem instances papers test on?
   - Q5: Practical gotcha: objective mismatch or hidden constraints?

2. **Time Horizons & Recurrence**
   - Q1: What time horizons do papers optimize over? (seconds to weeks?)
   - Q2: How often do papers re-optimize or replan?
   - Q3: Trade-off: long-horizon planning vs. responsive adaptation?
   - Q4: Evidence: real operational data papers validate against?
   - Q5: Practical gotcha: forecast error accumulation or plan obsolescence?

3. **Uncertainty & Stochasticity**
   - Q1: How do papers model randomness? (scenarios, distributions, robust optimization?)
   - Q2: How do papers validate uncertainty assumptions?
   - Q3: Trade-off: assuming known distributions vs. robust/adaptive?
   - Q4: Evidence: real data or operational results?
   - Q5: Practical gotcha: model misspecification or tail events?

4. **Computation & Solution Time**
   - Q1: What algorithms do papers use? (exact, heuristic, ML-hybrid?)
   - Q2: How do computation times scale with problem size?
   - Q3: Trade-off: solution quality vs. time budget?
   - Q4: Evidence: wall-clock times papers report?
   - Q5: Practical gotcha: solver instability or solver timeouts?

5. **Deployment & Continuous Optimization**
   - Q1: How do papers handle initial deployment or ramp-up?
   - Q2: How often do solutions update?
   - Q3: Trade-off: stable solutions vs. exploiting new information?
   - Q4: Evidence: production rollouts or A/B tests papers describe?
   - Q5: Practical gotcha: resistance to change, user acceptance, or system inertia?

---

## Anti-Patterns: Themes to Avoid

❌ **Overly Broad Themes** — "Everything about the topic" is too vague to focus analysis.

❌ **Perfectly Overlapping Themes** — "Accuracy" and "Evaluation metrics" answer the same questions; merge them.

❌ **Single-Paper Themes** — Themes should light up 3+ papers per dimension, not focus on one paper's approach.

❌ **Too Many Implementation Details** — "Hyperparameter tuning for algorithm X" is too narrow; prefer "Trade-offs: complexity vs. interpretability."

---

## Validating Your Themes

Before running the analysis, sanity-check your themes:

**Checklist:**

- [ ] **Coverage:** Do your 3-5 themes collectively span the anchor's core decision?
- [ ] **Granularity:** Does each theme produce 5 distinct sub-questions, or would it collapse into one question?
- [ ] **Orthogonality:** Do themes address different dimensions, or do they overlap?
- [ ] **Paper Relevance:** For each theme, can you name 3+ papers that address it?
- [ ] **Synthesis Clarity:** For each theme, can you write a 2-3 sentence synthesis that informs a choice?

If any check fails, refine or merge themes.

---

## Examples: Fully Developed Theme Sets

### Example 1: Machine Learning Application (Demand Forecasting)

**Core Decision:** "Forecast-driven vs. reactive replenishment? What optimization horizon?"

**Themes:**
1. THEME: "Demand forecasting accuracy and uncertainty"
   - Papers: [A1, A5, A8, A12]
   - Q1: What forecast horizons do papers optimize? (days? weeks?)
   - Q2: How do papers quantify forecast uncertainty?
   - Q3: Trade-off: accuracy vs. prediction interval width?
   - Q4: Evidence: real SKU data papers validate on?
   - Q5: Practical gotcha: forecast bias or seasonal miss?

2. THEME: "Model architecture selection for forecasting"
   - Papers: [A2, A4, A9]
   - Q1: What model types do papers recommend?
   - Q2: How do papers compare simpler vs. complex models?
   - Q3: Trade-off: accuracy vs. interpretability and deployment ease?
   - Q4: Evidence: benchmark comparisons?
   - Q5: Practical gotcha: cold-start or concept drift issues?

3. THEME: "Deployment and continuous adaptation"
   - Papers: [A3, A6, A10]
   - Q1: How often do papers retrain? (daily? weekly? adaptive?)
   - Q2: How do papers handle distribution shift?
   - Q3: Trade-off: stable forecasts vs. responsive updates?
   - Q4: Evidence: production systems papers describe?
   - Q5: Practical gotcha: feedback loops or compounding errors?

### Example 2: Operations Research Application

**Core Decision:** "Exact vs. heuristic optimization? What solution time tradeoff?"

**Themes:**
1. THEME: "Problem formulation and constraint modeling"
   - Papers: [B1, B3, B7]
   - Q1: What objective functions do papers optimize? (cost? service? hybrid?)
   - Q2: How are constraints modeled? (hard vs. soft?)
   - Q3: Trade-off: problem realism vs. tractability?
   - Q4: Evidence: real problem instances papers test on?
   - Q5: Practical gotcha: hidden constraints or objective misalignment?

2. THEME: "Algorithm selection and solution time"
   - Papers: [B2, B5, B8]
   - Q1: Which algorithms (exact, heuristic, ML-hybrid, metaheuristic) do papers use?
   - Q2: How does solution time scale with problem size?
   - Q3: Trade-off: solution quality vs. computation budget?
   - Q4: Evidence: wall-clock times and optimality gaps papers report?
   - Q5: Practical gotcha: solver instability or inconsistent convergence?

3. THEME: "Operational deployment and continuous re-optimization"
   - Papers: [B4, B6, B9]
   - Q1: How often do papers re-optimize plans? (daily? per-event? statically?)
   - Q2: How do papers handle plan updates and uncertainty?
   - Q3: Trade-off: stable plans vs. exploiting new information?
   - Q4: Evidence: production rollouts or A/B tests papers describe?
   - Q5: Practical gotcha: user resistance or system lag?

---

## Guiding Users to Choose Themes

When running the skill, ask in Round 2:

> "What 3-5 themes would you like to analyze through? For example:
> - If you're optimizing a system, consider: one theme per major component
> - If you're exploring theory, consider: foundational concepts → recent advances → open problems
> - If you're solving a specific problem, consider: what design decisions must the papers inform?
>
> Examples for your anchor:
> - [DOMAIN-SPECIFIC EXAMPLES based on their anchor]
>
> Which approach resonates? Or propose your own themes."

Provide 2-3 pre-generated examples tailored to their anchor to reduce decision fatigue.
