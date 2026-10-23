# Glossary

Domain and technical terms used throughout the project. UI strings are in Hebrew; code and docs use the English terms below.

## Domain terms

| Term | Hebrew (UI) | Meaning |
|---|---|---|
| **Tzamot** | צמות | Project name — literally *braids*. |
| **Client** | לקוחה | An end user booking an appointment. Identified only by full name + phone number. No account. |
| **Admin** | מנהלת | The business owner. Manages services, availability, and all appointments. |
| **Service** | שירות | Something the business offers (e.g. full-head braids). Has a **name**, **price**, and **duration in minutes**. |
| **Duration** | משך | How long a service takes. Drives the calendar blocking logic. |
| **Availability** | זמינות / שעות פעילות | A window of time on a specific date when the admin is working (start time → end time). |
| **Working hours** | שעות עבודה | The admin's weekly default availability pattern. |
| **Block / Blocked time** | חסימה | A period the admin marks as unavailable (personal time, holiday). |
| **Split shift** | משמרת מפוצלת | Two or more availability windows on the same day (e.g. 09:00–13:00 and 16:00–20:00). |
| **Slot** | משבצת / שעה פנויה | A candidate *start time* that can fit a service of a given duration without overlapping existing appointments. |
| **Appointment / Booking** | תור | A confirmed reservation: client + service + start time (+ computed end time). |
| **Dynamic time blocking** | — | Automatically reserving exactly `duration` minutes for a booking so nothing can overlap. See [Business rules](product/business-rules.md). |
| **Double booking** | כפל תורים | Two appointments overlapping in time. Must never happen. |
| **Self-service cancellation** | ביטול עצמי | A client cancelling their own appointment, allowed only ≥ 24 h before the start time. |
| **No-show** | אי-הגעה | Client didn't arrive. Reducing this is the motivation for future automated reminders. |

## Technical terms

| Term | Meaning |
|---|---|
| **PWA** | Progressive Web App — a website that can be added to the home screen and feels native. Requires `manifest.json` + a service worker. |
| **FastAPI** | Python web framework for the backend API. Auto-generates OpenAPI docs at `/docs`. |
| **SQLAlchemy** | Python ORM used to define database models. |
| **Alembic** | Database migration tool for SQLAlchemy. `alembic upgrade head` applies all migrations. |
| **PostgreSQL** | Relational database. Runs in Docker locally, in CI, and in production. |
| **Caddy** | Reverse proxy that terminates HTTPS (auto Let's Encrypt) and forwards to FastAPI. |
| **Cloudflare Pages** | Static hosting + CDN for the frontend. Deploys automatically on push to `main`. |
| **Hetzner VPS** | The Linux virtual server running Docker in production. |
| **Docker Compose** | Orchestrates the `caddy`, `api`, and `db` containers from one YAML file. |
| **Service container** | A throwaway database GitHub Actions boots for CI test runs. |
| **Seeding** | Populating a database with realistic mock data so tests exercise real business logic. |
| **GitHub Flow** | Branch from `main` → PR → review → merge. No long-lived branches. |
| **Branch protection** | GitHub rules preventing direct pushes to `main` and requiring review + green CI. |
| **Ruff / Black** | Python linter / formatter enforced in CI. |
| **Structured logging** | Logs with consistent fields (level, timestamp, request id, …) written to stdout/stderr so Docker can collect them. |
