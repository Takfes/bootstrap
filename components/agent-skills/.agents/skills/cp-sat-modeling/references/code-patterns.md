# CP-SAT Code Patterns

CP-SAT-specific code structure patterns. Loaded when the agent needs guidance on how to organize the Python that wraps the model — not how to write Python in general. This is a starter set; it can grow as patterns emerge from real usage.

## Solution Callbacks

`CpSolverSolutionCallback` is invoked every time the solver finds a new feasible (or improved) solution. Useful for monitoring progress, debugging objective behavior, and extracting intermediate solutions.

### Basic pattern

```python
from ortools.sat.python import cp_model

class SolutionLogger(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables_to_log):
        super().__init__()
        self._vars = variables_to_log
        self._count = 0

    def on_solution_callback(self):
        self._count += 1
        print(f"Solution {self._count}, obj={self.objective_value}, "
              f"best_bound={self.best_objective_bound}, "
              f"time={self.wall_time:.2f}s")
        for v in self._vars:
            print(f"  {v.name} = {self.value(v)}")

solver = cp_model.CpSolver()
callback = SolutionLogger([task.start_var for task in tasks])
solver.solve(model, callback)
```

### Debugging use

Solution callbacks are powerful for debugging objective behavior — print specific variables every time a new solution is found to see the *evolution* of solutions over the search. If the variables that should change with each improvement aren't changing, the objective isn't steering the search correctly.

### Production use

Keep callbacks lean. Heavy callback logic (database writes, complex calculations) slows down the search. If you need detailed logging, accumulate intermediate state in the callback and write/process it after the solve completes.

---

## Model Export and Reproducibility

### Exporting the model

```python
# Save the model in protobuf text format
with open('debug_model.pb.txt', 'w') as f:
    f.write(str(model.proto))

# Or binary format (faster, smaller)
with open('debug_model.pb', 'wb') as f:
    f.write(model.proto.SerializeToString())
```

The exported model can be:
- Re-loaded in another session for debugging
- Sent to the standalone `solve` command-line tool for diagnostic runs
- Diffed against a prior version to find what changed when "worked yesterday, broken today"

### Logging solver parameters

Always log the solver parameters used for a given run. The same model can produce different solutions on different runs because of `num_search_workers`, `random_seed`, `max_time_in_seconds`, and other parameters.

```python
solver = cp_model.CpSolver()
solver.parameters.num_search_workers = 8
solver.parameters.max_time_in_seconds = 60.0
solver.parameters.log_search_progress = True
solver.parameters.random_seed = 42  # for reproducibility

# Before solving: log the parameters
print(f"Solver params: workers={solver.parameters.num_search_workers}, "
      f"time={solver.parameters.max_time_in_seconds}s, "
      f"seed={solver.parameters.random_seed}")
```

When debugging an issue that only appears on specific runs, the parameters are part of the reproducible context.

---

## Naming Conventions

Variable names appear in the search log and in any model export. Bad names make logs unreadable. Two patterns help:

### Task and resource naming

Include both the entity and its role in the name:

```python
# Good — log output is interpretable
task_5_on_machine_2_interval
worker_3_shift_monday_present
```

```python
# Bad — log output is opaque
i123
b_45
```

### Boolean naming with negation in mind

Booleans appear positively and negatively in the log (`b` and `Not(b)`). Name them in a way that reads naturally in both:

```python
# Reads well: 'is_late' = True, Not(is_late) = "not late"
is_late = model.new_bool_var(f'is_late_task_{i}')
```

Avoid names that read awkwardly when negated (`not_finished` becomes `Not(not_finished)` in the log).

---

## Organizing a CP-SAT Codebase

For non-trivial models, three concerns benefit from being separated:

1. **Model construction.** The Python that builds the `cp_model.CpModel` instance — variables, constraints, objective.
2. **Solver configuration.** Parameters, callbacks, time limits.
3. **Solution extraction.** Code that reads the solution from the solver and produces the business output.

Mixing the three (e.g., setting solver parameters inside the function that builds the model) makes it hard to:
- Run the same model with different parameters
- Reuse the model construction in tests
- Save and load the model for diagnostic purposes

A working separation:

```python
def build_model(problem_data) -> cp_model.CpModel:
    """Construct the CpModel. No solving, no parameters, no extraction."""
    model = cp_model.CpModel()
    # ... variables, constraints, objective
    return model

def configure_solver(time_limit, num_workers) -> cp_model.CpSolver:
    """Build a configured solver. No model, no solving."""
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = num_workers
    solver.parameters.log_search_progress = True
    return solver

def extract_solution(solver, variables) -> dict:
    """Read the solution from the solver. No solving, no model knowledge beyond variables."""
    return {v.name: solver.value(v) for v in variables}
```

Tests can call `build_model` without solving. Debugging runs can pass different parameters to `configure_solver` without rebuilding. Solution extraction is decoupled from how the solution was found.

---

## Saving Solutions for Regression Tests

When a model "worked yesterday, broken today," the diagnostic move is comparing against a known-good prior solution. Save production-instance inputs and solutions:

```python
import json

# After a successful production solve
test_case = {
    'problem_input': problem_data,
    'expected_objective': solver.objective_value,
    'expected_assignments': {v.name: solver.value(v) for v in key_vars}
}
with open(f'test_cases/{instance_id}.json', 'w') as f:
    json.dump(test_case, f, indent=2)
```

When the model regresses, run the new model against the saved test cases. The cases that fail localize the regression.

---

## What This File Doesn't Cover

This is deliberately scoped to CP-SAT-specific patterns. The following are *not* covered here:

- General Python project structure (use whatever your team uses).
- Type hints, testing frameworks, documentation tooling (general Python concerns).
- Dependency management, packaging (project-level decisions).

The goal of this reference is to capture the patterns that are specific to CP-SAT and that practitioners reach for repeatedly. As more patterns emerge from real usage, extend this file.
