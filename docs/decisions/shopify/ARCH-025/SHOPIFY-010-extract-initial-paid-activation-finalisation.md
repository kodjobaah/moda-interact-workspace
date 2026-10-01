---
id: ARCH-025-SHOPIFY-010
architecture_id: ARCH-025
title: Extract initial Paid activation finalisation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-SHOPIFY-009
enables:
  - ARCH-025-SHOPIFY-011
created: 2026-10-01
updated: 2026-10-01
---

# Extract initial Paid activation finalisation

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Move only the special initial Paid durable finalisation branch out of `syncSubscription()` into the existing `SubscriptionActivationService`, preserving its strict Shop lock, exact pending-token/cycle/configuration validation and atomic entitlement creation.

## Context

After SHOPIFY-006, activation intent/retry/Free completion already has one owner, but `syncSubscription()` still contains the higher-risk initial Paid final commit. Extracting that branch separately before the general sync coordinator keeps the final task bounded and places all initial activation semantics together.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-activation.service.ts
app/services/billing/subscription-locks.ts
tests/unit/services/billing/subscription-activation.service.test.ts
```

No new service file is required unless implementation demonstrates a concrete cycle dependency; default is to extend the existing activation service.

## Out of Scope

- normal provider-to-local sync branches.
- changing Paid activation rules or configuration requirements.
- modifying provider API calls.
- edits to frozen `billing.service.test.ts`.

## Requirements

### Common ARCH-025 invariants

- Preserve `BillingService` constructor compatibility: `new BillingService(provider, database, dispatchTranslation)`.
- Preserve every existing public `BillingService` method signature and the `billingService` singleton export.
- Preserve all current public exports from `app/services/billing/billing.service.ts`; moved symbols must be compatibility re-exported from that file.
- Do not change routes/callers as part of extraction.
- Extracted modules MUST NOT import `billing.service.ts`; dependency direction is façade/coordinator -> collaborator.
- Do not change billing rules, error codes/strings, transaction boundaries, lock order, provider call order, retry semantics, idempotency, CAS/fencing, entitlement arithmetic or durable lifecycle state.
- Do not add provider/API calls or database round trips to the equivalent path solely because code moved.
- Extracted collaborator constructors must be side-effect-free: store/wire dependencies only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during `new BillingService(...)`; the frozen suite constructs the façade with many partial test doubles.
- This is move-only refactoring: do not remove, coalesce, reorder or otherwise optimise away an existing provider/database read, write, lock or transaction as an incidental cleanup. Any intentional I/O change is outside this task.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The proven pre-task failure set is `ARCH025-TEST-001`; the task must introduce no additional failing identifier.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — exact branch boundary inside the caller-owned sync transaction

Move only the body of the branch currently selected when an `expectedInitialSelection` for `PAID_METERED` matches the provider result and the durable pending initial intent. The remaining `syncSubscription()` must still open the existing outer transaction, acquire the shared `ShopSettings -> Subscription` lock, reread `existingSubscription`, reject a stale expected token, and determine whether the initial-Paid branch applies.

The activation finalisation method MUST accept the existing `Prisma.TransactionClient` and execute inside that **same already-open transaction**. It MUST NOT call `database.$transaction(...)`, create a nested/second transaction, move branch detection outside the lock, or commit independently.

### R2 — preserve full lock order and durable reread

Move `lockShopForInitialPaidActivation` into the shared `subscription-locks.ts` owner created by SHOPIFY-006, retaining its exact SQL. For this branch the effective lock order must remain:

```text
ShopSettings FOR UPDATE
Subscription FOR UPDATE
Shop FOR UPDATE
```

The first two locks are already held by the caller before finalisation is invoked. The finaliser acquires the Shop lock and retains all current durable rereads/identity checks. Do not duplicate lock SQL in the activation service.

### R3 — preserve fail-closed validations

Keep current behaviour for:

```text
missing/mismatched pending plan identity
missing provider cycle
Paid trial
missing/invalid included allowance
missing required provider usage meter
inactive/mismatched plan
existing conflicting/closed BillingPeriod
included counter conflicts
invalid lifetime-Free policy
```

The same current `SYNC_ERROR`/`lastSyncErrorCode` results and no-write/conflict semantics must remain. Preserve the current error-selection order exactly: missing/unexposed usage meter -> `MISSING_USAGE_METER`; supported meter plus unsupported Paid trial -> `UNSUPPORTED_PAID_TRIAL`; other invalid configuration/conflict -> `INVALID_PAID_PLAN_CONFIGURATION`. Do not strengthen existing counter/lifetime validation beyond what this branch currently checks.

### R4 — preserve atomic success commit

Successful finalisation must still atomically create/reuse the exact BillingPeriod, included counter and lifetime-Free counter as currently required, clear the pending selection, set ACTIVE projection fields and set the exact drain-window `nextReconcileAt`.

### R5 — no provider work and no generic-projection substitution

The service receives already obtained provider subscription evidence; it must not perform a new Shopify call. Do not replace the initial-Paid branch with SHOPIFY-001 `ensureMappedCurrentBillingPeriodProjection`: the current initial-Paid branch has intentionally different validation/conflict semantics and must remain exact.

### R6 — preserve stale-token and replay boundary

A stale `expectedInitialSelection` remains a no-op before the finaliser runs. Existing BillingPeriod/counter/lifetime rows are reused or rejected using the current branch-specific predicates; do not add arithmetic checks to the existing included counter or new validation of an existing lifetime counter as incidental cleanup.

## Work Items

- [ ] Extend `SubscriptionActivationService` with one bounded initial-Paid finalisation method that accepts the caller-owned `Prisma.TransactionClient`.
- [ ] Move `lockShopForInitialPaidActivation` into `subscription-locks.ts` and preserve full `ShopSettings -> Subscription -> Shop` lock order.
- [ ] Move only the identified branch body from `syncSubscription()`; keep outer transaction, stale-token fencing, existing-subscription reread and branch detection in sync.
- [ ] Extend focused activation tests for exact successful period/counters, Shop lock, all fail-closed cases, replay preservation and drain-window schedule.
- [ ] Prove no additional provider/database work was introduced around the branch.
- [ ] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Internal activation method accepts the caller-owned `Prisma.TransactionClient`, already obtained provider Subscription evidence, expected activation token, existing locked Subscription facts and `now`/other exact inputs needed by the current branch. It does not own or open a transaction and is not exposed to routes.

## Dependencies

- `ARCH-025-SHOPIFY-009`

## Enables

- `ARCH-025-SHOPIFY-011`

## Acceptance Criteria

- [ ] Initial Paid branch body no longer lives in `syncSubscription()`, but the existing sync transaction remains the owner and no nested/second transaction is introduced.
- [ ] Full `ShopSettings -> Subscription -> Shop` lock order and all strict initial Paid validation/entitlement semantics are unchanged.
- [ ] Activation service performs no provider call.
- [ ] `syncSubscription()` still exposes exactly the same public behaviour.
- [ ] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)"` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [ ] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [ ] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001`
- [ ] `npm test -- tests/unit/services/billing/subscription-activation.service.test.ts` passes the new focused capability tests
- [ ] `npm test` introduces no new failures
- [ ] `npm run typecheck`
- [ ] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-activation.service.ts app/services/billing/subscription-locks.ts tests/unit/services/billing/subscription-activation.service.test.ts`
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Do not use SHOPIFY-001 generic BillingPeriod projection to replace this branch. The finaliser is a transaction-participant, not a transaction owner. Preserve exact validation ordering and existing branch-specific permissiveness as well as strictness; “cleaning up” the predicates is a behaviour change.


## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
