---
id: ARCH-002-ADMIN-011
architecture_id: ARCH-002
title: Add protected Redis Shopify queue monitor to Admin tenant directory
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 31
executor: copilot
claimed_at: 2026-09-04T17:03:33Z
attempt: 2
depends_on:
  - ARCH-002-ADMIN-005
enables: []
created: 2026-09-04
updated: 2026-09-04
---

# Add Protected Redis Shopify Queue Monitor to Admin Tenant Directory

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Current Execution State

This task is **Complete — architect accepted Attempt 2**.

`moda_architect` inspected the submitted Attempt 2 implementation and accepted
the bounded correction. The first-use refresh now defaults to 5 seconds while
persisted Paused/2-second/invalid values behave as required. The repository
agent's validation report is complete and internally consistent.

No further implementation attempt is authorised under this task.

The developer-managed Render `REDIS_URL` value remains deployment configuration
for live testing and is not an application-code acceptance blocker for this
task.

## Objective

Extend the existing protected Admin **Tenant Directory** page with a small live
Redis/BullMQ queue monitor so the developer can observe the Shopify event queues
while testing the Render deployment.

The monitor is diagnostic operational UI. It should help answer:

```text
Did Shopify queue activity reach Redis?
Is work currently waiting / active / delayed / failed?
Is a worker attached to the queue?
Has the BullMQ queue event stream changed recently?
```

It is not a durable business-history screen.

The existing database-backed KPI:

```text
Active Recoveries (Now)
```

must remain unchanged.

## Current Implementation Facts

The current Tenant Directory page is server-rendered at:

```text
moda-interact-admin/src/app/(protected)/page.tsx
```

and renders reusable KPI cards through:

```text
moda-interact-admin/src/components/admin/kpi-card.tsx
```

The Admin repository already consumes:

```text
@modainteract/moda-interact-shared@0.4.0
```

The Shopify application already uses that same shared package release for the
canonical Shopify queue contracts. Reuse the published shared contract; do not
copy queue names/job names into a new Admin-owned contract.

Authoritative contract import:

```ts
import { SHOPIFY_WEBHOOK_QUEUE_CONTRACTS } from
  '@modainteract/moda-interact-shared/shopify';
```

The required contracts are:

```text
CHECKOUT_EVENTS
  queueName: checkout-events
  jobName:   checkout-created

CHECKOUT_UPDATED_EVENTS
  queueName: checkout-events
  jobName:   checkout-updated

ORDER_EVENTS
  queueName: order-events
  jobName:   order-completed
```

Important: checkout-created and checkout-updated share the same BullMQ queue.
Create/read **two queue instances**, not three:

```text
checkout-events
  jobs:
    checkout-created
    checkout-updated

order-events
  jobs:
    order-completed
```

The Shopify publisher currently uses:

```text
removeOnComplete: true
removeOnFail: false
```

Therefore a successful job may disappear immediately after completion.
Do not present a zero completed-job count as proof that no event was processed.
Do not redesign retention in another service for this task.

## Hard Repository Boundary

All implementation changes for this task MUST remain inside:

```text
moda-interact-admin/
```

plus this task/index/parent-architecture coordination documentation.

Do NOT modify:

```text
moda-interact/
moda-interact-background/
moda-interact-gateway/
moda-interact-messaging/
moda-interact-database/
moda-interact-shared/
moda-interact-system-test/
```

Do NOT create a database migration or add a database setting for refresh
frequency.

Do NOT alter queue producers, consumers, job retention, retry semantics,
concurrency or payloads.

Do NOT edit Render Blueprint YAML in this task.

## Redis Configuration Boundary

The Admin process may read Redis only from the server-side environment variable:

```text
REDIS_URL
```

Never send `REDIS_URL` or any Redis credentials to the browser.

Add a documented placeholder to:

```text
moda-interact-admin/.env.example
```

No real credential may be committed.

The current canonical Render topology does not inject the Redis configuration
group into the Admin service. This task MUST NOT change the gateway Blueprint to
fix that.

The Admin implementation must therefore behave safely when `REDIS_URL` is
absent:

```text
Admin page still loads
queue monitor shows Redis unavailable / not configured
existing tenant/recovery functionality remains usable
```

