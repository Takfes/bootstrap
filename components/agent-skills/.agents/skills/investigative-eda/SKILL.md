---
name: investigative-eda
description: Methodology for investigative, theory-building exploratory data analysis on tabular datasets. Use this skill whenever the task is open-ended understanding of a dataset — "explore this", "what's going on in this data", "what predicts the target", "find what's interesting", "tell me about this dataset", "profile this", or any prompt that wants insight rather than a single lookup. The skill encodes the investigative loop (observe → form working theory → consider alternatives → probe → refine), discipline for resumable state, leakage and artifact checks, segment-size guardrails, and the structure of a final findings report. Pair with the `eda-tooling` skill for library-specific code patterns. Use this skill proactively whenever a fresh dataset arrives and the user's intent is exploratory.
---

# Investigative EDA

You are doing detective work, not running a stats course. Each iteration you sharpen your understanding of what is going on in this data. You do **not** dump every possible chart. You follow the strongest thread, build a working theory, design the next view that would either crystallize or kill it, and update.

## The loop

Run the loop iteratively. Each pass goes:

```
1. Observe        → look at what you have so far
2. Theorize       → articulate the most interesting working theory you can support
3. Alternatives   → generate 2–3 competing explanations for the same pattern
4. Probe          → design ONE view that best discriminates between them
5. Refine         → update the working theory: confirm, narrow, pivot, or kill
```

A "view" is whatever shows you what you need: a focused plot, a grouped statistic, a faceted breakdown, a segment-isolated re-cut. It is almost never a wall of plots from an auto-EDA tool.

The critical step is **3 (Alternatives)**. Skipping it produces shallow analysis — patterns get adopted as findings without the most basic stress-test. A real investigator considers alternatives explicitly.

## Iteration mindset: depth, not coverage

You have a default budget of **3–5 iterations**. Use them on **the strongest thread**, not on covering ground.

| Iter | Focus |
|---|---|
| 1 | Orient. Shape, types, missingness, target distribution. Identify 2–4 candidate threads worth pursuing. Pick one. |
| 2 | Pursue the chosen thread. Build the first working theory. Generate alternatives. Probe. |
| 3 | Refine the surviving theory or pivot to a stronger thread that emerged. |
| 4 | Stress-test the leading theory: leakage check, segment robustness, artifact check. |
| 5 | Either consolidate (write up) or pursue one secondary thread that survived. |

This is **a guide, not a script**. If iteration 2 kills your only theory, iteration 3 should pivot, not continue refining a dead thread. If by iteration 3 the leading theory is robust and the secondary threads are weak, write up early — don't pad.

The failure mode this prevents: producing a "thorough" report that touches every variable and concludes nothing.

## Working theory log — the core artifact

Every working theory goes into `eda_output/theory_log.json` **before** you probe it. Format:

```json
{
  "id": "T3",
  "iteration": 2,
  "claim": "Customers in their first 6 months churn at multiples of the base rate, and the effect concentrates in month-to-month contracts",
  "confidence": "medium",
  "evidence_so_far": ["figs/iter2_tenure_buckets.png shows 47% vs 11% baseline", "concentrated in m2m: figs/iter2_tenure_x_contract.png"],
  "alternatives": [
    "Tenure is a proxy for contract type (new customers default to m2m)",
    "Tenure-churn link is an artifact of how 'churn' is defined for short-tenure customers",
    "A single acquisition campaign in the last 6 months brought in low-quality customers"
  ],
  "would_sharpen": "Faceted churn rate by tenure bucket, holding contract type fixed",
  "would_kill": "If within m2m customers, churn rate is flat across tenure buckets, the tenure effect is mediated and not independent",
  "next_view": "groupby([contract, tenure_bucket]).churn.mean(), plotted as grouped bars",
  "status": "probing",
  "outcome": null
}
```

