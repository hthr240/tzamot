# Decision Log

Architecture Decision Records (ADRs). Each one captures **what** we decided, **why**, and **what we gave up**, so future developers don't re-litigate settled questions — and know when a decision *should* be revisited.

Format: one short section per decision. Add new ones at the bottom; never edit a decided ADR — supersede it.

---

## ADR-001 · Monorepo

**Date:** 2026-10-23 · **Status:** ✅ Decided

**Context.** Two developers, one product with a backend and a thin static frontend that change together.

**Decision.** One repository, `hthr240/tzamot`, with `backend/`, `frontend/`, `infra/`, `docs/`. See [Project structure](development/project-structure.md).

**Why.** A feature that touches API + UI is one PR, one review. One Kanban board. One clone for onboarding. CI uses path filters so frontend-only changes don't run Python tests.

**Trade-off.** Cloudflare Pages must be pointed at the `frontend/` subdirectory; workflows need `paths:` filters.

**Revisit when:** a third team or a native mobile app appears.

---

## ADR-002 · Python 3.13

**Date:** 2026-10-23 · **Status:** ✅ Decided

**Decision.** Python **3.13** everywhere — developer laptops, CI (`setup-python`), and the Docker base image (`python:3.13-slim`).

**Why.** Already installed on the team lead's machine; FastAPI, SQLAlchemy, Alembic, psycopg all support it. One version avoids "works on 3.12 but not 3.13" surprises.

**Trade-off.** None significant.

---

## ADR-003 · No staging environment for the MVP

**Date:** 2026-10-23 · **Status:** ✅ Decided

**Context.** Staging costs either a second VPS or a second compose stack plus DNS, secrets, and data to maintain — for a 2-person team pre-launch.

**Decision.** Three environments only: **local → CI → production**. A **manual approval gate** before production ([ADR-006](#adr-006-manual-approval-before-production)) is the safety net instead. See [Environments](architecture/environments.md).

**Why.** Faster to launch; less to operate. Cloudflare Pages previews still give visual review of frontend PRs.

**Trade-off.** No full end-to-end rehearsal with production-like data before going live. Mitigated by seeded integration tests in CI and the approval click.

**Revisit when:** real clients depend on the app daily and a bad deploy would cost bookings — then add staging per the plan in [Environments → Adding staging later](architecture/environments.md#adding-staging-later).

---

## ADR-004 · `uv` + `pyproject.toml` for dependencies

**Date:** 2026-10-23 · **Status:** ✅ Decided

**Decision.** Dependencies declared in `backend/pyproject.toml`, locked in `backend/uv.lock`, installed with **`uv sync`**. Ruff, Black, and pytest configuration live in the same `pyproject.toml`.

**Why.** One file instead of `requirements.txt` + `requirements-dev.txt` + `setup.cfg`. The lockfile guarantees laptops, CI, and the Docker image install *identical* versions. `uv` is 10–100× faster than pip, which shortens every CI run and Docker build.

**Trade-off.** One more tool to install (`pip install uv` or the standalone installer). Supersedes the `requirements.txt` approach in the original DevOps report.

---

## ADR-005 · Deploy via GitHub Actions → GHCR → SSH

**Date:** 2026-10-23 · **Status:** ✅ Decided

**Context.** Options were (a) GitHub Actions builds and pushes an image then SSHes into the VPS to restart; (b) Watchtower on the VPS polling for new images; (c) manual SSH.

**Decision.** **(a)**. `deploy.yml` builds `ghcr.io/hthr240/tzamot-api:<sha>`, then over SSH runs `pull → alembic upgrade head → up -d → health check`. See [CI/CD](architecture/cicd.md).

**Why.** Every deploy is visible and logged in the Actions tab; migrations run in a controlled order *before* the new code starts; rollback is re-running a previous workflow. Watchtower deploys silently and cannot sequence migrations.

**Trade-off.** Requires an SSH key in GitHub secrets and a small amount of workflow YAML.

---

## ADR-006 · Manual approval before production

**Date:** 2026-10-23 · **Status:** ✅ Decided

**Decision.** The `deploy` job targets a GitHub **Environment** named `production` with a **required reviewer**. Merging to `main` builds the image automatically; nothing reaches the VPS until a human clicks **Approve**.

**Why.** With no staging ([ADR-003](#adr-003-no-staging-environment-for-the-mvp)), this is the one moment to say "not now" — e.g. avoid deploying while the owner is mid-workday. Free, built into GitHub, and when staging is added later it slots in before this gate without redesign.

**Trade-off.** One extra click per deploy. Alternatives considered: deploy on every merge (fast but risky), deploy on git tag (explicit versions but more ceremony than a 2-person team needs).

---

## ADR-007 · Hetzner VPS + Docker Compose + Caddy; Cloudflare Pages for the frontend

**Date:** 2026-10 (original infra report) · **Status:** ✅ Decided

**Decision.** Backend as three containers (`caddy`, `api`, `db`) on a Hetzner CX22; static frontend on Cloudflare Pages; DNS on Cloudflare.

**Why.** Always-on (no cold starts), no free-tier row/API limits, fixed ≈ €4.50/month, automatic HTTPS, root access. See [Architecture overview → Why these choices](architecture/index.md#why-these-choices).

---

## Pending decisions

| Topic | Options | Owner | Target |
|---|---|---|---|
| Domain name | `*.co.il` registrar | Team lead | Before Sprint 4 |
| Weekly working-hours model | Materialise into `availability` rows vs compute at query time — see [Data model](architecture/data-model.md#availability) | Both | Sprint 1–2 |
| Admin authentication | Static `ADMIN_TOKEN` header vs something stronger | Both | Sprint 2 |
| Slot granularity | 15 / 30 min | Both + owner | Sprint 3 |
| Client cancellation lookup | Token link vs phone lookup | Both | Sprint 4 |
| Logging library | `loguru` vs stdlib | Team lead | Sprint 1 |
