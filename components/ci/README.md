# Component: ci

**Purpose:** GitHub Actions workflows for automated testing, linting, and package publishing. Ensures every pull request is validated before merge, and every GitHub release triggers a clean PyPI publish.

---

## Files Delivered

| File | Description |
|------|-------------|
| `.github/workflows/main.yml` | Test/lint pipeline triggered on push and PR |
| `.github/workflows/publish.yml` | PyPI publish triggered on GitHub release |

---

## `main.yml` — CI Pipeline

**Triggers:** push to `main`, any pull request targeting `main`.

**Job: `test`**

Runs a matrix across multiple Python versions: the project's minimum version (from `{{python_version}}`) plus 3.12 and 3.13. This catches compatibility issues before they reach users on newer Pythons.

Steps:
1. `actions/checkout@v4` — standard checkout
2. `astral-sh/setup-uv@v5` — installs uv with caching enabled (speeds up subsequent runs significantly by caching the uv binary and the package download cache)
3. `uv python install` — pins the exact Python version for this matrix slot
4. `uv sync --all-extras --dev` — installs all dependencies including dev group
5. **Lint:** `uv run ruff check .`
6. **Format check:** `uv run ruff format --check .`
7. **Type check:** `uv run mypy src/`
8. **Tests:** `uv run pytest` (picks up config from pyproject.toml, outputs coverage XML)
9. **Coverage upload:** `codecov/codecov-action@v5` — uploads `coverage.xml` to Codecov. Requires `CODECOV_TOKEN` secret set in the repo settings.

The matrix runs all steps independently per Python version, so you see exactly which version a failure occurs on.

---

## `publish.yml` — PyPI Publish Pipeline

**Trigger:** `release` event with type `published` (i.e. when you create a GitHub release, not just a tag).

**Design: Trusted Publishing (no API tokens needed)**

Uses PyPI's OIDC trusted publishing mechanism. No `PYPI_TOKEN` secret required — PyPI trusts GitHub Actions directly based on the repo and workflow identity. You configure this once in PyPI's project settings (Trusted Publishers tab), pointing at this repo and workflow file name.

Steps:
1. Checkout
2. Install uv
3. `uv build` — builds the wheel and sdist into `dist/`
4. `uv publish` — uploads to PyPI using the OIDC token

The workflow runs with `permissions: id-token: write` which is required for OIDC authentication.

---

## Template Variables Used

`{{python_version}}` — sets the minimum Python version in the test matrix. The matrix also hard-codes 3.12 and 3.13 as "future compatibility" targets.

---

## Secrets Required

| Secret | Required for | Where to set |
|--------|-------------|--------------|
| `CODECOV_TOKEN` | Coverage upload | GitHub repo → Settings → Secrets → Actions |
| (none for PyPI) | Trusted publishing | Configure in PyPI project settings once |

---

## Future Refinements

- Add a `docs` workflow to build and deploy MkDocs to GitHub Pages on push to main
- Add `dependabot.yml` to auto-update Actions versions
- Consider `tox-uv` workflow for exhaustive multi-Python testing (separate from the PR matrix)
- Add a `draft-release` workflow using `release-drafter` to auto-generate changelogs
