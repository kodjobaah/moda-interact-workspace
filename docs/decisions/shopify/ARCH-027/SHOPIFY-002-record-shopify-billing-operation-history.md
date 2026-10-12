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
attempt: 2
depends_on:
  - ARCH-027-SHOPIFY-001
enables: []
created: 2026-10-07
updated: 2026-10-12
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

- [x] focused Shopify billing-operation unit tests
- [x] existing hosted plan-change/cancellation tests
- [x] existing top-up purchase/refund tests
- [x] TypeScript typecheck
- [x] lint for changed files
- [x] production build where required by the repository task contract

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to `moda_architect` and STOP. Do not begin system-test work.

## Implementation Notes

Prefer a small focused billing-operation collaborator called from existing Shopify command/reconciliation services. Do not turn this task into a rewrite of those services or remove current pending projection fields.

## Completion Report

### Status

Ready for Review — Attempt 2 corrections completed against the review feedback. Attempt 2 was claimed by the canonical launcher on 2026-10-12 and returned to review after the required corrections and validation.

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

Attempt 2 correction files:

- `app/services/billing/hosted-plan-change.service.ts`
- `app/services/billing/recovery-credit-purchase-request.service.ts`
- `app/services/billing/shopify-billing-operation.service.ts`
- `tests/unit/services/billing/hosted-plan-change.service.test.ts`
- `tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts`
- `tests/unit/services/billing/shopify-billing-operation.service.test.ts`

The accepted ARCH-027 `billing.BillingOperation` schema is present in `moda-interact/database/prisma/schema.prisma`; no new database migration is part of SHOPIFY-002.

### Work Completed

- Introduced `ShopifyBillingOperationService` as the Shopify-specific collaborator over the provider-neutral, Shop-owned `billing.BillingOperation` ledger. The helper validates `Shop.platform = SHOPIFY`, constructs deterministic request identities/fingerprints, reuses operations by `(shopId, requestKey)`, and rejects mismatched replay intent.
- Wired `SUBSCRIPTION_CREATE` intent into initial paid activation, `PLAN_SWITCH` and `CANCEL` into hosted plan-return handling, and `ONE_TIME_CHARGE` into the existing predefined recovery-credit top-up acquisition transaction.
- Recorded quoted paid-plan and usage-event pricing evidence without introducing a provider discriminator or `subscriptionId` field on `BillingOperation`. The top-up operation links to the exact `RecoveryCreditPurchase`; existing `UsageEvent` reporting/accounting evidence remains authoritative.
- Used existing trusted Shopify subscription reconciliation to confirm eligible recurring/cancellation operations. Missing references and ambiguous reconciliation matches do not fabricate confirmation.
- Preserved the separate Shopify provider API and live `Subscription.pending*` projection/reconciliation paths; the operation ledger adds intent/history rather than replacing them.
- Added a 13-case focused billing-operation test file, plus collaborator assertions in hosted plan, initial paid activation, purchase request, subscription synchronization, and aggregate billing tests.
- Removed the lifecycle-event-ID fallback when a stable Shopify subscription reference is absent; unresolved hosted changes no longer manufacture a `providerReference`.
- Changed `PLAN_SWITCH` reconciliation to confirm only when the observed stable Shopify subscription reference exactly matches the operation reference. A mismatch remains `AWAITING_CONFIRMATION`.
- Removed the Moda-generated Shopify App Events idempotency key from the one-time-charge provider-reference path. Top-up operations are created `AWAITING_CONFIRMATION` with `providerReference: null`; Moda request identity remains on the existing usage-event/purchase records.
- Updated focused regression tests for lifecycle-reference rejection, provider-reference mismatch, and null top-up reference semantics.

The Work Items and Acceptance Criteria above reflect the implementation and Attempt 2 verification recorded below.

### Validation Results

Attempt 2 validation completed in the canonical implementation worktree:

- `./node_modules/.bin/vitest run tests/unit/services/billing/shopify-billing-operation.service.test.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts` — **PASS**, 3 files / 35 tests.
- `./node_modules/.bin/vitest run tests/unit/services/billing.service.test.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/subscription-sync.service.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts tests/unit/services/recovery-credit-purchase-management.service.test.ts` — **PASS**, 6 files / 289 tests. Covers hosted plan/cancellation, reconciliation, top-up acquisition, and purchase/refund management.
- `npm run typecheck` — **PASS** (`react-router typegen && tsc --noEmit`).
- `./node_modules/.bin/eslint app/services/billing/hosted-plan-change.service.ts app/services/billing/recovery-credit-purchase-request.service.ts app/services/billing/shopify-billing-operation.service.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts` — **PASS**. ESLint emitted the repository's TypeScript 5.9.3 versus typescript-estree supported-version warning; no lint errors.
- `npm run build` — **PASS**, including `npm run prisma:generate` and production client/server builds. Vite emitted dependency annotation, Prisma browser externalization, and large-client-chunk warnings; the build completed successfully.
- `git diff --check` — **PASS**.

The task worktree had no local `node_modules`; validation used a temporary symlink to the canonical implementation checkout's existing `node_modules` (Vitest 4.1.11), then removed the symlink. No dependency or lockfile changes were made.

### Deviations

- The Attempt 2 launcher packet reported canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-SHOPIFY-002`, branch `task/ARCH-027-SHOPIFY-002`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-SHOPIFY-002`, branch `task/ARCH-027-SHOPIFY-002`.
- Start-of-attempt synchronization from the launcher: parent task branch fast-forward `not-needed`, parent `origin/main` incorporated `yes`; implementation task branch fast-forward `not-needed`, implementation `origin/main` `already-current`.
- Recursive implementation submodules: `git submodule sync --recursive` **passed**; `git submodule update --init --recursive` **passed**; `database` initialized at `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`.
- Shared workspace and shared implementation checkouts were not used for task edits; no other task worktree was reused.
- The original implementation task branch/history was unavailable during review recovery. The implementation worktree was restored from `origin/main`, which contains the original implementation commit `eb0eedd`; the launcher then reused the exact task worktree and recorded Attempt 2. No Attempt 1 task-branch history is claimed as recovered.

### Assumptions

- The developer's statement that `ARCH-027-SHOPIFY-002` has been implemented refers to the Shopify billing-operation integration present in this 2026-10-10 snapshot.
- `ARCH-027-DATABASE-001` and `ARCH-027-SHOPIFY-001` remain the accepted prerequisite contracts; Woo provider commands and reconciliation are outside this task.

### Unresolved Issues

- The original Attempt 1 branch history was not recovered; the current implementation and Attempt 2 review evidence are recorded above. This history limitation is explicit and does not replace the launcher-provided Attempt 2 worktree/synchronization evidence.

### Architectural Concerns

The inspected implementation is aligned with the intended Shop-owned operation boundary and leaves Shopify's existing pending subscription projection separate. Required validation and launcher-provided physical-execution evidence are recorded above; formal task acceptance remains with `moda_architect`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is not accepted. The implementation materially records Shopify billing operations, but the current source does not satisfy the task's provider-reference and trusted-confirmation requirements. The attached review artifact also does not contain Git/worktree metadata or the nested database submodule, so the required execution-isolation and full validation evidence cannot be independently verified from this submission.

Corrections required for Attempt 2:

1. **Do not substitute Shopify lifecycle-event identity for billing-contract identity.** `hosted-plan-change.service.ts` currently passes `current.providerSubscriptionId ?? current.lastProviderLifecycleEventId` as `providerReference`. `lastProviderLifecycleEventId` is lifecycle evidence, not the stable billing reference required by R4. When no stable Shopify billing reference is available, do not fabricate one merely to satisfy the operation schema; keep the operation/request in the architecture-approved unresolved state and report any state-model gap back to `moda_architect` rather than redefining `providerReference` locally.

2. **Do not confirm a plan switch against a different provider contract.** `reconcileActiveSubscription()` currently confirms an unambiguous `PLAN_SWITCH` using only the target plan, even when the operation already carries a different `providerReference` from the currently observed Shopify subscription. A provider-reference mismatch is ambiguous evidence under R6 and must not be transitioned to `CONFIRMED`. Update the reconciliation rule and its focused regression test so a mismatched stable provider reference remains unresolved/error-safe rather than being confirmed.

