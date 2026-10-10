---
id: ARCH-027-SHOPIFY-002
architecture_id: ARCH-027
title: Record Shopify billing command history in the common BillingOperation ledger
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 106
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-027-SHOPIFY-001
enables: []
created: 2026-10-07
updated: 2026-10-10
---

# Record Shopify billing command history in the common BillingOperation ledger

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Adopt the Shop-owned provider-neutral `billing.BillingOperation` ledger for existing Shopify billing commands without changing Shopify billing product behaviour or replacing Shopify's current pending-state/reconciliation mechanics.

## Context

`ARCH-027-DATABASE-001` introduces one provider-neutral billing command-intent/history ledger:

```text
Shop
    -> BillingOperation[]
```

`BillingOperation` has required `shopId`, no `subscriptionId`, and no provider discriminator. Shopify/Woo ownership is derived from `Shop.platform`.

The existing Shopify implementation already has durable current/pending projection fields on `Subscription` and dedicated purchase/usage rows. ARCH-027 does not remove those mechanisms. This task adds historical command provenance so equivalent Shopify and Woo merchant billing actions share one business-operation ledger.

## Scope

Modify only `moda-interact` Shopify billing command/reconciliation code and focused tests.

Record `BillingOperation` for the existing Shopify command paths corresponding to:

```text
SUBSCRIPTION_CREATE
PLAN_SWITCH
CANCEL
ONE_TIME_CHARGE
```

Use the existing authenticated Shop as `BillingOperation.shopId`.

Preserve existing Shopify provider APIs, pending fields and reconciliation behaviour.

## Out of Scope

- Removing or deriving `Subscription.pendingPlanId`, `pendingShopifyPlanHandle` or `pendingEffectiveAt`.
- Replacing Shopify provider lifecycle/reconciliation types.
- Changing Shopify plan-change, cancellation or top-up product behaviour.
- Creating a Shopify-specific operation table.
- Adding a provider discriminator to `BillingOperation`.
- Woo command/webhook/reconciliation implementation.
- Database migrations.
- Gateway/system-test implementation.

## Requirements

### R1 — Shop ownership and provider boundary

Every Shopify operation MUST use the authenticated Shopify `Shop.id` as `BillingOperation.shopId`.

The task MUST validate `Shop.platform = SHOPIFY` at the existing trusted command boundary and MUST NOT store a duplicate provider discriminator on the operation.

### R2 — Preserve existing pending projection

The common operation ledger is durable history/intent. Existing Shopify `Subscription.pending*` fields remain the live pending projection in ARCH-027 and continue to drive current provider reconciliation.

Creating or confirming a `BillingOperation` MUST NOT change when existing Shopify pending/current Subscription fields are written or cleared.

### R3 — Command identity

For each existing Shopify merchant billing command, create/reuse exactly one `BillingOperation` under the task-defined deterministic `requestKey`/`requestFingerprint` rules appropriate to that current command path.

Retries MUST NOT create duplicate operations for the same `(shopId, requestKey)`.

### R4 — Generic provider reference

Where the existing Shopify provider workflow exposes a stable billing reference, store it in `BillingOperation.providerReference` with the database write-once semantics. Do not fabricate a reference where none exists.

### R5 — Top-up provenance

For a Shopify predefined recovery-credit purchase, the operation MUST be linked to the exact `RecoveryCreditPurchase` row. Existing `RecoveryCreditPurchase.usageEventId` / `UsageEvent` accounting provenance remains authoritative and unchanged.

### R6 — Resolution state

When existing trusted Shopify reconciliation establishes that the command's requested business outcome is current, transition the matching operation to `CONFIRMED` using a focused helper/service rather than duplicating reconciliation rules.

Ambiguous provider outcomes must not be represented as confirmed merely to complete the ledger.

## Work Items

- [x] Update the nested database dependency to the accepted ARCH-027 database revision and regenerate Prisma.
- [x] Add a focused Shopify billing-operation helper/service for operation create/reuse/state transitions.
- [x] Record `SUBSCRIPTION_CREATE` intent in the existing initial paid-subscription path.
- [x] Record `PLAN_SWITCH` intent in the existing hosted plan-change path.
- [x] Record `CANCEL` intent in the existing cancellation path.
- [x] Record `ONE_TIME_CHARGE` intent and link it to the exact `RecoveryCreditPurchase`.
- [x] Integrate confirmation updates with existing trusted Shopify reconciliation without changing projection behaviour.
- [x] Add focused idempotency, provider-reference and provider-isolation tests.

## Interfaces / Contracts

Database contract owner:

`ARCH-027-DATABASE-001`

Consumed model:

