"""Component registry — dynamic catalogue of available template components."""

from dataclasses import dataclass
from functools import lru_cache


@dataclass
class ComponentSpec:
    """Specification for a single template component."""

    name: str
    description: str
    repo_path: str       # Path within the template repo, e.g. "components/uv"
    requires: list[str]  # Component names that must be present first
    optional: bool = True


@lru_cache(maxsize=4)
def get_components(repo_url: str | None = None, branch: str = "main") -> list[ComponentSpec]:
    """Load all available components from manifest.toml.

    Results are cached per (repo_url, branch) pair for the lifetime of the process.
    """
    from .manifest import load_manifest

    return load_manifest(repo_url=repo_url, branch=branch)


def get_component(
    name: str,
    repo_url: str | None = None,
    branch: str = "main",
) -> ComponentSpec | None:
    """Return the ComponentSpec for a given name, or None if not found."""
    return next((c for c in get_components(repo_url, branch) if c.name == name), None)
