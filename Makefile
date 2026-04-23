.PHONY: help up down build logs ps clean \
        test-all test-unit test-integration test-contract test-e2e \
        migrate-master lint format typecheck install-dev

SHELL := /bin/bash
PLATFORM_SERVICES := auth-service tenant-service user-service audit-service \
                     notification-service config-service workflow-engine \
                     file-service reporting-service analytics-service \
                     schedule-service gateway-service
QMS_SERVICES := document-service quality-event-service capa-service \
               training-service equipment-service
EM_SERVICES := plate-service image-service ai-service job-service qa-review-service
CCV_SERVICES := crm-service contract-service workorder-service \
               technician-service billing-service

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ============================================================
# Docker Compose
# ============================================================
up: ## Start full local dev stack
	docker-compose up -d

up-infra: ## Start only infrastructure services (postgres, redis, kafka, minio, etc.)
	docker-compose up -d postgres redis kafka schema-registry minio opensearch mailhog vault

up-observability: ## Start observability stack (prometheus, grafana, loki, jaeger)
	docker-compose up -d prometheus grafana loki promtail jaeger

down: ## Stop all services
	docker-compose down

down-volumes: ## Stop all services and remove volumes (DESTRUCTIVE)
	docker-compose down -v

build: ## Build all service images
	docker-compose build

build-service: ## Build specific service: make build-service SVC=auth-service
	docker-compose build $(SVC)

logs: ## Follow logs for all services
	docker-compose logs -f

logs-service: ## Follow logs for specific service: make logs-service SVC=auth-service
	docker-compose logs -f $(SVC)

ps: ## Show running services
	docker-compose ps

clean: ## Remove dangling images and volumes
	docker system prune -f

# ============================================================
# Testing
# ============================================================
test-unit: ## Run unit tests for all services (no containers)
	@for svc in $(PLATFORM_SERVICES); do \
		echo "=== Unit tests: $$svc ==="; \
		cd backend/platform/$$svc && \
		python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing --cov-fail-under=80 && \
		cd ../../..; \
	done

test-integration: ## Run integration tests (requires Docker)
	@for svc in $(PLATFORM_SERVICES); do \
		echo "=== Integration tests: $$svc ==="; \
		cd backend/platform/$$svc && \
		python -m pytest tests/integration/ -v && \
		cd ../../..; \
	done

test-contract: ## Run Pact contract tests
	@for svc in $(PLATFORM_SERVICES); do \
		echo "=== Contract tests: $$svc ==="; \
		cd backend/platform/$$svc && \
		python -m pytest tests/contract/ -v && \
		cd ../../..; \
	done

test-e2e: ## Run E2E tests
	@for svc in $(PLATFORM_SERVICES); do \
		echo "=== E2E tests: $$svc ==="; \
		cd backend/platform/$$svc && \
		python -m pytest tests/e2e/ -v && \
		cd ../../..; \
	done

test-all: test-unit test-integration test-contract test-e2e ## Run all tests

test-service: ## Run all tests for specific service: make test-service SVC=auth-service
	cd backend/platform/$(SVC) && \
	python -m pytest tests/ -v --cov=app --cov-report=html

test-unit-qms: ## Run unit tests for QMS services
	@for svc in $(QMS_SERVICES); do \
		echo "=== Unit tests: $$svc ==="; \
		cd backend/qms/$$svc && \
		python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing --cov-fail-under=70 && \
		cd ../../..; \
	done

test-unit-em: ## Run unit tests for EM services
	@for svc in $(EM_SERVICES); do \
		echo "=== Unit tests: $$svc ==="; \
		cd backend/em/$$svc && \
		python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing --cov-fail-under=70 && \
		cd ../../..; \
	done

test-unit-ccv: ## Run unit tests for CCV services
	@for svc in $(CCV_SERVICES); do \
		echo "=== Unit tests: $$svc ==="; \
		cd backend/ccv/$$svc && \
		python -m pytest tests/unit/ -v --cov=app --cov-report=term-missing --cov-fail-under=70 && \
		cd ../../..; \
	done

test-unit-all: test-unit test-unit-qms test-unit-em test-unit-ccv ## Run unit tests for ALL services

test-frontend: ## Run frontend tests
	cd frontend/apps/web && npm test

test-e2e-frontend: ## Run Playwright E2E tests
	cd frontend/apps/web && npx playwright test

# ============================================================
# Database Migrations
# ============================================================
migrate-master: ## Run master DB migrations
	cd backend/platform/auth-service && \
	alembic upgrade head

migrate-tenant: ## Run tenant DB migrations for all tenants
	python backend/scripts/migrate_all_tenants.py

migrate-qms: ## Run Alembic migrations for QMS services
	@for svc in $(QMS_SERVICES); do \
		echo "=== Migrating: $$svc ==="; \
		cd backend/qms/$$svc && alembic upgrade head && cd ../../..; \
	done

migrate-em: ## Run Alembic migrations for EM services
	@for svc in $(EM_SERVICES); do \
		echo "=== Migrating: $$svc ==="; \
		cd backend/em/$$svc && alembic upgrade head && cd ../../..; \
	done

migrate-ccv: ## Run Alembic migrations for CCV services
	@for svc in $(CCV_SERVICES); do \
		echo "=== Migrating: $$svc ==="; \
		cd backend/ccv/$$svc && alembic upgrade head && cd ../../..; \
	done

migrate-all: migrate-master migrate-qms migrate-em migrate-ccv ## Run ALL migrations

# ============================================================
# Code Quality
# ============================================================
lint: ## Run ruff linter on all backend
	ruff check backend/

format: ## Auto-format with ruff
	ruff format backend/
	ruff check --fix backend/

typecheck: ## Run mypy type checking
	mypy backend/shared/rainer_common \
	     backend/shared/rainer_auth_lib \
	     backend/shared/rainer_tenant_lib

lint-frontend: ## Lint frontend code
	cd frontend/apps/web && npm run lint

# ============================================================
# Setup
# ============================================================
install-dev: ## Install all Python dev dependencies
	pip install -e backend/shared/rainer_common[dev]
	pip install -e backend/shared/rainer_auth_lib[dev]
	pip install -e backend/shared/rainer_tenant_lib[dev,redis]
	@for svc in $(PLATFORM_SERVICES); do \
		pip install -e backend/platform/$$svc[dev]; \
	done
	@for svc in $(QMS_SERVICES); do \
		pip install -e backend/qms/$$svc[dev]; \
	done
	@for svc in $(EM_SERVICES); do \
		pip install -e backend/em/$$svc[dev]; \
	done
	@for svc in $(CCV_SERVICES); do \
		pip install -e backend/ccv/$$svc[dev]; \
	done

install-frontend: ## Install frontend dependencies
	cd frontend/apps/web && npm install

setup-minio: ## Create MinIO buckets
	@until docker-compose exec minio mc alias set local http://localhost:9000 rainer_minio rainer_minio_dev_secret; do sleep 2; done
	docker-compose exec minio mc mb local/rainer-files --ignore-existing
	docker-compose exec minio mc mb local/rainer-reports --ignore-existing

# ============================================================
# K8s
# ============================================================
k8s-apply: ## Apply all K8s manifests
	kubectl apply -f infra/k8s/namespaces/
	kubectl apply -f infra/k8s/infra/
	kubectl apply -f infra/k8s/platform/

k8s-delete: ## Delete all K8s resources
	kubectl delete -f infra/k8s/platform/
	kubectl delete -f infra/k8s/infra/
	kubectl delete -f infra/k8s/namespaces/
