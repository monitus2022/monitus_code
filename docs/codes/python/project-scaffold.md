---
title: Project scaffold
---

# Project scaffold

The repo-level layout and files for a fresh Python project — everything that
sits *outside* the `app/` package.

The application package itself (`main.py`, `core/`, `services/` and `api/v1/`)
is covered in [FastAPI boilerplate](fastapi-boilerplate.md).

## Layout

The layout includes:

- Github actions (CI/CD)
- Core logics
    - API serving (Health check / actual API serving)
    - Services
- Test modules
- Config / ENV setup
- Docker

??? "Example layout"

    ```text
    my-python-app/
    ├── .github/
    │   └── workflows/
    │       └── ci.yml              # CI pipeline (lint, dual-state test matrix, Docker checks)
    ├── app/                       # Application source code
    │   ├── __init__.py
    │   ├── main.py                # Entrypoint (e.g., FastAPI app instantiation)
    │   ├── api/                   # Route handlers & endpoints
    │   │   ├── __init__.py
    │   │   └── v1/
    │   │       └── search.py
    │   ├── core/                  # Infrastructure & configuration
    │   │   ├── __init__.py
    │   │   ├── config.py          # App settings (Pydantic Settings)
    │   │   ├── database.py        # Connection pools (asyncpg / pgvector)
    │   │   └── flags.py           # Feature gating registry & LRU cache
    │   └── services/              # Business logic & AI/RAG engine orchestration
    ├── scripts/                   # Dev & CI automation
    │   └── capture_ui.py          # Playwright headless screenshot tool for PR visual proof
    ├── tests/                     # Test suite
    │   ├── conftest.py            # Shared fixtures & test client setup
    │   ├── test_api.py            # API endpoint integration tests
    │   └── test_search_flags.py   # Dual-state feature flag verification tests
    ├── .env.example               # Template for local environment variables
    ├── .gitignore                 # Excludes .venv/, .ai/, __pycache__/, .env
    ├── AGENT.md                   # AI Coding Agent operational charter & rules
    ├── Dockerfile                 # Multi-stage Docker build using uv
    ├── docker-compose.yml         # Local dev environment & test database services
    ├── pyproject.toml             # Project dependencies + tool configs (Ruff, Pytest, Mypy)
    ├── uv.lock                    # Deterministic dependency lockfile
    └── README.md                  # Project overview & quickstart commands
    ```

## Project files

### `.env.example`

Copy to `.env` and fill in. The real `.env` is gitignored — only this template
is committed.

```ini
# App
APP_NAME=my-python-app
DEBUG=false

# Database (use host `db` instead of `localhost` inside docker-compose)
DATABASE_URL=postgresql://app:app@localhost:5432/app

# LLM provider
LLM_API_KEY=
LLM_MODEL=gpt-4o-mini

# CORS — JSON list of browser origins allowed to call the API
CORS_ORIGINS=["http://localhost:5173"]
```

### `.gitignore`

```text
# Virtual environment
.venv/
venv/

# Python
__pycache__/
*.py[cod]
*.egg-info/

# Environment & secrets
.env

# AI agent workspace
.ai/

# Tooling caches
.pytest_cache/
.ruff_cache/
.mypy_cache/

# IDE / OS
.idea/
.vscode/
.DS_Store
```

### `pyproject.toml`

```toml
[project]
name = "my-python-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.159.1",
    "uvicorn[standard]>=0.54.0",
    "pydantic-settings>=2.16.1",
    "asyncpg>=0.32.0",
    "pgvector>=0.5.1",
]

[dependency-groups]
dev = [
    "pytest>=9.1.1",
    "pytest-asyncio>=1.4.0",
    "httpx>=0.28.1",
    "ruff>=0.17.1",
    "mypy>=2.4.0",
]

[tool.uv]
package = false

[tool.ruff]
line-length = 100

[tool.mypy]
python_version = "3.12"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

### `Dockerfile`

```Dockerfile
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY app ./app
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker-compose.yml`

```yml
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 5

  app:
    build: .
    env_file: .env
    environment:
      DATABASE_URL: postgresql://app:app@db:5432/app
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
```

## Application code

Everything under `app/` — `main.py`, `core/`, `services/` and `api/v1/` — is
covered in [FastAPI boilerplate](fastapi-boilerplate.md), along with the local
run command.

## Related

- [Env setup](env-setup.md) — choosing the toolchain the scaffold assumes
- [FastAPI boilerplate](fastapi-boilerplate.md) — the `app/` package that sits
  inside this layout
