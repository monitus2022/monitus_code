---
title: Pydantic
---

# Pydantic

Models that check data at the boundary — API payloads, config, `.env` — and
refuse anything that does not match the type hints. A cheatsheet for Pydantic
v2, focused on `Field` and constraints.

The [FastAPI boilerplate](fastapi-boilerplate.md) already uses the two pieces
covered last: `BaseModel` schemas and `pydantic-settings` for config.

## When to use what

| Situation | Reach for |
| --- | --- |
| A number must stay inside bounds (`>=`, `<=`) | [Constraints](#field-constraints) |
| A string must have a length or match a shape | [Constraints](#field-constraints) |
| A field must be one of a few preset values | [Preset values](#preset-values) |
| The same rule recurs across models | [Reusable constraints](#reusable-constraints) |
| A rule `Field()` cannot express | [Custom validation](#custom-validation) |
| One field depends on another (end after start) | [Cross-field validation](#cross-field-validation) |
| A model must become a dict or JSON, or the reverse | [Serialization](#serialization) |
| Unknown input keys should error, not vanish | [Model config](#model-config) |
| A plain list or dict needs checking, no model | [TypeAdapter](#typeadapter) |
| Typed access to `.env` variables | [Pydantic Settings](#pydantic-settings) |

## Install

```bash
uv add pydantic            # models & validation
uv add pydantic-settings   # .env support — a separate package since v2
```

## Models & fields

A model is a class with type hints. Pydantic validates on the way in and
coerces where it can (`"3"` → `3`).

```python
from pydantic import BaseModel, Field


class Product(BaseModel):
    name: str
    price: float = Field(default=0.0, description="in EUR")  # shows in OpenAPI
    tags: list[str] = Field(default_factory=list)  # fresh list per instance
```

- `default=` for immutable defaults; `default_factory=` when the default is
  mutable or computed per call.
- `alias=` renames the incoming key (`Field(alias="unitPrice")`).

A bad value raises `ValidationError` — with the offending field, rule and
input all named:

```text
>>> Product(name="mug", price=-1)
ValidationError: 1 validation error for Product
price
  Input should be greater than or equal to 0
  [type=greater_than_equal, input_value=-1, ctx={'ge': 0}]
```

## Field constraints

The rules live in `Field(...)`. Numbers, strings and collections each have
their own set.

### Numbers

```python
from decimal import Decimal
from pydantic import BaseModel, Field


class Order(BaseModel):
    quantity: int = Field(ge=1, le=100)       # 1 <= quantity <= 100
    discount: float = Field(gt=0, lt=1)       # 0 and 1 excluded
    batch_size: int = Field(multiple_of=8)    # 8, 16, 24, ...
    price: Decimal = Field(gt=0, max_digits=8, decimal_places=2)
```

- `ge` / `le` — inclusive bounds (`>=`, `<=`)
- `gt` / `lt` — exclusive bounds (`>`, `<`)
- `multiple_of` — exact multiples (stick to ints or binary-exact steps like `0.5`)
- `max_digits` / `decimal_places` — for `Decimal`, the money-safe type

### Strings

```python
class Account(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    zip_code: str = Field(pattern=r"^\d{5}$")   # anchor with ^...$ to pin the whole string
    bio: str = Field(max_length=500)
```

To strip whitespace on every string field at once, set
`str_strip_whitespace=True` in [model config](#model-config).

### Collections

The same `min_length` / `max_length` names count *items* on lists, sets and
dicts:

```python
class Tagged(BaseModel):
    tags: list[str] = Field(min_length=1, max_length=10)  # item count
    name: str = Field(min_length=1)                       # character count
```

### Preset values

A field that must be one of a few fixed choices:

```python
from enum import Enum
from typing import Literal


class Status(str, Enum):        # str + Enum → dumps as plain JSON strings
    active = "active"
    banned = "banned"


class Account(BaseModel):
    size: Literal["small", "medium", "large"] = "medium"  # zero boilerplate
    status: Status = Status.active                          # shared / has logic


Account(size="huge")  # ValidationError: Input should be 'small', 'medium' or 'large'
```

- `Literal` — best for a handful of options used in one place; no class needed.
- `Enum` — when the same options recur across models or carry behavior.
  `str, Enum` (or `StrEnum` on Python 3.11+) keeps serialization JSON-friendly;
  `use_enum_values=True` in config dumps the raw value instead of the member.
- A shape that is not enumerable — semantic versions, slugs — is a
  [`pattern`](#strings) instead.

### Reusable constraints

`Annotated` moves the rule into the type, so one constraint can be shared by
any number of models and fields:

```python
from typing import Annotated
from pydantic import BaseModel, Field

Port = Annotated[int, Field(ge=1, le=65535)]
Percent = Annotated[float, Field(ge=0, le=100)]


class Server(BaseModel):
    port: Port = 8000       # default goes after the = once the type is Annotated
    load: Percent = 0.0
```

This is the current recommended style; the older `conint(ge=...)` /
`constr(...)` helpers do the same thing. FastAPI also reads `Annotated`
constraints on function parameters, so `Port` works as a query-param type
too.

## Common types

| Type | Use / notes |
| --- | --- |
| `EmailStr` | email format — needs the `email-validator` package |
| `HttpUrl` / `AnyHttpUrl` | absolute http(s) URL, parsed to a URL object |
| `UUID` | accepts the string form, becomes a real `UUID` |
| `datetime` / `date` | ISO 8601 strings parsed automatically |
| `Decimal` | exact money math, pairs with `max_digits` / `decimal_places` |
| `SecretStr` | hidden in repr and logs; `.get_secret_value()` to unwrap |
| `IPvAnyAddress` | v4 or v6 |
| `Path` | parsed to `pathlib.Path` — existence checks need a validator |

## Custom validation

When `Field()` has no constraint for the rule, write it as a validator.
Raising `ValueError` inside becomes a normal field error.

```python
from pydantic import BaseModel, field_validator


class User(BaseModel):
    name: str = Field(min_length=1)

    @field_validator("name")
    @classmethod
    def title_case(cls, v: str) -> str:
        return v.strip().title()
```

- `@field_validator("a", "b")` — the same check on several fields.
- `mode="before"` runs before type coercion, so `v` is raw input (`Any`) — the
  place to normalize before Pydantic parses.

### Cross-field validation

When one field only makes sense given another, use `model_validator` on the
whole model:

```python
from datetime import date
from typing import Self
from pydantic import BaseModel, model_validator


class Booking(BaseModel):
    start: date
    end: date

    @model_validator(mode="after")
    def check_order(self) -> Self:
        if self.end < self.start:
            raise ValueError("end must not be before start")
        return self
```

`mode="after"` receives the constructed model; `mode="before"` receives the
raw input dict, for renames and reshapes that must happen first.

### Computed fields

A read-only value derived from the fields — appears in `model_dump()` and
OpenAPI, but is never an input:

```python
from pydantic import BaseModel, computed_field


class Order(BaseModel):
    unit_price: float
    quantity: int

    @computed_field
    @property
    def total(self) -> float:
        return self.unit_price * self.quantity
```

## Serialization

Four methods cover the whole round trip:

```python
Product.model_validate({"name": "mug"})          # dict → model
Product.model_validate_json('{"name": "mug"}')   # JSON string → model, one pass
Product(name="mug").model_dump()                 # model → dict
Product(name="mug").model_dump_json(indent=2)    # model → JSON string
```

Useful flags on the dump side:

- `exclude_unset=True` — only fields the caller actually set; the right shape
  for PATCH payloads.
- `by_alias=True` — emit the `alias` names (camelCase out).
- `include={"name"}` / `exclude={"price"}` — trim the payload.

`.dict()` and `.json()` are the v1 names — gone in v2.

## Model config

One `model_config` sets behavior for the whole model:

```python
from pydantic import BaseModel, ConfigDict


class Payload(BaseModel):
    model_config = ConfigDict(
        extra="forbid",           # unknown keys raise instead of being dropped
        strict=True,             # no coercion: "3" no longer becomes 3
        frozen=True,             # immutable and hashable
        str_strip_whitespace=True,
        populate_by_name=True,   # accept both alias and field name
        from_attributes=True,    # build from ORM rows / objects, not just dicts
    )
```

The default `extra="ignore"` silently drops unknown input keys — fine for
internal models, dangerous for API payloads where a typo'd field name should
fail loudly.

## TypeAdapter

Validate a bare type — a list, dict, union — without declaring a model:

```python
from typing import Annotated
from pydantic import Field, TypeAdapter

ports = TypeAdapter(list[Annotated[int, Field(ge=1, le=65535)]])

ports.validate_python([80, "443"])  # → [80, 443]
ports.validate_python([0])         # ValidationError
```

Handy at the edge of the codebase: reading a JSON list from config, a file or
a queue.

## Pydantic Settings

`BaseSettings` reads env vars (and `.env`) into typed fields — the pattern
[`app/core/config.py`](fastapi-boilerplate.md) in the FastAPI boilerplate
uses:

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",  # .env also holds keys for other tools
    )

    app_name: str = "my-python-app"
    debug: bool = False                     # DEBUG=true / 1 / yes / on
    database_url: str = "postgresql://app:app@localhost:5432/app"
    cors_origins: list[str] = []            # CORS_ORIGINS='["https://app.example.com"]'
    llm_api_key: SecretStr = SecretStr("")  # shown as ********** in logs


settings = Settings()
```

- Env var name = field name, case-insensitive; `env_prefix="APP_"` in the
  config prefixes every one (`APP_DEBUG`).
- Complex types (list, dict) arrive as JSON strings.
- Everything on this page works here too — `Field` constraints, validators,
  `Annotated` types. A bad env var fails at startup, not three layers deep.

## Related

- [FastAPI boilerplate](fastapi-boilerplate.md) — where `schemas.py` and `Settings` plug in
- [Project scaffold](project-scaffold.md) — where the deps are declared
- [PyTest](pytest.md) — asserting on `ValidationError` cases
