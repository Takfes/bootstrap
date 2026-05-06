"""Dynamic component manifest loader.

Resolution order for finding manifest.toml:
1. BOOTSTRAP_COMPONENTS_DIR env var — explicit local path override
2. components/manifest.toml relative to the package source tree (local dev)
3. Fetch from the remote template repo via sparse-checkout (installed mode)
"""

import os
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

from .components import ComponentSpec


def load_manifest(repo_url: str | None = None, branch: str = "main") -> list[ComponentSpec]:
    """Load component specs from manifest.toml.

    Args:
        repo_url: Template repo URL — used only when local manifest is not found.
        branch: Branch to pull from when fetching remotely.

    Returns:
        Ordered list of ComponentSpec objects as declared in the manifest.

    Raises:
        RuntimeError: If the manifest cannot be found or parsed.
    """
    from .installer import get_template_repo

    repo_url = repo_url or get_template_repo()

    # 1. Explicit env var override
    env_dir = os.environ.get("BOOTSTRAP_COMPONENTS_DIR")
    if env_dir:
        manifest_path = Path(env_dir) / "manifest.toml"
        if manifest_path.exists():
            return _parse_manifest(manifest_path)

    # 2. Local dev mode — package lives at src/bootstrap/, components/ is three levels up
    local_manifest = Path(__file__).parent.parent.parent / "components" / "manifest.toml"
    if local_manifest.exists():
        return _parse_manifest(local_manifest)

    # 3. Fetch from remote repo
    return _fetch_remote_manifest(repo_url, branch)


def _parse_manifest(path: Path) -> list[ComponentSpec]:
    """Parse a manifest.toml file into ComponentSpec objects."""
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    specs: list[ComponentSpec] = []
    for item in data.get("components", []):
        specs.append(
            ComponentSpec(
                name=item["name"],
                description=item["description"],
                repo_path=item["repo_path"],
                requires=item.get("requires", []),
                optional=item.get("optional", True),
            )
        )
    return specs


def _fetch_remote_manifest(repo_url: str, branch: str) -> list[ComponentSpec]:
    """Fetch components/manifest.toml from remote repo via sparse-checkout."""
    temp_dir = Path(tempfile.mkdtemp(prefix="bootstrap_manifest_"))
    try:
        _run(["git", "init"], temp_dir)
        _run(["git", "remote", "add", "origin", repo_url], temp_dir)
        _run(["git", "config", "core.sparseCheckout", "true"], temp_dir)

        sparse_file = temp_dir / ".git" / "info" / "sparse-checkout"
        sparse_file.parent.mkdir(parents=True, exist_ok=True)
        sparse_file.write_text("components/manifest.toml\n")

        result = subprocess.run(
            ["git", "pull", "origin", branch],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to fetch manifest from {repo_url} (branch: {branch}).\n"
                f"{result.stderr.strip()}"
            )

        manifest_path = temp_dir / "components" / "manifest.toml"
        if not manifest_path.exists():
            raise RuntimeError(
                "components/manifest.toml not found in the template repo. "
                "Ensure the repo contains this file."
            )

        return _parse_manifest(manifest_path)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def _run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {result.stderr.strip()}")
