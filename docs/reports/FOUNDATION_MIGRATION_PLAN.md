# Foundation Migration Plan - vibe-agency
**Date:** 2025-11-15
**Session:** claude/foundation-hardening-uv-migration-01UniXx3ZaAgpePBtgYHebZF
**Based on:** FOUNDATION_ASSESSMENT.md

---

## Executive Summary

**Goal:** Transform "whacky haufen" → Production-ready foundation

**Strategy:** Incremental, backward-compatible migration
**Timeline:** 3-4 hours (this session)
**Risk Level:** LOW (fully reversible)

---

## Migration Priorities

### Priority 1: CRITICAL (Execute This Session)
**Timeline:** 3-4 hours
**Risk:** LOW
**Impact:** HIGH

Tasks:
1. ✅ Install and configure uv
2. ✅ Create pyproject.toml (consolidate configs)
3. ✅ Generate uv.lock (deterministic builds)
4. ✅ Create Makefile (automation)
5. ✅ Update setup.sh (use uv)
6. ✅ Update devcontainer (use uv)
7. ✅ Update CI workflows (use uv)
8. ✅ Update documentation
9. ✅ Validate migration

### Priority 2: HIGH (Next Session)
**Timeline:** 2-3 hours
**Risk:** LOW
**Impact:** MEDIUM

Tasks:
1. Add mypy strict mode
2. Add complexity checks (ruff mccabe)
3. Audit core_orchestrator.py (1284 lines)
4. Consolidate CI workflows

### Priority 3: MEDIUM (Backlog)
**Timeline:** 1-2 hours each
**Risk:** LOW
**Impact:** LOW-MEDIUM

Tasks:
1. Add property-based testing (hypothesis)
2. Enhance security scanning (pip-audit in CI)
3. Update architecture documentation

---

## Phase 1: UV Installation & Setup (30 min)

### Step 1.1: Install UV
```bash
# Install uv (handled by CI/devcontainer later)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
# Expected: uv 0.x.x
```

**Success Criteria:**
- ✅ `uv --version` works
- ✅ `uv` in PATH

### Step 1.2: Initialize UV Project
```bash
# Initialize (preserves requirements.txt)
uv init --no-workspace

# This creates:
# - pyproject.toml (minimal)
# - .python-version (if not exists)
```

**Success Criteria:**
- ✅ pyproject.toml created
- ✅ requirements.txt unchanged

### Step 1.3: Generate Lock File
```bash
# Sync dependencies and create lock file
uv sync

# This creates:
# - uv.lock (deterministic lock file)
# - .venv/ (virtual environment)
```

**Success Criteria:**
- ✅ uv.lock exists
- ✅ .venv/ created
- ✅ All dependencies installed

### Step 1.4: Test UV Installation
```bash
# Verify imports work
uv run python -c "import yaml; import requests; import bs4; print('✅ All imports work')"

# Run existing tests with uv
uv run pytest tests/ -v

# Expected: All tests pass (same as before)
```

**Success Criteria:**
- ✅ Imports work
- ✅ Tests pass (same results as pip)

---

## Phase 2: Configuration Consolidation (45 min)

### Step 2.1: Create Comprehensive pyproject.toml

**File:** `/home/user/vibe-agency/pyproject.toml`

