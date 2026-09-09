---
id: ARCH-008-BACKGROUND-002
architecture_id: ARCH-008
title: Confirm recovery-credit pack entitlements from Shopify meter usage
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 30
executor: copilot
claimed_at: 2026-09-09T16:45:36Z
attempt: 1
depends_on:
  - ARCH-008-BACKGROUND-001
  - ARCH-008-SHOPIFY-001
  - ARCH-007-BACKGROUND-008
  - ARCH-007-BACKGROUND-009
  - ARCH-007-SHOPIFY-001
enables:
  - ARCH-008-ADMIN-001
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008-BACKGROUND-002: Confirm recovery-credit pack entitlements from Shopify meter usage

## Architecture

Canonical: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

## Objective

Stop granting recovery-credit packs from App Events transport success and activate exactly the provider-confirmed aggregate number of current-cycle pack purchases using Partner `activeSubscription` pack-meter usage.

## Architectural invariant

```text
UsageEvent.REPORTED alone MUST NOT activate a RecoveryCreditPurchase.
```

Shopify provider `usage.quantity` is an aggregate confirmation signal. It does not identify a particular App Events idempotency key. Implementation must not claim otherwise.

## Architect reconciliation preflight — completed 2026-09-09

The architecture preflight is complete.

Decision:

```text
DATABASE TASK REQUIRED: NO
SHOPIFY PRODUCER HARDENING REQUIRED: YES
```

The existing schema is sufficient because exact reconciliation can use:

```text
provider current cycle start/end
-> exact BillingPeriod [shopId, periodStart, periodEnd]
-> UsageEvent.billingPeriodId
-> UsageEvent metric/quantity/report state/meter
-> RecoveryCreditPurchase plan/meter/credits snapshots
-> RecoveryCreditPurchase status
```

`ARCH-008-SHOPIFY-001` now guarantees that every **new** pack UsageEvent enters
this flow with a non-null exact current `billingPeriodId` and matching
provider/local cycle boundaries.

Do not create a database migration.

If a legacy/unexpected row with null or wrong cycle identity is encountered,
never infer cycle membership from timestamps. Exclude it from activation and
surface the existing attention/diagnostic outcome.

## Required preflight — do before editing

1. Work only in the launcher-resolved ARCH-008-BACKGROUND-002 task worktree after normal synchronisation.
2. Confirm `ARCH-008-BACKGROUND-001` is Complete and its 409/submission behavior is present.
3. Confirm `ARCH-008-SHOPIFY-001` is Complete and the integrated Shopify
   purchase path now requires exact non-null current-cycle identity.
4. Confirm accepted ARCH-007 capability is present:
   - `src/services/billing-reconciliation.service.ts`;
   - `src/providers/shopify-partner-billing.provider.ts`;
   - recurring billing worker from ARCH-007-BACKGROUND-008;
   - recovery-credit transaction/counter logic from ARCH-007-BACKGROUND-009.
5. Confirm the Partner projection still exposes:
   - current billing cycle start/end;
   - current plan handle;
   - provider usage snapshots with meter handle + quantity.
6. Confirm the Prisma schema still exposes:
   - `BillingPeriod` unique by `shopId + periodStart + periodEnd`;
   - `UsageEvent.billingPeriodId`;
   - `UsageEvent.shopifyEventHandle`;
   - `RecoveryCreditPurchase.shopifyPlanHandleSnapshot`;
   - `RecoveryCreditPurchase.shopifyEventHandleSnapshot`;
   - `RecoveryCreditPurchase.creditsGranted`.
7. If any of those **previously verified** capabilities has disappeared after
   synchronisation, STOP and report source drift to `moda_architect`.
   Do not invent a replacement schema or heuristic.

## Primary files

Expected implementation boundary:

- `moda-interact-background/src/services/shopify-usage-event-publisher.service.ts`
- `moda-interact-background/src/services/recovery-credit-purchase.service.ts`
- accepted ARCH-007 Partner reconciliation service/provider equivalents
- focused recovery-credit/reconciliation unit tests

Do not create a second Partner billing client if ARCH-007 already provides one.

## Required implementation

### Reconciliation orchestration — normative

Replace the current global transport-state purchase activation order:

```text
publishDue()
-> reconcilePending()   # must be removed as an activation source
-> fetch Partner subscriptions
```

with:

```text
publishDue()
-> select bounded rotating shop page
-> for each shop:
     fetch Partner activeSubscription
     apply/sync exact current subscription + BillingPeriod
     resolve exact configured pack meter
     reconcile provider-confirmed pack units for that shop/current cycle/meter
     compare normal recovery usage
```

`RecoveryCreditPurchaseService.reconcilePending()` must no longer activate
`REPORTED` pack purchases merely from local transport state. Remove it from the
billing-worker activation path or refactor it so it cannot grant without an
explicit provider-confirmed budget.

Introduce/reuse one bounded provider-confirmed reconciliation operation with an
input equivalent to:

```text
shopId
billingPeriodId
providerPlanHandle
packMeterHandle
providerUnits
```

The operation must perform ACTIVE matched-unit counting, candidate selection,
ambiguity evaluation and all new grants inside one Serializable transaction so
concurrent reconciliation retries the entire budget calculation.


