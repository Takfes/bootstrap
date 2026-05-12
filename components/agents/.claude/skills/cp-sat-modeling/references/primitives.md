# CP-SAT Primitives for Scheduling

The primitives covered here are the building blocks of CP-SAT scheduling models. The discipline is in choosing the right one — not in knowing all of them. CP-SAT's strength comes from specialized propagators on global constraints; manual decomposition into booleans gives that strength away.

## Interval Variables

Interval variables are the fundamental unit of scheduling. They link three quantities: `start + size = end`.

### When to use intervals vs plain integer start variables

Use `IntervalVar` whenever tasks interact through resources or non-overlap requirements. Intervals are mandatory input for `AddNoOverlap` and `AddCumulative`. The scheduling propagators (edge-finder, time-table) only activate on intervals, not on raw integer variables.

Plain integer start variables are acceptable only for simple precedence problems (`Start_B >= Start_A + Duration_A`) with no resource sharing and no disjunctive constraints. For any "real" scheduling problem with resources, default to intervals.

### Fixed-size vs variable-size intervals

`NewFixedSizeIntervalVar` — when duration is a known constant. Most efficient; the solver doesn't have to maintain `start + size = end` consistency over a variable size.

`NewIntervalVar` — when duration is a decision variable (e.g., 5–10 hours) or depends on other choices (e.g., processing time varies by machine).

The tradeoff: variable-size intervals are more flexible but more expensive. Prefer fixed-size whenever the modeling allows.

### Code patterns

```python
# Fixed size
start_var = model.new_int_var(0, horizon, 'start')
interval = model.new_fixed_size_interval_var(start_var, duration_const, 'interval')

# Variable size
duration_var = model.new_int_var(min_d, max_d, 'duration')
end_var = model.new_int_var(0, horizon, 'end')
interval = model.new_interval_var(start_var, duration_var, end_var, 'interval')
```

Name intervals after the task or resource they represent (e.g., `task_5_on_machine_2`) so log output is interpretable later.

---

## NoOverlap (Disjunctive Resource)

`AddNoOverlap` ensures no two intervals in a set overlap in time. Use it for unary or disjunctive resources — a single machine, a single worker, anything with capacity 1.

### When NoOverlap is the right choice

When a resource handles one task at a time. The constraint uses global algorithms (edge-finding, time-tabling) that propagate across the entire set of tasks simultaneously, pruning start and end times based on collective constraints.

### NoOverlap vs manual disjunction (the Big-M anti-pattern)

The single most important rule for CP-SAT modeling: **never encode disjunction with manual big-M or boolean enumeration when a global constraint exists.**

Manual disjunctions (`A before B OR B before A`, using `OnlyEnforceIf` over pairwise booleans) create a weak linear relaxation. They force the solver to branch on each pair. `AddNoOverlap` provides a tight constraint that the solver's internal scheduling engines exploit directly.

This anti-pattern often arrives by habit from MIP modeling. In MIP, you encode disjunction with big-M because that's the only mechanism available. In CP-SAT, the global constraint is the right tool — big-M formulations there ruin the linear relaxation, create numerical instability, and bypass the propagators that make CP-SAT fast. If a CP-SAT model has many big-M constants, it isn't really a CP-SAT model.

### NoOverlap with optional intervals

`AddNoOverlap` enforces non-overlap only among intervals that are *present* (their presence literal is true). Optional intervals are how you model "this task may or may not run on this resource."

```python
# Optional tasks on a single machine
machine_intervals = []
for task in tasks:
    presence_lit = model.new_bool_var(f'presence_{task.id}')
    interval = model.new_optional_fixed_size_interval_var(
        start, duration, presence_lit, f'interval_{task.id}')
    machine_intervals.append(interval)

model.add_no_overlap(machine_intervals)
```

---

## Cumulative (Shared Resource)

`AddCumulative` models resources with capacity greater than 1 — multiple tasks can run concurrently as long as total demand stays within capacity.

### When Cumulative is the right choice

Multi-capacity resources: a crew of 5 workers, a pool of 10 identical machines, a power grid with a capacity bound. The constraint enforces that at every time point, the sum of demands of active tasks is at most the capacity.

### Capacity-1 case

`AddCumulative` with capacity 1 will produce correct results but is generally less efficient than `AddNoOverlap` for the same problem. Default to `AddNoOverlap` for unary resources; reach for `AddCumulative` only when capacity is genuinely greater than 1.

### Time-varying capacity — the Mirror Task pattern

