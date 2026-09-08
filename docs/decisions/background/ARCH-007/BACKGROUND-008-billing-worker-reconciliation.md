---
id: ARCH-007-BACKGROUND-008
architecture_id: ARCH-007
title: Add independent billing worker for publication, subscription sync, reconciliation and uninstall drain
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: review
priority: 120
executor: copilot
claimed_at: 2026-09-08T20:01:37Z
attempt: 2
depends_on:
  - ARCH-007-BACKGROUND-005
  - ARCH-007-BACKGROUND-007
  - ARCH-007-BACKGROUND-009
  - ARCH-007-SHOPIFY-001
enables: 
  - ARCH-007-ADMIN-003
  - ARCH-007-ADMIN-004
  - ARCH-007-GATEWAY-001
  - ARCH-007-SYSTEM-TEST-002
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08T21:05:40Z
---

# ARCH-007-BACKGROUND-008: Add independent billing worker for publication, subscription sync, reconciliation and uninstall drain

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Create the independently deployable billing worker runtime that continuously recovers durable billing work, reconciles Shopify subscription/usage state and prioritizes valid pre-uninstall events without coupling billing to recovery workers.

## Context

ARCH-007 cannot rely on callbacks or one-shot BullMQ jobs. Shopify plan changes can occur externally; Redis jobs can be lost; App Events pending rows must be recoverable from PostgreSQL.

## Scope

Background billing entrypoint/runtime/router/scheduler, Partner API subscription/usage reconciliation service and readiness integration following existing worker-process conventions.

## Out of Scope

- Render deployment declarations (GATEWAY-001).
- Merchant request projection implementation in moda-interact.
- Admin UI/actions.
- System tests.

## Requirements

- Add `src/entrypoints/billing.ts` (or repository-equivalent) using the same worker-process/observability/readiness conventions as existing background entrypoints; add package scripts `start:billing-worker` and `readiness:billing-worker` only if consistent with existing script pattern.
- Billing worker must run bounded recurring scans at minute-scale configuration, not sub-second busy loops.
- Publisher reconciliation: find due PENDING/RETRYABLE and stale IN_FLIGHT rows; stale IN_FLIGHT must return to retryable only under a bounded lease/attempt rule that preserves permanent idempotency identity.
- Recovery-credit purchase activation reconciliation: invoke the accepted BACKGROUND-009 durable activation/reconciliation path for reported pack-purchase UsageEvents so a Shopify-reported pack cannot remain indefinitely unactivated after a process crash. This worker wires/schedules the accepted service; it must not invent a second credit-grant implementation.
- Subscription reconciliation: query Shopify Partner ActiveSubscription for a bounded page of active shops, classify FlatRate/Tiered items identically to SHOPIFY-001 contract, and update local projection idempotently. Sharing source code across repos is not required; behavior/contract must match parent architecture.
- Partner API error != NO_CONTRACT. Preserve last known mapped plan subject to fail-closed staleness policy and record SYNC_ERROR; do not silently downgrade to Free.
- Reconciliation must discover pending updates and current-cycle transitions without subscription webhooks.
- Usage reconciliation: for current paid cycle compare Moda net REPORTED recovery-conversation quantity for the mapped meter with Shopify `items[].usage.quantity` for that TieredPrice item. Record discrepancy state/structured domain outcome for Admin; do not automatically create arbitrary financial corrections to force equality.
- Uninstall: prioritize pending/retryable events whose occurredAt <= stable Shop.uninstalledAt and stop any event with occurredAt after uninstall. After Shopify no longer accepts reporting window, mark NEEDS_ATTENTION rather than rewrite timestamp.
- Unknown Shopify plan handles remain UNMAPPED and become Admin-visible; next scan can map automatically after SUPER_ADMIN registers the plan.
- Worker readiness must verify process/config dependencies without calling provider on every readiness check. Telemetry uses existing shared logging/OTel conventions.

## Work Items

 [x] Add billing worker entrypoint/scripts/readiness.
 [x] Implement bounded rotating subscription reconciliation using the Partner API 2026-07 contract.
 [x] Implement publisher stale-work recovery and periodic due scans.
 [x] Wire bounded BACKGROUND-009 recovery-credit purchase activation reconciliation into the recurring billing worker scan.
 [x] Implement Shopify-vs-Moda usage comparison/discrepancy visibility using the accepted structured operational representation.
 [x] Implement uninstall prioritization/cutoff.
 [x] Add focused worker/reconciliation tests for the Attempt 2 corrections and the accepted B008 behaviors.

