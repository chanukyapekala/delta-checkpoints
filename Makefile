.PHONY: help install install-dev test test-cov lint format type-check demo clean build publish publish-test

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package in development mode
	poetry install

install-dev: ## Install the package with all development dependencies
	poetry install --with dev,test

test: ## Run tests
	poetry run pytest

test-cov: ## Run tests with coverage
	poetry run pytest --cov=delta_checkpoints --cov-report=html --cov-report=term-missing

test-fast: ## Run tests without coverage (faster)
	poetry run pytest --no-cov

lint: ## Run linting checks
	poetry run flake8 delta_checkpoints tests
	poetry run black --check delta_checkpoints tests

format: ## Format code with black
	poetry run black delta_checkpoints tests

type-check: ## Run type checking with mypy
	poetry run mypy delta_checkpoints

demo: ## Run the demo script
	poetry run python demo.py

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	poetry build

publish: ## Publish to PyPI (requires authentication)
	./scripts/publish.sh

publish-test: ## Publish to Test PyPI (requires authentication)
	./scripts/publish.sh --test-pypi

publish-patch: ## Publish patch version to PyPI
	./scripts/publish.sh --patch

publish-minor: ## Publish minor version to PyPI
	./scripts/publish.sh --minor

publish-major: ## Publish major version to PyPI
	./scripts/publish.sh --major

check-all: ## Run all checks (lint, type-check, test)
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

dev-setup: ## Set up development environment
	poetry install --with dev,test
	poetry run pre-commit install

pre-commit: ## Run pre-commit hooks
	poetry run pre-commit run --all-files

release: ## Prepare a new release (build, test, check)
	$(MAKE) clean
	$(MAKE) check-all
	$(MAKE) build
	@echo "Release preparation complete. Run 'make publish' to publish to PyPI."

version: ## Show current version
	@poetry version -s

version-patch: ## Bump patch version
	poetry version patch
	@echo "Version bumped to $(shell poetry version -s)"

version-minor: ## Bump minor version
	poetry version minor
	@echo "Version bumped to $(shell poetry version -s)"

version-major: ## Bump major version
	poetry version major
	@echo "Version bumped to $(shell poetry version -s)" 