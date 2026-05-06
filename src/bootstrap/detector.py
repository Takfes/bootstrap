"""Project state detection.

Scans a directory to understand what's already set up, so the installer
can make smart decisions about what to add vs. skip.
"""

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Layout = Literal["src", "flat", "unknown"]


@dataclass
class ProjectState:
    """Snapshot of a project directory's current configuration."""

    path: Path

    # Tool presence flags
    is_git_repo: bool = False
    has_pyproject: bool = False
    has_uv_lock: bool = False
    has_precommit: bool = False
    has_devcontainer: bool = False
    has_github_actions: bool = False
    has_dockerfile: bool = False
    has_mkdocs: bool = False
    has_justfile: bool = False
    has_agents: bool = False

    # Project structure
    layout: Layout = "unknown"

    # Git / GitHub metadata (auto-detected from remote)
    github_remote: str | None = None
    github_org: str | None = None
    github_repo_name: str | None = None

    # Derived: which bootstrap components are already installed
    installed_components: set[str] = field(default_factory=set)

    @classmethod
    def scan(cls, path: Path) -> "ProjectState":
        """Scan a directory and return its current state.

        Args:
            path: Directory to scan. Typically the project root.

        Returns:
            Populated ProjectState instance.
        """
        state = cls(path=path)

        # --- Tool presence ---
        state.is_git_repo = (path / ".git").exists()
        state.has_pyproject = (path / "pyproject.toml").exists()
        state.has_uv_lock = (path / "uv.lock").exists()
        state.has_precommit = (path / ".pre-commit-config.yaml").exists()
        state.has_devcontainer = (path / ".devcontainer").exists()
        state.has_github_actions = (path / ".github" / "workflows").exists()
        state.has_dockerfile = (path / "Dockerfile").exists()
        state.has_mkdocs = (path / "mkdocs.yml").exists()
        state.has_justfile = (
            (path / "justfile").exists() or (path / "Justfile").exists()
        )
        state.has_agents = (
            (path / "CLAUDE.md").exists()
            or (path / "AGENTS.md").exists()
            or (path / ".claude").exists()
        )

        # --- Layout detection ---
        if (path / "src").is_dir():
            state.layout = "src"
        elif list(path.glob("*.py")) or list(path.glob("*/__init__.py")):
            state.layout = "flat"

        # --- GitHub remote parsing ---
        if state.is_git_repo:
            try:
                result = subprocess.run(
                    ["git", "remote", "get-url", "origin"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    remote = result.stdout.strip()
                    state.github_remote = remote
                    # Parse org/repo from both HTTPS and SSH formats:
                    #   https://github.com/org/repo.git
                    #   git@github.com:org/repo.git
                    clean = remote.removesuffix(".git")
                    if "github.com" in clean:
                        slug = clean.split("github.com")[-1].lstrip("/:")
                        parts = slug.split("/")
                        if len(parts) >= 2:
                            state.github_org = parts[0]
                            state.github_repo_name = parts[1]
            except Exception:
                pass  # Non-fatal — remote info is optional

        # --- Installed components ---
        if state.has_pyproject or state.has_uv_lock:
            state.installed_components.add("uv")
        if state.has_precommit:
            state.installed_components.add("precommit")
        if state.has_github_actions:
            state.installed_components.add("ci")
        if state.has_devcontainer:
            state.installed_components.add("devcontainer")
        if state.has_dockerfile:
            state.installed_components.add("container")
        if state.has_mkdocs:
            state.installed_components.add("docs")
        if state.has_justfile:
            state.installed_components.add("justfile")
        if state.has_agents:
            state.installed_components.add("agents")

        return state

    def missing_components(self, requested: list[str]) -> list[str]:
        """Return requested components that are not yet installed."""
        return [c for c in requested if c not in self.installed_components]

    def print_summary(self) -> None:
        """Print a human-readable summary of detected project state."""
        print(f"\nProject: {self.path}")
        print(f"  Git repo:      {'yes' if self.is_git_repo else 'no'}")
        print(f"  Layout:        {self.layout}")
        if self.github_org:
            print(f"  GitHub:        {self.github_org}/{self.github_repo_name}")
        print(f"  Components installed: ", end="")
        if self.installed_components:
            print(", ".join(sorted(self.installed_components)))
        else:
            print("none detected")
        print()
