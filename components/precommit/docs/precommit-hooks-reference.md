# pre-commit Hooks Reference

Per-hook detail: what each hook catches, how to install it, and how to run it manually. For the quick overview table and install instructions, see the component `README.md`.

---

## Hooks in detail

### Stage: commit

Fast checks. Run on every `git commit`. Auto-fix where possible; block where not.

---

#### `clean-cache-files`

Removes generated and temporary directories before the commit is staged. Prevents cache artifacts from being accidentally committed and keeps the tree clean.

**Catches:** `__pycache__/`, `.DS_Store`, `.ruff_cache/`, `.ipynb_checkpoints/`, `*.egg-info/`, `catboost_info/`. Always runs; not filtered by file type. Skips `.venv/` entirely.

**Install:** No installation needed — runs as a plain bash script via the system shell.

**Run manually:**

```bash
pre-commit run clean-cache-files --all-files
```

---

#### `uv-lock-check`

Verifies that `uv.lock` is consistent with `pyproject.toml`. Only activates when either file is staged — zero overhead on unrelated commits.

**Catches:** Editing `pyproject.toml` (adding, removing, or changing a dependency) without regenerating the lockfile. If stale, the commit is blocked.

**Fix when it fires:**

```bash
uv lock        # regenerate the lockfile
git add uv.lock
git commit
```

**Install:** `uv` is the project's package manager — already available if you're using this bootstrap.

**Run manually:**

```bash
uv lock --locked    # exits non-zero if lockfile is stale, zero if consistent
```

---

#### `file hygiene`

A group of lightweight checks from [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks). Most auto-fix silently and re-stage the modified files.

| Hook ID                                                  | Auto-fixes? | What it catches                                                              |
| -------------------------------------------------------- | ----------- | ---------------------------------------------------------------------------- |
| `trailing-whitespace`                                    | Yes         | Trailing spaces; preserves intentional Markdown line breaks                  |
| `end-of-file-fixer`                                      | Yes         | Files missing a trailing newline                                             |
| `check-added-large-files`                                | No — blocks | Files over 500 KB. Adjust `--maxkb` per project; use Git LFS for binaries    |
| `mixed-line-ending`                                      | Yes         | CRLF/LF inconsistencies (`--fix=auto` detects the predominant style)         |
| `check-case-conflict`                                    | No — blocks | `File.py` vs `file.py` collisions that break on case-insensitive filesystems |
| `check-merge-conflict`                                   | No — blocks | `<<<<<<<` / `=======` / `>>>>>>>` markers left in source files               |
| `check-executables-have-shebangs`                        | No — blocks | `chmod +x` files missing a `#!/usr/bin/env ...` line                         |
| `check-shebang-scripts-are-executable`                   | No — blocks | `#!` scripts not marked executable                                           |
| `debug-statements`                                       | No — blocks | `breakpoint()`, `import pdb`, `pdb.set_trace()` left in committed code       |
| `check-docstring-first`                                  | No — blocks | Module docstring appearing after imports or other statements                 |
| `check-yaml` / `check-toml` / `check-json` / `check-xml` | No — blocks | Syntax errors in config files                                                |
| `pretty-format-json`                                     | Yes         | JSON indented with 2 spaces, key order preserved. Excludes `.ipynb`.         |

**Install:** Managed automatically by pre-commit — no separate installation needed.

**Run a specific check manually:**

```bash
pre-commit run trailing-whitespace --all-files
pre-commit run end-of-file-fixer --all-files
pre-commit run check-yaml --all-files
pre-commit run pretty-format-json --all-files
# Replace with any hook ID from the table above
```

---

#### `ruff-check` and `ruff-format`

Ruff handles Python **linting** and **formatting** in one tool.

**What a linter does:** Statically analyses source code without running it — flags errors, bugs, style violations, and suspicious patterns. Ruff's linter is the equivalent of running flake8, isort, and a dozen plugins simultaneously.

**What a formatter does:** Automatically rewrites code to match a consistent style — indentation, quote style, line wrapping, trailing commas. No judgment on logic; purely cosmetic and structural. Ruff's formatter is the equivalent of Black.

`ruff-check` runs on all `.py` files and auto-fixes what it can (`--fix`). `--exit-non-zero-on-fix` means the hook fails when it makes changes — you see what was fixed before re-committing. A second `ruff-check` pass runs separately on `.ipynb` notebooks.

`ruff-format` reformats all `.py` files to the configured style.

Both hooks read their configuration from `[tool.ruff]` in `pyproject.toml`.

> Keep the `rev:` pin in `.pre-commit-config.yaml` in sync with `ruff>=...` in `[dependency-groups].dev` in `pyproject.toml`. Mismatched versions can produce different lint results between `pre-commit run` and `uv run ruff`.