```toml
[project]
name = "vibe-agency"
version = "1.0.0"
description = "File-based prompt framework for AI-assisted software project planning"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }

authors = [
    { name = "vibe-agency team" }
]

# Dependencies from requirements.txt
dependencies = [
    "pyyaml>=6.0.1",
    "requests>=2.31.0",
    "beautifulsoup4>=4.12.0",
    "google-api-python-client>=2.100.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=24.1.0",
    "ruff>=0.1.0",
    "isort>=5.13.0",
    "yamllint>=1.35.0",
    "mypy>=1.7.0",
]

security = [
    "pip-audit>=2.6.0",
    "detect-secrets>=1.4.0",
]

hooks = [
    "pre-commit>=3.6.0",
]

# Install all extras with: uv sync --extra dev --extra security --extra hooks
all = [
    "vibe-agency[dev,security,hooks]",
]

[project.scripts]
vibe-cli = "vibe_cli:main"

# ============================================================================
# TOOL CONFIGURATIONS (Consolidated from .flake8, ruff.toml, etc.)
# ============================================================================

[tool.ruff]
line-length = 100
target-version = "py311"

# Ruff replaces: flake8, isort, black, bandit, etc.
[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "F",     # pyflakes
    "I",     # isort (import sorting)
    "B",     # flake8-bugbear
    "SIM",   # flake8-simplify
    "UP",    # pyupgrade
    "S",     # flake8-bandit (security)
    "RUF",   # ruff-specific rules
    "C90",   # mccabe complexity
]

ignore = [
    "E501",  # line-too-long (handled by formatter)
    "S101",  # assert-used (OK in tests)
]

# Complexity checks (stricter than flake8's max-complexity=10)
[tool.ruff.lint.mccabe]
max-complexity = 15

# Per-file ignores
[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = ["E402", "S101"]  # Allow late imports and asserts in tests
"test_*.py" = ["E402", "S101"]
"*-cli.py" = ["E402"]  # CLI scripts may need path manipulation

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
    "--disable-warnings",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

# ============================================================================
# MYPY CONFIGURATION (Type Checking)
# ============================================================================

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false  # Start lenient, tighten gradually
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Gradually enable strict mode per module
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

# ============================================================================
# BLACK CONFIGURATION (Code Formatting)
# ============================================================================

[tool.black]
line-length = 100
target-version = ["py311"]
include = '\.pyi?$'
extend-exclude = '''
/(
  # Defaults
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

# ============================================================================
# ISORT CONFIGURATION (Import Sorting)
# ============================================================================

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

# ============================================================================
# COVERAGE CONFIGURATION
# ============================================================================

[tool.coverage.run]
source = ["agency_os"]
omit = [
    "tests/*",
    "**/__pycache__/*",
    "**/test_*.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]

# ============================================================================
# UV CONFIGURATION
# ============================================================================

[tool.uv]
dev-dependencies = []  # Managed via [project.optional-dependencies]

# ============================================================================
# BUILD SYSTEM
# ============================================================================

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

**Success Criteria:**
- ✅ pyproject.toml valid (TOML syntax)
- ✅ All configs consolidated
- ✅ `uv sync` works with new config

### Step 2.2: Update UV Sync with Extras
```bash
# Sync with all optional dependencies
uv sync --all-extras

# Or selectively:
# uv sync --extra dev --extra security --extra hooks
```

**Success Criteria:**
- ✅ All dev dependencies installed
- ✅ Tests still pass

### Step 2.3: Validate Consolidation
```bash
# Test ruff with new config
uv run ruff check .

# Test pytest with new config
uv run pytest tests/ -v

# Test mypy (new)
uv run mypy agency_os/ --install-types --non-interactive || echo "⚠️ Type errors expected (baseline)"
```

**Success Criteria:**
- ✅ Ruff works (same or better results)
- ✅ Pytest works (same results)
- ✅ Mypy runs (errors OK for now)

---

## Phase 3: Makefile Creation (30 min)

### Step 3.1: Create Makefile

**File:** `/home/user/vibe-agency/Makefile`

```makefile
# ============================================================================
# VIBE AGENCY - MAKEFILE
# ============================================================================
# Self-running system automation for non-technical users
#
# Quick Start:
#   make install    # One-command setup
#   make test       # Run all tests
#   make lint       # Check code quality
#   make ci         # Run full CI validation
#
# ============================================================================

.PHONY: help install clean test lint format ci validate-deps

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# HELP
# ============================================================================

help:  ## Show this help message
	@echo "📚 Vibe Agency - Available Commands"
	@echo "===================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick Start:"
	@echo "  make install   # Setup environment"
	@echo "  make test      # Run tests"
	@echo "  make ci        # Full validation"

# ============================================================================
# INSTALLATION
# ============================================================================

install: clean  ## Install all dependencies and setup environment
	@echo "🔧 Installing dependencies with uv..."
	uv sync --all-extras
	@echo "🪝 Setting up pre-commit hooks..."
	uv run pre-commit install
	@echo "🔍 Validating knowledge bases..."
	@if [ -f "validate_knowledge_index.py" ]; then \
		uv run python validate_knowledge_index.py; \
	else \
		echo "⚠️  validate_knowledge_index.py not found (skipping)"; \
	fi
	@echo ""
	@echo "✅ Environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  make test      # Run tests"
	@echo "  make lint      # Check quality"
	@echo "  ./vibe-cli run <project-id>"

