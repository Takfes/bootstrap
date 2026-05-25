# agent-skills

Provides a library of reusable skill definitions and browser commands for Claude Code. Skills are focused, invocable capabilities that the AI can load on demand — covering everything from CP-SAT modelling to PDF handling, git workflows, research synthesis, and presentation building.

## What Gets Installed

- `.agents/skills/` — skill definition directories, each containing a `SKILL.md` and supporting reference files
- `.agents/commands/` — two command files: `agent-browser.md` and `skill-browser.md` for discovering available agents and skills

## Contents

### Commands

| File | Description |
|------|-------------|
| `.agents/commands/agent-browser.md` | Lists and describes all available agents in `.agents/agents/` |
| `.agents/commands/skill-browser.md` | Lists and describes all available skills in `.agents/skills/` |

### Skills (selected)

| Skill | Description |
|-------|-------------|
| `agent-development` | Build and validate new Claude Code agent profiles |
| `brainstorming` | Structured creative exploration before implementation |
| `cp-sat-modeling` | Constraint programming model design with OR-Tools |
| `cp-sat-debugging-and-performance` | Debug and tune CP-SAT models |
| `eda-tooling` | Exploratory data analysis with pandas, matplotlib, seaborn |
| `executing-plans` | Execute multi-step implementation plans with checkpoints |
| `writing-plans` | Write structured implementation plans from specs |
| `git-commit` / `git-commit-wizard` | Conventional commit message generation |
| `python-refactor` | Systematic Python refactoring with quality gates |
| `python-testing-patterns` | pytest patterns, fixtures, coverage strategies |
| `pdf` | Read, merge, split, and process PDF files |
| `pptx` | Create and edit PowerPoint presentations |
| `notion-api` | Interact with the Notion API |
| `search-web` / `search-youtube` / `search-zotero` | Targeted search skills for different sources |
| `research-synthesis-planner` | Structure and synthesise research findings |
| `skill-creator` | Build new skills from scratch or improve existing ones |
| `subagent-driven-development` | Orchestrate parallel subagents for implementation tasks |

There are 55 skills in total. Run the `skill-browser` command in Claude Code to see the full list with descriptions.

## Dependencies

None.

## Usage

After installing with `bootstrap add agent-skills`, skills are invoked via Claude Code's Skill tool using the skill name (e.g. `/brainstorming`, `/git-commit`, `/python-refactor`). The `skill-browser` command provides an interactive index of all available skills.
