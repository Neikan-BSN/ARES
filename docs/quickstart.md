# Quick Start

Get up and running with Agent Reliability Enforcement System in minutes!

## 1. Setup

```bash
# Clone and enter the project
git clone https://github.com/ares-team/ares.git
cd ares

# Run the interactive setup (recommended)
./scripts/setup_project.sh
```

Or manually:

```bash
# Install dependencies
make install

# Set up secrets management
doppler setup --project ares --config development
```

## 2. Basic Usage

### Command Line Interface

```bash
# Run the CLI
uv run project-cli --help

# Example usage
uv run project-cli --verbose
```

### As a Python Module

```python
from ares import main

# Run the main function
main()
```

### API Server (if applicable)

```bash
# Start the development server
make run-api

# The API will be available at http://localhost:8000
```

## 3. Development Workflow

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Fix issues automatically
make lint-fix
```

### Testing

```bash
# Run all tests
make test

# Run with coverage
make test
```

### Security

```bash
# Run security scans
make security

# Update dependencies
uv sync --upgrade
```

## 4. Common Tasks

### Adding Dependencies

```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --group dev pytest-mock
```

### Environment Variables

Set in Doppler:
```bash
doppler secrets set NEW_SECRET="value"  # pragma: allowlist secret
```

Or locally (development only):
```bash
export NEW_SECRET="value"  # pragma: allowlist secret
```

### Running Scripts

```bash
# With Doppler (recommended)
doppler run -- python your_script.py

# With UV
uv run python your_script.py
```

## 5. Deployment

### Building

```bash
# Build the package
uv build

# Build Docker image
make docker-build
```

### CI/CD

The project includes GitHub Actions workflows that automatically:

- Run tests on every push
- Perform security scans
- Build and deploy (when configured)

## 6. Getting Help

### Documentation

```bash
# Serve documentation locally
make docs-serve
# Visit http://localhost:8001
```

### Available Commands

```bash
# See all available make commands
make help
```

### Common Commands

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make test` | Run test suite |
| `make lint` | Run code quality checks |
| `make format` | Format code |
| `make run` | Start development server |
| `make docs` | Generate documentation |
| `make clean` | Clean build artifacts |

## 7. Next Steps

- Read the [API Reference](api.md)
- Set up your [development environment](development.md)
- Learn about [contributing](contributing.md)
- Explore the [configuration options](configuration.md)

## Examples

### Basic Example

```python
# example.py
from ares import main

if __name__ == "__main__":
    main()
```

Run with:
```bash
uv run python example.py
```

### Advanced Example

See the `examples/` directory for more comprehensive examples.

## Troubleshooting

**Import errors**: Make sure you're using `uv run` or have activated the virtual environment.

**Permission errors**: Make scripts executable with `chmod +x scripts/*.sh`.

**Doppler issues**: Run `doppler login` and `doppler setup` to reconfigure.
