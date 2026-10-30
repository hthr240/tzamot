# Project Structure

!!! success "Decided — monorepo"
    See [ADR-001](../decisions.md#adr-001-monorepo). This page maps the target
    repository. Items marked :construction: are not implemented yet. Local/CI
    scaffolding belongs to [Sprint 1](../roadmap/sprint-1.md); production
    deployment files belong to [Sprint 4](../roadmap/sprint-4.md).

## Current foundation

The directory skeleton from #6 exists:

- `backend/app/` and its `core`, `models`, `schemas`, `routers`, and `services`
  packages have empty `__init__.py` files.
- `backend/tests/` and `backend/scripts/` have `.gitkeep` placeholders.
- `frontend/css/`, `frontend/js/`, and `frontend/icons/` have `.gitkeep` placeholders.
- `infra/docker-compose.dev.yml` runs local PostgreSQL 16 with a health check,
  localhost-only port, and persistent named volume.
- `infra/README.md` documents startup, connection, stop, and destructive reset.

The layout below is the **target**, not an inventory of implemented modules.
FastAPI, application database sessions, migrations, UI files, dependency
manifests, Dockerfiles, production Compose, and the app launcher are still
later tickets. The database is usable independently; the empty packages do not
provide a running application.

## Repository layout

```
tzamot/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                  🚧 lint · format · migrate · seed · test · docker build (PRs)
│   │   ├── deploy.yml              🚧 Sprint 4: image → GHCR → approval → SSH
│   │   └── docs.yml                ✅ build + publish this site
│   ├── ISSUE_TEMPLATE/            story.yml · task.yml · bug.yml
│   └── PULL_REQUEST_TEMPLATE.md
│
├── backend/                        package skeleton exists; FastAPI app planned
│   ├── app/
│   │   ├── main.py                 FastAPI app factory, middleware, router registration
│   │   ├── core/
│   │   │   ├── config.py           Settings from environment variables
│   │   │   ├── logging.py          Structured logging setup
│   │   │   └── db.py               Engine, session dependency
│   │   ├── models/                 SQLAlchemy: service.py · availability.py · appointment.py
│   │   ├── schemas/                Pydantic request/response models
│   │   ├── routers/                services · availability · slots · appointments · admin · health
│   │   └── services/               Use-cases: slots.py (algorithm) · booking.py · cancellation.py
│   ├── alembic/                    Migrations (versions/)
│   ├── alembic.ini
│   ├── scripts/
│   │   └── seed_test_db.py
│   ├── tests/
│   │   ├── conftest.py             DB session fixture, frozen clock
│   │   └── test_*.py
│   ├── Dockerfile                  python:3.13-slim + uv sync --frozen
│   ├── pyproject.toml              deps + [tool.ruff] [tool.black] [tool.pytest]
│   ├── uv.lock                     locked versions — commit it
│   └── .env.example                every config key with local defaults
│
├── frontend/                       asset directories exist; static PWA planned
│   ├── index.html                  client booking flow
│   ├── admin.html                  hidden admin UI
│   ├── css/
│   ├── js/
│   │   ├── config.js               API base URL by hostname
│   │   ├── api.js                  fetch wrapper, errors, spinner
│   │   ├── strings.js              Hebrew UI copy
│   │   ├── booking.js              client flow
│   │   └── admin.js                admin flow
│   ├── icons/
│   ├── manifest.json
│   └── sw.js                       service worker
│
├── infra/                          local Postgres Compose ready; production planned
│   ├── docker-compose.dev.yml      local: postgres only
│   ├── docker-compose.prod.yml     Sprint 4: VPS, caddy + api + db
│   ├── Caddyfile                   Sprint 4
│   └── README.md                   local database runbook; production comes later
│
├── docs/                           ✅ this site
├── mkdocs.yml                      ✅
├── .gitignore                      ✅
└── README.md                       ✅
```

## Conventions

| Rule | Detail |
|---|---|
| **One image, one `backend/`** | `backend/Dockerfile` is the only image we build. Its build context is `backend/`. |
| **`infra/` owns runtime** | Compose files, Caddyfile, and the provisioning runbook. Nothing in `infra/` is imported by Python. |
| **Frontend has no build step** | Plain files; Cloudflare Pages serves `frontend/` as-is. |
| **Commit `uv.lock`** | It is what makes local, CI, and Docker installs identical. |
| **Commit `.env.example`, never `.env`** | Enforced by `.gitignore`. |
| **Do not require a skipped workflow** | Docs uses path filters. A future required backend check must report on every PR; see [CI pipeline](ci-pipeline.md). Production deploy is deferred to Sprint 4. |

## Everyday commands (from the repo root)

| Task | Command |
|---|---|
| Start local DB | `docker compose -f infra\docker-compose.dev.yml up -d --wait --wait-timeout 60` |
| Install backend deps | `cd backend && uv sync` |
| Run API | `cd backend && uv run uvicorn app.main:app --reload` |
| Migrate | `cd backend && uv run alembic upgrade head` |
| Seed | `cd backend && uv run python scripts/seed_test_db.py` |
| Test | `cd backend && uv run pytest` |
| Lint / format | `cd backend && uv run ruff check . && uv run black --check .` |
| Serve frontend | `cd frontend && python -m http.server 5500` (or Live Server) |
| Serve docs | `mkdocs serve` |

!!! tip
    A `Makefile` / `justfile` wrapping these is a nice Sprint 1 stretch goal.

## Monorepo vs. multi-repo (for the record)

| | Monorepo (chosen) | Separate repos |
|---|---|---|
| PRs touching API + UI | One PR, one review | Two PRs, coordinate merges |
| CI | Path filters | Naturally separate |
| Cloudflare Pages | Root directory `frontend/` | Repo root |
| Issue tracking | One board | Two boards |
| Onboarding | One clone | Two clones |
