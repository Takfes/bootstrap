"""bootstrap CLI — portable Python project scaffolding tool.

Entry points:
  bootstrap new <project-name>   — scaffold a new project
  bootstrap add [component...]   — add components to existing project
  bootstrap list                 — list available components
  bootstrap detect               — detect what's already configured here
"""

import argparse
import sys
from datetime import date
from pathlib import Path

from . import __version__
from .components import ComponentSpec, get_component, get_components
from .detector import ProjectState
from .installer import (
    POST_INSTALL_COMMANDS,
    components_with_post_install,
    get_template_repo,
    install_component,
    run_post_install_commands,
)


# PyPI trove classifier for each supported license_type — keeps [project]
# classifiers in pyproject.toml consistent with the actual LICENSE chosen.
_LICENSE_CLASSIFIERS: dict[str, str] = {
    "MIT": "License :: OSI Approved :: MIT License",
    "APACHE": "License :: OSI Approved :: Apache Software License",
    "BSD": "License :: OSI Approved :: BSD License",
    "ISC": "License :: OSI Approved :: ISC License (ISCL)",
    "GPL": "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
}


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------

def _collect_context(
    project_name: str,
    *,
    state: ProjectState | None = None,
    needed: set[str] | None = None,
    extra: dict[str, str] | None = None,
) -> dict[str, str]:
    """Gather template substitution variables interactively.

    Only prompts for variables listed in `needed` — the union of context_vars
    declared by the components the user selected (see _needed_context_vars).
    Pass `needed=None` to ask everything (default, backward-compatible).

    Pre-fills known values from detected project state where available.
    """
    ctx: dict[str, str] = {}

    # Always derived from the project name — never gated behind component selection.
    ctx["project_name"] = project_name
    # Distribution name (PyPI/repo) vs. import name are independent concepts
    # (e.g. `Pillow` installs, `PIL` imports) — prompted separately so they
    # can diverge, with today's derivation as the default.
    default_package_name = project_name.lower().replace("-", "_").replace(" ", "_")
    ctx["package_name"] = _ask("Python package/import name", default=default_package_name)
    ctx["repo_name"] = project_name.lower().replace("_", "-").replace(" ", "-")
    ctx["year"] = str(date.today().year)
    # Not prompted — hardcoded default to remove signup friction.
    ctx["agent_name"] = "Claude"

    ask_all = needed is None

    if ask_all or "author" in needed:
        ctx["author"] = _ask("Your name", default="Your Name")
    if ask_all or "author_email" in needed:
        ctx["author_email"] = _ask("Your email", default="you@example.com")
    if ask_all or "github_org" in needed:
        default_org = (state.github_org if state else None) or ""
        ctx["github_org"] = _ask("GitHub org/username", default=default_org)
    if ask_all or "description" in needed:
        ctx["description"] = _ask("One-line project description", default="")

    if ask_all or "python_version" in needed:
        python_version = _ask("Minimum Python version", default="3.11")
        ctx["python_version"] = python_version
        ctx["python_version_nodot"] = python_version.replace(".", "")

    if ask_all or "layout" in needed:
        raw_layout = _ask("Package layout (flat/src)", default="src").strip().lower()
        ctx["layout"] = raw_layout if raw_layout in ("flat", "src") else "src"

    if ask_all or "license_type" in needed:
        ctx["license_type"] = _ask(
            "License type (MIT/Apache/BSD/ISC/GPL)", default="MIT"
        ).upper()
        ctx["license_classifier"] = _LICENSE_CLASSIFIERS.get(
            ctx["license_type"], _LICENSE_CLASSIFIERS["MIT"]
        )

    if extra:
        ctx.update(extra)

    # Derived from package_name + layout — computed unconditionally since
    # mkdocstrings' source path needs it even when "layout" itself wasn't
    # prompted (e.g. uv not selected), falling back to the src-layout default.
    layout = ctx.get("layout", "src")
    ctx["package_src_path"] = (
        ctx["package_name"] if layout == "flat" else f"src/{ctx['package_name']}"
    )

    # description is an optional prompt — README.md gets a placeholder sentence
    # instead of a blank line when it's left empty.
    python_version = ctx.get("python_version", "3.11")
    ctx["description_or_placeholder"] = (
        ctx.get("description") or f"A new {python_version}+ Python project."
    )

    return ctx


def _ask(prompt: str, *, default: str = "") -> str:
    """Prompt the user for a value, with an optional default."""
    display = f"{prompt} [{default}]: " if default else f"{prompt}: "
    value = input(display).strip()
    return value if value else default