### A. Remove pack activation from App Events HTTP-success path

In the durable App Events publisher:

- remove the success-path dependency/callback that activates a `RECOVERY_CREDIT_PACK_PURCHASE` solely after `markReported`;
- leave successful UsageEvent transition to `REPORTED` intact;
- leave normal usage publication and retry semantics intact.

After 202:

```text
UsageEvent = REPORTED
RecoveryCreditPurchase = PENDING_BILLING
purchased credit counter unchanged
```

### B. Make RecoveryCreditPurchase activation provider-confirmation-only

Any existing public method such as `activateFromUsageEvent` / `activateForUsageEvent` that activates solely because linked UsageEvent is `REPORTED` must no longer be used as a transport-success activator.

Refactor narrowly so activation occurs only through the provider reconciliation path with an explicit confirmed-unit budget.

Keep the existing exactly-once durable transaction semantics:

- purchase transitions to ACTIVE once;
- `activatedAt` is set once;
- `PURCHASED_RECOVERY_CREDITS.grantedQuantity` is incremented once by that purchase's `creditsGranted` snapshot;
- repeated reconciliation cannot increment again.

Do not revoke ACTIVE purchases automatically if a later provider quantity falls below previously matched units. Surface discrepancy/attention instead.

### C. Provider aggregate calculation

For one **shop + provider current billing cycle + exact pack meter**:

```text
providerUnits = Partner activeSubscription pack usage.quantity
```

Validate before using:

- finite number;
- integer;
- >= 0;
- belongs to exact configured pack meter for the effective plan/current cycle.

If provider quantity is missing/non-finite/negative/non-integer or the meter cannot be identified exactly, activate nothing and route through the existing reconciliation attention/diagnostic outcome.

### D. Local matched/eligible sets

Calculate within the same shop/cycle/meter scope:

```text
alreadyMatchedUnits = count of ACTIVE pack purchases already matched for this provider cycle/meter
```

Each pack purchase represents one provider App Event unit regardless of `creditsGranted`.

Eligible pending candidates must satisfy **all** of:

- `RecoveryCreditPurchase.status == PENDING_BILLING` (or an accepted retryable attention state only if ARCH-007 explicitly allows safe re-entry);
- linked UsageEvent exists;
- linked UsageEvent metric is `RECOVERY_CREDIT_PACK_PURCHASE`;
- linked UsageEvent quantity is exactly `+1`;
- linked UsageEvent `shopifyReportState == REPORTED`;
- candidate belongs to the provider current billing cycle;
- candidate corresponds to the exact pack meter/effective plan configuration being reconciled;
- `RecoveryCreditPurchase.shopifyPlanHandleSnapshot` equals the current provider plan handle;
- `RecoveryCreditPurchase.shopifyEventHandleSnapshot` equals the exact pack meter;
- candidate is not already ACTIVE/cancelled.

Do not count a merely-created local purchase whose App Event was never submitted.

### E. Confirmed unit budget

```text
confirmedDelta = providerUnits - alreadyMatchedUnits
```

Rules:

1. `confirmedDelta <= 0`
   - activate no new purchases;
   - if `< 0`, surface provider-under-local discrepancy/attention; do not revoke.
2. `confirmedDelta == eligibleCandidateCount`
   - all eligible candidates are provider-covered; activate all deterministically.
3. `confirmedDelta > eligibleCandidateCount`
   - activate all eligible candidates only;
   - surface provider-over-local discrepancy for unmatched provider units;
   - do not fabricate local purchases.
4. `0 < confirmedDelta < eligibleCandidateCount`
   - provider confirms only a subset; apply the ambiguity rule below.

### F. Ambiguous partial matching rule

Shopify does not expose which App Event produced an aggregate unit. Therefore when only a subset is confirmed:

- order equivalent candidates deterministically by `createdAt ASC`, then `id ASC`;
- **but** do not arbitrarily choose across candidates whose entitlement value/configuration differs.

Define an equivalent candidate group as candidates that share all provider-relevant/configuration snapshots required to make one unit interchangeable, including at minimum the same effective pack-meter identity and same `creditsGranted` snapshot.

For partial confirmation:

- if every eligible candidate is equivalent, activate the earliest `confirmedDelta` candidates by `createdAt`, then `id`;
- if the partial boundary crosses candidates with different `creditsGranted` or different pack/meter/plan snapshots, **activate none from the ambiguous subset**, surface `NEEDS_ATTENTION`/reconciliation discrepancy, and require operator resolution;
- never choose the most valuable/least valuable/newest candidate heuristically.

If current accepted state already records a stronger deterministic provider correlation, use it only if it comes from a supported Shopify API and is documented in Completion Report. Do not invent correlation from request timing.

### G. Reconciliation replay and concurrency

Reuse the accepted ARCH-007 transaction/isolation/locking approach. The implementation must remain correct when:

- two billing reconciliation runs overlap;
- reconciliation is retried after process failure;
- provider quantity has not changed;
- a purchase is activated by the other transaction first.

