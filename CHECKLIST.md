# Bootstrap — Pending Work Checklist

---

## Short-term

### Repository & Publishing
- [ ] Create GitHub repo `Takfes/bootstrap` and push
- [ ] Wire `DEFAULT_TEMPLATE_REPO` URL in `installer.py`
- [ ] Add `LICENSE` file
- [ ] Add `CONTRIBUTING.md`

### Components — Graduate from `future_work/`
- [ ] Move `future_work/justfile` → `components/justfile` + add to `manifest.toml`
- [ ] Move `future_work/makefile` → `components/makefile` + add to `manifest.toml`

### Component Completeness
- [ ] Add `README.md` to `components/agents/`
- [ ] Add `.python-version` placeholder to `components/uv/`
- [ ] Move `future_work/docs/` content into per-component `README.md` files (`uv`, `precommit`)
- [ ] Wire dependency relationships in `manifest.toml` for graduated components

### `pyproject.toml` Hardening (`components/uv/pyproject.toml`)
- [ ] Add `[project.urls]` (Homepage, Repository, Documentation)
- [ ] Add classifiers
- [ ] Add dev dependency group (pytest, mypy, ruff, deptry, pre-commit, mkdocs)
- [ ] Add `[tool.pytest.ini_options]`
- [ ] Add `[tool.coverage.run]` + `[tool.coverage.report]`
- [ ] Expand ruff lint ruleset

### Component Bug Fixes
- [ ] Fix undocumented `{{python_version_nodot}}` template variable — add derivation to `installer.py` or replace with explicit value in `components/uv/pyproject.toml`
- [ ] Fix tox config: `extras = dev` → `dependency-groups = ["dev"]` in `components/uv/pyproject.toml`
- [ ] Document system prerequisites (`trivy`, `markdownlint-cli2` / Node.js) in `components/precommit/` README
- [ ] Remove or populate empty `components/docs/` directory

---

## Mid-term

### Components — Graduate from `future_work/`
- [ ] Move `future_work/container` → `components/container` + add to `manifest.toml`
- [ ] Move `future_work/devcontainer` → `components/devcontainer` + add to `manifest.toml`
- [ ] Move `future_work/mkdocs` → `components/mkdocs` + add to `manifest.toml`
- [ ] Create `future_work/codecov/` component + graduate to `components/codecov` + add to `manifest.toml`

### README & Documentation
- [ ] Add badges to `README.md` (build status, license, version, codecov, commit activity)
- [ ] Set up MkDocs site (`mkdocs.yml`, `docs/` folder, GitHub Pages deploy)
- [ ] Document each component with its own page in MkDocs

---

## Long-term

### Components — Graduate from `future_work/`
- [ ] Move `future_work/ci` → `components/ci` + add to `manifest.toml`

### Repository & Publishing
- [ ] Publish to PyPI

### Tests
- [ ] Write pytest suite for CLI commands (`new`, `add`, `list`, `detect`)
- [ ] Write tests for `manifest.py` (local load, remote fallback)
- [ ] Write tests for `detector.py`
- [ ] Set up `tox.ini` for multi-version testing

### New Features
- [ ] Implement `update` command (re-apply components to refresh configs)
