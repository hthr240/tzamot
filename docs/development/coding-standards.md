# Coding Standards

Enforced automatically where possible (CI fails otherwise); the rest is convention.

## Python (backend)

| Concern | Tool / rule | Enforced by |
|---|---|---|
| Formatting | **Black**, default settings (line length 88) | CI (`black --check .`) |
| Linting | **Ruff** — PEP 8 + import sorting (`I`) + bugbear (`B`) + pyupgrade (`UP`) | CI (`ruff check .`) |
| Python version | **3.13**, declared in `pyproject.toml` (`requires-python`), used by `uv`, CI, and the `python:3.13-slim` image | uv, CI, Docker |
| Dependencies | `uv add <pkg>` / `uv add --dev <pkg>`; commit `pyproject.toml` **and** `uv.lock` | CI (`uv sync --frozen`) |
| Type hints | Required on all public functions; FastAPI relies on them | Review |
| Imports | Absolute imports within the package | Ruff `I` |
| Naming | `snake_case` functions/vars, `PascalCase` classes, `UPPER_CASE` constants | Ruff `N` (optional) |
| Secrets | Never in code. Environment variables only. | Review + `.gitignore` |

??? example "pyproject.toml (reference)"
    ```toml
    [project]
    name = "tzamot-api"
    version = "0.1.0"
    requires-python = ">=3.13"
    dependencies = [
      "fastapi",
      "uvicorn[standard]",
      "sqlalchemy",
      "alembic",
      "psycopg[binary]",
      "pydantic-settings",
    ]

    [dependency-groups]
    dev = ["pytest", "httpx", "freezegun", "ruff", "black"]

    [tool.black]
    line-length = 88
    target-version = ["py313"]

    [tool.ruff]
    line-length = 88
    target-version = "py313"

    [tool.ruff.lint]
    select = ["E", "F", "I", "B", "UP"]

    [tool.pytest.ini_options]
    testpaths = ["tests"]
    ```

## Tests

- **pytest**, integration-style against the seeded PostgreSQL (same as CI).
- One test module per router/use-case: `tests/test_slots.py`, `tests/test_booking.py`, …
- Every **business rule** in [Business rules](../product/business-rules.md) has at least one test. The [booking algorithm edge-case list](../architecture/booking-algorithm.md#edge-cases-the-tests-must-cover) is the minimum for Sprint 3.
- Freeze time in tests (e.g. `freezegun`) so "24 hours before" and "today" are deterministic.

## API design

- Resource-oriented paths (`/services`, `/appointments`), admin routes under `/admin/`.
- Pydantic schemas for every request and response; never return ORM objects directly.
- Status codes: `201` create, `204` delete/cancel, `400` invalid input, `404` not found, `409` conflict (slot taken), `422` validation (FastAPI default).
- Error bodies have a stable shape: `{"detail": "...", "code": "slot_taken"}` so the frontend can map `code` → Hebrew message.

## Frontend (vanilla JS)

- `<html lang="he" dir="rtl">`; mobile-first CSS.
- ES modules, `const`/`let`, `async/await`. No jQuery, no framework.
- All API calls go through one `api.js` module that handles base URL, JSON, errors, and the loading indicator.
- User-facing strings live in one place (`strings.js`) to keep Hebrew copy consistent.
- Formatter: **Prettier** with defaults (optional CI step later).

## Database

- Every model change ships with an Alembic migration (`alembic revision --autogenerate -m "..."`, then **review the generated SQL**).
- `timestamptz` in UTC; business timezone `Asia/Jerusalem` at the boundary.
- Soft deletes only (`is_active`, `status`).

## Docs

- Behaviour change → update the relevant page under `docs/` in the same PR.
- Diagrams are Mermaid in Markdown — no binary images to keep in sync.
