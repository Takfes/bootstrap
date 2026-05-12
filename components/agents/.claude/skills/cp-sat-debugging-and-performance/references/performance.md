# Performance Optimization for CP-SAT Scheduling

"Performance optimization" in CP-SAT is less about code-level micro-optimization and more about **assisting the solver in pruning the search space.** The solver is already highly tuned; what makes a slow model fast is usually a modeling change, not a parameter change.

The single most common performance anti-pattern is **blind parameter tuning** — adjusting solver parameters before the model is well-formulated. Default parameters in CP-SAT are well-chosen; tampering with them can disrupt the solver's internal optimizations and mask modeling errors. Parameter tuning is the last step, not the first.

## I. The Performance Triage Hierarchy

When a model is slow, work in this order. Higher tiers give larger and more reliable gains.

1. **Domain tightening and variable reduction.** The most significant gains come from reducing the search space *before* it reaches the SAT engine.
2. **Reformulation with global constraints.** Replacing manual logic with high-level globals lets the solver use specialized algorithms.
3. **Symmetry breaking.** Eliminating identical solutions that force the solver to explore the same tree multiple times.
4. **Redundant and implied constraints.** Adding constraints that don't change feasibility but improve propagation.
5. **Search hints.** Providing a warm start from a heuristic solution.
6. **Parameter tuning.** Adjusting solver internals as the last resort.

### Diagnosing the bottleneck

Before applying any move, enable `log_search_progress = True` and read the log to identify what kind of bottleneck you have. (See debugging reference for log structure.)

**Propagation bottleneck.** Very few conflicts per second, high CPU usage. The model has too many variables or expensive constraints (`AddMultiplicationEquality` and similar). Action: simplify constraints, tighten domains, or split heavy constraints.

**Search bottleneck.** Massive failure counts, objective gap not closing. The solver is exploring a poorly constrained or highly symmetric region. Action: symmetry breaking, redundant constraints, search hints.

**LP relaxation bottleneck.** The linearization subsolvers contribute most of the bounds but take a long time. Action: adjust `linearization_level` (lower it) or simplify the linear part of the model.

Apply the move that matches the bottleneck. Applying random performance tricks without diagnosing the bottleneck is the constraint-reflex applied to performance — adding work without addressing the cause.

---

## II. Symmetry Breaking

Symmetry occurs when variables or values can be swapped without changing feasibility or the objective. It's the silent killer of CP performance — the solver must explore each symmetric variant to prove none is better than the others.

### Common scheduling symmetries

- **Identical machines.** Three identical lathes — any schedule on Lathe 1 is functionally identical to the same schedule on Lathe 2.
- **Interchangeable tasks.** Five identical inspection tasks — their relative order may not matter.
- **Time-shift symmetries.** Sunday and Monday have identical requirements — they are symmetric in scheduling.

### Symmetry-breaking patterns

The canonical recipe is to impose an arbitrary ordering.

**Pattern: lexicographical ordering for identical machines.**

```python
# Force machine i to handle a task index lower than machine i+1
for i in range(num_machines - 1):
    model.add(first_task_on_machine[i] <= first_task_on_machine[i+1])
```

This prevents the solver from exploring "Machine 2 does Task A" if it has already explored "Machine 1 does Task A."

**Pattern: chronological ordering for identical tasks.**

```python
# Force tasks to start in index order
for i in range(n - 1):
    model.add(S[i] <= S[i+1])
```

The pattern is the same idea applied to time rather than to machines.

### When symmetry breaking backfires

Complete symmetry breaking can hurt. If a symmetry-breaking constraint conflicts with a powerful internal heuristic (a specific LNS strategy, a search hint), it can make good solutions harder to find — even if it makes proving optimality easier.

**The signal:** the solver finds a better solution faster *without* the symmetry-breaking constraint, but takes longer to prove optimality. The constraint is interfering with finding-heuristics.

**Partial vs complete.** It's often better to break symmetries partially — enough to remove the worst redundancy, not so much that the heuristics are blocked. Lexicographic ordering on the *first* task of each machine is partial; full ordering on every task is complete. Start partial.

---

## III. Redundant Constraints

A redundant constraint adds no logical information — every solution that satisfied the original model still satisfies it. What it adds is **propagation strength**: the solver sees a global view that it could in principle derive but doesn't, because deriving it would require many steps of inference.

### The capacity-vs-demand pattern

In scheduling, `AddNoOverlap` is excellent at local pruning ("tasks A and B can't overlap"). A redundant `AddCumulative` looks at total demand-energy over a time window. Combining them gives the solver both local and global views.

```python
# Already have:
model.add_no_overlap(intervals)

# Adding a redundant cumulative gives global energy view:
model.add_cumulative(intervals, [1] * len(intervals), num_machines)
```

### Makespan lower bound

When minimizing makespan, a redundant lower bound pushes the bound up — the solver doesn't waste time exploring makespans that can't possibly be achieved.

```python
# The makespan is at least the total work divided by parallel capacity
total_work = sum(task_durations)
model.add(makespan_var * num_machines >= total_work)
```

This is implied by the scheduling constraints but explicitly stating it dramatically accelerates lower-bound proof.

### Precedence redundancy

When precedence chains are long, the solver may take many inference steps to derive transitive bounds. Adding the transitive constraint directly accelerates propagation:

```python
# Given Start(A) + Dur(A) <= Start(B) and Start(B) + Dur(B) <= Start(C)
# Add the derived: Start(A) + Dur(A) + Dur(B) <= Start(C)
```

### The redundant-constraint trap

Not all redundant constraints help. A poorly chosen redundant constraint adds overhead (the solver must check and propagate it) without enough pruning benefit. Two warning signs:

