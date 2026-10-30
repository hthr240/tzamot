# Infrastructure

This directory owns local and future production runtime configuration.
Only the local PostgreSQL service is implemented. The API, UI, migrations,
and app launcher remain later tickets.

## Local database

With Docker Desktop running, execute from the repository root:

```powershell
docker compose -f infra\docker-compose.dev.yml up -d --wait --wait-timeout 60
docker compose -f infra\docker-compose.dev.yml ps
```

The first start pulls `postgres:16` if it is not already available. Startup
waits for the database health check; an unhealthy or unavailable service fails
the command rather than being reported as ready.

| Setting | Local value |
|---|---|
| Host / port | `127.0.0.1:5432`, not exposed to the LAN |
| Database / username / password | `tzamot` / `tzamot` / `tzamot` |
| Compose project | `tzamot-dev`, unless explicitly overridden |
| Default named volume | `tzamot-dev_pg_dev_data` |

These are public local-development defaults, never production credentials.

Connect using the PostgreSQL client inside the container:

```powershell
docker compose -f infra\docker-compose.dev.yml exec db psql -U tzamot -d tzamot
```

Exit the SQL prompt with `\q`.

## Stop versus reset

```powershell
docker compose -f infra\docker-compose.dev.yml stop db
docker compose -f infra\docker-compose.dev.yml down
```

Both preserve database data in the named volume. Starting again reuses it,
even after the container was removed by `down`.

**Destructive reset:** only run this when you intend to delete all data in the
local `tzamot-dev` project. The explicit project name prevents an environment
override from targeting a different Compose project.

```powershell
docker compose -p tzamot-dev -f infra\docker-compose.dev.yml down --volumes
docker compose -p tzamot-dev -f infra\docker-compose.dev.yml up -d --wait --wait-timeout 60
```

Do not delete another project's volumes or stop an unrelated service if port
5432 is occupied. Inspect the conflict and agree on a change first.

See [Local setup](../docs/development/local-setup.md) for the full target
workflow. Production Compose, Caddy, VPS and domain work are deferred to
[Sprint 4](../docs/roadmap/sprint-4.md), after local MVP readiness.
