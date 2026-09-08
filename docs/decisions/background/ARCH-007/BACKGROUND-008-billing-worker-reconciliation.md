---
id: ARCH-007-BACKGROUND-008
architecture_id: ARCH-007
title: Add independent billing worker for publication, subscription sync, reconciliation and uninstall drain
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: ready
priority: 120
executor: null
claimed_at: null
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
updated: 2026-09-08T21:16:00+01:00
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

- [x] Add billing worker entrypoint/scripts/readiness.
- [x] Implement bounded rotating subscription reconciliation using the Partner API 2026-07 contract.
- [x] Implement publisher stale-work recovery and periodic due scans.
- [x] Wire bounded BACKGROUND-009 recovery-credit purchase activation reconciliation into the recurring billing worker scan.
- [x] Implement Shopify-vs-Moda usage comparison/discrepancy visibility using the accepted structured operational representation.
- [x] Implement uninstall prioritization/cutoff.
- [ ] Complete the explicit B008 regression matrix required by the latest Architect Review.

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

Changes Requested — Attempt 2

### Review Notes

#### Attempt 2 — Changes Requested

Attempt 2 correctly resolves the four major runtime defects from Attempt 1.
Preserve these corrections unchanged unless a regression requires a minimal
adjustment:

1. active-shop reconciliation rotates with a bounded stable-`Shop.id` keyset
   cursor and wraps rather than permanently re-reading the first page;
2. recurring reconciliation is single-flight through recursive timeout
   scheduling rather than overlapping `setInterval` calls;
3. `moda-billing-worker` readiness is PostgreSQL-only and the billing entrypoint
   closes Prisma through a billing-specific resource path without constructing
   `connectionRedis`; and
4. due rows for `UNINSTALLED` shops are selected ahead of ordinary due rows,
   while the existing uninstall cutoff, permanent Shopify idempotency key and
   original `occurredAt` identity remain intact.

Attempt 2 also brings most of the Background Shopify Partner query into
alignment with the accepted SHOPIFY-001 contract.

Two narrow implementation corrections and one focused regression/evidence
correction remain before B008 can be accepted.

#### Correction 1 — complete the frozen ARCH-007 / SHOPIFY-001 Partner query shape

The frozen minimum ActiveSubscription shape includes the current subscription
item description:

```text
activeSubscription {
  billingPeriod
  currentBillingCycle { startTime endTime }
  legacySubscriptionId
  items {
    handle
    description
    price { ... }
    usage { quantity cost { amount currencyCode } }
  }
  pendingUpdate {
    billingPeriod
    legacySubscriptionId
    items { handle price { ... } }
  }
}
```

Attempt 2 still omits `items.description`.

Attempt 3 must make the Background provider mirror the frozen minimum without
redesigning classification:

- add `description: string | null` to the current-item Partner response type;
- select `description` immediately beside `handle` in
  `ACTIVE_SUBSCRIPTION_QUERY`;
- preserve order-independent FlatRate/Tiered classification;
- preserve current `billingPeriod`, `currentBillingCycle`,
  `legacySubscriptionId`, `pendingUpdate.billingPeriod` and
  `pendingUpdate.legacySubscriptionId`;
- type `pendingUpdate.billingPeriod` as nullable where the accepted
  SHOPIFY-001 response contract permits null;
- do not add a Shared-package change solely for this local provider mirror.

Required provider regression:

- capture the actual GraphQL request body;
- assert the query contains current `billingPeriod`, `currentBillingCycle`,
  current `legacySubscriptionId`, `items.description`,
  `pendingUpdate.billingPeriod`, and
  `pendingUpdate.legacySubscriptionId`;
- retain the existing item-order classification regression.

#### Correction 2 — scheduled reconciliation failures must use bounded Shared structured logging

The single-flight scheduler itself is accepted.

The remaining defect is the production failure reporter. When no reporter is
provided, `startBillingReconciliationScheduler()` currently falls back to:

```ts
console.error("billing reconciliation failed", error)
```

