# pre-commit Component

Installs `.pre-commit-config.yaml` with 15 hooks covering three Git stages: `commit`, `commit-msg`, and `push`. Catches common problems (secrets, broken lockfiles, type errors, lint violations, spelling mistakes) before they reach version control.

---

## What Gets Installed

- `.pre-commit-config.yaml` — fully configured hook definitions for all three Git stages

---

## Install

Run once per clone after installing with `bootstrap add precommit`:

```bash
pre-commit install \
  --hook-type pre-commit \
  --hook-type commit-msg \
  --hook-type pre-push
```

Re-run after any change to `.pre-commit-config.yaml`.

**Why three `--hook-type` flags?** By default `pre-commit install` only wires up the `pre-commit` Git hook. The `commit-msg` and `push` stage hooks live in separate files in `.git/hooks/` and are silently ignored unless explicitly installed.

---

## All hooks at a glance

| Hook | Stage | Description |
| ---- | ------ | ----------- |
| `clean-cache-files` | commit | Removes `__pycache__`, `.DS_Store`, `.ruff_cache`, etc. before every commit |
| `uv-lock-check` | commit | Blocks commits where `pyproject.toml` and `uv.lock` have diverged |
| file hygiene (~14 hooks) | commit | Whitespace, line endings, file size, config syntax (YAML/TOML/JSON/XML) |
| `ruff-check` + `ruff-format` | commit | Lints and reformats Python files and notebooks |
| `nbstripout` | commit | Strips notebook outputs so diffs show only code changes |
| `interrogate` | commit | Enforces docstring presence — fails below the configured threshold |
| `markdownlint-cli2` | commit | Lints Markdown for structural consistency, auto-fixes what it can |
| `codespell` | commit | Detects common spelling mistakes, auto-corrects in-place |
| `gitleaks` | commit | Scans staged content for secrets, API keys, and credentials |
| `deptry` | commit | Audits `pyproject.toml` against actual imports |
| `sqlfluff` | commit | Lints and auto-formats SQL files |
| `conventional-pre-commit` | commit-msg | Validates Conventional Commits format on every commit message |
| `mypy` | push | Full static type checking across the codebase |
| `semgrep` | push | Security and code quality analysis (OWASP, `p/python` rule set) |
| `trivy-config` | push | Scans IaC and config files for HIGH/CRITICAL misconfigurations |

For per-hook details — what each catches, how to install it, and how to run it manually — see [`docs/precommit-hooks-reference.md`](docs/precommit-hooks-reference.md).

---

## Dependencies

None. Works standalone, though it pairs naturally with the `ultraviolet` component (which provides the `pyproject.toml` that several hooks read for their configuration).

## Usage

After installing with `bootstrap add precommit` and running the install command above, hooks fire automatically on `git commit`, `git commit --amend`, and `git push`. Run any hook manually with:

```bash
pre-commit run --all-files                          # all commit-stage hooks
pre-commit run --hook-stage push --all-files        # all push-stage hooks
pre-commit run <hook-id> --all-files                # a specific hook
```
