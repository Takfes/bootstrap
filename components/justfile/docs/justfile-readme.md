# justfile

Installs a `justfile` (used with the `just` command runner) defining the standard set of development commands for every project. A purpose-built task runner with consistent cross-platform behaviour, readable syntax, and no tab or `.PHONY` quirks.

---

## What Gets Installed

| File | Destination |
|------|-------------|
| `justfile` | Project root |

---

## Why `just` over `make`

`make` is a build system repurposed as a task runner. It has significant footguns: tab-sensitive syntax, `.PHONY` declarations required for non-file targets, different behaviour between GNU make (Linux) and BSD make (macOS), and poor Windows support.

`just` is purpose-built for running commands. It installs via `brew install just`, `scoop install just`, `cargo install just`, or `winget install just`.

See the [makefile component](../../makefile/docs/makefile-readme.md) if you prefer `make`.

---

## Prerequisites

Both must be on your `PATH` before any recipe will work:

- [`uv`](https://docs.astral.sh/uv/) — Python package and project manager
- [`pre-commit`](https://pre-commit.com/) — required for `hooks`, `validate`, `gitleaks`, `file-checks`, and `clean-cache`

---

## Commands Reference

### Setup & Environment

| Command | Description |
|---------|-------------|
| `just` (default) | List all available commands |
| `just install` | `uv sync --all-extras --dev` + install pre-commit hooks |
| `just update` | `uv sync --upgrade --all-extras --dev` — upgrade all deps to latest allowed versions |
| `just lock` | `uv lock` — regenerate lockfile without syncing |
| `just venv` | Show Python version, venv path, and installed packages |
| `just reset-venv` | Delete `.venv` and reinstall everything (prompts for confirmation) |
| `just clean-cache` | Remove cache and temporary files (via pre-commit hook) |
| `just clean` | Remove all generated artefacts (`.venv`, `dist`, caches, coverage) — runs `clean-build` first |

### Code Quality

| Command | Description |
|---------|-------------|
| `just ruff-check` | Run ruff linter on `src/` and `tests/` |
| `just ruff-format` | Run ruff formatter check on `src/` and `tests/` |
| `just fix` | `ruff check --fix` + `ruff format` — auto-fix all issues |
| `just format` | Alias for `just fix` |
| `just interrogate` | Check docstring coverage (`interrogate`) |
| `just deptry` | Analyse dependencies (`deptry .`) |
| `just typecheck` | `uv run mypy` |
| `just lint` | `ruff-check` + `ruff-format` + `interrogate` + `deptry` |

### Security & Validation

| Command | Description |
|---------|-------------|
| `just gitleaks` | Scan for hardcoded secrets (via pre-commit) |
| `just file-checks` | Run all file validation checks (via pre-commit) |
| `just validate` | `file-checks` + `gitleaks` + `clean-cache` |

### Testing

| Command | Description |
|---------|-------------|
| `just test` | `uv run pytest` |
| `just test-cov` | `uv run pytest --cov --cov-report=term-missing --cov-report=html` |

### Pre-commit & Hooks

| Command | Description |
|---------|-------------|
| `just pre-commit-staged` | Run pre-commit hooks on currently staged files |
| `just pre-commit-all` | Run pre-commit hooks on all files in the repo |
| `just hooks` | All hooks consolidated: `lint` + `validate` |

### Quality Gates

| Command | Description |
|---------|-------------|
| `just check` | Full quality gate: lock check + pre-commit (all files) + mypy + tests |
| `just ci` | Same as `check`; separate recipe so CI divergence stays explicit |

### Build

| Command | Description |
|---------|-------------|
| `just clean-build` | Remove build artefacts (`dist/`, `build/`) |
| `just build` | `uv build` — build wheel and sdist (runs `clean-build` first) |

### Run

| Command | Description |
|---------|-------------|
| `just run [args...]` | `uv run python -m {{package_name}} [args]` — run the project |

### Docs

| Command | Description |
|---------|-------------|
| `just docs-build` | `uv run mkdocs build` — build documentation site |
| `just docs-serve` | `uv run mkdocs serve` — serve docs locally with live reload |
| `just docs-test` | `uv run mkdocs build -s` — build docs and fail on any warning |

---

## Template Variables

`{{project_name}}` (comment at top), `{{package_name}}` (used in `just run`).

**Note on `{{...}}` syntax:** `just` and the bootstrap CLI both use `{{...}}` notation. `{{package_name}}` is a **bootstrap placeholder** replaced before the file is ever read by `just`. `{{args}}` in `just run` is a **just variadic argument** (native just syntax). Do not run `just` commands in a freshly templated repo before `bootstrap` substitution has completed.

---

## Installing `just`

```bash
# macOS
brew install just

# Windows
winget install just
scoop install just

# Linux / anywhere with cargo
cargo install just

# Or via pip (works everywhere Python does)
pip install rust-just
```

---

## Dependencies

None for most recipes. `gitleaks`, `file-checks`, `clean-cache`, `pre-commit-staged`, and `pre-commit-all` require pre-commit to be installed and configured in `.pre-commit-config.yaml`.

## Usage

```
bootstrap add justfile
```

The `justfile` is written to the project root. If one already exists it is skipped unless `--overwrite` is passed.