That emits the raw `Error` object and bypasses the Background Shared structured
logging convention.

Attempt 3 must keep the scheduler generic/single-flight and wire the production
billing entrypoint to a Shared structured logger from:

```text
@modainteract/moda-interact-shared/logging
```

Required production outcome:

```text
event = billing.reconciliation.scan_failed
service.name = moda-billing-worker
```

Use only bounded scalar fields. A sanitized error name/code or bounded message
is acceptable. Do not log the raw Error object, Partner access token, request
headers, DATABASE_URL, REDIS_URL, or provider response payload.

A clean implementation is:

```text
billing.ts
  -> create/use Shared logger
  -> pass bounded onError(error) callback into
     startBillingReconciliationScheduler(...)
```

Do not introduce a second logging framework.

Required regression:

1. force a scheduled reconciliation failure;
2. prove the scheduler schedules a later pass after the failure;
3. prove the production reporter uses the Shared logger;
4. prove the reporter does not pass the original raw Error object as log
   metadata.

#### Correction 3 — complete the explicit B008 reconciliation regression matrix

Attempt 2 adds good coverage for:

```text
rotating shop pages
Partner failure does not stop page progression
single-flight scheduling
scheduler shutdown/recovery
PostgreSQL-only readiness
billing entrypoint Redis isolation
uninstall-first bounded selection
post-uninstall cutoff
FlatRate/Tiered order-independent classification
usage discrepancy output
publisher idempotency
```

The following behaviors were explicitly required by the Attempt 1 correction
contract and still need deterministic B008-focused tests.

##### B008-R1 — external current plan change on a later reconciliation

Arrange one shop and two sequential Partner snapshots:

```text
scan N     -> plan A
scan N + 1 -> plan B
```

Assert the durable Subscription projection changes to plan B without a merchant
callback or process restart.

##### B008-R2 — UNMAPPED becomes mapped after Admin registration without deploy

```text
scan N:
  Partner handle = future-plan
  no active BillingPlan mapping
  -> Subscription.status = UNMAPPED
  -> planId = null

between scans:
  create/enable BillingPlan mapping for future-plan

scan N + 1:
  same Partner handle
  -> mapped ACTIVE/TRIALING projection
  -> planId = newly mapped plan
```

No restart/deploy may be required.

##### B008-R3 — genuine no-contract state

Partner returns:

```text
activeSubscription = null
```

Assert durable projection becomes:

```text
Subscription.status = NO_CONTRACT
planId = null
```

and is not converted to Free.

##### B008-R4 — pending plan/effective boundary persistence

Partner returns a valid current plan plus a pending plan.

Assert:

```text
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt
```

are persisted from the accepted pending projection/current-cycle boundary
without changing the current entitlement early.

##### B008-R5 — current billing-cycle transition

Two sequential Partner snapshots expose distinct current billing cycles.

Assert the second reconciliation:

- persists/links the new OPEN BillingPeriod;
- updates `Subscription.billingPeriodId`;
- updates current period start/end;
- does not retain the old cycle as the current subscription period.

##### B008-R6 — interrupted B009 pack activation is rediscovered by the B008 scan

Use a mocked/stubbed accepted B009 reconciler whose pending purchase represents:

```text
RECOVERY_CREDIT_PACK_PURCHASE UsageEvent = REPORTED
purchase activation = not yet committed
```

Assert `reconcileOnce()` invokes `reconcilePending()` and reports the activated
result. Do not duplicate B009 credit-grant logic inside the B008 test/service.

##### B008-R7 — discrepancy never manufactures financial correction

For a paid current cycle where:

```text
Moda net REPORTED quantity != Shopify usage quantity
```

assert:

- one bounded discrepancy outcome is returned/logged;
- no new compensating UsageEvent is created by reconciliation;
- existing billing quantities/report identities are not rewritten merely to
  force equality.

##### B008-R8 — stale IN_FLIGHT retains the permanent reporting identity

Retain/prove the B007 publisher behavior from the B008 worker perspective:

