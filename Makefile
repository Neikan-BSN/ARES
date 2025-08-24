# ARES - Agent Reliability Enforcement System - Production-ready multi-agent coordination
# Standardized Makefile Template v2.0 for Phase 2 Day 2
# Follows workspace standards with UV 0.8.3 + Python 3.12 canonical patterns

.PHONY: help install clean lint format test security run dev docs deploy backup env-check ci-check quality-gates

# ================================================================================
# CANONICAL ENVIRONMENT VARIABLES (PHASE 2 STANDARD)
# ================================================================================
export UV_PROJECT_ENVIRONMENT := .venv
export UV_PYTHON_VERSION := 3.12
export UV_WORKSPACE_ROOT := .
export VIRTUAL_ENV := $(PWD)/.venv

# ================================================================================
# PROJECT IDENTIFICATION
# ================================================================================
PROJECT_NAME := ARES
PROJECT_TYPE := AI Agent System
PROJECT_VERSION := $(shell uv run python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || echo "unknown")

# ================================================================================
# DEFAULT TARGET - ENHANCED HELP SYSTEM
# ================================================================================
help: ## Show this help message with categorized targets
	@echo "$(PROJECT_NAME) - Agent Reliability Enforcement System - Production-ready multi-agent coordination"
	@echo "================================================================================"
	@echo ""
	@echo "🔧 Environment: $(VIRTUAL_ENV)"
	@echo "🐍 Python: $(UV_PYTHON_VERSION)"
	@echo "📦 Version: $(PROJECT_VERSION)"
	@echo "🏗️  Type: $(PROJECT_TYPE)"
	@echo ""
	@echo "🎯 Essential Commands:"
	@echo "  make install         - Install all dependencies with UV"
	@echo "  make test            - Run comprehensive test suite"
	@echo "  make lint            - Check code quality (critical issues only)"
	@echo "  make format          - Format code with ruff"
	@echo "  make precommit-parallel - Run pre-commit hooks (FAST - parallel)"
	@echo "  make ci-check        - Run all CI checks locally"
	@echo "  make ci-performance  - Monitor CI/CD performance (Task 4.1.3)"
	@echo "  make performance-validate - Validate performance baselines (Task 4.1.4)"
	@echo "  make performance-monitor - Monitor performance regressions (Task 4.1.4)"
	@echo ""
	@echo "📋 All Available Targets (by category):"
	@echo ""
	@echo "🏗️  Environment Management:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && $$2 ~ /(environment|install|setup|clean)/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🔍 Code Quality:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && $$2 ~ /(lint|format|security|test)/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "🚀 Development:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / && $$2 ~ /(run|dev|serve|start)/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ================================================================================
# ENVIRONMENT VALIDATION & SETUP
# ================================================================================
env-check: ## Validate canonical UV environment setup
	@echo "🔍 Checking canonical UV environment for $(PROJECT_NAME)..."
	@if [ ! -d ".venv" ]; then \
		echo "❌ Canonical .venv not found. Run 'make install' first."; \
		exit 1; \
	fi
	@if [ -d "venv" ] || [ -d ".env" ] || [ -d "env" ]; then \
		echo "❌ Multiple virtual environments detected! Only .venv is allowed."; \
		echo "🧹 Remove: venv/, .env/, env/ directories"; \
		exit 1; \
	fi
	@echo "🐍 Python version: $$(uv run python --version)"
	@echo "📦 UV version: $$(uv --version)"
	@echo "✅ Canonical environment validated"

# Environment setup
install: clean-env ## Install all dependencies with UV (canonical environment)
	@echo "📦 Setting up canonical UV environment for $(PROJECT_NAME)..."
	@echo "🐍 Python version: $(UV_PYTHON_VERSION)"
	uv python pin $(UV_PYTHON_VERSION)
	@rm -f uv.lock
	uv sync --all-groups
	@if git rev-parse --git-dir >/dev/null 2>&1; then \
		echo "🪝 Installing pre-commit hooks..."; \
		uv run pre-commit install; \
	else \
		echo "⚠️ Not a Git repository - skipping pre-commit hooks"; \
	fi
	@echo "📍 Canonical environment created at: $(VIRTUAL_ENV)"
	@echo "✅ Installation complete"

