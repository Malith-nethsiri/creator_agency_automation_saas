.PHONY: help build up down logs shell migrate test clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up

down: ## Stop all services
	docker-compose down

logs: ## View logs
	docker-compose logs -f

shell: ## Access backend container shell
	docker-compose exec backend bash

migrate: ## Run database migrations
	docker-compose exec backend alembic upgrade head

test: ## Run tests
	docker-compose exec backend pytest

clean: ## Clean up containers and volumes
	docker-compose down -v
	docker system prune -f

restart: down up ## Restart all services

health: ## Check service health
	curl -f http://localhost:8000/api/v1/health

prod-deploy: ## Deploy to production
	docker-compose -f docker-compose.yml up -d --build
