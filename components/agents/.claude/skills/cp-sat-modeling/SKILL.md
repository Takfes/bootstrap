---
name: cp-sat-modeling
description: Use this skill when building a Google OR-Tools CP-SAT scheduling model from a problem statement, or modifying an existing one. This skill encodes the methodology for the build phase — choosing CP-SAT primitives for scheduling, designing objectives and soft constraints, modeling time and capacity, and deciding whether and how to decompose large problems. Triggers when the user asks to "build", "construct", "model", or "design" a scheduling problem, when discussing a fresh scheduling problem statement, when adding new constraints or features to an existing model, or when choosing between modeling alternatives (which primitive, how to handle soft constraints, whether to decompose). Use this skill proactively for any open-ended CP-SAT scheduling modeling work.
---

# CP-SAT Modeling for Scheduling

The build-phase methodology for CP-SAT scheduling models. This skill is loaded when constructing, designing, or modifying scheduling models. For diagnosing slow or infeasible models, see the `cp-sat-debugging-and-performance` skill.

## Prime directive

Build models that **reveal the combinatorial substructure to the solver**, not that hide it. CP-SAT's strength comes from specialized propagators on global constraints — manual decomposition into booleans gives that strength away. Every modeling decision should favor expressing the problem in CP-SAT-native terms (intervals, no-overlap, cumulative, circuit, alternatives) over MIP-style encodings (big-M, manual disjunction, large boolean enumerations).

## The build sequence

Work through these stages in order. Each layer builds on the previous one.

1. **Characterize the problem before coding.** Identify entities (nouns) and constraints/relationships (verbs). Distinguish hard requirements from soft preferences. Sketch the model structure on paper or in comments before writing code.
2. **Solve the nominal version first.** Assume 24/7 availability, no setup times, no calendar effects. Verify the solver finds a solution. This catches modeling errors early.
3. **Add resource bottlenecks.** `AddNoOverlap` for unary resources, `AddCumulative` for shared resources. Use the primitive selection ladder below.
4. **Layer in calendar and availability.** Forbidden intervals, breaks, shift patterns. Watch for infeasibility from too-tight horizons.
5. **Add transitions and setup times.** `AddCircuit` for sequence-dependent setups.
6. **Design the objective.** Pick objective forms that propagate well; tier soft constraints if there are many.
7. **Decompose only if monolithic doesn't scale.** First-tier is always monolithic; decompose only after evidence that the monolithic approach cannot handle the problem size.

## The primitive selection ladder

Use this as the decision procedure for choosing constraints:

1. **Unary resources** (one task at a time) → `NewIntervalVar` + `AddNoOverlap`.
2. **Shared resources** (capacity > 1) → `AddCumulative` with per-task demands.
3. **Resource choice** (a task can run on multiple resources) → **Alternative Resource pattern** (master + optional child intervals + `AddExactlyOne` on presence literals).
4. **Sequence-dependent setup times** → `AddCircuit` with arcs encoding setup costs.
5. **Regular-language work-rest rules** → `AddAutomaton`.
6. **Valid patterns expressible as tuples** → `AddAllowedAssignments` (table constraint).
7. **Redundant constraints** (see debugging-and-performance skill) → consider only after baseline is correct.

For detailed code patterns and reasoning per primitive, see `references/primitives.md`.

## Hard vs soft — the discipline question

Industrial scheduling problems are almost always over-constrained. A hard constraint is a commitment that no solution is preferable to a solution that violates it. When that's not the actual business position, the constraint must be soft.

When uncertain, default to soft. The hard-to-soft relaxation pattern (see references/objectives.md) lets you re-tighten if violations turn out to be unacceptable. The opposite move — discovering after the fact that infeasibility is caused by a constraint that should have been soft — is more costly.

## Objective design — quick rules

- Default form: weighted sum of penalties (minimization, not maximization).
- Prefer penalties over incentives; minimization bounds work better with solver pruning.
- For many soft constraints (5+), use lexicographic tiers (Critical / Important / Preferred) with weighted sums within tiers.
- Calibrate weights using the **telltale rule**: always-violated means too low, never-violated means too high.
- Don't mix wildly different magnitude scales in one weighted sum; use lexicographic tiers instead.

Full guidance on objectives, soft constraint mechanics, and penalty calibration: `references/objectives.md`.

## Time and capacity — quick rules

- Granularity: use the GCD of all task durations and time-based constraints.
- Horizon: realistic worst-case upper bound, not `INT_MAX`.
- Calendar interruptions: model as fixed intervals on the resource's `AddNoOverlap` set ("forbidden interval" pattern).
- Time-varying capacity: keep nominal capacity constant; use "mirror task" dummy intervals to consume the unavailable portion.
- Sliding-window aggregates ("no more than N in any T-hour window"): use `AddCumulative` with fixed duration T as a buffering resource ("Temporal Resource Buffering" pattern).

Full guidance on time representation, capacity, resources, setup times, skills/compatibility, and availability: `references/time-capacity.md`.

## Decomposition — quick rules

- Start monolithic. Don't decompose preemptively.
- Decomposition signals: thousands of tightly-coupled tasks, stalled search log over minutes, loose coupling structure (e.g., independent days, independent customer orders).
- The decomposition ladder: monolithic → symmetry breaking → built-in LNS (more workers) → reformulation → custom LNS or rolling horizon → full decomposition (Benders, column generation).
- Don't over-decompose. Sub-problems too small lose global view and produce solutions no better than heuristics.

Full guidance on LNS, rolling horizon, logic-based Benders, column generation, and the decomposition ladder: `references/decomposition.md`.

## Code organization

For CP-SAT-specific code patterns (solution callbacks, model export, parameter logging, naming conventions, separation of model construction from solving): `references/code-patterns.md`.

## Anti-patterns (modeling phase)

- **Big-M for disjunction.** Use `OnlyEnforceIf` and specialized global constraints (`AddNoOverlap`, `AddCircuit`) instead. If a model has many big-M constants, it's not really a CP-SAT model.
- **Decomposing global constraints into booleans.** Hides the combinatorial substructure the solver's propagators rely on. Use the most specific global constraint available.
- **Index overuse.** Constraints based purely on integer indices (`AddElement`, `AddInverse`) often have weaker propagation than binary-variable encodings. Use binary variables for matching unless the index value carries inherent meaning.
- **Modeling illegal assignments.** When a resource can't serve a task, omit the variable rather than create it and forbid it.
- **Making every business rule a hard constraint.** Industrial problems are over-constrained; default soft, harden only when justified.
- **Skipping the nominal-problem-first step.** Solving the full model immediately means modeling errors are tangled with the solver's struggles. Solve the simpler version first.

## When to load this skill alongside others

- For diagnosing infeasibility or performance: also load `cp-sat-debugging-and-performance`.
- For non-trivial OR-Tools API code: consult Context7 for current API patterns; this skill says *what* to do, Context7 says *how the current API expresses it*.

## Working artifact

The subagent maintains `cp-notes-agent.md` with modeling decisions: what primitives were chosen, what alternatives were considered, what was rejected and why. This persists across iterations within the session and is the working record of the build phase.
