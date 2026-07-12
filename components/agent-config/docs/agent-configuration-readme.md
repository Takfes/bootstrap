# agent-configuration

Provides Claude Code's behavioural foundation for a project. Installs a `CLAUDE.md` at the target project root and a set of rule files under `.agents/rules/` that define how the AI assistant should behave across all sessions in that project.

## What Gets Installed

- `CLAUDE.md` — root-level instruction file read automatically by Claude Code on every session
- `.agents/rules/` — 8 markdown rule files covering distinct behavioural domains

## Contents

| File | Description |
|------|-------------|
| `CLAUDE.md` | Master instruction file: standing orders, workspace layout, context references, and rule-loading triggers |
| `.agents/rules/agent-orchestration.md` | When and how to use subagents, parallelisation, model selection, staffing decisions |
| `.agents/rules/coding-conventions.md` | Python style, docstrings, error handling, testing standards, tool preferences |
| `.agents/rules/communication-style.md` | Proactive sharing, clarification thresholds, options format, devil's advocate framework |
| `.agents/rules/complexity-management.md` | Prompt optimisation, 4D methodology for ambiguous or multi-layered inputs |
| `.agents/rules/karpathy-guidelines.md` | Lean coding: think before coding, simplicity first, surgical changes, goal-driven execution |
| `.agents/rules/memory-workflows.md` | Search before starting, what to persist, how to use claude-mem across sessions |
| `.agents/rules/output-persistence.md` | File naming conventions, save-before-close protocol, session summaries |
| `.agents/rules/workspace-structure.md` | Folder layout, project lifecycle, archiving, intel log and learnings disciplines |

## Dependencies

None.

## Usage

After installing with `bootstrap add agent-configuration`, Claude Code reads `CLAUDE.md` on every session start and loads the relevant `.agents/rules/` files based on the task at hand. No further configuration required.
