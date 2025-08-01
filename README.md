# Python Project Template

A modern Python project template with comprehensive development tools, automation, and best practices.

## 🚀 Features

- **Python 3.12.10** setup with UV package manager
- **Comprehensive code quality tools** (ruff, black, mypy)
- **Pre-commit hooks** for automated quality checks
- **Doppler integration** for secure secrets management
- **GitHub Actions CI/CD** with automated workflows
- **Comprehensive test suite** with pytest and coverage
- **Security scanning** with bandit and safety
- **Documentation** with MkDocs
- **Interactive setup script** for easy customization

## 📦 Quick Start

### 1. Use This Template

```bash
# Clone or copy this template to your new project directory
cp -r template_workspace/ my_new_project/
cd my_new_project/

# Run the interactive setup
./scripts/setup_project.sh
```

### 2. Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
make install

# Set up Doppler for secrets management
doppler setup --project your-project-name --config development
```

## 🛠️ Development Workflow

### Environment Setup
```bash
# Install all dependencies
make install

# Install only development dependencies
make install-dev
```

### Code Quality
```bash
# Format code
make format

# Check formatting
make format-check

# Run linting
make lint

# Fix linting issues automatically
make lint-fix
```

### Testing
```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run integration tests
make test-integration
```

### Security
```bash
# Run security scans
make security

# Update secrets baseline
make secrets-update
```

### Development Server
```bash
# Start development server
make run

# Start API server (if applicable)
make run-api
```

## 📋 Available Commands

Run `make help` to see all available commands:

```
Environment setup:
  install         Install all dependencies with UV
  install-dev     Install development dependencies only

Code quality:
  lint           Run all linting checks
  format         Format code with black and ruff
  format-check   Check if code is properly formatted
  lint-fix       Automatically fix linting issues

Testing:
  test           Run all tests
  test-unit      Run unit tests only
  test-integration Run integration tests

Security:
  security       Run security scans
  secrets-update Update secrets baseline

Development:
  run            Start the development server
  run-api        Start API server
  clean          Clean build artifacts and cache
  dev-reset      Reset development environment
  ci-check       Run all CI checks locally

Documentation:
  docs           Generate documentation
  docs-serve     Serve documentation locally
  docs-deploy    Deploy documentation

Utilities:
  backup         Backup project data
  restore        Restore from backup
  version        Show current version
  setup          Run interactive project setup
```

## 🔐 Environment Variables

This project uses **Doppler** for secrets management. See `.env.doppler.template` for all available configuration options.

### Required Secrets (set in Doppler):
- `API_SECRET_KEY` - Application secret key
- `JWT_SECRET_KEY` - JWT signing secret

### Optional Configuration:
- `DATABASE_URL` - Database connection string
- `DEBUG` - Debug mode (true/false)
- `LOG_LEVEL` - Logging level (info, debug, warning, error)

### Doppler Setup:
```bash
# Install Doppler CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# Login and setup
doppler login
doppler setup --project your-project-name --config development

# Set required secrets
doppler secrets set API_SECRET_KEY="your-secret-key"
doppler secrets set JWT_SECRET_KEY="your-jwt-secret"

# Run with secrets
doppler run -- python src/project_name/main.py
```

## 🏗️ Project Structure

```
project_name/
├── src/
│   └── project_name/           # Main package
│       ├── __init__.py
│       ├── main.py             # Main application entry
│       └── cli.py              # Command line interface
├── tests/                      # Test suite
│   ├── __init__.py
│   └── test_main.py
├── scripts/                    # Utility scripts
│   └── setup_project.sh        # Interactive setup
├── docs/                       # Documentation
├── .github/
│   └── workflows/              # GitHub Actions
│       ├── ci.yml              # Main CI/CD pipeline
│       ├── health-monitor.yml  # Health monitoring
│       └── lint-repair-validation.yml
├── config/                     # Configuration files
├── pyproject.toml             # Dependencies & tool config
├── Makefile                   # Development automation
├── .pre-commit-config.yaml    # Pre-commit hooks
├── .env.doppler.template      # Environment template
├── .env.DOPPLER_REQUIRED      # Required secrets
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔧 Customization

### Interactive Setup
The template includes an interactive setup script that customizes the project:

```bash
./scripts/setup_project.sh
```

This script will:
- Prompt for project details (name, description, author, etc.)
- Customize all template files with your information
- Set up the Python environment
- Install dependencies and pre-commit hooks
- Generate project-specific documentation

### Manual Customization
If you prefer manual customization, replace the following placeholders:

- `project_name` → your actual project name (snake_case)
- `PROJECT_NAME` → your project display name
- `your.email@example.com` → your email address
- `Your Name` → your name
- `your-username` → your GitHub username

## 🚀 GitHub Actions

The template includes comprehensive GitHub Actions workflows:

### CI/CD Pipeline (`ci.yml`)
- Code quality checks (ruff, black, mypy)
- Security scanning (bandit, safety)
- Test execution with coverage
- Package building
- Docker image building
- Automated deployment

### Health Monitor (`health-monitor.yml`)
- Daily health checks
- Dependency audits
- Code quality trend analysis
- Automated issue creation for problems

### Lint Repair Validation (`lint-repair-validation.yml`)
- Validates automated lint repairs
- Ensures fixes don't break functionality
- Safety validation for repair tools

## 📚 Documentation

Generate and serve documentation:

```bash
# Generate documentation
make docs

# Serve locally at http://localhost:8001
make docs-serve

# Deploy to GitHub Pages
make docs-deploy
```

## 🐳 Docker Support

Build and run with Docker:

```bash
# Build Docker image
make docker-build

# Run with Docker Compose
make docker-run
```

## 🔒 Security

The template includes comprehensive security measures:

- **Secrets management** with Doppler (no .env files)
- **Security scanning** with bandit and safety
- **Dependency vulnerability checks**
- **Secret detection** with detect-secrets
- **Pre-commit security hooks**

## 📄 License

This template is provided under the MIT License. Replace with your project's license.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make ci-check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📞 Support

For questions about this template:

- Create an issue in the repository
- Check the documentation in `docs/`
- Review the example configurations

## 🎯 Next Steps After Setup

1. **Configure Doppler secrets** for your environment
2. **Set up your GitHub repository** and enable Actions
3. **Customize the CI/CD pipeline** for your deployment needs
4. **Add project-specific dependencies** to `pyproject.toml`
5. **Write your application code** in `src/project_name/`
6. **Add comprehensive tests** in `tests/`
7. **Update documentation** in `docs/`

---

**Happy coding!** 🚀

This template provides a solid foundation for modern Python development with best practices, automation, and security built-in.
