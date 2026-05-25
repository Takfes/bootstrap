# {{project_name}}

> {{description}}

[![CI](https://github.com/{{github_org}}/{{repo_name}}/actions/workflows/main.yml/badge.svg)](https://github.com/{{github_org}}/{{repo_name}}/actions)
[![Coverage](https://codecov.io/gh/{{github_org}}/{{repo_name}}/branch/main/graph/badge.svg)](https://codecov.io/gh/{{github_org}}/{{repo_name}})
[![PyPI](https://img.shields.io/pypi/v/{{repo_name}})](https://pypi.org/project/{{repo_name}}/)
[![Python](https://img.shields.io/pypi/pyversions/{{repo_name}})](https://pypi.org/project/{{repo_name}}/)
[![License](https://img.shields.io/github/license/{{github_org}}/{{repo_name}})](LICENSE)

---

## Installation

```bash
# pip
pip install {{repo_name}}

# uv (recommended)
uv add {{repo_name}}
```

## Quick Start

```python
import {{package_name}}

# TODO: add a minimal usage example here
```

## Development

### Setup

```bash
git clone https://github.com/{{github_org}}/{{repo_name}}.git
cd {{repo_name}}
uv sync --all-extras --dev
pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

### Common commands

**With `just`:**

| Command | Description |
|---------|-------------|
| `just check` | Full quality gate: lint + typecheck + tests + deps |
| `just test` | Run the test suite |
| `just fix` | Auto-fix all lint issues |
| `just docs-serve` | Serve docs locally with live reload |

**With `make`:**

| Command | Description |
|---------|-------------|
| `make check` | Full quality gate |
| `make test` | Run the test suite |
| `make fix` | Auto-fix all lint issues |
| `make docs` | Serve docs locally |

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit following [Conventional Commits](https://www.conventionalcommits.org/)
4. Push and open a Pull Request

## License

{{license_type}} © {{year}} {{author}}
