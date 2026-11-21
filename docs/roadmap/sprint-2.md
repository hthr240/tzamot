# Sprint 2 — Admin Core

**Team:** both developers — the second developer joins here.
**Goal:** build the backend entities and the hidden admin interface so the business owner can start configuring her services and working hours.

Track work in the [Sprint 2 milestone](https://github.com/hthr240/tzamot/milestone/2)
and [Project](https://github.com/users/hthr240/projects/3). Parent stories: admin
auth (#58), services API (#59), availability API (#60), admin UI (#61).

## Checklist

### Backend — Admin protection

- [ ] Decide the minimum viable admin auth (e.g. `ADMIN_TOKEN` bearer header) and apply to `/admin/*` — #62

### Backend — Services API

- [ ] CRUD endpoints for `services`: create, read, update, deactivate (name, duration in minutes, price) — #63; see [Backend → API surface](../architecture/backend.md#api-surface-mvp)
- [ ] `GET /services` returns only **active** services — #63
- [ ] Pydantic schemas with validation (`duration_minutes > 0`, `price >= 0`) — #63
- [ ] **Logging:** `service.created`, `service.updated`, `service.disabled` — #63
- [ ] Tests against the seeded DB — #63

### Backend — Availability API

- [ ] Endpoints to set working hours (start time, end time) for specific dates — #64
- [ ] Support multiple windows per day (split shifts) and removing windows (block time) — #64
- [ ] Implement weekly confirmation and single-day edits on the materialised template — #65; [ADR-008](../decisions.md#adr-008-materialised-weekly-working-hours)
- [ ] **Logging:** `availability.created`, `availability.deleted` — #64
- [ ] Tests — #64 · #65

### Frontend — Admin UI

- [ ] `api.js` wrapper with loading indicator and error mapping — #66
- [ ] Base HTML/CSS layout, **mobile-first, RTL Hebrew** — #67; see [Frontend](../architecture/frontend.md)
- [ ] Hidden / unlisted `admin.html` — #67
- [ ] Vanilla JS: fetch and display services; add / edit / disable forms — #68
- [ ] Vanilla JS: fetch and display availability per week; add / remove windows — #69
- [ ] Daily and weekly schedule views (appointments list — will be empty until Sprint 3) — #70

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
