# Armada PBMS Development Commands

.PHONY: help test test-unit test-integration test-functional test-coverage run clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

test: ## Run all tests
	@echo "Running all tests..."
	@python -m pytest tests/ -v

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	@python -m pytest tests/unit/ -v -m unit

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	@python -m pytest tests/integration/ -v -m integration

test-functional: ## Run functional tests only
	@echo "Running functional tests..."
	@python -m pytest tests/functional/ -v -m functional

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	@python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

run: ## Run the Flask application
	@echo "Starting Flask application..."
	@python run.py

run-dev: ## Run the Flask application in development mode
	@echo "Starting Flask application in development mode..."
	@FLASK_ENV=development FLASK_DEBUG=1 python run.py

clean: ## Clean up generated files
	@echo "Cleaning up..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@find . -type d -name "htmlcov" -exec rm -rf {} +
	@find . -type f -name ".coverage" -delete
	@echo "✅ Cleanup complete" 