# Decomposition Strategies

Decomposition is the move from "find the best possible solution" to "find a solution that is significantly better than manual or heuristic methods, within a business time window." It is not a rejection of CP-SAT's power; it is the necessary architecture when the combinatorial scale exceeds what systematic search can handle.

The first-tier strategy is always to start with a monolithic model — CP-SAT's internal portfolio and Lazy Clause Generation are highly effective at finding structure that manual decompositions might obscure. Decomposition is what you do *after* the monolithic model proves it cannot scale.

## When to Decompose

### Criteria for transitioning from monolithic

**Scale signal.** CP-SAT can handle hundreds of thousands of variables in many contexts, but monolithic scheduling models typically start to struggle when discrete tasks exceed a few thousand and are tightly coupled via resource capacity constraints.

**Search-log signal.** Watch for stalling. If the solver finds an initial solution quickly but makes zero progress on the lower bound or upper bound over several minutes despite having many workers active, the search space is too vast for the current branching strategy.

**Structural signal.** Loose coupling between sub-problems is the strongest sign that decomposition will pay off. If a 30-day schedule has many constraints within each day but few constraints between days, it's a candidate for decomposition by day. If tasks fall into clearly separable groups (different customer orders, different shop floors, different geographic regions), decomposition by group is natural.

### The cost of decomposition

Decomposition has hidden costs:

- **Loss of global optimality.** Most decomposition strategies — especially LNS and rolling horizon — sacrifice the ability to *prove* optimality. You get a good solution, not a provably best one.
- **Implementation complexity.** Sub-model managers, state-handling logic between windows, custom validators to ensure independent sub-problem solutions are jointly feasible.
- **Meta-parameter tuning.** LNS adds neighborhood size and iteration count. Rolling horizon adds window size and overlap. These require their own benchmarking.

Don't decompose without confirming that the monolithic model genuinely can't scale to the required problem size. Decomposition is a meaningful commitment.

---

## Large Neighborhood Search (LNS)

LNS is the workhorse for scaling CP-SAT. Instead of searching the entire space, LNS iteratively destroys part of a current solution and uses the solver to optimally repair that fragment.

### Built-in LNS vs custom outer loop

**Built-in workers.** CP-SAT has a portfolio of LNS workers (e.g., `routing_path_lns`, `rins_lns`) that run in parallel and use different destroy heuristics. For medium-to-large problems, these are often sufficient and should be the first attempt at LNS.

To enable them, increase `num_search_workers` so CP-SAT can dedicate workers to LNS strategies in addition to the standard search. The solver picks LNS strategies automatically based on the problem.

**Custom outer loop.** When the built-in neighborhoods are too generic for a specific industrial structure, build an outer loop:

1. Call the solver to find an initial solution.
2. Extract the solution.
3. Manually freeze variables (set value or add a constraint pinning them).
4. Provide the previous solution as a hint via the `SolutionHint` API.
5. Re-call the solver for a short burst.

The custom loop is more work but lets you encode domain-specific "destroy operators" the generic strategies can't infer.

### Designing the neighborhood (the destroy operator)

The core of a custom LNS is which variables to release for re-optimization. Scheduling-specific patterns:

- **Time-window LNS.** Freeze all tasks except those starting within a specific 4-hour window. The solver intensely optimizes local task ordering without disturbing the rest of the week.
- **Machine-based LNS.** On a multi-machine shop floor, freeze assignments on all machines except one or two. The solver explores re-sequencing only on those.
- **Task-cluster LNS.** Use domain logic to identify correlated tasks (e.g., all tasks for one customer order) and release only the cluster. Useful when business structure determines what should move together.

### The LNS recipe

A working procedure for a custom outer loop:

1. **Initial solution.** Find any feasible solution quickly. A greedy heuristic is often good enough as a starting point.
2. **Select a neighborhood strategy.** Pick from the patterns above based on problem structure.
3. **Freeze and hint.** Fix variables in the frozen region. Provide the rest of the previous solution as a hint to the solver.
4. **Re-solve.** Run the solver for a short burst — typically 10–30 seconds.
5. **Accept or repeat.** If the new solution is better, keep it. If progress stalls in one neighborhood, switch strategies (round-robin or random-switch).

The patience-to-progress ratio matters. Each LNS iteration should yield improvement; if many iterations yield none, switch strategy rather than continuing the same one.

---

## Rolling Horizon

Rolling horizon decomposition is the natural fit for problems with a strong temporal component where future decisions have less impact on immediate decisions — port scheduling, workforce shift assignment, manufacturing operations that stream over weeks.

### The mechanics

The problem is sliced into overlapping segments:

