# geotravels

MVP backend API for marking visited countries on a political map.

## Stack
- Python 3.14
- Litestar 2
- Pydantic + pydantic-settings
- SQLAlchemy Core
- PostgreSQL
- asyncpg connection pool
- Alembic

## Quick start
1. Start PostgreSQL:
   ```bash
   docker compose up -d
   ```
2. Sync dependencies:
   ```bash
   uv sync --group dev
   ```
3. Configure env:
   ```bash
   cp .env.example .env
   ```
4. Run migrations and seed countries:
   ```bash
   uv run python manage.py migrate
   uv run python manage.py seed-countries
   ```
5. Run API:
   ```bash
   uv run python manage.py run --reload
   ```

## Management commands
- `uv run python manage.py run --reload`
- `uv run python manage.py migrate [revision]`
- `uv run python manage.py create-revision -m "message" --autogenerate`
- `uv run python manage.py seed-countries`
- `uv run python manage.py init-db`
