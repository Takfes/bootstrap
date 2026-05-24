# Python Packaging Structures

The architect's reference — open this when starting a new project or deciding how to structure one. Covers terminology, layout options, multi-package patterns, workspaces, optional extras, and a complete decision guide.

For build mechanics, editable installs, and sys.path internals, see `packaging-mechanics.md`.

---

## 0. Terminology

| Term | What it is | Example |
|------|-----------|---------|
| **Module** | A single `.py` file | `utils.py` → `import utils` |
| **Package** (importable) | A directory with `__init__.py` | `myapp/` → `import myapp` |
| **Sub-package** | A package nested inside another package | `myapp/core/` → `import myapp.core` |
| **Distribution package** | What you install with `pip install` / `uv add`. One distribution can expose *many* importable packages. | `pip install requests` installs the `requests` importable package |
| **Namespace package** | A directory *without* `__init__.py` (PEP 420). Used in advanced monorepos; ignore until you need it. | `myorg/utils/` — no `__init__.py` |
| **Extra / optional dependency** | A named group of dependencies you opt into at install time | `pip install myapp[gui]` |

### The critical distinction: distribution name ≠ importable name

"Distribution package" (what PyPI ships and `pip install` names) and "importable package" (what `import` sees) are **completely independent**. They can and often do differ:

| `pip install X` | `import Y` |
|-----------------|------------|
| `Pillow` | `PIL` |
| `scikit-learn` | `sklearn` |
| `beautifulsoup4` | `bs4` |
| `python-dateutil` | `dateutil` |

The distribution name comes from `[project] name` in `pyproject.toml`. The importable name(s) come from the package directory names under `src/` (or the project root for flat layout). These are set independently and have no required relationship.

This is the root of most confusion in multi-package setups — covered in detail in sections 3 and 6.

---

## 1. Layout Options

### 1a. Flat layout

```
myproject/
├── pyproject.toml
├── mypackage/
│   ├── __init__.py
│   └── core.py
└── tests/
    └── test_core.py
```

**pyproject.toml (hatchling):**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["mypackage"]
```

**Practical implications:**

Simple. Works fine for small, standalone scripts and apps you're not distributing.

**Import trap risk — flat layout does NOT protect you.** This is a common misconception. When you `cd` into the project root and run Python, Python adds `.` to `sys.path`. Since `mypackage/` sits right there at the root, Python imports it directly from the filesystem — it never looks in `.venv/`. If your installed version differs from your local folder (say, you forgot to reinstall after a change), you won't notice. Your tests can silently pass against uninstalled code.

```
myproject/
├── mypackage/       ← Python sees this when you're in myproject/
└── .venv/
    └── lib/site-packages/mypackage/  ← the actually installed version
```

The same applies when you have multiple top-level packages in flat layout: `package1/` and `package2/` at the project root are both directly importable from the filesystem, bypassing the installed version.

---

### 1b. src layout — recommended for distributable libraries

```
myproject/
├── pyproject.toml
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── core.py
└── tests/
    └── test_core.py
```

**pyproject.toml (hatchling):**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/mypackage"]
```

**Why src/ fixes the import trap:**

The `src/` prefix is a deliberate barrier. From the project root, `mypackage/` is not at `.` — it's at `src/mypackage/`. Since `src/` is not on `sys.path` (unless the editable install puts it there through its `.pth` machinery), Python is forced to use the installed version. The trap is physically impossible.

`uv sync` installs your project in editable mode by default, adding `src/` to `sys.path` via a `.pth` file — so your source changes are still live. But the path goes through the install machinery, not through accidental filesystem discovery.

**The `src/` prefix is invisible to importers.** The package is installed as `mypackage`, not `src.mypackage`. `src/` exists only to solve the import-trap problem; it vanishes at install time.

**`uv init --lib` generates the src layout by default.**

**Note on what goes in `src/`:** `src/` is a container directory — you do not put `.py` files directly in it. The importable package is always `src/mypackage/`. Loose `.py` files at `src/` level are not packages and won't be discovered.

