# Variables
DOCKER = /usr/local/bin/docker
DOCKER_COMPOSE = /usr/local/bin/docker compose
BACKEND_DIR = backend
FRONTEND_DIR = frontend

.PHONY: help build up down restart logs clean-docker test

help:
	@echo "Usage:"
	@echo "  make build          Build all docker images"
	@echo "  make up             Start all services in background"
	@echo "  make down           Stop and remove all containers"
	@echo "  make restart        Restart all services"
	@echo "  make logs           Show logs for all services"
	@echo "  make clean-docker   Remove unused docker images and volumes"
	@echo "  make test           Run tests (placeholder)"

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) restart

logs:
	$(DOCKER_COMPOSE) logs -f

clean-docker:
	docker system prune -f

test:
	@echo "Running backend tests..."
	cd $(BACKEND_DIR) && python3 -m pytest test_app.py
