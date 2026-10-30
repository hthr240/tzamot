# Infrastructure

This directory owns local and future production runtime configuration. It is
currently a directory scaffold only; no services are started or provisioned.

- Local PostgreSQL Compose configuration is the next infrastructure task (#7).
- The backend runs natively during development; see [Local setup](../docs/development/local-setup.md).
- Production Compose, Caddy, VPS and domain work are deferred to
  [Sprint 4](../docs/roadmap/sprint-4.md), after local MVP readiness.

No hosting, domain purchase, or production secrets are needed for this scaffold.
