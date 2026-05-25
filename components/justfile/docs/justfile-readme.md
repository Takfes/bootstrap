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

## Commands Reference

### Setup & Environment

| Command | Description |
|---------|-------------|
| `just` (default) | List all available commands |
| `just install` | `uv sync --all-extras --dev` — install all dependencies |
| `just update` | `uv sync --upgrade --all-extras --dev` — upgrade all deps to latest allowed versions |
| `just lock` | `uv lock` — regenerate lockfile without syncing |
| `just env` | Show Python version, venv path, and installed packages |
| `just reset-env` | Delete `.venv` and reinstall everything (prompts for confirmation) |
| `just clean` | Remove `dist/`, `build/`, `htmlcov/`, cache dirs |

### Run

| Command | Description |
|---------|-------------|
| `just run [args...]` | `uv run python -m {{package_name}} [args]` — run the project |

### Code Quality

| Command | Description |
|---------|-------------|
| `just lint` | `ruff check` + `ruff format --check` — lint, no fixes |
| `just fix` | `ruff check --fix` + `ruff format` — auto-fix all issues |
| `just format` | Alias for `just fix` |
| `just typecheck` | `uv run mypy src/` |
| `just deps` | `uv run deptry src/` — check for unused/missing dependencies |

### Testing

| Command | Description |
|---------|-------------|
| `just test` | `uv run pytest` |
| `just test-cov` | `uv run pytest --cov --cov-report=html` + open hint |

### Pre-commit & Hooks

| Command | Description |
|---------|-------------|
| `just hooks` | Install pre-commit for all stages, then run all hooks |
| `just pre-commit` | `pre-commit run --all-files` — run all hooks against entire repo |

### Quality Gates

| Command | Description |
|---------|-------------|
| `just check` | `lint` + `typecheck` + `test` + `deps` — full pre-PR validation |
| `just ci` | Same as `check`; separate recipe so CI divergence stays explicit |

### Build

| Command | Description |
|---------|-------------|
| `just build` | `uv build` — build wheel and sdist |

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

None. Works standalone after `just install` has run.

## Usage

```
bootstrap add justfile
```

The `justfile` is written to the project root. If one already exists it is skipped unless `--overwrite` is passed.
