# Debugging CP-SAT Scheduling Models

Debugging CP-SAT requires shifting from imperative debugging to a logic-centric diagnostic procedure. When a model behaves unexpectedly — `INFEASIBLE` when it shouldn't be, a wrong solution that looks valid, a search that plateaus — the solver's log and specific API diagnostic moves are the primary tools.

The most common failure mode in debugging is the **constraint reflex** — reaching for a new constraint to "fix" the symptom instead of finding the root cause. This produces brittle models that work on one instance and fail on the next. The discipline is to understand *why* the model produced the unexpected behavior before adding any constraint.

## I. Diagnosing Infeasibility

When the solver returns `INFEASIBLE`, the question is: which constraints are in conflict?

### Recommended procedure

1. **Model validation.** Run `validate_model(model.proto)`. This catches structural problems — variable domains out of supported range, malformed constraints — *before* the search begins.
2. **Assumption-based isolation.** Use the "sufficient assumptions" technique below. This is the gold-standard diagnostic move.
3. **Manual relaxation / binary search.** If assumptions don't isolate the conflict, comment out groups of constraints, restore until infeasibility returns, then binary-search within the restored group.

### Using `sufficient_assumptions_for_infeasibility`

Wrap "suspicious" constraints in boolean variables and pass them as assumptions. The solver returns a **minimal** subset of these literals that are mutually inconsistent.

```python
# Instead of: model.add(x + y <= 10)
# Use an indicator:
is_constraint_active = model.new_bool_var('capacity_constraint')
model.add(x + y <= 10).only_enforce_if(is_constraint_active)

# Mark the constraint as an assumption
model.add_assumption(is_constraint_active)
status = solver.solve(model)

if status == cp_model.INFEASIBLE:
    conflict = solver.sufficient_assumptions_for_infeasibility()
    print(f"Minimal conflict: {conflict}")
```

The returned subset identifies exactly which requirements are in conflict. In a nurse rostering model, this might surface as "'Nurse A must have Sunday off' conflicts with 'The clinic requires 5 nurses on Sunday.'"

The technique works best when you wrap *suspect* constraints — domain limits, business rules, capacity constraints. Wrapping every constraint dilutes the signal.

### Hard-to-soft relaxation (alternative diagnostic)

For infeasibility that doesn't isolate cleanly with assumptions, convert one or more hard constraints to soft constraints with high penalties (see modeling skill, objectives reference). The solver will then return a solution showing exactly which constraints had to be violated and by how much. The pattern of violations reveals the conflict.

### Distinguishing modeling errors from genuine infeasibility

**Modeling error.** Typically manifests as presolve-time infeasibility — the log shows `INFEASIBLE` in 0.00s, often with a domain reduced to empty during presolve. The cause is usually a contradiction visible from a small set of constraints (often two or three).

**Genuine infeasibility.** Takes time to prove. The log shows conflicts rising as the solver explores the search space. If `INFEASIBLE` takes seconds or minutes to return, it's a complex interaction of many global constraints — the actual problem has no feasible solution under the stated constraints.

The diagnostic move differs:
- Presolve infeasibility → check the constraints involved in the empty-domain reduction (the log usually names them).
- Search-time infeasibility → the conflict is in the interaction; assumptions or hard-to-soft relaxation is needed to isolate.

---

## II. Reading the CP-SAT Log

The log is not a status report; it is a diagnostic stream that reveals the model's "physics."

### Log structure

A standard log contains:

- **Model summary** — variables, constraints, coefficient statistics.
- **Presolve phase** — simplifications applied to the model before search.
- **Search progress table** — real-time objective values, best bound, gap.
- **Statistics summary** — final tallies of conflicts, branches, worker performance.

### Presolve signals

**Aggressive variable elimination (80%+ of variables removed).** Generally good for performance, but can mask the source of modeling errors. If presolve removes most of the model, verify that the remaining variables and constraints match expectations — a massive reduction might mean the problem was over-constrained and simplified into triviality.

**Long presolve time (more than a few seconds on small models).** Suggests the solver is struggling to find affine relations, or that the model has many small independent constraints that should be expressed as a single global constraint. Replace manual decompositions with globals (`AddAllDifferent` instead of $N^2$ "not equal" constraints).

### Search progress signals

The progress table shows two crucial numbers:
- **Best objective** — the best feasible solution found so far (the upper bound in minimization).
- **Best bound** — the theoretical lower limit the solver can prove (lower bound in minimization).

The gap between them is the proof of optimality.

