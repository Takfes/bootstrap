# Time, Capacity, and Resource Modeling

CP-SAT scheduling is the arrangement of interval variables across a temporal horizon, governed by constraints managing how resources are consumed or shared. The decisions made on time representation, capacity, and resources cascade through the entire model — getting them right at the outset is far cheaper than refactoring later.

## Time Representation

### Granularity

CP-SAT is a discrete solver: all temporal values are integers. The choice of time unit is the most foundational decision in the model.

**The selection rule:** use the greatest common divisor (GCD) of all task durations, setup times, and time-based constraints. If tasks are 15, 30, and 45 minutes, the time unit is 15 minutes. If a single task takes 17 minutes, the whole model moves to 1-minute granularity.

**Too fine (e.g., milliseconds over a month-long horizon):**
- Numerical instability in the LP relaxation
- Slower propagation, especially for `AddCumulative`
- Tighter bounds become harder to maintain

**Too coarse:**
- Aliasing — feasible solutions are lost because they don't align with the grid
- Rounding errors that make the modeled problem subtly different from the real one

### Scaling continuous time

When time is naturally continuous (1.5 hours), use a fixed-point representation:

```python
# Scaling factor of 100 for two decimal places
scaling_factor = 100
duration_minutes = int(1.5 * 60 * scaling_factor)  # 9000 units of (minute/100)
```

Pick the smallest scaling factor that preserves meaningful differences. Don't scale to keep precision that won't affect business decisions.

### Horizon sizing

The horizon is the upper bound for every `End` variable. CP-SAT tolerates large horizons better than most solvers because Lazy Clause Generation only creates literals as needed — but unnecessary horizon expansion is still wasted bound that loosens the LP relaxation.

**Horizon sizing procedure:**
1. Compute a realistic lazy upper bound: $\sum(\text{Durations}) + \sum(\text{Max Transitions})$.
2. If the problem is shift-scheduled, the horizon is the strict end of the last shift.
3. Avoid `INT_MAX` unless genuinely necessary. Use a realistic worst-case bound.

### Calendar effects and forbidden intervals

Real-world time is interrupted by weekends, holidays, nights, and breaks. The cleanest pattern is to model calendar interruptions as **fixed, non-optional intervals** added to the resource's `AddNoOverlap` set.

```python
# A machine is unavailable from time 100 to 150
downtime = model.new_fixed_size_interval_var(100, 50, 'downtime')
model.add_no_overlap(task_intervals + [downtime])
```

The solver pushes tasks either before 100 or after 150 without any explicit `if-then` logic. This is far cleaner than introducing conditional constraints to "skip" time.

---

## Capacity and Shared Resources

### Single-capacity (disjunctive) resources

The most common scheduling case: a resource handles one task at a time. The tool is `AddNoOverlap`.

**Pattern: optional task on multi-resource set.** A task may run on Resource A or Resource B. Use optional intervals with presence literals:

```python
presence_lit = model.new_bool_var(f'task_{i}_on_res_{r}')
interval = model.new_optional_interval_var(
    start, duration, end, presence_lit, f'interval_{i}_{r}')
```

Combined with `AddExactlyOne` over the presence literals across resources, this is the alternative-resource pattern (covered in primitives.md).

**Edge case: planned downtime.** Treat maintenance windows as fixed-time, highest-priority tasks — not a separate solver mode. The forbidden-interval pattern above handles this cleanly.

### Multi-capacity (cumulative) resources

When a resource can handle multiple tasks concurrently (a crew of 10 workers, a pool of identical machines), use `AddCumulative`.

The invariant: at any time t, the sum of demands of active tasks ≤ resource capacity.

### Time-varying capacity — the Mirror Task pattern

When capacity changes over the horizon (10 workers during the day, 2 at night), do not introduce a time-varying capacity variable. Keep the resource's nominal capacity constant and create dummy tasks that consume the difference.

