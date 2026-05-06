# bootstrap — development commands

# List available commands
default:
    @just --list

# Install dev dependencies
install:
    uv sync

# Run the CLI locally (pass args after --)
run *args:
    uv run bootstrap {{args}}

# Lint and format
lint:
    uv run ruff check src/
    uv run ruff format --check src/

# Fix lint issues
fix:
    uv run ruff check --fix src/
    uv run ruff format src/

# Type check
typecheck:
    uv run mypy src/

# Run all checks
check: lint typecheck

# Test the CLI end-to-end (dry run against a temp dir)
test-cli:
    @echo "Testing 'bootstrap list'..."
    uv run bootstrap list
    @echo "Testing 'bootstrap detect'..."
    uv run bootstrap detect

# Build the package
build:
    uv build

# Show what would be published
publish-dry:
    uv publish --dry-run
