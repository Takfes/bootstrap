# Objective Design and Soft Constraints

The objective function is the primary driver of search behavior in CP-SAT. Soft constraints — rules that should be followed but may be violated at a cost — are not native primitives; they are constructed using reification. Getting the objective and soft-constraint design right is often the difference between a model that finds useful solutions and one that finds technically-valid-but-useless ones.

## Common Scheduling Objectives

### Makespan ($C_{max}$)

The completion time of the last task. Implemented as `model.add_max_equality(makespan_var, [end_times])`.

**Solver behavior:** notorious for weak propagation. Because makespan depends only on the single latest task, the solver can spend significant time moving non-critical tasks that don't change the objective. The search landscape is "flat" — many distinct solutions look equally good to the solver.

**Pitfall:** in flexible models, using makespan alone often produces many equivalent solutions differing only in placement of non-critical tasks. The solver may also struggle to prove optimality because the lower bound is weak.

### Total Tardiness / Total Lateness

Sum of delays past due dates. For each task: `delay_i = max(0, end_i - due_date_i)`, then minimize `sum(delay_i)`.

**Solver behavior:** typically propagates better than makespan because reducing any late task's delay improves the objective. The objective gives a gradient across the entire task set, providing more pruning signals than makespan's single-point dependence.

### Weighted Completion Time

Sum of (weight × completion time) over tasks. Used for throughput and turnaround-time problems.

**Pitfall:** in multi-stage problems (job-shops), minimizing total completion time can encourage "front-loading" — the solver pushes easy tasks early, potentially starving later resource-intensive tasks. Worth checking whether the resulting schedule matches business intent.

### Resource Leveling (Peak Shaving)

Minimize the maximum resource usage at any point in time. Implementation typically involves `FixedSizeIntervalVar` with a `Cumulative` constraint where the capacity becomes the variable being minimized.

**Cost:** computationally expensive — interacts heavily with the cumulative propagator. Use when peak demand is the actual business constraint, not as a default.

### Choosing the right objective

The objective should reflect business goal, but propagation strength is a real consideration. If the natural objective propagates poorly (makespan in a flexible model), there are two options:

1. Accept the cost and use makespan, possibly with redundant constraints to strengthen the lower bound.
2. Use a **surrogate** that correlates with the business goal but propagates better — total weighted tardiness, total squared tardiness, total completion time. If the surrogate is good enough, the solver works substantially faster.

The discipline: don't pick a "bad" objective for performance reasons without confirming that the surrogate produces solutions the business actually wants.

---

## Multi-Objective Handling

CP-SAT natively supports a single linear objective. Multiple goals require deliberate combination.

### Weighted Sum

The default workhorse. `objective = sum(weight_i * term_i)`.

Default starting heuristic: choose weights separated by at least one order of magnitude. This prevents an objective with naturally large numbers from drowning out one with small numbers.

When weighted sum fails: when the priorities are truly categorical rather than tradeable. If a one-unit violation of constraint A is *infinitely worse* than any amount of B, weighted sums won't capture that — the relative weight must be impossibly large.

### Lexicographic (Hierarchical) Optimization

Used when objective A is strictly more important than B — any improvement in A justifies any worsening in B.

**Method A (single solve, big-M scaling):** multiply the primary objective by a constant larger than the maximum possible value of the secondary objective. Combines them into one linear objective the solver minimizes.

**Method B (iterative solve, preferred):**
1. Solve for the primary objective.
2. Fix or constrain its value: `model.add(obj_primary == best_value_or_better)`.
3. Re-solve for the secondary objective.

Method B avoids numerical scaling issues. It's clearer about intent — the constraint that the primary objective stay at its best value is explicit. The downside is multiple solves, but for problems where the tier structure is genuinely categorical, the cost is worth the correctness.

### Epsilon-Constraint

Fix all-but-one objectives as constraints with budget values; minimize the remaining one. Used to explore the Pareto frontier — sweep the budget and observe how the free objective changes. Mostly an analysis technique, less common in production solving.

### Handling Many Soft Constraints (5+)

When a problem has many soft constraints, weighted sums often produce noisy objective landscapes that hurt search. Two patterns:

- **Tier into hard categories.** Group constraints by importance: Critical, Important, Preferred. Use lexicographic optimization across tiers; within each tier, weighted sum with consciously chosen weights.
- **Normalize before weighting.** Map each soft constraint's penalty to a common scale (e.g., 0–10,000 representing relative business impact) before applying weights. This catches the trap of "intuitive weights" — `10, 100, 1000` looks principled but doesn't necessarily reflect actual importance.

---

## Objective Scaling and Numerical Conditioning

CP-SAT is integer-only. Floats must be scaled to integers.

### Avoiding floats

Multiply the entire objective by a power of 10 (e.g., 100 or 1000) and round to integers. The conventional scaling factor for two decimal places is 100; for three, 1000.

### Coefficient magnitudes

Keep the *sum* of objective term magnitudes well within 64-bit integer arithmetic. Concretely: the total of all coefficient × maximum-value contributions should stay below $2^{53} - 1$ to keep exact integer arithmetic across all sub-solvers, including the LP relaxation.

Extreme differences (1 vs 1,000,000,000) cause numerical instability in the LP relaxation and may degrade pruning even when arithmetic remains exact. If you need that range, use lexicographic optimization rather than enormous coefficients.

### Precision vs performance

Scaling up increases the cost of every search step (larger integers, tighter domains). Scale only as much as you need to preserve meaningful differences. If business decisions don't depend on the third decimal, don't scale to keep three decimals.

---

## Soft Constraints — Mechanics

Three primary patterns for implementing soft constraints. Pick based on the nature of the violation.

### Reification with Penalty (Boolean Indicator)

For "if-then" constraints with binary "satisfied or not" outcomes.

```python
# Constraint: task should start before time 100 (soft)
violated = model.new_bool_var('violated_deadline')
model.add(start_var > 100).only_enforce_if(violated)
model.add(start_var <= 100).only_enforce_if(violated.Not())

model.minimize(violated * PENALTY_WEIGHT)
```

### Slack Variables (Distance Costs)

When the penalty scales with the degree of violation — "five minutes late is much worse than one minute late."

```python
# Preferred start is 50; penalty is 5 per unit of delay
slack = model.new_int_var(0, max_time, 'slack')
model.add(slack >= start_var - 50)
model.minimize(slack * 5)
```

### Indicator Booleans for Discrete Tiers

When the penalty is non-linear — "0–10 mins late is a small cost, more than 10 is a major cost."

```python
late_a_little = model.new_bool_var('late_a_little')  # 1-10 mins
late_a_lot = model.new_bool_var('late_a_lot')        # 10+ mins

# Define the threshold conditions for each indicator
# ... (channeling start_var to the indicators)

model.minimize(50 * late_a_little + 500 * late_a_lot)
```

---

## Penalty Calibration

Setting weights is one of the hardest parts of model tuning.

### The Telltale Rule

The first diagnostic for whether a penalty is well-calibrated:

- If the soft constraint is **always violated** in optimal solutions, the penalty is too low — the solver is choosing the violation over the objective gain.
- If the soft constraint is **never violated** even when it seems like the cost of satisfying it should be prohibitive, the penalty has effectively become a hard constraint and may be blocking globally better solutions.

When you see either pattern, the calibration is wrong, not the model.

### Relative Magnitudes

To enforce a preference order between two soft constraints (A more important than B), the penalty for one A violation must exceed the *maximum possible total penalty* of all B violations combined. Otherwise, the solver will trade an A violation for many B improvements.

This is harder than it sounds: in problems with hundreds of B-instances, the total B-penalty can be very large. If preference order matters categorically, use lexicographic optimization rather than trying to outscale.

### The Trap of Arbitrary Weights

Common failure: using "nice" numbers (10, 100, 1000) without computing the actual relative impact. The numbers feel principled but don't reflect business importance.

The corrective: **normalize to a common scale.** Map each penalty to a 0–10,000 range based on its actual business impact, then apply weights. The mapping itself is the discipline — it forces explicit reasoning about how much each constraint matters.

### Iterative Tuning

In practice, calibration is iterative:
1. Set initial weights based on order-of-magnitude intuition.
2. Solve.
3. Check the telltale rule for each soft constraint.
4. Adjust weights for any that are always or never violated.
5. Repeat until the violation patterns match business intent.

