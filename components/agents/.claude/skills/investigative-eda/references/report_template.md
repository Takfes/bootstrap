# Final report template (annotated)

The structure for `eda_output/final_report.md`. Comments in `<!-- -->` are guidance; remove them in the actual report.

```markdown
# EDA Report: Telco Customer Churn

<!-- TL;DR is the single most important section. The reader may read nothing else. -->
<!-- Lead with confirmed findings — direction and magnitude — not framing. -->
## TL;DR
- **Tenure under 6 months drives churn** at 47% vs 11% baseline. Effect concentrates in month-to-month customers (within annual contracts the tenure effect is muted).
- **Month-to-month contract is the second strongest signal.** 43% churn vs 7% on annual. Confounded with tenure (most new customers default to month-to-month) but carries independent effect after controlling.
- **Fiber + month-to-month combination** churns at 58% (n=412), suggesting a service-quality issue specific to that combination, not fiber alone.
- **No definitional leakage detected after check** — see methodology notes for the `total_charges` analysis.
- **3 plausible theories killed during investigation** — see "Theories that did not survive" below.

## Dataset overview
<!-- Keep terse. The auto-EDA HTML is there for detail. -->
- 7,043 rows × 21 columns
- Target: `churn` (binary, 26.5% positive — moderate imbalance)
- 17 categorical, 3 numeric, 1 ID column (dropped)
- Missing: `total_charges` 0.16% (11 rows, all new customers — imputed to 0; verified the imputation is not driving findings)
- Single snapshot, no time column

## Domain framing assumed
<!-- If you generated this from candidate framings, say so. -->
Subscription telecom, retention is the priority. A 3pp shift in churn rate is materially meaningful. Operating assumption: any finding actionable enough to inform a retention intervention is worth reporting; pure statistical curiosities are not.

## Confirmed findings

### F1: Tenure < 6 months drives churn, predominantly within month-to-month
- **Working theory:** New customers churn at multiples of base rate, but the effect concentrates in month-to-month contracts.
- **Evidence:**
  - Bucketed churn rates: 47% / 28% / 19% / 9% across [0–6, 7–12, 13–24, 25+] months. (`figs/iter2_tenure_buckets.png`)
  - Faceted by contract: within month-to-month, the tenure effect is sharp (51% → 13%); within annual contracts, tenure has minimal effect (8% → 6%). (`figs/iter3_tenure_x_contract.png`)
- **Alternatives considered and ruled out:**
  - *Confounding by contract:* survives the within-contract conditioning above.
  - *Survivor bias in long-tenure cohort:* checked dropout-rate-by-tenure separately; pattern holds.
- **Caveats:** New customers self-select into month-to-month; some of the "tenure effect" within month-to-month may itself be driven by customer type, not duration. Recommend follow-up with acquisition-channel data.
- **Magnitude:** ~4x relative risk for new month-to-month customers vs. baseline.

<!-- Repeat per finding. Keep each tight: theory, evidence, alternatives ruled out, caveats, magnitude. -->

## Theories that did not survive
<!-- High-signal section. Don't skip. The reader is silently asking "did they test the obvious thing?" -->

- **"Senior citizens churn more"** — The 24% senior vs 26% non-senior gap is within sampling noise. Killed.
- **"Higher monthly charges → higher churn"** — Looked promising in iter 2 (`figs/iter2_charges_vs_churn.png`). Killed in iter 4 after segment check: the effect is fully mediated by service mix (high-charge customers tend to be fiber + multiple services). Within service-mix segments, charges have no independent effect.
- **"Streaming services predict churn"** — Looked like a 5pp effect. Killed after controlling for tenure: streaming customers are systematically newer, and tenure is the real driver.

## Open threads
<!-- Threads that were promising but not pursued — for whoever continues this work. -->

- The fiber + month-to-month interaction (F3) suggests a service-quality issue specific to that combination. Pulling support-ticket data for that segment would distinguish "billing-driven churn" from "service-quality churn."
- The "auto-pay" effect was investigated and looked real (independent of contract type, see F4) but the mechanism is unclear — sticky habit vs. selection by engaged customers. Behavioral data on payment-method-change events would clarify.
- No geographic data — regional variation in fiber complaints is plausible based on F3 but unverifiable.

## Methodology notes

- **Iterations run:** 4 (stopped at 4 — iteration 4 produced no new theory worth pursuing).
- **Tools:** ydata-profiling for orientation (iter 1), sweetviz for target-vs-feature ranking (iter 2), custom seaborn for all probe views (iter 2–4).
- **Leakage check performed:** `total_charges` is mechanically `monthly_charges × tenure`. Verified by re-running F1 with `total_charges` removed; rankings unchanged. `total_charges` was not used as a primary predictor.
- **Imputation check:** Re-ran F1 excluding the 11 imputed rows; no change.
- **Outlier check:** Trimmed top/bottom 1% of `monthly_charges`; F1 and F2 robust, F3 effect size attenuated by ~5pp but direction held.
- **Segment-size discipline:** All reported segment claims have n ≥ 100. F3's n=412 is in the report; one promising lead at n=23 was excluded as anecdote.
- **Domain assumption:** Telecom retention context per intro; if this is being repurposed for a different problem (e.g., predictive modeling pipeline), some of the "actionability" filtering may have suppressed signal that would matter for that use case.
```

## Notes on writing this report

- **Lead with findings, not preamble.** The TL;DR is for an executive who reads only that section.
- **Effect magnitude over p-values.** "Confirmed" means the theory survived the alternatives check and the leakage check, not "p < 0.05". A statistically significant effect of 0.5pp on a 26% baseline is rarely actionable.
- **Killed theories belong in the report.** They tell the reader you considered the alternatives. Leaving them out makes the report look shallow even if the work was thorough.
- **Caveats are protection, not weakness.** The reader who acts on a finding without knowing its caveats is the one who'll come back angry. Be specific about what would change the conclusion.
- **Open threads are a gift to whoever continues.** A few sentences about what you'd investigate next is often more useful than a longer "future work" section in academic style.