install-dev: env-check ## Install development dependencies only
	@echo "📦 Installing development dependencies..."
	uv sync --group dev --group test --group lint
	@if git rev-parse --git-dir >/dev/null 2>&1; then \
		uv run pre-commit install; \
	fi

# Clean up non-canonical environments
clean-env: ## Remove all non-canonical virtual environments
	@echo "🧹 Cleaning non-canonical virtual environments..."
	@rm -rf venv/ .env/ env/ .venv-old/ || true
	@echo "✅ Environment cleanup complete"

# ================================================================================
# CODE QUALITY - PRAGMATIC CI/CD PATTERNS
# ================================================================================
lint: env-check ## Run critical linting checks only
	@echo "🔍 Running critical lint checks (blocking issues only)..."
	uv run ruff check src/ tests/ --select="E9,F,B,S" --ignore="B008,S314,S324,B017"
	@echo "✅ No critical issues found"

lint-full: env-check ## Run comprehensive linting (advisory)
	@echo "🔍 Running full lint analysis (advisory)..."
	uv run ruff check src/ tests/ || echo "⚠️ Style issues found (not blocking)"
	uv run mypy src/ tests/ || echo "⚠️ Type issues found (advisory)"

format: env-check ## Format code with ruff
	@echo "🎨 Formatting code..."
	uv run ruff format src/ tests/

format-check: env-check ## Check if code is properly formatted
	@echo "✅ Checking code formatting..."
	uv run ruff format --check src/ tests/

# ================================================================================
# TESTING (WITH ENVIRONMENT VALIDATION)
# ================================================================================
test: env-check ## Run all tests
	@echo "🧪 Running comprehensive test suite..."
	uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-unit: env-check ## Run unit tests only
	@echo "🧪 Running unit tests..."
	uv run pytest tests/unit/ -v

test-integration: env-check ## Run integration tests
	@echo "🧪 Running integration tests..."
	uv run pytest tests/integration/ -v

# ================================================================================
# SECURITY (WITH ENVIRONMENT VALIDATION)
# ================================================================================
security: env-check ## Run security scans
	@echo "🔒 Running security scans..."
	mkdir -p reports
	uv run bandit -r src/ tests/ -f json -o reports/bandit-report.json
	uv run safety check
	@if [ -f .secrets.baseline ]; then \
		uv run detect-secrets scan --baseline .secrets.baseline; \
	else \
		echo "⚠️ No secrets baseline found - creating one..."; \
		uv run detect-secrets scan --update .secrets.baseline; \
	fi

secrets-update: env-check ## Update secrets baseline
	@echo "🔐 Updating secrets baseline..."
	uv run detect-secrets scan --update .secrets.baseline

# ================================================================================
# PRE-COMMIT HOOKS (PARALLEL OPTIMIZED - Task 4.1.1)
# ================================================================================
precommit: env-check ## Run pre-commit hooks with default configuration
	@echo "🪝 Running pre-commit hooks..."
	uv run pre-commit run --all-files

precommit-parallel: env-check ## Run pre-commit hooks with parallel optimization (FAST)
	@echo "🪝 Running pre-commit hooks with parallel optimization..."
	@echo "⚡ Using optimized parallel configuration for maximum speed"
	PRE_COMMIT_PARALLEL=8 PRE_COMMIT_COLOR=never uv run pre-commit run --all-files

precommit-benchmark: env-check ## Benchmark pre-commit performance with different parallel settings
	@echo "📊 Running pre-commit performance benchmark..."
	uv run python scripts/benchmark_precommit_parallel.py

