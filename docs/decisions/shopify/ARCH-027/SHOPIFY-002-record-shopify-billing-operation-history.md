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
attempt: 5
depends_on:
  - ARCH-027-SHOPIFY-001
  - ARCH-027-DATABASE-003
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

- `ARCH-027-SHOPIFY-001` — Complete.
- `ARCH-027-DATABASE-003` — Complete (architect-accepted 2026-10-12).

## Enables

None directly. This task is a terminal implementation dependency of `ARCH-027-SYSTEM-TEST-001`.

## Acceptance Criteria

- [ ] Equivalent Shopify create/switch/cancel/top-up commands create/reuse Shop-owned `BillingOperation` history for all permitted provider states, including missing stable subscription references. Missing reference evidence must not suppress a valid operation or permit ambiguous outcome confirmation.
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

Blocked — Attempt 3 corrected the database-invalid one-time-charge state and reran the required validation. The task cannot return to review because Shopify's provider/application contract allows an active subscription without a stable subscription reference, while the accepted database contract requires a nonblank reference for PLAN_SWITCH and CANCEL operations. The claim was cleared after recording this cross-contract blocker for `moda_architect`.

Attempt 2 was claimed by the canonical launcher on 2026-10-12 and returned to review after its requested corrections and validation. The latest launcher claimed Attempt 3 on 2026-10-12; its physical worktree, synchronization, dependency gate, and submodule evidence is recorded under Attempt 3 below.

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

### Attempt 3 Corrections and Blocker

- Changed `recordOneTimeChargeIntent()` to create `ONE_TIME_CHARGE` in `INITIATING` with `providerReference: null`. This is a database-valid unresolved state and does not repurpose the Moda App Events idempotency key or add Historical Events charge correlation.
- Updated the focused billing-operation test to assert `INITIATING` with a null provider reference.
- The missing-reference recurring-command case cannot be closed within this repository contract. The Shopify Partner API response shape declares `activeSubscription.legacySubscriptionId` nullable; `ShopifyBillingProvider` copies it directly into `ProviderSubscription.providerSubscriptionId`, whose type is nullable; and subscription synchronization persists that value without rejecting an active subscription when it is null. The hosted plan-change/cancellation return path likewise passes the nullable persisted `providerSubscriptionId` to the operation service.
- Under the accepted database migration, PLAN_SWITCH and CANCEL require a nonblank `providerReference`; the state/reference check also prohibits AWAITING_CONFIRMATION or CONFIRMED without one. Thus a permitted provider response can reach the trusted command path without a database-valid recurring BillingOperation identity. The existing no-reference early return would omit required operation history; fabricating a lifecycle or Moda request ID is not acceptable. Per the Attempt 3 review, this task is blocked for `moda_architect` to resolve the cross-contract gap. No source behavior was changed to silently bless omission or to reject an otherwise accepted Shopify subscription state.

### Attempt 3 Validation Results

Validation completed in the canonical implementation task worktree:

- `./node_modules/.bin/vitest run tests/unit/services/billing/shopify-billing-operation.service.test.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts` — **PASS**, 3 files / 35 tests.
- `./node_modules/.bin/vitest run tests/unit/services/billing.service.test.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/subscription-sync.service.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts tests/unit/services/recovery-credit-purchase-management.service.test.ts` — **PASS**, 6 files / 289 tests.
- `npm run typecheck` — **PASS** (`react-router typegen && tsc --noEmit`).
- `./node_modules/.bin/eslint app/services/billing/hosted-plan-change.service.ts app/services/billing/recovery-credit-purchase-request.service.ts app/services/billing/shopify-billing-operation.service.ts tests/unit/services/billing/hosted-plan-change.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts` — **PASS**. The command emitted the existing TypeScript 5.9.3 versus typescript-estree supported-version warning; there were no lint errors.
- `npm run build` — **PASS**, including Prisma generation and client/server production builds. Existing dependency annotation, Prisma browser externalization, empty route chunk, and large client-chunk warnings were emitted.
- `git diff --check` — **PASS**.

The task worktree had no local `node_modules`; validation used a temporary symlink to the canonical implementation checkout's existing dependency install, then removed it. Prisma Client generation wrote into that dependency install's generated client directory; no tracked dependency, lockfile, or source-checkout files were intentionally changed.