- Adding the constraint increases solve time rather than decreasing it.
- The constraint encodes the same information the solver was already deriving — it propagates the same things, just adds work.

If a redundant constraint doesn't help, remove it. Performance work is empirical — measure before keeping.

---

## IV. Reformulation

Reformulation changes *how* a requirement is expressed to maximize the solver's filtering power.

### Global constraints over manual encoding

Manual boolean logic ($x \implies y$) over many variables is typically less effective than a single global constraint (`AddAllowedAssignments` for table constraints, `AddAllDifferent` for distinctness).

Global constraints have dedicated algorithms — matching for `AllDifferent`, edge-finding for scheduling — that prune values in polynomial time. Manual encoding forces the solver to derive the same conclusion through exponential search.

### Channeled representations (dual modeling)

Sometimes the same decision is naturally expressed in two ways:
- `x[task] = machine` (assignment view)
- `y[machine][time] = task` (timeline view)

Linking them with `AddInverse` or boolean channeling means a deduction in one view immediately prunes the other. Some constraints are easier to write in one view; some in the other. Maintaining both can accelerate propagation, at the cost of a slightly larger model.

Use sparingly — channeling adds variables and constraints. Only worth it when both views genuinely contribute pruning.

### Variable domain tightening

Reducing the initial domains of variables is one of the highest-leverage performance moves and the cheapest to apply.

- Are integer ranges as small as possible? (Don't use 0–1,000,000 if 0–1,000 suffices.)
- Can preprocessing analysis prove that certain values are infeasible?
- Are there dominance arguments that eliminate dominated assignments?

This work is often algebraic — derive tighter bounds from the problem structure, then encode them as the domain rather than as an explicit constraint.

---

## V. Search Hints and Warm Starts

`AddHint` is not a hard constraint; it's advice to the solver: "Try these values first."

### When hints earn their place

**Heuristic integration.** A fast greedy algorithm finds a decent schedule in milliseconds. Feeding it to CP-SAT as a hint gives the solver a valid incumbent immediately, so it spends 100% of its time on improvement and pruning rather than on finding a first feasible solution.

**Near-feasible solutions.** Even a slightly infeasible solution (one task overlaps) gives useful structure when hinted. The other 99% of values guide the solver to the right region; it then resolves the small infeasibility.

```python
# After running a heuristic
for task in tasks:
    model.add_hint(task.start_var, heuristic_start_time[task.id])
    model.add_hint(task.assigned_machine, heuristic_machine[task.id])
```

### The warning

A hint very far from the optimal region can slow the solver — it spends time trying to repair a bad hint instead of exploring better regions. If a hint doesn't help, measure and remove.

---

## VI. Parameter Tuning (Last Resort)

Adjust parameters only after model-level work is exhausted. The defaults are well-tuned for general use; changes should be motivated by specific evidence from the log, not by intuition.

### Key parameters

**`num_search_workers`.** The single most impactful parameter. Increasing it lets CP-SAT run more diverse subsolvers (LNS, LP-first, SAT-first) in parallel. Returns are sublinear but almost always positive when more cores are available.

**`linearization_level`.**
- Level 1 (default): prunes based on the LP relaxation.
- Level 2: adds more aggressive cuts. Useful for models with many linear constraints or that look like classical MIPs.
- Level 0: disable LP-based pruning. Worth trying when the LP relaxation is expensive and providing little — see the "no_lp worker outperforms default_lp" log signal in debugging.

**`max_time_in_seconds`.** Essential for production. Set based on diminishing-returns observed in the log — once the gap stops closing, additional time mostly returns marginal improvements.

**`cp_model_presolve`.** Default-on. Disabling presolve is occasionally useful to verify the original model is the source of an issue (the simplified model can hide bugs), but generally leave on.

### The trust-the-defaults nuance

The default search strategies are well-chosen. Manual variable ordering (`CHOOSE_FIRST`, `SELECT_MIN_VALUE`) often performs worse than the solver's internal learned branching, which is more adaptive.

Override decision strategies only when you have deep domain knowledge the solver cannot infer — e.g., a very specific priority for certain tasks that's known from the business but not from the model's structure.

If you do override, measure carefully. The change should produce visible improvement in the log; otherwise revert.

---

## VII. The Performance Sequence

When a model is slow, the practical sequence:

1. **Tighten domains.** Are integers as small as possible?
2. **Enable logging.** What does the log show — search problem (stuck upper bound) or proof problem (stuck lower bound)?
3. **Globalize.** Replace manual loops and `if`/`else` logic with `AddCumulative`, `AddNoOverlap`, `AddCircuit`, `AddAllDifferent` where applicable.
4. **Break symmetries** appropriate to the problem. Start partial, not complete.
5. **Add targeted redundant constraints** — makespan lower bound, cumulative on top of no-overlap, transitive precedence. Measure each.
6. **Provide hints** from a heuristic if the search struggles to find an initial feasible solution.
7. **Parallelize.** Increase `num_search_workers` to use available cores.
8. **Adjust other parameters** only with log evidence motivating the change.

---

## Discipline Points (Performance Phase)

The judgment moves that distinguish principled performance work from flailing:

- **Diagnose before applying moves.** The log tells you whether you have a search problem or a proof problem. The right move differs.
- **Don't tune parameters before fixing the model.** Default parameters are well-tuned; modeling improvements have larger gains.
- **Measure every change.** Performance work is empirical. A redundant constraint that "should help" but doesn't is overhead — remove it.
- **Don't optimize a model that's wrong.** If the model has a modeling error, performance work hides it. Verify correctness before optimization.
- **Don't declare done at the first solution.** Check the gap between best solution and best bound. A "feasible" return that's far from the bound may be leaving significant value on the table.
- **Don't blind-tune the solver.** Parameter changes without log evidence are guesses. Each change should be motivated by a specific signal.
