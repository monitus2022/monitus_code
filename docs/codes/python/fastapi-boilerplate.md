---
title: FastAPI boilerplate
---

# FastAPI boilerplate

A starting point for a small service: the `app/` package — settings, middleware,
services and routes.

The surrounding repo files (`pyproject.toml`, `Dockerfile`, `.env`, compose) are
covered in [Project scaffold](project-scaffold.md).

## App layout

Where routes, settings and dependencies sit relative to each other.

The app is a package: `main.py` builds the `FastAPI` instance and mounts the
versioned routers, `core/` holds infrastructure such as settings and middleware,
`api/v1/` holds the endpoints, and `services/` holds the business logic they
call. This is the same layout as the [project scaffold](project-scaffold.md),
trimmed to what a service needs to boot.

```text
app/
├── __init__.py
├── main.py                # App instance, middleware & router wiring
├── api/                   # Route handlers & endpoints
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── routes.py      # Endpoints
│       └── schemas.py     # Request / response models
├── core/                  # Infrastructure & configuration
│   ├── __init__.py
│   ├── config.py          # App settings (Pydantic Settings)
│   ├── database.py        # Connection pool (asyncpg / pgvector)
│   └── middleware.py      # CORS & other cross-cutting HTTP middleware
└── services/              # Business logic & AI/RAG orchestration
```

## Files template

### `app/core/config.py`

Settings are defined once and imported as the module-level `settings` object,
the same way the scaffold does it. `database_url` is a plain `postgresql://`
DSN, because the pool below talks to `asyncpg` directly — SQLAlchemy would
instead want the `postgresql+asyncpg://` scheme.

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "my-python-app"
    debug: bool = False
    database_url: str = "postgresql://app:app@localhost:5432/app"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""

    # Browser origins allowed to call the API. Set as a JSON list, e.g.
    # CORS_ORIGINS=["https://app.example.com"]
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()
```

### `app/core/database.py`

A single pool is opened at startup and closed at shutdown; handlers borrow a
connection through `Depends`. The pool lives on `app.state`, so there is no
module-level global to reset between tests.

```python
from collections.abc import AsyncIterator

import asyncpg
from fastapi import FastAPI, Request

from app.core.config import settings


async def connect(app: FastAPI) -> None:
    app.state.pool = await asyncpg.create_pool(settings.database_url)


async def disconnect(app: FastAPI) -> None:
    await app.state.pool.close()


async def get_conn(request: Request) -> AsyncIterator[asyncpg.Connection]:
    async with request.app.state.pool.acquire() as conn:
        yield conn
```

### `app/core/middleware.py`

Cross-cutting HTTP concerns live here. CORS is the one most services need: it
tells browsers which origins may call the API and answers the preflight
`OPTIONS` requests they send.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


def setup_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

`add_middleware` applies middleware in reverse order of addition, so the last
one added is the outermost. Call `setup_cors(app)` after any other middleware so
CORS sees requests first and preflight `OPTIONS` calls are not rejected by auth.

### `app/services/search.py`

Business logic lives in a service, not in the route handler. Keep one class per
concern and let the route translate HTTP into a method call. Services that touch
the network or database are `async def` and raise domain errors; the handler
maps those errors to HTTP status codes.

```python
class SearchError(Exception):
    """Raised when a search query is invalid."""


class SearchService:
    """Example service: keep business logic out of the route handlers."""

    def __init__(self, items: list[str]) -> None:
        self._items = items

    async def search(self, query: str) -> list[str]:
        query = query.strip().lower()
        if not query:
            raise SearchError("query must not be empty")
        return [item for item in self._items if query in item.lower()]
```

Re-export it from the package so callers import from `app.services` instead of
the deep module path:

```python
# app/services/__init__.py
from app.services.search import SearchError, SearchService

__all__ = ["SearchError", "SearchService"]
```

### `app/api/v1/schemas.py`

Request and response models live here, so handlers stay thin and the OpenAPI
docs stay typed. Request bodies are defined the same way.

```python
from pydantic import BaseModel


class SearchResult(BaseModel):
    query: str
    matches: list[str]
```

### `app/api/v1/routes.py`

Endpoints hang off an `APIRouter`, which `main.py` mounts under `/api/v1`. Give
each resource its own module under `api/v1/`; `routes.py` is the smallest
example. The handler depends on the service rather than building it inline, so
tests can swap in a fake.

```python
from fastapi import APIRouter, Depends

from app.api.v1.schemas import SearchResult
from app.core.config import settings
from app.services import SearchService

router = APIRouter(tags=["v1"])

_search = SearchService(items=["apple", "banana", "cherry"])


def get_search_service() -> SearchService:
    return _search


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


@router.get("/search", response_model=SearchResult)
async def search(
    q: str,
    service: SearchService = Depends(get_search_service),
) -> SearchResult:
    matches = await service.search(q)
    return SearchResult(query=q, matches=matches)
```

### `app/main.py`

Create the app, attach middleware, then mount the routers with a version prefix.
Startup and shutdown (the database pool, caches) go in a `lifespan` handler, and
domain errors are mapped to HTTP responses with an exception handler.

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1 import routes
from app.core.config import settings
from app.core.database import connect, disconnect
from app.core.middleware import setup_cors
from app.services import SearchError


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect(app)
    yield
    await disconnect(app)


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
setup_cors(app)
app.include_router(routes.router, prefix="/api/v1")


@app.exception_handler(SearchError)
async def search_error_handler(request: Request, exc: SearchError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})
```

## Running it

Local run and reload behaviour. Point uvicorn at the app instance —
`module:attribute`.

=== "Dev"

    ```bash
    # Reload the worker whenever a source file changes (development only)
    uvicorn app.main:app --reload
    ```

    Docs are served at `/docs` (Swagger) and `/redoc`.

=== "Container"

    ```bash
    # Inside Docker: bind all interfaces and drop reload for stability
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

## Testing

Tests live in `tests/`, next to `app/`. Because the handlers depend on
`get_search_service`, a test swaps in a fake instead of touching the real
service or the database.

```python
# tests/conftest.py
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.api.v1.routes import get_search_service
from app.main import app


class FakeSearchService:
    async def search(self, query: str) -> list[str]:
        return ["fake-result"]


@pytest.fixture
def client() -> Iterator[TestClient]:
    app.dependency_overrides[get_search_service] = lambda: FakeSearchService()
    yield TestClient(app)
    app.dependency_overrides.clear()
```

```python
# tests/test_api.py
from fastapi.testclient import TestClient


def test_search(client: TestClient) -> None:
    response = client.get("/api/v1/search", params={"q": "anything"})
    assert response.status_code == 200
    assert response.json() == {"query": "anything", "matches": ["fake-result"]}
```

`TestClient(app)` used as a plain object does not run the lifespan, so this test
needs no database. Use `with TestClient(app) as client` when a test needs
startup resources such as the pool.

## Related

- [Project scaffold](project-scaffold.md) — the surrounding project structure