- **Window size and overlap.** A common pattern: solve a 48-hour window but commit only the first 24 hours of decisions. The next iteration starts at the 24-hour mark, re-optimizing the overlap to account for cross-window transitions.
- **Handling commitments.** Decisions made in the committed part of the previous window are treated as fixed constants (hard constraints) in the current window.
- **Look-ahead value.** The uncommitted part of the window is a buffer that prevents current decisions from leading to states that make the next window infeasible. (For example: don't end a shift in a location with no work in the next window.)

### Worked pattern — port scheduling

Port scheduling exemplifies why rolling horizon fits:
- Ships arrive over time.
- Crane availability changes.
- A monolithic model for a month is intractable.

The solver processes a 3-day window each day, ensuring smooth transitions of equipment and staff. Decisions inside the committed period (today's berthing assignments) are fixed; decisions in the look-ahead period (tomorrow and beyond) get re-optimized as new information arrives.

### When rolling horizon fits

- The problem has natural temporal segmentation.
- Decisions far in the future have less impact on present ones.
- Information arrives incrementally — you don't know the full problem at start.
- Reasonable look-ahead is enough to prevent locally-optimal-but-globally-bad decisions.

### When rolling horizon doesn't fit

- Tight coupling between distant time periods (e.g., a constraint that the total over the whole horizon must equal X).
- The problem genuinely needs a global view.
- Look-ahead can't capture enough to prevent bad early commitments.

---

## Logic-Based Benders Decomposition

A powerful pattern for problems that split naturally into an "assignment" master and a "scheduling" sub-problem.

### Structure: master and sub-problem

**Master problem.** Assigns resources or tasks to high-level buckets (e.g., tasks to machines, or tasks to days). Focuses on the "what" and "where," ignores the detailed "when."

**Sub-problem.** For each bucket assigned by the master, the sub-problem tries to find a feasible schedule. Because it looks at one machine or one day at a time, it can use intensive propagation (`AddNoOverlap`, `AddCumulative`) very effectively on a small problem.

### The feedback loop — cut generation

If the sub-problem finds a master assignment infeasible, it returns a "no-good cut" to the master. The master is re-solved with the cut, producing a new assignment that respects the discovered infeasibility.

**Combinatorial cuts.** Simple constraints that forbid the specific combination: "this set of tasks cannot all be on Machine A simultaneously."

**Analytic / capacity cuts.** If the sub-problem fails because of energy or capacity reasoning, derive a cut from the failure: "any subset of tasks whose total work exceeds available capacity in this window cannot all be assigned together."

Combinatorial cuts are easier to derive; analytic cuts are stronger when applicable.

---

## Other Decomposition Patterns

### Column Generation (Dantzig-Wolfe)

Replaces a group of correlated individual variables with composite ones. In workforce scheduling, a composite variable represents an entire valid weekly shift pattern for an employee.

**Master problem.** Instead of thousands of individual shift-start variables, the master chooses one valid composite pattern per employee, ensuring overall coverage and labor-law compliance.

**Sub-problem (pricing).** A separate model (or dynamic programming algorithm) generates new high-quality patterns based on the dual prices of the current master solution.

Useful when natural composite units exist (weekly shifts, vehicle routes) and the number of feasible patterns is too large to enumerate explicitly.

### Hierarchical decomposition

Decomposes by organizational level rather than by time or resource. A "Week Manager" decides daily staffing totals and high-level goals; a "Day Manager" takes those totals as constraints and builds the hourly schedule.

**Trade-off.** Faster and more maintainable than monolithic, but risks over-constraining the lower level — the Week Manager's totals may be physically impossible to schedule given local travel-time or break-time rules. Mitigation: feedback channels between levels, or coarse-to-fine iteration.

---

## The Decomposition Ladder

A working procedure when facing a scaling issue:

1. **Monolithic with logging.** Enable `log_search_progress`, ensure the model is numerically stable, use global constraints over manual decompositions.
2. **Symmetry breaking.** Before decomposing, check if high failure rates in the search log are due to symmetric solutions. Add static symmetry-breaking constraints. (See performance reference.)
3. **Built-in LNS.** Increase `num_search_workers` to let CP-SAT explore diverse LNS strategies automatically in the background.
4. **Problem reformulation.** If the model still stalls, reconsider the "what." Sometimes replacing index-based `AddElement` constraints with binary variables $x_{ij}$ significantly improves the solver's bound-finding.
5. **Custom LNS or rolling horizon.** Only if the above fail, implement an outer loop. LNS for global optimization where parts of the whole can be improved. Rolling horizon for streaming or temporal problems.
6. **Full decomposition (Benders, column generation).** Advanced techniques for specific classes (large-scale logistics, complex workforce). Highest implementation effort.

### When to stop decomposing

Over-decomposition is a real failure mode. If sub-problems are so small that they lose global view, the resulting solution may be no better than a greedy heuristic. The rule: **sacrifice computation time before relaxing pruning standards.** An expensive propagation algorithm on a slightly larger sub-problem is usually better than a fast algorithm on a tiny, disconnected fragment.

If decomposition produces solutions visibly worse than what a heuristic alone produces, the decomposition is wrong, not the problem.