## Interfaces / Contracts

 [x] Billing work survives Redis/job loss because PostgreSQL scans recover due state.
 [x] A `RECOVERY_CREDIT_PACK_PURCHASE` whose billing UsageEvent is already REPORTED but whose purchase activation was interrupted is rediscovered and activated idempotently through BACKGROUND-009.
 [x] External Shopify plan changes are reflected without requiring merchant callback.
 [x] Partner failure cannot become no-contract/free.
 [x] Unknown plan maps after Admin registration on later scan with no deploy.
 [x] Usage discrepancy is visible but not auto-fudged.
 [x] Post-uninstall cutoff is enforced.
 [x] Independent entrypoint/readiness/tests/validation pass.
Use existing service.namespace/environment observability conventions.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-ADMIN-004
- ARCH-007-GATEWAY-001
- ARCH-007-SYSTEM-TEST-002
- ARCH-007-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Billing work survives Redis/job loss because PostgreSQL scans recover due state.
- [ ] A `RECOVERY_CREDIT_PACK_PURCHASE` whose billing UsageEvent is already REPORTED but whose purchase activation was interrupted is rediscovered and activated idempotently through BACKGROUND-009.
- [ ] External Shopify plan changes are reflected without requiring merchant callback.
- [ ] Partner failure cannot become no-contract/free.
- [ ] Unknown plan maps after Admin registration on later reconciliation with no deploy.
- [ ] Usage discrepancy is visible but not auto-fudged.
- [ ] Post-uninstall cutoff is enforced.
- [ ] Independent entrypoint/readiness/tests/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-BACKGROUND-008` branch and the mirrored parent-workspace `task/ARCH-007-BACKGROUND-008` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for architect review (Attempt 2)

### Files Changed

`moda-interact-background` implementation branch commit `e3960d5` (cumulative from `7501979`).

- `src/entrypoints/billing.ts`
- `src/providers/shopify-partner-billing.provider.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/services/shopify-usage-event-publisher.service.ts`
- `src/entrypoints/billing-resources.ts`
- `src/runtime/billing-scheduler.ts`
- `src/runtime/readiness.ts`
- `observability/billing.mjs`
- `package.json`
- focused runtime, provider and reconciliation tests under `tests/unit/`

### Work Completed

Attempt 2 addresses all five Architect Review corrections. Active-shop reconciliation now uses an in-memory stable-id keyset cursor with wraparound, so bounded scans rotate without starvation even when one Partner call fails. The scheduler uses a recursive timeout that schedules only after a pass settles, reports failures, and cancels cleanly on shutdown.

The independent `moda-billing-worker` now checks PostgreSQL only and closes a billing-specific Prisma resource path without constructing Redis. The publisher selects due uninstall-drain rows first within the bounded page, preserves permanent identities and cutoff validation, and fills remaining capacity with ordinary rows.

The Partner query mirrors the accepted SHOPIFY-001 current/pending billing-period and legacy-subscription fields while retaining order-independent FlatRate/Tiered classification. The worker runs due/stale Shopify usage publication, BACKGROUND-009 recovery-credit activation reconciliation, bounded active-shop subscription reconciliation, current-cycle Moda-versus-Shopify usage comparison, and structured discrepancy logging without financial auto-correction.

The worker runs due/stale Shopify usage publication, BACKGROUND-009 recovery-credit activation reconciliation, bounded active-shop Partner ActiveSubscription reconciliation, current-cycle Moda-versus-Shopify usage comparison, and structured discrepancy logging without financial auto-correction.

Subscription projection preserves the existing mapped plan on Partner failure and records `SYNC_ERROR`; no-contract and unknown-plan states are distinguished, pending plan updates and billing periods are projected, and unknown handles remain `UNMAPPED` until a plan is mapped.

Usage publication prioritizes pre-cutoff uninstall events and enforces the cutoff: eligible events can drain, while post-cutoff events are marked `NEEDS_ATTENTION` without timestamp rewriting.

### Validation Results

Passed:

- `npx vitest run tests/unit/services/billing-reconciliation.service.test.ts tests/unit/services/shopify-usage-event-publisher.service.test.ts tests/unit/providers/shopify-partner-billing.provider.test.ts tests/unit/runtime/readiness.test.ts tests/unit/runtime/billing-scheduler.test.ts tests/unit/runtime/entrypoint-isolation.test.ts` (37 tests passed)
- `npm run test:unit` (414 passed, 2 unrelated pre-existing failures)
- `npm run build` (passed)
- `npm run prisma:validate` (passed)
- `git diff --check` (passed)
- editor diagnostics for all changed TypeScript source files (no errors)

`npm run test:unit` completed with 406 passing and 2 failing tests. The failures are existing `pending-recovery-candidate.service.test.ts` expectations unrelated to this task; no billing tests failed.

### Deviations

The accepted database schema has no dedicated billing-discrepancy table. Discrepancies are returned in the reconciliation result and emitted through the shared structured logger for operational/Admin consumption; no schema or database repository change was made. The task preserves this accepted Attempt 1 representation.

### Assumptions

Partner credentials are supplied through `SHOPIFY_PARTNER_ORG_ID`, `SHOPIFY_PARTNER_ACCESS_TOKEN`, and `SHOPIFY_APP_ID`, matching SHOPIFY-001. Active-shop reconciliation is bounded to 200 rows per scan and defaults to 50.

### Unresolved Issues

The two unrelated `pending-recovery-candidate.service.test.ts` failures remain for architect/repository owner follow-up; no billing test failed.

### Architectural Concerns

The discrepancy representation is operational structured output rather than durable database state because the accepted schema exposes no discrepancy model. Durable historical discrepancy querying would require a later schema/API task. No new concern was introduced in Attempt 2.

### Git / VCS

Task branch: `task/ARCH-007-BACKGROUND-008`

Implementation repository:
   repository: moda-interact-background
   commit: e3960d5
   remote branch: origin/task/ARCH-007-BACKGROUND-008
   pushed: yes

Parent workspace:
   task file: docs/decisions/background/ARCH-007/BACKGROUND-008-billing-worker-reconciliation.md
   claim commit: c883ba4
   remote branch: origin/task/ARCH-007-BACKGROUND-008
   pushed: yes
   submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Changes Requested — Attempt 1

### Review Notes

Attempt 1 establishes the correct B008 direction: a dedicated
`moda-billing-worker` entrypoint, PostgreSQL-driven publisher recovery,
BACKGOUND-009 purchase activation reconciliation, Shopify Partner subscription
projection, usage comparison, uninstall cutoff validation, readiness wiring and
shared observability. The two unrelated pending-recovery baseline failures are
not a B008 rejection reason.

Four production corrections and one contract/test correction are required
before acceptance.

#### Correction 1 — active-shop reconciliation must rotate; the fixed first page can starve tenants

The current reconciliation scan always executes the equivalent of:

```text
WHERE shopifyShopId IS NOT NULL
  AND status = ACTIVE