install-dev: clean  ## Install only dev dependencies (faster)
	@echo "🔧 Installing dev dependencies..."
	uv sync --extra dev
	@echo "✅ Dev environment ready!"

# ============================================================================
# TESTING
# ============================================================================

test:  ## Run all tests
	@echo "🧪 Running test suite..."
	uv run pytest tests/ -v --tb=short

test-cov:  ## Run tests with coverage report
	@echo "🧪 Running tests with coverage..."
	uv run pytest tests/ -v --cov=agency_os --cov-report=term-missing --cov-report=html

test-unit:  ## Run only unit tests
	@echo "🧪 Running unit tests..."
	uv run pytest tests/ -v -m unit

test-integration:  ## Run only integration tests
	@echo "🧪 Running integration tests..."
	uv run pytest tests/ -v -m integration

test-fast:  ## Run tests (skip slow tests)
	@echo "🧪 Running fast tests..."
	uv run pytest tests/ -v -m "not slow"

# ============================================================================
# CODE QUALITY
# ============================================================================

lint:  ## Run all linters
	@echo "🔍 Running linters..."
	@echo "  → Ruff (linter)..."
	uv run ruff check .
	@echo "  → Ruff (formatter check)..."
	uv run ruff format --check .
	@echo "  → YAMLlint..."
	uv run yamllint -c .yamllint agency_os/ system_steward_framework/ || true
	@echo "✅ Linting complete!"

format:  ## Auto-format code
	@echo "🎨 Formatting code..."
	uv run ruff check --fix .
	uv run ruff format .
	uv run black .
	uv run isort .
	@echo "✅ Formatting complete!"

type-check:  ## Run type checker (mypy)
	@echo "🔍 Running type checker..."
	uv run mypy agency_os/ --install-types --non-interactive || true
	@echo "⚠️  Type checking baseline (errors expected)"

complexity:  ## Check code complexity
	@echo "🔍 Checking complexity..."
	uv run ruff check . --select C90
	@echo "✅ Complexity check complete!"

security:  ## Run security checks
	@echo "🔒 Running security checks..."
	@echo "  → Ruff security rules..."
	uv run ruff check . --select S
	@echo "  → pip-audit (dependency vulnerabilities)..."
	uv run pip-audit || true
	@echo "  → detect-secrets..."
	uv run detect-secrets scan || true
	@echo "✅ Security scan complete!"

# ============================================================================
# CI/CD SIMULATION
# ============================================================================

ci: lint test validate-deps  ## Run full CI validation (what CI runs)
	@echo ""
	@echo "✅ All CI checks passed!"
	@echo ""

ci-strict: lint test-cov type-check security validate-deps  ## Strict CI (all checks)
	@echo ""
	@echo "✅ All strict CI checks passed!"
	@echo ""

# ============================================================================
# VALIDATION
# ============================================================================

validate-deps:  ## Validate dependencies and lock file
	@echo "🔍 Validating dependencies..."
	@if [ -f "uv.lock" ]; then \
		echo "  ✅ uv.lock exists"; \
	else \
		echo "  ❌ uv.lock missing (run: uv sync)"; \
		exit 1; \
	fi
	@echo "  → Checking for dependency issues..."
	uv sync --frozen || (echo "❌ Lock file out of sync (run: uv lock)" && exit 1)
	@echo "✅ Dependencies valid!"

validate-knowledge:  ## Validate knowledge bases
	@echo "🔍 Validating knowledge bases..."
	@if [ -f "validate_knowledge_index.py" ]; then \
		uv run python validate_knowledge_index.py; \
	else \
		echo "⚠️  validate_knowledge_index.py not found (skipping)"; \
	fi

# ============================================================================
# CLEANUP
# ============================================================================

clean:  ## Clean build artifacts and caches
	@echo "🧹 Cleaning..."
	rm -rf .venv/
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

clean-all: clean  ## Clean everything including uv.lock (full reset)
	rm -rf uv.lock
	@echo "✅ Full cleanup complete! (run 'make install' to rebuild)"

# ============================================================================
# DEVELOPMENT HELPERS
# ============================================================================

shell:  ## Start a shell with activated virtualenv
	@echo "🐚 Starting shell (uv environment)..."
	uv run bash

update:  ## Update dependencies to latest versions
	@echo "📦 Updating dependencies..."
	uv lock --upgrade
	@echo "✅ Dependencies updated! Review uv.lock changes."

freeze:  ## Show installed package versions
	uv pip list

