---
id: ARCH-025-SHOPIFY-008
architecture_id: ARCH-025
title: Extract recovery-credit purchase request workflow
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-SHOPIFY-007
enables:
  - ARCH-025-SHOPIFY-009
created: 2026-10-01
updated: 2026-10-02
---

# Extract recovery-credit purchase request workflow

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract `requestRecoveryCreditPack` and its provider-evidence/idempotency helpers into a dedicated purchase-request service without moving it into the already-large purchase-management/refund service.

## Context

Purchase initiation is a command workflow with provider-before/provider-after verification, Serializable transaction semantics and single-flight/idempotency rules. `recovery-credit-purchase-management.service.ts` already owns history/refunds and is approximately 867 lines; absorbing initiation there would recreate the maintainability problem.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/recovery-credit-purchase-request.service.ts              # new
tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts  # new
```

Existing `recovery-credit-purchase-management.service.ts` is read-only/out-of-scope for this task.

## Out of Scope

- refund/history management.
- purchase activation/reconciliation owned elsewhere.
- changing Shopify usage event format or idempotency key.
- billing-page read logic.
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

### R1 — move exact command

Move implementation ownership of `requestRecoveryCreditPack(shopId, intent, purchaseId, eventHandle)` and directly associated constants/helpers:

```text
RECOVERY_CREDIT_PURCHASE_INTENT
RECOVERY_CREDIT_PACK_UNAVAILABLE_DURING_TRANSITION
isSafeNonNegativeNumber
purchase ID validation
provider-before evidence validation
executable provider subscription selection
provider evidence equality
unresolved purchase message
same-id unique-race handling
```

### R2 — preserve provider/transaction boundary

Shopify/provider verification that currently occurs before the Prisma write transaction MUST remain before it. No provider/network call may move into the transaction.

### R3 — preserve transaction and locking

Keep Serializable isolation, Subscription locking order, single-flight lookup, current BillingPeriod/cycle validation and exact durable revalidation after provider verification.

### R4 — preserve provider evidence fencing and read count

The provider snapshot used for admission must still be revalidated against live/durable state as today. Preserve the current **two** `getSubscriptionLifecycleSnapshot(...)` reads before the write transaction (initial evidence, then provider revalidation), with no additional provider snapshot read. A changed lifecycle/configuration/cycle/meter must fail closed without creating a usage event.

### R5 — reuse projection and catalogue owners without changing rereads

Use SHOPIFY-001 `hasDurableBillingPeriod`, `hasMatchingBillingCycle` and `deriveBillingPeriodPhase`; do not duplicate cycle logic. Use SHOPIFY-002 `readMerchantPricingPlan`; preserve the current first catalogue read and the second **current catalogue reread** after provider revalidation so a changed `creditsGrantedPerUnit` still fails closed. Do not cache/coalesce these two reads.

### R6 — preserve idempotency

Keep client purchase ID validation, existing-purchase replay, unresolved offer/provider-context blocking, deterministic Shopify usage idempotency key and P2002 same-ID recovery semantics.

### R7 — ignore undeclared client-supplied pricing/plan payloads

The frozen suite deliberately invokes the JavaScript method with a fifth attacker-controlled argument containing plan/pricing/meter fields. `BillingService.requestRecoveryCreditPack` and its delegate must continue using only the four declared inputs (`shopId`, `intent`, `purchaseId`, `eventHandle`) and must not forward, inspect or trust additional runtime arguments.

## Work Items

- [x] Create `RecoveryCreditPurchaseRequestService` with provider, Prisma, SHOPIFY-001 cycle helpers and SHOPIFY-002 catalogue collaborator dependencies.
- [x] Move request command/helpers and leave façade delegate.
- [x] Do not edit purchase-management/refund service.
- [x] Add focused tests proving exactly two provider lifecycle snapshot reads, two-stage catalogue verification, provider-before ordering, Serializable/lock order, exact cycle, duplicate replay, unresolved blocking, changed provider/config evidence, invalid IDs and unique-race recovery.
- [x] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Consumes existing `BillingProvider`, Shared `createShopifyUsageIdempotencyKey`/provider-context identity and existing Prisma purchase/usage-event models. No new queue/provider contract.

## Dependencies

- `ARCH-025-SHOPIFY-007`

## Enables

- `ARCH-025-SHOPIFY-009`

## Acceptance Criteria

- [x] Purchase initiation is owned by a dedicated request service.
- [x] Existing purchase-management/refund service is not enlarged by this refactor.
- [x] Provider-before/provider-after evidence, exact two provider snapshot reads, catalogue reread and transaction ordering are unchanged.
- [x] Idempotency/single-flight behaviour is unchanged.
- [x] Extra runtime/client-supplied plan/pricing arguments remain ignored and cannot influence the persisted usage event or purchase.
- [x] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [x] `npm run prisma:generate` passed.
- [x] Frozen test SHA-256 is `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; `git diff -- tests/unit/services/billing.service.test.ts` is empty.
- [x] Frozen façade suite: 195 passed, 18 failed; all 18 failures match `ARCH025-TEST-001`.
- [x] Focused purchase-request suite: 10 passed.
- [x] Full `npm test`: 1,001 passed, 24 failed, 33 skipped across 94 files; all 24 failures match `ARCH025-TEST-001`.
- [x] `npm run typecheck` passed.
- [x] Task-scoped ESLint passed (existing TypeScript parser compatibility warning only).
- [x] `npm run build` passed (existing large-chunk warning).
- [x] `git diff --check` passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