```text
billing.BillingOperation
    shopId
    kind
    state
    requestKey
    requestFingerprint
    merchantPricingPlanId?
    merchantPricingUsageEventId?
    recoveryCreditPurchaseId?
    providerReference?
```

Provider selection:

```text
BillingOperation.shopId -> Shop.platform = SHOPIFY
```

No cross-service runtime contract is introduced.

## Dependencies

- `ARCH-027-SHOPIFY-001`

## Enables

None directly. This task is a terminal implementation dependency of `ARCH-027-SYSTEM-TEST-001`.

## Acceptance Criteria

- [x] Equivalent Shopify create/switch/cancel/top-up commands create/reuse Shop-owned `BillingOperation` history.
- [x] `BillingOperation` stores neither `subscriptionId` nor provider discriminator.
- [x] Existing Shopify `Subscription.pending*` semantics and merchant-visible billing behaviour remain unchanged.
- [x] `(shopId, requestKey)` retries do not create duplicate operations.
- [x] Shopify top-up operation links to the exact `RecoveryCreditPurchase`, whose existing `UsageEvent` provenance remains intact.
- [x] Woo Shops cannot be processed by the Shopify operation integration.
- [x] Operation confirmation is driven only by existing trusted Shopify outcome/reconciliation evidence.

## Validation

- [ ] focused Shopify billing-operation unit tests
- [ ] existing hosted plan-change/cancellation tests
- [ ] existing top-up purchase/refund tests
- [ ] TypeScript typecheck
- [ ] lint for changed files
- [ ] production build where required by the repository task contract

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to `moda_architect` and STOP. Do not begin system-test work.

## Implementation Notes

Prefer a small focused billing-operation collaborator called from existing Shopify command/reconciliation services. Do not turn this task into a rewrite of those services or remove current pending projection fields.

## Completion Report

### Status

Ready for Review — retrospective report for the Shopify implementation present in the 2026-10-10 workspace snapshot. The developer reports the task implemented. The attempt number is reconstructed as the first documented implementation attempt; original claim metadata and any intermediate attempts are unavailable in this ZIP.

### Files Changed

The original `ARCH-027-SHOPIFY-002-record-shopify-billing-operation-history.patch` enumerates **13 implementation files (7 production, 6 tests)**. Their Shopify billing-operation integration is visible in the supplied snapshot; later edits mean the original patch does not reverse-apply unchanged to every current file.

Production:

- `app/services/billing/billing-plan-resolution.service.ts`
- `app/services/billing/billing.service.ts`
- `app/services/billing/hosted-plan-change.service.ts`
- `app/services/billing/recovery-credit-purchase-request.service.ts`
- `app/services/billing/shopify-billing-operation.service.ts` (new focused service)
- `app/services/billing/subscription-activation.service.ts`
- `app/services/billing/subscription-sync.service.ts`

Focused tests:

- `tests/unit/services/billing.service.test.ts`
- `tests/unit/services/billing/hosted-plan-change.service.test.ts`
- `tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts`
- `tests/unit/services/billing/shopify-billing-operation.service.test.ts` (new focused suite)
- `tests/unit/services/billing/subscription-activation.service.test.ts`
- `tests/unit/services/billing/subscription-sync.service.test.ts`

**This report-only correction changes no application files.** The accepted ARCH-027 `billing.BillingOperation` schema is present in `moda-interact/database/prisma/schema.prisma`; no new database migration is claimed for SHOPIFY-002. The ZIP lacks Git metadata, so the exact historical database gitlink update or Prisma generation command cannot be independently reconstructed.

### Work Completed

- Introduced `ShopifyBillingOperationService` as the Shopify-specific collaborator over the provider-neutral, Shop-owned `billing.BillingOperation` ledger. The helper validates `Shop.platform = SHOPIFY`, constructs deterministic request identities/fingerprints, reuses operations by `(shopId, requestKey)`, and rejects mismatched replay intent.
- Wired `SUBSCRIPTION_CREATE` intent into initial paid activation, `PLAN_SWITCH` and `CANCEL` into hosted plan-return handling, and `ONE_TIME_CHARGE` into the existing predefined recovery-credit top-up acquisition transaction.
- Recorded quoted paid-plan and usage-event pricing evidence without introducing a provider discriminator or `subscriptionId` field on `BillingOperation`. The top-up operation links to the exact `RecoveryCreditPurchase`; existing `UsageEvent` reporting/accounting evidence remains authoritative.
- Used existing trusted Shopify subscription reconciliation to confirm eligible recurring/cancellation operations. Missing references and ambiguous reconciliation matches do not fabricate confirmation.
- Preserved the separate Shopify provider API and live `Subscription.pending*` projection/reconciliation paths; the operation ledger adds intent/history rather than replacing them.
- Added a 13-case focused billing-operation test file, plus collaborator assertions in hosted plan, initial paid activation, purchase request, subscription synchronization, and aggregate billing tests.

