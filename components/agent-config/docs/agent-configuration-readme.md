# agent-configuration

Provides Claude Code's behavioural foundation for a project. Installs an `AGENTS.md` at the target project root and a set of rule files under `.agents/rules/` that define how the AI assistant should behave across all sessions in that project.

## What Gets Installed

- `AGENTS.md` — root-level instruction file read automatically by Claude Code on every session
- `.agents/rules/` — 4 markdown rule files covering distinct behavioural domains

## Contents

| File | Description |
|------|-------------|
| `AGENTS.md` | Master instruction file: core operating rules, git workflow, maintenance |
| `.agents/rules/workspace.md` | Workspace folder layout (the `agents.io/` IO contract), stack, commands, documentation |
| `.agents/rules/coding-conventions.md` | Language-agnostic coding conventions: scope, complexity, surgical editing, docstrings, error handling, testing, tool preferences |
| `.agents/rules/python.md` | Python-specific style, docstrings, error handling, testing standards |
| `.agents/rules/karpathy-guidelines.md` | Lean coding: think before coding, simplicity first, surgical changes, goal-driven execution |

## Dependencies

None.

## Usage

After installing with `bootstrap add agent-configuration`, Claude Code reads `AGENTS.md` on every session start and loads the relevant `.agents/rules/` files based on the task at hand. No further configuration required.
