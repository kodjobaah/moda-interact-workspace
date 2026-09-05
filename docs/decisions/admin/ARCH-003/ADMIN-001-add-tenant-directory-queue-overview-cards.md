---
id: ARCH-003-ADMIN-001
architecture_id: ARCH-003
title: Add compact queue activity overview cards to Tenant Directory
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 10
executor: copilot
claimed_at: 2026-09-04T19:03:54Z
attempt: 3
depends_on:
  - ARCH-002-ADMIN-011
enables:
  - ARCH-003-ADMIN-002
created: 2026-09-04
updated: 2026-09-04
---

# Add compact queue activity overview cards to Tenant Directory

## Architecture

Architecture ID:

`ARCH-003`

Architecture document:

`docs/architecture/ARCH-003-admin-operational-ui.md`

Coordinator:

`moda_architect`

## Objective

Add four compact KPI-style cards to `Tenant Directory` that show the current
number of **active** jobs for each of the four observed BullMQ queues.

## Context

The current queue monitor proved that Admin can read Redis queue state, but the
large in-page monitor is too heavy for the primary `Tenant Directory` screen.

The Tenant Directory should expose a concise overview only. Administrators still
need to know whether work is actively executing in each queue, but they do not
need detailed queue diagnostics on this screen.

## Scope

- add four compact overview cards to `Tenant Directory`;
- represent the four observed queues:
  - `checkout-events`
  - `order-events`
  - `pending-recovery-candidates`
  - `whatsapp-events`;
- show the BullMQ `active` count only for each queue;
- fetch queue overview data server-side using the existing protected Admin queue
  access pattern;
- update the page layout so the six summary cards (`Active Tenants`, `Active
  Recoveries (Now)`, plus four queue cards) fit cleanly without clutter;
- keep the existing tenant table below the overview section.

## Out of Scope

- failed-job diagnostics;
- moving the large queue monitor out of the page;
- refresh controls visible on `Tenant Directory`;
- queue details pages or drawers;
- mutations such as retry/delete/pause/resume;
- database changes.

## Requirements

- the four cards must be visually consistent with the existing summary-card
  design language;
- each card must show one queue only;
- each card must show the current BullMQ `active` count and no failed-job data;
- labels must be understandable to a platform admin and may use user-friendly
  card titles rather than raw Redis key syntax;
- the screen must remain readable at typical laptop widths without the page
  feeling dominated by observability content;
- the data access must remain server-side and protected; Redis credentials must
  not be exposed to the browser;
- when Redis is temporarily unavailable, the queue cards must degrade safely and
  must not break the rest of the Tenant Directory page.

## Work Items

- [x] Define the Admin-owned read-only overview model for the four queue cards.
- [x] Extend or adapt the existing server-side queue reader so the page can read
      the `active` count for the four observed queues.
- [x] Add the four queue overview cards to `Tenant Directory`.
- [x] Arrange the six-card overview grid responsively.
- [x] Add safe unavailable/loading states that keep the rest of the page usable.
- [x] Add focused tests for the new overview-card behavior.

## Interfaces / Contracts

Consumes:

- existing Admin queue reader patterns from `ARCH-002-ADMIN-011`;
- existing `SHOPIFY_WEBHOOK_QUEUE_CONTRACTS` where useful for
  `checkout-events` and `order-events`.

Admin-owned observability configuration may define the two additional read-only
queue identities required for this screen:

- `pending-recovery-candidates`
- `whatsapp-events`

This task does not introduce a new cross-service payload contract.

## Dependencies

- `ARCH-002-ADMIN-011`

## Enables

- `ARCH-003-ADMIN-002`

## Acceptance Criteria

- [x] `Tenant Directory` shows four additional queue cards.
- [x] The cards represent `checkout-events`, `order-events`,
      `pending-recovery-candidates`, and `whatsapp-events`.
- [x] Each card shows only the queue's current `active` count.
- [x] No failed-job count is shown on the overview cards.
- [x] The cards are visually compact and consistent with the existing summary
      cards.
- [x] Redis unavailability does not break the rest of the page.
- [x] Redis credentials remain server-side only.

## Validation