**Install:** Managed by pre-commit automatically. Also available as a dev dependency:

```bash
uv add --dev ruff    # if not already in pyproject.toml
```

**Run manually:**

```bash
uv run ruff check . --fix                    # lint with auto-fix
uv run ruff check . --fix --unsafe-fixes     # include unsafe fixes
uv run ruff format .                         # format all files
uv run ruff check . --output-format=concise  # compact CI-style output
```

---

#### `nbstripout`

Strips cell outputs and execution counts from Jupyter notebooks before committing.

**Why it matters:** Notebook outputs embed rendered data, images, and execution counts that can inflate diffs to thousands of lines, make reviews unreadable, and inadvertently leak intermediate data or model outputs. Stripping them means diffs show only code changes.

**Remove or comment this hook out** if the project contains no `.ipynb` files.

**Install:** Managed by pre-commit automatically. Also installable directly:

```bash
uv add --dev nbstripout
# or: pip install nbstripout
```

**Run manually:**

```bash
nbstripout notebook.ipynb                      # strip a single notebook
find . -name "*.ipynb" | xargs nbstripout      # strip all notebooks
nbstripout --dry-run notebook.ipynb            # preview without modifying
pre-commit run nbstripout --all-files
```

---

#### `interrogate`

Checks that every public function, class, and module has a docstring. Fails if coverage falls below the configured threshold.

**Catches:** Missing docstrings on the public API surface. Configured at 80% (`--fail-under=80`). Ignores `__init__` methods, `__init__.py` module docstrings, and magic methods — the class docstring covers those.

Lower the threshold for early-stage projects; raise it as the public API stabilises.

**Install:** Managed by pre-commit automatically. Also in `[dependency-groups].dev`:

```bash
uv add --dev interrogate    # if not already present
```

**Run manually:**

```bash
uv run interrogate src/ -vv               # verbose — shows exactly what's missing
uv run interrogate src/ --fail-under=80   # matches the configured threshold
```

---

#### `markdownlint-cli2`

Lints Markdown files for structural and style consistency and auto-fixes what it can.

**Catches:** Heading hierarchy violations, inconsistent list markers, missing blank lines around headings, trailing spaces, bare URLs, and other [markdownlint rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md).

**Install:** Pre-commit installs this automatically via its `node` language handler — no manual step needed if Node.js LTS is available on the system (`nvm` or a system install). If the hook fails during pre-commit install, install Node.js first:

```bash
brew install node        # macOS
nvm install --lts        # with nvm
```

**Run manually:**

```bash
npx markdownlint-cli2 "**/*.md"          # lint
npx markdownlint-cli2 --fix "**/*.md"    # lint and auto-fix
pre-commit run markdownlint-cli2 --all-files
```

---

#### `codespell`

Detects common spelling mistakes in source code, comments, docstrings, and documentation. Auto-corrects in-place.

**Catches:** Typos matching codespell's built-in dictionary — common misspellings in identifiers, comments, and prose. Skips lock files, TOML, dist, and `.venv` by default.

> `--write-changes` modifies files silently during the commit hook. After a commit where codespell fires, you may see files re-staged automatically. This is intentional and mirrors how `ruff --fix` works.

To ignore project-specific terms that look like typos, add them to `[tool.codespell] ignore-words-list` in `pyproject.toml`.

**Install:** Managed by pre-commit automatically. Also in `[dependency-groups].dev`:

```bash
uv add --dev codespell    # if not already present
```

**Run manually:**

```bash
uv run codespell .                                       # report only
uv run codespell . --write-changes                       # report and auto-correct
uv run codespell . --ignore-words-list "myterm,other"    # ignore specific words
```

---

#### `gitleaks`

Scans staged content for secrets, API keys, tokens, and credentials using pattern matching.

