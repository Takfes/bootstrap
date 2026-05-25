# uv Workflow Reference

uv replaces pip, pip-tools, pipx, poetry, pyenv, and virtualenv. Single tool, single lockfile, consistent environment across machines.

---

## Command decision map

| Intent | Command |
|--------|---------|
| Start a new application project | `uv init` |
| Start a new distributable library | `uv init --lib` |
| Install a specific Python version | `uv python install 3.12` |
| Pin Python version for this project | `uv python pin 3.12` |
| Create/update `.venv` from lockfile | `uv sync` |
| Run a script or tool inside the project env | `uv run <cmd>` |
| Add a runtime dependency | `uv add <pkg>` |
| Add a dev-only dependency | `uv add --dev <pkg>` |
| Remove a dependency | `uv remove <pkg>` |
| See the full dependency graph | `uv tree` |
| See what's installed (flat list) | `uv pip list` |
| Export a requirements.txt | `uv export` |
| Regenerate lockfile without installing | `uv lock` |
| Upgrade all packages to latest allowed | `uv lock --upgrade` |
| Verify lockfile is consistent (CI) | `uv lock --check` |
| Run a one-off tool without installing it | `uvx <tool>` |
| Build distribution artifacts | `uv build` |
| Publish to PyPI | `uv publish` |

---

## 1. Project scaffolding

```bash
uv init             # application project in the current directory
uv init my-project  # application project in a new subdirectory
uv init --lib       # library project with src/ layout
```

### What each creates on disk

| File | `uv init` (app) | `uv init --lib` |
|------|:--------------:|:---------------:|
| `pyproject.toml` | metadata only | metadata + `[build-system]` + src layout |
| `.python-version` | yes | yes |
| `README.md` | yes | yes |
| `.gitignore` | yes (ignores `.venv`, build artifacts) | yes |
| `hello.py` | yes | no |
| `src/<pkg>/__init__.py` | no | yes |
| `src/<pkg>/py.typed` | no | yes (PEP 561 marker) |

### When to use which

| | `uv init` | `uv init --lib` |
|--|-----------|-----------------|
| **Use for** | Scripts, one-off tools, internal apps | Packages you will distribute or import from elsewhere |
| **src layout?** | No | Yes |
| **Prevents import confusion?** | No | Yes — local folder isn't on `sys.path` by accident |
| **Build system configured?** | No | Yes |

### Multi-package src layout

By default uv assumes one package in `src/`. To include multiple packages, override the build backend. The following works with setuptools and auto-discovers everything under `src/`:

```toml
[build-system]
requires = ["setuptools >= 61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.packages.find]
where = ["src"]
```