audit:  ## Run full project audit
	@echo "🔍 Project Audit"
	@echo "================"
	@echo ""
	@echo "📊 Project Stats:"
	@find agency_os -name "*.py" -type f | wc -l | xargs echo "  Python files:"
	@find agency_os -name "*.py" -type f -exec wc -l {} + | tail -1 | awk '{print "  Total lines:", $$1}'
	@echo ""
	@echo "📦 Dependencies:"
	@uv pip list | wc -l | xargs echo "  Installed packages:"
	@echo ""
	@echo "🧪 Test Coverage:"
	@make test-cov > /dev/null 2>&1 || true
	@echo ""
	@echo "🔍 Code Quality:"
	@make lint || true

# ============================================================================
# PROJECT INFO
# ============================================================================

info:  ## Show project information
	@echo "📋 Vibe Agency - Project Info"
	@echo "=============================="
	@echo "Python Version: $(shell python3 --version)"
	@echo "UV Version: $(shell uv --version)"
	@echo "Working Directory: $(shell pwd)"
	@echo "Lock File: $(shell [ -f uv.lock ] && echo '✅ exists' || echo '❌ missing')"
	@echo "Virtual Env: $(shell [ -d .venv ] && echo '✅ exists' || echo '❌ missing')"
	@echo ""
	@echo "Configuration Files:"
	@echo "  pyproject.toml: $(shell [ -f pyproject.toml ] && echo '✅' || echo '❌')"
	@echo "  requirements.txt: $(shell [ -f requirements.txt ] && echo '✅' || echo '❌')"
	@echo "  Makefile: ✅"
	@echo ""
```

**Success Criteria:**
- ✅ Makefile created
- ✅ `make help` works
- ✅ `make install` works
- ✅ `make test` works
- ✅ `make lint` works

---

## Phase 4: Update Entry Points (45 min)

### Step 4.1: Update setup.sh

**File:** `/home/user/vibe-agency/setup.sh`

**Changes:**
```bash
# OLD:
# pip install -r requirements.txt
# pip install pre-commit

# NEW:
echo "📦 Installing dependencies with uv..."
uv sync --all-extras
```

**Full Updated File:**
```bash
#!/bin/bash
# ============================================================================
# LAYER 3: MANUAL DEPENDENCY SETUP (Fallback)
# ============================================================================
# Usage: ./setup.sh
#
# This is a manual fallback for environments where auto-install fails.
# Part of 4-layer dependency defense strategy.
#
# NOTE: Prefer using Makefile: make install

set -e  # Exit on any error

echo "🔧 Vibe Agency - Environment Setup"
echo "=================================="
echo ""
echo "ℹ️  Tip: Use 'make install' for a better experience!"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "⚠️  Warning: Python $PYTHON_VERSION detected (recommended: 3.11+)"
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "⚠️  uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install dependencies with uv
echo ""
echo "📦 Installing dependencies with uv..."
uv sync --all-extras

# Install and activate pre-commit hooks
echo ""
echo "🪝 Setting up pre-commit hooks..."
uv run pre-commit install
echo "✅ Pre-commit hooks activated"

# Validate knowledge bases
echo ""
echo "🔍 Validating knowledge bases..."
if [ -f "validate_knowledge_index.py" ]; then
    uv run python validate_knowledge_index.py
else
    echo "⚠️  validate_knowledge_index.py not found (skipping)"
fi

# Success
echo ""
echo "✅ Environment ready!"
echo ""
echo "Next steps:"
echo "  make test                        # Run tests (recommended)"
echo "  make lint                        # Check code quality"
echo "  ./vibe-cli run <project-id>      # Run a project"
echo ""
echo "Or use Makefile commands:"
echo "  make help                        # See all available commands"
echo ""
```

**Success Criteria:**
- ✅ setup.sh uses uv
- ✅ Backward compatible (checks for uv, installs if missing)
- ✅ Points users to Makefile

### Step 4.2: Update Devcontainer

**File:** `/home/user/vibe-agency/.devcontainer/devcontainer.json`

**Changes:**
```json
{
  "name": "vibe-agency",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/git:1": {},
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/astral-sh/uv-devcontainer-feature:latest": {}
  },
  "postCreateCommand": "uv sync --all-extras && uv run pre-commit install && python3 validate_knowledge_index.py",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker"
      ],
      "settings": {
        "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
        "python.linting.enabled": true,
        "python.linting.ruffEnabled": true,
        "python.formatting.provider": "black",
        "[python]": {
          "editor.defaultFormatter": "charliermarsh.ruff",
          "editor.formatOnSave": true,
          "editor.codeActionsOnSave": {
            "source.organizeImports": true,
            "source.fixAll": true
          }
        },
        "mypy-type-checker.args": [
          "--config-file=pyproject.toml"
        ]
      }
    }
  }
}
```

**Success Criteria:**
- ✅ Uses uv devcontainer feature
- ✅ postCreateCommand uses uv
- ✅ Adds mypy extension
- ✅ Format on save enabled

### Step 4.3: Update CI Workflows

**Primary Workflow:** `.github/workflows/validate.yml`

**Changes:**
```yaml
name: Validate Environment

