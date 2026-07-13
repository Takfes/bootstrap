# Multi-stage build using uv for fast, reproducible dependency installation.
# https://docs.astral.sh/uv/guides/integration/docker/

FROM python:{{python_version}}-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-install-project --no-dev

# Copy source
COPY src/ ./src/

# Install the project itself
RUN uv sync --frozen --no-dev

# --- Runtime stage ---
FROM python:{{python_version}}-slim AS runtime

WORKDIR /app

# Copy the pre-built virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source
COPY --from=builder /app/src ./src/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "{{package_name}}"]