- [x] focused component / model tests for queue overview cards
- [x] affected Admin test suite
- [x] repository typecheck
- [x] repository lint
- [x] production build
- [x] `git diff --check`

## Implementation Notes

- Use a quiet, non-cluttering presentation; the overview cards should feel like
  part of the primary dashboard rather than a second observability console.
- A background refresh strategy may be used if it remains unobtrusive and does
  not require storing user preferences in the database.
- If a background refresh is implemented for this page, keep it fixed and
  low-noise rather than adding visible refresh controls to `Tenant Directory`.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-admin/src/app/(protected)/page.tsx`
- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-001-add-tenant-directory-queue-overview-cards.md`

### Work Completed

- Added an Admin-owned read-only overview model for the four observed BullMQ queues.
- Added server-side active-count reads for `checkout-events`, `order-events`,
  `pending-recovery-candidates`, and `whatsapp-events`.
- Added four compact KPI cards to the Tenant Directory and changed the summary
  grid to a responsive six-card layout.
- Added an `Unavailable` fallback so Redis failure does not prevent tenant data
  from rendering.
- Kept queue access server-side and reused the existing protected page boundary.
- Attempt 2 restored the Admin Redis/BullMQ reader connections to bounded,
  fail-fast request behavior with `enableOfflineQueue: false` and
  `maxRetriesPerRequest: 1`.
- Attempt 3 removed the overview-only raw Redis reader and cache. The overview
  path now creates only BullMQ queue readers and reads `active` counts.

### Validation Results

- `node --test tests/security/admin-queue-monitor.test.mjs` — 7 passed, 0 failed.
- `npm test` — 35 passed, 0 failed.
- `npm exec tsc -- --noEmit` — passed.
- `npm run lint` — passed with no warnings.
- `npm run build` — passed. Existing optional BullMQ `@valkey/valkey-glide`
  module warning remains; it does not affect the ioredis build path.
- `git diff --check` — passed.

### Deviations

None.

### Assumptions

The two additional queue identities are Admin-owned observability configuration,
as authorized by the task contract, and do not require shared producer changes.
Admin queue reads must remain bounded request operations rather than worker-style
offline queues. The overview path does not need the raw Redis event stream.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 completes the bounded correction requested during architect review.

Architect source inspection confirms:

- the four Tenant Directory queue cards remain scoped to active-job counts only;
- the overview covers `checkout-events`, `order-events`,
  `pending-recovery-candidates`, and `whatsapp-events`;
- the overview path now creates only BullMQ `Queue` readers and no longer
  constructs or caches a raw `ioredis` event-stream reader;
- the existing detailed queue monitor retains its separate raw Redis reader for
  last-event inspection, which is outside this overview correction;
- Admin queue reads retain bounded fail-fast settings:
  `enableOfflineQueue: false`, `maxRetriesPerRequest: 1`, and bounded connect /
  command timeouts;
- the focused regression test supplies a `redisFactory` that throws if called by
  the overview path, proving that the overview does not depend on the raw Redis
  reader;
- Redis-unavailable handling remains isolated from Tenant Directory data;
- no ADMIN-002 implementation was started.

No further correction is required for ARCH-003-ADMIN-001.

### Reviewed Files

- `moda-interact-admin/src/app/(protected)/page.tsx`
- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- `docs/decisions/admin/ARCH-003/ADMIN-001-add-tenant-directory-queue-overview-cards.md`

### Validation Reviewed

Implementing-agent Attempt 3 evidence records:

- focused tests: 7 passed;
- full Admin tests: 35 passed;
- TypeScript: passed;
- lint: passed;
- production build: passed;
- diagnostics: passed;
- `git diff --check`: passed.

Architect source inspection independently verified the Attempt 3 code and
focused regression assertion. The supplied review archive does not contain the
complete workspace toolchain markers used by the repository agent, so the
agent's recorded validation remains the authoritative executable validation for
this acceptance.

### Architecture Conformance

Accepted. The implementation conforms to ARCH-003-ADMIN-001 scope and preserves
the Admin-only, read-only, bounded Redis/BullMQ boundary.

### Follow-up

`ARCH-003-ADMIN-002` is now unblocked and may be promoted to `ready`.