The Work Items and Acceptance Criteria above are checked based on the implementation visible in the snapshot and the developer's completion statement; **their checked state is not a claim that the original automated validation output was recovered**.

### Validation Results

Verified during retrospective snapshot inspection:

- `node --experimental-strip-types --check app/services/billing/shopify-billing-operation.service.ts` — **PASS** (Node v22.16.0 syntax parse).
- `node --experimental-strip-types --check tests/unit/services/billing/shopify-billing-operation.service.test.ts` — **PASS** (syntax parse only, not test execution).
- Confirmed the required Prisma `BillingOperation` model contains Shop ownership, unique `(shopId, requestKey)`, purchase linkage, optional provider reference, and no `subscriptionId` or provider field.
- Confirmed the dedicated Vitest file declares 13 cases and the relevant calling services/tests are present.

**Not independently verified in this report:** original Vitest pass/fail output, existing hosted-plan/cancellation/top-up/refund regressions, Prisma generation, TypeScript typecheck, changed-file lint, and production build. The uploaded ZIP contains no `node_modules` or original command output; therefore all Validation checkboxes above remain unchecked rather than assigning invented PASS results. Patch applicability/whitespace checks are reported separately with the delivered report patch.

### Deviations

- This is a retrospective documentation correction, not a replay of the original implementation execution.
- The supplied ZIP contains no Git metadata or prepared execution packet. Physical parent/implementation task worktree locations, matching `task/ARCH-027-SHOPIFY-002` branches, start-of-attempt synchronization, commits and pushes are **unverified**. It is **not asserted** that a shared checkout was or was not used.
- `attempt: 1` reflects the reconstructed first recorded implementation attempt for this previously unclaimed task; the true execution history and original executor/claim timestamp were not supplied and are not fabricated.
- No domain `_index.md` or parent architecture rollup is changed in this patch, pending the user-requested session-finalization step.

### Assumptions

- The developer's statement that `ARCH-027-SHOPIFY-002` has been implemented refers to the Shopify billing-operation integration present in this 2026-10-10 snapshot.
- `ARCH-027-DATABASE-001` and `ARCH-027-SHOPIFY-001` remain the accepted prerequisite contracts; Woo provider commands and reconciliation are outside this task.

### Unresolved Issues

- Original developer validation results and canonical worktree/start-of-attempt evidence have not been recovered from these attachments. These are evidence gaps for formal architect acceptance, **not evidence of a runtime failure**.
- Full focused/regression tests and repository typecheck/lint/build cannot be independently rerun in the dependency-free archive. The pending Validation items must not be interpreted as failures.

### Architectural Concerns

The inspected implementation is aligned with the intended Shop-owned operation boundary and leaves Shopify's existing pending subscription projection separate. Formal task acceptance remains gated on the task's required validation and physical-execution evidence under `docs/agent-worktree-isolation-policy.md`.

## Architect Review

### Review Status

Pending — source reviewed; validation and execution evidence incomplete.

### Review Notes

Retrospective inspection confirms the Shopify billing-operation helper, four command paths, top-up purchase association, recurring reconciliation hooks, and focused tests in the uploaded implementation. This review does **not** assert that tests were executed successfully or that the required mirrored task worktrees/branches were used.

### Reviewed Files

- `app/services/billing/shopify-billing-operation.service.ts`
- `app/services/billing/subscription-activation.service.ts`
- `app/services/billing/hosted-plan-change.service.ts`
- `app/services/billing/recovery-credit-purchase-request.service.ts`
- `app/services/billing/subscription-sync.service.ts`
- `app/services/billing/billing.service.ts`
- `tests/unit/services/billing/shopify-billing-operation.service.test.ts`
- associated focused caller tests
- `database/prisma/schema.prisma` (consumed schema inspection only)

### Validation Reviewed

- Focused service and test TypeScript syntax checks: **PASS** (not Vitest).
- Schema and wiring: inspected statically.
- Required runtime tests, lint, typecheck, build, and task-worktree evidence: **not supplied/independently verified**.

### Architecture Conformance

Source-level design conforms to the bounded ARCH-027 Shopify operation-history intent: Shop ownership, provider isolation, deterministic command identity, distinct current/pending subscription projection, linked purchase provenance, and confirmation tied to trusted reconciliation. Final architect acceptance is **pending**, not implied by this report patch.

### Follow-up

Recover or rerun required validation in the canonical `ARCH-027-SHOPIFY-002` implementation worktree, document matching parent/implementation worktree and synchronization evidence, and then complete architect review. Do not update `_index.md` until the user explicitly closes this architecture session.
