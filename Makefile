SOURCE_VERSION := $(shell git rev-parse HEAD)

start:
	docker compose up -d web
	docker compose logs -f web

down:
	docker compose down --remove-orphans

build:
	docker compose build --compress --build-arg SOURCE_VERSION=$(SOURCE_VERSION)

clean:
	docker system prune -f -a --filter "until=24h"

deps:
	docker compose run --rm --no-deps web pip-compile

migrate:
	docker compose up -d db
	sleep 5
	docker compose run --rm web python3 manage.py migrate

makemigrations:
	docker compose run --rm web python3 manage.py makemigrations

mergemigrations:
	docker compose run --rm web python3 manage.py makemigrations --merge

console:
	docker compose run web python3 manage.py shell_plus

celery-worker:
	docker compose run web celery -A backend_service worker -l info

celery-worker-beat:
	docker compose run web celery -A backend_service worker -l info -B --concurrency=6

test-local:
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=backend_service.settings pytest --reuse-db -W error -W ignore::django.utils.deprecation.RemovedInDjango51Warning --cov-config=.coveragerc --cov-fail-under=88 --cov-report html --cov=communication --cov=engineering --cov=services --cov=utils --durations=10

test:
	docker compose up -d web
	docker compose run web pytest --reuse-db -W error -W ignore::django.utils.deprecation.RemovedInDjango51Warning --cov-config=.coveragerc --cov-fail-under=88 --cov-report html --cov=communication --cov=engineering --cov=services --cov=utils --durations=10

lint-local:
	PYTHONPATH=. DJANGO_SETTINGS_MODULE=backend_service.settings pylint -j 0 --rcfile=.pylintrc backend_service communications engineering services utils

lint:
	docker compose run --no-deps web pylint --rcfile=.pylintrc backend_service communications engineering services utils

security-local:
	bandit -r backend_service communications engineering services utils

security:
	docker compose run --no-deps web bandit -r backend_service communications engineering services utils
