# Sprint 3 — The Booking Engine

**Team:** both developers.
**Goal:** implement the dynamic time-blocking algorithm and build the client-facing booking flow. This is the **core complexity** of the product.

## Checklist

### Backend — the algorithm

- [ ] Core function: given a date and service id, load availability for the date, subtract all booked appointments, return only start times that fit `duration_minutes` — see [Booking algorithm](../architecture/booking-algorithm.md)
- [ ] Decide `SLOT_STEP_MINUTES` (proposed 30)
- [ ] Exclude past times for today
- [ ] `GET /slots?service_id=&date=`

### Backend — Booking API

- [ ] `POST /appointments`: **re-validate the slot inside a transaction** to prevent race conditions; save client name, phone, service, start, computed end
- [ ] Return `409 Conflict` with a stable error code when the slot is taken
- [ ] Optional hardening: PostgreSQL exclusion constraint — see [Data model](../architecture/data-model.md#the-no-overlap-guarantee)
- [ ] Admin manual booking uses the same endpoint/validation
- [ ] `GET /admin/appointments?from=&to=` for the schedule views; `DELETE /admin/appointments/{id}`
- [ ] **Logging:** `booking.started`, `appointment.created`, `booking.conflict` (*"User attempted to book an already taken slot"*), `appointment.cancelled_by_admin`

### Frontend — client flow

- [ ] Landing page listing all active services (name, price, duration)
- [ ] Simple calendar / date picker
- [ ] Fetch and display slots dynamically for the chosen service + date
- [ ] Booking form (full name, phone) and success confirmation screen
- [ ] Handle `409` gracefully: refresh slots and show a friendly message
- [ ] Wire admin schedule views to real appointments

### Automated testing

- [ ] Integration tests for the time-blocking algorithm covering **every item** in the [edge-case list](../architecture/booking-algorithm.md#edge-cases-the-tests-must-cover)
- [ ] Concurrency test: two bookings for the same slot → exactly one succeeds
- [ ] Freeze time in tests for deterministic "today"

## Definition of done

1. A client can book a real appointment from a phone in under a minute
2. `pytest` proves no overlapping appointment can be created
3. The owner sees the booking in her daily view immediately

## Demo script

1. Seed a day with 09:00–13:00 availability and a 10:00–11:00 booking
2. Pick a 90-minute service → only 11:00 and 11:30 are offered
3. Book 11:00 on two phones simultaneously → one succeeds, the other sees "slot just taken"