For current Render testing, the developer can provide the existing test Redis
URL to the Admin service outside this repository task. The value must remain a
Render-held secret/configuration value.

## Required UI

On the protected Tenant Directory page, add a section directly below the
existing platform-summary KPI row.

Suggested presentation:

```text
Shopify Queue Activity                         Refresh: [5 seconds v] [Refresh now]
Last updated: 17:25:31

+--------------------------------------+  +--------------------------------------+
| Checkout Events                      |  | Order Events                         |
| checkout-events                      |  | order-events                         |
| checkout-created                     |  | order-completed                      |
| checkout-updated                     |  |                                      |
|                                      |  |                                      |
| Waiting  0   Active  0               |  | Waiting  0   Active  0               |
| Delayed  0   Failed  0               |  | Delayed  0   Failed  0               |
| Workers  1                           |  | Workers  1                           |
| Last Redis activity: completed ...   |  | Last Redis activity: ...             |
+--------------------------------------+  +--------------------------------------+
```

Use the existing Admin visual language rather than inventing a separate design
system.

The section must show for each queue:

- queue name;
- canonical job name(s) belonging to that queue;
- current waiting count;
- current active count;
- current delayed count;
- current failed count;
- current worker count;
- timestamp/type of the latest BullMQ Redis event-stream entry when available;
- a clear unavailable/error state that does not hide the rest of the page.

Do not display:

- Redis URLs/hosts/passwords;
- job payloads;
- customer data;
- Shopify webhook payloads;
- access tokens;
- raw failure stack traces;
- BullMQ return values.

A job ID is not required by this task and should not be sent to the browser.

## Refresh Behaviour

Refresh configuration is **browser-local UI state**, not durable application
state.

Implement a small client component that:

1. performs one fetch immediately when mounted;
2. polls the protected Admin queue API at the selected interval;
3. provides a `Refresh now` control;
4. provides these bounded interval choices:

```text
Paused
2 seconds
5 seconds   <- default
10 seconds
30 seconds
60 seconds
```

5. persists the selected interval in browser `localStorage` under an Admin-owned
   key;
6. never writes the interval to PostgreSQL;
7. stops polling when `Paused` is selected;
8. cleans up timers/aborted requests on unmount;
9. avoids overlapping requests when a prior poll is still in flight;
10. keeps the last successful snapshot visible during a transient poll failure
    and marks it stale/unavailable rather than replacing the entire page.

Do not use URL query parameters for the refresh interval.

## Server-side Redis Reader

Create a dedicated server-only Admin module, for example:

```text
moda-interact-admin/src/lib/admin/queue-monitor.ts
```

Responsibilities:

1. read `REDIS_URL` only on the server;
2. reuse `SHOPIFY_WEBHOOK_QUEUE_CONTRACTS` from the shared package;
3. lazily create/reuse exactly two BullMQ `Queue` objects:
   - `checkout-events`
   - `order-events`;
4. use bounded BullMQ public getter APIs for current queue state;
5. read only the most recent BullMQ queue-event stream entry needed for the
   `last activity` field;
6. derive the events-stream Redis key from the BullMQ queue object/configuration
   rather than hard-coding a second queue naming contract where practical;
7. bound Redis connection/query failure so a dead Redis endpoint does not hang
   Admin requests indefinitely;
8. return a small data-only snapshot safe to serialize to the browser;
9. never return Redis connection details, job payloads or raw provider errors.

Use BullMQ public getters (or their current-version equivalents) for:

```text
waiting
active
delayed
failed
worker count
```

Do not enumerate an unbounded number of jobs in order to calculate per-job-name
counts.

Because both checkout job names share `checkout-events`, state counts are
queue-level counts. The UI must not label them as separate exact
`checkout-created` versus `checkout-updated` counts.

### Latest Redis Activity

The BullMQ queue event stream is useful here because successful jobs are removed
on completion.

For each queue, perform only a bounded `latest entry` read from the BullMQ event
stream (for example one reverse-range entry), and expose only:

```text
event type
observed stream timestamp
```

Do not expose the stream's raw payload fields.

This is recent operational evidence, not durable history. If no event-stream
entry exists, return `null`/`none` rather than treating that as an error.

## Dependencies

Add direct runtime dependencies to `moda-interact-admin` only if required by the
implementation.

Expected aligned dependencies are:

