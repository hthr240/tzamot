# Tzamot — צמות

Mobile-first Hebrew PWA for booking braids & hair-styling appointments. Clients book with just a name and phone number; the owner manages services, working hours, and the calendar from her phone.

**Stack:** FastAPI · SQLAlchemy · Alembic · PostgreSQL · Vanilla JS PWA · Docker · Caddy · Cloudflare Pages · Hetzner.

## Documentation

Full developer documentation lives in [`docs/`](docs/) and is published as an MkDocs Material site.

- **New developer?** Start at [docs/onboarding.md](docs/onboarding.md).
- Product requirements → [docs/product/](docs/product/index.md)
- Architecture & infra → [docs/architecture/](docs/architecture/index.md)
- Development workflow, CI, logging → [docs/development/](docs/development/index.md)
- Sprint roadmap → [docs/roadmap/](docs/roadmap/index.md)

### Run the docs locally

On Windows, double-click [`open-docs.cmd`](open-docs.cmd). It starts the
documentation server in a dedicated Google Chrome window and shuts the server
down when that window closes. From VS Code, you can also run **Tasks: Run
Task** and select **Open documentation in Chrome**.

Alternatively, start the server manually:

```bash
pip install mkdocs-material
mkdocs serve        # http://127.0.0.1:8000
```

## Status

Sprint 1 (Foundation & DevOps) — in progress. See the [roadmap](docs/roadmap/index.md).
