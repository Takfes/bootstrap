# Library recipes (full versions)

Detailed patterns per library, with gotchas and version notes. Load when the SKILL.md quick recipe isn't enough.

## YData Profiling

**Strengths:** Comprehensive single-report overview. Correlations, distributions, missingness, duplicates, alerts.
**Weaknesses:** Slow on >100K rows. Output overwhelming if pasted whole. Not target-aware.
**Use for:** Iteration 1 only — first orientation. After this, drop it.

```python
from ydata_profiling import ProfileReport

profile = ProfileReport(
    df,
    title=f"{dataset_name} — Overview",
    minimal=True,           # REQUIRED for >50K rows; otherwise expect minutes-to-hours
    explorative=False,      # rarely worth the runtime
    correlations={
        "auto":     {"calculate": True},
        "pearson":  {"calculate": True},
        "spearman": {"calculate": True},
        "phi_k":    {"calculate": False},  # slow, often redundant with auto
        "cramers":  {"calculate": False},
    },
    interactions={"continuous": False},   # disable; pairwise scatters explode runtime
)
profile.to_file("eda_output/auto_eda/ydata_overview.html")

# Programmatic extraction — this is the deliverable, not the HTML:
desc = profile.get_description()
alerts = desc.alerts                  # the highest-signal summary
# Log these as orientation observations, not findings.
```

**Gotchas:**
- `pandas-profiling` was renamed `ydata-profiling` in 2023. Old code/imports will fail.
- The `minimal=True` flag matters a lot — without it, the tool computes all interactions.
- `phi_k` and `cramers` correlations are slow. Disable unless you specifically want them.
- `to_widgets()` was removed in some 4.x versions; use `to_file()` or `to_html()`.

## Sweetviz

**Strengths:** Excellent target-vs-features visualization. Compare two datasets (train/test). Fast.
**Weaknesses:** Static HTML, no interactivity, less depth than YData on individual variable distributions.
**Use for:** Iteration 2 — once target is confirmed.

```python
import sweetviz as sv

# Categorical / binary target
report = sv.analyze(df, target_feat="target_col")
report.show_html("eda_output/auto_eda/sweetviz_target.html",
                 open_browser=False, layout="vertical")

# Train vs test comparison — useful for spotting drift / leakage candidates
report = sv.compare(
    [df_train, "Train"],
    [df_test,  "Test"],
    target_feat="target_col"
)
report.show_html("eda_output/auto_eda/sweetviz_compare.html", open_browser=False)
```

**Gotchas:**
- For continuous targets, Sweetviz works but the visualizations are less differentiating than for categorical/binary.
- Will fail or produce odd output if target column has NaNs — drop or impute target NaNs first.
- `FeatureConfig` API for marking columns as ID/skipped has shifted across versions; check Context7 if needed.

## AutoViz

**Strengths:** Auto-selects appropriate plot types per column pair. Fast.
**Weaknesses:** Quality varies, many output plots are noisy. Best for browsing, not for the final report.
**Use for:** Quick "what's in here" scan when you don't know what to look at — fallback only.

```python
from autoviz import AutoViz_Class

AV = AutoViz_Class()
df_av = AV.AutoViz(
    "",                              # filename (empty string when passing dfte directly)
    dfte=df,
    depVar="target_col",
    chart_format="png",
    save_plot_dir="eda_output/auto_eda/autoviz/",
    max_rows_analyzed=100_000,
    max_cols_analyzed=30,
    verbose=0,
)
```

**Gotchas:**
- `chart_format="png"` saves files; "html" or "bokeh" produces interactive output.
- Will pollute `save_plot_dir` with many files. Inspect, keep what's useful, prune the rest before committing.
- `AutoViz_Class()` instantiation is required — don't import a function.

## Dataprep

**Strengths:** Fast, targeted plotting. Composable. Good API for one-line investigations.
**Weaknesses:** Maintenance has been intermittent — pin versions if reproducibility matters.
**Use for:** Targeted views during iterations 2–3.

```python
from dataprep.eda import plot, plot_correlation, plot_missing

# Distribution + relationship to target in one call
plot(df, "feature_x", "target_col").save("eda_output/figures/iter2_x_vs_target.html")

# Correlation overview
plot_correlation(df).save("eda_output/figures/iter2_corr.html")

# Missingness patterns
plot_missing(df).save("eda_output/figures/iter1_missing.html")
```

**Gotchas:**
- HTML outputs require a browser to view; for the final report, prefer static plots from custom seaborn.
- Some users report install issues on newer Python versions; pin if needed.

## Dabl

**Strengths:** Smart automatic plot selection. Concise. Good defaults.
**Weaknesses:** Limited customization. Best for quick first looks, not deep dives.
**Use for:** Iteration 1 sanity check, or "show me one variable vs target in 2 lines."

```python
import dabl

dabl.plot(df, target_col="target_col")  # auto-selects useful plots, displays inline

# Type cleaning helper (separate concern):
df_clean = dabl.clean(df, type_hints={"id_col": "useless"})
```

**Gotchas:**
- `dabl.plot()` displays inline rather than returning a figure object, so saving programmatically is awkward. Use `plt.savefig()` after the call to capture the latest figure.
- Limited control over which plots are produced.