**Catches:** AWS keys, GitHub tokens, private keys, generic high-entropy strings, and hundreds of other credential patterns from [gitleaks' built-in ruleset](https://github.com/gitleaks/gitleaks/tree/master/config). Redacts found values in output (`--redact`) to avoid leaking them further via terminal logs.

If you have a false positive (e.g. a test fixture with a dummy token), add a `gitleaks:allow` inline comment or create a `.gitleaksignore` file.

> **Requires `gitleaks` installed on the host** — pre-commit's `repo: https://github.com/gitleaks/gitleaks` hook type manages this via Go, but you may also install it directly:

**Install:**

```bash
brew install gitleaks                  # macOS
# Linux: https://github.com/gitleaks/gitleaks#installing
# or: go install github.com/zricethezav/gitleaks/v8@latest
```

**Run manually:**

```bash
gitleaks detect --report-format=table --redact --source .
gitleaks detect --report-format=table --redact --no-git    # scan all files, not just git history
pre-commit run gitleaks --all-files
```

---

#### `deptry`

Analyses source code against `pyproject.toml` to surface dependency declaration problems.

**Catches:**

| Code     | What it flags                                                                                          | Enforced?                                                        |
| -------- | ------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| `DEP001` | Imported in code but not declared in `[project.dependencies]`                                          | Yes                                                              |
| `DEP003` | Imported directly but only available as a transitive dependency (fragile — can break on parent update) | Yes                                                              |
| `DEP004` | Dev tooling accidentally declared in runtime `dependencies`                                            | Yes                                                              |
| `DEP002` | Declared in `dependencies` but never imported                                                          | No — ignored due to false positives from optional/lazy imports   |

**Install:** Managed by pre-commit automatically. Also in `[dependency-groups].dev`:

```bash
uv add --dev deptry    # if not already present
```

**Run manually:**

```bash
uv run deptry src/
uv run deptry src/ --ignore DEP002    # same as the hook default
```

---

#### `sqlfluff`

Lints and auto-formats SQL files for style and correctness.

**Catches:** Inconsistent capitalisation, formatting violations, aliasing issues, and SQL anti-patterns. The `--dialect` setting controls which SQL variant is expected.

**Remove or comment this hook out** if the project contains no SQL files. When keeping it, set `--dialect` to match your database engine in `.pre-commit-config.yaml`:

```yaml
args: [--dialect, postgres] # or: ansi, mysql, bigquery, snowflake, …
```

**Install:** Managed by pre-commit automatically. Also installable as a dev dependency:

```bash
uv add --dev sqlfluff
```

**Run manually:**

```bash
uv run sqlfluff lint . --dialect ansi        # lint
uv run sqlfluff fix . --dialect ansi         # lint and auto-fix
uv run sqlfluff lint path/to/query.sql       # single file
pre-commit run sqlfluff-lint --all-files
pre-commit run sqlfluff-fix --all-files
```

---

### Stage: commit-msg

Runs after the commit message is typed, before the commit is recorded. Only one hook; focused solely on message format.

---

#### `conventional-pre-commit`

Enforces the [Conventional Commits](https://www.conventionalcommits.org) format on every commit message.

**Why Conventional Commits:** A structured message format (`type(scope): description`) enables automated changelog generation, semantic versioning, and makes `git log` scannable. Tools like `release-please` and `semantic-release` depend on it.

**Required format:** `<type>(<optional scope>): <description>`

**Allowed types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`, `revert`

**Valid examples:**

```
feat: add user authentication
fix(api): handle null response from upstream
docs: update install steps in README
chore!: drop Python 3.10 support
```

**Catches:** Messages not starting with a recognised type, missing colon, wrong casing, unrecognised type prefixes.

**Install:** Managed by pre-commit automatically — no separate install needed.

**There is no useful standalone equivalent** — this hook only makes sense in the context of a real commit message. To test a message format interactively:

```bash
echo "feat: my message" | pre-commit run conventional-pre-commit --commit-msg-filename /dev/stdin
```

---

### Stage: push

Slower or network-dependent checks. Run once on `git push`, not on every commit — designed so the development loop stays fast.

---

#### `mypy`

Runs static **type checking** across the full codebase.

**What a type checker does:** Analyses type annotations to verify that values are used consistently — that a function expecting a `str` doesn't receive an `int`, that return types match declarations, that optional values are handled before use. It catches an entire class of bugs that linters and tests typically miss, without running the code.

**Catches:** Type mismatches, missing annotations (in strict mode), incorrect argument types, incompatible assignments, use of possibly-`None` values without guards.

If mypy reports `error: Library stubs not installed for "X"`, add the relevant stubs package to `additional_dependencies` in the hook entry:

```yaml
additional_dependencies: [types-requests, types-PyYAML]
```

**Install:** Managed by pre-commit automatically via `mirrors-mypy`. Also in `[dependency-groups].dev`:

```bash
uv add --dev mypy    # if not already present
```

**Run manually:**

```bash
uv run mypy src/
uv run mypy src/ --show-error-codes          # include error codes (enables targeted suppression)
uv run mypy src/ --ignore-missing-imports    # suppress stubs-not-found errors
pre-commit run mypy --all-files --hook-stage push
```

---

#### `semgrep`

Advanced static analysis for security vulnerabilities and code quality anti-patterns.

**Catches:** SQL injection patterns, unsafe deserialisation, hardcoded credentials, insecure cryptography, OWASP Top 10 patterns, and Python-specific anti-patterns via the `p/python` rule set from the Semgrep Registry.

> **Requires network** to fetch the rule set on first run. Subsequent runs use the cached version. Skip when offline:
>
> ```bash
> SKIP=semgrep git push
> ```

**Install:** Managed by pre-commit automatically. Also installable directly:

```bash
pip install semgrep
# or: brew install semgrep   (macOS)
```

**Run manually:**

```bash
semgrep --config=p/python --error .    # fail on findings
semgrep --config=p/python .            # report only, don't fail
pre-commit run semgrep --all-files --hook-stage push
```

---

#### `trivy-config`

Scans Infrastructure-as-Code and configuration files for misconfigurations and known vulnerabilities.

**Catches:** Misconfigured Dockerfiles, Kubernetes manifests, Terraform configs, and other IaC files at `HIGH` or `CRITICAL` severity using Trivy's built-in misconfiguration rules.

If contributors may not have trivy installed locally, skip it with `SKIP=trivy-config git push` and run it in CI instead.

> **Requires `trivy` installed on the host** — pre-commit cannot manage this automatically.

**Install:**

```bash
brew install trivy                   # macOS
# Linux: https://aquasecurity.github.io/trivy/latest/getting-started/installation/
```

**Run manually:**

```bash
trivy config --exit-code 1 --severity HIGH,CRITICAL .    # fail on findings
trivy config --severity HIGH,CRITICAL .                  # report only
pre-commit run trivy-config --all-files --hook-stage push
```

---

## Running hooks manually

Run any hook or stage outside the commit cycle — useful for a full check before opening a PR, or to diagnose a specific hook.

```bash
# All commit-stage hooks, all files
pre-commit run --all-files

# All push-stage hooks, all files
pre-commit run --hook-stage push --all-files

# A single hook by ID
pre-commit run ruff-check --all-files
pre-commit run mypy --all-files

# On specific files only
pre-commit run ruff-check --files src/mypackage/core.py src/mypackage/utils.py
```

---

## Skipping and bypassing

### Skip one hook for a single commit or push

```bash
SKIP=gitleaks git commit -m "chore: add test fixture with dummy token"
SKIP=semgrep git push                   # e.g. when offline
SKIP=trivy-config git push              # if trivy is not installed locally
SKIP=ruff-check,mypy git commit         # multiple hooks, comma-separated
```

`SKIP` is an environment variable — the commit or push proceeds; only the named hook IDs are bypassed. All other hooks still run.

### Bypass all hooks

```bash
git commit --no-verify -m "wip: quick save"
git push --no-verify
```

`--no-verify` skips every hook entirely. Use only for work-in-progress saves or when you understand exactly why a hook is failing. **Never use it to silence a security finding.**

---

## Updating hooks

### Bump all hook versions to latest

```bash
pre-commit autoupdate
```

Rewrites every `rev:` pin in `.pre-commit-config.yaml` to the latest release tag. Review the diff before committing — minor version bumps sometimes introduce breaking rule changes.

> After `autoupdate`, verify that the ruff `rev:` matches the `ruff>=...` constraint in `[dependency-groups].dev` in `pyproject.toml`. Mismatched versions mean `pre-commit run ruff-check` and `uv run ruff check` can produce different results.

### Re-install after config changes

Any change to `.pre-commit-config.yaml` — adding, removing, or updating a hook — requires reinstalling:

```bash
pre-commit install \
  --hook-type pre-commit \
  --hook-type commit-msg \
  --hook-type pre-push
```

### Clear the hook cache

If hooks behave unexpectedly after an update or a Python version change:

```bash
pre-commit clean     # removes all cached hook environments
pre-commit install \
  --hook-type pre-commit \
  --hook-type commit-msg \
  --hook-type pre-push
```

---

## Host dependencies

Most hooks are managed entirely by pre-commit. The following require tools installed on the host machine:

| Tool       | Hook                | Why pre-commit can't manage it                                               | Install                                                                                                          |
| ---------- | ------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `gitleaks` | `gitleaks`          | Uses a Go binary not distributable via pip/node                              | `brew install gitleaks` (macOS) / [docs](https://github.com/gitleaks/gitleaks#installing)                        |
| `trivy`    | `trivy-config`      | System binary with OS-level dependencies                                     | `brew install trivy` (macOS) / [docs](https://aquasecurity.github.io/trivy/latest/getting-started/installation/) |
| `Node.js`  | `markdownlint-cli2` | Pre-commit installs via its `node` handler, but Node must already be present | `brew install node` or [nvm](https://github.com/nvm-sh/nvm)                                                      |