### Attempt 3 Launcher Evidence

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; resolution was not derived from a previous task worktree.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-SHOPIFY-002`, branch `task/ARCH-027-SHOPIFY-002`; start synchronization: remote task branch fast-forward `not-needed`, `origin/main` incorporated `already-current`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-SHOPIFY-002`, branch `task/ARCH-027-SHOPIFY-002`; start synchronization: remote task branch fast-forward `not-needed`, `origin/main` incorporated `already-current`.
- Shared workspace checkout switched/mutated for task source work: no. Shared implementation checkout switched/mutated for task source work: no. Another task worktree reused: no.
- Launcher dependency gate: passed (`ARCH-027-SHOPIFY-001` complete). Recursive `git submodule sync --recursive` and `git submodule update --init --recursive`: passed. `database` initialized at `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`.
- Attempt 3 was claimed as `copilot` at `2026-10-12T12:00:31Z`; the durable claim commit was `dbf732e717befb079ca0936d2f37ae0e129ca22e`. Claim metadata is cleared in this blocked task record.

## Architect Review

### Review Status

Changes Requested — database blocker resolved; task Ready for Attempt 4 (2026-10-12).

### Review Notes

Attempt 3 correctly implements the requested one-time-charge correction: Shopify `ONE_TIME_CHARGE` intent is now persisted as `INITIATING` with `providerReference = null`, preserving the separation between Moda/App-Events request identity and provider charge identity. The recorded focused/regression/typecheck/lint/build/diff validation is accepted for that correction.

The task is **not** returned for another Shopify-only correction yet. The repository agent correctly identified a cross-repository persistence-contract defect for recurring Shopify operations. Shopify Partner `activeSubscription.legacySubscriptionId` is nullable and is expected to be null for subscriptions created natively in managed pricing. The current provider adapter faithfully projects that nullable value to `ProviderSubscription.providerSubscriptionId`, and subscription synchronization permits an otherwise valid active Shopify subscription with that value absent.

The accepted `ARCH-027-DATABASE-001` design already describes `BillingOperation.providerReference` as generic optional provider evidence. Its migration nevertheless places provider/workflow-specific requiredness in PostgreSQL by requiring a nonblank reference for every `PLAN_SWITCH` and `CANCEL`, and again for every `AWAITING_CONFIRMATION` / `CONFIRMED` operation. That requiredness does not belong in the provider-neutral database layer. PostgreSQL should enforce nullable/nonblank-if-present/write-once integrity; the application that owns each provider workflow must decide whether a reference is required for a command or state transition.

This is therefore an architecture/database-boundary correction, not a reason to fabricate another Shopify identifier and not a reason to omit required BillingOperation history. `ARCH-027-DATABASE-003` removes provider-reference requiredness from PostgreSQL and leaves provider-specific requiredness in the owning application layer. It is introduced as the blocking dependency.

After `ARCH-027-DATABASE-003` is Complete, the next Shopify attempt must complete the original ledger adoption with these rules:

1. A missing stable Shopify subscription reference is a supported provider state, not an invariant violation. `PLAN_SWITCH` and `CANCEL` must still create/reuse their Shop-owned BillingOperation.
2. `providerReference` remains optional provider evidence. Never substitute `lastProviderLifecycleEventId`, a Moda request key, a Shopify App Events idempotency key, `Subscription.id`, or another local identifier.
3. Recurring `requestKey` / `requestFingerprint` identity must remain stable whether `providerReference` is absent initially or appears later. Provider evidence must not change the Moda command identity for the same command.
4. Existing trusted Shopify business-outcome reconciliation may move an unambiguously matched recurring operation to `AWAITING_CONFIRMATION` / `CONFIRMED` even when the provider exposes no stable subscription reference. Confirmation still requires exact/unique command-outcome attribution; ambiguity must remain unresolved.
5. If a stable provider reference later becomes available for the same operation, the existing database write-once rule may attach it exactly once. A conflicting later reference must fail closed.
6. Keep the accepted Attempt 3 top-up behavior unchanged: `ONE_TIME_CHARGE` starts `INITIATING` with no fabricated provider reference. Historical `Charge.chargeId` convergence belongs to the separately defined Background task, not this Shopify task.

### Reviewed Files

- `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`
- `docs/decisions/database/ARCH-027/DATABASE-001-add-minimal-woocommerce-billing-persistence.md`
- `docs/decisions/shopify/ARCH-027/SHOPIFY-002-record-shopify-billing-operation-history.md`
- `moda-interact/database/prisma/schema.prisma`
- `moda-interact/database/prisma/migrations/20261008110000_arch027_woocommerce_billing_persistence/migration.sql`
- `moda-interact/app/services/billing/providers/shopify-billing.provider.ts`
- `moda-interact/app/services/billing/billing.types.ts`
- `moda-interact/app/services/billing/subscription-sync.service.ts`
- `moda-interact/app/services/billing/hosted-plan-change.service.ts`
- `moda-interact/app/services/billing/shopify-billing-operation.service.ts`
- `moda-interact/tests/unit/services/billing/hosted-plan-change.service.test.ts`

