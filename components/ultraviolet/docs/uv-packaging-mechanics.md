# Python Packaging Mechanics

How the build pipeline works, what editable mode actually does, and why imports resolve the way they do. Open this file when debugging an import error or trying to understand a packaging behaviour from first principles.

For layout decisions and "which structure should I use", see `uv-packaging-structures.md`.

---

## 1. Build System Architecture

### The frontend / backend split (PEP 517/518)

Python's build system has two distinct layers with clearly separated responsibilities:

```
You type:   uv build
              │
              ▼
   ┌─────────────────────┐
   │   BUILD FRONTEND    │  (uv, pip, python -m build)
   │                     │  – Parses your request
   │                     │  – Creates an isolated env
   │                     │  – Calls the backend inside it
   └──────────┬──────────┘
              │  PEP 517 API calls
              ▼
   ┌─────────────────────┐
   │   BUILD BACKEND     │  (hatchling, setuptools, flit_core…)
   │                     │  – Reads pyproject.toml
   │                     │  – Discovers/locates source files
   │                     │  – Produces .whl and .tar.gz
   └─────────────────────┘
              │
              ▼
         dist/
           mypackage-0.1.0-py3-none-any.whl
           mypackage-0.1.0.tar.gz
```

**What the frontend does:** Accepts user commands, resolves which backend to use (from `[build-system]` in `pyproject.toml`), spins up an isolated temporary environment containing that backend, and invokes it via the PEP 517 API.

**What the backend does:** Reads your `pyproject.toml`, finds your package source files, strips layout prefixes (e.g. `src/`), and writes the wheel and sdist to `dist/`.

**Why the backend is isolated from your venv:** The backend is declared in `[build-system] requires` and installed in a **temporary, separate environment** by the frontend. It is never in your project's `.venv`. This prevents build tool versions from conflicting with your runtime dependencies. That's why `hatchling` or `setuptools` appears under `[build-system] requires` but not in `[dependency-groups]`.

```toml
[build-system]
requires = ["hatchling"]        # ← installed in isolated temp env, not your .venv
build-backend = "hatchling.build"
```

---

## 2. Build Backends Compared

### hatchling

