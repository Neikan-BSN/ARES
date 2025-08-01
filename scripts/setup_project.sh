#!/bin/bash
# Python Project Template Setup Script
# Interactive setup and customization for new Python projects

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.12.10"
TEMPLATE_NAME="project_name"

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
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

# Welcome and project information gathering
welcome() {
    clear
    header "🚀 =================================================="
    header "🚀  PYTHON PROJECT TEMPLATE SETUP"
    header "🚀  Interactive Project Customization"
    header "🚀 =================================================="
    echo ""
    log "Setting up a new Python project with modern best practices..."
    echo ""
}

# Gather project information
gather_project_info() {
    log "Please provide project information:"
    echo ""

    # Project name
    read -p "📦 Project name (snake_case): " PROJECT_NAME
    if [ -z "$PROJECT_NAME" ]; then
        error "Project name cannot be empty"
        exit 1
    fi

    # Project display name
    read -p "📋 Project display name: " PROJECT_DISPLAY_NAME
    if [ -z "$PROJECT_DISPLAY_NAME" ]; then
        PROJECT_DISPLAY_NAME="$PROJECT_NAME"
    fi

    # Description
    read -p "📝 Project description: " PROJECT_DESCRIPTION
    if [ -z "$PROJECT_DESCRIPTION" ]; then
        PROJECT_DESCRIPTION="A modern Python project"
    fi

    # Author information
    read -p "👤 Author name: " AUTHOR_NAME
    if [ -z "$AUTHOR_NAME" ]; then
        AUTHOR_NAME="Your Name"
    fi

    read -p "📧 Author email: " AUTHOR_EMAIL
    if [ -z "$AUTHOR_EMAIL" ]; then
        AUTHOR_EMAIL="your.email@example.com"
    fi

    # GitHub info
    read -p "🐙 GitHub username/organization: " GITHUB_USER
    if [ -z "$GITHUB_USER" ]; then
        GITHUB_USER="your-username"
    fi

    # Package type
    echo ""
    log "Select project type:"
    echo "1) Library/Package"
    echo "2) Web API (FastAPI)"
    echo "3) CLI Application"
    echo "4) Data Science Project"
    echo "5) General Application"
    read -p "Choose project type (1-5): " PROJECT_TYPE

    case $PROJECT_TYPE in
        1) TYPE_NAME="library" ;;
        2) TYPE_NAME="api" ;;
        3) TYPE_NAME="cli" ;;
        4) TYPE_NAME="datascience" ;;
        5) TYPE_NAME="general" ;;
        *) TYPE_NAME="general" ;;
    esac

    echo ""
    success "Project information collected!"
}

# Display confirmation
confirm_settings() {
    echo ""
    header "📋 PROJECT CONFIGURATION SUMMARY"
    echo ""
    echo "Project Name:     $PROJECT_NAME"
    echo "Display Name:     $PROJECT_DISPLAY_NAME"
    echo "Description:      $PROJECT_DESCRIPTION"
    echo "Author:           $AUTHOR_NAME <$AUTHOR_EMAIL>"
    echo "GitHub User:      $GITHUB_USER"
    echo "Project Type:     $TYPE_NAME"
    echo "Python Version:   $PYTHON_VERSION"
    echo ""
    
    read -p "✅ Proceed with this configuration? (y/N): " CONFIRM
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        log "Setup cancelled by user"
        exit 0
    fi
}

# Customize template files
customize_template() {
    log "Customizing template files..."

    # Update pyproject.toml
    sed -i "s/project_name/$PROJECT_NAME/g" pyproject.toml
    sed -i "s/A modern Python project template with best practices/$PROJECT_DESCRIPTION/g" pyproject.toml

    # Update Makefile
    sed -i "s/PROJECT_NAME/$PROJECT_DISPLAY_NAME/g" Makefile
    sed -i "s/project_name/$PROJECT_NAME/g" Makefile

    # Update Doppler template
    sed -i "s/project_name/$PROJECT_NAME/g" .env.doppler.template
    sed -i "s/PROJECT_NAME/$PROJECT_DISPLAY_NAME/g" .env.doppler.template

    # Rename source directory
    if [ -d "src/project_name" ]; then
        mv "src/project_name" "src/$PROJECT_NAME"
    fi

    success "Template files customized"
}

# Create project-specific dependencies based on type
customize_dependencies() {
    log "Customizing dependencies for $TYPE_NAME project..."

    case $TYPE_NAME in
        "api")
            log "Adding API-specific dependencies..."
            # Add to pyproject.toml dependencies
            ;;
        "cli")
            log "Adding CLI-specific dependencies..."
            ;;
        "datascience")
            log "Adding data science dependencies..."
            # Could add jupyter, matplotlib, seaborn, etc.
            ;;
    esac
}

# Create initial source files
create_source_files() {
    log "Creating initial source files..."

    # Create __init__.py
    cat > "src/$PROJECT_NAME/__init__.py" << EOF
"""$PROJECT_DISPLAY_NAME - $PROJECT_DESCRIPTION"""

__version__ = "0.1.0"
__author__ = "$AUTHOR_NAME"
__email__ = "$AUTHOR_EMAIL"
EOF

    # Create main.py based on project type
    case $TYPE_NAME in
        "api")
            create_api_files
            ;;
        "cli")
            create_cli_files
            ;;
        *)
            create_general_files
            ;;
    esac

    success "Source files created"
}