on:
  push:
    branches: ["**"]
  pull_request:
    branches: [main]

jobs:
  validate:
    name: Validate Dependencies & Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11"]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Restore uv cache
        uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}
          restore-keys: |
            uv-${{ runner.os }}-

      - name: Install dependencies
        run: |
          uv sync --frozen --all-extras

      - name: Validate knowledge bases
        run: |
          if [ -f "validate_knowledge_index.py" ]; then
            uv run python validate_knowledge_index.py
          else
            echo "⚠️  validate_knowledge_index.py not found (skipping)"
          fi

      - name: Run tests
        run: |
          uv run pytest tests/ -v --tb=short

      - name: Check code quality
        run: |
          uv run ruff check . --output-format=github
          uv run ruff format --check .

      - name: Type check (baseline)
        run: |
          uv run mypy agency_os/ --install-types --non-interactive || true
        continue-on-error: true

  validate-devcontainer:
    name: Validate Devcontainer Config
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Validate devcontainer.json syntax
        run: |
          python3 -c "import json; json.load(open('.devcontainer/devcontainer.json'))"
          echo "✅ devcontainer.json is valid JSON"

      - name: Validate pyproject.toml syntax
        run: |
          python3 -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
          echo "✅ pyproject.toml is valid TOML"
```

**Success Criteria:**
- ✅ Uses uv instead of pip
- ✅ Includes uv cache (faster CI)
- ✅ Uses `uv sync --frozen` (locked dependencies)
- ✅ Adds mypy type checking (baseline)
- ✅ Validates pyproject.toml

**Secondary Workflow:** `.github/workflows/test.yml` (Optional: Merge or Keep)

**Option 1: Keep Separate (Update to UV)**
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop, 'claude/**' ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH

    - name: Restore uv cache
      uses: actions/cache@v4
      with:
        path: ~/.cache/uv
        key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}

    - name: Install dependencies
      run: |
        uv sync --frozen --all-extras

    - name: Lint with ruff
      run: |
        uv run ruff check . --select=E9,F63,F7,F82 --output-format=github

    - name: Validate YAML files
      run: |
        uv run yamllint -c .yamllint agency_os/ system_steward_framework/ || true

    - name: Run prompt composition tests
      run: |
        uv run python tests/test_prompt_composition.py

    - name: Test VIBE_ALIGNER composition
      run: |
        uv run python test_vibe_aligner.py

    - name: Validate knowledge index
      run: |
        uv run python validate_knowledge_index.py
```

**Option 2: Merge into validate.yml** (Recommended for simplicity)

**Success Criteria:**
- ✅ All workflows use uv
- ✅ Caching configured
- ✅ Faster CI runs

---

## Phase 5: Documentation Updates (30 min)

### Step 5.1: Update README.md

**File:** `/home/user/vibe-agency/README.md`

**Add Quick Start Section (Top of File):**
```markdown
## Quick Start

### Setup (One Command)
```bash
make install
```

Or manually:
```bash
./setup.sh
```

### Usage
```bash
# Run a project
./vibe-cli run <project-id>

# Run tests
make test

# Check code quality
make lint

# Full validation (what CI runs)
make ci
```

### Development
```bash
# See all available commands
make help

# Run tests with coverage
make test-cov

# Auto-format code
make format

# Type check
make type-check

# Security scan
make security
```

### Requirements
- Python 3.11+
- `uv` (installed automatically by setup.sh)

### For Devcontainer Users
Open in VS Code with Dev Containers extension. Everything auto-installs.
```

### Step 5.2: Create MIGRATION_NOTES.md

**File:** `/home/user/vibe-agency/MIGRATION_NOTES.md`