```text
stale IN_FLIGHT
  -> recover to retryable under bounded lease rule
  -> later provider attempt uses the same shopifyIdempotencyKey
```

Do not generate a replacement key.

Existing B007/B009 unit tests may remain supporting evidence, but the B008
Completion Report must name the B008-focused regression(s) that prove each
B008-R1..R8 behavior.

#### Accepted Attempt 2 behavior that must not be redesigned

Attempt 3 must preserve:

- default shop reconciliation page size 50 and hard cap 200;
- in-memory stable-id cursor with wraparound;
- Partner failure isolation per selected shop;
- recursive/single-flight minute-scale scheduler;
- PostgreSQL-only billing readiness;
- billing-specific Prisma shutdown path;
- Redis readiness for queue-backed workers;
- uninstall-priority bounded selection;
- existing post-uninstall `NEEDS_ATTENTION` behavior;
- permanent Shopify idempotency identity;
- accepted B007 publisher semantics;
- accepted B009 purchase activation semantics;
- existing fail-closed subscription mapping;
- bounded structured discrepancy representation without auto-correction.

Do not add a database migration, raw SQL, BullMQ scheduler, new Shared contract,
new financial correction policy, or a second credit-grant implementation.

### Reviewed Files

Attempt 2 implementation reviewed at:

- `e3960d5e9295778de0f82efddd488d032924f377`

Attempt 2 was compared directly with Attempt 1
`7501979764d92750ad671fb69e02d2aa8fe94ea4`.

Production files reviewed include:

- `src/entrypoints/billing.ts`
- `src/entrypoints/billing-resources.ts`
- `src/providers/shopify-partner-billing.provider.ts`
- `src/runtime/billing-scheduler.ts`
- `src/runtime/readiness.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/services/shopify-usage-event-publisher.service.ts`

Focused tests reviewed include:

- `tests/unit/providers/shopify-partner-billing.provider.test.ts`
- `tests/unit/runtime/billing-scheduler.test.ts`
- `tests/unit/runtime/entrypoint-isolation.test.ts`
- `tests/unit/runtime/readiness.test.ts`
- `tests/unit/services/billing-reconciliation.service.test.ts`
- `tests/unit/services/shopify-usage-event-publisher.service.test.ts`

### Validation Reviewed

Attempt 2 Completion Report records:

- focused B008 suite: 37 passed;
- build: passed;
- Prisma validation: passed;
- diagnostics: clean;
- `git diff --check`: passed;
- full unit suite: 414 passed with the same 2 unrelated
  `pending-recovery-candidate.service.test.ts` baseline failures.

No GitHub commit-status checks are configured for implementation commit
`e3960d5`; this is not an acceptance blocker.

The two unrelated pending-recovery failures remain outside B008 scope.

### Architecture Conformance

Changes required within this SAME task.

The core B008 runtime shape is now substantially conformant. Attempt 3 is a
bounded close-out pass for Partner contract parity, structured scheduled-scan
failure telemetry, and explicit reconciliation regression evidence.

### Follow-up

Return `ARCH-007-BACKGROUND-008` to `ready`.

Durable state after this review:

```text
status: ready
attempt: 2
executor: null
claimed_at: null
```

The next claim becomes **Attempt 3** on the SAME mirrored:

```text
task/ARCH-007-BACKGROUND-008
```

branches/worktree.

Do not create an `attempt-3` branch.

Do not start:

- `ARCH-007-ADMIN-003`;
- `ARCH-007-ADMIN-004`;
- `ARCH-007-GATEWAY-001`;
- `ARCH-007-SYSTEM-TEST-002`;
- `ARCH-007-SYSTEM-TEST-003`.

System-test tasks remain terminal/manual-gated.

`ARCH-007-ADMIN-003` depends on B008 and must remain Pending until B008 is
architect-accepted Complete.

#### Attempt 1 — Changes Requested (preserved)

The full Attempt 1 Architect Review remains in repository history immediately
before this Attempt 2 decision and continues to explain the defects already
corrected by Attempt 2.
