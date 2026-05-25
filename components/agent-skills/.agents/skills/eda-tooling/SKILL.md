---
name: eda-tooling
description: Library-specific code patterns for exploratory data analysis tooling — YData Profiling, Sweetviz, AutoViz, Dataprep, Dabl, and custom matplotlib/seaborn/plotly. Use this skill alongside `investigative-eda` for any open-ended EDA task. Use this skill standalone when the task is narrow and tool-specific (e.g., "generate a profile report", "run sweetviz on this dataset", "make a Plotly dashboard of these features"). Triggers on mentions of any of the named libraries, requests for "EDA report", "profile report", "auto-EDA", "data profiling tool", or when the agent needs current API patterns for any of these libraries.
---

# EDA Tooling

Library-specific recipes for EDA tools. This skill is the **how-to-use-the-tools** layer. Pair with `investigative-eda` for the methodology layer.

## Tool selection — one-line rules

- **First-pass overview** → YData Profiling (once, then move on)
- **Target-vs-features ranking** → Sweetviz with `target_feat=...`
- **Train vs test comparison** → Sweetviz `compare()`
- **Quick auto-plot of one variable vs target** → Dabl
- **Targeted programmatic plots** → Dataprep `plot()` / `plot_correlation()` / `plot_missing()`
- **Browse-everything fallback when you don't know what to look at** → AutoViz
- **Statistical depth, faceted views, publication-quality static** → Custom seaborn + matplotlib
- **Interactive exploration, hover tooltips, large categorical breakdowns** → Custom plotly

## Discipline rules

- **Cap auto-EDA tools at 2 per analysis.** YData (overview) + Sweetviz (target) is usually enough. Adding more rarely produces new signal and bloats the output dir.
- **Auto-EDA outputs are inputs to investigation, not deliverables.** Read the report, extract 3–5 interesting signals, write them down, then drop the report and write custom code.
- **Save figures with their code.** Every PNG in `eda_output/figures/` should have a sibling `.py`.
- **Check Context7 before non-trivial library code.** These libraries iterate fast; training-data API memory is unreliable. See "Context7 lookup" below.

## Quick recipes (full versions in `references/library_recipes.md`)

### YData Profiling — first orientation

```python
from ydata_profiling import ProfileReport

profile = ProfileReport(
    df,
    title=f"{name} — Overview",
    minimal=True,           # REQUIRED for >50K rows
    explorative=False,      # explorative=True is slow, rarely worth it
)
profile.to_file("eda_output/auto_eda/ydata_overview.html")

# Programmatic extraction — this is the actual deliverable, not the HTML:
desc = profile.get_description()
alerts = desc.alerts          # highest-signal summary — log these
```

### Sweetviz — target-aware ranking

```python
import sweetviz as sv

report = sv.analyze(df, target_feat="target_col")
report.show_html("eda_output/auto_eda/sweetviz_target.html", open_browser=False)
```

Sweetviz orders features by association with the target. Pull the top 5–10 from the report, pick 2–4 for deeper investigation in custom code.

### Custom seaborn — the workhorse

For most probe views in iterations 2+, prefer custom seaborn over auto-EDA. It gives faceted, conditioned views — exactly what the investigative loop demands.

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Faceted by a confounder — the bread-and-butter probe
g = sns.catplot(
    data=df,
    x="tenure_bucket",
    y="churn",
    col="contract_type",
    kind="bar",
    estimator="mean",
    errorbar=("ci", 95),
    height=4, aspect=1.0,
)
g.savefig("eda_output/figures/iter3_tenure_x_contract.png", dpi=120, bbox_inches="tight")
```

### Plotly — when interactivity earns its keep

```python
import plotly.express as px

fig = px.box(df, x="contract_type", y="monthly_charges", color="churn",
             points="suspectedoutliers", hover_data=["tenure_months"])
fig.write_html("eda_output/figures/iter3_charges_by_contract.html")
```

Use plotly when: many categories to scan, hover-revealed detail matters, or the user will browse the figure interactively. Don't use it for figures that go in the final report — static PNGs render reliably; HTML doesn't.

## Context7 lookup pattern

Before writing more than ~20 lines against any of these libraries:

```
mcp__context7__resolve-library-id    library="ydata-profiling"
mcp__context7__get-library-docs      library_id=<from-resolve>
```

Catches drift like:
- `pandas-profiling` → `ydata-profiling` (full rename, 2023)
- YData's `ProfileReport.to_widgets()` removed in some 4.x versions
- Sweetviz `FeatureConfig` API changes
- Dataprep ownership / maintenance gaps

If Context7 isn't available, fall back to library docs via web fetch, but flag the assumption in the analysis.

## When to skip the auto-EDA libraries entirely

Auto-EDA earns its place for first-pass orientation. After iteration 2, custom code dominates. The auto-EDA libraries are also a poor fit for:

- **Time series** — they don't understand temporal structure. Use custom code or a TS-specific library.
- **Heavily nested or hierarchical data** — flatten first or use custom code.
- **Datasets > 1M rows** — most auto-EDA tools choke or take forever. Sample first or skip auto-EDA.
- **When you already know the question.** "Does X correlate with Y?" → just plot X vs Y. Don't run YData.

## Custom plotting cheat sheet

Decision tree for "what plot do I draw":

| You want to see... | Plot |
|---|---|
| Distribution of one continuous var | histogram + KDE, or ECDF for tail behavior |
| Distribution by group | boxplot or violin, ECDF if comparing tails |
| Two continuous vars | scatter (small n) or hex/2D-histogram (large n) |
| Continuous vs categorical | boxplot, stripplot, or bar of group means with CI |
| Two categoricals | heatmap of crosstab, or grouped bar |
| Categorical vs binary target | bar of mean target per category, ordered by effect |
| Effect of A on Y conditioned on B | faceted plot (`col=` or `row=` in seaborn) |
| Time trend with groups | line plot per group, or small multiples |
| Many features at once | small-multiple grid; do not use a 30-feature pairplot |

The single most-underused move: **faceted plots**. The investigative loop's "condition on the alternative" almost always becomes `col=alternative_var` in a seaborn `catplot` or `relplot`.

## Saving figures: convention

Every figure follows this pattern:

```
eda_output/figures/iter{N}_{slug}.png        # the figure
eda_output/figures/iter{N}_{slug}.py         # the code that produced it
```

Slug is short and describes the content (`tenure_x_contract`, `charges_by_segment`). The `.py` should be runnable standalone — it loads the data, produces the figure, saves the PNG. This is what makes figures **reproducible** and what lets a reviewer or follow-up agent regenerate or modify them.

## Full library reference

For complete code snippets, version notes, and gotchas per library, see `references/library_recipes.md`. Load that file when you need the full version of any of the patterns above.