```markdown
# Migration to UV - Notes

**Date:** 2025-11-15
**Session:** claude/foundation-hardening-uv-migration-01UniXx3ZaAgpePBtgYHebZF

## What Changed

### New Files
- ✅ `pyproject.toml` - Unified project configuration
- ✅ `Makefile` - Automation commands
- ✅ `uv.lock` - Deterministic dependency lock file

### Updated Files
- ✅ `setup.sh` - Uses uv instead of pip
- ✅ `.devcontainer/devcontainer.json` - Uses uv feature
- ✅ `.github/workflows/validate.yml` - Uses uv, adds caching
- ✅ `.github/workflows/test.yml` - Uses uv
- ✅ `README.md` - Updated setup instructions

### Deprecated (But Still Work)
- `.flake8` - Config moved to pyproject.toml (can delete)
- `ruff.toml` - Config moved to pyproject.toml (can delete)

### Unchanged
- `requirements.txt` - Kept for backward compatibility (uv reads it)
- `agency_os/` - No code changes
- `tests/` - No test changes
- `vibe-cli` - Works as-is

## Migration Benefits

### Speed Improvements
| Operation | Before (pip) | After (uv) | Speedup |
|-----------|-------------|-----------|---------|
| Fresh install | ~2-3 min | ~10-20 sec | 10-15x |
| CI runtime | ~3-5 min | ~1-2 min | 2-3x |
| Lock update | N/A | ~5 sec | N/A |

### Reliability Improvements
- ✅ Deterministic builds (uv.lock)
- ✅ No version drift (locked dependencies)
- ✅ Cached installs (faster dev loop)
- ✅ Better error messages

### Developer Experience
- ✅ One-command setup (`make install`)
- ✅ Simple workflows (`make test`, `make lint`)
- ✅ Self-documenting (`make help`)
- ✅ No manual commands to remember

## For Users

### Old Way (Still Works)
```bash
pip install -r requirements.txt
pip install pre-commit
pre-commit install
pytest tests/
```

### New Way (Recommended)
```bash
make install  # Does everything
make test     # Run tests
make lint     # Check quality
```

### Migrating Existing Environment
```bash
# Clean old environment
make clean

# Reinstall with uv
make install

# Verify
make test
```

## For CI/CD

### Old Workflow
```yaml
- pip install --upgrade pip
- pip install -r requirements.txt  # Slow, no cache
- pytest tests/
```

### New Workflow
```yaml
- name: Install uv
  run: curl -LsSf https://astral.sh/uv/install.sh | sh

- name: Cache uv
  uses: actions/cache@v4
  with:
    path: ~/.cache/uv
    key: uv-${{ runner.os }}-${{ hashFiles('uv.lock') }}

- name: Install dependencies
  run: uv sync --frozen --all-extras  # Fast, cached, locked

- name: Run tests
  run: uv run pytest tests/ -v
```

## Rollback Plan

If anything breaks:

```bash
# 1. Remove new files
rm -rf .venv uv.lock

# 2. Use old setup.sh (fallback to pip)
git checkout HEAD~1 setup.sh
./setup.sh

# 3. Run tests
pytest tests/ -v
```

Or use git to revert:
```bash
git revert <migration-commit-sha>
```

## Troubleshooting

### "uv: command not found"
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"
```

### "uv.lock out of sync"
```bash
uv lock         # Regenerate lock file
uv sync         # Sync dependencies
```

### "Tests fail after migration"
```bash
make clean      # Clean old environment
make install    # Fresh install
make test       # Should pass now
```

### "Missing dependency"
```bash
# Check what's installed
uv pip list

# Add missing dependency
# Edit pyproject.toml → dependencies section
uv sync
```

## FAQ

**Q: Do I need to keep requirements.txt?**
A: Yes, for backward compatibility. uv reads it automatically.

**Q: Can I still use pip?**
A: Yes, but not recommended. uv is faster and more reliable.

**Q: What if uv isn't available?**
A: setup.sh auto-installs uv. CI workflows install it too.

**Q: Is this a breaking change?**
A: No. Backward compatible. Old workflows still work.

**Q: Do I need to learn new commands?**
A: No. Use Makefile (`make install`, `make test`). Simple.

## Next Steps

### Immediate (Done This Session)
- ✅ UV migration complete
- ✅ Makefile automation
- ✅ CI updated

