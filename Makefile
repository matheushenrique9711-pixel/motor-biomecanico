.PHONY: help build up down logs clean dev prod restart health test

# Project name
PROJECT_NAME := motor-biomecanico

# Docker compose commands
COMPOSE := docker-compose
COMPOSE_DEV := docker-compose -f docker-compose.yml -f docker-compose.dev.yml

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Display this help message
	@echo "$(BLUE)Motor Biomecânico - Docker Management$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Usage:$(NC)"
	@echo "  make help          Show this help message"
	@echo "  make dev           Start development environment"
	@echo "  make prod          Start production environment"
	@echo ""

# ============================================================================
# Development Commands
# ============================================================================

dev: ## Start development environment with hot reload
	@echo "$(BLUE)Starting development environment...$(NC)"
	$(COMPOSE_DEV) up --build
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "  Frontend: http://localhost:5173 (Vite dev)"
	@echo "  Backend:  http://localhost:8000/api"

dev-d: ## Start development environment in background
	@echo "$(BLUE)Starting development environment (background)...$(NC)"
	$(COMPOSE_DEV) up -d --build
	@echo "$(GREEN)✓ Development environment started$(NC)"
	@make health

# ============================================================================
# Production Commands
# ============================================================================

prod: ## Start production environment
	@echo "$(BLUE)Starting production environment...$(NC)"
	$(COMPOSE) up --build
	@echo "$(GREEN)✓ Production environment ready$(NC)"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000/api"

prod-d: ## Start production environment in background
	@echo "$(BLUE)Starting production environment (background)...$(NC)"
	$(COMPOSE) up -d --build
	@echo "$(GREEN)✓ Production environment started$(NC)"
	@make health

# ============================================================================
# Container Management
# ============================================================================

build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(COMPOSE) build
	@echo "$(GREEN)✓ Images built successfully$(NC)"

build-nc: ## Build Docker images without cache
	@echo "$(BLUE)Building Docker images (no cache)...$(NC)"
	$(COMPOSE) build --no-cache
	@echo "$(GREEN)✓ Images built successfully$(NC)"

up: ## Start services
	@echo "$(BLUE)Starting services...$(NC)"
	$(COMPOSE) up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@make health

down: ## Stop and remove containers
	@echo "$(BLUE)Stopping services...$(NC)"
	$(COMPOSE) down
	@echo "$(GREEN)✓ Services stopped$(NC)"

stop: ## Stop services
	@echo "$(BLUE)Stopping services...$(NC)"
	$(COMPOSE) stop
	@echo "$(GREEN)✓ Services stopped$(NC)"

start: ## Start services
	@echo "$(BLUE)Starting services...$(NC)"
	$(COMPOSE) start
	@echo "$(GREEN)✓ Services started$(NC)"

restart: ## Restart services
	@echo "$(BLUE)Restarting services...$(NC)"
	$(COMPOSE) restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

ps: ## Show running containers
	@$(COMPOSE) ps

# ============================================================================
# Logging and Debugging
# ============================================================================

logs: ## Show logs for all services
	@$(COMPOSE) logs -f

logs-backend: ## Show logs for backend
	@$(COMPOSE) logs -f backend

logs-frontend: ## Show logs for frontend
	@$(COMPOSE) logs -f frontend

shell-backend: ## Open shell in backend container
	@$(COMPOSE) exec backend bash

shell-frontend: ## Open shell in frontend container
	@$(COMPOSE) exec frontend sh

health: ## Check health status of services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo "Backend: " && curl -s http://localhost:8000/api/health | jq . || echo "$(RED)✗ Backend unreachable$(NC)"
	@echo "Frontend: " && curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)✓ Frontend healthy$(NC)" || echo "$(RED)✗ Frontend unreachable$(NC)"

stats: ## Show container resource usage
	@docker stats --no-stream

# ============================================================================
# Cleaning
# ============================================================================

clean: ## Remove containers and anonymous volumes
	@echo "$(BLUE)Cleaning up containers and volumes...$(NC)"
	$(COMPOSE) down -v
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-all: ## Remove all containers, volumes, and images (use with caution)
	@echo "$(RED)WARNING: This will remove all containers, volumes, and images$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(COMPOSE) down -v; \
		docker rmi $$(docker images | grep $(PROJECT_NAME) | awk '{print $$3}') 2>/dev/null || true; \
		echo "$(GREEN)✓ Complete cleanup done$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

prune: ## Remove unused Docker resources
	@echo "$(BLUE)Pruning unused Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)✓ Pruning complete$(NC)"

# ============================================================================
# Testing
# ============================================================================

test: ## Run integration tests
	@echo "$(BLUE)Running integration tests...$(NC)"
	@bash integration_test.sh
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-backend: ## Test backend endpoint
	@echo "$(BLUE)Testing backend...$(NC)"
	@curl -s http://localhost:8000/api/health | jq . && echo "$(GREEN)✓ Backend test passed$(NC)" || echo "$(RED)✗ Backend test failed$(NC)"

test-frontend: ## Test frontend endpoint
	@echo "$(BLUE)Testing frontend...$(NC)"
	@curl -s http://localhost:3000 > /dev/null && echo "$(GREEN)✓ Frontend test passed$(NC)" || echo "$(RED)✗ Frontend test failed$(NC)"

# ============================================================================
# Development Utilities
# ============================================================================

install-dev: ## Install development dependencies locally
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	cd frontend && npm install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

lint-backend: ## Run linter on backend
	@echo "$(BLUE)Linting backend...$(NC)"
	$(COMPOSE) exec backend python -m pylint app/

lint-frontend: ## Run linter on frontend
	@echo "$(BLUE)Linting frontend...$(NC)"
	$(COMPOSE) exec frontend npm run lint

# ============================================================================
# Information
# ============================================================================

info: ## Show project information
	@echo "$(BLUE)Motor Biomecânico - Project Information$(NC)"
	@echo ""
	@echo "$(GREEN)Project Name:$(NC) $(PROJECT_NAME)"
	@echo "$(GREEN)Docker Compose:$(NC) $$(docker-compose --version)"
	@echo "$(GREEN)Docker:$(NC) $$(docker --version)"
	@echo ""
	@echo "$(GREEN)Services:$(NC)"
	@$(COMPOSE) ps
	@echo ""
	@echo "$(GREEN)Volumes:$(NC)"
	@docker volume ls | grep $(PROJECT_NAME) || echo "No volumes found"
	@echo ""
	@echo "$(GREEN)Networks:$(NC)"
	@docker network ls | grep $(PROJECT_NAME) || echo "No networks found"

version: ## Show version information
	@echo "Motor Biomecânico v1.0"
	@echo "Docker Setup: Phase 3"
	@echo "Date: 2026-09-28"

# ============================================================================
# Default target
# ============================================================================

.DEFAULT_GOAL := help
