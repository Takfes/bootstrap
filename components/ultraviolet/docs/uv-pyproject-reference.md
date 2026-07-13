# `pyproject.toml` Annotated Reference

**Purpose:** Open this when you don't recognise a config section, need the rationale behind a setting, or want to know which values to change for a specific layout. This is not a tutorial — it assumes familiarity with Python packaging basics.

**Template placeholders** (substituted by the bootstrap CLI at generation time):
- `{{repo_name}}` — the repository / distribution name (e.g. `my-library`)
- `{{package_name}}` — the importable Python package name (e.g. `my_library`)
- `{{python_version}}` — version as `X.Y` (e.g. `3.12`)
- `{{python_version_nodot}}` — version as `XY` (e.g. `312`)
- `{{github_org}}` — project metadata
- `{{author}}` / `{{author_email}}` — prompted at install time

---

## Section map

| Section | Purpose | Required? |
|---|---|---|
| `[project]` | Core package metadata (name, version, deps, Python constraint) | Required |
| `[project.urls]` | Links shown on PyPI | Optional |
| `[project.scripts]` | CLI entry points | Optional — commented out by default |
| `[build-system]` | Build backend declaration | Required |
| `[tool.hatch.build.targets.wheel]` | Tells hatchling which directories to package | Required with hatchling |
| `[dependency-groups]` | Local-only dev/docs/notebook dependencies (not published) | Optional |
| `[tool.uv]` | uv-specific project config (Python management, index config) | Optional |
| `[tool.ruff]` | Linter and formatter configuration | Optional |
| `[tool.ruff.lint]` | Lint rule selection and per-file overrides | Optional |
| `[tool.ruff.format]` | Formatter options | Optional |
| `[tool.mypy]` | Static type checker configuration | Optional |
| `[tool.pytest.ini_options]` | Test runner configuration | Optional |
| `[tool.coverage.run]` | Coverage measurement configuration | Optional |
| `[tool.coverage.report]` | Coverage reporting thresholds | Optional |
| `[tool.interrogate]` | Docstring coverage enforcement | Optional |
| `[tool.codespell]` | Spell-checking for source files | Optional |
| `[tool.tox]` | Multi-Python-version test matrix | Optional |
| `[tool.deptry]` | Dependency hygiene (unused, missing, transitive) | Optional |

---

## `[project]`

```toml
[project]
name = "{{repo_name}}"
version = "0.1.0"
description = "{{description}}"
authors = [{ name = "{{author}}", email = "{{author_email}}" }]
readme = "README.md"
keywords = []
requires-python = ">={{python_version}},<4"  # Update upper bound when Python 4 is released
license = { text = "MIT" }
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = []
```

**`name`** — the distribution name as it appears on PyPI. Use hyphens (e.g. `my-library`), not underscores. This is separate from the importable package name.

