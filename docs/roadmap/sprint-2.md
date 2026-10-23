# Sprint 2 — Admin Core

**Team:** both developers — the second developer joins here.
**Goal:** build the backend entities and the hidden admin interface so the business owner can start configuring her services and working hours.

## Checklist

### Backend — Services API

- [ ] CRUD endpoints for `services`: create, read, update, deactivate (name, duration in minutes, price) — see [Backend → API surface](../architecture/backend.md#api-surface-mvp)
- [ ] `GET /services` returns only **active** services
- [ ] Pydantic schemas with validation (`duration_minutes > 0`, `price >= 0`)
- [ ] **Logging:** `service.created`, `service.updated`, `service.disabled`
- [ ] Tests against the seeded DB

### Backend — Availability API

- [ ] Endpoints to set working hours (start time, end time) for specific dates
- [ ] Support multiple windows per day (split shifts) and removing windows (block time)
- [ ] Decide & implement the weekly template approach — see [Data model](../architecture/data-model.md#availability)
- [ ] **Logging:** `availability.created`, `availability.deleted`
- [ ] Tests

### Backend — Admin protection

- [ ] Decide the minimum viable admin auth (e.g. `ADMIN_TOKEN` bearer header) and apply to `/admin/*`

### Frontend — Admin UI

- [ ] Base HTML/CSS layout, **mobile-first, RTL Hebrew** — see [Frontend](../architecture/frontend.md)
- [ ] Hidden / unlisted `admin.html`
- [ ] Vanilla JS: fetch and display services; add / edit / disable forms
- [ ] Vanilla JS: fetch and display availability per week; add / remove windows
- [ ] Daily and weekly schedule views (appointments list — will be empty until Sprint 3)
- [ ] `api.js` wrapper with loading indicator and error mapping

## Definition of done

The owner can, from her phone:

1. Add her real services with prices and durations
2. Set her working hours for the next two weeks, including a split-shift day and a day off
3. See both reflected immediately in the admin UI

## Demo script

1. Open `admin.html` on a phone
2. Create "Box braids — 240 min — ₪600"
3. Edit the price, then disable the service, confirm it's hidden from `GET /services`
4. Add Sunday 09:00–13:00 and 16:00–20:00; delete the afternoon window