The final durable counter must equal the sum of ACTIVE purchase `creditsGranted` snapshots, never double-counting the same purchase.

### H. Normal recovery isolation

Do not gate ordinary checkout recovery completion, customer messaging or paid-recovery UsageEvent creation on Partner reconciliation. Only **advance pack entitlement grant** waits for provider aggregate confirmation.

## Required tests

Add/adjust focused tests proving:

1. 202/`REPORTED` leaves pack PENDING and counter unchanged.
2. Provider quantity increment of 1 activates exactly one equivalent eligible pending purchase.
3. Re-running same provider quantity grants nothing twice.
4. Provider increment 2 activates two equivalent candidates deterministically.
5. Provider quantity lower than ACTIVE matched units revokes nothing and surfaces discrepancy.
6. Provider quantity greater than local eligible + active units fabricates nothing and surfaces discrepancy.
7. Partial confirmation across candidates with different `creditsGranted` fails closed for the ambiguous subset.
8. Non-REPORTED candidate is never activated.
9. Wrong cycle/wrong meter candidate is never consumed by current reconciliation.
10. Concurrent/replayed reconciliation remains exactly once.
11. Normal recovery path remains independent of provider reconciliation availability.

## Out of Scope / MUST NOT

- No database migration unless architect creates a separate database task after a reported gap.
- No Shopify app UI/plan-selection changes.
- No App Events endpoint redesign.
- No Admin layout work.
- No automatic credit clawback.
- No synthetic “provider confirmed event id” field based on local assumptions.
- No date-window approximation when durable billing-cycle identity is missing.
- No cross-repository edits.

## Acceptance Criteria

- [ ] Transport success no longer activates a recovery-credit purchase.
- [ ] Provider current-cycle exact pack-meter quantity is required for activation.
- [ ] Aggregate matching never claims per-event Shopify confirmation.
- [ ] Exact provider-confirmed unit budget is respected.
- [ ] Equivalent partial candidates use deterministic `createdAt`, then `id` ordering.
- [ ] Non-equivalent ambiguous partial matching fails closed.
- [ ] ACTIVE purchase credit is granted exactly once under replay/concurrency.
- [ ] Provider under/over-count discrepancies are surfaced without destructive correction/fabrication.
- [ ] Normal recovery remains independent of reconciliation latency/failure.
- [ ] No schema/cross-repository change is introduced silently.

## Validation — run from `moda-interact-background`

Run exact focused unit tests for changed services first, for example:

```bash
npx vitest run \
  tests/unit/services/recovery-credit-purchase.service.test.ts \
  tests/unit/services/billing-reconciliation.service.test.ts \
  <any-new-focused-test>
```

Use actual current filenames if accepted ARCH-007 uses different names.

Then run:

```bash
npm run test:unit
npm run build
npm run prisma:validate
git diff --check
```

Do not invent a lint command if none exists.

## Stop / return rule

If preflight reveals a missing durable cycle/meter identity, return `blocked`/architectural concern with exact evidence instead of implementing a heuristic.

Otherwise, after successful implementation/validation:

1. complete Completion Report;
2. set status `review`;
3. return to `moda_architect`;
4. STOP.

Do not begin ADMIN-001.

## Completion Report

### Status

Blocked — preflight source drift requires architect coordination.

### Files Changed

None. The implementation worktree remains clean; no implementation source was modified.

### Work Completed

Completed the required task routing, dependency verification, dedicated worktree setup, fresh synchronization, and ARCH-008 preflight.

### Validation Results

Preflight evidence:

- Parent task worktree synchronized from `origin/main` to `0d12fe8` and is clean.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-008-BACKGROUND-002` is clean at `9abae33`, branch `task/ARCH-008-BACKGROUND-002`.
- The resolver-selected implementation worktree is at commit `9abae33` from `origin/main` and contains only `prisma/schema.prisma`; it has no `database/prisma/schema.prisma`, even though `package.json` and `prisma.config.ts` reference `database/prisma/schema.prisma`.
- The canonical Background source checkout is detached at commit `125f1a9` and does contain `database/prisma/schema.prisma` with `Subscription`, `BillingPeriod`, `UsageEvent`, and `RecoveryCreditPurchase`.
- The canonical checkout is not a valid replacement implementation base for this task: `125f1a9` is not an ancestor of `origin/main` and its diff removes the accepted reconciliation service/provider surface present at `9abae33`.

### Deviations

Implementation was not started because the task's required preflight failed. No migration, schema repair, heuristic, or cross-repository change was introduced.

### Assumptions

None.

### Unresolved Issues

`ARCH-008-BACKGROUND-002` cannot implement provider-confirmed reconciliation until `moda_architect` reconciles the stale `origin/main` implementation base with the canonical schema-bearing checkout and publishes an authorized task branch. The task requires stopping rather than copying files, switching a shared checkout, creating a replacement schema, or inventing a migration.

### Architectural Concerns

Source/worktree drift: the canonical Background checkout contains the required durable schema at `125f1a9`, while the resolver-selected implementation branch is based on stale `origin/main` `9abae33` and lacks that schema path while retaining service references to it. This requires architect coordination to publish/reconcile the correct implementation base before work can safely proceed.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
