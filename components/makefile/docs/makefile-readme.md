# makefile

Installs a self-documenting `Makefile` that wraps common development tasks — environment setup, linting, testing, building, and docs — behind short, memorable targets.

---

## What Gets Installed

| File | Destination |
|------|-------------|
| `Makefile` | Project root |

---

## When to use `make` vs `just`

Use `make` (this component) for standard Python project workflows when GNU Make is already on your PATH (Linux/macOS default). Consider [`just`](../justfile/docs/justfile-readme.md) if you want cross-platform compatibility without GNU Make, or cleaner syntax for complex multi-command recipes.

---

## Prerequisites

Both must be on your `PATH` before any target will work:

- [`uv`](https://docs.astral.sh/uv/) — Python package and project manager
- [`pre-commit`](https://pre-commit.com/) — required for `hooks`, `validate`, `gitleaks`, and `file-checks` targets

---

## Commands Reference

### Setup & Environment

| Target | Description |
|--------|-------------|
| `make install` | Create `.venv`, sync deps, install pre-commit hooks |
| `make update` | Upgrade all deps to their latest allowed versions |
| `make lock` | Update `uv.lock` to match `pyproject.toml` |
| `make venv` | Show Python version, venv path, and installed packages |
| `make reset-venv` | Delete `.venv` and reinstall everything (prompts for confirmation) |
| `make clean-cache` | Remove cache and temporary files (via pre-commit hook) |
| `make clean` | Remove all generated artefacts (`.venv`, `dist`, caches, coverage) — runs `clean-build` first |

### Code Quality

| Target | Description |
|--------|-------------|
| `make ruff-check` | Run ruff linter on `src/` and `tests/` |
| `make ruff-format` | Run ruff formatter check on `src/` and `tests/` |
| `make fix` | Auto-fix lint issues (`ruff check --fix` + `ruff format`) |
| `make interrogate` | Check docstring coverage (`interrogate`) |
| `make deptry` | Analyse dependencies (`deptry .`) |
| `make typecheck` | Run mypy static type checker |
| `make lint` | `ruff-check` + `ruff-format` + `interrogate` + `deptry` |

### Security & Validation

| Target | Description |
|--------|-------------|
| `make gitleaks` | Scan for hardcoded secrets (via pre-commit) |
| `make file-checks` | Run all file validation checks (via pre-commit) |
| `make validate` | `file-checks` + `gitleaks` + `clean-cache` |

### Testing

| Target | Description |
|--------|-------------|
| `make test` | Run pytest |
| `make test-cov` | Run tests with coverage and generate HTML report |

### Pre-commit & Hooks

| Target | Description |
|--------|-------------|
| `make pre-commit-staged` | Run pre-commit hooks on currently staged files |
| `make pre-commit-all` | Run pre-commit hooks on all files in the repo |
| `make hooks` | All hooks consolidated: `lint` + `validate` |

### Quality Gates

| Target | Description |
|--------|-------------|
| `make check` | Full quality gate: lock check + pre-commit (all files) + mypy |

### Build

| Target | Description |
|--------|-------------|
| `make clean-build` | Remove build artefacts (`dist/`) |
| `make build` | Build wheel and sdist (runs `clean-build` first) |

### Run

| Target | Description |
|--------|-------------|
| `make run` | `uv run python -m $(PACKAGE_NAME)` — run the project |

### Docs

| Target | Description |
|--------|-------------|
| `make docs-test` | Build MkDocs and fail on any warning |
| `make docs` | Build and serve docs locally at `http://127.0.0.1:8000` |

### Utilities

| Target | Description |
|--------|-------------|
| `make help` | Print this target list (default goal) |

---

## How the help system works

Running `make` with no arguments prints the target list because `Makefile` sets:

```makefile
.DEFAULT_GOAL := help
```

The `help` target scans `$(MAKEFILE_LIST)` for any target with a `## comment`. Add `## your description` to any new target and it appears in the output automatically.

---

## Template variables

This `Makefile` uses `PACKAGE_NAME` as a variable for the `run` target. Set it at the top of the Makefile or override from the environment:

```bash
make run PACKAGE_NAME=myapp
```

All other targets are fully concrete and need no customisation.

---

## Dependencies

None for most targets. `gitleaks`, `file-checks`, `clean-cache`, `pre-commit-staged`, and `pre-commit-all` require pre-commit to be installed and configured in `.pre-commit-config.yaml`.

## Usage

```
bootstrap add makefile
```

The `Makefile` is written to the project root. If one already exists it is skipped unless `--overwrite` is passed.
