# Out of Scope for the MVP

To ship fast, the following features are **explicitly deferred** to future phases. If you find yourself building one of these, stop and check with the team lead.

| Feature | Why deferred | MVP workaround | Likely phase |
|---|---|---|---|
| **Online payments & invoicing** — Apple Pay, Google Pay, Bit, credit card; automated tax receipts | Requires clearing-company integration, compliance, and receipts logic | Payment is collected **on-site** | Phase 2 |
| **Automated reminders** — SMS / WhatsApp 24 h before the appointment | Needs a messaging provider, cost per message, opt-in handling | Owner reminds manually if needed | Phase 2 |
| **Client history (CRM)** — past appointments, internal notes per client | Needs a proper client entity and privacy considerations | Owner keeps notes elsewhere | Phase 2 |
| **Photo gallery** — showcase past work | Pure marketing; not needed to book | Instagram link | Phase 3 |
| **Admin "force double-book" override** | Conflicts with the core no-overlap guarantee | Admin adjusts availability instead | TBD |
| **Formal admin authentication** (beyond a hidden URL) | Not in the PRD; evaluate risk in Sprint 2 | Hidden/unlisted `/admin.html` | Sprint 2 decision |

!!! tip "Design for it, don't build it"
    When modelling data in Sprint 1, keep these in mind so they're easy to add later — e.g. store the client's phone in a normalised format so a future `clients` table can be derived from appointments. But **don't** add the tables now.
