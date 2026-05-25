# agent-subagents

Provides a roster of 21 specialised AI agent profiles for Claude Code. Each profile is a markdown file that defines a named agent with a specific role, expertise, and behavioural instructions. Agents can be referenced by name in prompts to dispatch focused subagents for specialised tasks.

## What Gets Installed

- `.agents/agents/` — 21 markdown agent profile files, each defining a named agent with a role title, system prompt, and domain expertise

## Contents

| Agent file | Role |
|------------|------|
| `python-pro.md` | Senior Python engineer — code quality, architecture, performance |
| `business-analyst.md` | Requirements gathering, process modelling, stakeholder communication |
| `code-reviewer.md` | Code review with correctness, security, and maintainability focus |
| `code-simplifier.md` | Reduces complexity, removes redundancy, improves readability |
| `codebase-orchestrator.md` | Multi-file refactoring and large-scale codebase changes |
| `competitive-analyst.md` | Market research, competitor analysis, strategic positioning |
| `cp-sat-scheduler.md` | Constraint programming with Google OR-Tools CP-SAT solver |
| `database-engineer.md` | Schema design, query optimisation, migrations |
| `devops-engineer.md` | CI/CD pipelines, infrastructure, deployment automation |
| `docker-expert.md` | Containerisation, Dockerfile best practices, multi-stage builds |
| `documentation-engineer.md` | Technical writing, API docs, docstring coverage |
| `eda-analyst.md` | Exploratory data analysis, statistical summaries, visualisation |
| `git-workflow-manager.md` | Branch strategies, commit hygiene, merge and rebase workflows |
| `knowledge-synthesizer.md` | Research synthesis, literature review, structured summaries |
| `kubernetes-specialist.md` | Kubernetes manifests, Helm charts, cluster management |
| `prompt-engineer.md` | Prompt design, optimisation, and evaluation |
| `qa-expert.md` | Test strategy, test coverage, QA process design |
| `research-analyst.md` | Deep research, evidence gathering, analytical reports |
| `agents-scrum-master.md` | Sprint planning, backlog management, agile ceremonies |
| `search-specialist.md` | Search query construction, information retrieval strategies |
| `technical-writer.md` | User-facing documentation, guides, tutorials |

## Dependencies

None. Works standalone, though pairing with `agent-configuration` is recommended so agents inherit the project's behavioural rules.

## Usage

After installing with `bootstrap add agent-subagents`, agents can be referenced by name in prompts to Claude Code (e.g. "get the code-reviewer on this" or "dispatch the eda-analyst"). Agent files live in `.agents/agents/` and are discovered automatically by Claude Code's agent tooling.