create_api_files() {
    cat > "src/$PROJECT_NAME/main.py" << EOF
"""FastAPI application entry point."""

from fastapi import FastAPI

app = FastAPI(
    title="$PROJECT_DISPLAY_NAME",
    description="$PROJECT_DESCRIPTION",
    version="0.1.0"
)

@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Hello from $PROJECT_DISPLAY_NAME!"}

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF
}

create_cli_files() {
    cat > "src/$PROJECT_NAME/cli.py" << EOF
"""Command line interface for $PROJECT_DISPLAY_NAME."""

import click

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(verbose: bool):
    """$PROJECT_DISPLAY_NAME CLI."""
    if verbose:
        click.echo(f"Starting $PROJECT_DISPLAY_NAME in verbose mode...")
    else:
        click.echo(f"Hello from $PROJECT_DISPLAY_NAME!")

if __name__ == "__main__":
    main()
EOF
}

create_general_files() {
    cat > "src/$PROJECT_NAME/main.py" << EOF
"""Main module for $PROJECT_DISPLAY_NAME."""

def main():
    """Main function."""
    print("Hello from $PROJECT_DISPLAY_NAME!")

if __name__ == "__main__":
    main()
EOF
}

# Create test files
create_test_files() {
    log "Creating test structure..."

    mkdir -p tests/unit tests/integration

    cat > "tests/__init__.py" << EOF
"""Test package for $PROJECT_DISPLAY_NAME."""
EOF

    cat > "tests/test_main.py" << EOF
"""Test main module."""

import pytest
from src.$PROJECT_NAME.main import main


def test_main():
    """Test main function."""
    # Add your tests here
    assert main is not None
EOF

    success "Test files created"
}

# Create documentation
create_docs() {
    log "Creating documentation..."

    cat > "README.md" << EOF
# $PROJECT_DISPLAY_NAME

$PROJECT_DESCRIPTION

## 🚀 Features

- Modern Python $PYTHON_VERSION setup with UV
- Comprehensive code quality tools (ruff, black, mypy)
- Pre-commit hooks for automated quality checks
- Doppler integration for secure secrets management
- GitHub Actions CI/CD
- Comprehensive test suite with pytest
- Security scanning with bandit and safety
- Documentation with MkDocs

## 📦 Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/$GITHUB_USER/$PROJECT_NAME.git
cd $PROJECT_NAME

# Install dependencies
make install

# Set up Doppler (for secrets management)
doppler setup --project $PROJECT_NAME --config development
\`\`\`

## 🛠️ Development

\`\`\`bash
# Run tests
make test

# Format code
make format

# Run linting
make lint

# Run security checks
make security

# Start development server (if applicable)
make run
\`\`\`

## 📋 Available Commands

Run \`make help\` to see all available commands.

## 🔐 Environment Variables

This project uses Doppler for secrets management. See \`.env.doppler.template\` for required variables.

## 📄 License

MIT License - see LICENSE file for details.

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📞 Contact

**$AUTHOR_NAME** - $AUTHOR_EMAIL

Project Link: [https://github.com/$GITHUB_USER/$PROJECT_NAME](https://github.com/$GITHUB_USER/$PROJECT_NAME)
EOF

    success "Documentation created"
}

# Install UV and setup environment
setup_environment() {
    log "Setting up Python environment..."

    # Install UV if needed
    if ! command -v uv &> /dev/null; then
        log "Installing UV package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.cargo/bin:$PATH"
    fi

    # Install Python and dependencies
    log "Installing Python $PYTHON_VERSION and dependencies..."
    uv python install $PYTHON_VERSION
    uv sync --all-groups

    # Install pre-commit hooks
    log "Installing pre-commit hooks..."
    uv run pre-commit install

    success "Environment setup complete"
}

# Final summary
final_summary() {
    echo ""
    header "🎉 =================================================="
    header "🎉  PROJECT SETUP COMPLETE!"
    header "🎉 =================================================="
    echo ""

    success "✅ Project '$PROJECT_NAME' configured and ready"
    success "✅ Python $PYTHON_VERSION environment set up"
    success "✅ Dependencies installed"
    success "✅ Pre-commit hooks configured"
    success "✅ Initial source files created"

    echo ""
    header "🚀 NEXT STEPS:"
    echo ""
    echo "1. Set up Doppler for secrets:"
    echo "   doppler setup --project $PROJECT_NAME --config development"
    echo ""
    echo "2. Start developing:"
    echo "   make run          # Start development server"
    echo "   make test         # Run tests"
    echo "   make lint         # Check code quality"
    echo ""
    echo "3. Set up GitHub repository:"
    echo "   git remote add origin https://github.com/$GITHUB_USER/$PROJECT_NAME.git"
    echo "   git add ."
    echo "   git commit -m \"Initial project setup\""
    echo "   git push -u origin main"
    echo ""

    success "Happy coding! 🚀"
}

# Main execution
main() {
    welcome
    gather_project_info
    confirm_settings
    customize_template
    customize_dependencies
    create_source_files
    create_test_files
    create_docs
    setup_environment
    final_summary
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Python Project Template Setup Script"
        echo ""
        echo "Usage: $0"
        echo ""
        echo "This script interactively sets up a new Python project"
        echo "with modern best practices and development tools."
        exit 0
        ;;
    *)
        main
        ;;
esac
