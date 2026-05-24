# Investigation patterns: worked examples

Loaded only when the agent needs concrete examples of the playbook moves. The main SKILL.md describes the discipline; this file shows what it looks like in practice.

## Competing-explanations: worked examples

### Example 1: Confounding

**Pattern observed:** Customers with fiber internet churn at 42% vs 19% for DSL.

**Naive theory:** Fiber service has quality problems that drive churn.

**Alternatives generated:**
1. *Confounding by contract type* — fiber customers may disproportionately be on month-to-month contracts (more flexibility expectation), and contract type is the real driver.
2. *Confounding by tenure* — fiber is the newer product, so fiber customers are systematically newer, and tenure is the real driver.
3. *Real causal story* — fiber actually has quality issues.

**Probe:** Faceted churn rate by `internet_service × contract_type`, also faceted by `tenure_bucket`.

**Possible outcomes:**
- Within each contract type, fiber still churns more → contract is not the full story.
- Within each tenure bucket, fiber still churns more → tenure is not the full story.
- Effect disappears after both controls → both confounders together explained it; not a fiber-quality story.
- Effect survives both controls → genuinely something about the fiber product. Worth deeper investigation.

The point: you don't know which it is until you draw the conditioned view. Forming the alternatives forced the right probe.

### Example 2: Mediation

**Pattern observed:** Customers with auto-pay enabled have 8% churn vs 31% without.

**Naive theory:** Auto-pay creates stickiness — once enabled, customers don't actively re-decide each month.

**Alternatives:**
1. *Mediation by contract type* — auto-pay is far more common on annual contracts, and the contract is what's locking customers in. Auto-pay is incidental.
2. *Mediation by customer engagement* — engaged customers both enable auto-pay and don't churn. Auto-pay is a marker, not a cause.
3. *Real causal story* — auto-pay has independent effect.

**Probe:** Within each contract type, what's the auto-pay effect?

**Distinguishing outcomes:**
- Within month-to-month customers (where commitment is low), auto-pay still cuts churn substantially → independent effect, the stickiness theory survives.
- Auto-pay effect collapses within contract type → it's a marker for contract choice.

### Example 3: Selection / sampling artifact

**Pattern observed:** Customers in the dataset with phone-only service have 0% churn.

**Naive theory:** Phone-only is the most retained product.

**Alternatives:**
1. *Sampling artifact* — the dataset is recent customers; phone-only is a legacy product that's no longer offered to new customers, so existing phone-only customers are by definition long-tenured survivors.
2. *Definitional* — "churn" might be coded differently for phone-only.
3. *Real story.*

**Probe:** Tenure distribution of phone-only customers vs. others.

If phone-only customers all have tenure > 5 years and no one with shorter tenure is in that segment, the segment is **survivor-biased** and the 0% churn rate is meaningless for any forward-looking question.

### Example 4: Leakage / definitional

**Pattern observed:** `total_charges` is the strongest predictor of churn, with a steep inverse relationship.

**Naive theory:** Higher-value customers are more retained.

**Alternatives — definitional dominates:**
1. `total_charges = monthly_charges × tenure`. Tenure is mechanically lower for churners (because churning ends accumulation). The relationship is partly a definitional artifact.

**Probe:** Compute `monthly_charges` (the rate, not the cumulative) churn relationship. Compute tenure churn relationship. See if `total_charges` carries any information beyond what those two carry jointly.

This one is almost always at least partly definitional. Reporting it as a "finding" without the check is a serious error.

### Example 5: Outlier-driven

**Pattern observed:** Customers with `monthly_charges > $90` churn at 51%, vs 23% baseline.

**Naive theory:** Premium-tier pricing drives churn.

**Alternatives:**
1. *Outlier-driven* — five customers with charges in the $200+ range have all churned, dragging up the rate for the whole bucket.
2. *Threshold real* — there's a real cliff effect above some price point.
3. *Confounded by service mix* — high-charge customers have multiple services bundled, and it's the bundle complexity that's driving churn.

**Probe:** Re-bucket more finely (e.g. $90–100, $100–110, etc.). Look at the within-bucket churn rate and bucket sizes.

If the rate is monotonic and gradual across buckets, it's a real gradient. If it's flat-then-spike-in-the-tail with tiny tail bucket, it's outlier-driven.

### Example 6: Threshold / non-linear

**Pattern observed:** Tenure has a weak negative correlation with churn (Pearson r ≈ -0.18).

**Naive theory:** Tenure doesn't matter much.

**Alternative — non-linearity:**
1. The relationship is sharply non-linear: churn is high for tenure < 6 months, then drops off and is flat for the rest of the range. A correlation coefficient assuming linearity will dramatically understate this.

**Probe:** Bucketed view. Plot churn rate by tenure decile or by month-bucket.

This is one of the most common cases where naive correlation hides a real pattern.

## Leakage check: worked examples

### Definitional leakage

`total_charges` and `tenure` when target is `churn`. As above. Always check.

Less obvious: a "satisfaction_score" measured at the point of churn. Or "support_tickets_lifetime" which keeps accumulating only for retained customers.

**Detection:** Ask "could I, in principle, have computed this feature *before* the target outcome was determined?"

### Temporal leakage

In a churn dataset: "customer's last call to support was about cancellation." Yes, that predicts churn perfectly. No, you can't use it.

**Detection:** For each strong predictor, ask "what's the timestamp of this measurement vs. the timestamp of the outcome?"

### Imputation artifact

`total_charges` has 11 missing rows, all imputed to 0. The relationship between `total_charges` and `churn` may now have a spike at 0 that is entirely an artifact of those 11 rows being new customers with not-yet-billed status.

**Detection:** Re-run the key analysis only on rows where the predictor was not imputed. If the effect survives there, it's real. If it collapses, it was the imputation.

### Outlier domination

A handful of extreme rows can dominate any aggregate. Always re-run with top/bottom 1% (or top 5% for very heavy tails) trimmed and confirm.

### Segment domination

A "population effect" that's actually one segment doing all the work. Compute the effect within each major segment. If 80%+ comes from one segment, the finding is segment-specific.

## Segment-size in practice

| Total dataset size | "Pursue" floor | "Caution" floor |
|---|---|---|
| > 10,000 rows     | 50  | 20  |
| 1,000–10,000      | 30  | 15  |
| 200–1,000         | 20  | 10  |
| < 200             | 10  | 5   |

These are *minimum cell counts* for a segment-level claim, not relative percentages. A 0.5% segment of a million-row dataset is fine (5,000 rows). A 10% segment of a 100-row dataset is anecdote (10 rows).

When reporting a segment claim, **always include the n**:
> "Within the high-charge fiber-optic segment (n=143), churn was 58% vs. 26% baseline."

Without the n, the reader cannot calibrate whether to trust the claim.

## When to break these rules

The patterns above are guidance, not law. Cases where deviation is justified:

- **Tiny dataset, large effect.** A 50-row dataset with a 90% effect concentrated in a 12-row segment may still be reportable as "tentative — would need more data." Just label it.
- **Domain context demands it.** Rare-event analysis (fraud, medical adverse events) often *requires* small-segment claims because the segment is the point. Lower the n threshold but raise the caveat.
- **The pattern is robust to multiple cuts.** A 30-row segment that shows the same pattern across three different definitions of the segment is more credible than a 50-row segment that only works under one definition.

In all such cases: report the deviation explicitly. Don't paper over it.
