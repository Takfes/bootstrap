---
paths:
  - "**/*.py"
  - "**/*.sh"
  - "**/*.sql"
  - "**/*.js"
  - "**/*.ts"
  - "**/*.jsx"
  - "**/*.tsx"
  - "**/pyproject.toml"
  - "**/requirements*.txt"
  - "**/package.json"
  - "**/Cargo.toml"
  - "**/go.mod"
  - "**/Gemfile"
---

## Before Writing Code

- State assumptions explicitly; if uncertain, ask rather than guess.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so and push back when warranted.

## Simplicity & Scope

- Minimum code that solves the problem — no speculative features, no unrequested flexibility/configurability, no error handling for impossible scenarios.

## Before Adding Code

Before writing something new, check in order — stop at the first that solves it: is it necessary at all (YAGNI) → does it already exist in this codebase → standard library → a dependency already installed → a one-liner. Only write new code once those are exhausted.

## Complexity Smells

Watch for: single-implementation abstractions (an interface, factory, or strategy with exactly one real case), thin wrappers that just delegate, deep inheritance or indirection chains, god objects (too many responsibilities), long functions, deep nesting, magic numbers, code built for "future needs" that aren't here yet. Prefer readability over cleverness; keep related code together.

Don't apply this to: untested legacy code, measured performance-critical paths, code about to be replaced soon, or complexity required by an external constraint.

## Surgical Editing

- Touch only what the task requires. Don't "improve" adjacent code, comments, or formatting. Don't refactor things that aren't broken. Match existing style even if you'd do it differently.
- Remove imports/variables/functions your own changes made unused. Leave pre-existing dead code alone — mention it, don't delete it, unless asked.
- Every changed line should trace directly to the request.

## Documentation & Readability

- Public functions, classes, and modules get a docstring covering purpose, parameters, return value, and error conditions, in the language's idiomatic format.
- Inline comments explain _why_, not _what_ — skip comments that just restate the code.
- Keep functions single-purpose; if a function's description needs "and," split it.

## Error Handling

Messages must answer three questions — what failed, why, and what to try next. Never swallow exceptions silently; prefer explicit over implicit.

## Testing & Verification

- Write tests for new public functions and any logic with branching, state, or side effects. Pure single-path transformations don't need tests.
- Bug fixes get a regression test that would have caught the bug.
- Define success criteria before starting multi-step work; loop until verified rather than declaring done on a guess.

## Behaviour

**Ask before major changes:** interface changes (rename/reorder/remove parameters), restructuring a module or moving files, changing behaviour existing callers depend on, or any edit touching more than ~30 lines outside the task's scope. Minor edits (bug fixes, a new optional parameter, a new function) don't need confirmation.

**Explain decisions** in one sentence: _"Using a dict here instead of a list for O(1) lookup."_

## Linting

If a linter or formatter can enforce a rule (naming, import order, formatting), configure the linter — don't restate it here as prose. This file is for judgment calls a linter can't make.

## Tool Preferences

| Task           | Use     | Not                   |
| -------------- | ------- | --------------------- |
| Read a file    | `Read`  | `cat`, `head`, `tail` |
| Search content | `Grep`  | `grep`, `rg`          |
| Find files     | `Glob`  | `find`, `ls`          |
| Edit a file    | `Edit`  | `sed`, `awk`          |
| Create a file  | `Write` | `echo >`, heredoc     |

Reserve Bash for system commands with no dedicated tool equivalent.

## Dependencies

Don't add a new dependency without asking first — name what you'd install and why, then wait for confirmation. Prefer the standard library or a dependency already in the project.
