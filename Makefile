.PHONY: help install run test lint format docker-build docker-up docker-down clean

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

run: ## Run the application locally
	python run.py

test: ## Run tests with coverage
	FLASK_ENV=testing GROQ_API_KEY=test-key pytest tests/ -v --cov=app --cov-report=term-missing

lint: ## Run linting checks
	flake8 app/ tests/ --max-line-length=100
	black --check --line-length 100 app/ tests/
	isort --check-only app/ tests/

format: ## Auto-format code
	black --line-length 100 app/ tests/
	isort app/ tests/

docker-build: ## Build Docker image
	docker build -t devops-llm-app .

docker-up: ## Start all services with Docker Compose
	docker-compose up -d --build

docker-down: ## Stop all services
	docker-compose down

docker-logs: ## View container logs
	docker-compose logs -f app

health: ## Check application health
	curl -s http://localhost:5000/health | python -m json.tool

clean: ## Remove cache and temporary files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage coverage.xml htmlcov/