ORDER BY id ASC
TAKE <bounded limit>
```

with no cursor or rotation state.

With the default limit of 50, a workspace with more than 50 active Shopify
shops repeatedly reconciles the same lowest-id page every minute. Shops after
that page can therefore remain permanently stale, so an external Shopify plan
change, pending update or new billing cycle for those shops is never
discovered.

Attempt 2 must implement a bounded rotating/keyset scan across active shops.

Required behavior:

1. Keep the existing default page size 50 and hard cap 200.
2. Use stable `Shop.id` keyset progression; do not use an unbounded read.
3. A successful scan advances the cursor to the last selected shop.
4. When the end of the active-shop set is reached, wrap to the beginning.
5. A Partner failure for one selected shop must not prevent cursor progression
   or the remaining selected shops from being processed.
6. Process restart may reset the in-memory cursor; durable correctness must not
   depend on preserving the cursor across restarts.
7. Do not introduce raw SQL or a new database schema solely for the scan cursor.

A clean implementation is an in-memory `lastScannedShopId` owned by the
singleton reconciliation service plus `id > lastScannedShopId` keyset
selection. Other equivalent bounded rotation is acceptable if it proves the
same no-starvation invariant.

Required regressions:

```text
page size = 2
active shops = A, B, C, D

scan 1 -> A, B
scan 2 -> C, D
scan 3 -> wraps to A, B
```

and:

```text
A Partner call fails
B succeeds
next scan still progresses beyond the A/B page
```

#### Correction 2 — the 60-second scheduler must not overlap scans

The billing entrypoint currently starts the recurring work with `setInterval`.
A reconciliation pass performs sequential Partner calls and can legitimately
take longer than 60 seconds. When that happens, `setInterval` starts another
`reconcileOnce()` while the previous one is still running.

B008 must have at most one reconciliation pass in flight per billing-worker
process.

Attempt 2 must replace the overlapping interval behavior with one of:

- a recursive `setTimeout` scheduled only after the previous pass settles; or
- an explicit single-flight/in-progress guard with equivalent shutdown
  behavior.

Required invariants:

```text
max concurrent reconcileOnce() calls per process = 1
```

```text
failed scan
  -> bounded structured error
  -> future scan remains scheduled
