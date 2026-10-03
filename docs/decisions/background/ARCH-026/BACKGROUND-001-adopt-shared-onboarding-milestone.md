---
id: ARCH-026-BACKGROUND-001
architecture_id: ARCH-026
title: Adopt the shared Shop onboarding milestone in Background billing workflows
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-10-03T16:42:32Z
attempt: 2
depends_on:
  - ARCH-026-DATABASE-001
  - ARCH-025-BACKGROUND-007
enables:
  - ARCH-026-ADMIN-001
  - ARCH-026-BACKGROUND-002
created: 2026-10-02
updated: 2026-10-03
---

# Adopt the shared Shop onboarding milestone in Background billing workflows

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Migrate Background billing/subscription reconciliation and Shopify discount-catalogue eligibility from the legacy Shopify-specific `ShopSettings.onboardingCompleted` source to provider-neutral `commerce.Shop.onboardingCompleted`, while continuing to mirror successful onboarding completion to `shopify.ShopSettings.onboardingCompleted` for transitional compatibility.

Preserve all existing reconciliation classification, locking, retry, billing-period, pending-plan, reinstall and discount-sync semantics.

## Context

DATABASE-001 adds and backfills:

```text
commerce.Shop.onboardingCompleted
```

while retaining:

```text
shopify.ShopSettings.onboardingCompleted
```

ARCH-025 has completed the billing-subscription reconciliation maintainability refactor. The previous 1,900-line implementation is now a thin coordinator plus extracted collaborators. The current inspected production references to the legacy onboarding milestone are owned by:

```text
src/services/billing-subscription-reconciliation/reconciliation-context.ts
src/services/billing-subscription-reconciliation/classification.ts
src/services/billing-subscription-reconciliation/reconciliation-queue.service.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts
src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts
src/services/shopify-discount-catalogue.service.ts
```

`ReconciliationContextService` owns the durable Shop/subscription snapshot, `classification.ts` owns lifecycle classification, `ReconciliationQueueService` owns startup reconstruction eligibility, and the coordinator owns only dispatch/logging. Successful initial activation and reinstall completion writes now live in their dedicated lifecycle services.

ARCH-025 also deliberately preserved the pre-existing `lockShop(...)` SQL text in `billing-subscription-reconciliation/locking.ts`. That helper currently targets `"shopify"."Shop"`, while the canonical Shop table is `"commerce"."Shop"`. ARCH-025 was move-only and explicitly did not correct that target. Because this ARCH-026 task makes the shared Shop row authoritative and writes it in onboarding-completion transactions, correcting that lock target and establishing a safe lock order for those dual-write completion transactions is now directly in scope.

The discount catalogue uses the legacy flag as one eligibility condition.

WooCommerce must not depend on a Shopify settings table. The shared Shop field becomes the provider-neutral lifecycle source, but the legacy field remains a compatibility mirror until a later cleanup architecture explicitly removes it.

## Scope

Modify only `moda-interact-background` production/test files required to migrate these onboarding reads/writes.

### Authoritative reads

After this task, Background lifecycle/reconciliation decisions that mean "has this Moda merchant completed the one-time onboarding milestone?" MUST read:

```text
Shop.onboardingCompleted
```

rather than the nested Shopify settings flag.

This includes reconciliation classification branches such as initial-versus-established activation, cycle discovery/rollover/frozen/plan-change decisions, startup reconstruction eligibility and Shopify discount catalogue eligibility where onboarding completion is a condition.

The extracted reconciliation boundary MUST make the shared field explicit rather than carrying the legacy relation forward:

- `ReconciliationContextService` selects top-level `Shop.onboardingCompleted`;
- `ReconciliationClassificationRow` carries `onboardingCompleted: boolean` rather than `settings.onboardingCompleted`;
- classification, skip telemetry and coordinator accepted-job logging consume that top-level value;
- `ReconciliationQueueService.reconstruct()` filters on top-level `Shop.onboardingCompleted`;
- no lifecycle handler should need `ShopSettings` merely to determine whether onboarding completed.

Do not change provider-specific conditions that are genuinely Shopify-owned.

### Completion writes

Every Background transaction that currently establishes onboarding completion by writing:

```text
ShopSettings.onboardingCompleted = true
```

