# CI Pipeline

The backend quality gate lives in `.github/workflows/ci.yml` (#24).
It runs when a pull request targeting `main` is opened, when new commits
are pushed to that pull request, and when the pull request is reopened.
The `backend` check is required to merge into `main` (#31). A pull request
with a failing or missing run cannot merge. Peer approvals stay at zero
while development is solo.

Verified on 2026-11-08: PR #52 merged with a green `backend` run; a
docs-only change on PR #53 still started `backend`; a deliberate failing
test left PR #53 blocked until the failure was reverted.

## What it does

```mermaid
flowchart LR
    A[Checkout +<br/>setup uv] --> B[uv sync --frozen]
    B --> C[Ruff lint]
    C --> D[Black --check]
    D --> E[(Postgres<br/>service container)]
    E --> F[alembic upgrade head]
    F --> G[Seed test DB]
    G --> H[pytest]
    H --> J[docker build]
    J --> I{{✅ status check}}
```

| Step | Command | Fails when |
|---|---|---|
| **Checkout & setup** | `actions/checkout`, `astral-sh/setup-uv`, `uv sync --frozen` (installs Python 3.13 + locked deps) | Lockfile out of date or dependency resolution fails |
| **Lint** | `uv run ruff check .` | Any lint violation |
| **Format** | `uv run black --check .` | Any file isn't Black-formatted |
| **Ephemeral DB** | GitHub Actions **service container** `postgres:16` with a health check | DB fails to start |
| **Migrate** | `uv run alembic upgrade head` | A migration is broken or missing |
| **Seed** | `uv run python -m scripts.seed_test_db` | Seed script fails (often = model/migration mismatch) |
| **Test** | `uv run pytest -v` | Any test fails |
| **Docker build** | `docker build -t tzamot-api:ci .` from `backend/` (not pushed) | `Dockerfile` is broken — caught before merge, so deploys never fail on build |

## Why seed the database?

!!! success "Testing against real scenarios"
    Testing against an **empty** database only verifies basic schema constraints. By seeding realistic data — 5 services, 2 weeks of admin availability, a few booked appointments — integration tests can assert the **core business logic**: e.g. that `/slots` correctly excludes times blocked by existing appointments, or that back-to-back bookings are allowed.

### Database seeding

`scripts/seed_test_db.py` is idempotent and deterministic (fixed dates relative to a frozen "today"), so tests can make exact assertions. Contents described in [Data model → Seed data](../architecture/data-model.md#seed-data-ci-local).

## Workflow

??? example ".github/workflows/ci.yml"
    ```yaml
    name: CI

    on:
      pull_request:
        branches: [main]
        types: [opened, synchronize, reopened]

    jobs:
      backend:
        runs-on: ubuntu-latest
        defaults:
          run:
            working-directory: backend

        services:
          postgres:
            image: postgres:16
            env:
              POSTGRES_USER: tzamot
              POSTGRES_PASSWORD: tzamot
              POSTGRES_DB: tzamot_test
            ports: ["5432:5432"]
            options: >-
              --health-cmd "pg_isready -U tzamot"
              --health-interval 5s
              --health-timeout 5s
              --health-retries 10

        env:
          DATABASE_URL: postgresql+psycopg://tzamot:tzamot@localhost:5432/tzamot_test
          # Pytest ignores DATABASE_URL and reads TEST_DATABASE_URL.
          TEST_DATABASE_URL: postgresql+psycopg://tzamot:tzamot@localhost:5432/tzamot_test
          ENV: ci
          TZ: Asia/Jerusalem
          ADMIN_TOKEN: ci-token

        steps:
          - uses: actions/checkout@v4

          - uses: astral-sh/setup-uv@v5
            with:
              enable-cache: true
              cache-dependency-glob: backend/uv.lock
              working-directory: backend

          - name: Install dependencies (locked)
            run: uv sync --frozen

          - name: Lint (Ruff)
            run: uv run ruff check .

          - name: Format check (Black)
            run: uv run black --check .

          - name: Run migrations
            run: uv run alembic upgrade head

          - name: Seed test database
            run: uv run python -m scripts.seed_test_db

          - name: Tests
            run: uv run pytest -v

          - name: Docker build (sanity, not pushed)
            run: docker build -t tzamot-api:ci .
    ```

    There is no path filter, so a docs-only pull request still gets a `backend`
    result. Infrastructure changes are covered for the same reason. That is
    why `backend` can be required: a pull request is not left waiting for a
    workflow that never started.

    Pytest reads `TEST_DATABASE_URL`, not `DATABASE_URL`, so both point at the
    service database. `setup-uv` uses `backend/` because `pyproject.toml` and
    `uv.lock` are not in the repository root.

## Local parity

Run the same checks before pushing (from `backend/`):

```bash
uv run ruff check . && uv run black --check . && uv run pytest
```

Consider a `pre-commit` config (Sprint 1 stretch goal) so Ruff and Black run on every commit automatically.

## Beyond CI: deployment

What happens *after* a green merge — image build, approval gate, SSH deploy — is
a planned Sprint 4 workflow (`deploy.yml`) described in
[Architecture → CI/CD](../architecture/cicd.md). It is not needed for local
development and must not require a paid server before MVP readiness.
Docs are published independently by `docs.yml`.
