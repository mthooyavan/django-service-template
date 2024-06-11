# Makefile for backend project

# Define variables
DEV_COMPOSE_FILE=docker-compose.yml
IMAGE_NAME=backend-web
PROJECT_NAME=service

# Get the current git commit hash
SOURCE_VERSION=$(shell git rev-parse HEAD)

all: help

start:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) up -d $(IMAGE_NAME)
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) logs -f $(IMAGE_NAME)

down:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) down --remove-orphans

build:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) build --compress --build-arg SOURCE_VERSION=$(SOURCE_VERSION)

clean:
	docker system prune -f -a --filter "until=24h"

deps:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm --no-deps $(IMAGE_NAME) pip-compile --strip-extras

migrate:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python3 manage.py migrate

command:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python3 manage.py $(app)

makemigrations:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python3 manage.py makemigrations

mergemigrations:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python3 manage.py makemigrations --merge

console:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python3 manage.py shell_plus

celery-worker:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) celery -A backend_service worker -l info

celery-worker-beat:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) celery -A backend_service worker -l info -B --concurrency=6

test-local:
	PYTHONPATH=. GEOIP_PATH=./utils/geoip/ DJANGO_SETTINGS_MODULE=backend_service.settings.test pytest --reuse-db -W ignore --cov-config=.coveragerc --cov-fail-under=88 --cov-report html --cov=communications --cov=utils --durations=10

test:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run -e DJANGO_SETTINGS_MODULE=backend_service.settings.test --rm $(IMAGE_NAME) pytest --reuse-db -n auto -W ignore --cov-config=.coveragerc --cov-fail-under=88 --cov-report html --cov=communications --cov=utils --durations=10
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) down --remove-orphans

lint-local:
	PYTHONPATH=. GEOIP_PATH=./utils/geoip/ DJANGO_SETTINGS_MODULE=backend_service.settings.test pylint -j 0 --rcfile=.pylintrc backend_service communications utils tests

lint:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm --no-deps $(IMAGE_NAME) pylint --rcfile=.pylintrc backend_service communications utils tests

security-local:
	bandit -r backend_service communications utils

security:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm --no-deps $(IMAGE_NAME) bandit -r backend_service communications utils

makemessages:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py makemessages -l ar
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py makemessages -l de
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py makemessages -l es
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py makemessages -l fr
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py makemessages -l hi
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py makemessages -l kn
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py makemessages -l ta
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py makemessages -l te
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python auto_translate.py

compilemessages:
	docker compose -f $(DEV_COMPOSE_FILE) -p $(PROJECT_NAME) run --rm $(IMAGE_NAME) python manage.py compilemessages

help:
	@echo "start: Start the development server"
	@echo "down: Stop the development server"
	@echo "build: Build the development server"
	@echo "clean: Clean the docker system"
	@echo "deps: Update the dependencies"
	@echo "migrate: Run the migrations"
	@echo "makemigrations: Create the migrations"
	@echo "mergemigrations: Merge the migrations"
	@echo "console: Open the Django shell"
	@echo "celery-worker: Start the celery worker"
	@echo "celery-worker-beat: Start the celery worker with beat"
	@echo "test-local: Run the tests locally"
	@echo "test: Run the tests"
	@echo "lint-local: Run the linter locally"
	@echo "lint: Run the linter"
	@echo "security-local: Run the security check locally"
	@echo "security: Run the security check"
	@echo "makemessages: Create the messages"
	@echo "compilemessages: Compile the messages"
	@echo "help: Show this help message"

.PHONY: start down build clean deps migrate makemigrations mergemigrations console celery-worker celery-worker-beat test-local test lint-local lint security-local security makemessages compilemessages help