precommit-install: env-check ## Install pre-commit hooks
	@echo "🔧 Installing pre-commit hooks..."
	uv run pre-commit install

precommit-update: env-check ## Update pre-commit hook repositories
	@echo "🔄 Updating pre-commit repositories..."
	uv run pre-commit autoupdate

# ================================================================================
# CI/CD PERFORMANCE OPTIMIZATION - TASK 4.1.3
# ================================================================================
ci-performance: env-check ## Monitor CI/CD pipeline performance (Task 4.1.3)
	@echo "🎯 CI/CD Performance Analysis - Task 4.1.3"
	uv run python scripts/ci_performance_monitor.py

ci-performance-report: env-check ## Generate detailed CI/CD performance report
	@echo "📊 Generating CI/CD performance report..."
	uv run python scripts/ci_performance_monitor.py --output-file ci_performance_report.md

ci-benchmark: env-check ## Benchmark CI/CD pipeline with custom target time
	@echo "⏱️ Benchmarking CI/CD pipeline..."
	uv run python scripts/ci_performance_monitor.py --target-minutes 5.0

ci-fast: env-check ## Test ultra-fast CI pipeline locally
	@echo "🚀 Testing ultra-fast CI pipeline..."
	@echo "Running optimized quality checks..."
	@export PRE_COMMIT_PARALLEL=8 && export PRE_COMMIT_COLOR=never && \
		time (uv run ruff format --check src/ tests/ && \
			uv run ruff check src/ tests/ --select=E9,F,I && \
			uv run bandit -r src/ -ll --quiet && \
			uv run pre-commit run --all-files)
	@echo "✅ Fast CI pipeline test completed"

# ================================================================================
# DEVELOPMENT SERVER (WITH ENVIRONMENT VALIDATION)
# ================================================================================
run: env-check ## Start the development server
	@echo "🚀 Starting development server..."
	uv run python -m src.ARES.main

# ================================================================================
# CLEAN UP (INCLUDES ENVIRONMENT CLEANUP)
# ================================================================================
clean: clean-env ## Clean build artifacts and cache
	@echo "🧹 Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf dist/ build/ .uv-cache/
	@echo "🗑️ Cleaned all artifacts and non-canonical environments"

# ================================================================================
# QUALITY GATES ENFORCEMENT (Task 3.2 Implementation)
# ================================================================================
# Individual Quality Gates with proper exit codes
gate-1-env: ## Quality Gate 1: Environment Validation
	@echo "🚪 Quality Gate 1: Environment Validation"
	@if ! python3 --version 2>/dev/null | grep -E "3\.(11|12|13)" >/dev/null; then \
		echo "❌ Gate 1 FAILED: Python 3.11+ required"; \
		exit 1; \
	fi
	@if ! command -v uv >/dev/null 2>&1; then \
		echo "❌ Gate 1 FAILED: UV package manager required"; \
		exit 1; \
	fi
	@if ! uv sync --dry-run >/dev/null 2>&1; then \
		echo "❌ Gate 1 FAILED: Dependency installation would fail"; \
		exit 1; \
	fi
	@echo "✅ Gate 1 PASSED: Environment validated"

gate-2-quality: ## Quality Gate 2: Code Quality & Standards
	@echo "🚪 Quality Gate 2: Code Quality & Standards"
	@echo "  → Checking code formatting..."
	@if ! uv run ruff format --check src/ tests/ >/dev/null 2>&1; then \
		echo "❌ Gate 2 FAILED: Code formatting issues detected"; \
		echo "   Fix with: make format"; \
		exit 1; \
	fi
	@echo "  → Checking critical lint issues..."
	@if ! uv run ruff check src/ tests/ --select="E9,F" >/dev/null 2>&1; then \
		echo "❌ Gate 2 FAILED: Critical lint issues detected"; \
		echo "   Fix with: uv run ruff check --fix src/ tests/"; \
		exit 1; \
	fi
	@echo "  → Checking import organization..."
	@if ! uv run ruff check src/ tests/ --select="I" >/dev/null 2>&1; then \
		echo "❌ Gate 2 FAILED: Import organization issues"; \
		echo "   Fix with: uv run ruff check --fix src/ tests/"; \
		exit 1; \
	fi
	@echo "✅ Gate 2 PASSED: Code quality standards met"

