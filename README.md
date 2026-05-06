# bootstrap

A portable Python project scaffolding CLI. Add modern tooling — dependency management, linting, pre-commit hooks, AI agent configs — to any project, new or existing, one component at a time.

---

## The Problem

Tools like cookiecutter-uv generate an entire project at once. That works for green-field projects but leaves two gaps:

- **Existing projects** can't be retrofitted
- **Selective adoption** isn't possible — it's everything or nothing

`bootstrap` solves both: it's a catalogue of independent components you can install into any project, in any combination, at any time.

---

## Quick Start

```bash
# No install needed — run directly from GitHub
uvx --from git+https://github.com/Takfes/bootstrap.git bootstrap --help

# Scaffold a new project (interactive — you pick the components)
bootstrap new my-project

# Add components to an existing project
bootstrap add

# See what components are available
bootstrap list

# See what's already configured in the current directory
bootstrap detect
```

---

## Installation

```bash
# Permanent install (recommended)
uv tool install git+https://github.com/Takfes/bootstrap.git

# Or run ad-hoc without installing
uvx --from git+https://github.com/Takfes/bootstrap.git bootstrap <command>
```

To enable the terminal UI:

```bash
uv tool install "bootstrap[tui] @ git+https://github.com/Takfes/bootstrap.git"
```

---

## Available Components

| Component | What it adds | Requires |
|-----------|-------------|---------|
| `uv` | `pyproject.toml` with uv, ruff, mypy, deptry, pytest, coverage configs | — |
| `precommit` | `.pre-commit-config.yaml` — ruff, mypy, gitleaks, semgrep, conventional commits | uv |
| `agents` | AI agent configs: Claude (`CLAUDE.md`), Gemini, Copilot, VSCode | — |

Components are fetched from this repo via git sparse-checkout — only the requested folder is downloaded, never the full repo.

---

## Commands

### `bootstrap new <project-name>`

Scaffold a new project. Prompts for template variables (author, GitHub org, Python version), then presents a component checklist — nothing is pre-selected, you choose what to install.

```bash
bootstrap new my-project
bootstrap new my-project -c uv precommit   # skip the checklist, install specific components
bootstrap new my-project -d ~/code/my-project
```

### `bootstrap add [component...]`

Add components to an existing project. Run without arguments to get the interactive checklist. If a component appears to be already installed, you'll be prompted before overwriting.

```bash
bootstrap add                  # interactive selection
bootstrap add agents           # install specific component
bootstrap add precommit --overwrite   # re-install, bypassing the overwrite prompt
```

### `bootstrap list`

Show all available components with descriptions and dependencies.

### `bootstrap detect`

Scan the current directory and report which components are installed, the project layout, and the detected GitHub remote.

---

## Terminal UI

Pass `--tui` to any interactive command to launch a full-screen terminal interface (requires `bootstrap[tui]`):

```bash
bootstrap --tui new my-project   # form for variables + component checklist
bootstrap --tui add              # component checklist with installed items marked
```

---

## Template Variables

Component files use `{{variable}}` placeholders substituted at install time.

| Variable | Source |
|----------|--------|
| `project_name` | CLI argument |
| `package_name` | Derived — underscores, e.g. `my_project` |
| `repo_name` | Derived — hyphens, e.g. `my-project` |
| `github_org` | Auto-detected from git remote, else prompted |
| `author` | Prompted |
| `author_email` | Prompted |
| `description` | Prompted (optional) |
| `python_version` | Prompted |

---

## Override the Template Repo

Components are fetched from this repo by default. To use a fork:

```bash
export BOOTSTRAP_TEMPLATE_REPO=https://github.com/your-org/bootstrap.git
bootstrap new my-project

# Or per-invocation
bootstrap add agents --repo-url https://github.com/your-org/bootstrap.git
```

---

## Architecture

```
src/bootstrap/
├── cli.py          # argparse CLI — subcommands: new, add, list, detect
├── manifest.py     # loads component list from components/manifest.toml
├── components.py   # ComponentSpec dataclass + cached get_components()
├── fetcher.py      # git sparse-checkout primitive
├── installer.py    # fetch + substitute + copy; smart merge for pyproject.toml
├── detector.py     # scans project for layout, installed components, git remote
└── tui.py          # optional Textual TUI (bootstrap[tui])

components/
├── manifest.toml   # source of truth for available components
├── uv/
├── precommit/
└── agents/
```

**Zero runtime dependencies.** Pure Python standard library. The `fetcher.py` primitive is also the shared entry point for a planned agentic skill — the same function the CLI calls can be called by Claude or Gemini to add components based on project context.

---

## Development

```bash
git clone https://github.com/Takfes/bootstrap
cd bootstrap
uv sync
just check      # lint + typecheck
just test-cli   # smoke test list + detect
just run list   # run any command locally
```

---

## Roadmap

- [ ] Agentic skill wrapping `fetcher.py` for AI-driven setup
- [ ] `bootstrap update` — re-apply components to refresh config files
- [ ] LLM-powered `README.md` generation in `bootstrap new`
- [ ] More components: CI/CD, devcontainer, docs, Dockerfile, justfile