For the default Hatch backend, list packages explicitly:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/package1", "src/package2"]
```

---

## 2. Python version management

uv manages Python installations directly — no pyenv needed.

```bash
uv python list              # show installed and available versions
uv python install 3.12      # download and install Python 3.12
uv python pin 3.11          # write/update .python-version; all uv commands use this version
uv run python --version     # confirm what version the project is actually running
```

`.python-version` is the pin file. Once it exists, every `uv run`, `uv sync`, and `uv add` command in that directory respects it.

---

## 3. `uv init` vs `uv venv`

| Command | Purpose | When to use |
|---------|---------|-------------|
| `uv init` | Scaffold a project with `pyproject.toml` | Starting any new project |
| `uv venv` | Manually create a `.venv` | Legacy workflows; IDE integration that requires `.venv` to exist before first sync |

In a normal uv project, you never need `uv venv`. Running `uv run`, `uv add`, or `uv sync` creates and manages `.venv` automatically.

---

## 4. Environment lifecycle

### `uv sync` — the "make it so" command

Reads `uv.lock`, installs every dependency into `.venv`, and installs the project itself in editable mode. Creates `.venv` if it doesn't exist.

```bash
uv sync                   # installs default + dev groups
uv sync --group docs      # also install the docs group
uv sync --all-groups      # install all defined groups
```

Run `uv sync` after:
- A `git pull` that changed `uv.lock`
- Any manual edit to `pyproject.toml`

### `uv run` — the safe execution wrapper

Runs `uv sync` internally if the environment is stale, then executes the command inside the managed environment.

```bash
uv run python script.py
uv run pytest
uv run ruff format .
uv run mypy src/
```

**`uv run` is safer than activating the virtualenv** because it guarantees the environment matches the lockfile before running. Use it by default; reserve activation for interactive sessions.

### Manual activation (interactive sessions)

```bash
source .venv/bin/activate   # standard virtualenv behaviour
```

Once activated, bare `python` and tool commands resolve to the environment. Deactivate with `deactivate`.

---

## 5. Dependency management

### Add and remove

```bash
uv add requests                     # runtime dependency
uv add --dev ruff pytest mypy       # dev-only (added to [dependency-groups] dev)
uv remove requests                  # remove and update lockfile
```

`uv add` updates `pyproject.toml`, resolves the new dependency graph, updates `uv.lock`, and syncs `.venv` — all in one step.

### `[dependency-groups]` vs `[project.optional-dependencies]`

| | `[dependency-groups]` | `[project.optional-dependencies]` |
|--|----------------------|-----------------------------------|
| **Purpose** | Local dev tooling (test, lint, docs) | Optional features for end users of your package |
| **Installed by default?** | `dev` group: yes. Others: opt-in. | No — user installs with `pip install pkg[extra]` |
| **Appears in wheel?** | No | Yes |
| **Added by `uv add --dev`** | Yes | No |

### Version pinning

In `pyproject.toml`, pin a top-level version like `requests==2.31.0` for strict control. `uv.lock` handles deep pinning of all transitive dependencies automatically — you don't need to pin sub-dependencies.

### Inspecting dependencies

```bash
uv tree           # nested dependency graph — shows why a package was installed
uv export         # flat resolved list in requirements.txt format
uv pip list       # installed packages in current .venv (pip-compatible output)
```

---

## 6. `uvx` — ephemeral runner

`uvx` is the uv equivalent of `pipx`. It runs a Python tool in a temporary, isolated environment without touching your project.

```bash
uvx ruff check .                         # run ruff without adding it to the project
uvx cowsay "Hello"                       # one-off tool
uvx --from build pyproject-build --installer uv   # run a specific package's CLI
```

### `uvx` vs `uv add --dev`

| | `uvx` | `uv add --dev` |
|--|-------|----------------|
| **Persists in project?** | No | Yes |
| **Appears in lockfile?** | No | Yes |
| **Use when** | One-off or global tools; CI steps that don't belong in the project | Tools the whole team runs repeatedly via `uv run` |

---

## 7. Locking

`uv lock` resolves the dependency graph and writes `uv.lock`. It does **not** install anything.

```bash
uv lock                   # resolve and write lockfile
uv lock --upgrade         # upgrade all packages to latest versions allowed by pyproject.toml
uv lock --check           # exit non-zero if lockfile is stale (use in CI)
```

### What makes the lockfile stale

Any manual change to `pyproject.toml` can make `uv.lock` stale:
- Adding, removing, or changing a dependency version
- Changing `requires-python`
- Changing dev dependency groups
- Running on a different platform or Python version without an existing cross-platform lock

After manual edits, run `uv lock` (to update lock only) or `uv sync` (to update lock and install).

---

## 8. Building and publishing

### `uv build`

Creates distribution artifacts in `dist/`. Does not install anything.

```bash
uv build    # produces dist/*.whl and dist/*.tar.gz
```

Run this only when you're preparing to distribute or publish. For local development, `uv sync` (editable install) is sufficient.

**Cleaning dist before a fresh build:**

```bash
uv run python -c "import shutil, os; shutil.rmtree('dist') if os.path.exists('dist') else None"
```

### Editable mode and the import trap

`uv sync` installs your project in editable mode — a live link to `src/`. Changes to source code take effect immediately without rebuilding.

**The import trap:** Python will sometimes import the local `src/` folder directly instead of the installed package, masking installation errors. To verify the package is correctly installed:

1. Run `uv sync`
2. Move to a different directory: `cd ..`
3. Run the provenance check:

```bash
uv run python -c "import my_project; print(my_project.__file__)"
```

4. Interpret the result:
   - Path points to your dev `src/` folder (from outside the project) → **editable install — normal for development.** `uv sync` defaults to editable mode, so this is the expected outcome. Changes to source are live.
   - Path points to `.venv/lib/.../site-packages/my_project` → non-editable copy installed. Changes to source are NOT live until you rebuild.
   - Any path resolving to the project's source directory when run from *inside* the project → potential flat-layout import trap (see `uv-packaging-mechanics.md`).

### `uv publish`

```bash
uv publish    # upload dist/ artifacts to PyPI
```

Requires built artifacts in `dist/`. Run `uv build` first.