must set both:

```text
Shop.onboardingCompleted = true
ShopSettings.onboardingCompleted = true
```

inside the same existing transaction/provider-I/O boundary.

Because the shared Shop row is now part of the completion write, this task explicitly authorises the minimum lock correction required for those completion transactions:

- correct `lockShop(...)` to lock `"commerce"."Shop"`;
- where onboarding completion writes Shop + ShopSettings + Subscription state, acquire the three lifecycle row locks in `Shop -> ShopSettings -> Subscription` order before the authoritative writes;
- where a delegated helper acquires the Subscription lock (for example same-plan rollover), acquire Shop and ShopSettings before invoking that helper;
- do not change lock order for retry/failure/cycle/plan-change transactions that do not establish onboarding completion.

Do not move provider/network calls into the database transaction. Do not introduce a second lock abstraction.

The shared field is monotonic in normal runtime behavior. No Background path may reset it to false.

### Reinstall semantics

Reinstall/reconciliation must preserve the existing invariant that a merchant who completed onboarding previously does not become a first-time onboarding merchant again.

Do not use plugin/install connection state as the onboarding source.

## Out of Scope

- Removing `ShopSettings.onboardingCompleted`.
- Shopify app migration; owned by ARCH-026-SHOPIFY-001.
- Admin migration; owned by ARCH-026-ADMIN-001.
- Further restructuring of the ARCH-025 reconciliation collaborators or coordinator beyond changes directly required for this source/dual-write migration.
- Subscription status/state redesign.
- Billing-provider abstraction.
- Woo billing implementation.
- Queue/event contract changes.
- Gateway/API/WordPress changes.
- System-test terminal validation.

## Requirements

### R1 — Shared field is authoritative for Background lifecycle reads

Background must use `Shop.onboardingCompleted` when determining the one-time Moda onboarding milestone.

### R2 — Transaction/provider boundaries are preserved and completion locking is safe

Provider/network placement and transaction boundaries remain unchanged. The only authorised lock change is the shared-Shop correction/canonical completion ordering defined in Scope.

### R3 — Successful completion is mirrored

Every Background-owned transition that establishes onboarding completion sets both shared and legacy flags to true in the same transaction.

### R4 — No reset to onboarding

Established merchant reconciliation, reinstall, cancellation, plan change, rollover or billing attention must not reset the shared milestone.

### R5 — No lifecycle redesign

Do not add a new durable activation/account status; preserve existing Subscription projection and pending-plan semantics.

### R6 — Discount behavior is unchanged except source

Shopify discount catalogue eligibility retains the same behavioral conditions while replacing only the onboarding source.

## Work Items

- [ ] Update the Background repository's nested database gitlink to accepted DATABASE-001 and regenerate Prisma.
- [ ] Update `reconciliation-context.ts` to select top-level `Shop.onboardingCompleted` and stop selecting ShopSettings solely for lifecycle classification.
- [ ] Update `classification.ts`, coordinator logging and `reconciliation-queue.service.ts` to consume the shared top-level milestone.
- [ ] Correct `lockShop(...)` to target `"commerce"."Shop"` and update focused lock tests.
- [ ] Change `initial-activation-reconciliation.service.ts` completion transactions to set shared + legacy flags atomically using the authorised completion lock order.
- [ ] Change every `reinstall-reconciliation.service.ts` path that currently establishes onboarding completion to set shared + legacy flags atomically; preserve provider/retry/rollover semantics.
- [ ] Change Shopify discount catalogue onboarding eligibility to read the shared Shop field.
- [ ] Update focused extracted reconciliation/discount tests without weakening existing lifecycle assertions.
- [ ] Add static audit coverage documenting any remaining legacy field references as compatibility writes only.

## Interfaces / Contracts

### Database contract owner

`ARCH-026-DATABASE-001`

### Authoritative lifecycle field

```text
commerce.Shop.onboardingCompleted
```

### Retained compatibility mirror

```text
shopify.ShopSettings.onboardingCompleted
```

No queue/shared-package contract changes are introduced.

## Dependencies

- `ARCH-026-DATABASE-001`
- `ARCH-025-BACKGROUND-007`

