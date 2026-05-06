"""Sparse-checkout fetcher for template components.

Adapted from the skill-downloader utility. Provides a clean programmatic API
(no interactive prompts) for fetching specific directories from a Git repo via
git sparse-checkout — only the requested path is downloaded, not the full repo.

This is the shared primitive used by both the CLI and the agentic skill.
"""

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class FetchError(Exception):
    """Raised when a component cannot be fetched from the remote repo."""


@dataclass
class FetchResult:
    """Result of a fetch operation. Use as a context manager for auto-cleanup.

    Example::

        with fetch_component("components/uv", REPO_URL) as result:
            # result.path points to the downloaded component directory
            shutil.copytree(result.path, dest)
        # temp dir is cleaned up automatically on exit
    """

    path: Path        # Path to the downloaded component directory
    _temp_dir: Path   # Root temp dir — cleaned up on close()

    def cleanup(self) -> None:
        """Remove the temporary directory created during fetch."""
        shutil.rmtree(self._temp_dir, ignore_errors=True)

    def __enter__(self) -> "FetchResult":
        return self

    def __exit__(self, *args: object) -> None:
        self.cleanup()


def fetch_component(
    component_path: str,
    repo_url: str,
    branch: str = "main",
) -> FetchResult:
    """Fetch a component directory from a remote repo via git sparse-checkout.

    Downloads only the specified subdirectory. The caller is responsible for
    cleanup — prefer using the returned FetchResult as a context manager.

    Args:
        component_path: Path within the repo, e.g. ``"components/uv"``.
        repo_url: HTTPS URL to the Git repository.
        branch: Branch to pull from. Defaults to ``"main"``.

    Returns:
        FetchResult with ``.path`` pointing to the downloaded content.

    Raises:
        FetchError: If the component cannot be fetched for any reason.
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="bootstrap_fetch_"))

    try:
        _git(["init"], cwd=temp_dir)
        _git(["remote", "add", "origin", repo_url], cwd=temp_dir)
        _git(["config", "core.sparseCheckout", "true"], cwd=temp_dir)

        sparse_file = temp_dir / ".git" / "info" / "sparse-checkout"
        sparse_file.parent.mkdir(parents=True, exist_ok=True)
        sparse_file.write_text(f"{component_path}/*\n")

        result = subprocess.run(
            ["git", "pull", "origin", branch],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise FetchError(
                f"Failed to pull '{component_path}' from {repo_url} "
                f"(branch: {branch}).\n{result.stderr.strip()}"
            )

        # Navigate into the nested component directory
        component_dir = temp_dir
        for part in component_path.split("/"):
            component_dir = component_dir / part

        if not component_dir.exists():
            raise FetchError(
                f"Path '{component_path}' not found in repo after pull. "
                f"Check the path and branch are correct."
            )

        return FetchResult(path=component_dir, _temp_dir=temp_dir)

    except FetchError:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise FetchError(f"Unexpected error fetching component: {e}") from e


def _git(cmd: list[str], cwd: Path) -> None:
    """Run a git subcommand, raising FetchError on non-zero exit."""
    result = subprocess.run(
        ["git", *cmd],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise FetchError(
            f"git {' '.join(cmd)} failed: {result.stderr.strip()}"
        )
