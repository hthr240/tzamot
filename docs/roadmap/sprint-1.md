# Sprint 1 — Foundation & DevOps

**Owner:** team lead, solo.
**Goal:** a robust, production-ready development environment and CI/CD pipeline so that when the second developer joins, they can pull the repository and start writing business logic immediately.

## Checklist

### Repository & project management

- [x] Create the GitHub repository (`hthr240/tzamot`)
- [x] Write developer documentation (this site)
- [x] Decide repository layout — monorepo, [ADR-001](../decisions.md#adr-001-monorepo)
- [ ] Set up the GitHub Projects Kanban board — To Do · In Progress · Done — see [Task management](../development/task-management.md)
- [ ] Configure branch protection for `main`: require 1 approval, require passing status checks — see [Workflow](../development/workflow.md#branch-protection-on-main)
- [ ] Add `.github/PULL_REQUEST_TEMPLATE.md`
- [ ] Create folder skeleton: `backend/`, `frontend/`, `infra/` — see [Project structure](../development/project-structure.md)

### Local environment

- [ ] Write `infra/docker-compose.dev.yml` running a local PostgreSQL — see [Local setup](../development/local-setup.md)
- [ ] Initialise the FastAPI project with `uv init` → `pyproject.toml` + `uv.lock` (Python 3.13)
- [ ] `backend/.env.example` with all config keys — see [Environments → Configuration](../architecture/environments.md#configuration-per-environment)
- [ ] `/health` endpoint

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

### CI/CD pipelines

- [ ] `.github/workflows/ci.yml`: `uv sync` → Ruff → Black → PostgreSQL service container → `alembic upgrade head` → seed → `pytest` (dummy test) → `docker build` — see [CI pipeline](../development/ci-pipeline.md)
- [ ] Mark the `backend` CI job as a required status check on `main`
- [ ] `backend/Dockerfile` (`python:3.13-slim` + uv) — see [Backend → Dockerfile](../architecture/backend.md#dockerfile)
- [ ] `.github/workflows/deploy.yml`: build → push to GHCR → `production` environment approval → SSH deploy — see [CI/CD](../architecture/cicd.md)
- [ ] GitHub Environment `production` with required reviewer and secrets placeholders
- [ ] `infra/docker-compose.prod.yml` + `infra/Caddyfile` — see [Deployment](../architecture/deployment.md)
- [x] `.github/workflows/docs.yml` publishes this site

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

## Open questions

| Question | Options | Decision |
|---|---|---|
| Weekly working-hours template model | Materialise into `availability` vs compute at query time | pending — see [Data model](../architecture/data-model.md#availability) |
| Logging library | `loguru` vs stdlib `logging` | pending |
| ~~Dependency management~~ | | **uv + pyproject.toml** — [ADR-004](../decisions.md#adr-004-uv-pyprojecttoml-for-dependencies) |
| ~~Python version~~ | | **3.13** — [ADR-002](../decisions.md#adr-002-python-313) |
