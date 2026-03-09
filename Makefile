PY_DEPS = 'requirements/out.txt'
PYTEST_CMD = python -m pytest

upgrade-pip:
	@python -m pip install --upgrade pip setuptools

install: upgrade-pip	# Install all dependencies (production dependencies, tests, linter, plugins)
	@pip install -Ur $(PY_DEPS)

update_project_requirements:
	@docker-compose up -d update_project_requirements

build:
	@docker-compose build --build-arg PYPI_TOKEN=$(PYPI_TOKEN)

deps:
	@docker-compose up -d --scale payments_backend=0 --scale payments_postgres_migrations=0 --scale init-kafka=0 --scale pp_minio_createbucket=0

up: deps
	@python manage.py start

up-worker: deps
	@python manage.py start-tasks-worker

up-payment-worker: deps
	@python manage.py start-payment-worker

up-disbursement-worker: deps
	@python manage.py start-disbursement-worker

up-payment-processing-worker: deps
	@python manage.py start-payment-processing-worker

up-clients-events-worker: deps
	@python manage.py start-clients-events-worker

stop:
	@docker-compose stop

down:
	@docker-compose down -v --remove-orphans

history:
	@alembic history

upgrade: deps
	@alembic upgrade head

downgrade: deps
	@alembic downgrade -1

base: deps
	@alembic downgrade base

stairway: deps
	@alembic upgrade head
	@alembic downgrade -1
	@alembic upgrade head

generate: deps
	@alembic revision -m "$(NAME)" --autogenerate
	@alembic upgrade head
	@alembic downgrade -1
	@alembic upgrade head
	@alembic downgrade -1

test:
	@$(PYTEST_CMD) . -m "not slow" -q -o log_cli=false

regress:
	@$(PYTEST_CMD) . -m "not slow" -v --lf --log-cli-level=DEBUG

test-all:
	@$(PYTEST_CMD) . -v

lint:
	@ruff check . --fix
	@ruff format --check .

format:
	@ruff format .

fix:
	@ruff check . --fix
	@ruff format .

clean:
	@rm -rf `find . -name __pycache__`
	@rm -f `find . -type f -name '*.py[co]' `
	@rm -f `find . -type f -name '*~' `
	@rm -f `find . -type f -name '.*~' `
	@rm -f `find . -type f -name '@*' `
	@rm -f `find . -type f -name '#*#' `
	@rm -f `find . -type f -name '*.orig' `
	@rm -f `find . -type f -name '*.rej' `
	@rm -rf `find . -type d -name '.pytest_cache' `
	@rm -rf `find . -type d -name '.flakeheaven_cache' `
	@rm -f .coverage
	@rm -rf htmlcov

hooks:
	@pre-commit install
