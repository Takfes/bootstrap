---
name: cp-sat-debugging-and-performance
description: Use this skill when diagnosing or improving an existing Google OR-Tools CP-SAT scheduling model — debugging infeasibility, reading solver logs, fixing wrong-but-valid solutions, or making a slow model faster. This skill encodes the optimize-phase methodology: diagnostic procedures for unexpected behavior, log signal interpretation, the performance triage hierarchy (domain tightening, reformulation, symmetry breaking, redundant constraints, hints, parameter tuning). Triggers when the user reports their model is "infeasible", "slow", "stuck", "hangs", "doesn't improve", "returns wrong answer", "worked yesterday broken today", or when discussing solver logs, search progress, or parameter tuning. Use this skill proactively whenever the user signals the build phase is complete and the work has shifted to diagnostics or optimization.
---

# CP-SAT Debugging and Performance

The optimize-phase methodology for CP-SAT scheduling models. This skill is loaded when a model is already built and the work has shifted to diagnosing unexpected behavior or improving performance. For build-phase methodology (choosing primitives, designing objectives, modeling time and capacity), see the `cp-sat-modeling` skill.

## Prime directive

Diagnose before you act. The most common failure mode in this phase is the **constraint reflex** — adding a constraint to fix a symptom without understanding the cause. This produces brittle models that work on one instance and fail on the next. Every change in this phase should be motivated by a specific diagnostic signal (a log entry, an assumption-isolated conflict, a measured before/after performance comparison), not by intuition about what "should" help.

## When something is wrong — the triage

What kind of problem is it? The diagnostic move differs by symptom.

**Model returns `INFEASIBLE` unexpectedly** → infeasibility diagnosis.
**Model returns a valid but wrong solution** → wrong-solution diagnosis.
**Model is slow / search stalls / objective doesn't improve** → performance work.
**Model worked yesterday but doesn't today** → regression diagnosis (diffing).

Don't conflate these. The procedures are different.

## Infeasibility diagnosis

When the solver returns `INFEASIBLE` but the model should have a solution:

1. **Run `validate_model(model.proto)`.** Catches structural issues before search.
2. **Use `sufficient_assumptions_for_infeasibility`.** The gold-standard isolation move. Wrap suspect constraints with boolean indicators and let the solver return the minimal conflicting set.
3. **If assumptions don't isolate it**, use **manual relaxation / binary search** — comment out groups of constraints, restore until infeasibility returns, binary-search within.

Distinguish modeling errors (presolve-time infeasibility, fast return) from genuine infeasibility (takes time to prove, often complex interaction).

Full diagnostic patterns, including the hard-to-soft relaxation alternative and worked scenarios: `references/debugging.md`.

## Wrong-solution diagnosis

When the solver returns `OPTIMAL` or `FEASIBLE` but the solution doesn't match business intent — the most reliable move is to **hard-code the expected solution as constraints and re-solve**:

- Returns `INFEASIBLE` → there is a constraint that *forbids* the expected solution. Find which.
- Returns `OPTIMAL` → there is *no constraint* that prefers the expected over the wrong. You are missing a constraint.

This binary outcome localizes the issue precisely. Don't add "fix" constraints before running this diagnostic.

For full guidance including poor-quality-solution causes (objective scaling, soft constraint balance, search stalling): `references/debugging.md`.

## Reading the CP-SAT log

Enable `log_search_progress = True` and read the log as a diagnostic stream, not as a status report.

