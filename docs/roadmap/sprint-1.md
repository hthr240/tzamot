# Sprint 1 — Foundation & Local Dev

**Owner:** team lead, solo.
**Goal:** a developer can clone the repository and, in under 30 minutes, run the
backend, database, and frontend locally, run tests, and open a PR checked by CI.
**Budget:** no paid infrastructure; no fixed due date.

Track work in the [Sprint 1 milestone](https://github.com/hthr240/tzamot/milestone/1)
and [Project](https://github.com/users/hthr240/projects/3). The six parent stories
cover management (#1), local backend/database (#5), logging (#12), schema/seed
data (#16), CI (#22), and the frontend shell (#27).

## Checklist

### Repository & project management

- [x] Create the GitHub repository (`hthr240/tzamot`)
- [x] Write developer documentation (this site)
- [x] Decide repository layout — monorepo, [ADR-001](../decisions.md#adr-001-monorepo)
- [x] Set up milestones, labels, parent/task links, estimates, dependencies, and the five-column board — #2
- [x] Configure solo-friendly branch protection: require PRs, zero peer approvals, block force-push/deletion — #25; see [Workflow](../development/workflow.md#branch-protection-on-main)
- [x] Merge story/task/bug forms and `.github/PULL_REQUEST_TEMPLATE.md` — #3
- [x] Align process documentation and the zero-spend scope — #4
- [x] Record the dependency-respecting task sequence in the Project's Work queue and Execution order field
- [x] Create folder skeleton: `backend/`, `frontend/`, `infra/` — #6; see [Project structure](../development/project-structure.md)

### Local environment

- [x] Write `infra/docker-compose.dev.yml` running local PostgreSQL 16, with health checks and persistent data — #7; see [Local setup](../development/local-setup.md)
- [x] Initialise the FastAPI project with `uv init` → `pyproject.toml` + `uv.lock` (Python 3.13) — #8
- [x] `backend/.env.example` with all config keys and typed settings loading — #9; see [Environments → Configuration](../architecture/environments.md#configuration-per-environment)
- [ ] `/health` endpoint
- [ ] Frontend shell served locally on port 5500, calling the local API without CORS errors
- [ ] One-command launcher for the DB, migrations, API, and frontend; documented stop procedure — #11

### Structured logging

- [ ] Choose `loguru` vs stdlib `logging`
- [ ] Request middleware: request id, method, path, status, duration
- [ ] INFO/DEBUG process logs for API requests, DB queries, background work
- [ ] ERROR/CRITICAL logs with full stack traces for unhandled exceptions and API failures
- [ ] Output to stdout/stderr, readable in Docker — see [Logging](../development/logging.md)

### Database & migrations

- [ ] Initial SQLAlchemy models: `Service`, `Availability`, `Appointment` — see [Data model](../architecture/data-model.md)
- [ ] Initialise Alembic and create the first baseline migration
- [ ] `scripts/seed_test_db.py` with realistic data

### CI pipelines

- [ ] `.github/workflows/ci.yml`: `uv sync` → Ruff → Black → PostgreSQL service container → `alembic upgrade head` → seed → `pytest` (dummy test) → `docker build` — see [CI pipeline](../development/ci-pipeline.md)
- [ ] Require the `backend` status check only after it reports on every PR — #31, blocked by #24 and #25
- [ ] `backend/Dockerfile` (`python:3.13-slim` + uv) — see [Backend → Dockerfile](../architecture/backend.md#dockerfile)
- [x] `.github/workflows/docs.yml` publishes this site

### Deferred to Sprint 4

Production deployment, the `production` GitHub Environment, production Compose,
Caddy, VPS provisioning, and domain/DNS work belong to
[Sprint 4](sprint-4.md#deployment-the-launch). They are not prerequisites for
writing or testing the app locally. Do not buy hosting or a domain before MVP readiness.

### Infra design

- [x] Define environments: local → CI → production, no staging — [Environments](../architecture/environments.md), [ADR-003](../decisions.md#adr-003-no-staging-environment-for-the-mvp)
- [x] Define CI/CD: GitHub Actions → GHCR → approval → SSH — [CI/CD](../architecture/cicd.md), [ADR-005](../decisions.md#adr-005-deploy-via-github-actions-ghcr-ssh), [ADR-006](../decisions.md#adr-006-manual-approval-before-production)
- [x] Python 3.13 + uv — [ADR-002](../decisions.md#adr-002-python-313), [ADR-004](../decisions.md#adr-004-uv-pyprojecttoml-for-dependencies)
- [x] Secrets handling per environment — [Environments → Where secrets live](../architecture/environments.md#where-secrets-live)

## Definition of done

A new developer can:

1. Clone the repo
2. Follow [Local setup](../development/local-setup.md) in under 30 minutes
3. Run `pytest` green locally
4. Open a PR and see CI run
5. Load the frontend and verify that it calls the local API
6. Stop and restart local services without losing database data

## Open questions

| Question | Options | Decision |
|---|---|---|
| Weekly working-hours template model | Materialise into `availability` vs compute at query time | pending — see [Data model](../architecture/data-model.md#availability) |
| Logging library | `loguru` vs stdlib `logging` | pending |
| ~~Dependency management~~ | | **uv + pyproject.toml** — [ADR-004](../decisions.md#adr-004-uv-pyprojecttoml-for-dependencies) |
| ~~Python version~~ | | **3.13** — [ADR-002](../decisions.md#adr-002-python-313) |