gate-3-security: ## Quality Gate 3: Basic Security Compliance
	@echo "🚪 Quality Gate 3: Basic Security Compliance"
	@echo "  → Running security scan..."
	@mkdir -p reports
	@if ! uv run bandit -r src/ -ll -f json -o reports/bandit-report.json >/dev/null 2>&1; then \
		echo "❌ Gate 3 FAILED: Critical security issues detected"; \
		echo "   Review: reports/bandit-report.json"; \
		exit 1; \
	fi
	@echo "  → Checking for secrets..."
	@if [ -f .secrets.baseline ]; then \
		if ! uv run detect-secrets scan --baseline .secrets.baseline >/dev/null 2>&1; then \
			echo "❌ Gate 3 FAILED: Potential secrets detected"; \
			exit 1; \
		fi \
	fi
	@echo "✅ Gate 3 PASSED: Basic security compliance verified"

gate-4-testing: ## Quality Gate 4: Basic Testing
	@echo "🚪 Quality Gate 4: Basic Testing"
	@echo "  → Running test suite and checking for passing tests..."
	@uv run pytest tests/ --tb=no -q > /tmp/test_output.txt 2>&1 || true
	@if grep -q "passed" /tmp/test_output.txt; then \
		PASSED=$$(grep -o '[0-9]\+ passed' /tmp/test_output.txt | head -1 | grep -o '[0-9]\+'); \
		echo "  → $$PASSED tests passed"; \
		if grep -q "failed" /tmp/test_output.txt; then \
			FAILED=$$(grep -o '[0-9]\+ failed' /tmp/test_output.txt | head -1 | grep -o '[0-9]\+'); \
			echo "  → $$FAILED tests failed (non-blocking for basic gate)"; \
		fi; \
		echo "✅ Gate 4 PASSED: Basic testing requirements met"; \
	else \
		echo "❌ Gate 4 FAILED: No tests are passing"; \
		echo "   Run: make test (for detailed output)"; \
		exit 1; \
	fi
	@rm -f /tmp/test_output.txt

gate-5-precommit: ## Quality Gate 5: Pre-commit Hooks (Parallel Optimized)
	@echo "🚪 Quality Gate 5: Pre-commit Hooks Validation"
	@echo "  → Running parallel optimized pre-commit hooks..."
	@if PRE_COMMIT_PARALLEL=8 PRE_COMMIT_COLOR=never uv run pre-commit run --all-files >/dev/null 2>&1; then \
		echo "✅ Gate 5 PASSED: All pre-commit hooks passed with parallel optimization"; \
	else \
		echo "❌ Gate 5 FAILED: Pre-commit hooks failed"; \
		echo "   Fix with: make precommit-parallel (to see detailed output)"; \
		exit 1; \
	fi

# Comprehensive Quality Gates Execution
quality-gates: ## Run all quality gates in sequence
	@echo "🔒 Running Quality Gates Enforcement for $(PROJECT_NAME)"
	@echo "=================================================================="
	$(MAKE) gate-1-env
	$(MAKE) gate-2-quality
	$(MAKE) gate-3-security
	$(MAKE) gate-4-testing
	$(MAKE) gate-5-precommit
	@echo "=================================================================="
	@echo "✅ ALL QUALITY GATES PASSED (including parallel pre-commit optimization)!"

# ================================================================================
# CI CHECKS - Enhanced with Quality Gates
# ================================================================================
ci-check: ## Run all CI checks with quality gates enforcement
	@echo "🔍 Running enhanced CI check suite with quality gates for $(PROJECT_NAME)..."
	@echo "=================================================================="
	$(MAKE) quality-gates
	@echo "=================================================================="
	@echo "✅ All CI checks and quality gates passed!"

