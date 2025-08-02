# Agent Reliability Enforcement System - Python Project Template
# Makefile for development workflow automation

.PHONY: help install clean lint format test security run dev docs deploy backup

# Default target
help: ## Show this help message
	@echo "Agent Reliability Enforcement System - Python Project Template"
	@echo "======================================"
	@echo ""
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
install: ## Install all dependencies with UV
	@echo "📦 Installing project dependencies..."
	uv sync --all-groups
	@echo "🪝 Installing pre-commit hooks..."
	uv run pre-commit install
	@echo "✅ Installation complete"

install-dev: ## Install development dependencies only
	@echo "📦 Installing development dependencies..."
	uv sync --group dev --group test --group lint --group format
	uv run pre-commit install

# Code quality
lint: ## Run all linting checks
	@echo "🔍 Running lint checks..."
	uv run ruff check src/ tests/
	uv run mypy src/

format: ## Format code with black and ruff
	@echo "🎨 Formatting code..."
	uv run ruff format src/ tests/
	uv run black src/ tests/

format-check: ## Check if code is properly formatted
	@echo "✅ Checking code formatting..."
	uv run ruff format --check src/ tests/
	uv run black --check src/ tests/

# Testing
test: ## Run all tests
	@echo "🧪 Running tests..."
	uv run pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	uv run pytest tests/unit/ -v

test-integration: ## Run integration tests
	@echo "🧪 Running integration tests..."
	uv run pytest tests/integration/ -v

# Security
security: ## Run security scans
	@echo "🔒 Running security scans..."
	mkdir -p reports
	uv run bandit -r src/ -f json -o reports/bandit-report.json
	uv run safety check
	uv run detect-secrets scan --baseline .secrets.baseline

secrets-update: ## Update secrets baseline
	@echo "🔐 Updating secrets baseline..."
	uv run detect-secrets scan --update .secrets.baseline

# Development server
run: ## Start the development server
	@echo "🚀 Starting development server..."
	uv run python -m src.ares.main

run-api: ## Start API server
	@echo "⚡ Starting API server..."
	uv run uvicorn src.ares.api.main:app --reload --host 0.0.0.0 --port 8000

# Clean up
clean: ## Clean build artifacts and cache
	@echo "🧹 Cleaning build artifacts..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/
	rm -rf dist/ build/

# Documentation
docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	uv run mkdocs build

docs-serve: ## Serve documentation locally
	@echo "📖 Serving documentation at http://localhost:8001"
	uv run mkdocs serve --dev-addr 0.0.0.0:8001

docs-deploy: ## Deploy documentation
	@echo "🚀 Deploying documentation..."
	uv run mkdocs gh-deploy

# Docker
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t ares:latest .

docker-run: ## Run Docker container
	@echo "🐳 Running Docker container..."
	docker-compose up

# Backup and recovery
backup: ## Backup project data
	@echo "💾 Creating project backup..."
	./scripts/backup.sh

restore: ## Restore from backup
	@echo "🔄 Restoring from backup..."
	@read -p "Enter backup file path: " backup_file; \
	./scripts/restore.sh "$$backup_file"

# Development utilities
dev-reset: ## Reset development environment
	@echo "🔄 Resetting development environment..."
	$(MAKE) clean
	$(MAKE) install

lint-fix: ## Automatically fix linting issues
	@echo "🔧 Auto-fixing lint issues..."
	uv run ruff check --fix src/ tests/
	uv run ruff format src/ tests/
	uv run black src/ tests/

ci-check: ## Run all CI checks locally
	@echo "🔍 Running full CI check suite..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test
	@echo "✅ All CI checks passed!"

# Version management
version: ## Show current version
	@echo "📦 Current version:"
	@uv run python -c "from src.ares import __version__; print(__version__)"

# Setup and customization
setup: ## Run interactive project setup
	@echo "🛠️ Starting interactive project setup..."
	./scripts/setup_project.sh

customize: ## Customize project template
	@echo "🎨 Customizing project template..."
	./scripts/customize_template.py
