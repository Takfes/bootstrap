# Component: container

**Purpose:** A production-ready Dockerfile using uv for fast, reproducible dependency installation, built as a multi-stage image to keep the final runtime image small. Optional — add when the project needs to be containerised for deployment.

---

## Files Delivered

| File | Description |
|------|-------------|
| `Dockerfile` | Multi-stage uv-based build |
| `.dockerignore` | Excludes dev artefacts from the build context |

---

## `Dockerfile` — Build Strategy

**Multi-stage build** with two stages:

### Stage 1: `builder`

Base: `python:{{python_version}}-slim`

1. Copies the uv binary directly from the official uv image (`ghcr.io/astral-sh/uv:latest`) — no pip install of uv needed.
2. Copies `pyproject.toml` and `uv.lock` first (before source code) so Docker can cache the dependency layer. If only source code changes, dependencies don't reinstall.
3. `uv sync --frozen --no-install-project --no-dev` — installs all runtime dependencies into `.venv` without installing the project itself yet.
4. Copies source code.
5. `uv sync --frozen --no-dev` — installs the project into the already-populated `.venv`.

### Stage 2: `runtime`

Base: same `python:{{python_version}}-slim` (no uv, no build tools — clean runtime image).

1. Copies only `.venv` and `src/` from the builder stage.
2. Sets `PATH` to include `.venv/bin` so Python packages are directly accessible.
3. Sets `PYTHONUNBUFFERED=1` for clean log output in container environments.
4. `CMD ["python", "-m", "{{package_name}}"]` — runs the package as a module. Adjust this to your entry point.

**Result:** a minimal runtime image with no build toolchain, no uv binary, no dev dependencies.

---

## `.dockerignore`

Excludes: `.venv/`, `dist/`, `build/`, `.git/`, `.github/`, mypy/ruff/pytest cache directories, `__pycache__`, compiled Python files (`.pyc`), egg-info directories, and environment files (`.env`, `.env.*`).

The `.env` exclusion is important — prevents secrets from accidentally entering the build context.

---

## Layout Note

The template assumes **src layout** (`src/{{package_name}}/`). If your project uses flat layout, adjust the `COPY src/ ./src/` line to `COPY {{package_name}}/ ./{{package_name}}/` and update the CMD accordingly.

The `bootstrap detect` command identifies the layout so this can be handled automatically in a future version.

---

## Template Variables Used

`{{python_version}}`, `{{package_name}}`

---

## Building and Running

```bash
docker build -t {{repo_name}} .
docker run --rm {{repo_name}}
```

---

## Future Refinements

- Add a `docker-compose.yml` for local multi-service development (e.g. project + database)
- Add a `Podman`-compatible variant (already compatible in most cases — Podman is OCI-compliant)
- Add health check instruction (`HEALTHCHECK`) for web service projects
- Add non-root user creation for security hardening in production images
- Consider `CMD` vs `ENTRYPOINT` split for more flexible container invocation