Keep notes on weight changes and their effects — without notes, this devolves into random adjustment.

---

## Failure Modes and Diagnostic Patterns

### Common mistakes

**Over-constraining (the infeasible wall).** Treating every business rule as a hard constraint. Industrial scheduling problems are almost always over-constrained in practice. A hard constraint is a commitment that no solution at all is better than a solution that violates it. When that's not the actual business position, the constraint should be soft.

**Soft constraints that pollute search.** Adding hundreds of individual preferences creates a noisy objective landscape where every small move changes the objective slightly. This can defeat the solver's Large Neighborhood Search workers, which rely on the objective to provide useful gradients.

### Symptoms of bad weighting

**Jittering.** The solver finds a solution, then spends hours making improvements that change the objective by 1 unit at a time. Suggests penalties are scaled too small relative to the main goal; the solver is exploring trivial improvements rather than meaningful ones.

**Objective dominance.** The solver ignores the main goal to satisfy a small soft constraint. Happens when the cumulative penalty of many small violations outweighs the primary objective.

### Hard-to-soft relaxation (diagnostic move)

When a model is unexpectedly infeasible, the standard move is to convert hard constraints into soft constraints with high penalties:

1. Identify the suspected conflicting constraints.
2. Replace `model.add(x == y)` with the reified version: a boolean `violated`, the constraint enforced on `Not(violated)`, the penalty added to a diagnostic objective.
3. Solve.
4. The result shows exactly which constraints were violated and by how much — making the conflict explicit.

The pattern reveals whether infeasibility is a single sharp conflict (one constraint must be relaxed) or a systemic one (many constraints all need relaxation). Use this whenever an `INFEASIBLE` return is unexpected.

---

## Incentives vs Penalties

For most scheduling problems, **penalties (minimization) are preferred over incentives (maximization).**

Reason: minimization bounds work better with the solver's pruning logic. In maximization, the initial bound is +∞ — uninformative. In minimization, the bound starts at 0 (a known floor) and the solver can prune any branch that exceeds the current best. The gradient direction matters for how quickly the solver can shrink the search space.

Concrete reframing: instead of "reward +10 for each nurse getting their preferred day off," use "penalty -10 for each nurse denied their preferred day off." Same business meaning; better solver behavior.

---

## Time-Dependent Penalties

When the cost of an event depends on *when* it happens (late delivery at 5 PM is worse than at 2 PM), the standard pattern is `AddElement` to map a time variable to a cost array.

```python
# cost_per_hour[h] = penalty for the event occurring in hour h
time_index = model.new_int_var(0, 23, 'time_index')
model.add(time_index == end_time_var // 60)

penalty = model.new_int_var(0, max(cost_per_hour), 'penalty')
model.add_element(time_index, cost_per_hour, penalty)
model.minimize(penalty)
```

The pattern generalizes to any "look up cost from a table based on a decision variable." Useful for shift premiums, peak-hour pricing, deadline-related cost ramps.

---

## Practical Rules for Industrial Models

A working summary of patterns that hold across most scheduling problems:

- **Default objective:** weighted sum of penalties.
- **Tier when needed:** group related soft constraints (Critical, Important, Preferred); use lexicographic optimization between tiers, weighted sum within them.
- **Normalize before weighting** when penalties span different business dimensions.
- **Penalties over incentives** for solver-friendliness.
- **Surrogate objectives** when the natural one propagates poorly.
- **Warm starts** for complex objectives — provide a Solution Hint from a fast heuristic so the solver starts with a baseline feasible solution.

---

## Expert Discipline (Soft Constraint Phase)

The judgment moves that separate experienced modelers from novices on objective design:

- **Lexicographical preferences over single mega-objectives.** Solving in tiers is more robust than trying to outscale many objectives in one weighted sum.
- **Avoid mixing wildly different scales.** Use lexicographic tiers instead.
- **Calibrate by observing solver behavior, not by intuition.** The telltale rule and the symptoms of bad weighting are the actual feedback signal.
- **Always question whether a hard constraint should be soft.** Industrial problems are over-constrained by default; treating every rule as hard usually produces infeasibility, not safety.