# ---------------------------------------------------------------------------
# Component selection helpers
# ---------------------------------------------------------------------------

def _select_components_cli(components: list[ComponentSpec]) -> list[str]:
    """Present a numbered checklist in the terminal and return selected names."""
    print("\nAvailable components:")
    for i, spec in enumerate(components, 1):
        deps = f"  (needs: {', '.join(spec.requires)})" if spec.requires else ""
        print(f"  [{i:2}] {spec.name:<15}  {spec.description}{deps}")
    print()
    raw = input(
        "Select components — space-separated numbers or names, 'all', "
        "or 'i' to pick interactively (e.g. '1 3 agents'): "
    ).strip()

    if not raw:
        return []

    if raw.lower() == "all":
        return [spec.name for spec in components]

    if raw.lower() == "i":
        return _toggle_select(components)

    name_map = {spec.name: spec for spec in components}
    selected: list[str] = []
    seen: set[str] = set()

    for token in raw.split():
        name: str | None = None
        if token.isdigit():
            idx = int(token) - 1
            if 0 <= idx < len(components):
                name = components[idx].name
        elif token in name_map:
            name = token
        else:
            print(f"  warning: '{token}' is not a valid component or number — skipped")
            continue
        if name and name not in seen:
            selected.append(name)
            seen.add(name)

    return selected


def _toggle_select(components: list[ComponentSpec]) -> list[str]:
    """Interactive toggle loop: type a number to flip it, empty input to confirm."""
    picked = [False] * len(components)

    while True:
        print("\nToggle components (number to flip, empty to confirm):")
        for i, spec in enumerate(components, 1):
            mark = "x" if picked[i - 1] else " "
            deps = f"  (needs: {', '.join(spec.requires)})" if spec.requires else ""
            print(f"  [{mark}] {i:2}  {spec.name:<15}  {spec.description}{deps}")

        raw = input("\nToggle #: ").strip()
        if not raw:
            break
        if raw.isdigit() and 0 <= int(raw) - 1 < len(components):
            picked[int(raw) - 1] = not picked[int(raw) - 1]
        else:
            print(f"  warning: '{raw}' is not a valid number — pick a listed index")

    return [spec.name for spec, is_picked in zip(components, picked) if is_picked]


def _resolve_dependencies(
    requested: list[str],
    comp_map: dict[str, ComponentSpec],
) -> list[str]:
    """Expand requested list with required dependencies, deps-first ordering."""
    resolved: list[str] = []
    seen: set[str] = set()

    def _add(name: str, *, auto_added: bool = False) -> None:
        if name in seen:
            return
        seen.add(name)
        spec = comp_map.get(name)
        if spec is None:
            return
        for req in spec.requires:
            if req not in seen:
                if req not in {c for c in requested}:
                    print(f"  note: adding '{req}' (required by '{name}')")
                _add(req)
        resolved.append(name)

    for name in requested:
        _add(name)

    return resolved


def _needed_context_vars(
    names: list[str],
    comp_map: dict[str, ComponentSpec],
) -> set[str]:
    """Union of context_vars declared by the given components."""
    needed: set[str] = set()
    for name in names:
        spec = comp_map.get(name)
        if spec is not None:
            needed.update(spec.context_vars)
    return needed


def _confirm_overwrite_components(
    ordered: list[str],
    installed: set[str],
    *,
    force_overwrite: bool = False,
) -> dict[str, bool]:
    """For each already-installed component, ask user whether to overwrite.

    Returns a dict mapping component name to overwrite bool.
    If force_overwrite is True, all already-installed components are overwritten
    without prompting (backward-compatible --overwrite flag behaviour).
    """
    overwrite_map: dict[str, bool] = {}
    for name in ordered:
        if name in installed:
            if force_overwrite:
                overwrite_map[name] = True
            else:
                answer = input(
                    f"  Component '{name}' appears to be installed. Overwrite? [y/N]: "
                ).strip().lower()
                overwrite_map[name] = answer in ("y", "yes")
        else:
            overwrite_map[name] = False
    return overwrite_map


