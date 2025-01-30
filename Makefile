# Makefile for the Content Rating System

# Python settings
PYTHON := python
VENV := venv
PIP := $(VENV)/bin/pip

# Test settings
PYTEST := $(VENV)/bin/pytest
COVERAGE := $(VENV)/bin/coverage
TEST_PATH := tests/

# Project directories
SRC_DIR := .
CORE_DIR := core
MODELS_DIR := models
UTILS_DIR := utils
API_DIR := api
STREAMLIT_DIR := streamlit_app

.PHONY: all clean install test coverage lint format help run run-api run-ui

all: install test lint ## Install dependencies, run tests and lint

help: ## Show this help message
@echo 'Usage:'
@echo '  make [target]'
@echo ''
@echo 'Targets:'
@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: clean-build clean-pyc ## Remove all build and Python artifacts

clean-build: ## Remove build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info
rm -rf htmlcov/
rm -rf .coverage
rm -rf .pytest_cache
rm -rf .cache

clean-pyc: ## Remove Python file artifacts
find . -name '*.pyc' -exec rm -f {} +
find . -name '*.pyo' -exec rm -f {} +
find . -name '__pycache__' -exec rm -rf {} +
find . -name '.pytest_cache' -exec rm -rf {} +

venv: ## Create a Python virtual environment
$(PYTHON) -m venv $(VENV)
$(PIP) install --upgrade pip

install: venv ## Install the project dependencies
$(PIP) install -r requirements.txt

test: ## Run tests with pytest
$(PYTEST) $(TEST_PATH) -v

test-unit: ## Run only unit tests
$(PYTEST) $(TEST_PATH) -v -m "unit"

test-integration: ## Run only integration tests
$(PYTEST) $(TEST_PATH) -v -m "integration"

test-fast: ## Run tests without slow-marked tests
$(PYTEST) $(TEST_PATH) -v -m "not slow"

coverage: ## Run tests with coverage report
$(PYTEST) $(TEST_PATH) --cov=$(SRC_DIR) --cov-report=term-missing --cov-report=html

coverage-report: ## Open coverage report in browser
python -m webbrowser "htmlcov/index.html"

lint: ## Check code style with pylint
$(VENV)/bin/pylint $(CORE_DIR) $(MODELS_DIR) $(UTILS_DIR) $(API_DIR) $(STREAMLIT_DIR)

format: ## Format code with black
$(VENV)/bin/black $(CORE_DIR) $(MODELS_DIR) $(UTILS_DIR) $(API_DIR) $(STREAMLIT_DIR) $(TEST_PATH)

run: ## Run both FastAPI and Streamlit servers
$(PYTHON) run.py

run-api: ## Run only the FastAPI server
uvicorn api.main:app --reload --port 8000

run-ui: ## Run only the Streamlit UI
streamlit run streamlit_app/app.py --server.port 8501

init-nltk: ## Download required NLTK data
$(PYTHON) -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Development workflow targets
dev-setup: install init-nltk ## Setup complete development environment
$(PIP) install black pylint
@echo "Development environment setup complete"

dev-clean: clean ## Clean development artifacts
rm -rf .pytest_cache
rm -rf .coverage
rm -rf htmlcov/
@echo "Development artifacts cleaned"

# Documentation targets
docs: ## Generate documentation
@echo "TODO: Add documentation generation"

# Release workflow
dist: clean ## Build distribution
$(PYTHON) setup.py sdist bdist_wheel

release: dist ## Release to PyPI
@echo "TODO: Add release process"

# CI targets
ci-test: ## Run tests in CI environment
$(PYTEST) $(TEST_PATH) -v --junitxml=test-results.xml

# Docker targets
docker-build: ## Build Docker image
docker build -t content-rating-system .

docker-run: ## Run Docker container
docker run -p 8000:8000 -p 8501:8501 content-rating-system

# Default target
.DEFAULT_GOAL := help
