# uv Component

Provides the Python project foundation: `pyproject.toml`, `.python-version`, and a real starter
package + test so the project builds and passes immediately.

---

## What's in this folder

| File | What it is |
|------|-----------|
| `pyproject-flat.toml` / `pyproject-src.toml` | Two complete variants — the one matching your `layout` choice is installed as `pyproject.toml`; the other is skipped entirely |
| `.python-version` | Python version pin for uv (`{{python_version}}`) |
| `src/{{package_name}}/__init__.py` | Starter package (a `main()` function) — installed at `src/{{package_name}}/` for `src` layout, or `{{package_name}}/` at the project root for `flat` layout |
| `tests/test_main.py` | Matching test for the starter package |
| `docs/uv-workflow.md` | uv commands and daily workflow reference |
| `docs/uv-pyproject-reference.md` | Every `pyproject.toml` section annotated — what it does and why |
| `docs/uv-packaging-structures.md` | How to structure a project — layouts, workspaces, extras, decision guide |
| `docs/uv-packaging-mechanics.md` | How the build and import system works under the hood |

---

## Start here — based on what you need

| Goal | Read |
|------|------|
| Learn uv commands and daily workflow | `docs/uv-workflow.md` |
| Understand what a section in `pyproject.toml` does | `docs/uv-pyproject-reference.md` |
| Decide how to structure a new project (layouts, workspaces, extras) | `docs/uv-packaging-structures.md` |
| Debug an import error, understand editable mode, or learn how builds work | `docs/uv-packaging-mechanics.md` |
| Just want the template variable reference | Section below ↓ |

---

## Template variables

| Variable | Controls |
|----------|----------|
| `{{repo_name}}` | `[project] name`, GitHub URLs |
| `{{description}}` | `[project] description` |
| `{{github_org}}` | GitHub URL prefix |
| `{{python_version}}` | `requires-python`, mypy target, `.python-version` pin |
| `{{python_version_nodot}}` | ruff `target-version` (e.g. `312` for 3.12) |
| `{{package_name}}` | Importable package name — prompted, defaults to the derived form (can diverge from `{{repo_name}}`, like `Pillow`/`PIL`) |
| `{{layout}}` | `flat` or `src` — selects which `pyproject-*.toml` variant is installed and where the starter package lands |

`[project] authors` (`{{author}}` / `{{author_email}}`) and `{{layout}}` are prompted at install time.

---

## Dependency groups

```toml
[dependency-groups]
dev       = [ruff, mypy, deptry, pytest, pytest-cov, pre-commit, interrogate, codespell, tox-uv]
docs      = [mkdocs, mkdocs-material, mkdocstrings[python]]
notebooks = [nbqa, ipykernel]
```

```bash
uv sync                   # installs dev group by default
uv sync --group docs      # add the docs group
uv sync --all-groups      # install everything
```

---

## Quick command reference

```bash
uv sync                   # create/update .venv from lockfile
uv add <pkg>              # add runtime dependency
uv add --dev <pkg>        # add to dev group
uv run pytest             # run inside managed venv
uv run ruff check .       # lint
uv run ruff format .      # format
uv run mypy .             # type-check (mypy resolves the package via [tool.mypy], regardless of layout)
uv lock                   # regenerate uv.lock without installing
uv build                  # produce dist/*.whl and dist/*.tar.gz
```

---

## Superseded files

The following files are kept for reference but their content has been reorganised into the docs above:

| Old file | Content now in |
|----------|---------------|
| `uv-python-crash-course.md` | `docs/uv-workflow.md` |
| `PLAN.md` | `docs/uv-pyproject-reference.md` (fixes applied inline) |
| `packaging-structures.md` (original) | `docs/uv-packaging-structures.md` (rewritten) |
| `packaging-deep-dive.md` (original) | `docs/uv-packaging-structures.md` + `docs/uv-packaging-mechanics.md` |