When capacity changes over the horizon (e.g., 10 workers during the day, 2 at night), do not introduce a time-varying capacity variable. Keep the resource's nominal capacity constant and create "dummy" intervals that consume the difference.

If capacity is 10 by default but 2 from time 500 to 1000, create a fixed interval `[500, 1000]` with demand 8. The solver sees a constant capacity of 10 with 8 units blocked at night, which propagates efficiently.

### Cumulative on top of NoOverlap

Adding `AddCumulative` on top of `AddNoOverlap` is sometimes worthwhile as a redundant constraint — see the performance skill for the discipline around redundant constraints in general. The brief version: if some subset of tasks would saturate the resource regardless of order, a cumulative constraint over them adds propagation strength.

### Worked pattern — multi-worker crew

A project has 10 tasks. Each task needs 1–3 workers. Total available: 5.

```python
intervals = []
demands = []
for t in tasks:
    iv = model.new_fixed_size_interval_var(t.start_var, t.duration, f'task_{t.id}')
    intervals.append(iv)
    demands.append(t.workers_needed)

model.add_cumulative(intervals, demands, 5)
```

---

## Circuit and Routing Structures

For sequence problems where the order of tasks matters more than absolute timing, or for traveling-salesman-style problems.

### AddCircuit vs manual sequence encoding

`AddCircuit` enforces a Hamiltonian circuit in a graph — a single loop visiting all nodes exactly once. The constraint has dedicated logic that prevents sub-tours at the propagator level. For any problem that decomposes into "find a circuit," it is the right tool.

Manual sequence encoding (boolean variables `x_i_j` meaning *i is immediately followed by j*) is needed when the structure is not a clean single circuit — multiple independent routes, partial sequences, paths rather than cycles. Manual encoding is typically used in conjunction with non-overlap rather than as a replacement for circuits.

### Sequence-dependent setup times

When the setup time between task A and task B depends on the specific pair (cleaning when switching from red paint to white paint), the canonical pattern is to use `AddCircuit` over a node graph.

- Nodes: tasks
- Arcs: possible transitions A → B, each carrying the corresponding setup time
- If the arc A → B is selected, then `End(A) + Setup(A, B) <= Start(B)`

`AddCircuit` provides far stronger pruning for this structure than `AddElement` over a transition matrix.

---

## Reservoir

Use `AddReservoirConstraint` for resources that are produced and consumed over time — they fill and drain rather than just being occupied.

### How reservoir differs from cumulative

- **Cumulative:** a task occupies a resource for a duration, then releases it. Inventory of "concurrently active" tasks.
- **Reservoir:** a task adds or subtracts a permanent quantity from a running total. The level at time t is the cumulative sum of all changes up to t.

Use cumulative for workers, machines, concurrent capacity. Use reservoir for fuel tanks, cash budgets, inventory levels, batteries.

### Worked pattern — inventory management

A warehouse capacity is 0–1000 units. Some tasks produce (add inventory), some consume (remove inventory). The constraint keeps the running level between 0 and 1000 at all times.

```python
times = [...]    # when each change occurs
demands = [...]  # positive to fill, negative to drain
model.add_reservoir_constraint(times, demands, 0, 1000)
```

### Cost gotcha

Reservoir constraints are computationally heavier than cumulative. Use them only when the resource genuinely behaves as fill-and-drain (specific events change the level), not just when a resource has a capacity. A cumulative will usually be cheaper if the modeling allows it.

---

## Optional Intervals and Alternative Resources

### Presence literals

A presence literal is a boolean variable that determines whether an interval is active in the solution. If false, the interval is invisible to `NoOverlap`, `Cumulative`, and `Circuit`.

**Gotcha:** constraints *outside* these global scheduling constraints — a simple `Start_A <= Start_B`, for example — still apply unless explicitly wrapped in `OnlyEnforceIf(presence_lit)`. Forgetting this wrapping is a common source of incorrect models where optional tasks are accidentally constrained as if always present.

### The Alternative Resource pattern

The canonical pattern for "Task T can run on Machine A or B or C":

1. Create one **master interval** representing the task's timeframe (optional or mandatory based on whether the task itself is optional).
2. Create one **child interval** for each candidate resource.
3. Each child has its own **presence literal** (`p_A`, `p_B`, `p_C`).
4. Constrain `ExactlyOne(p_A, p_B, p_C)` — exactly one resource is selected.
5. Link master and chosen child: `master.start == child_i.start`, `master.duration == child_i.duration`, all enforced `OnlyEnforceIf(p_i)`.

