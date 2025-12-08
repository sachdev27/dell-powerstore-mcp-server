# Contributing to PowerStore MCP Server

Thank you for your interest in contributing to the PowerStore MCP Server! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Release Process](#release-process)

## Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

### Our Standards

- **Be respectful**: Treat everyone with respect and consideration
- **Be constructive**: Provide helpful feedback and accept it graciously
- **Be inclusive**: Welcome newcomers and help them learn
- **Be professional**: Focus on what is best for the community and project

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- A GitHub account

### Finding Issues to Work On

- Look for issues labeled `good first issue` for beginner-friendly tasks
- Issues labeled `help wanted` are actively seeking contributions
- Feel free to ask questions on any issue before starting work

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/powerstore-mcp-server.git
cd powerstore-mcp-server

# Add the upstream repository
git remote add upstream https://github.com/sachdev27/powerstore-mcp-server.git
```

### 2. Create Virtual Environment

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows
```

### 3. Install Dependencies

```bash
# Install in development mode with all extras
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 4. Verify Setup

```bash
# Run tests to ensure everything is working
pytest

# Run linting
ruff check powerstore_mcp

# Run type checking
mypy powerstore_mcp
```

## Making Changes

### 1. Create a Branch

```bash
# Sync with upstream
git fetch upstream
git checkout main
git merge upstream/main

# Create a feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes

### 2. Make Your Changes

- Write clean, readable code
- Follow the [coding standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run the full test suite
pytest

# Run with coverage
pytest --cov=powerstore_mcp --cov-report=term-missing

# Run specific tests
pytest tests/test_tool_generator.py -v

# Run pre-commit checks
pre-commit run --all-files
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new feature X"
```

#### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Test additions or fixes
- `chore` - Maintenance tasks

**Examples:**
```
feat(tools): add support for volume snapshots
fix(api): handle connection timeout properly
docs(readme): add installation instructions
test(server): add unit tests for tool handlers
```

## Submitting Changes

### 1. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 2. Create a Pull Request

1. Go to your fork on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template:
   - Clear description of changes
   - Link to related issues
   - Screenshots if applicable
   - Testing instructions

### Pull Request Guidelines

- **One feature per PR**: Keep PRs focused and atomic
- **Tests required**: All new features must have tests
- **Documentation**: Update docs for user-facing changes
- **CI must pass**: All checks must be green before merge
- **Code review**: Address all review comments

### 3. Respond to Review

- Be responsive to feedback
- Make requested changes promptly
- Push additional commits to the same branch
- Request re-review when ready

## Coding Standards

### Python Style

We use [Black](https://black.readthedocs.io/) for formatting and [Ruff](https://github.com/astral-sh/ruff) for linting:

```bash
# Format code
black powerstore_mcp tests

# Check linting
ruff check powerstore_mcp tests

# Fix auto-fixable issues
ruff check --fix powerstore_mcp tests
```

### Type Hints

All code should include type hints:

```python
from typing import Any

async def process_data(
    data: dict[str, Any],
    validate: bool = True,
) -> list[str]:
    """Process the input data.

    Args:
        data: The data to process.
        validate: Whether to validate input.

    Returns:
        List of processed strings.

    Raises:
        ValueError: If data is invalid.
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def function_name(arg1: str, arg2: int) -> bool:
    """Short description of function.

    Longer description if needed, explaining the function's
    behavior in more detail.

    Args:
        arg1: Description of first argument.
        arg2: Description of second argument.

    Returns:
        Description of return value.

    Raises:
        ValueError: When arg1 is empty.
        TypeError: When arg2 is not an integer.

    Example:
        >>> function_name("hello", 42)
        True
    """
```

### Import Organization

Imports should be organized in this order:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

import httpx
from mcp.types import Tool

from powerstore_mcp.config import Config
from powerstore_mcp.exceptions import APIError

if TYPE_CHECKING:
    from collections.abc import Sequence
```

## Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_api_client.py   # API client tests
├── test_config.py       # Configuration tests
├── test_server.py       # Server tests
└── test_tool_generator.py  # Tool generator tests
```

### Writing Tests

```python
import pytest
from powerstore_mcp.config import Config

class TestConfig:
    """Tests for Config class."""

    def test_default_values(self) -> None:
        """Test that default values are set correctly."""
        config = Config()
        assert config.log_level == "info"

    def test_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test loading from environment variables."""
        monkeypatch.setenv("LOG_LEVEL", "debug")
        config = Config.from_environment()
        assert config.log_level == "debug"

    @pytest.mark.asyncio
    async def test_async_operation(self) -> None:
        """Test async functionality."""
        result = await some_async_function()
        assert result is not None
```

### Test Requirements

- **Isolation**: Tests should not depend on each other
- **Mocking**: Mock external services and APIs
- **Coverage**: Aim for >80% code coverage
- **Speed**: Tests should run quickly

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=powerstore_mcp --cov-report=html

# Run specific test class
pytest tests/test_config.py::TestConfig

# Run tests matching pattern
pytest -k "test_api"
```

## Documentation

### Where to Document

- **Code**: Docstrings for all public functions/classes
- **README.md**: User-facing documentation
- **CHANGELOG.md**: Version history and changes
- **docs/**: Extended documentation (if needed)

### Documentation Style

- Use clear, concise language
- Include code examples
- Keep documentation up to date with code changes
- Use proper Markdown formatting

## Release Process

Releases are managed by maintainers. Here's an overview:

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Creating a Release

1. Update `CHANGELOG.md` with changes
2. Update version in `powerstore_mcp/__init__.py`
3. Create a version tag:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
4. GitHub Actions will automatically:
   - Run tests
   - Build packages
   - Create GitHub release
   - Publish to PyPI

## Questions?

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers for sensitive issues

---

Thank you for contributing! 🎉
