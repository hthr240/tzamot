# Sprint 4 — PWA, Polish & Production Launch

**Team:** both developers.
**Goal:** upgrade the website to a native-feeling mobile app, finalise edge-case features, and deploy to the live servers.

## Checklist

### PWA transformation

- [ ] `manifest.json` — app name, `lang: he`, `dir: rtl`, theme colours, home-screen icons, `display: standalone`
- [ ] Basic service worker so browsers prompt **"Add to Home Screen"**; cache the app shell only, never API responses — see [Frontend → PWA](../architecture/frontend.md#pwa-requirements-sprint-4)
- [ ] Test install on iOS Safari and Android Chrome

### Client self-cancellation

- [ ] Choose lookup mechanism: link in confirmation (token) vs. "find my appointment" by phone
- [ ] `DELETE /appointments/{id}` — **blocked if less than 24 hours** before start — see [Business rules](../product/business-rules.md#24-hour-cancellation-rule)
- [ ] Cancellation frees the slot immediately
- [ ] **Logging:** `appointment.cancelled`, `cancellation.refused`
- [ ] Tests: exactly 24 h, 23 h 59 m, 25 h; timezone edge around DST

### UI/UX polish

- [ ] Loading spinners during every API call
- [ ] User-friendly Hebrew error messages — e.g. *"This time slot was just taken, please choose another"*
- [ ] Empty states (no services, no slots on this day)
- [ ] Final RTL / mobile QA pass on real devices

### Deployment — the launch

- [ ] Connect the repository to **Cloudflare Pages** for automatic frontend deployments
- [ ] Provision the **Hetzner VPS** (CX22), harden SSH, install Docker
- [ ] `docker-compose.prod.yml` with **Caddy** (reverse proxy) + **FastAPI** + **PostgreSQL** (persistent volume) — see [Deployment](../architecture/deployment.md)
- [ ] `Caddyfile` for `api.<domain>`
- [ ] Production `.env` on the VPS; `CORS_ORIGINS` set to the production frontend
- [ ] Run migrations on deploy
- [ ] Point DNS: root → Cloudflare Pages, `api` → VPS; verify SSL on both
- [ ] Smoke-test a full booking + cancellation from a phone in production
- [ ] Hand the owner her admin URL and walk her through it

### Operations minimum (added)

- [ ] Docker log rotation in `docker-compose.prod.yml`
- [ ] Nightly `pg_dump` backup — see [Deployment → Operations](../architecture/deployment.md#operations)
- [ ] Uptime monitor on `/health`

## Definition of done — MVP launched

- [ ] The owner has configured real services and hours in production
- [ ] At least one real client has booked through the app
- [ ] All [success criteria](../product/index.md#success-criteria-for-the-mvp) are met

## After launch

Collect feedback for two weeks, then plan Phase 2 from [Out of scope](../product/out-of-scope.md): reminders first (biggest no-show impact), then payments.