---

## 2. Multiple packages in one distribution

One `pip install` that gives the user several importable packages. Both the flat and src variants are shown.

### 2a. Multiple top-level packages (flat layout)

```
myproject/
├── pyproject.toml
├── package1/
│   └── __init__.py
└── package2/
    └── __init__.py
```

**pyproject.toml (hatchling — explicit list):**
```toml
[tool.hatch.build.targets.wheel]
packages = ["package1", "package2"]
```

---

### 2b. Multiple top-level packages (src layout)

```
myproject/
├── pyproject.toml
└── src/
    ├── package1/
    │   └── __init__.py
    └── package2/
        └── __init__.py
```

**pyproject.toml (hatchling — explicit list):**
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/package1", "src/package2"]
```

**pyproject.toml (setuptools — auto-discovers all packages under src/):**
```toml
[build-system]
requires = ["setuptools >= 61.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = { "" = "src" }

[tool.setuptools.packages.find]
where = ["src"]
```

The setuptools auto-discovery tradeoff: new packages are found automatically as you add them; hatchling's explicit list requires manual updates but is easier to audit.

---

### What does the user get?

After `pip install myproject` (or `uv add myproject`), both packages are importable:

```python
import package1
import package2
```

They are **not** `myproject.package1`. The distribution name (`myproject`) is completely separate from the importable names (`package1`, `package2`). `import myproject` will raise `ModuleNotFoundError` — there is no `myproject` package, only a distribution label.

This surprises people. It's correct Python packaging behaviour, but it's also why this pattern is considered confusing and rarely the right choice for new projects. See the comparison table in section 3c.

---

### 2c. Sub-packages under a single namespace — the preferred alternative

If you want `myproject.package1` style imports, make the pieces sub-packages of a single top-level package:

```
myproject/
├── pyproject.toml
└── src/
    └── myproject/
        ├── __init__.py
        ├── package1/
        │   └── __init__.py
        └── package2/
            └── __init__.py
```

**pyproject.toml:**
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/myproject"]
```

**How users import:**
```python
from myproject import package1
from myproject.package2 import something
import myproject   # the parent itself is importable
```

This is the more common pattern for a cohesive library. The namespace (`myproject`) is self-documenting — users can see exactly where `X` comes from. Real-world examples: `numpy.linalg`, `pandas.io`, `requests.auth`.

**Use sub-packages when:**
- The pieces are parts of one cohesive library — same purpose, same release cycle, often with internal imports between them
- You want a unified top-level entry point (`import myproject`)
- You want the namespace to be self-documenting

---

### 3. Side-by-side: sub-packages vs multiple top-level packages in one distribution

| | Sub-packages | Multiple top-level in one distro |
|--|-------------|----------------------------------|
| Import style | `from myorg.core import X` | `import core` (separate namespace) |
| Relationship visible to the user? | Yes — the namespace makes it explicit | No — the distribution name disappears |
| Single `__init__.py` entry point? | Yes — `import myorg` can expose everything | No — no shared root |
| Distribution name matches import? | Usually yes | Usually no |
| Recommended for new projects? | **Yes** | Rarely — see edge cases below |

**The only cases where multiple top-level packages in one distribution are warranted:**
1. Backwards compatibility transition: two importable names (`oldname` and `newname`) that users already know, and you need one `pip install` to provide both.
2. Wrapping a third-party C library that installs companion importable namespaces alongside the main one.
3. Plugin architecture where the distribution needs to inject code into multiple existing namespaces simultaneously.

Outside those cases: if the packages are cohesive, use sub-packages. If they're independent, use a workspace.

---

## 4. Workspace — multiple independent distributions

Use when packages are independently useful (some users want only part of the suite), have different dependency sets, or need to be published to PyPI separately. Each package gets its own `pyproject.toml`.

```
myrepo/
├── pyproject.toml          ← workspace root (declares members; no [project] section needed)
├── uv.lock                 ← ONE lockfile for the whole workspace
└── packages/
    ├── core/
    │   ├── pyproject.toml
    │   └── src/
    │       └── core/
    │           └── __init__.py
    ├── cli/
    │   ├── pyproject.toml  ← can declare `core` as a workspace dependency
    │   └── src/
    │       └── cli/
    │           └── __init__.py
    └── api/
        ├── pyproject.toml
        └── src/
            └── api/
                └── __init__.py
```

**Root pyproject.toml:**
```toml
[tool.uv.workspace]
members = ["packages/*"]

# Optionally, shared dev dependencies for the whole workspace:
[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.9"]
```

**packages/cli/pyproject.toml (member that depends on another member):**
```toml
[project]
name = "mycli"
version = "0.1.0"
dependencies = ["mycore>=0.1.0"]   # refer by distribution name

[tool.uv.sources]
mycore = { workspace = true }      # resolve from workspace, not PyPI

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/cli"]
```

**Key uv workspace commands:**
```bash
# From the root — affects all members
uv sync                            # install all workspace members and their deps
uv sync --package mycli            # install only mycli and its deps

# Add a dep to a specific package
uv add requests --package mycli

# Run something in a specific package context
uv run --package mycli python -c "import cli"
```

**Lock file behaviour:** There is ONE `uv.lock` at the workspace root covering all members. uv resolves the full dependency graph once, ensuring no version conflicts between packages. If `core` and `cli` both depend on `pydantic`, uv ensures they agree on the same version — that guarantee breaks if each had its own lockfile. **The single lockfile is a feature, not a limitation.**

You cannot have multiple `uv.lock` files in a single workspace; this is intentional by design.

---

## 5. Optional extras

Use when a single distribution has optional components that require extra dependencies. The package always installs; extras pull in additional dependencies only when the user opts in.

**pyproject.toml — full example with multiple extras and a convenience `all` group:**
```toml
[project]
name = "myapp"
dependencies = [
    "pydantic>=2.0",   # always installed — the core dependency
]

[project.optional-dependencies]
interface = [
    "fastapi>=0.100",
    "uvicorn[standard]>=0.20",
]
backend = [
    "sqlalchemy>=2.0",
    "psycopg2-binary>=2.9",
]
ml = [
    "torch>=2.0",
    "transformers>=4.30",
]
all = [
    "myapp[interface,backend,ml]",  # convenience: install everything
]
```

**How users install:**
```bash
uv add myapp                        # core only
uv add "myapp[interface]"           # core + FastAPI stack
uv add "myapp[interface,backend]"   # core + FastAPI + SQLAlchemy
uv add "myapp[all]"                 # everything
```

**How to sync during development:**
```bash
uv sync --extra interface           # install the interface extras into your venv
uv sync --all-extras                # install all extras
```

**What extras do and don't do:**

Extras are a dependency-group selector. They do not change what *code* is installed — only which *dependencies* come with it. All source files are installed regardless of which extras the user picks. Extras are purely a mechanism for conditional dependency pulling.

Common use cases: heavy ML dependencies (`[ml]`), optional GUI (`[gui]`), async support (`[async]`), database backends (`[postgres]`, `[mysql]`).

### `[project.optional-dependencies]` vs `[dependency-groups]`

These serve different purposes and have different scopes:

| | `[project.optional-dependencies]` | `[dependency-groups]` |
|--|-----------------------------------|----------------------|
| Published to PyPI? | **Yes** — end users see and install these | **No** — local dev only, not published |
| Intended for | End users: `pip install myapp[ml]` | Developers: `uv sync --group dev` |
| Appears in dist-info? | Yes | No |
| Typical contents | Optional runtime features | `pytest`, `ruff`, `mypy`, type stubs |

For dev tooling (`pytest`, `ruff`, linters, type checkers), use `[dependency-groups]`. Reserve `[project.optional-dependencies]` for optional runtime features that end users of your published package will actually use.

---

## 6. Where does the distribution name come from?

The distribution name comes exclusively from **`[project] name`** in `pyproject.toml`:

```toml
[project]
name = "my-distribution"    # what PyPI shows; what pip/uv uses to install
version = "0.1.0"
```

This is completely independent of what you can `import`. The importable name(s) are determined by the package directory names — not by `[project] name`.

**In a multi-package distribution, the decoupling trap is severe:**

```toml
[project]
name = "mytoolkit"     # pip install mytoolkit

[tool.hatch.build.targets.wheel]
packages = ["src/package1", "src/package2"]
```

After `pip install mytoolkit`:
```python
import mytoolkit   # ModuleNotFoundError — there is no mytoolkit package
import package1    # works
import package2    # works
```

`mytoolkit` is only a distribution label. No importable package named `mytoolkit` is created unless you explicitly create `src/mytoolkit/__init__.py`. This mismatch is a support burden and one of the main reasons the multi-top-level pattern is not recommended for new projects.

---

## 7. Decision guide

```
One repo, one installable thing?
│
├── Simple script / app, no distribution intended
│   └── Flat layout
│       mypackage/ at project root, pyproject.toml alongside it
│       Accept the import trap — you're not distributing
│
└── Library for distribution
    └── src layout
        src/mypackage/ — uv init --lib gives you this by default


One repo, multiple things?
│
├── They belong together — same purpose, same release cycle,
│   users always want all of them?
│   └── ONE distribution, sub-packages
│       src/myorg/__init__.py
│       src/myorg/core/__init__.py
│       src/myorg/utils/__init__.py
│       → pip install myorg → from myorg.core import X
│
├── They have different optional dependency sets
│   (heavy ML add-on, GUI, async support, database backend)?
│   └── ONE distribution, optional extras
│       [project.optional-dependencies]
│       ml = ["torch"]
│       → pip install myapp[ml]
│
├── They're independently useful — some users want only part of
│   the suite, or they have meaningfully different dependency sets?
│   └── uv WORKSPACE — multiple distributions, one lockfile
│       packages/core/ + packages/cli/ + packages/api/
│       → pip install mycore | pip install mycli (independently)
│
└── They're truly separate — different teams, different versioning,
    different repos?
    └── Separate repos entirely


Special case — single distribution, multiple top-level packages:

This fits between "sub-packages" and "workspace" but is almost never
the right first choice. Reach for it only when:

  1. Backwards compatibility: two importable names (oldname and newname)
     that users already know, bundled in one pip install during a transition.
  2. Wrapping a C library that installs companion importable namespaces.
  3. Plugin architecture requiring injection into multiple existing namespaces.

Outside those cases:
  cohesive → sub-packages
  independent → workspace
```

---

## 8. Common mistakes

**1. Trying to `import` the distribution name when it differs from the package name.**

After `pip install mytoolkit`, developers try `import mytoolkit` and get `ModuleNotFoundError`. The distribution name is only a PyPI/install label. The importable names come from the package directory names in `src/`. If there's no `src/mytoolkit/__init__.py`, there's no `mytoolkit` to import. Check the wheel's actual package list (`[tool.hatch.build.targets.wheel] packages`) to see what will be importable.

**2. Forgetting `__init__.py` in a sub-package directory.**

A directory without `__init__.py` is a namespace package (PEP 420), not a regular package. It may import inconsistently across tools and environments. Unless you're intentionally using namespace packages for an advanced monorepo pattern, every package directory needs `__init__.py`.

**3. Assuming flat layout prevents the import trap.**

It does not. With flat layout, `mypackage/` sits at the project root, which is on `sys.path`. Python imports it directly from the filesystem, bypassing the installed `.venv` copy. Tests can silently pass against uninstalled code. If you're writing a library for distribution, use the src layout.

**4. Using `[project.optional-dependencies]` for dev tooling.**

Dev tools (`pytest`, `ruff`, `mypy`) published under `[project.optional-dependencies]` end up in your package's PyPI metadata and are visible to end users as extras. They should go in `[dependency-groups]` instead — those are local-only and not published. The rule of thumb: if an end user of your published package would never run `pip install myapp[dev]`, it belongs in `[dependency-groups]`, not `[project.optional-dependencies]`.
