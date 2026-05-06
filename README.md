# bootstrap

A portable Python project scaffolding CLI. Add modern tooling — dependency management, linting, pre-commit hooks, AI agent configs — to any project, new or existing, one component at a time.

---

## The Problem

Tools like cookiecutter-uv generate an entire project at once. That works for green-field projects but leaves two gaps:

- **Existing projects** can't be retrofitted
- **Selective adoption** isn't possible — it's everything or nothing

`bootstrap` solves both: it's a catalogue of independent components you can install into any project, in any combination, at any time.

---

## Getting Started

### Without Installing (uvx)

**CLI:**

```bash
uvx --from git+https://github.com/Takfes/bootstrap.git bootstrap new my-project
uvx --from git+https://github.com/Takfes/bootstrap.git bootstrap add
uvx --from git+https://github.com/Takfes/bootstrap.git bootstrap list
```

**TUI:**

```bash
uvx --from "bootstrap[tui] @ git+https://github.com/Takfes/bootstrap.git" bootstrap --tui new my-project
uvx --from "bootstrap[tui] @ git+https://github.com/Takfes/bootstrap.git" bootstrap --tui add
```

### With Installation

**CLI:**

```bash
uv tool install git+https://github.com/Takfes/bootstrap.git
bootstrap new my-project
bootstrap add
bootstrap list
```

**TUI:**

```bash
uv tool install "bootstrap[tui] @ git+https://github.com/Takfes/bootstrap.git"
bootstrap --tui new my-project
bootstrap --tui add
```

---

## Commands

The following commands are identical regardless of how you invoke `bootstrap` (installed or via uvx).

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

## Source

### `src/bootstrap/`

```
src/bootstrap/
├── cli.py          # argparse CLI — subcommands: new, add, list, detect
├── manifest.py     # loads component list from components/manifest.toml
├── components.py   # ComponentSpec dataclass + cached get_components()
├── fetcher.py      # git sparse-checkout primitive
├── installer.py    # fetch + substitute + copy; smart merge for pyproject.toml
├── detector.py     # scans project for layout, installed components, git remote
└── tui.py          # optional Textual TUI (bootstrap[tui])
```

Zero runtime dependencies — pure Python standard library.

### Available Components

```
components/
├── manifest.toml   # source of truth for available components
├── uv/
├── precommit/
└── agents/
```

| Component | What it adds | Requires |
|-----------|-------------|---------|
| `uv` | `pyproject.toml` with uv, ruff, mypy, deptry, pytest, coverage configs | — |
| `precommit` | `.pre-commit-config.yaml` — ruff, mypy, gitleaks, semgrep, conventional commits | uv |
| `agents` | AI agent configs: Claude (`CLAUDE.md`), Gemini, Copilot, VSCode | — |

Components are fetched via git sparse-checkout — only the requested folder is downloaded, never the full repo.

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