```text
bullmq ^6.3.1
ioredis ^6.0.0
```

Update both:

```text
moda-interact-admin/package.json
moda-interact-admin/package-lock.json
```

Do not upgrade `@modainteract/moda-interact-shared` for this task.

If the existing installed `0.4.0` package unexpectedly does not expose the
canonical queue contract used by the Shopify app, STOP and return that concrete
dependency mismatch to `moda_architect`; do not edit `moda-interact-shared`.

## Protected API Route

Create one same-service read-only route, for example:

```text
GET /api/admin/queues
```

The route must:

1. call the existing `requirePlatformAdminRead()` security boundary before
   Redis access;
2. be dynamic/no-store so snapshots are never served from application caching;
3. return a small JSON snapshot on success;
4. return a bounded unauthorized response when the platform-admin boundary
   denies access;
5. return a bounded `503` unavailable response when `REDIS_URL` is absent or
   Redis cannot be queried;
6. never include connection strings, raw Redis errors, stack traces or job data
   in the response.

A successful response may use this repository-local shape:

```ts
type QueueMonitorSnapshot = {
  observedAt: string;
  queues: Array<{
    queueName: string;
    jobNames: string[];
    counts: {
      waiting: number;
      active: number;
      delayed: number;
      failed: number;
      workers: number;
    };
    lastActivity: null | {
      event: string;
      observedAt: string;
    };
  }>;
};
```

This shape is local to Admin and is not a new cross-service contract.

## Expected File-level Implementation

Keep the implementation small. The expected change set is approximately:

```text
moda-interact-admin/package.json
moda-interact-admin/package-lock.json
moda-interact-admin/.env.example

moda-interact-admin/src/lib/admin/queue-monitor.ts
moda-interact-admin/src/app/api/admin/queues/route.ts
moda-interact-admin/src/components/admin/queue-monitor.tsx
moda-interact-admin/src/components/admin/queue-status-card.tsx   (optional if useful)
moda-interact-admin/src/app/(protected)/page.tsx

moda-interact-admin/tests/security/admin-queue-monitor.test.mjs
```

Do not create extra abstractions unless required by the implementation.

## Luna Execution Order

Implement in this order so each step can be reasoned about independently.

### Step 1 — Inspect before editing

Read:

```text
moda-interact-admin/src/app/(protected)/page.tsx
moda-interact-admin/src/components/admin/kpi-card.tsx
moda-interact-admin/src/lib/auth/platform-admin.ts
moda-interact-admin/package.json
moda-interact-admin/.env.example
```

Confirm the shared contract import exists in the installed dependency surface.

### Step 2 — Add Admin-local queue dependencies

Add only the runtime packages required to create/read BullMQ queues.
Regenerate `package-lock.json` through npm rather than hand-editing lock data.

### Step 3 — Implement the server-only queue snapshot reader

Implement the two canonical queue readers and a small serializable snapshot.
Keep all Redis configuration and clients server-side.

Make missing `REDIS_URL` an expected unavailable state, not a process-start
failure.

### Step 4 — Implement the protected GET route

Require platform-admin read access first, then call the queue reader.
Return no-store JSON and bounded 401/503 behavior.

### Step 5 — Implement the polling client component

Implement immediate fetch, interval selector, localStorage persistence, manual
refresh, no overlapping polls and stale/error presentation.

### Step 6 — Add the queue section to Tenant Directory

Do not change the current Prisma-backed KPI calculation.
Place the queue monitor below the existing KPI summary.

### Step 7 — Add focused tests

Use a small test seam/fake queue reader; do not require a developer Redis
instance for the normal repository test suite.

### Step 8 — Validate and stop

Run the required checks below, update this task to `review`, write the Completion
Report and STOP.

## Out of Scope

Explicitly out of scope:

- PostgreSQL schema or migration changes;
- storing refresh preferences in PostgreSQL;
- gateway or Render Blueprint changes;
- worker changes;
- Shopify webhook changes;
- BullMQ queue/job contract changes;
- changing `removeOnComplete` / `removeOnFail`;
- durable queue history;
- queue retry/pause/resume/delete controls;
- job mutation/retry/removal buttons;
- arbitrary Redis command UI;
- displaying job payloads;
- per-tenant queue filtering;
- WhatsApp queues;
- CommerceAgent queues;
- new OpenTelemetry metrics;
- Grafana changes;
- creating a new shared package contract.