### Validation Reviewed

- Attempt 3 reports **35 focused tests PASS**.
- Attempt 3 reports **289 billing regression tests PASS**.
- Attempt 3 reports TypeScript typecheck, changed-file lint, production build and `git diff --check` **PASS**.
- Attempt 3 records canonical launcher/worktree synchronization and clean pushed task branches.
- Static contract inspection confirms `BillingOperation_kind_shape_check` requires `providerReference` for `PLAN_SWITCH` and `CANCEL`, and `BillingOperation_state_provider_reference_check` requires it for `AWAITING_CONFIRMATION` and `CONFIRMED`.
- Static provider inspection confirms `legacySubscriptionId` / `ProviderSubscription.providerSubscriptionId` are nullable and are persisted as nullable provider evidence.

### Architecture Conformance

- Attempt 3 one-time-charge correction: conforms.
- Lifecycle-event identity separation: conforms.
- PLAN_SWITCH mismatched-provider confirmation protection: conforms.
- Validation/worktree evidence: sufficient for the Attempt 3 source correction.
- Complete recurring command-history coverage: blocked by the accepted database constraint, not by a remaining Shopify-local implementation choice.

### Follow-up

Do **not** reclaim `ARCH-027-SHOPIFY-002` for Attempt 4 until `ARCH-027-DATABASE-003` is architect-accepted Complete. The task remains `blocked` with claim metadata cleared. Once the database correction is Complete, return this same task to `ready`; the next claim becomes Attempt 4 and must implement the Shopify application-layer nullable-provider-reference behavior above without changing Shopify product behavior or adding Historical Events charge correlation.

### Latest Re-gate Decision — 2026-10-12

`ARCH-027-DATABASE-003` is now architect-accepted Complete on the developer's PostgreSQL 17 rehearsal evidence. Together with Complete `ARCH-027-SHOPIFY-001`, every declared dependency is satisfied. The earlier database blocker is lifted. This changes only task eligibility, not the acceptance status of Shopify's unfinished implementation.

The canonical task is `status: ready` with `executor: null`, `claimed_at: null`, and `attempt: 3`; the next authorized `/moda-task ARCH-027-SHOPIFY-002` claim is **Attempt 4**. The six provider-reference and reconciliation correction requirements under the prior `### Review Notes` remain the binding Attempt 4 contract.

Before executing the new attempt, the launcher must prepare the dedicated parent/implementation worktrees and the Shopify `database` submodule must resolve to a Database revision containing the accepted DATABASE-003 migration; the developer must verify migration deployment in the target integration database. Do not manufacture a provider reference or weaken deterministic request identity, provider-outcome attribution, write-once rules, or the accepted `ONE_TIME_CHARGE` behaviour. No Shopify source changes, claim, push, or passing tests are asserted by this re-gate patch.

### Attempt 4 Execution Note — Blocked Before Implementation

The canonical launcher claimed Attempt 4 as `copilot` at `2026-10-12T17:10:06Z` (durable claim commit `bb223d62f0aad90f5f47aedbb8d38b11e6c779e9`). Its dependency gate passed for `ARCH-027-SHOPIFY-001` and `ARCH-027-DATABASE-003`; the dedicated worktrees were reused and the recursive submodule initialization reported ready. However, the exact initialized `database` submodule commit is `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a` (`feat(database) added merchant lifecycle`), and this revision does not contain the accepted DATABASE-003 nullable-reference migration required by the re-gate above.

Inspection of the pinned `database/prisma/migrations/20261008110000_arch027_woocommerce_billing_persistence/migration.sql` confirms it still requires nonblank `providerReference` for `PLAN_SWITCH` and `CANCEL` in `BillingOperation_kind_shape_check`, and for `AWAITING_CONFIRMATION` / `CONFIRMED` in `BillingOperation_state_provider_reference_check`. The migration search found no later migration in this pinned revision removing those checks. Therefore the prepared implementation worktree does not satisfy the explicit Attempt 4 database-revision prerequisite. Migration deployment to the target integration database could not be verified against the required DATABASE-003 migration because that migration is absent from the pinned submodule revision.

No Shopify source or test files were changed in Attempt 4, and no Attempt 4 validation is claimed. The implementation worktree remains clean. The task claim is cleared and the task is `blocked` pending correction of the database submodule revision/deployment evidence and a fresh launcher preparation. The Attempt 4 launcher packet recorded parent synchronization (`origin/main` incorporated: `yes`; remote task fast-forward: `not-needed`), implementation synchronization (`origin/main` incorporated: `already-current`; remote task fast-forward: `not-needed`), and canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.

