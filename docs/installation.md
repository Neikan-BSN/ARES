# Installation

## Prerequisites

- Python 3.12.10 or higher
- UV package manager

## Install UV

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Install Agent Reliability Enforcement System

### From Source

```bash
# Clone the repository
git clone https://github.com/ares-team/ares.git
cd ares

# Install dependencies
make install
```

### From PyPI (when published)

```bash
uv add ares
```

## Environment Setup

### 1. Doppler Setup (Recommended)

```bash
# Install Doppler CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# Login and setup
doppler login
doppler setup --project ares --config development

# Set required secrets
doppler secrets set API_SECRET_KEY="your-secret-key"  # pragma: allowlist secret
doppler secrets set JWT_SECRET_KEY="your-jwt-secret"  # pragma: allowlist secret
```

### 2. Local Environment (Development Only)

For local development, you can use environment variables:

```bash
export API_SECRET_KEY="your-secret-key"  # pragma: allowlist secret
export JWT_SECRET_KEY="your-jwt-secret"  # pragma: allowlist secret
```

## Verification

Verify your installation:

```bash
# Check installation
make test

# Run the application
make run
```

## Development Setup

For development, install additional tools:

```bash
# Install all development dependencies
make install-dev

# Install pre-commit hooks
make install
```

## Docker Setup (Optional)

```bash
# Build Docker image
make docker-build

# Run with Docker Compose
make docker-run
```

## Troubleshooting

### Common Issues

**UV not found**
```bash
# Add UV to PATH
export PATH="$HOME/.cargo/bin:$PATH"
```

**Permission errors**
```bash
# Make scripts executable
chmod +x scripts/*.sh
```

**Import errors**
```bash
# Ensure you're in the project root and have activated the environment
uv run python -c "import ares; print('✅ Import successful')"
```

## Next Steps

- [Quick Start Guide](quickstart.md)
- [Configuration](configuration.md)
- [API Reference](api.md)