Fields:
- **claim** — the working theory in one sentence. Specific. Falsifiable in principle.
- **confidence** — `low` / `medium` / `high`. Honest. Most working theories should start at `low`.
- **evidence_so_far** — what made you form this theory. Links to figures.
- **alternatives** — 2–3 competing explanations. **Required**, not optional.
- **would_sharpen** — what view, if it showed pattern X, would make you more confident.
- **would_kill** — what view, if it showed pattern Y, would make you abandon this theory.
- **next_view** — the actual concrete thing to draw or compute next.
- **status** — `probing` / `confirmed` / `narrowed` / `killed` / `pivoted`.
- **outcome** — fill in after probing. What happened. Reference the figure.

The discipline: writing `would_kill` *before* you draw the chart is what keeps you honest. If you can't articulate what would kill the theory, you don't have a theory yet — you have a vibe.

## Competing-explanations playbook

For any pattern "A relates to B", the candidate alternatives are almost always one of:

1. **Confounding** — A and B share a common driver C. Probe: condition on C.
2. **Mediation** — A's effect on B runs entirely through some intermediate M. Probe: control for M.
3. **Selection / sampling artifact** — the pattern only exists because of how the data was collected. Probe: examine the collection process or compare segments with different selection.
4. **Leakage / definitional** — A is partly a function of B by construction (or vice versa). Probe: inspect how each was computed.
5. **Outlier-driven** — a small slice of rows produces the apparent pattern. Probe: remove top/bottom 1–5% and re-check; check effect within different segments.
6. **Threshold / non-linear** — the relationship only exists in a specific range. Probe: faceted views by value bucket.

Use this list explicitly when generating the `alternatives` field. See `references/investigation_patterns.md` for worked examples.

## Thread-level stopping rules

Abandon a thread when **any** is true:

- Two consecutive probes failed to sharpen the claim (no clearer pattern, no narrowing of conditions).
- Sharpening would require data you don't have access to.
- Sharpening would require a view so specific it crosses into post-hoc fishing — a slice defined by the very pattern you're trying to confirm.
- The claim has been narrowed to a segment small enough to fail the segment-size guardrail (below).

Pivoting after a thread dies is **not failure** — it is the loop working as designed.

## Segment-size guardrails

Patterns inside small segments are mostly noise. Apply these:

- **n ≥ 50 in the segment**: claim is worth pursuing.
- **20 ≤ n < 50**: caution. Mention as "tentative" if it makes the report; do not build dependent theories on top of it.
- **n < 20**: ignore for theory-building. Note as anecdote at most.

These thresholds are guidance, not law — adjust if the dataset is small overall (a 200-row dataset may warrant lower thresholds with explicit caveat) or if the effect size is enormous. But the default discipline holds.

## Leakage / artifact check — gate before "finding"

Before any working theory is upgraded from `confirmed` to a reported finding, run this checklist:

1. **Definitional leakage** — is the predictor partly a function of the target by construction? (e.g., `total_charges = monthly_charges × tenure`, when target is `churn` which terminates `total_charges`.)
2. **Temporal leakage** — was the predictor only observable *after* the target was determined? (e.g., "did customer call support" measured post-churn.)
3. **Imputation artifact** — is the pattern an artifact of how missing values were filled? Re-run the analysis on rows with no imputation; does it survive?
4. **Outlier domination** — re-run with the top/bottom 1% removed. Does the effect survive?
5. **Segment domination** — does one segment account for >70% of the apparent effect? If so, the finding belongs to that segment, not the population.
6. **Selection artifact** — was the data collected in a way that would produce this pattern even if no real relationship exists?

A theory that fails any of these is **narrowed** or **killed**, not reported as-is. The check itself is part of the report (in "Methodology notes").

## Domain-context elicitation

Domain context determines what's interesting. Without it, a 5% effect is just a number — could be a breakthrough or a rounding error.

If domain context wasn't provided in the brief, **do not just ask vaguely**. Generate 2–3 candidate framings:

> "I'm reading this as a churn problem for a subscription service where retention is the priority — a 3pp effect on churn rate would matter for business. Two alternative readings: (a) this is for a model training pipeline where any signal is interesting, (b) this is fraud detection where rare-segment patterns matter more than population effects. Which is closest, or is it something else?"

Make best-effort assumptions and proceed if no answer comes. Flag the assumption explicitly in the final report.

## Resumable state — `investigation_state.json`

The subagent may die mid-iteration (context overflow, tool failure, dataset issue). Maintain a single state file at `eda_output/investigation_state.json` with **exactly three fields**:

```json
{
  "open_threads": [
    {"id": "T7", "claim": "...", "status": "probing"},
    {"id": "T9", "claim": "...", "status": "queued"}
  ],
  "current_thread": "T7",
  "completed_threads": [
    {"id": "T1", "claim": "...", "status": "confirmed", "report_section": "F1"},
    {"id": "T2", "claim": "...", "status": "killed", "reason": "mediated by contract"}
  ]
}
```

Update at iteration boundaries only. Not a journal. Not stream-of-consciousness. The recovery property is the point: a fresh subagent reading this file should know exactly what to pick up.

## Required inputs (confirm at start)

- **Dataset path**
- **Target variable** (name + kind: continuous / binary / multiclass / ordinal / none-this-is-unsupervised)
- **Domain context** (1–2 sentences, with framings if not provided — see above)
- **Known column roles** if any (IDs to ignore, time columns, leakage suspects)

If target or domain is missing, generate framings, ask once, proceed with best guesses if no answer.

## Output artifacts

Save to `./eda_output/`:
- `orientation.json` — bootstrap script output
- `theory_log.json` — every working theory with full fields
- `investigation_state.json` — resumable state (3 fields)
- `iter_{N}_notes.md` — short narrative per iteration
- `figures/` — every figure as PNG **and** the `.py` that produced it
- `auto_eda/` — auto-EDA HTML reports (max 2 — see `eda-tooling` skill)
- `final_report.md` — see `references/report_template.md`

## Final report

Use the template in `references/report_template.md`. Key requirements:

- **TL;DR first** — 3–5 confirmed findings with effect direction and magnitude. Assume reader stops here.
- **Killed theories section** — what looked promising and didn't hold. This is high-signal for the reader; do not skip.
- **Methodology notes** — iterations run, tools used, domain framing assumed, leakage checks performed.
- **Caveats** — sample sizes for segment-level claims, assumptions made, data not available.

## Anti-patterns

- ❌ Skipping the alternatives step. "It's obviously X" is not analysis.
- ❌ Treating one chart as confirmation. Patterns that only show up in the angle you first chose usually aren't real.
- ❌ Continuing to "explore" past the stopping rules. Diminishing returns are real.
- ❌ Writing claims without `would_kill`. If you can't say what would kill it, it's not a theory.
- ❌ Reporting segment-level findings without sample sizes.
- ❌ Upgrading a theory to a finding without running the leakage check.
- ❌ Producing a "thorough" report that lists every variable and concludes nothing.
- ❌ Coverage mindset — touching every column equally rather than going deep on the strongest thread.

## Helper script

Run first in iteration 1:

```bash
python .claude/skills/investigative-eda/scripts/init_eda.py \
  --data path/to/data.csv \
  --target target_col \
  --output ./eda_output
```

Bootstraps directories, loads the dataset, prints orientation summary, seeds empty `theory_log.json` and `investigation_state.json`.

## Pairing with `eda-tooling`

For library-specific code (YData Profiling, Sweetviz, AutoViz, Dataprep, Dabl, custom matplotlib/seaborn/plotly patterns), load the `eda-tooling` skill. This skill (investigative-eda) is the **methodology**; that one is the **how-to-use-the-tools**. Keep them separate — methodology is durable, tooling churns.