**Stuck upper bound** (best objective doesn't improve): **search problem**. Solver can't find a better feasible solution. Try LNS (more workers), solution hints, check for symmetric solutions.

**Stuck lower bound** (best bound doesn't improve): **proof problem**. Solver can't prove optimality. Add redundant constraints to strengthen the LP relaxation, check for big-M weakening the bounds.

**Exploding conflicts** (high conflict count, no improvement): **thrashing**. Often signals missing symmetry breaking or poor variable ordering.

**Long presolve / aggressive variable elimination**: verify the simplification matches expectations. Massive reduction can mean the problem was over-constrained and simplified into triviality.

Full log structure, worker information, and signal interpretation: `references/debugging.md`.

## Performance triage — the hierarchy of effort

When a model is slow, work in this order. Higher tiers give larger and more reliable gains.

1. **Domain tightening.** Are integers as small as possible? (E.g., 0–1,000 not 0–1,000,000.)
2. **Reformulation with global constraints.** Replace manual loops and `if`/`else` logic with `AddCumulative`, `AddNoOverlap`, `AddCircuit`, `AddAllDifferent` where applicable.
3. **Symmetry breaking** appropriate to the problem. Start partial, not complete.
4. **Redundant constraints** — makespan lower bounds, cumulative on top of no-overlap, transitive precedence. Measure each.
5. **Solution hints** if the search struggles to find an initial feasible solution.
6. **`num_search_workers`** — increase to use available cores. Largest parameter impact.
7. **Other parameters** — only with log evidence motivating the change.

Parameter tuning is the *last* step, not the first. Default parameters are well-chosen; tampering before fixing the model masks modeling errors and rarely produces large gains.

## Symmetry breaking — quick rules

- Common scheduling symmetries: identical machines, interchangeable tasks, time-shift symmetries.
- Canonical recipe: impose arbitrary ordering (lexicographic on first task per machine; chronological on identical tasks).
- Start partial, not complete. Complete symmetry breaking can conflict with internal heuristics.
- Signal that symmetry breaking is hurting: solver finds better solutions faster *without* the constraint but takes longer to prove optimality.

Full patterns and when symmetry breaking backfires: `references/performance.md`.

## Redundant constraints — quick rules

- Capacity-vs-demand: `AddCumulative` on top of `AddNoOverlap` for global energy view.
- Makespan lower bound from total work divided by parallelism.
- Transitive precedence when chains are long.
- **Trap:** a redundant constraint that doesn't help is overhead. Measure before keeping. Remove if it doesn't reduce solve time.

Full patterns and reformulation guidance (channeled representations, dual modeling): `references/performance.md`.

## Search hints — quick rules

- Feed a heuristic solution as a hint: the solver spends 100% of time on improvement, not on finding initial feasibility.
- Near-feasible hints (one task overlapping) are still useful — the rest guides the solver to the right region.
- A hint far from optimal can slow the solver. If a hint doesn't help, remove it.

Full guidance on parameter tuning, the trust-the-defaults nuance, and parallel workers: `references/performance.md`.

## Reproducibility and instrumentation

- **Export the model.** When an issue is reported, save the model proto (`model.proto`) for reproduction.
- **Log solver parameters.** Different worker counts, random seeds, time limits produce different solutions.
- **Use solution callbacks** to observe how solutions evolve during search.
- **For regressions** ("worked yesterday, broken today"): diff the prior and current model exports to localize the change.

Code patterns for these: `references/debugging.md` and the modeling skill's `references/code-patterns.md`.

## Anti-patterns (optimize phase)

- **The constraint reflex.** Adding a constraint to fix a symptom without diagnosing the cause. Produces brittle models.
- **Blind parameter tuning.** Adjusting solver parameters before the model is correct. Defaults are well-tuned; modeling improvements are larger gains.
- **Optimizing a model that's wrong.** Performance work hides modeling errors. Verify correctness before optimization.
- **Declaring done at the first solution.** Check the gap between best solution and best bound. A "feasible" return far from the bound may be leaving significant value on the table.
- **Treating the log as a status report.** It's a diagnostic stream. The discipline of reading it carefully is the difference between effective work and flailing.
- **Blaming the solver before assuming a modeling error.** "CP-SAT has a bug" is almost never the cause.

## When to load this skill alongside others

- For build-phase modeling questions or modifications: also load `cp-sat-modeling`.
- For non-trivial OR-Tools API code: consult Context7 for current API patterns.

## Working artifact

The subagent maintains `cp-notes-agent.md` with performance work logged: what was tried (which performance move from the triage), what helped, what didn't, with the before/after measurement. This is the working record of the optimize phase and prevents repeating performance moves that didn't help.