```python
# Nominal capacity: 10
# At night (time 500-1000), actual capacity is 2 → block 8 units
night_blocker = model.new_fixed_size_interval_var(500, 500, 'night_blocker')
demands_with_blocker = task_demands + [8]
intervals_with_blocker = task_intervals + [night_blocker]
model.add_cumulative(intervals_with_blocker, demands_with_blocker, 10)
```

The solver sees a constant capacity of 10 with 8 units "blocked" at night. This propagates efficiently. Trying to model time-varying capacity directly typically requires complex conditional logic that propagates worse.

### Reservoir-type resources

For resources that fill and drain — tanks, batteries, cash budgets — use `AddReservoirConstraint`. It takes lists of times (or intervals) and level changes:

```python
times = [...]    # when each change occurs
demands = [...]  # positive for fill, negative for drain
model.add_reservoir_constraint(times, demands, min_level, max_level)
```

Reservoirs are computationally heavier than cumulatives. Use them when the resource genuinely fills and drains via discrete events, not just when a resource has capacity. If a cumulative will express the constraint, prefer cumulative.

---

## Setup, Transition, and Travel Times

Basic models that ignore setup times are typically demos. Industrial models almost always have setup or transition costs.

### Sequence-dependent setup times

If Task B follows Task A on a resource, there is a setup time $S_{AB}$ that depends on the pair.

**The Circuit pattern** is the canonical CP-SAT approach:

1. Create a node for every task on the resource.
2. Add a literal for every possible transition $A \to B$.
3. `model.add_circuit(arcs)` ensures a single Hamiltonian path.
4. Link the arc to the timing: if arc $A \to B$ is selected, then `End(A) + Setup(A, B) <= Start(B)`.

This provides much stronger pruning than `AddElement` over a transition matrix, because `AddCircuit`'s no-subtour logic prunes large parts of the search space that pure linear constraints cannot.

**The Element alternative:** for smaller problems where setup matters but the full sequencing isn't the focus, `AddElement` into a transition matrix is simpler to write. Acceptable for small task counts; falls behind on larger problems.

### Travel times (routing-scheduling hybrid)

In technician scheduling or vehicle routing, "setup time" becomes "travel time between locations." Treat each technician or vehicle as a resource, and use `AddMultipleCircuit` for multiple agents.

```python
# Logical constraint when arc (i,j) is selected for a technician:
# End(visit_i) + Travel(i,j) <= Start(visit_j)
```

For routing problems with significant scheduling components, the dedicated OR-Tools routing library may be more appropriate than building everything from CP-SAT primitives. Use CP-SAT directly when the scheduling constraints dominate the routing aspects.

---

## Availability, Breaks, and Rosters

The corpus draws a sharp practical line between **scheduling** (when does the task start?) and **rostering** (who works which shift?).

### Worker shifts and roster patterns

Use boolean sequences for shift patterns. To enforce "no more than 6 days in a row":

```python
for d in range(num_days - 6):
    model.add(sum(work_days[d : d+7]) <= 6)
```

This is a sliding-window pattern; it generalizes to any "no more than X of Y consecutive" rule.

### Forbidden assignments

If a worker cannot work shift X, *do not create the boolean variable*. Reducing the search space before solving starts is more efficient than creating variables and then forbidding them:

```python
# Only create variables for legal assignments
allowed_workers = [w for w in workers if w.has_skill(task.required_skill)]
assign_vars = [model.new_bool_var(f'task_{i}_on_{w.id}') for w in allowed_workers]
model.add_exactly_one(assign_vars)
```

### Preemption (interruptible tasks)

CP-SAT `IntervalVar` is non-preemptable — a single start, duration, and end. To model interruptible tasks (e.g., paused for lunch), the standard approach is the **breakdown pattern**:

1. Split the task into `Part_1` and `Part_2`.
2. `Duration(Part_1) + Duration(Part_2) == Total_Duration`.
3. `End(Part_1) <= Start(Part_2)`.
4. Add a minimum gap if the break has a fixed length; allow flexibility if not.

