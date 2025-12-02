# Makefile for SilentTrendFarm Project

.PHONY: help install dev build deploy test clean

help: ## Show this help message
	@echo "SilentTrendFarm - Blog with Python Backend"
	@echo "==========================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies (frontend + backend)
	@echo "📦 Installing frontend dependencies..."
	npm install
	@echo "📦 Installing backend dependencies..."
	pip install -r requirements.txt
	@echo "✅ All dependencies installed!"

dev: ## Run development servers (frontend + backend)
	@echo "🚀 Starting development servers..."
	@echo "Frontend: http://localhost:4321"
	@echo "Backend:  http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@trap 'kill %1; kill %2' SIGINT; \
	npm run dev & \
	cd backend && python run_server.py & \
	wait

dev-frontend: ## Run only frontend dev server
	npm run dev

dev-backend: ## Run only backend dev server
	cd backend && python run_server.py

dev-docker: ## Run with Docker Compose
	docker-compose up

build: ## Build production assets
	@echo "🔨 Building production assets..."
	npm run build
	@echo "✅ Build complete! Output in ./dist"

test-backend: ## Run backend tests
	@echo "🧪 Running backend tests..."
	cd backend && python -m pytest tests/ -v

test-api: ## Test API endpoints
	@echo "🧪 Testing API endpoints..."
	@curl -s http://localhost:8000/health | python -m json.tool
	@echo ""
	@curl -s http://localhost:8000/api/stats | python -m json.tool

deploy-netlify: ## Deploy to Netlify
	@echo "🚀 Deploying to Netlify..."
	npm run build
	netlify deploy --prod

deploy-backend: ## Deploy backend (interactive)
	cd backend && bash deploy.sh

setup-env: ## Setup environment file
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ Created .env file. Please edit it with your API keys."; \
	else \
		echo "⚠️  .env file already exists"; \
	fi

lint: ## Lint code
	@echo "🔍 Linting code..."
	cd backend && python -m flake8 . --max-line-length=100
	npm run lint --if-present

format: ## Format code
	@echo "✨ Formatting code..."
	cd backend && python -m black .
	npm run format --if-present

clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/
	rm -rf backend/__pycache__/
	rm -rf backend/*.pyc
	rm -rf node_modules/
	@echo "✅ Clean complete!"

docker-build: ## Build Docker image
	docker build -t silenttrendfarm-backend ./backend

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env silenttrendfarm-backend

logs: ## Show backend logs
	tail -f backend/logs/*.log 2>/dev/null || echo "No logs found"

status: ## Check service status
	@echo "📊 Service Status:"
	@echo "==================="
	@curl -s http://localhost:4321 > /dev/null 2>&1 && echo "✅ Frontend: Running" || echo "❌ Frontend: Not running"
	@curl -s http://localhost:8000/health > /dev/null 2>&1 && echo "✅ Backend: Running" || echo "❌ Backend: Not running"
	@curl -s http://localhost:8000/docs > /dev/null 2>&1 && echo "✅ API Docs: Available" || echo "❌ API Docs: Not available"

# Quick commands
up: dev ## Alias for dev
down: ## Stop all services
	@pkill -f "npm run dev" || true
	@pkill -f "uvicorn" || true
	@docker-compose down || true
	@echo "✅ All services stopped"