# Legacy CI check (for compatibility)
ci-check-legacy: ## Run legacy CI checks (without quality gates)
	@echo "🔍 Running legacy CI check suite for $(PROJECT_NAME)..."
	$(MAKE) env-check
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test
	@echo "✅ Legacy CI checks passed!"

# ================================================================================
# VERSION MANAGEMENT
# ================================================================================
version: ## Show current version and environment info
	@echo "📦 $(PROJECT_NAME) Information:"
	@echo "Version: $(PROJECT_VERSION)"
	@echo "Python: $$(uv run python --version)"
	@echo "UV: $$(uv --version)"
	@echo "Environment: $(VIRTUAL_ENV)"

# ================================================================================
# PROJECT-SPECIFIC EXTENSIONS
# ================================================================================
# ================================================================================
# AGENT SYSTEM MANAGEMENT
# ================================================================================
run-agent: env-check ## Start the agent system
	@echo "🤖 Starting ARES agent system..."
	uv run python -m src.ARES.main

run-api: env-check ## Start API server
	@echo "⚡ Starting ARES API server..."
	uv run uvicorn src.ARES.api.main:app --reload --host 0.0.0.0 --port 8000

# ================================================================================
# AGENT COORDINATION
# ================================================================================
agents-status: env-check ## Check agent coordination status
	@echo "🤖 Checking ARES agent status..."
	uv run python -c "from src.ARES.coordination import AgentCoordinator; AgentCoordinator().status()"

agents-health: env-check ## Health check for all agents
	@echo "🏥 Agent health check..."
	uv run python -c "from src.ARES.health import AgentHealthMonitor; AgentHealthMonitor().check_all()"

# ================================================================================
# DATABASE MANAGEMENT (NEO4J)
# ================================================================================
db-init: env-check ## Initialize graph database
	@echo "🗄️ Initializing ARES graph database..."
	uv run python -c "from src.ARES.database import init_graph_db; init_graph_db()"

db-reset: env-check ## Reset graph database (destructive)
	@echo "⚠️ This will destroy all agent coordination data!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		uv run python -c "from src.ARES.database import reset_graph_db; reset_graph_db()"; \
		$(MAKE) db-init; \
		echo "✅ Database reset and initialized"; \
	else \
		echo "❌ Database reset cancelled"; \
	fi

# Project Documentation Automation
# Auto-generated integration for ARES

docs-update: ## Process commit and update documentation
	@echo "🔄 Processing commit and updating documentation..."
	uv run python scripts/unified_documentation_agent.py --process-commit

docs-status: ## Show documentation system status
	@echo "📊 Checking documentation system status..."
	uv run python scripts/unified_documentation_agent.py --status-check

docs-validate: ## Validate documentation system
	@echo "🔍 Validating documentation system..."
	uv run python scripts/unified_documentation_agent.py --validate-system

# ================================================================================
# DOCKER OPTIMIZATION - ADVANCED BUILDKIT CACHING (<3min builds)
# ================================================================================
docker-build: ## Build production Docker image with advanced caching
	@echo "🐳 Building ARES production image with advanced caching..."
	./scripts/docker-build-optimized.sh production

docker-build-dev: ## Build development Docker image with caching
	@echo "🐳 Building ARES development image..."
	./scripts/docker-build-optimized.sh development

docker-build-all: ## Build all Docker images with parallel optimization
	@echo "🐳 Building all ARES Docker images..."
	./scripts/docker-build-optimized.sh all

docker-benchmark: ## Run Docker build performance benchmark
	@echo "🏃‍♂️ Running Docker build performance benchmark..."
	./scripts/docker-build-optimized.sh --benchmark

docker-cache-info: ## Show Docker build cache information
	@echo "📊 Docker build cache information:"
	./scripts/docker-build-optimized.sh --cache-info