This is a read-only diagnostic surface.

## Acceptance Criteria

- [x] existing Tenant Directory and `Active Recoveries (Now)` behavior is unchanged;
- [x] protected Tenant Directory contains a new Shopify Queue Activity section;
- [x] `checkout-events` is shown once and lists both `checkout-created` and
      `checkout-updated` canonical job names;
- [x] `order-events` is shown once and lists `order-completed`;
- [x] queue names/job names come from `SHOPIFY_WEBHOOK_QUEUE_CONTRACTS`, not
      duplicated local literals used as runtime contracts;
- [x] current waiting/active/delayed/failed/worker counts are read from Redis via
      BullMQ;
- [x] latest queue event-stream type/timestamp is read with a bounded operation;
- [x] UI does not pretend queue-level counts are exact per-job-name counts;
- [x] UI does not use completed count as durable proof because successful jobs
      are removed on completion;
- [x] refresh is configurable on-screen with Paused/2/5/10/30/60-second choices;
- [x] default refresh is 5 seconds;
- [x] refresh preference is browser-local and never stored in PostgreSQL;
- [x] manual `Refresh now` works;
- [x] polling starts immediately, does not overlap, and is cleaned up on unmount;
- [x] last successful snapshot remains visible during transient Redis/API errors;
- [x] queue API requires existing platform-admin read authorization;
- [x] `REDIS_URL` and Redis credentials remain server-only;
- [x] absent/unavailable Redis does not break the Tenant Directory page;
- [x] no job/customer/webhook payload data is returned to the browser;
- [x] no database/schema, gateway, worker, Shopify ingress, messaging or shared
      repository changes are made;
- [x] implementation is ready for developer commit/push; repository agent does
      not commit or push.

## Focused Tests

Add focused tests that prove at minimum:

```text
canonical contract mapping
  checkout-events -> checkout-created + checkout-updated
  order-events    -> order-completed

snapshot mapping
  waiting/active/delayed/failed/workers returned correctly
  latest event type/time is bounded and serialized
  no payload/connection material is serialized

missing configuration
  REDIS_URL absent -> bounded unavailable result

security boundary
  unauthorised queue API request cannot read Redis / receive queue data
```

Use fakes/test seams where necessary. Normal tests must not require a live Redis
server.

## Validation

Before returning for architect review:

- [x] inspect `moda-interact-admin/package.json` and use its declared scripts;
- [x] focused Admin queue-monitor tests pass;
- [x] `npm test` passes;
- [x] `npm exec tsc -- --noEmit` passes (repository has no dedicated `typecheck`
      script at task creation);
- [x] `npm run lint` passes;
- [x] `npm run build` passes;
- [x] inspect the final browser/server boundary for Redis/job-data leakage;
- [x] inspect the diff for changes outside the allowed Admin scope;
- [x] `git diff --check` passes;
- [x] do not commit;
- [x] do not push.

If a validation failure reveals that correct implementation requires changing
another repository, a database schema, a shared contract, queue retention or
Render Blueprint configuration, set this task to `blocked`, document the exact
gap, return to `moda_architect`, and STOP.

## Stop Condition

After the read-only queue monitor is implemented and validated:

```text
status: in_progress -> review
Completion Report: Ready for Review
```

Return to `moda_architect` and STOP.

Do not mark the task Complete yourself.

## Completion Report

### Status

Ready for Review — Attempt 2 correction complete

### Files Changed

- `moda-interact-admin/package.json`
- `moda-interact-admin/package-lock.json`
- `moda-interact-admin/.env.example`
- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/src/app/api/admin/queues/route.ts`
- `moda-interact-admin/src/components/admin/queue-monitor.tsx`
- `moda-interact-admin/src/components/admin/queue-monitor-refresh.ts`
- `moda-interact-admin/src/app/(protected)/page.tsx`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`

### Work Completed

Implemented a protected, read-only Shopify BullMQ queue monitor on the Admin
Tenant Directory. The server reader uses the shared Shopify queue contracts,
creates exactly two queue readers, reports bounded queue counts/worker counts,
and reads only the latest event-stream entry. Redis configuration and errors
remain server-side and missing/unavailable Redis returns a bounded `503`.