3. **Keep Moda request identity separate from Shopify provider charge identity for one-time charges.** `recovery-credit-purchase-request.service.ts` currently passes `UsageEvent.shopifyIdempotencyKey` into `recordOneTimeChargeIntent()` as `providerReference`. Shopify documents App Events `idempotency_key` as an app-generated unique key, and a successful App Events submission returns only HTTP `202` with `{ "success": true }`; it does not synchronously return a Shopify charge identifier. Shopify's Partner Historical Events later exposes `Charge.chargeId` as the stable identifier for `CHARGE_USAGE`. For this task, update `recordOneTimeChargeIntent()` and its caller/tests so the `ONE_TIME_CHARGE` operation is created in `AWAITING_CONFIRMATION` with `providerReference: null`, while the Moda-generated idempotency key remains only in the existing UsageEvent/request identity. Do **not** expand SHOPIFY-002 into a new Historical Events charge-correlation mechanism. A later trusted reconciliation may populate `providerReference` with Shopify `chargeId` only when the exact charge can be associated deterministically; ambiguous evidence must leave the reference unset and must not confirm the operation.

4. **Complete and record the required validation in the task Completion Report.** Re-run the focused billing-operation tests plus the repository's declared typecheck/build/test validation required by this task. Record the exact commands/results. The submission must also include launcher-resolved dedicated parent/implementation worktree and start-of-attempt synchronization evidence before acceptance.

### Reviewed Files

- `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`
- `docs/decisions/shopify/ARCH-027/SHOPIFY-001-*.md`
- `docs/decisions/shopify/ARCH-027/SHOPIFY-002-record-shopify-billing-operation-history.md`
- `moda-interact/app/services/billing/shopify-billing-operation.service.ts`
- `moda-interact/app/services/billing/hosted-plan-change.service.ts`
- `moda-interact/app/services/billing/recovery-credit-purchase-request.service.ts`
- `moda-interact/app/services/billing/subscription-activation.service.ts`
- `moda-interact/app/services/billing/subscription-sync.service.ts`
- `moda-interact/tests/unit/services/billing/shopify-billing-operation.service.test.ts`
- `moda-interact/tests/unit/services/billing/hosted-plan-change.service.test.ts`
- `moda-interact/tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts`

### Validation Reviewed

- Static source/task/architecture review completed against the submitted ARCH-027-SHOPIFY-002 workspace archive.
- Node syntax parsing (`node --experimental-strip-types --check`) passed for the reviewed TypeScript implementation/test files.
- Full repository tests, typecheck, build, Prisma validation/migration validation and Git/worktree synchronization evidence were not independently reproducible from the submitted archive because it does not include installed dependencies, Git metadata, or the nested database submodule.

### Architecture Conformance

- Repository ownership: conforms; implementation is contained in `moda-interact`.
- Dependency: `ARCH-027-SHOPIFY-001` is recorded Complete in the submitted task set.
- `Subscription.pending*` compatibility: no conflicting write was identified in the reviewed code.
- Deterministic operation request/fingerprint usage: present.
- Shopify operation history coverage: present for create/switch/cancel/top-up paths.
- Provider-reference semantics: **does not conform** to R4 because lifecycle-event identity and the app-generated App Events idempotency key are used as provider billing references. Shopify App Events does not return a charge identifier synchronously; the later Partner Historical Events `Charge.chargeId` is the provider-side stable charge identity.
- Trusted confirmation semantics: **does not conform** to R6 because a plan-switch operation can be confirmed despite a different observed provider subscription reference.
- Execution/worktree evidence: incomplete for acceptance.

### Follow-up

Return `ARCH-027-SHOPIFY-002` through its normal `moda_app` execution path for Attempt 2. Preserve the existing bounded task; do not create a separate correction task for these in-scope fixes. For `ONE_TIME_CHARGE`, the bounded correction is to persist the intent with `providerReference: null`; do not add Partner Historical Events charge correlation under this task. If implementation unexpectedly reveals that the consumed database/shared contract cannot represent that nullable unresolved state, stop that part and return the cross-repository contract gap to `moda_architect` rather than overloading another identity field.
