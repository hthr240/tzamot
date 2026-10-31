# Environments

The target architecture has **three environments**. Local app development and
backend CI are Sprint 1 work, not implemented yet. Production is deferred to
Sprint 4: no VPS or domain purchase before the local MVP is ready. Hostnames in
this page describe the design, not an already purchased domain or live app.
Staging is deliberately deferred — see [Decision log](../decisions.md#adr-003-no-staging-environment-for-the-mvp).

```mermaid
flowchart LR
    Dev["💻 <b>Local</b><br/>laptop<br/>Docker Postgres + uvicorn"]
    CI["🤖 <b>CI</b><br/>GitHub Actions<br/>throwaway VM per run"]
    Prod["🌍 <b>Production</b><br/>Hetzner VPS + Cloudflare Pages<br/>real clients"]

    Dev -- "push branch / open PR" --> CI
    CI -- "merge to main<br/>→ build image<br/>→ ⏸ approval click" --> Prod
```

## Side by side

| | Local | CI | Production |
|---|---|---|---|
| **Purpose** | Write and debug code | Automatic quality gate on every PR | Serve real clients and the owner |
| **Who uses it** | Each developer | Nobody — automatic | Clients, admin |
| **Lives** | As long as you want | Minutes, then destroyed | 24/7 |
| **API** | `uvicorn --reload` in a venv on `:8000` | `pytest` in-process (no server) + `docker build` check | `api` container behind Caddy on `api.tzamot.co.il` |
| **Database** | Docker `postgres:16` on `localhost:5432`, named volume | GitHub *service container* `postgres:16`, fresh every run | Docker `postgres:16`, `pg_data` volume, internal network only |
| **Data** | Seeded fake data (`seed_test_db.py`) | Seeded fake data (same script) | Real data |
| **Frontend** | Live Server / `python -m http.server` on `:5500` | Not tested in MVP | Cloudflare Pages, `tzamot.co.il` |
| **Config** | `backend/.env` (git-ignored) | Workflow `env:` block | `/opt/tzamot/.env` on the VPS (never in git, never in the image) |
| **`ENV`** | `local` | `ci` | `production` |
| **`LOG_LEVEL`** | `DEBUG` | `INFO` | `INFO` |
| **Swagger `/docs`** | On | — | **Off** |
| **CORS origins** | `http://127.0.0.1:5500`, `http://localhost:5500` | — | `https://tzamot.co.il` |
| **Deploy** | — | — | GitHub Actions after approval — see [CI/CD](cicd.md) |

## Configuration per environment

All configuration is read from **environment variables** (12-factor). The same image runs everywhere; only the variables differ.

| Variable | Local | CI | Production |
|---|---|---|---|
| `ENV` | `local` | `ci` | `production` |
| `DATABASE_URL` | `postgresql+psycopg://tzamot:tzamot@localhost:5432/tzamot` | `postgresql+psycopg://tzamot:tzamot@localhost:5432/tzamot_test` | `postgresql+psycopg://tzamot:<secret>@db:5432/tzamot` |
| `LOG_LEVEL` | `DEBUG` | `INFO` | `INFO` |
| `CORS_ORIGINS` | `http://127.0.0.1:5500,http://localhost:5500` | — | `https://tzamot.co.il` |
| `TZ` | `Asia/Jerusalem` | `Asia/Jerusalem` | `Asia/Jerusalem` |
| `ADMIN_TOKEN` | `dev-token` | `ci-token` | `<secret>` |
| `POSTGRES_PASSWORD` *(db container)* | `tzamot` | `tzamot` | `<secret>` |

`backend/.env.example` is the checked-in template listing every key with local defaults. Copy it to `.env`; never commit `.env`.

### Backend settings

`app.core.config.Settings` validates these values when instantiated. Process
environment variables take precedence over `backend/.env`; missing values use
the documented local defaults. `CORS_ORIGINS` is a comma-separated value and is
exposed to application code as a trimmed `list[str]`.

```python
from app.core.config import Settings

settings = Settings()
```

## Frontend config

The static frontend cannot read environment variables. `frontend/js/config.js` picks the API base URL by hostname:

```js
const API_BASE = location.hostname === "tzamot.co.il"
  ? "https://api.tzamot.co.il"
  : "http://localhost:8000";
```

Cloudflare Pages **preview deployments** (`*.tzamot.pages.dev`) therefore talk to `localhost` — i.e. they are useful for *visual* review only, not end-to-end testing. Acceptable for the MVP; revisit when staging exists.

## Where secrets live

```mermaid
flowchart TB
    subgraph Laptop
        envfile["backend/.env<br/>(git-ignored)"]
    end
    subgraph GitHub
        gh_env["Environment: production<br/>VPS_HOST · VPS_USER · VPS_SSH_KEY"]
        ghcr["GHCR<br/>(image, no secrets inside)"]
    end
    subgraph VPS["Hetzner VPS"]
        vps_env["/opt/tzamot/.env<br/>DATABASE_URL · POSTGRES_PASSWORD · ADMIN_TOKEN · …"]
    end
    gh_env -- "SSH" --> VPS
    ghcr -- "docker compose pull" --> VPS
```

| Secret | Stored in | Used by |
|---|---|---|
| Production DB password, `ADMIN_TOKEN` | `/opt/tzamot/.env` on the VPS, created once by hand | `docker compose` on the VPS |
| SSH private key, VPS host/user | GitHub → Settings → Environments → **production** → secrets | `deploy.yml` |
| `GITHUB_TOKEN` (push to GHCR) | Automatic, provided by GitHub Actions | `deploy.yml` |

Rules: no secrets in code, in the Docker image, or in `docker-compose.prod.yml`. Rotate `ADMIN_TOKEN` and the SSH key if a laptop is lost.

## Adding staging later

When the team wants a dress-rehearsal environment, the design extends without rework:

1. Add a second compose project on the same VPS (or a second CX22) with `staging-api.tzamot.co.il` in the Caddyfile.
2. Add a GitHub Environment **staging** *without* required reviewers; `deploy.yml` deploys there automatically on `main`, then waits for approval to deploy **production**.
3. Add a Cloudflare Pages branch deployment (`staging` branch) and extend `config.js` with the staging hostname.

Tracked in [Roadmap → Post-MVP](../roadmap/index.md).