### Upcoming (Priority 2)
- Add mypy strict mode (gradual)
- Add complexity checks (enforce quality)
- Audit core_orchestrator.py (1284 lines)

### Future (Priority 3)
- Property-based testing (hypothesis)
- Enhanced security scanning
- Architecture documentation updates
```

---

## Phase 6: Validation & Testing (45 min)

### Step 6.1: Local Validation
```bash
# Clean slate
make clean

# Fresh install
make install
# Expected: Completes in ~10-20 seconds

# Run tests
make test
# Expected: All tests pass (same as before migration)

# Run linting
make lint
# Expected: Pass (same or better than before)

# Full CI simulation
make ci
# Expected: All checks pass
```

**Success Criteria:**
- ✅ `make install` completes successfully
- ✅ All tests pass (same results as before)
- ✅ Linting passes
- ✅ Faster than pip-based workflow

### Step 6.2: Verify Lock File
```bash
# Check lock file exists
ls -la uv.lock
# Expected: File exists, 500-2000 lines

# Verify determinism (lock shouldn't change)
uv sync --frozen
# Expected: No changes to uv.lock

# Check locked versions
uv pip list
# Expected: All dependencies at exact versions
```

**Success Criteria:**
- ✅ uv.lock exists
- ✅ `uv sync --frozen` succeeds (no changes)
- ✅ Dependencies locked to exact versions

### Step 6.3: Compare Performance
```bash
# Benchmark: UV install
time make clean && time make install
# Expected: ~10-20 seconds

# Benchmark: Old way (for comparison, don't commit)
# time pip install -r requirements.txt
# Expected: ~2-3 minutes

# Speedup: ~10-15x
```

**Success Criteria:**
- ✅ UV install significantly faster than pip
- ✅ Cached installs even faster (~5 seconds)

### Step 6.4: Test Makefile Commands
```bash
# Test all Makefile targets
make help           # Should show all commands
make info           # Should show project info
make test           # Should run tests
make lint           # Should run linters
make format         # Should format code
make type-check     # Should run mypy (errors OK)
make security       # Should run security checks
make validate-deps  # Should validate uv.lock
make ci             # Should run full CI
make audit          # Should show project stats
```

**Success Criteria:**
- ✅ All Makefile targets work
- ✅ No errors (except type-check baseline)

### Step 6.5: Test Devcontainer (Optional)
```bash
# If devcontainer is available:
# 1. Rebuild devcontainer
# 2. Check environment
uv --version
python --version
# 3. Run tests
make test
```

**Success Criteria:**
- ✅ Devcontainer builds successfully
- ✅ UV installed automatically
- ✅ Tests pass in devcontainer

---

## Phase 7: Git Commit & Documentation (30 min)

### Step 7.1: Review Changes
```bash
git status
# Expected: New files, updated files, no secrets

git diff setup.sh
git diff .devcontainer/devcontainer.json
git diff .github/workflows/validate.yml
```

**Success Criteria:**
- ✅ All changes intentional
- ✅ No secrets in diff
- ✅ No unintended changes

### Step 7.2: Commit Migration
```bash
# Stage files
git add pyproject.toml
git add Makefile
git add uv.lock
git add setup.sh
git add .devcontainer/devcontainer.json
git add .github/workflows/validate.yml
git add .github/workflows/test.yml
git add README.md
git add FOUNDATION_ASSESSMENT.md
git add FOUNDATION_MIGRATION_PLAN.md
git add MIGRATION_NOTES.md

# Commit
git commit -m "$(cat <<'EOF'
feat: Migrate to UV - Foundation hardening

Systematic infrastructure upgrade from pip to uv for faster, more
reliable dependency management. Part of foundation hardening mission.

Changes:
- Add pyproject.toml (consolidate configs from .flake8, ruff.toml)
- Add Makefile (automation: make install, make test, make ci)
- Add uv.lock (deterministic builds)
- Update setup.sh to use uv (10-100x faster than pip)
- Update devcontainer to use uv feature
- Update CI workflows (validate.yml, test.yml) to use uv with caching
- Add comprehensive documentation (FOUNDATION_ASSESSMENT.md, MIGRATION_NOTES.md)

Benefits:
- 10-15x faster local installs (~10-20 sec vs 2-3 min)
- 2-3x faster CI (~1-2 min vs 3-5 min)
- Deterministic builds (uv.lock prevents version drift)
- Simplified workflows (make install, make test)
- Better developer experience (self-documenting Makefile)