def _offer_post_install(names: list[str], project_dir: Path) -> bool:
    """Ask once whether to run post-install commands for installed components.

    Returns True if the commands were run (or there were none to run), False
    if the user declined — the caller uses this to decide what to tell the
    user to run manually.
    """
    relevant = components_with_post_install(names)
    if not relevant:
        return True

    listed = ", ".join(
        " ".join(cmd) for name in relevant for cmd in POST_INSTALL_COMMANDS[name]
    )
    answer = input(f"\nRun post-install commands now? ({listed}) [Y/n]: ").strip().lower()
    if answer in ("", "y", "yes"):
        run_post_install_commands(relevant, project_dir)
        return True
    return False


# ---------------------------------------------------------------------------
# Subcommand: new
# ---------------------------------------------------------------------------

def cmd_new(args: argparse.Namespace) -> int:
    """Scaffold a new project from scratch."""
    project_name: str = args.name
    project_dir = Path(args.directory or project_name)

    if project_dir.exists() and any(project_dir.iterdir()):
        print(f"✗ Directory '{project_dir}' already exists and is not empty.")
        print("  Use 'bootstrap add' to add components to an existing project.")
        return 1

    project_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nScaffolding new project '{project_name}' in {project_dir}/\n")

    state = ProjectState.scan(project_dir)

    try:
        components = get_components(repo_url=args.repo_url, branch=args.branch)
    except Exception as e:
        print(f"✗ Failed to load component list: {e}")
        return 1

    comp_map = {c.name: c for c in components}

    # --- Select components ---
    if args.components:
        requested = args.components
    else:
        requested = _select_components_cli(components)
        if not requested:
            print("No components selected. Nothing to install.")
            return 0

    # --- Validate ---
    unknown = [c for c in requested if c not in comp_map]
    if unknown:
        print(f"✗ Unknown components: {', '.join(unknown)}")
        print("  Run 'bootstrap list' to see available components.")
        return 1

    # --- Resolve dependencies ---
    ordered = _resolve_dependencies(requested, comp_map)

    # --- Collect context (only what the resolved components need) ---
    needed_vars = _needed_context_vars(ordered, comp_map)
    context = _collect_context(project_name, state=state, needed=needed_vars)

    # --- Overwrite confirmation ---
    overwrite_map = _confirm_overwrite_components(
        ordered, state.installed_components, force_overwrite=False
    )

    # --- Install ---
    print(f"\nInstalling: {', '.join(ordered)}\n")
    failed: list[str] = []
    for name in ordered:
        ok = install_component(
            name,
            project_dir,
            context,
            overwrite=overwrite_map.get(name, False),
            repo_url=args.repo_url,
            branch=args.branch,
        )
        if not ok:
            failed.append(name)

    print()
    if failed:
        print(f"⚠  Completed with errors. Failed components: {', '.join(failed)}")
        return 1

    # --- Post-install commands (uv sync, pre-commit install) ---
    post_install_ran = _offer_post_install(ordered, project_dir)

    print(f"✓ Project '{project_name}' ready in {project_dir}/")
    print(f"\nNext steps:")
    print(f"  cd {project_dir}")
    if not post_install_ran:
        if "uv" in ordered:
            print(f"  uv sync              # installs dependencies into .venv")
        if "precommit" in ordered:
            print(f"  pre-commit install   # enables checks on every commit")
    if "justfile" in ordered:
        print(f"  just --list          # see available dev commands")
    if "makefile" in ordered:
        print(f"  make help            # see available dev commands")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: add
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> int:
    """Add one or more components to an existing project."""
    project_dir = Path(args.directory or ".")

    if not project_dir.exists():
        print(f"✗ Directory '{project_dir}' does not exist.")
        return 1

    state = ProjectState.scan(project_dir)
    project_name = _infer_project_name(project_dir)

    try:
        components = get_components(repo_url=args.repo_url, branch=args.branch)
    except Exception as e:
        print(f"✗ Failed to load component list: {e}")
        return 1

    comp_map = {c.name: c for c in components}

    # --- Select components ---
    if args.components:
        requested = list(args.components)
    else:
        requested = _select_components_cli(components)
        if not requested:
            print("No components selected. Nothing to add.")
            return 0

    # --- Validate ---
    unknown = [c for c in requested if c not in comp_map]
    if unknown:
        print(f"✗ Unknown components: {', '.join(unknown)}")
        print("  Run 'bootstrap list' to see available components.")
        return 1

    # --- Collect context (only what the requested components need) ---
    needed_vars = _needed_context_vars(requested, comp_map)
    context = _collect_context(project_name, state=state, needed=needed_vars)

    # --- Overwrite confirmation (--overwrite skips the prompt) ---
    overwrite_map = _confirm_overwrite_components(
        requested, state.installed_components, force_overwrite=args.overwrite
    )

    # --- Install ---
    print(f"\nAdding to {project_dir}/: {', '.join(requested)}\n")
    failed: list[str] = []
    for name in requested:
        ok = install_component(
            name,
            project_dir,
            context,
            overwrite=overwrite_map.get(name, False),
            repo_url=args.repo_url,
            branch=args.branch,
        )
        if not ok:
            failed.append(name)

    print()
    if failed:
        print(f"⚠  Completed with errors. Failed: {', '.join(failed)}")
        return 1

    _offer_post_install(requested, project_dir)

    print("✓ Done.")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: list