Added a no-store `GET /api/admin/queues` route with the existing platform-admin
read boundary, plus a client-local refresh selector with Paused, 2, 5, 10, 30,
and 60-second options. Polling avoids overlap, aborts on unmount, supports
manual refresh, and preserves the last successful snapshot during failures.

Corrected the browser-local refresh initialisation so an absent localStorage
entry defaults to 5 seconds, while explicit `0`, valid intervals, and invalid
values restore or fall back as required. Added executable coverage for all four
cases.

### Validation Results

```text
focused queue monitor tests: 5 passed, 0 failed
npm test: 33 passed, 0 failed
npm exec tsc -- --noEmit: passed
npm run lint: passed
npm run build: passed
git diff --check: passed
```

The production build reports a non-fatal optional BullMQ warning because
`@valkey/valkey-glide` is not installed; the build completes successfully and
the Redis/ioredis path used by this task does not require that optional client.

### Deviations

None. No other repository, database schema, queue producer/consumer, gateway,
Blueprint, or shared contract was changed.

### Assumptions

The existing Render/Admin deployment will receive `REDIS_URL` through its
developer-managed server configuration when live queue observation is needed.

### Unresolved Issues

No implementation blockers. Live visual/browser verification with a configured
Redis instance remains developer-owned deployment validation.

### Architectural Concerns

None. The monitor is read-only and remains inside the Admin repository.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-ADMIN-011` is architect-accepted after Attempt 2.

The Attempt 1 review findings have been resolved within the original task scope:

- first-use refresh now distinguishes an absent localStorage entry from an
  explicitly persisted `0` / Paused value;
- no saved preference defaults to `5000` ms / 5 seconds;
- saved `0` restores Paused;
- saved `2000` restores the 2-second option;
- invalid persisted values fall back to 5 seconds;
- the stale duplicate Completion Report sections were removed.

The implementation remains a protected, read-only Admin diagnostic surface and
does not expand into database, gateway, Shopify, background, messaging or shared
repository ownership.

The malformed `REDIS_URL` observed during manual Render testing was identified as
a developer-managed environment-value issue. No application-code correction is
required for that configuration mistake, and it is not an acceptance blocker for
this task.

### Reviewed Files

Architect review inspected at minimum:

```text
moda-interact-admin/src/components/admin/queue-monitor-refresh.ts
moda-interact-admin/src/components/admin/queue-monitor.tsx
moda-interact-admin/src/lib/admin/queue-monitor.ts
moda-interact-admin/src/app/api/admin/queues/route.ts
moda-interact-admin/tests/security/admin-queue-monitor.test.mjs
docs/decisions/admin/ARCH-002/ADMIN-011-add-redis-queue-monitor.md
```

### Validation Reviewed

The implementing agent reported for Attempt 2:

```text
focused queue monitor tests: 5 passed, 0 failed
npm test: 33 passed, 0 failed
npm exec tsc -- --noEmit: passed
npm run lint: passed
npm run build: passed
git diff --check: passed
```

Architect source inspection confirms the corrected refresh helper explicitly
handles `localStorage.getItem(...) === null` before numeric conversion and the
focused test covers the required default/saved-value matrix.

An independent focused-suite rerun was not used as acceptance evidence because
the review container provides Node 22 while the workspace baseline is Node
24.19.0; direct Node 22 execution cannot load the TypeScript modules used by the
repository test harness. The repository-agent validation above was completed in
the intended workspace toolchain.

### Architecture Conformance

Accepted as conformant with the task and ARCH-002 boundaries:

- queue names/job names come from the canonical shared Shopify contracts;
- exactly the two logical BullMQ queues are observed;
- Redis access and credentials remain server-side;
- the API remains protected by the existing platform-admin read boundary;
- refresh preference remains browser-local with no database/schema change;
- the monitor remains read-only and does not alter queue semantics;
- missing/unavailable Redis degrades the monitor rather than the Tenant Directory;
- no other runtime repository or Render Blueprint is modified by this task.

### Follow-up

None required for task acceptance.

`ARCH-002-ADMIN-011` is Complete. Live Render queue observation remains
developer-owned deployment validation using the correctly configured Admin
`REDIS_URL`.