```python
master_start = model.new_int_var(0, horizon, 'master_start')
master_dur = model.new_int_var(min_d, max_d, 'master_dur')
master_end = model.new_int_var(0, horizon, 'master_end')

presence_lits = []
for r in candidate_resources:
    p = model.new_bool_var(f'task_on_{r.id}')
    child_dur = r.duration_for_task  # may differ per resource
    child = model.new_optional_interval_var(
        master_start, child_dur, master_end, p, f'child_{r.id}')
    presence_lits.append(p)
    # Link master to child when this resource is chosen
    model.add(master_dur == child_dur).only_enforce_if(p)
    # add child to the appropriate resource's NoOverlap/Cumulative

model.add_exactly_one(presence_lits)
```

**Variations:**
- **Alternative durations:** child intervals have different durations per resource (faster machine, slower machine).
- **Alternative skills:** only create child intervals for resources that have the required skill — illegal assignments are not modeled at all, which is more efficient than modeling and forbidding them.

### Optional tasks

For tasks that may not happen at all (optional maintenance, optional overtime shifts), use a single `NewOptionalIntervalVar` and tie its presence to the objective:

```python
present = model.new_bool_var('do_maintenance')
maintenance = model.new_optional_fixed_size_interval_var(
    start, duration, present, 'maintenance')

# Without an objective tie, the solver will skip optional tasks to ease constraints.
# Reward presence or penalize absence:
model.maximize(present * profit)
```

If the presence is not tied to the objective, the solver will simply set optional tasks to "not present" to make constraint satisfaction easier.

---

## Other Useful Primitives

### AddElement

Index lookup: `value = array[index]` where `index` is a decision variable. In scheduling, often used to map a task-type variable to a duration, cost, or transition time. Useful but generally less powerful than binary-variable encodings for the same logic — when both are expressible, binary variables with `AddExactlyOne` tend to propagate better and are more natural.

### AddAllowedAssignments (Table Constraint)

Defines a set of valid tuples for a group of variables. In scheduling, often used to define valid shift patterns or work-rest combinations that cannot be cleanly expressed by other constraints.

### AddAutomaton

Enforces that a sequence of values follows a state machine. Useful for complex work-rest rules like "after 4 hours of work, you must have at least 30 minutes of break." When the rule structure is regular-language-like, the automaton is far more efficient than encoding the rule manually.

### AddInverse

Links two arrays so that `f[i] = j` iff `inv[j] = i`. Useful for connecting two complementary views of the same decision (task-to-resource and resource-to-task assignment arrays). Use sparingly: the channeling can be more elegantly handled with binary variables for many problems, and inverse constraints sometimes have weaker propagation than the binary encoding for matching-style problems.

---

## The Primitive Selection Ladder

A working procedure for picking primitives given a fresh scheduling problem:

1. **Identify the unary resources** (one task at a time): `NewIntervalVar` + `AddNoOverlap`.
2. **Identify the shared resources** (capacity > 1): `AddCumulative` with task demands.
3. **Identify the choice points** (a task can run on multiple resources, with multiple durations): use the **Alternative Resource pattern**.
4. **Add sequence logic** if setup times depend on task order: `AddCircuit` with arcs carrying the setup costs.
5. **Look for problem-specific structure** (work-rest rules, valid patterns, regular-language constraints): `AddAutomaton` or `AddAllowedAssignments` where applicable.
6. **Consider redundant constraints** (see performance reference) once the baseline model is correct.

Following this ladder helps prevent the most common modeling mistake: building a brittle, hand-coded boolean-and-big-M model that the solver cannot effectively prune.

## Anti-Pattern Recap (Modeling Phase)

The discipline points worth keeping in mind while building the model:

- **Big-M is an MIP habit.** In CP-SAT, use `OnlyEnforceIf` or specialized global constraints instead.
- **Don't decompose global constraints.** Breaking `AllDifferent`, `Circuit`, or `Cumulative` into pairwise booleans hides the combinatorial structure that CP-SAT's propagators exploit.
- **Don't overuse indices.** Constraints based purely on integer indices (`AddElement`, `AddInverse`) often have less effective propagation than binary-variable encodings. Use binary variables for matching and assignment unless the index value carries inherent meaning.
- **Don't model illegal assignments.** When a resource cannot serve a task, simply omit the variable rather than create it and forbid it. Smaller search space, faster propagation.