## Custom matplotlib / seaborn — the workhorse

For most probe views in iterations 2+, prefer custom code over auto-EDA. The patterns below cover the vast majority of investigative views.

### Faceted bar of mean target by category, conditioned on a confounder

The single most-used investigative probe.

```python
import seaborn as sns
import matplotlib.pyplot as plt

g = sns.catplot(
    data=df,
    x="tenure_bucket",
    y="churn",
    col="contract_type",       # the conditioning variable
    kind="bar",
    estimator="mean",
    errorbar=("ci", 95),
    height=4, aspect=1.0,
    order=["0-6","7-12","13-24","25+"],   # explicit ordering matters
)
g.set_axis_labels("Tenure bucket", "Churn rate")
g.set_titles("{col_name}")
g.savefig("eda_output/figures/iter3_tenure_x_contract.png", dpi=120, bbox_inches="tight")
plt.close()
```

### Distribution comparison via ECDF (better than histograms for tails)

```python
fig, ax = plt.subplots(figsize=(7, 4))
sns.ecdfplot(data=df, x="monthly_charges", hue="churn", ax=ax)
ax.set_title("Monthly charges distribution by churn outcome")
fig.savefig("eda_output/figures/iter2_charges_ecdf.png", dpi=120, bbox_inches="tight")
plt.close()
```

ECDFs are underused. They show distribution shape clearly, are robust to bin choice, and make tail differences obvious — much better than histograms when comparing groups.

### 2D histogram for large-n scatter

```python
fig, ax = plt.subplots(figsize=(7, 5))
hb = ax.hexbin(df["x"], df["y"], gridsize=40, cmap="viridis", mincnt=1)
fig.colorbar(hb, ax=ax, label="count")
ax.set_xlabel("x")
ax.set_ylabel("y")
fig.savefig("eda_output/figures/iter3_x_vs_y_hex.png", dpi=120, bbox_inches="tight")
plt.close()
```

For >5K rows, scatter plots become an undifferentiated cloud. Switch to hexbin or 2D-histogram.

### Group means with confidence intervals — clean and readable

```python
import numpy as np

g = sns.catplot(
    data=df,
    x="segment",
    y="metric",
    kind="point",
    estimator="mean",
    errorbar=("ci", 95),
    join=False,
    height=4, aspect=1.5,
)
g.set_axis_labels("Segment", "Mean metric")
g.savefig("eda_output/figures/iter4_segment_means.png", dpi=120, bbox_inches="tight")
plt.close()
```

Cleaner than bars when comparing many groups. The CIs make the eye-line skepticism work — if the CIs overlap heavily across groups, the apparent differences are noise.

## Plotly — interactive exploration

```python
import plotly.express as px

# Interactive box with hover detail
fig = px.box(
    df,
    x="contract_type",
    y="monthly_charges",
    color="churn",
    points="suspectedoutliers",
    hover_data=["customer_id", "tenure_months"],
)
fig.write_html("eda_output/figures/iter3_charges_by_contract.html")

# Interactive scatter with color gradient
fig = px.scatter(
    df.sample(min(5000, len(df))),       # sample if large
    x="tenure_months",
    y="monthly_charges",
    color="churn",
    hover_data=["contract_type", "internet_service"],
    opacity=0.5,
)
fig.write_html("eda_output/figures/iter4_tenure_vs_charges.html")
```

**When plotly earns its place:**
- Many categories where hover detail matters
- The user will browse interactively (not read a static report)
- Faceting becomes unwieldy with too many small-multiples

**When to avoid plotly:**
- Final report figures — HTML doesn't render reliably in markdown viewers
- Print/PDF output — static PNG is the only choice
- Quick checks during iteration — slower than seaborn for one-off plots

## Custom plotting decision tree (full version)

| Goal | Best plot | Library |
|---|---|---|
| Distribution of one continuous var | histogram + KDE, or ECDF | seaborn |
| Distribution by group, comparing tails | ECDF, one line per group | seaborn |
| Distribution by group, summary | boxplot or violin | seaborn |
| Two continuous, small n (<5K) | scatter | seaborn / matplotlib |
| Two continuous, large n | hexbin or 2D-histogram | matplotlib |
| Continuous vs categorical | boxplot or stripplot | seaborn |
| Categorical vs categorical | heatmap of crosstab | seaborn |
| Categorical vs binary target | bar of mean target, ordered by effect | seaborn |
| Effect of A on Y conditioned on B | catplot/relplot with `col=B` | seaborn |
| Time trend with groups | lineplot, one line per group | seaborn |
| Many features at once | small-multiple grid | seaborn FacetGrid |
| Interactive multi-feature | parallel coordinates or scatter matrix | plotly |
| Geographic | scatter on map | plotly |

## Saving figures — convention

Every figure has both a PNG and the script that produced it:

```
eda_output/figures/iter3_tenure_x_contract.png
eda_output/figures/iter3_tenure_x_contract.py
```

The `.py` should:
- Load the data from a fixed path
- Produce the figure
- Save the PNG
- Be runnable standalone with no edits

This makes figures **reproducible** — a reviewer or follow-up agent can regenerate any figure or modify it for a related question. It also catches data-snooping: if you can't write the script, you probably constructed the figure interactively in a way that won't replicate.
