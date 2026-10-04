.PHONY: up down restart logs clean shell psql migrations migrate ruff test build ps

up:
	docker compose -f docker-compose.dev.yml up -d --build

down:
	docker compose -f docker-compose.dev.yml down

restart: down up

logs:
	docker compose -f docker-compose.dev.yml logs -f

logs-app:
	docker compose -f docker-compose.dev.yml logs -f app

clean:
	docker compose -f docker-compose.dev.yml down -v --remove-orphans

shell:
	docker compose -f docker-compose.dev.yml exec app bash

psql:
	docker compose -f docker-compose.dev.yml exec postgres psql -U postgres -d ApplicationDatabase

migrations:
	docker compose -f docker-compose.dev.yml exec app alembic revision --autogenerate -m "$(msg)"

migrate:
	docker compose -f docker-compose.dev.yml exec app alembic upgrade head

downgrade:
	docker compose -f docker-compose.dev.yml exec app alembic downgrade -1

test:
	docker compose -f docker-compose.dev.yml exec app pytest -v

build:
	docker compose -f docker-compose.dev.yml build --no-cache

ps:
	docker compose -f docker-compose.dev.yml ps

help:
	@echo "Avalible commands:"
	@echo "  make up          - start all"
	@echo "  make down        - stop all containers"
	@echo "  make restart     - restart all containers"
	@echo "  make logs        - logs from all services"
	@echo "  make clean       - delete containers + volumes"
	@echo "  make shell       - shell in app"
	@echo "  make psql        - psql console"
	@echo "  make migrations msg='...' - make migration"
	@echo "  make test        - start tests"
