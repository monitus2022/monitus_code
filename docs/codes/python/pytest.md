---
title: PyTest
---

# PyTest

A template for testing the most common kinds of Python logic, wired to the
[project scaffold](project-scaffold.md) and the
[FastAPI service](fastapi-boilerplate.md).

## When to use what

Choose by the situation, not by habit:

| Situation | Reach for |
| --- | --- |
| Several tests need the same state set up | [Fixtures](#fixtures) |
| That setup is expensive and safe to reuse | [Fixture scopes](#fixtures) |
| One behaviour must hold across many inputs | [Parametrize](#parametrize) |
| A feature flag must be checked on *and* off | [Parametrize](#parametrize) |
| The code under test is `async def` | [Async tests](#async-tests) |
| An env var, the clock or a network call must be faked | [Mocking](#mocking) |
| An endpoint must be tested without the real DB | [Testing FastAPI](#testing-fastapi) |
| A test is slow or opt-in | [Running](#running) |

Unit tests of pure logic need almost none of this — a plain `def` and `assert`.
The sections below matter as the code gains shared setup, IO and HTTP surface.


## Install & config

Skip this if the [project scaffold](project-scaffold.md) already added the dev
dependencies — otherwise add both blocks to `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=9.1.1",
    "pytest-asyncio>=1.4.0",
    "httpx>=0.28.1",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

`asyncio_mode = "auto"` lets `async def` tests run without an
`@pytest.mark.asyncio` decorator on every one of them.

## Layout

Tests live in `tests/`, next to `app/`. Files must be named `test_*.py` (or
`*_test.py`) and functions `test_*` for discovery.

```text
tests/
├── conftest.py            # shared fixtures
├── test_api.py            # endpoint tests
└── test_search_flags.py   # parameterised / dual-state tests
```

## A plain test first

Start here. A sync service with no IO is tested by constructing it, calling the
method and comparing the result — no fixtures, no mocking, no async. Given:

```python
# app/services/search.py
class SearchService:
    def __init__(self, items: list[str]) -> None:
        self._items = items

    def search(self, query: str) -> list[str]:
        query = query.strip().lower()
        return [item for item in self._items if query in item.lower()]
```

the test is just a function prefixed `test_`:

```python
# tests/test_search.py
from app.services.search import SearchService


def test_search_matches_substring() -> None:
    service = SearchService(items=["apple", "banana", "cherry"])
    assert service.search("app") == ["apple"]


def test_search_is_case_insensitive() -> None:
    service = SearchService(items=["Apple", "Banana"])
    assert service.search("BAN") == ["Banana"]
```

Each test builds its own small input, so the cases stay independent. Reach for
the sections below only when the setup is shared, the method is `async def`, or
something outside the test must be faked.

## Fixtures

**Use it when** several tests need the same starting state — a test client, a
seeded database row, sample data — and you would otherwise copy that setup into
each test. A fixture gives it one definition and a clean teardown.

A fixture provides setup and teardown. A `conftest.py` makes it available to
every test in that directory without an import.

```python
import pytest


@pytest.fixture
def items() -> list[str]:
    return ["apple", "banana", "cherry"]


def test_len(items: list[str]) -> None:
    assert len(items) == 3
```

**Widen the scope when** the setup is expensive (a container, a connection
pool) and tests do not mutate it; keep the default `function` scope when each
test needs a clean copy.

Scopes are `function` (default), `class`, `module`, `package` and `session`. Use
a `yield` fixture when there is teardown:

```python
@pytest.fixture
def resource():
    handle = open_resource()
    yield handle
    handle.close()
```

## Parametrize

**Use it when** one behaviour must hold across many inputs — valid values,
boundaries, empty and malformed input — or when a feature flag must be verified
in both the on and off state, as `tests/test_search_flags.py` does in the
[project scaffold](project-scaffold.md).

One test body, many cases. `ids` only names the cases in the output.

```python
@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("app", ["apple"]),
        ("", []),
        ("ZZZ", []),
    ],
    ids=["match", "empty", "no-match"],
)
def test_search(query: str, expected: list[str]) -> None:
    ...
```

The flag case is the same test run twice, once per state:

```python
@pytest.mark.parametrize("enabled", [True, False], ids=["on", "off"])
def test_search_flag(
    enabled: bool,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "search_enabled", enabled)
    ...
```

## Async tests

**Use it when** the function under test is `async def` — service methods,
database calls, outbound HTTP. A plain `def` test cannot `await`, so the
coroutine would never actually run.

With `asyncio_mode = "auto"`, just write `async def`:

```python
async def test_search() -> None:
    service = SearchService(items=["apple", "banana"])
    assert await service.search("app") == ["apple"]
```

## Mocking

**Use it when** a test must not touch the outside world — environment
variables, the clock, the filesystem, a paid or flaky API — or when the real
dependency is simply absent in CI.

`monkeypatch` swaps values for the duration of one test:

```python
def test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_NAME", "test")
    assert settings.app_name == "test"
```

Use `unittest.mock` when you need to assert *how* something was called:

```python
from unittest.mock import AsyncMock

async def test_calls_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = AsyncMock(return_value=["hit"])
    monkeypatch.setattr(service, "_provider", fake)

    await service.search("x")

    fake.assert_awaited_once_with("x")
```

## Testing FastAPI

**Use it when** you want to exercise the HTTP layer — routing, status codes,
JSON shape — without starting a server or running the lifespan. Override a
dependency so the test never touches the real service or database. This mirrors
[FastAPI boilerplate](fastapi-boilerplate.md).

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
startup resources such as the connection pool.

## Running

**Use it when** you are iterating: narrow the run to the failing case instead
of the full suite, or select the slow tests you skipped in the default run.

=== "All"

    ```bash
    pytest
    ```

=== "One test"

    ```bash
    # file::function
    pytest tests/test_api.py::test_search

    # match by keyword, excluding others
    pytest -k "search and not slow"
    ```

=== "By marker"

    ```bash
    pytest -m "not slow" -q
    ```

Useful flags: `-x` stop on first failure, `-vv` verbose, `-s` show prints,
`-q` quiet, `--lf` rerun only last failed.

Custom markers must be registered or `-m` will warn. Declare them next to the
config above:

```toml
[tool.pytest.ini_options]
markers = ["slow: long-running tests excluded by default"]
```

## Coverage

**Use it when** you want to know which lines still never run — before adding
tests, or as a gate in CI. `pytest-cov` reports what the suite executed; it is
the pytest front end for the `coverage.py` engine, so the config uses the
standard `[tool.coverage.*]` keys.

=== "Install & run"

    ```bash
    uv add --dev pytest-cov

    pytest --cov=app --cov-report=term-missing
    ```

=== "Config"

    ```toml
    [tool.coverage.run]
    source = ["app"]
    branch = true          # count branch coverage, not just executed lines

    [tool.coverage.report]
    show_missing = true
    fail_under = 80        # nonzero exit when coverage drops below 80%
    ```

`--cov-report=html` writes `htmlcov/` to browse locally; `--cov-report=xml`
produces `coverage.xml` for CI, where `--cov-fail-under=80` turns the report
into a gate.

Coverage measures execution, not correctness — a test that calls a function and
asserts nothing still counts as covered. It answers "what never ran?", not "is
the logic right?".

## Related

- [Project scaffold](project-scaffold.md) — where `tests/` and the dev deps live
- [FastAPI boilerplate](fastapi-boilerplate.md) — the app these tests exercise
- [Env setup](env-setup.md) — installing dev dependencies