### Developer Override — Reopened (2026-10-12)

- Previous accepted attempt: none recorded. The latest workflow cycle remains Attempt 4, blocked before implementation; preserve `attempt: 4` without incrementing.
- Reason: the developer reports that the DATABASE-003 migration has completed and explicitly requests reopening this task to allow the canonical task workflow to prepare the next implementation attempt and update its database submodule.
- Reopen is not a claim. Task execution/completion modes remain unchanged; `executor` and `claimed_at` are null. All prior review and blocker history, including the Attempt 4 execution note, is preserved.
- Dependency frontier checked: `ARCH-027-BACKGROUND-007` and `ARCH-027-SYSTEM-TEST-001` directly depend on this task and are both still `pending`; neither status changes on reopen. No downstream dependency regression was found.

### Attempt 5 Execution Note — Implemented, Submitted for Review

The canonical launcher claimed Attempt 5 as `copilot` at `2026-10-12T18:38:59Z` and pushed durable parent claim commit `9f3fb7b981b53dd4ddaece2fcde91863054146e1`. Its dependency gate passed for `ARCH-027-SHOPIFY-001` and `ARCH-027-DATABASE-003`. The dedicated parent and implementation worktrees were reused; both remote task branches were already current and both `origin/main` tips were already incorporated.

The implementation worktree's nested `database` submodule initially remained pinned to `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`, which did not contain DATABASE-003. The canonical Database checkout was clean on `main` at `98574d4ec164e8b7e5b34be2ecf73d42b7cacfdc`. Fetching only `origin/main` into the nested submodule exposed that exact commit; inspection confirmed it contains `prisma/migrations/20261012170000_arch027_relax_billing_operation_provider_reference/migration.sql`, which replaces the provider-specific operation-kind constraint and drops the state-wide provider-reference requirement while preserving the nonblank-if-present and write-once guards. The Shopify implementation worktree now pins exactly `98574d4ec164e8b7e5b34be2ecf73d42b7cacfdc`.

The Shopify service now creates/reuses `PLAN_SWITCH` and `CANCEL` operations when the stable provider reference is absent. Recurring request keys and fingerprints use command identity rather than provider evidence. Trusted reconciliation confirms a uniquely attributed operation without a reference, uses exact references to disambiguate matching outcomes, and leaves multiple unresolved candidates open. A later provider reference attaches once; a conflicting reference fails closed, and confirmation without new evidence preserves an already attached reference. `ONE_TIME_CHARGE` remains `INITIATING` with a null provider reference.

### Attempt 5 Validation

- Focused `shopify-billing-operation.service.test.ts`: **PASS**, 19 tests.
- Billing regression suite (`billing.service`, hosted plan change, subscription sync, operation service, top-up request, purchase management): **PASS**, 6 files / 295 tests.
- `npm run typecheck`: **PASS**.
- Changed-file ESLint: **PASS**. It emitted the existing TypeScript 5.9.3 versus typescript-estree supported-version warning.
- `npm run build`: **PASS**, including Prisma Client generation from the updated database submodule. Existing dependency annotation, Prisma browser externalization and large client chunk warnings were emitted.
- `git diff --check`: **PASS**.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run prisma:status`: **NOT RUN TO COMPLETION**; Prisma returned `P1001` because no server was reachable at `localhost:5432`. Migration deployment to a persistent integration database remains unverified; no remote database was contacted.

The implementation worktree had no local `node_modules`; validation used a temporary symlink to the canonical Shopify checkout's existing dependencies and removed it afterward. No dependency manifest or lockfile changes were made.

### Attempt 5 Git / VCS

Task branch: `task/ARCH-027-SHOPIFY-002`.

Physical worktree isolation:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-SHOPIFY-002`, branch `task/ARCH-027-SHOPIFY-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-SHOPIFY-002`, branch `task/ARCH-027-SHOPIFY-002`.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.

Start-of-attempt synchronization from the launcher: parent remote task branch fast-forward `not-needed`; parent `origin/main` incorporated `yes`. Implementation remote task branch fast-forward `not-needed`; implementation `origin/main` incorporated `already-current`.

The implementation commit and parent report commit/push identifiers are recorded by their respective task-branch commits after this report is committed. The parent task file is the only file to stage in the parent repository; the `database` gitlink is staged only in the implementation repository. Merged to implementation `main`: no. Merged to workspace `main`: no.

### Attempt 5 Follow-up

Submitted for `moda_architect` review. The exact DATABASE-003 migration is now present in the pinned submodule, but migration deployment to a persistent local/integration database could not be verified because the documented local PostgreSQL endpoint was unavailable. No downstream Background or system-test work was started.