# ---------------------------------------------------------------------------

def cmd_list(args: argparse.Namespace) -> int:
    """List available components."""
    repo_url = getattr(args, "repo_url", None)
    branch = getattr(args, "branch", "main")

    try:
        components = get_components(repo_url=repo_url, branch=branch)
    except Exception as e:
        print(f"✗ Failed to load component list: {e}")
        return 1

    print("\nAvailable components:\n")
    max_name = max(len(c.name) for c in components)
    for spec in components:
        deps = f"  (needs: {', '.join(spec.requires)})" if spec.requires else ""
        print(f"  {spec.name:<{max_name}}  {spec.description}{deps}")
    print()
    return 0


# ---------------------------------------------------------------------------
# Subcommand: detect
# ---------------------------------------------------------------------------

def cmd_detect(args: argparse.Namespace) -> int:
    """Detect the current state of a project directory."""
    project_dir = Path(args.directory or ".")
    state = ProjectState.scan(project_dir)
    state.print_summary()

    try:
        components = get_components()
    except Exception:
        return 0

    missing = [c.name for c in components if c.name not in state.installed_components]
    if missing:
        print(f"Components not yet installed: {', '.join(missing)}")
        print(f"  Run: bootstrap add {' '.join(missing)}")
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _infer_project_name(project_dir: Path) -> str:
    """Try to read project name from pyproject.toml, fall back to dirname."""
    pyproject = project_dir / "pyproject.toml"
    if pyproject.exists():
        try:
            import tomllib

            data = tomllib.loads(pyproject.read_text())
            name = data.get("project", {}).get("name")
            if name:
                return name
        except Exception:
            pass
    return project_dir.resolve().name


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="bootstrap",
        description="Portable Python project scaffolding CLI.",
    )
    parser.add_argument(
        "--version", action="version", version=f"bootstrap {__version__}"
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    # --- new ---
    p_new = sub.add_parser("new", help="Scaffold a new project")
    p_new.add_argument("name", help="Project name (also used as directory name)")
    p_new.add_argument(
        "-d", "--directory",
        help="Target directory (defaults to <name>)",
    )
    p_new.add_argument(
        "-c", "--components",
        nargs="+",
        metavar="COMPONENT",
        help="Components to install — skips interactive selection",
    )
    _add_remote_args(p_new)
    p_new.set_defaults(func=cmd_new)

    # --- add ---
    p_add = sub.add_parser("add", help="Add component(s) to an existing project")
    p_add.add_argument(
        "components",
        nargs="*",
        metavar="COMPONENT",
        help="Component names to add (omit to pick interactively)",
    )
    p_add.add_argument(
        "-d", "--directory",
        help="Project directory (defaults to current directory)",
    )
    p_add.add_argument(
        "--overwrite",
        action="store_true",
        help="Silently overwrite existing files (skips the per-component prompt)",
    )
    _add_remote_args(p_add)
    p_add.set_defaults(func=cmd_add)

    # --- list ---
    p_list = sub.add_parser("list", help="List available components")
    _add_remote_args(p_list)
    p_list.set_defaults(func=cmd_list)

    # --- detect ---
    p_detect = sub.add_parser("detect", help="Detect current project configuration")
    p_detect.add_argument(
        "-d", "--directory",
        help="Directory to scan (defaults to current directory)",
    )
    p_detect.set_defaults(func=cmd_detect)

    args = parser.parse_args()
    return args.func(args)


def _add_remote_args(parser: argparse.ArgumentParser) -> None:
    """Add shared remote-control arguments to a subparser."""
    parser.add_argument(
        "--repo-url",
        default=None,
        help=f"Override template repo URL (default: {get_template_repo()})",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Template repo branch to pull from (default: main)",
    )


if __name__ == "__main__":
    sys.exit(main())