Backward Compatible:
- requirements.txt still works (uv reads it)
- Old workflows still work (pip not removed)
- Gradual migration (no breaking changes)

Testing:
- ✅ All existing tests pass
- ✅ Linting passes (ruff)
- ✅ CI validation passes
- ✅ Devcontainer builds successfully

Related:
- CLAUDE.md: Foundation hardening mission
- Python_Projekt_Best_Practices_SUMMARY.yaml: Reference standard

Session: claude/foundation-hardening-uv-migration-01UniXx3ZaAgpePBtgYHebZF
EOF
)"
```

**Success Criteria:**
- ✅ Commit created
- ✅ Descriptive message
- ✅ All changes staged

### Step 7.3: Push to Branch
```bash
# Push to feature branch
git push -u origin claude/foundation-hardening-uv-migration-01UniXx3ZaAgpePBtgYHebZF

# Expected: Push succeeds, CI triggers
```

**Success Criteria:**
- ✅ Push succeeds
- ✅ CI starts running
- ✅ No push failures

---

## Success Metrics

### Before Migration (Baseline)
```
CI Runtime: ~3-5 minutes
Setup Time: ~2-3 minutes
Config Files: 6 files
Lock File: ❌ None
Type Safety: ❌ None
Automation: ❌ Manual commands
```

### After Migration (Target)
```
CI Runtime: ~1-2 minutes ✅ (50-60% reduction)
Setup Time: ~10-20 seconds ✅ (90% reduction)
Config Files: 3 files ✅ (50% reduction)
Lock File: ✅ uv.lock (deterministic)
Type Safety: ⚠️ mypy baseline (Priority 2)
Automation: ✅ Makefile (one-command workflows)
```

---

## Risk Mitigation

### Rollback Plan
```bash
# If anything breaks:
git revert <migration-commit-sha>

# Or manual rollback:
make clean
git checkout HEAD~1 setup.sh
git checkout HEAD~1 .devcontainer/devcontainer.json
git checkout HEAD~1 .github/workflows/validate.yml
./setup.sh  # Falls back to pip
```

### Gradual Migration
- ✅ Keep requirements.txt (backward compatible)
- ✅ Keep old workflows (can run both)
- ✅ Test thoroughly before removing old tools

### User Support
- ✅ Clear documentation (MIGRATION_NOTES.md)
- ✅ Troubleshooting guide (FAQ section)
- ✅ Makefile help (`make help`)

---

## Next Steps (Priority 2 - Future Session)

### 1. Add Mypy Strict Mode
```toml
[tool.mypy]
strict = true  # Currently false
```
- Gradual rollout per module
- Start with new code
- Fix existing code incrementally

### 2. Enhance Complexity Checks
```toml
[tool.ruff.lint.mccabe]
max-complexity = 10  # Stricter (currently 15)
```
- Audit core_orchestrator.py (1284 lines)
- Refactor if needed

### 3. Consolidate CI Workflows
- Merge validate.yml + test.yml
- Remove redundant steps
- Simplify maintenance

---

## Timeline Summary

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | UV installation & setup | 30 min | Ready |
| 2 | Configuration consolidation | 45 min | Ready |
| 3 | Makefile creation | 30 min | Ready |
| 4 | Update entry points | 45 min | Ready |
| 5 | Documentation updates | 30 min | Ready |
| 6 | Validation & testing | 45 min | Ready |
| 7 | Git commit & push | 30 min | Ready |
| **Total** | | **~4 hours** | **Ready to execute** |

---

## Execution Checklist

### Pre-flight
- [x] Assessment complete (FOUNDATION_ASSESSMENT.md)
- [x] Migration plan approved (this document)
- [ ] Ready to execute

### Execution (Follow Phase Order)
- [ ] Phase 1: Install UV ✅
- [ ] Phase 2: Create pyproject.toml ✅
- [ ] Phase 3: Create Makefile ✅
- [ ] Phase 4: Update setup.sh, devcontainer, CI ✅
- [ ] Phase 5: Update documentation ✅
- [ ] Phase 6: Validate migration ✅
- [ ] Phase 7: Commit & push ✅

### Post-migration
- [ ] CI passes
- [ ] Documentation updated
- [ ] Team notified (if applicable)

---

**Plan Complete - Ready to Execute**

Next: Begin Phase 1 (UV Installation & Setup)
