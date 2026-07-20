# ── Setup & Environment ──────────────────────────────────────────────────────

.PHONY: install
install: ## Install the virtual environment and pre-commit hooks
	@echo "Creating virtual environment using uv"
	@uv sync --all-extras --dev
	@uv run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg

.PHONY: update
update: ## Upgrade all dependencies to their latest allowed versions
	@echo "Upgrading all dependencies"
	@uv sync --upgrade --all-extras --dev

.PHONY: lock
lock: ## Update the lock file
	@echo "Updating lock file with uv lock"
	@uv lock

.PHONY: venv
venv: ## Show Python version, venv path, and installed packages
	@echo "Python environment information:"
	@uv run python --version
	@uv run python -c "import sys; print('Virtual env path:', sys.prefix)"
	@echo "Installed packages:"
	@uv run pip list

.PHONY: reset-venv
reset-venv: ## Reset the virtual environment (requires confirmation)
	@echo "This will delete your .venv and reinstall everything."
	@printf "Are you sure? [y/N] " && read ans && [ "$${ans:-N}" = "y" ]
	@echo "Resetting environment..."
	@rm -rf .venv
	@uv sync --all-extras --dev
	@uv run pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg

.PHONY: clean-cache
clean-cache: ## Remove cache and temporary files (requires clean-cache-files hook in .pre-commit-config.yaml)
	@echo "Running cache cleanup"
	@uv run pre-commit run clean-cache-files

.PHONY: clean
clean: clean-build ## Remove all generated artefacts (.venv, dist, caches, coverage)
	@rm -rf .venv htmlcov .coverage .mypy_cache .pytest_cache .ruff_cache __pycache__
	@echo "Workspace cleaned"

# ── Code Quality ─────────────────────────────────────────────────────────────

.PHONY: ruff-check
ruff-check: ## Run ruff linter on src/ and tests/
	@echo "Running ruff check"
	@uv run ruff check src/ tests/

.PHONY: ruff-format
ruff-format: ## Run ruff formatter check on src/ and tests/
	@echo "Running ruff format check"
	@uv run ruff format --check src/ tests/

.PHONY: fix
fix: ## Auto-fix lint issues (ruff check --fix + ruff format)
	@echo "Auto-fixing lint issues"
	@uv run ruff check --fix src/ tests/
	@uv run ruff format src/ tests/

.PHONY: interrogate
interrogate: ## Check docstring coverage
	@echo "Running interrogate"
	@uv run interrogate src/ tests/

.PHONY: deptry
deptry: ## Analyse dependencies for unused/missing packages
	@echo "Running deptry"
	@uv run deptry .

.PHONY: typecheck
typecheck: ## Run mypy static type checker
	@echo "Running mypy..."
	@uv run mypy

.PHONY: lint
lint: ruff-check ruff-format interrogate deptry ## Run all Python linting and analysis checks
	@echo "All linting checks completed"

# ── Security & Validation ────────────────────────────────────────────────────

.PHONY: gitleaks
gitleaks: ## Scan for hardcoded secrets (requires gitleaks hook in .pre-commit-config.yaml)
	@echo "Running gitleaks"
	@uv run pre-commit run gitleaks

.PHONY: file-checks
file-checks: ## Run all file validation checks (requires hooks in .pre-commit-config.yaml)
	@echo "Running file validation checks"
	@uv run pre-commit run check-case-conflict
	@uv run pre-commit run check-merge-conflict
	@uv run pre-commit run end-of-file-fixer
	@uv run pre-commit run trailing-whitespace
	@uv run pre-commit run check-added-large-files
	@uv run pre-commit run mixed-line-ending
	@uv run pre-commit run check-json
	@uv run pre-commit run pretty-format-json
	@uv run pre-commit run check-toml
	@uv run pre-commit run check-yaml
	@uv run pre-commit run check-xml
	@uv run pre-commit run check-executables-have-shebangs
	@uv run pre-commit run check-shebang-scripts-are-executable

.PHONY: validate
validate: file-checks gitleaks clean-cache ## Run all validation and security checks
	@echo "All validation checks completed"

# ── Testing ───────────────────────────────────────────────────────────────────

.PHONY: test
test: ## Run tests with pytest
	@echo "Testing code: Running pytest"
	@uv run pytest

.PHONY: test-cov
test-cov: ## Run tests with coverage and generate HTML report
	@uv run pytest --cov --cov-report=term-missing --cov-report=html
	@echo "HTML coverage report: htmlcov/index.html"

# ── Pre-commit & Hooks ───────────────────────────────────────────────────────

.PHONY: pre-commit-staged
pre-commit-staged: ## Run pre-commit hooks on currently staged files
	@echo "Running pre-commit hooks on staged files"
	@uv run pre-commit run

.PHONY: pre-commit-all
pre-commit-all: ## Run pre-commit hooks on all files in the repo
	@echo "Running pre-commit hooks on all files"
	@uv run pre-commit run --all-files

.PHONY: hooks
hooks: lint validate ## Run all hooks consolidated (lint + validate)
	@echo "All pre-commit hooks completed successfully"

# ── Quality Gates ─────────────────────────────────────────────────────────────

.PHONY: check
check: test ## Run all code quality tools (tests + lock check + pre-commit + mypy)
	@echo "Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "Static type checking: Running mypy"
	@uv run mypy

# ── Build ─────────────────────────────────────────────────────────────────────

.PHONY: clean-build
clean-build: ## Remove build artefacts (dist/)
	@echo "Removing build artefacts"
	@rm -rf dist/

.PHONY: build
build: clean-build ## Build wheel and sdist
	@echo "Building package"
	@uv build

# ── Run ──────────────────────────────────────────────────────────────────────

# Set PACKAGE_NAME at the top of your Makefile or pass it on the command line:
#   make run PACKAGE_NAME=myapp
PACKAGE_NAME ?= $(shell basename $(CURDIR) | tr - _)

.PHONY: run
run: ## Run the project (override PACKAGE_NAME as needed)
	@uv run python -m $(PACKAGE_NAME)

# ── Docs ──────────────────────────────────────────────────────────────────────

.PHONY: docs-test
docs-test: ## Build MkDocs and fail on any warning
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation at http://127.0.0.1:8000
	@uv run mkdocs serve

# ── Utilities ─────────────────────────────────────────────────────────────────

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