Do not generalise this into a command bus. Keep current error messages because billing routes/tests may display/assert them. A tiny service-local P2002 predicate is acceptable; do not import plan-resolution internals solely to share that mechanical check.


## Completion Report

### Status

Review

### Files Changed

Implementation repository (`moda-interact`):

- `app/services/billing/billing.service.ts`
- `app/services/billing/recovery-credit-purchase-request.service.ts` (new)
- `tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts` (new)

Parent workspace: this task report only.

### Work Completed

- Moved the recovery-credit request workflow and its provider-evidence, request validation, unresolved purchase, idempotency and unique-race helpers into `RecoveryCreditPurchaseRequestService`; the four-argument `BillingService` method delegates without forwarding extra runtime arguments.
- Reused `BillingPlanResolutionService.readMerchantPricingPlan` and SHOPIFY-001 billing-cycle helpers; retained the provider-before transaction boundary, two lifecycle snapshot reads, two catalogue reads, Serializable isolation, Subscription lock, single-flight lookup and durable transaction reread.
- Left purchase-management/refund ownership and all routes unchanged.
- Added ten focused tests covering two provider snapshots/two catalogue reads, provider-before ordering, Serializable/lock order, exact billing-cycle identity, frozen lifecycle, provider/catalogue changes, existing replay, unresolved blocking, invalid IDs, same-ID P2002 recovery and ignored extra pricing payloads.

### Validation Results

Passed: Prisma client generation, focused purchase-request suite (10/10), typecheck, task-scoped ESLint, production build, frozen test hash/diff verification and `git diff --check`.

The frozen façade suite ran 213 tests: 195 passed and 18 failed; all 18 identifiers match the existing `ARCH025-TEST-001` baseline. Full `npm test` ran 1,058 tests across 94 files: 1,001 passed, 24 failed and 33 skipped. The 24 failure identifiers match the documented 18 frozen plus six unrelated full-suite baseline failures; no new failing identifier was observed.

ESLint emitted the existing TypeScript parser compatibility warning; the production build emitted the existing large-chunk warning. Neither command failed.

### Deviations

The fresh implementation worktree initially lacked installed dependencies; `npm ci` installed from the committed lockfile before Prisma generation and validation. No task scope or behavior deviations.

### Assumptions

None.

### Unresolved Issues

