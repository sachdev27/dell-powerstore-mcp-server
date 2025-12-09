# =============================================================================
# Dell PowerStore MCP Server - Makefile
# Common development commands
# =============================================================================

.PHONY: help install install-dev test test-cov lint format typecheck security clean build docker-build docker-run run run-http docs

# Default target
help:
	@echo "Dell PowerStore MCP Server - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install        Install production dependencies"
	@echo "  make install-dev    Install development dependencies"
	@echo "  make setup          Complete development setup"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run tests"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make test-verbose   Run tests with verbose output"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run linting (ruff)"
	@echo "  make format         Format code (black + ruff)"
	@echo "  make typecheck      Run type checking (mypy)"
	@echo "  make security       Run security checks (bandit)"
	@echo "  make check          Run all quality checks"
	@echo ""
	@echo "Running:"
	@echo "  make run            Run stdio server"
	@echo "  make run-http       Run HTTP/SSE server"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build   Build Docker image"
	@echo "  make docker-run     Run Docker container"
	@echo "  make docker-stop    Stop Docker container"
	@echo ""
	@echo "Build & Release:"
	@echo "  make build          Build distribution packages"
	@echo "  make clean          Clean build artifacts"
	@echo ""

# =============================================================================
# Setup
# =============================================================================

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

setup: install-dev
	@echo "Development environment ready!"

# =============================================================================
# Testing
# =============================================================================

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=powerstore_mcp --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

test-verbose:
	pytest tests/ -v -s --tb=long

# =============================================================================
# Code Quality
# =============================================================================

lint:
	ruff check powerstore_mcp tests

lint-fix:
	ruff check --fix powerstore_mcp tests

format:
	black powerstore_mcp tests
	ruff check --fix powerstore_mcp tests

format-check:
	black --check powerstore_mcp tests
	ruff check powerstore_mcp tests

typecheck:
	mypy powerstore_mcp

security:
	bandit -r powerstore_mcp -c pyproject.toml

check: format-check typecheck security test
	@echo "All checks passed!"

# =============================================================================
# Running
# =============================================================================

run:
	python -m powerstore_mcp.main

run-http:
	uvicorn powerstore_mcp.http_server:app --host 0.0.0.0 --port 3000 --reload

run-http-prod:
	uvicorn powerstore_mcp.http_server:app --host 0.0.0.0 --port 3000

# =============================================================================
# Docker
# =============================================================================

docker-build:
	docker build -t dell-powerstore-mcp-server:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-shell:
	docker-compose exec powerstore-mcp /bin/bash

# =============================================================================
# Build & Release
# =============================================================================

build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# =============================================================================
# Documentation
# =============================================================================

docs:
	@echo "Documentation is in README.md and CONTRIBUTING.md"

# =============================================================================
# Pre-commit
# =============================================================================

pre-commit:
	pre-commit run --all-files

pre-commit-update:
	pre-commit autoupdate