DATABASE-001 must be architect-accepted Complete and the Background nested database gitlink must point to the accepted main commit before implementation. ARCH-025-BACKGROUND-007 is Complete and establishes the extracted reconciliation ownership boundaries this task must modify rather than recreating the former monolith.

## Enables

- `ARCH-026-ADMIN-001`
- `ARCH-026-BACKGROUND-002`

ADMIN-001 additionally depends on SHOPIFY-001 so Admin switches its cross-platform presentation only after both current onboarding completion writers maintain the shared field. BACKGROUND-002 serializes the later shared international-context source migration in the same repository.

## Acceptance Criteria

- [ ] Background reconciliation classification reads shared `Shop.onboardingCompleted` rather than legacy ShopSettings state.
- [ ] Every Background initial-activation completion path sets shared and legacy onboarding flags to true in the same existing transaction.
- [ ] No Background production path resets shared onboarding completion to false.
- [ ] Established reinstall/rollover/plan-change/frozen paths retain their existing classification semantics.
- [ ] Shopify discount catalogue behavior is unchanged except that onboarding eligibility reads the shared field.
- [ ] Transaction boundaries, provider-call placement, retry scheduling and log semantics remain unchanged; onboarding-completion transactions use the explicitly authorised `Shop -> ShopSettings -> Subscription` lock order and no other lifecycle lock ordering changes.
- [ ] No queue contract or billing state vocabulary changes.
- [ ] Legacy ShopSettings field remains present and is used only as a compatibility mirror in changed Background code.
- [ ] `lockShop(...)` targets the canonical `"commerce"."Shop"` table; no production lock SQL references `"shopify"."Shop"`.

## Validation

Required categories:

- [ ] `npm run prisma:generate` from the accepted DATABASE-001 gitlink and `npm run prisma:validate`;
- [ ] focused `vitest` suites for `reconciliation-context`, `classification`, `reconciliation-queue`, coordinator dispatch/logging, initial activation, reinstall and locking;
- [ ] focused regression proving every successful Background-owned onboarding completion writes shared + legacy milestones in one transaction and uses the authorised lock order;
- [ ] focused Shopify discount-catalogue eligibility test proving the shared Shop milestone is authoritative; add a direct service test if the current worker tests do not exercise `getEligibility(...)`;
- [ ] existing `billing-subscription-reconciliation.service.test.ts` regression suite remains active; update fixtures/assertions to the shared top-level milestone without weakening lifecycle coverage;
- [ ] static search/audit of production `src/` legacy onboarding references with compatibility writes documented;
- [ ] `npm run test:unit`;
- [ ] `npm test`;
- [ ] `npm run build` (the repository build runs TypeScript compilation);
- [ ] `git diff --check`;
- [ ] clean task-worktree evidence.

The repository currently declares no standalone `lint` or `typecheck` npm script. Do not invent one for this task; use the repository-declared build plus focused/full tests above.

## Stop Condition

After Work Items, Acceptance Criteria and Validation complete, set the task to `review`, finish the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

ARCH-025 already completed the maintainability refactor. Do not collapse or bypass its extracted owners. Make the source migration in the canonical collaborator that now owns each behavior, and keep `billing-subscription-reconciliation.service.ts` as the coordinator.

The `lockShop(...)` schema-target correction and onboarding-completion lock ordering are authorised only because the shared Shop row becomes part of the durable completion boundary in this task; do not broaden this into general lock cleanup.

The legacy field remains because other consumers are being migrated incrementally. This is pre-production transitional compatibility, not a new permanent dual-source design.

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

- DATABASE-001 adds/backfills the shared Shop milestone and keeps the legacy field.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Developer Override - Reopened (2026-10-03)

- Previous accepted attempt: none. Attempt 1 was claimed and remained in progress; no implementation changes or acceptance record exist.
- Reopen reason: the developer explicitly requested `/moda_developer_update ARCH-026-BACKGROUND-001 reopen` after the task launcher declined to prepare the existing active claim. Reopening clears that claim so the task can return to normal preparation without losing Attempt 1 history.
- Transition: `in_progress` -> `ready`; `executor` and `claimed_at` cleared; `attempt` remains `1`.
- This reopen is not a claim. `execution_mode: agent` and `completion_mode: automatic` remain unchanged. The implementation task worktree contains no task changes and remains at `origin/main`.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
