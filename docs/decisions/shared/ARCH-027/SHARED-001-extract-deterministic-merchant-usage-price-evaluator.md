---
id: ARCH-027-SHARED-001
architecture_id: ARCH-027
title: Extract deterministic merchant usage-price evaluator
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-03
updated: 2026-10-03
---

# Extract deterministic merchant usage-price evaluator

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

**Superseded before implementation.**

Do not implement a Shared usage-price evaluator for ARCH-027. The task was defined before the Woo top-up purchase semantics were fully clarified. Woo v1 purchases one predefined recovery-credit bundle at the retail price already persisted on its selected `MerchantPricingUsageEvent`; the Woo adapter does not accept an arbitrary quantity and does not evaluate `GRADUATED` / `VOLUME` tiers at charge time.

## Context

The original task assumed the Woo API would receive a usage-event ID plus an arbitrary requested quantity and would therefore need the same `FIXED` / `GRADUATED` / `VOLUME` arithmetic currently used by Admin portfolio economics.

That assumption has been superseded by the confirmed ARCH-027 product contract:

```text
Woo v1 top-up
    -> select one predefined MerchantPricingUsageEvent bundle
    -> require pricingMode = FIXED
    -> read stored fixedUnitAmountMinor + currency
    -> creditsGranted = creditsGrantedPerUnit
    -> snapshot that exact stored amount in WooCommerceBillingOperation
    -> POST one Woo /charges request

merchant buys the same bundle again
    -> new request key
    -> new Woo one-time-charge operation / provider contract
    -> new RecoveryCreditPurchase lot
```

Admin may continue to use its existing `FIXED` / `GRADUATED` / `VOLUME` economics code for catalogue/portfolio analysis. Woo v1 does not require that arithmetic to cross a repository boundary. Creating Shared runtime pricing machinery solely because this task was already authored would violate ARCH-027's minimal-change rule.

## Scope

This file is retained only as a durable coordination/supersession record.

No `moda-interact-shared` implementation, test, package export, version change or publication is authorised by this task.

## Out of Scope

- Adding a Shared usage-price evaluator.
- Moving Admin portfolio-economics code into Shared.
- Changing Admin FIXED/GRADUATED/VOLUME behaviour.
- Adding Woo-specific price calculation.
- Publishing a Shared package version.
- Implementing the Woo API top-up command.
- Defining the API -> Background billing lifecycle/receipt contract.

A later Shared task may be created for a genuine cross-repository lifecycle/receipt contract if ARCH-027 determines that the API -> Background handoff requires one.

## Requirements

### R1 — Superseded tasks are not executable

`ARCH-027-SHARED-001` MUST remain `status: superseded` and MUST NOT be claimed, implemented, published or used as a dependency.

### R2 — Woo v1 consumes a directly stored bundle price

The ARCH-027 Woo adapter must treat one selected `MerchantPricingUsageEvent` as one predefined bundle. Woo-v1 eligibility requires a directly priced `FIXED` event with non-null positive `fixedUnitAmountMinor`; the adapter reads that stored amount/currency and does not evaluate tier pricing.

### R3 — Repeated bundle purchases are separate purchase lots

Buying the same bundle again is a new billing request and a new `RecoveryCreditPurchase` lot. It is not represented as an increased quantity on one Woo charge.

## Work Items

- [x] Mark `ARCH-027-SHARED-001` superseded before implementation.
- [x] Clear downstream `enables`.
- [x] Record the predefined-bundle decision and reason for supersession.
- [x] Record that no Shared pricing export/package publication is produced.

No implementation work items remain.

## Interfaces / Contracts

None.

This superseded task produces no Shared runtime contract or package export.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [x] Task metadata is `status: superseded`.
- [x] `executor` and `claimed_at` remain null and `attempt` remains `0`.
- [x] The task produces no Shared implementation or publication.
- [x] The supersession rationale states that Woo v1 buys one predefined directly priced FIXED bundle per charge.
- [x] No downstream ARCH-027 task is enabled by or should depend on this task.

## Validation

No repository implementation validation is required because the task was superseded before execution.

The architect reconciliation patch that changes this task must pass `git apply --check --whitespace=error-all`, `git apply --whitespace=error-all`, and `git diff --check` against the exact coordination baseline.

## Stop Condition

STOP. Do not execute this task. Do not create a Shared pricing implementation branch/worktree for it.

## Implementation Notes

- Admin portfolio economics remains Admin-owned and unchanged by this supersession.
- Woo v1 top-up pricing is read from the selected event's persisted `fixedUnitAmountMinor` / `currency`.
- `GRADUATED` / `VOLUME` remain existing catalogue capabilities but are not Woo-v1 charge-time pricing modes.
- A separate Shared lifecycle/receipt task may still be justified later if a real API -> Background cross-repository contract is identified.

## Completion Report

### Status

Not Started — superseded before execution

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; no implementation exists.

### Deviations

None.

### Assumptions

- Woo v1 top-ups are predefined bundles.
- One Woo `ONE_TIME_CHARGE` represents one selected bundle.

### Unresolved Issues

None. This task is no longer executable.

### Architectural Concerns

Implementing the original evaluator after the product clarification would introduce unnecessary cross-repository pricing machinery.

## Architect Review

### Review Status

Pending

### Review Notes

Superseded by architecture decision before implementation or claim. No implementation review is applicable. Woo v1 top-ups are predefined, directly priced bundles; the Woo adapter must read the persisted bundle price rather than reevaluate Admin tier-pricing formulas.

### Reviewed Files

Task definition and ARCH-027 architecture coordination only; there is no implementation to review.

### Validation Reviewed

No implementation validation applicable.

### Architecture Conformance

The supersession conforms to ARCH-027's minimal-change rule: do not introduce a cross-repository pricing primitive that the Woo runtime does not require.

### Follow-up

- Do not execute or reclaim `ARCH-027-SHARED-001`.
- Remove it from downstream dependency graphs.
- Keep Admin portfolio economics unchanged.
- Define a Shared lifecycle/receipt contract later only if the API -> Background runtime handoff actually requires a cross-repository schema.