None task-introduced. The documented `ARCH025-TEST-001` failures remain unchanged.

### Architectural Concerns

None identified. Provider/network verification remains outside the Prisma transaction; shared cycle and catalogue ownership are reused without changing read counts; the request service does not import the façade.

### Launcher and VCS Evidence

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-008
parent branch: task/ARCH-025-SHOPIFY-008
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-008
implementation branch: task/ARCH-025-SHOPIFY-008
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recorded database submodule commit: cfeeb12456b4e05067a96857a8c47837d7e33bbd
launcher claim commit: 8eb3dda29603ce6a1e3636872c3c83825bfbb008
implementation commit: 96f7db9e437b9732ba0f2b4186fa9306e72dec97 (pushed to origin/task/ARCH-025-SHOPIFY-008)
```

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 accepted.

The recovery-credit purchase request extraction is a move-only refactor. Direct comparison with the pre-task `BillingService.requestRecoveryCreditPack(...)` implementation confirms the complete command body is unchanged apart from ownership/delegation. Provider verification remains outside the Prisma transaction; exactly two lifecycle snapshots and two catalogue reads remain on the successful path before the Serializable transaction; the Subscription row is locked before unresolved-purchase and durable-state revalidation; and no provider/network operation occurs inside the transaction.

The four-argument `BillingService.requestRecoveryCreditPack(shopId, intent, purchaseId, eventHandle)` compatibility method delegates only those four declared arguments. The fifth attacker-controlled runtime argument exercised by the frozen regression suite is not forwarded or inspected and therefore cannot influence persisted plan, meter, credits or pricing evidence.

Existing-purchase replay, same-shop validation, unresolved same-offer blocking, exact BillingPeriod/cycle/phase validation, provider-before evidence capture, provider-context identity, provider/catalogue change fencing, deterministic Shopify usage idempotency, usage-event/purchase write ordering and P2002 same-ID recovery semantics are unchanged. `recovery-credit-purchase-management.service.ts` and all routes remain untouched.

Implementation commit reviewed: `96f7db9e437b9732ba0f2b4186fa9306e72dec97`.
Parent Completion Report reviewed: `42652f3bf02ad7443b20073e62551f41050668f9`.

### Reviewed Files

- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/services/billing/recovery-credit-purchase-request.service.ts`
- `moda-interact/tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts`
- `docs/decisions/shopify/ARCH-025/SHOPIFY-008-extract-recovery-credit-purchase-request-service.md`
- `docs/decisions/shopify/ARCH-025/_index.md`
- `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`
- `docs/development-baseline.md`

### Validation Reviewed

- Focused purchase-request suite: 10/10 passed.
- Frozen façade SHA-256 remains `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; frozen test diff is empty.
- Frozen façade suite: 195 passed / 18 failed, with all failures contained in `ARCH025-TEST-001`.
- Full suite: 1,001 passed / 24 failed / 33 skipped, with all failures contained in `ARCH025-TEST-001` and no task-only failing identifier.
- Prisma generation, typecheck, task-scoped ESLint, production build and `git diff --check`: passed.
- GitHub branch comparison confirms implementation commit `96f7db9e437b9732ba0f2b4186fa9306e72dec97` is the single task implementation commit ahead of its base and changes only the three authorised implementation/test files.
- Uploaded review snapshot contains no cross-task `node_modules` symlink.

### Architecture Conformance

Conforms to ARCH-025 and SHOPIFY-008. Purchase initiation has one dedicated owner; the façade remains stable; SHOPIFY-001 cycle helpers and SHOPIFY-002 catalogue ownership are reused without coalescing the deliberate rereads; provider/transaction, locking, Serializable isolation, idempotency and durable-fencing semantics are preserved; and no new external contract, database schema, route or purchase-management ownership change is introduced.

### Follow-up

`ARCH-025-SHOPIFY-009` is now Ready. Do not begin SHOPIFY-010 until SHOPIFY-009 is architect-accepted Complete.