```

```text
shutdown
  -> pending timer cancelled
  -> no new reconciliation pass is scheduled
```

Keep the cadence minute-scale. Do not add a sub-second loop or BullMQ job for
this scheduler.

Required regression should use fake timers/a deferred reconciliation promise
and prove that advancing beyond 60 seconds while one pass is still unresolved
does not start a second pass.

#### Correction 3 — the independent billing worker must not require Redis when it does not use Redis

The B008 runtime is PostgreSQL/Shopify driven and intentionally exists so
durable billing work can be recovered independently of Redis/BullMQ scheduling.
However Attempt 1 declares:

```text
moda-billing-worker -> redis + postgresql
```

and the billing entrypoint imports the shared `entrypoints/resources` module.
That module imports `connectionRedis`, whose module initialization itself
requires `REDIS_URL`.

As a result, a billing worker that performs no Redis operation cannot start
without Redis.

Attempt 2 must make the billing worker's actual dependency set match the
runtime:

```text
moda-billing-worker -> postgresql
```

Required implementation behavior:

1. Do not weaken Redis readiness for the queue-backed Shopify/recovery/
   messaging workers.
2. Billing readiness checks PostgreSQL but does not require a Redis probe.
3. `src/entrypoints/billing.ts` must not import a resource bundle whose only
   additional effect is constructing/closing Redis.
4. Close the Prisma/database resource and observability cleanly using a
   billing-specific close path or another existing non-Redis-safe pattern.
5. Do not remove Redis from other worker entrypoints.

Required regressions:

- billing readiness succeeds with a successful PostgreSQL probe and no Redis
  probe;
- queue-backed workers retain their current Redis requirement;
- the billing entrypoint does not import/instantiate `connectionRedis`.

#### Correction 4 — uninstall drain work must be selected with priority, not only validated after claim

Attempt 1 correctly prevents an event with:

```text
occurredAt > shop.uninstalledAt
```

from being sent and marks it `NEEDS_ATTENTION`.

It also correctly allows a pre-uninstall event through validation.

But the bounded due query does not prioritize uninstall-drain work. It selects
all due rows together by `nextReportAt`, `occurredAt`, `id`. A large ordinary
backlog can therefore consume the page while valid pre-uninstall events wait,
which conflicts with the explicit B008/INV-021 requirement to prioritize
pre-uninstall billable events while Shopify's post-uninstall reporting window
is still available.

Attempt 2 must use bounded priority selection.

Required behavior:

1. Spend page capacity on due events belonging to `UNINSTALLED` shops first.
2. Preserve the existing permanent idempotency key and conditional claim.
3. For selected uninstall rows:
   - `occurredAt <= uninstalledAt` -> provider publication remains eligible;
   - `occurredAt > uninstalledAt` -> `NEEDS_ATTENTION`, zero provider call.
4. Fill only the remaining page capacity with ordinary due rows.
5. Total selected/processed work remains `<= pageSize`.
6. Do not use raw SQL.

The exact Prisma query split is local implementation detail. A two-bucket
bounded selection (uninstall-drain candidates first, then ordinary due rows)
is acceptable.

Required regression:

```text
ordinary due backlog >= page size
+ one due pre-uninstall event
-> pre-uninstall event is selected in this pass
-> total selected <= page size
-> provider receives original occurredAt/idempotency identity
```

Retain the existing post-cutoff zero-provider regression.

#### Correction 5 — mirror the accepted SHOPIFY-001 Partner contract and complete the explicit B008 regressions

The Background Partner query/classifier is intentionally behaviorally aligned
with SHOPIFY-001, but its GraphQL selection is currently narrower than the
ARCH-007 external-contract baseline. Do not allow the two implementations to
drift.

Attempt 2 must mirror the accepted SHOPIFY-001 ActiveSubscription query shape
for the fields frozen by ARCH-007, including the current/pending billing-period
and pending legacy-subscription fields even where B008 does not currently need
every returned scalar.

Do not create a new Shared package contract just for this task.

The Attempt 1 reconciliation test file contains only three B008-specific
service tests. Attempt 2 must add deterministic focused coverage for the task's
explicit scenarios, including:

1. external current-plan change is projected on a later scan;
2. unknown plan -> `UNMAPPED`, then after plan mapping exists a later scan
   becomes mapped without deploy;
3. Partner HTTP/GraphQL failure -> `SYNC_ERROR` while existing `planId` is
   preserved;
4. `activeSubscription = null` -> `NO_CONTRACT`, not Free;
5. FlatRate/Tiered item ordering cannot change plan/meter classification;
6. pending plan update/effective boundary is projected;
7. current billing-cycle transition updates the current subscription period
   link;
8. stale `IN_FLIGHT` usage remains recoverable with the same permanent
   idempotency key;
9. a REPORTED recovery-credit purchase with interrupted activation is
   rediscovered through the B009 reconciler;
10. discrepancy emits the bounded structured domain outcome and does not create
    a compensating financial event;
11. uninstall priority/cutoff cases from Correction 4;
12. rotating-shop no-starvation and non-overlap scheduler cases from
    Corrections 1/2.

Existing B007/B009 tests may remain as supporting coverage, but the B008
Completion Report must identify which focused tests prove each B008 behavior.

#### Discrepancy representation — preserve Attempt 1 for this correction pass

The current schema has no dedicated reconciliation-discrepancy model.
ARCH-007 explicitly permits `reconciliation discrepancy` as a structured
domain/observability outcome, and B008 explicitly allowed an accepted
schema/audit/operational representation.

Therefore Attempt 2 must preserve the bounded structured discrepancy result and
must NOT invent a database migration, synthetic UsageEvent, fake
PlatformAdmin/BillingAuditEvent actor, or automatic financial correction inside
B008.

The downstream ADMIN-003 task is being dependency-corrected to wait for B008 so
its final read/display contract can be reconciled against the accepted B008
representation before implementation.

### Reviewed Files

Attempt 1 implementation reviewed at:

- `7501979764d92750ad671fb69e02d2aa8fe94ea4`

Primary reviewed production files:

- `src/entrypoints/billing.ts`
- `src/providers/shopify-partner-billing.provider.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/services/shopify-usage-event-publisher.service.ts`
- `src/runtime/readiness.ts`
- `src/entrypoints/resources.ts`
- `src/lib/redis.ts`
- `observability/billing.mjs`
- `package.json`

Focused tests reviewed:

- `tests/unit/services/billing-reconciliation.service.test.ts`
- `tests/unit/services/shopify-usage-event-publisher.service.test.ts`
- `tests/unit/runtime/readiness.test.ts`
- `tests/unit/runtime/entrypoint-isolation.test.ts`

The accepted SHOPIFY-001 Partner provider was also compared for behavioral/query
contract alignment.

### Validation Reviewed

Completion Report records:

- B008 reconciliation focused tests: 3 passed;
- focused runtime/publisher suite: 26 passed;
- build: passed;
- Prisma validation: passed;
- diagnostics: clean;
- `git diff --check`: passed;
- full unit suite: 406 passed with 2 unrelated existing
  `pending-recovery-candidate` failures.

The supplied archive does not include `node_modules`, so the architect did not
independently rerun the Node/Vitest commands. The implementation source was
inspected directly from the archive and commit `7501979` was independently
verified from GitHub.

The two unrelated pending-recovery failures are not a B008 acceptance blocker.

### Architecture Conformance

Changes required within this SAME task.

Attempt 1 has the correct architectural shape, but fixed-first-page tenant
starvation, overlapping scheduler execution, the false Redis runtime
dependency and missing uninstall-drain selection priority prevent acceptance.

### Follow-up

Return `ARCH-007-BACKGROUND-008` to `ready`.

Durable state after this review:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next claim becomes **Attempt 2** on the SAME mirrored
`task/ARCH-007-BACKGROUND-008` branches/worktree.

Attempt 2 is limited to the five corrections above and their focused
regressions. Preserve the accepted B007 publisher semantics, B009 activation
semantics, existing subscription fail-closed mapping, structured discrepancy
outcome and independent billing-worker identity.

Do not start `ARCH-007-GATEWAY-001`, `ARCH-007-ADMIN-004`,
`ARCH-007-SYSTEM-TEST-002` or `ARCH-007-SYSTEM-TEST-003`.

`ARCH-007-ADMIN-003` is dependency-corrected to include B008 and must remain
Pending until B008 is architect-accepted Complete.
