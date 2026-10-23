# Onboarding Checklist

Welcome to the team! This page gets you from zero to your first merged pull request. Tick the boxes as you go — they're saved in your browser.

!!! info "Who does what"
    - **Team lead** owns infrastructure, CI/CD, repo settings and Sprint 1. Ask them for access.
    - **Everyone** owns code quality: every PR is reviewed by the other developer.

## Day 1 — Understand the product

- [ ] Read the [Product overview](product/index.md) (10 min)
- [ ] Read the [Business rules](product/business-rules.md) — especially *dynamic time blocking* and the *24-hour cancellation rule*
- [ ] Read [Out of scope](product/out-of-scope.md) so you don't accidentally build Phase 2 features
- [ ] Skim the [Glossary](glossary.md) for domain terms

## Day 1 — Understand the system

- [ ] Read the [Architecture overview](architecture/index.md)
- [ ] Trace a booking through the [Request flow](architecture/request-flow.md)
- [ ] Study the [Data model](architecture/data-model.md) and the [Booking algorithm](architecture/booking-algorithm.md)
- [ ] Skim the [Decision log](decisions.md) — why things are the way they are

## Day 1 — Get access

- [ ] GitHub: write access to `hthr240/tzamot`
- [ ] GitHub Projects board (see [Task management](development/task-management.md))
- [ ] Shared `.env` secrets for local development (ask the team lead; **never** commit them)

## Day 2 — Set up your machine

Follow [Local setup](development/local-setup.md) end to end:

- [ ] Docker Desktop installed and running
- [ ] `uv` installed; `uv sync` in `backend/` succeeds
- [ ] `docker compose -f infra/docker-compose.dev.yml up -d` → PostgreSQL running on `:5432`
- [ ] `uv run alembic upgrade head` succeeds
- [ ] `uv run uvicorn app.main:app --reload` serves the API on `:8000` and `/docs` opens
- [ ] Frontend served locally and talking to the API
- [ ] `uv run pytest` passes locally
- [ ] `uv run ruff check .` and `uv run black --check .` pass locally

## Day 2 — Learn the workflow

- [ ] Read [Git workflow & code review](development/workflow.md)
- [ ] Read the [CI pipeline](development/ci-pipeline.md) so you know what will block your PR
- [ ] Read [Logging](development/logging.md) and [Coding standards](development/coding-standards.md)

## Day 2–3 — Ship something

- [ ] Pick a small issue from the **To Do** column and assign yourself
- [ ] Create a branch: `git checkout -b feature/<issue-number>-short-description`
- [ ] Open a PR with `Resolves #<issue-number>` in the description
- [ ] Get CI green, get one approval, merge :tada:

## Still stuck?

Open a GitHub Discussion or ping the team lead. If a step in this checklist was confusing, **fix the docs** — that counts as a contribution.
