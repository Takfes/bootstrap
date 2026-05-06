"""Component installer.

Orchestrates fetching a component from the template repo and installing it
into a target project directory, with template variable substitution and
smart handling of existing projects.
"""

import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path

from .components import get_component
from .fetcher import FetchError, fetch_component

# Template variable pattern: {{variable_name}}
_VAR_RE = re.compile(r"\{\{(\w+)\}\}")

# Default template repo — override with BOOTSTRAP_TEMPLATE_REPO env var.
# Points to THIS repo once published.
DEFAULT_TEMPLATE_REPO = "https://github.com/Takfes/bootstrap.git"


def get_template_repo() -> str:
    """Return the template repo URL, respecting env var override."""
    return os.environ.get("BOOTSTRAP_TEMPLATE_REPO", DEFAULT_TEMPLATE_REPO)


def substitute(text: str, context: dict[str, str]) -> str:
    """Replace ``{{variable}}`` placeholders with values from context.

    Unknown variables are left as-is rather than raising an error.
    """
    def _replace(match: re.Match) -> str:
        return context.get(match.group(1), match.group(0))

    return _VAR_RE.sub(_replace, text)


def install_component(
    name: str,
    project_dir: Path,
    context: dict[str, str],
    *,
    overwrite: bool = False,
    repo_url: str | None = None,
    branch: str = "main",
) -> bool:
    """Fetch and install a single component into project_dir.

    Args:
        name: Component name, e.g. ``"uv"``, ``"devcontainer"``.
        project_dir: Root of the target project.
        context: Template substitution variables (project_name, github_org, …).
        overwrite: If True, overwrite existing files silently.
        repo_url: Override the template repo URL (for testing or forks).
        branch: Branch to pull from.

    Returns:
        True on success, False on failure.
    """
    spec = get_component(name)
    if spec is None:
        print(
            f"  ✗ Unknown component '{name}'. "
            f"Run 'bootstrap list' to see available components."
        )
        return False
    repo_url = repo_url or get_template_repo()

    print(f"  → Fetching '{name}'...")
    try:
        with fetch_component(spec.repo_path, repo_url, branch=branch) as result:
            # Special case: uv on an existing project — merge, don't overwrite
            if name == "uv" and (project_dir / "pyproject.toml").exists():
                success = _merge_pyproject(result.path, project_dir, context)
            else:
                _copy_files(result.path, project_dir, context, overwrite=overwrite)
                success = True

    except FetchError as e:
        print(f"  ✗ Fetch failed for '{name}': {e}")
        return False

    if success:
        _post_install(name, project_dir)
        print(f"  ✓ Installed '{name}'")

    return success


def _copy_files(
    component_dir: Path,
    project_dir: Path,
    context: dict[str, str],
    *,
    overwrite: bool = False,
) -> None:
    """Copy all files from component_dir into project_dir.

    - Applies {{variable}} substitution to file *contents* and *paths*.
    - Strips ``.tmpl`` extension from destination filename.
    - Skips existing files unless overwrite=True.
    """
    for src in component_dir.rglob("*"):
        if src.is_dir():
            continue

        rel = src.relative_to(component_dir)

        # Substitute variables in each path segment
        substituted_parts = [substitute(p, context) for p in rel.parts]
        dest_rel = Path(*substituted_parts)

        # Strip .tmpl extension
        if dest_rel.suffix == ".tmpl":
            dest_rel = dest_rel.with_suffix("")

        dest = project_dir / dest_rel

        if dest.exists() and not overwrite:
            print(f"    skip  {dest_rel}  (exists — use --overwrite to replace)")
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            content = src.read_text(encoding="utf-8")
            dest.write_text(substitute(content, context), encoding="utf-8")
        except UnicodeDecodeError:
            shutil.copy2(src, dest)  # Binary file — copy as-is


def _merge_pyproject(
    component_dir: Path,
    project_dir: Path,
    context: dict[str, str],
) -> bool:
    """Merge tool config sections from template into an existing pyproject.toml.

    Reads ``[tool.*]`` sections from the template and appends any that are
    missing from the existing file. Leaves existing content untouched.
    """
    template_file = component_dir / "pyproject.toml"
    if not template_file.exists():
        print("  ✗ No pyproject.toml found in uv component")
        return False

    template_text = substitute(template_file.read_text(), context)
    existing_path = project_dir / "pyproject.toml"
    existing_text = existing_path.read_text()

    # Extract [tool.*] sections from template using simple text splitting.
    # Each section runs from its header to the next top-level header or EOF.
    section_re = re.compile(
        r"^(\[tool\.[^\]]+\][^\[]*)",
        re.MULTILINE | re.DOTALL,
    )
    template_sections = section_re.findall(template_text)

    added: list[str] = []
    for section in template_sections:
        header_match = re.match(r"\[([^\]]+)\]", section.strip())
        if not header_match:
            continue
        header = header_match.group(1)
        if f"[{header}]" not in existing_text:
            existing_text += f"\n{section.rstrip()}\n"
            added.append(header)

    if added:
        existing_path.write_text(existing_text)
        print(f"    merged: {', '.join(added)}")
    else:
        print("    pyproject.toml already has all tool configs — nothing to merge")

    return True


def _post_install(name: str, project_dir: Path) -> None:
    """Run any post-install commands for a component."""
    commands: dict[str, list[list[str]]] = {
        "uv": [["uv", "sync"]],
        "precommit": [["pre-commit", "install"]],
    }
    for cmd in commands.get(name, []):
        try:
            subprocess.run(cmd, cwd=project_dir, check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Post-install commands are best-effort — don't fail the install
            tool = cmd[0]
            print(f"    note: '{tool}' not available — run manually when ready")