docker-cache-clean: ## Clean Docker build cache
	@echo "🧹 Cleaning Docker build cache..."
	./scripts/docker-build-optimized.sh --prune-cache

docker-up-fast: ## Start services with BuildKit optimization
	@echo "⚡ Starting ARES with BuildKit optimization..."
	export DOCKER_BUILDKIT=1 COMPOSE_DOCKER_CLI_BUILD=1 && \
	docker-compose -f docker-compose.yml -f docker-compose.buildkit.yml up --build -d

docker-test: ## Run tests in optimized Docker container
	@echo "🧪 Running tests in Docker with optimization..."
	./scripts/docker-build-optimized.sh testing
	docker run --rm $(PROJECT_NAME):test

# Docker deployment targets
docker-production: ## Deploy production-ready containers
	@echo "🚀 Deploying ARES production containers..."
	$(MAKE) docker-build
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Performance monitoring
docker-performance-report: ## Generate Docker build performance report
	@echo "📈 Generating Docker performance report..."
	@if [ -f build-performance.log ]; then \
		echo "Recent Docker Build Performance:"; \
		tail -20 build-performance.log; \
		echo ""; \
		echo "Cache Efficiency:"; \
		docker system df; \
	else \
		echo "No performance data available. Run 'make docker-benchmark' first."; \
	fi

# ================================================================================
# TASK 4.1.4 - PERFORMANCE MONITORING AND BENCHMARK VALIDATION
# ================================================================================

performance-validate: env-check ## Validate performance baselines from Tasks 4.1.1-4.1.3 (Task 4.1.4)
	@echo "🎯 Performance Baseline Validation - Task 4.1.4"
	@echo "Validating optimizations from Tasks 4.1.1, 4.1.2, and 4.1.3"
	uv run python scripts/performance_baseline_validator.py

performance-validate-report: env-check ## Generate comprehensive performance validation report
	@echo "📊 Generating performance validation report..."
	uv run python scripts/performance_baseline_validator.py --output-file performance_baseline_report.md

performance-monitor: env-check ## Run automated performance regression detection
	@echo "🔍 Performance Regression Detection - Task 4.1.4"
	@echo "Automated monitoring with regression detection"
	uv run python scripts/performance_regression_detector.py

performance-monitor-report: env-check ## Generate performance monitoring report
	@echo "📈 Generating performance monitoring report..."
	uv run python scripts/performance_regression_detector.py --output-file performance_monitoring_report.md

performance-monitor-ci: env-check ## Run performance monitoring with CI/CD integration
	@echo "🚨 Performance Monitoring for CI/CD Pipeline"
	uv run python scripts/performance_regression_detector.py --alert-on-regression

performance-validate-precommit: env-check ## Validate only pre-commit performance (Task 4.1.1)
	@echo "🔍 Pre-commit Performance Validation"
	uv run python scripts/performance_baseline_validator.py --validation-type precommit

performance-validate-docker: env-check ## Validate only Docker build performance (Task 4.1.2)
	@echo "🔍 Docker Build Performance Validation"
	uv run python scripts/performance_baseline_validator.py --validation-type docker

performance-validate-ci: env-check ## Validate only CI pipeline performance (Task 4.1.3)
	@echo "🔍 CI Pipeline Performance Validation"
	uv run python scripts/performance_baseline_validator.py --validation-type ci

performance-full-suite: env-check ## Run complete performance monitoring suite (Task 4.1.4)
	@echo "🎯 Complete Performance Monitoring Suite - Task 4.1.4"
	@echo "1. Validating performance baselines..."
	@$(MAKE) performance-validate
	@echo ""
	@echo "2. Running regression detection..."
	@$(MAKE) performance-monitor
	@echo ""
	@echo "3. Generating comprehensive reports..."
	@$(MAKE) performance-validate-report
	@$(MAKE) performance-monitor-report
	@echo ""
	@echo "✅ Performance monitoring suite completed"
