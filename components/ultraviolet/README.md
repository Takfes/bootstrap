# {{project_name}}

{{description_or_placeholder}}

Requires Python {{python_version}}+.

---

## Installation

```bash
uv sync --all-extras --dev
```

Creates a `.venv` and installs the project along with its dev tools (ruff, mypy, pytest, deptry, ...).

## Running

```bash
uv run python -m {{package_name}}
```

## Development

Everyday commands, run through `uv`:

```bash
uv run pytest                       # run the test suite
uv run pytest --cov                 # ... with coverage
uv run ruff check .                 # lint
uv run ruff check --fix .           # lint, auto-fixing what it can
uv run ruff format .                # format
uv run mypy                         # type check
uv run deptry .                     # find unused / missing dependencies
```

If this project also has a `justfile` or `Makefile` — added via the bootstrap `justfile`/`makefile` component — prefer that instead: run `just` or `make help` to see the full, pre-wired set of commands (install, lint, test, build, docs, ...).

## Project Structure

```
{{package_name}}/   # source (src/{{package_name}}/ if you chose the "src" layout)
tests/               # test suite
pyproject.toml       # dependencies + tool config (ruff, mypy, pytest, deptry, ...)
```

## Code Quality

If a `.pre-commit-config.yaml` is present — added via the bootstrap `precommit` component — install the git hooks once:

```bash
uv run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
```

They then run automatically on `git commit` / `git push`. To run every hook against the whole repo on demand:

```bash
uv run pre-commit run --all-files
```

## License

{{license_type}} (declared in `pyproject.toml`). Full text in `LICENSE`, if the bootstrap `license` component was added.