**`version`** — starts at `0.1.0`. Follows [SemVer](https://semver.org/). If you want dynamic versioning from git tags, switch to `dynamic = ["version"]` and configure `[tool.hatch.version]`.

**`requires-python`** — the version constraint pip and uv enforce when installing.

> **Fix applied (PLAN.md item 7 — Low):** The upper bound `<4` is intentional. An unbounded `>=X.Y` constraint claims compatibility with all future Python versions including 4.x. This may not be true and can confuse installers. Tighten or loosen when Python 4 is released or if you have tested beyond the current bound.

**`license`** — inline text form is the simplest. Alternatively use `{ file = "LICENSE" }` to point at a license file.

**`classifiers`** — trove classifiers used by PyPI for search and display. The three included here are a minimal baseline. Extend with specific Python version classifiers (e.g. `"Programming Language :: Python :: 3.12"`) once you know your supported range.

**`dependencies`** — runtime dependencies only. Keep this list minimal: list what your package imports, not what the dev toolchain needs. Dev tools go in `[dependency-groups]`.

---

## `[project.urls]`

```toml
[project.urls]
Homepage = "https://github.com/{{github_org}}/{{repo_name}}"
Repository = "https://github.com/{{github_org}}/{{repo_name}}"
```

Arbitrary key-value pairs displayed as links on the PyPI project page. Common additions: `Documentation`, `Changelog`, `Bug Tracker`. The keys are display labels; the values must be valid URLs.

---

## `[project.scripts]`

```toml
# [project.scripts]
# {{repo_name}} = "{{package_name}}.cli:main"
```

Commented out by default because not all packages ship a CLI.

**When to uncomment:** when your package provides a command-line tool.

**Value format:** `"<importable.module.path>:<callable>"`. The part before `:` is a dotted import path; the part after is the function to call when the command runs. In the template, `{{package_name}}.cli:main` means: import `my_package.cli`, call `main()`.

The key (left of `=`) is the command name the user types in their shell. It does not have to match the package name, but it usually does.

---

## `[build-system]`

```toml
[build-system]
requires = ["hatchling"]  # Installed by the build frontend in an isolated env; not needed in the venv
build-backend = "hatchling.build"
# Alternatives: setuptools, flit_core, pdm-backend
```

**`requires`** — packages the build frontend (pip, uv) installs into a temporary isolated environment before building. This is **not** the same as the project's runtime or development dependencies.

> **Fix applied (PLAN.md item 12 — Enhancement):** `hatchling` is listed here but intentionally absent from `[dependency-groups].dev`. It does not need to be in your virtual environment. The build frontend handles it. Developers who notice the discrepancy sometimes add it to dev deps unnecessarily — the comment prevents this.

**`build-backend`** — the Python module that implements the [PEP 517](https://peps.python.org/pep-0517/) build interface.

**Alternatives table:**

| Backend | Package in `requires` | Notes |
|---|---|---|
| Hatchling (default) | `hatchling` | Modern, fast, good src-layout support |
| setuptools | `setuptools` | Most widely supported, largest ecosystem |
| flit_core | `flit_core` | Minimal, pure-Python packages only |
| pdm-backend | `pdm-backend` | PDM project ecosystem; full-featured |

Switch backends by replacing both `requires` and `build-backend`. The rest of `pyproject.toml` stays the same (tool sections are backend-agnostic).

---

## `[tool.hatch.build.targets.wheel]`

```toml
[tool.hatch.build.targets.wheel]
# src layout: packages = ["src/{{package_name}}"]
# flat layout: packages = ["{{package_name}}"]
packages = ["src/{{package_name}}"]
```

**`packages`** — tells hatchling which directories to include in the wheel. Without this, hatchling uses auto-discovery, which can include test files or other directories unintentionally.

**src layout** (`src/my_package/`) — package lives one level deeper. The path must include the `src/` prefix: `["src/my_package"]`. This is the template default.

**Flat layout** (`my_package/` at the root) — simpler directory structure but more risk of accidental imports during development. Use `["my_package"]` without the prefix.

If you change the layout, update this setting and also `[tool.mypy]`, `[tool.coverage.run]`, and the pytest `--cov` configuration to match (see those sections below).

---

## `[dependency-groups]`

```toml
[dependency-groups]
dev = [
    "ruff>=0.9",
    "mypy>=1.14",
    "deptry>=0.23",
    "pytest>=8.3",
    "pytest-cov>=6.0",
    "pre-commit>=4.0",
    "interrogate>=1.7",
    "codespell>=2.3",
    "tox-uv>=1.0",
]
docs = [
    "mkdocs>=1.6",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.27",
]
notebooks = [
    "nbqa>=1.9",
    "ipykernel>=6.29",
]
```

**Dependency groups vs `[project.optional-dependencies]`:** Groups defined here are local-only. They are never published to PyPI and never appear in package metadata. Use `[project.optional-dependencies]` when you want extras consumers can install (`pip install my-package[dev]`). Use `[dependency-groups]` for tooling that is only relevant inside this repository.

**Installation with uv:**
```bash
uv sync --group dev           # install the dev group
uv sync --group docs          # install the docs group
uv sync --group dev --group docs  # install multiple groups
```

**`dev` group — what each tool does:**

| Package | Role |
|---|---|
| `ruff` | Linter and formatter |
| `mypy` | Static type checker |
| `deptry` | Dependency hygiene (unused, missing, transitive) |
| `pytest` + `pytest-cov` | Test runner with coverage |
| `pre-commit` | Git hook manager |
| `interrogate` | Docstring coverage enforcer |
| `codespell` | Spell checker |
| `tox-uv` | uv-native tox backend for multi-version testing |

**`docs` group** — MkDocs with the Material theme and mkdocstrings for auto-generated API docs from docstrings.

**`notebooks` group** — `nbqa` runs ruff/mypy inside notebooks; `ipykernel` registers the virtualenv as a Jupyter kernel.

---

## `[tool.uv]`

```toml
[tool.uv]
# managed = true  # Uncomment to signal this project uses uv-managed Python
# python-preference = "managed-only"  # Prefer uv-installed Pythons over system ones
```

> **Fix applied (PLAN.md item 10 — Enhancement):** Section added so developers know where uv-level project config lives. Both options are commented out because they are environment-specific choices.

**`managed = true`** — marks the project as using uv-managed Python. Useful as a signal in CI or team environments where multiple Python managers might be present.

**`python-preference = "managed-only"`** — tells uv to use only the Pythons it installed (via `uv python install`), ignoring system Pythons. Removes a common source of environment contamination.

**Index configuration** (commented out above `[tool.ruff]` in the file):

```toml
# [tool.uv.sources]
# private-package = { index = "private-index" }

# [[tool.uv.indexes]]
# name = "private-index"
# url = "https://pypi.example.com/simple/"
# explicit = true
```

Use these when you have a private package index. `explicit = true` means uv only uses that index for packages explicitly routed to it — it does not replace PyPI.

---

## `[tool.ruff]`

```toml
[tool.ruff]
line-length = 100
target-version = "py{{python_version_nodot}}"
exclude = [".venv", "dist", "build"]
```

**`line-length = 100`** — used by both the linter (E501 detection) and the formatter (wrapping target). 100 is a common compromise between the PEP 8 default of 79 and the "no limit" extreme.

**`target-version`** — controls which Python syntax ruff treats as valid and which pyupgrade (`UP`) suggestions are offered. Set to match `requires-python`.

**`exclude`** — directories ruff skips entirely. Always include `.venv`, `dist`, and `build` to avoid linting generated or vendored code.

---

## `[tool.ruff.lint]`

```toml
[tool.ruff.lint]
# D (pydocstring) rules intentionally omitted — interrogate enforces docstring coverage
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "A",    # flake8-builtins
    "C4",   # flake8-comprehensions
    "C90",  # mccabe complexity
    "S",    # flake8-bandit (security)
    "SIM",  # flake8-simplify
    "TRY",  # tryceratops
    "PGH",  # pygrep-hooks
    "RUF",  # ruff-specific rules
    "YTT",  # flake8-2020
    "T10",  # flake8-debugger
]
ignore = [
    "E501",   # line length — handled by the formatter, not the linter
    "E731",   # lambda assignment — sometimes more readable than a def
    "TRY003", # long messages outside exception class — too restrictive for library code
    "TRY004", # prefer TypeError — breaks existing idioms
    "SIM108", # ternary operator preference — not always more readable
]
```

**Rule groups — brief rationale:**

| Code | Origin | What it catches |
|---|---|---|
| `E` / `W` | pycodestyle | PEP 8 style errors and warnings |
| `F` | pyflakes | Undefined names, unused imports, redefinitions |
| `I` | isort | Import ordering and grouping |
| `UP` | pyupgrade | Syntax that can be modernised for the target Python version |
| `B` | flake8-bugbear | Likely bugs and design problems (opinionated) |
| `A` | flake8-builtins | Variable names shadowing Python builtins |
| `C4` | flake8-comprehensions | Unnecessary list/set/dict constructions |
| `C90` | mccabe | Functions that exceed cyclomatic complexity threshold |
| `S` | flake8-bandit | Common security anti-patterns |
| `SIM` | flake8-simplify | Code that can be simplified (e.g. redundant conditions) |
| `TRY` | tryceratops | Exception handling anti-patterns |
| `PGH` | pygrep-hooks | Regex-based checks (e.g. broad `type: ignore`) |
| `RUF` | ruff-specific | Rules unique to ruff (not from any upstream flake8 plugin) |
| `YTT` | flake8-2020 | `sys.version` comparisons that break on Python 3.10+ |
| `T10` | flake8-debugger | `pdb` / `breakpoint()` left in committed code |

**Why `D` rules are absent:**

> **Fix applied (PLAN.md item 6 — Low):** `D` (pydocstring conventions) rules are intentionally omitted. `interrogate` already enforces that docstrings exist. Running both would produce overlapping and sometimes conflicting feedback. The comment on `select` preserves this intent for future maintainers.

**Ignored rules rationale:**
- `E501` — the formatter handles line length; the linter firing on the same thing is noise.
- `E731` — lambda assignments are sometimes the clearest way to express a simple transform.
- `TRY003` / `TRY004` — both are opinionated in ways that conflict with common library idioms.
- `SIM108` — ternary operators are not always more readable than `if/else` blocks.

### `[tool.ruff.lint.per-file-ignores]`

```toml
[tool.ruff.lint.per-file-ignores]
"tests/**" = [
    "S101",  # assert statements are normal in tests
    "S105",  # hardcoded password string — test fixtures use dummy credentials
    "S106",  # hardcoded password in function arg — same reason
]
```

Tests legitimately use `assert`, hardcoded dummy credentials, and other patterns that bandit (`S`) flags in production code. These ignores are scoped to `tests/` only.

### `[tool.ruff.format]`

```toml
[tool.ruff.format]
# preview = true  # Enables unstable rules; re-evaluate on each ruff release
```

> **Fix applied (PLAN.md item 5 — Medium):** `preview = true` is commented out. Preview mode enables formatting rules that are not yet stable. A ruff version bump could reformat the entire codebase with no functional change, polluting diffs and blame history. If you need a specific preview rule, enable it by rule ID rather than enabling all of them.

With no options set, the formatter uses ruff's defaults: double quotes, 4-space indentation, trailing commas, wrapping at the configured `line-length`.

---

## `[tool.mypy]`

```toml
[tool.mypy]
python_version = "{{python_version}}"
strict = true
disallow_any_unimported = true  # strict doesn't cover this; prevents silent Any from missing stubs
warn_unused_ignores = true      # surfaces stale type: ignore comments after upstream fixes
show_error_codes = true         # enables targeted type: ignore[code] suppression
no_implicit_optional = true     # None defaults must be explicitly typed as Optional[T]
warn_return_any = true
warn_unused_configs = true
mypy_path = ["src"]
# src layout: packages = ["{{package_name}}"]
packages = ["{{package_name}}"]
```

> **Critical fix (PLAN.md item 2):** `mypy_path = ["src"]` is required for src layout. Without it, mypy looks for `{{package_name}}` at the project root and cannot find it. The combination of `mypy_path = ["src"]` + `packages = ["{{package_name}}"]` is correct: mypy_path extends the module search path, and packages names the package to check.

**`strict = true`** — enables a large set of checks including `disallow_untyped_defs`, `disallow_incomplete_defs`, `check_untyped_defs`, `no_implicit_reexport`, and others. See `mypy --help` for the full list.

**`disallow_any_unimported = true`** — not included in `strict`. When an imported type lacks stubs, mypy silently falls back to `Any`. This option makes that an error instead. Add the relevant `-stubs` package to `[dependency-groups].dev` when this fires.

**`warn_unused_ignores = true`** — `# type: ignore` comments that no longer suppress any error (because the upstream library fixed its types) are flagged. Keeps suppressions honest.

**`show_error_codes = true`** — mypy error output includes codes like `[assignment]` or `[arg-type]`. Enables targeted suppression: `# type: ignore[arg-type]` instead of silencing everything.

**`no_implicit_optional = true`** — a function signature like `def f(x: str = None)` is treated as `Optional[str]` without this setting. With it, you must write `Optional[str]` explicitly.

---

## `[tool.pytest.ini_options]`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov --cov-report=term-missing --cov-report=xml"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

> **Critical fix (PLAN.md item 3):** `--cov` is used without an argument. Previously, `--cov={{package_name}}` pointed at the project root, which fails silently with src layout (the package is not there). Without an argument, `--cov` defers to `[tool.coverage.run] source` for the measurement target. That setting is the single source of truth for what gets measured.

**`testpaths`** — limits pytest discovery to the `tests/` directory. Without this, pytest would also crawl `src/`, `docs/`, and other directories.

**`--cov-report=term-missing`** — prints a table in the terminal showing which specific lines are not covered. `--cov-report=xml` writes `coverage.xml` for CI tools (e.g. Codecov, SonarQube).

**`markers`** — declares custom markers to avoid `PytestUnknownMarkWarning`. Use them to selectively run subsets:
```bash
pytest -m "not slow"         # skip slow tests
pytest -m integration        # run only integration tests
```

---

## `[tool.coverage.run]` and `[tool.coverage.report]`

```toml
[tool.coverage.run]
source = ["src/{{package_name}}"]
omit = ["tests/*"]

[tool.coverage.report]
fail_under = 80
```

> **Critical fix (PLAN.md item 3):** `source = ["src/{{package_name}}"]` includes the `src/` prefix. With a flat layout, this would be `["{{package_name}}"]`. The `src/` prefix is required for src layout — without it, coverage measures nothing and silently reports 0% or raises a `ModuleNotFoundError`.

**`omit`** — prevents test files from inflating the coverage percentage.

**`fail_under = 80`** — `pytest --cov` exits with a non-zero status if branch coverage falls below 80%. Edit this value directly to change it. Remove this key entirely if you want coverage reporting without enforcement.

---

## `[tool.interrogate]`

```toml
[tool.interrogate]
ignore-init-method = true   # class docstring covers __init__
ignore-init-module = true   # __init__.py files rarely benefit from module docstrings
ignore-magic = true         # __repr__, __str__ etc. are self-documenting by convention
ignore-semiprivate = false  # set true to skip _private methods
ignore-private = false      # set true to skip __dunder methods beyond magic
ignore-property-decorators = false
ignore-module = false
ignore-nested-functions = false
ignore-setters = false
fail-under = 80
verbose = 0
quiet = false
whitelist-regex = []
color = true
```

**What interrogate enforces:** that every public function, class, and module has a docstring. It counts coverage as a percentage and fails if the threshold is not met.

> **Fix applied (PLAN.md item 9 — Low):** `ignore-semiprivate` and `ignore-private` are now present with explicit values and comments. The defaults (`false`) require docstrings on `_private` and `__dunder` methods beyond the magic list. This is stricter than most teams expect. Set both to `true` if you only want to enforce docstrings on the public API.

**`ignore-init-method = true`** — the class-level docstring is the appropriate place to document `__init__`; requiring a separate docstring on the method is redundant.

**`ignore-magic = true`** — magic methods like `__repr__`, `__str__`, `__len__` have self-evident purpose from their names; docstrings add little value.

**`fail-under = 80`** — same threshold pattern as coverage. Run `interrogate src/` to see the breakdown before adjusting.

**Ruff `D` rules vs interrogate:** Ruff's `D` rules check docstring *style and format*; interrogate checks *presence*. The template uses interrogate for presence (simpler, focused) and omits `D` from ruff to avoid double-reporting.

---

## `[tool.codespell]`

```toml
[tool.codespell]
skip = ".git,*.lock,*.toml,dist,build,.venv"
# ignore-words-list = "exemple,woord"
count = true
quiet-level = 3
```

**What codespell checks:** source files for common spelling mistakes using a built-in dictionary. It catches typos in comments, docstrings, and string literals.

> **Fix applied (PLAN.md item 4 — High):** `ignore-words-list` is now commented out rather than set to `""`. An empty string `""` is not a valid entry and may be treated as a literal ignore pattern, causing unexpected behaviour. To ignore specific words (e.g. domain jargon that looks like a typo), uncomment the line and replace the examples with your actual words.

**`skip`** — comma-separated glob patterns. Lock files and TOML configs are skipped because they often contain hashes, URLs, and machine-generated identifiers that trigger false positives.

**`count = true`** — prints the total number of errors found.

**`quiet-level = 3`** — suppresses informational output; only prints actual errors.

---

## `[tool.tox]`

```toml
[tool.tox]
# Requires py311/py312/py313 to be installed: uv python install 3.11 3.12 3.13
legacy_tox_ini = """
[tox]
envlist = py311, py312, py313
isolated_build = true

[testenv]
extras = dev
commands = pytest {posargs}
"""
```

**What tox does:** creates isolated virtual environments for each Python version in `envlist` and runs the test suite in each. Catches bugs that only manifest on specific Python versions.

> **Fix applied (PLAN.md item 8 — Low):** The prerequisite is now documented in the comment. Tox will fail silently or with a confusing error if the required interpreters are not installed. Install them first:
> ```bash
> uv python install 3.11 3.12 3.13
> ```
> Then run `tox`. Use `pytest` directly for day-to-day development; tox is for pre-release multi-version verification.

**`isolated_build = true`** — tox builds the package in an isolated environment (PEP 517) before installing it into each test environment. This tests the published package, not just the source tree.

**`extras = dev`** — installs the `dev` dependency group into each test environment. Note: with `[dependency-groups]`, the correct key may depend on the tox-uv version. Verify against tox-uv documentation if this causes issues.

**`{posargs}`** — allows passing arguments through tox to pytest, e.g. `tox -- -k test_foo`.

**`tox-uv`** — the `tox-uv` package in `[dependency-groups].dev` replaces tox's default pip-based environment management with uv, making environment creation significantly faster.

---

## `[tool.deptry]`

```toml
[tool.deptry]
root_packages = ["{{package_name}}"]
```

**What deptry checks:** scans your source code and `pyproject.toml` to detect:
- **Missing dependencies** — imported in code but not listed in `[project.dependencies]`
- **Unused dependencies** — listed in `[project.dependencies]` but never imported
- **Transitive dependencies** — imported directly but only available because another package pulls them in (fragile — they can disappear when the parent package is updated)
- **Misplaced dev dependencies** — dev tools accidentally listed in runtime `dependencies`

**`root_packages`** — the package(s) deptry should scan. Points at the importable package name, not the directory path.

Run deptry manually or add it to a pre-commit hook:
```bash
uv run deptry src/
```

Deptry complements `ruff` (`F401` catches unused imports at the file level) by checking the project-level dependency declaration.
