#!/bin/bash
# Template Workspace Setup - Final Configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

header() {
    echo -e "${PURPLE}$1${NC}"
}

# Main setup function
main() {
    header "🚀 Python Project Template - Final Setup"
    echo ""

    # Fix Git permissions
    log "Configuring Git permissions..."
    git config --global --add safe.directory "$(pwd)" || warning "Could not set Git safe directory"

    # Make scripts executable
    log "Making scripts executable..."
    chmod +x scripts/*.sh || warning "Could not make scripts executable"
    chmod +x scripts/*.py || warning "Could not make Python scripts executable"

    # Initialize Git and add files
    log "Setting up Git repository..."
    git add . || warning "Could not add files to Git"
    
    if ! git diff --cached --quiet; then
        git commit -m "Initial template workspace setup

- Complete Python project template with modern tooling
- UV package management with Python 3.12.10
- Comprehensive CI/CD with GitHub Actions
- Security-first approach with Doppler integration
- Pre-commit hooks and code quality tools
- Interactive setup scripts for customization
- Documentation with MkDocs Material
- Comprehensive Makefile for automation

Ready for project customization and development." || warning "Could not commit initial setup"
    else
        log "No changes to commit"
    fi

    # Template completion summary
    echo ""
    header "✅ TEMPLATE WORKSPACE COMPLETE!"
    echo ""
    
    success "📁 Project structure created"
    success "📦 Dependencies configured (minimal set)"
    success "🔧 Development tools set up (ruff, black, mypy, pytest)"
    success "🔒 Security tools integrated (bandit, safety, detect-secrets)"
    success "🚀 GitHub Actions workflows ready"
    success "🛠️ Interactive setup scripts created"
    success "📚 Documentation framework ready"
    success "🎯 Doppler secrets management configured"

    echo ""
    header "📋 TEMPLATE FEATURES:"
    echo ""
    echo "Core Infrastructure:"
    echo "  • Python 3.12.10 with UV package manager"
    echo "  • Comprehensive pyproject.toml with dependency groups"
    echo "  • Makefile with 25+ automation commands"
    echo "  • Pre-commit hooks for quality assurance"
    echo ""
    echo "Development Tools:"
    echo "  • Ruff for linting and formatting"
    echo "  • Black for code formatting"
    echo "  • MyPy for type checking"
    echo "  • Pytest with coverage reporting"
    echo ""
    echo "Security & Secrets:"
    echo "  • Doppler integration (no .env files)"
    echo "  • Bandit security scanning"
    echo "  • Safety vulnerability checking"
    echo "  • Detect-secrets for credential protection"
    echo ""
    echo "CI/CD & Automation:"
    echo "  • GitHub Actions workflows (ci.yml)"
    echo "  • Health monitoring (health-monitor.yml)"
    echo "  • Lint repair validation (lint-repair-validation.yml)"
    echo "  • Automated quality checks and deployment"
    echo ""
    echo "Customization:"
    echo "  • Interactive setup script (setup_project.sh)"
    echo "  • Python customization script (customize_template.py)"
    echo "  • Template placeholders for easy replacement"
    echo ""

    echo ""
    header "🎯 HOW TO USE THIS TEMPLATE:"
    echo ""
    echo "1. Copy template to new project:"
    echo "   cp -r template_workspace/ my_new_project/"
    echo "   cd my_new_project/"
    echo ""
    echo "2. Run interactive setup:"
    echo "   ./scripts/setup_project.sh"
    echo ""
    echo "3. Or customize manually:"
    echo "   python scripts/customize_template.py"
    echo ""
    echo "4. Set up Doppler secrets:"
    echo "   doppler setup --project your-project --config development"
    echo ""
    echo "5. Start developing:"
    echo "   make install"
    echo "   make test"
    echo "   make run"
    echo ""

    echo ""
    header "📁 TEMPLATE STRUCTURE:"
    echo ""
    echo "template_workspace/"
    echo "├── src/project_name/              # Source code (placeholder)"
    echo "├── tests/                         # Test suite"
    echo "├── scripts/                       # Setup and utility scripts"
    echo "├── docs/                          # Documentation"
    echo "├── .github/workflows/             # CI/CD workflows"
    echo "├── config/                        # Configuration files"
    echo "├── pyproject.toml                 # Dependencies & tools"
    echo "├── Makefile                       # Automation commands"
    echo "├── .pre-commit-config.yaml        # Quality hooks"
    echo "├── .env.doppler.template          # Secrets template"
    echo "├── .gitignore                     # Git ignore rules"
    echo "└── README.md                      # Documentation"
    echo ""

    echo ""
    header "🔧 CUSTOMIZATION PLACEHOLDERS:"
    echo ""
    echo "The following placeholders will be replaced during setup:"
    echo "  • project_name → your_project_name"
    echo "  • PROJECT_NAME → Your Project Display Name"
    echo "  • Your Name → your actual name"
    echo "  • your.email@example.com → your email"
    echo "  • your-username → your GitHub username"
    echo ""

    echo ""
    header "⚡ AVAILABLE MAKE COMMANDS:"
    echo ""
    echo "Environment:"
    echo "  make install        # Install all dependencies"
    echo "  make install-dev    # Install dev dependencies only"
    echo ""
    echo "Code Quality:"
    echo "  make lint          # Run linting checks"
    echo "  make format        # Format code"
    echo "  make lint-fix      # Auto-fix lint issues"
    echo ""
    echo "Testing:"
    echo "  make test          # Run test suite"
    echo "  make test-unit     # Run unit tests"
    echo "  make security      # Run security scans"
    echo ""
    echo "Development:"
    echo "  make run           # Start development server"
    echo "  make docs-serve    # Serve documentation"
    echo "  make clean         # Clean build artifacts"
    echo "  make ci-check      # Run all CI checks locally"
    echo ""

    echo ""
    success "🎉 Template workspace is ready for use!"
    echo ""
    warning "📝 Remember: This is a TEMPLATE, not a working project"
    warning "📝 Use the setup scripts to customize for your specific project"
    echo ""
    log "Next steps: Copy this template and run ./scripts/setup_project.sh"
    echo ""
}

# Run main function
main "$@"