This is correct but explicit. There is a Jackson's Preemptive Schedule approach where each task is split into many 1-unit intervals managed by `AddCumulative`, but it is extremely slow for non-trivial problems. Stick to discrete parts when preemption matters.

---

## Compatibility and Skills

### Skill-matching

For "task X needs a worker with skill Y," the recommended pattern uses a precomputed compatibility matrix and creates variables only for legal assignments:

```python
worker_has_skill = {(w, s): w.has_skill(s) for w in workers for s in skills}

for task in tasks:
    allowed = [w for w in workers if worker_has_skill[(w, task.required_skill)]]
    assign_vars = [model.new_bool_var(f'task_{task.id}_on_{w.id}') for w in allowed]
    model.add_exactly_one(assign_vars)
```

This avoids the modeling error of creating variables for illegal pairs and then forbidding them — same answer, larger search space.

### Resource compatibility groups with different speeds

When a task can use any machine in a group, but machines have different speeds, use `AddElement` to look up the per-machine speed and bind the task's duration accordingly:

```python
worker_idx = model.new_int_var(0, num_workers - 1, 'worker_idx')
current_speed = model.new_int_var(min_speed, max_speed, 'current_speed')
model.add_element(worker_idx, worker_speeds, current_speed)
duration_i = model.new_int_var(min_duration, max_duration, 'duration_i')
model.add(duration_i * current_speed == base_work_units)
```

---

## Time-Windowed Aggregates (Sliding Windows)

A common industrial constraint: "no more than N occurrences of pattern X in any T-hour window." The naive implementation loops through every possible T-hour window and adds a sum constraint — that's $O(H)$ constraints over a horizon $H$, which is wasteful.

**The Temporal Resource Buffering pattern:** use `AddCumulative` even when the resource has no actual capacity limit.

To express "no more than 3 heavy-lifting tasks in any 4-hour window":

1. Give every heavy-lifting task a demand of 1.
2. Give every such task a **fixed duration of 4 hours**, regardless of its actual work duration.
3. Set the buffering resource's capacity to 3.

Because each task "occupies" 4 hours of capacity-3 buffering resource, the constraint is satisfied. The cumulative propagator handles the sliding window logic efficiently. One constraint replaces $O(H)$.

---

## The Modeling Workflow

A working sequence for building scheduling models from a problem statement:

1. **Start with the nominal problem.** Assume 24/7 availability, no setup times, no calendar effects. Verify the solver finds a solution to the simpler problem first.
2. **Add NoOverlap / Cumulative for resource bottlenecks.** This introduces the core scheduling structure.
3. **Layer in forbidden intervals (calendars).** Watch for infeasibility here — a too-tight horizon plus calendar interruptions can make a feasible-looking model infeasible.
4. **Add transitions and setup times.** Use `AddCircuit` for sequence-dependent setups.
5. **Performance check via the search log.** If the post-presolve boolean count explodes, you likely created too many optional intervals or unnecessary transition arcs.
6. **Revisit redundant constraints and symmetry breaking** (see performance reference) only after the baseline model is correct.

The discipline of solving the simpler version first catches modeling errors early. A model that won't solve at all is harder to debug than a model that solves the wrong thing.

---

## Known Limitation: Time-Varying Task Demands

The standard patterns treat task demand as constant over the interval. For tasks whose resource consumption changes *while running* (e.g., a process that needs 5 workers for the first hour and 2 for the rest), the workaround is to split the task into consecutive intervals with different demand levels, linked by precedence:

```python
part_1 = model.new_fixed_size_interval_var(start_1, 1, 'part_1')   # demand 5
part_2 = model.new_fixed_size_interval_var(start_2, 3, 'part_2')   # demand 2
model.add(start_2 == start_1 + 1)
model.add_cumulative([part_1, part_2], [5, 2], capacity)
```

This works but is verbose. There is no native CP-SAT support for time-varying demand within a single interval.
