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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-DATABASE-001
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

Current inspected Background production references are concentrated in:

```text
src/services/billing-subscription-reconciliation.service.ts
src/services/shopify-discount-catalogue.service.ts
```

The billing reconciliation service currently uses the legacy flag both to classify established/post-onboarding lifecycle work and to mark initial activation complete. The discount catalogue uses it as one eligibility condition.

WooCommerce must not depend on a Shopify settings table. The shared Shop field becomes the provider-neutral lifecycle source, but the legacy field remains a compatibility mirror until a later cleanup architecture explicitly removes it.

## Scope

Modify only `moda-interact-background` production/test files required to migrate these onboarding reads/writes.

### Authoritative reads

After this task, Background lifecycle/reconciliation decisions that mean "has this Moda merchant completed the one-time onboarding milestone?" MUST read:

```text
Shop.onboardingCompleted
```

rather than the nested Shopify settings flag.

This includes reconciliation classification branches such as initial-versus-established activation, cycle discovery/rollover/frozen/plan-change decisions and Shopify discount catalogue eligibility where onboarding completion is a condition.

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

inside the same existing transaction/lock boundary.

Do not move provider/network calls into the database transaction and do not alter lock acquisition order.

The shared field is monotonic in normal runtime behavior. No Background path may reset it to false.

### Reinstall semantics

Reinstall/reconciliation must preserve the existing invariant that a merchant who completed onboarding previously does not become a first-time onboarding merchant again.

Do not use plugin/install connection state as the onboarding source.

## Out of Scope

- Removing `ShopSettings.onboardingCompleted`.
- Shopify app migration; owned by ARCH-026-SHOPIFY-001.
- Admin migration; owned by ARCH-026-ADMIN-001.
- Refactoring the 1,900-line reconciliation service beyond changes directly required for this source migration.
- Subscription status/state redesign.
- Billing-provider abstraction.
- Woo billing implementation.
- Queue/event contract changes.
- Gateway/API/WordPress changes.
- System-test terminal validation.

## Requirements

### R1 — Shared field is authoritative for Background lifecycle reads

Background must use `Shop.onboardingCompleted` when determining the one-time Moda onboarding milestone.

### R2 — Existing transaction boundaries are preserved

Adding the shared write must not change the current transaction/lock/provider-I/O boundary.

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
- [ ] Change billing-reconciliation query projections/classification to read `Shop.onboardingCompleted`.
- [ ] Change all Background-owned onboarding completion writes to set shared + legacy flags atomically in the existing transaction.
- [ ] Change Shopify discount catalogue onboarding eligibility to read the shared Shop field.
- [ ] Update focused reconciliation/discount tests without weakening existing lifecycle assertions.
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

DATABASE-001 must be architect-accepted Complete and the Background nested database gitlink must point to the accepted main commit before implementation.

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
- [ ] Transaction boundaries, lock order, provider-call placement, retry scheduling and log semantics remain unchanged.
- [ ] No queue contract or billing state vocabulary changes.
- [ ] Legacy ShopSettings field remains present and is used only as a compatibility mirror in changed Background code.

## Validation

Required categories:

- [ ] Prisma generation from accepted DATABASE-001 gitlink;
- [ ] typecheck;
- [ ] targeted lint;
- [ ] focused billing-subscription reconciliation suite covering fresh activation, established lifecycle, reinstall, rollover, plan change and failure/retry paths;
- [ ] assertions proving shared + legacy completion writes occur in the same transaction;
- [ ] Shopify discount catalogue focused tests;
- [ ] static search/audit of production `src/` legacy onboarding references with compatibility writes documented;
- [ ] production build;
- [ ] `git diff --check`;
- [ ] clean task-worktree evidence.

## Stop Condition

After Work Items, Acceptance Criteria and Validation complete, set the task to `review`, finish the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

Do not use this task as an opportunity to perform the separate maintainability refactor of `billing-subscription-reconciliation.service.ts`. Move only the data source/write needed for the provider-neutral onboarding milestone.

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