The build backend shipped by the [Hatch](https://hatch.pypa.io/) project. The default backend for `uv init --lib`.

- Modern (2022+), fast, opinionated defaults
- Configuration via `[tool.hatch.*]` sections
- Package list is **explicit** — you list each package path
- No support for C/Fortran extensions
- Lower complexity; fewer legacy knobs to misread

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mypackage"]          # explicit: must list every package
```

For a multi-package src layout this becomes a maintenance burden — every new package directory must be added manually.

### setuptools

The oldest and most widely deployed backend. Required for C/Fortran extensions.

- Configuration via `[tool.setuptools.*]` sections
- Package list can be **auto-discovered** — scans a directory and finds all packages
- Full support for C/Fortran extensions via `ext_modules`
- Higher complexity; many legacy configuration paths

```toml
[build-system]
requires = ["setuptools >= 61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.packages.find]
where = ["src"]                       # auto-discovers all packages under src/
```

The auto-discovery makes setuptools genuinely more convenient for a multi-package src layout — new package directories are picked up automatically without touching config.

### flit_core and pdm-backend

Two other backends in the same slot:

- **flit_core**: Minimal and fast. Designed for simple pure-Python packages. Less adoption, simpler config, no auto-discovery.
- **pdm-backend**: Shipped by the PDM project. Similar goals to hatchling — modern, opinionated, growing. Less widely adopted outside the PDM ecosystem.

### Comparison table

| | setuptools | hatchling | flit_core | pdm-backend |
|---|---|---|---|---|
| Age / adoption | Oldest, most widely used | Modern (2022+), fast-growing | Mature, niche | Newer, PDM ecosystem |
| Config style | `[tool.setuptools.*]` | `[tool.hatch.*]` | `[tool.flit.*]` | `[tool.pdm.*]` |
| Package discovery | Auto (`packages.find`) | Explicit list | Explicit | Explicit |
| C/Fortran extensions | Full support | No | No | No |
| uv default (`uv init --lib`) | No | **Yes** | No | No |
| Best for | Multi-package src; C extensions; max compatibility | Pure-Python libraries; clean config | Simple single-package libs | PDM users |

### Your annotated setuptools config

```toml
[build-system]
requires = ["setuptools >= 61.0"]   # 61.0 = when pyproject.toml support became stable
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = { "" = "src" }        # ← The key line (see explanation below)

[tool.setuptools.packages.find]
where = ["src"]                     # Auto-discover all packages under src/
```

**What `package-dir = { "" = "src" }` means:**

The `""` key is Python's concept of the "root package directory" — the namespace anchor for all package resolution. Setting it to `"src"` tells setuptools: "when resolving any package name, start from `src/`."

The effect: `src/mypackage/` → installed as `mypackage`. The `src/` prefix is stripped at install time. Without this line, setuptools looks for packages at the project root, and `src/mypackage/` would not be found or would be installed incorrectly as `src.mypackage`.

**What `where = ["src"]` means:**

Tells setuptools' auto-discovery to scan `src/` for directories containing an `__init__.py`. Any such directory becomes a discovered package. This fires after `package-dir` has already established that `src/` is the root, so package names are correctly stripped of the `src/` prefix.

**Status of each line:**

| Line | Status | Notes |
|---|---|---|
| `requires = ["setuptools >= 61.0"]` | Keep | Correct minimum for pyproject.toml-native config |
| `build-backend = "setuptools.build_meta"` | Keep | Correct backend reference |
| `package-dir = { "" = "src" }` | Keep | Required for src layout with setuptools |
| `where = ["src"]` | Keep | Auto-discovers all packages — no manual list needed |

**Could this be replaced with hatchling?** Yes. The hatchling equivalent:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/package1", "src/package2"]   # explicit — no auto-discovery
```

The tradeoff: setuptools auto-discovers new packages as you add them; hatchling requires you to add each one to the list. For a multi-package src layout, the setuptools auto-discovery is more convenient.

---

## 3. The Import Trap — Mechanics

### What `sys.path` is

When you write `import mypackage`, Python does not search the entire filesystem. It searches a list of directories called `sys.path`, in order, and returns the first match.

```python
import sys
print(sys.path)
# ['/your/current/dir', '/usr/lib/python3.x', '/path/to/.venv/lib/python3.x/site-packages', ...]
```

The first entry is typically `""` or `"."` — the current working directory. This is the root of the import trap.

### Why flat layout is vulnerable

In a flat layout, the importable package directory sits directly at the project root:

```
myproject/
├── pyproject.toml
├── mypackage/            ← sits at the project root
│   └── __init__.py
└── .venv/
    └── lib/site-packages/
        └── mypackage/    ← the actually installed version
```

When you `cd myproject` and run Python:

```
sys.path = [".", "/usr/lib/python3.x", ".venv/lib/site-packages", ...]
              ↑
              "." resolves to /path/to/myproject/
              mypackage/ is right here → Python finds it immediately
              → never reaches .venv/lib/site-packages/mypackage/
```

Python imports `mypackage/` directly from the filesystem. The installed version in `.venv` is never reached. If these two copies differ — for example, you edited a file but forgot to reinstall — Python silently uses the wrong version. Tests can pass against uninstalled code.

**Flat layout does NOT protect you from this. It has no mechanism to do so.** This is a common misconception. Having a `pyproject.toml`, having a `.venv`, or having run `uv sync` does not change the `sys.path` ordering. The trap is always active when `.` appears before `site-packages` on `sys.path`.

### Why src layout prevents it

In a src layout, the importable package is nested one level deeper:

```
myproject/
├── pyproject.toml
├── src/
│   └── mypackage/        ← NOT at the project root
└── .venv/
    └── lib/site-packages/
        └── mypackage/
```

When you `cd myproject` and run Python:

```
sys.path = [".", "/usr/lib/python3.x", ".venv/lib/site-packages", ...]
              ↑
              "." resolves to /path/to/myproject/
              mypackage/ is NOT here — it's at src/mypackage/
              src/ is not on sys.path
              → Python must reach .venv/lib/site-packages/mypackage/
```

There is no `mypackage/` at `.`, and `src/` is not on `sys.path` unless an editable install explicitly adds it (see Section 4). The filesystem accident is structurally impossible. Either the package is installed (and importable via site-packages) or the import raises `ModuleNotFoundError` — which is the correct, informative failure mode.

### The same trap with multiple top-level packages

Having `package1/` and `package2/` at the project root in flat layout means both are directly importable from the filesystem. `sys.path` sees `.` first, finds both directories, and never consults the installed versions. Flat layout does not protect you regardless of how many packages are present.

---

## 4. Editable Installs

### What a non-editable install does

```bash
pip install .
# or: uv pip install .
```

Copies your package files into `.venv/lib/python3.x/site-packages/mypackage/`. From that point, `import mypackage` finds the copy. If you change your source code, **you must reinstall for the changes to take effect**. The copy and your source are now independent.

```
.venv/lib/python3.x/site-packages/
└── mypackage/
    ├── __init__.py    ← a static copy, not your source file
    └── core.py
```

### What an editable install does

```bash
pip install -e .
# or with uv (the default):
uv sync
```

Instead of copying files, the backend creates a small pointer file in site-packages — a `.pth` file (or `__editable__` dist-info entry) — that **adds your `src/` directory to `sys.path`**. No files are copied. Your source is the live import target.

```
.venv/lib/python3.x/site-packages/
└── __editable__.mypackage.pth     ← contains: /path/to/myproject/src
```

When Python starts, it processes all `.pth` files in site-packages, and the path inside is appended to `sys.path`:

```
sys.path = [".", "/path/to/myproject/src", "/usr/lib/python3.x", ".venv/lib/site-packages", ...]
                  ↑
                  added by the .pth file
```

`import mypackage` → Python finds `src/mypackage/` via the `.pth` entry. Changes to your source files take effect immediately — no reinstall needed.

### Why `uv sync` always uses editable mode for your own project

`uv sync` always installs your own project in editable mode. This is intentional: during development you want code changes to be live immediately. The `.pth` mechanism is what makes the src layout work for development — it threads through the `src/` barrier specifically via the package machinery, so you get both the import-trap protection and live source editing.

### When you would need a non-editable install

Rarely. The main cases:
- **Testing packaging**: verifying that the wheel is correctly built and installable before publishing to PyPI
- **CI verification**: confirming the installed artifact behaves identically to source
- **Reproducing a user environment**: simulating what a downstream consumer of your package actually gets

```bash
# Force non-editable in uv
uv pip install --no-editable .
```

### The import trap verification steps

To verify the editable install is working correctly — i.e., that Python is using the install machinery and not accidentally hitting the raw filesystem:

```bash
# 1. Sync the project
uv sync

# 2. Step away from the project directory
cd ..

# 3. Provenance check — where is the code actually coming from?
uv run python -c "import mypackage; print(mypackage.__file__)"
```

**Interpreting the result:**
- Path points to `.venv/lib/.../site-packages/mypackage/` → non-editable install; the copy in site-packages
- Path points to your development `src/mypackage/` folder (from outside the project directory) → editable install working correctly; the `.pth` link is live

Running the check from outside the project directory is important. From inside the project root, flat layout ambiguity can mask what's actually happening. Stepping away forces Python to rely entirely on `sys.path` entries from the install machinery.

---

## 5. The Three States — How Imports Resolve

Import resolution depends on which of three states your project is in.

### State 1: Not installed (raw source)

```
sys.path = [".", "/usr/lib/python3.x", ...]
```

No `.pth` file, no site-packages entry. What happens when you run `import mypackage`:

| Layout | What Python finds | Outcome |
|---|---|---|
| **Flat** | `mypackage/` at `.` | Imports directly from filesystem. Accidentally works. |
| **src** | Nothing at `.`, nothing in stdlib | `ModuleNotFoundError`. Correctly fails — forces you to install. |

The src layout "correctly fails" is a feature: it means your development environment can never silently diverge from the installed state.

### State 2: Editable install (`uv sync`)

uv writes a `.pth` file:

```
.venv/lib/python3.x/site-packages/__editable__.mypackage.pth
```

containing the path to your `src/` directory. Python processes this at startup:

```
sys.path = [".", "/path/to/myproject/src", "/usr/lib/python3.x", ".venv/lib/site-packages", ...]
                  ↑─────────────────────────
                  added by the .pth file at interpreter startup
```

`import mypackage` → Python scans `sys.path` in order → finds `src/mypackage/` → your live source files. Changes take effect immediately. No reinstall needed for modified files.

### State 3: Non-editable install

Files copied to `.venv/lib/python3.x/site-packages/mypackage/`. No `.pth` file.

```
sys.path = [".", "/usr/lib/python3.x", ".venv/lib/python3.x/site-packages", ...]
```

`import mypackage` → Python reaches `site-packages/mypackage/` → the static copy. Source changes are invisible until you rebuild and reinstall.

### Summary: actions and what changes

| Action | Editable install | Non-editable install |
|---|---|---|
| Edit an existing `.py` file | Live immediately | Invisible — reinstall required |
| Add a new `.py` file to an existing package | Live immediately | Invisible — reinstall required |
| Add a new package directory (+ `__init__.py`) | Requires `uv sync` to update install record | Requires rebuild + reinstall |
| Change `pyproject.toml` dependencies | Run `uv sync` to update `.venv` | Run `uv sync` to update `.venv` |
| Build for distribution | `uv build` → creates `dist/*.whl` | `uv build` → creates `dist/*.whl` |

---

## 6. What `uv build` Actually Produces

### The build command

```bash
uv build
```

The build backend reads `pyproject.toml`, locates your source files, and produces two artifacts:

```
dist/
├── mypackage-0.1.0-py3-none-any.whl    ← wheel (for installing)
└── mypackage-0.1.0.tar.gz              ← sdist (source archive)
```

`uv build` does **not** install anything. It only creates these distribution files.

### The wheel is a zip

A `.whl` file is a zip archive. If you unzip it:

```
mypackage-0.1.0-py3-none-any.whl (unzipped)
├── mypackage/
│   ├── __init__.py
│   └── core.py
└── mypackage-0.1.0.dist-info/
    ├── METADATA       ← name, version, author, dependencies from pyproject.toml
    ├── RECORD         ← checksums of all installed files
    └── WHEEL          ← wheel format version, generator info
```

The critical transformation: **`src/` is stripped**. `src/mypackage/core.py` in your repo becomes `mypackage/core.py` in the wheel. The installed layout has no trace of your source layout.

### sdist vs wheel

| | Wheel (`.whl`) | sdist (`.tar.gz`) |
|---|---|---|
| Contents | Pre-built, ready to install | Raw source + build config |
| When used | Direct installation (pip, uv) | Fallback if no wheel available; source distributions |
| Build step at install | None | Runs build backend at install time |
| Platform-specific? | Can be (C extensions); pure-Python wheels are universal | No — always source |

PyPI serves wheels whenever available. The sdist is the fallback for platforms/Python versions with no pre-built wheel, or when the user explicitly requests source.

### The `dist/` output

The files in `dist/` are what you would upload to PyPI:

```bash
uv publish    # uploads dist/*.whl and dist/*.tar.gz to PyPI
```

Until you run `uv build`, `dist/` does not exist. The build step is only needed for distribution — not for development, not for running tests, not for `import` to work locally.

### Wheel filename anatomy

```
mypackage-0.1.0-py3-none-any.whl
│           │     │    │    │
│           │     │    │    └── ABI tag (none = pure Python)
│           │     │    └─────── Platform tag (any = not platform-specific)
│           │     └──────────── Python tag (py3 = Python 3.x)
│           └────────────────── Version
└────────────────────────────── Distribution name
```

A `py3-none-any` wheel installs on any Python 3, any platform. C extension wheels would have platform-specific tags like `cp312-cp312-manylinux_2_17_x86_64`.

---

## 7. Debugging Checklist

When imports fail or behave unexpectedly, work through these checks in order.

### 1. Is the package installed at all?

```bash
uv pip list | grep mypackage
# or
uv run python -c "import mypackage" && echo "OK" || echo "NOT FOUND"
```

If not listed → run `uv sync`.

### 2. Is it installed as editable or non-editable?

```bash
# Look for a .pth file (editable)
ls .venv/lib/python*/site-packages/__editable__*.pth

# Look for the dist-info directory (either mode)
ls .venv/lib/python*/site-packages/mypackage-*.dist-info/

# Check the direct value
uv run python -c "import mypackage; print(mypackage.__file__)"
```

- Path under `src/` → editable install, `.pth` link is active
- Path under `.venv/lib/.../site-packages/` → non-editable copy

### 3. What is on `sys.path`?

```bash
uv run python -c "import sys; [print(p) for p in sys.path]"
```

Check whether `src/` appears (editable), whether the project root `.` appears (expected), and whether `site-packages` appears (always should). If `src/` is absent and you expected editable mode, the `.pth` file may be missing → re-run `uv sync`.

### 4. Are you importing the right copy?

The provenance check — step outside the project first:

```bash
cd ..
uv run python -c "import mypackage; print(mypackage.__file__)"
```

If running from inside the project and from outside gives different paths, you have the flat-layout import trap: Python is finding the raw source directory before the installed version.

### 5. Is there a stale non-editable copy shadowing the editable?

If you previously ran `pip install .` (non-editable) and later switched to `uv sync` (editable), you may have both a copy in site-packages and a `.pth` entry. The copy comes first on `sys.path`.

```bash
# Check for both
ls .venv/lib/python*/site-packages/mypackage/          # non-editable copy
ls .venv/lib/python*/site-packages/__editable__*.pth   # editable pointer
```

If both exist, reinstall cleanly:

```bash
uv pip uninstall mypackage
uv sync
```

### 6. Did you add a new package directory without re-syncing?

Adding a new `src/newpackage/__init__.py` requires updating the install record even in editable mode:

```bash
uv sync    # re-registers the new package with the editable install
```

### 7. Is `pyproject.toml` correctly configured for the layout?

For setuptools + src layout: confirm `package-dir = { "" = "src" }` is present. Without it, setuptools looks at the project root and `src/mypackage/` is not found.

For hatchling + src layout: confirm `packages = ["src/mypackage"]` (with the `src/` prefix). Without the prefix, hatchling looks for `mypackage/` at the project root.

```bash
# Dry-run the build to see what gets packaged
uv build --no-wheel 2>&1 | head -40
# or build the wheel and inspect it
uv build
unzip -l dist/*.whl | head -30
```

The unzipped listing should show `mypackage/...` at the top level with no `src/` prefix. If it shows `src/mypackage/...`, the backend config is wrong.