**Stuck upper bound** (best objective doesn't improve). The solver cannot find a better feasible solution. This is a **search problem**.
- Try LNS (increase `num_search_workers` to enable more LNS workers).
- Provide a solution hint as a warm start.
- Check for symmetric solutions that may be trapping the search.

**Stuck lower bound** (best bound doesn't improve). The solver cannot prove the current solution is optimal. This is a **proof problem**.
- Add redundant constraints to strengthen the LP relaxation.
- Check whether big-M formulations are weakening the bounds.
- Sometimes the optimal solution *is* the current one — verify with assumptions before assuming proof problem.

**Exploding conflicts** (high conflict count without objective improvement). The solver is thrashing — making decisions that lead to immediate failures. Often signals missing **symmetry breaking** or poor variable ordering. (See performance reference.)

### Worker information

CP-SAT runs a portfolio of workers (`default_lp`, `max_lp`, `pseudo_costs`, `rins_lns`, etc.) in parallel, each with different search strategies. The log shows which workers find solutions.

**Signal:** if `rins_lns` is the only worker finding solutions, the problem is heavy-optimization-dominant — local search is the only effective path. Consider whether the natural objective propagates poorly and a surrogate would help.

**Signal:** if a `no_lp` worker finds a solution that a `default_lp` worker cannot, the LP relaxation is actually *slowing* the search — too expensive relative to the pruning it provides. May indicate the linearization should be lowered or removed for this problem.

---

## III. Debugging Unexpected Solutions

A "feasible but wrong" solution is more dangerous than `INFEASIBLE`. The solver returns `OPTIMAL` or `FEASIBLE`, but the solution doesn't match business intent.

### The wrong-solution diagnostic

The standard pattern: **hard-code the expected solution into the model as constraints, then re-solve.**

- If the solver returns `INFEASIBLE`: there is a constraint in the model that *forbids* the expected solution. You added a constraint you misunderstood. Find it.
- If the solver returns `OPTIMAL` (or `FEASIBLE`): there is *no constraint* in the model that prefers the expected solution over the wrong one. You are missing a constraint that would prohibit the wrong solution.

This is the most reliable move when the symptom is "the solver returned a valid but wrong answer." It converts a vague concern into a binary question with a precise diagnostic.

### Worked scenario: overlap in nurse scheduling

A nurse is assigned to two overlapping shifts. The fix involves checking `IntervalVar` definitions used in `AddNoOverlap` — typically an off-by-one in time-window boundaries, or shifts using different time bases that the no-overlap constraint cannot see as overlapping.

The diagnostic move (hard-code the expected non-overlap and re-solve) localizes which `IntervalVar` definition is wrong.

### Poor solution quality

If the solver returns a "valid but terrible" solution:

1. **Check objective scaling.** If objective weights are too small (e.g., 1 in a model where other quantities are 1,000,000), the solver may ignore them due to internal scaling. See objectives reference.
2. **Check soft constraint balance.** If a critical violation costs less than many trivial improvements combined, the solver will trade the critical violation for trivia. This is the "objective dominance" symptom in the objectives reference.
3. **Check the search log for stalling.** A terrible solution that the solver hasn't improved on may mean the search is stuck (search problem), not that a better solution doesn't exist.

---

## IV. Reproducibility and Instrumentation

The discipline of debugging includes making problems reproducible.

### Model and solution export

```python
# Save the model in protobuf text format
with open('debug_model.pb.txt', 'w') as f:
    f.write(str(model.proto))
```

The exported model can be loaded into the `solve` command-line tool or shared for analysis. Always export the model when an issue is reported — without the exact model, debugging is guesswork.

### Always log solver parameters

A different number of threads, a different random seed, or a different time limit can produce different solutions and different search paths. Log the exact parameters used:

```python
print(f"Workers: {solver.parameters.num_search_workers}, "
      f"Time: {solver.parameters.max_time_in_seconds}s, "
      f"Seed: {solver.parameters.random_seed}")
```

When a bug is reproducible only under specific parameters, that's diagnostic information.

### Solution callbacks for debugging

While often used for monitoring, callbacks are powerful debuggers. Print specific variables every time a new solution is found to see how solutions evolve. If the variables that should change between successive solutions aren't changing, the objective isn't steering the search correctly.

### "Worked yesterday, broken today"

The diffing strategy for regressions:

1. Export the prior model (the one that worked) to text format.
2. Export the current model (the one that's broken).
3. Use a standard `diff` tool on the two text files.
4. The diff localizes exactly which constraint or variable bound changed.

A common cause of "worked yesterday" regressions: refactoring that accidentally introduced shared variables where there should be unique ones (copy-paste error in scheduling loops). The diff catches this immediately.

---

## V. Discipline Points (Debugging Phase)

The judgment moves that distinguish careful debugging from constraint-reflexive flailing:

- **Don't add a constraint to fix a symptom you don't understand.** Use the log, assumptions, and the hard-coded-expected-solution diagnostic to find the cause first.
- **Don't blame the solver before assuming a modeling error.** "CP-SAT has a bug" is almost never the cause. The modeling error usually is.
- **Always export the model when an issue is reported.** Without the exact reproducer, debugging is guessing.
- **Treat the search log as a mentor, not a status report.** It tells you where time is going, which workers are productive, where the search is stuck. The discipline of reading the log carefully is the difference between effective debugging and blind parameter tuning.
- **Verify the number of variables and constraints after presolve match your expectations.** A massive reduction may mean the problem simplified into triviality — not a bug, but worth checking before declaring success.
