---
id: ARCH-027-DATABASE-003
architecture_id: ARCH-027
title: Relax BillingOperation provider-reference constraints for provider-neutral recurring history
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 11
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-DATABASE-001
  - ARCH-027-DATABASE-002
enables:
  - ARCH-027-SHOPIFY-002
created: 2026-10-12
updated: 2026-10-12
---

# Relax BillingOperation provider-reference constraints for provider-neutral recurring history

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Correct the accepted `billing.BillingOperation` database constraints so the generic optional `providerReference` can remain null when a provider does not expose a stable operation/subscription reference, while preserving operation shape, idempotency, nonblank-if-present validation and write-once provider-reference semantics.

## Context

`ARCH-027-DATABASE-001` intentionally defined `BillingOperation.providerReference` as provider-neutral optional evidence. Its accepted task text also states that Shopify may record its existing stable billing reference **where available** and that the generic ledger must not manufacture one.

The accepted migration nevertheless imposes two stronger global constraints:

```text
BillingOperation_kind_shape_check
    PLAN_SWITCH -> providerReference IS NOT NULL
    CANCEL      -> providerReference IS NOT NULL

BillingOperation_state_provider_reference_check
    AWAITING_CONFIRMATION -> providerReference IS NOT NULL
    CONFIRMED             -> providerReference IS NOT NULL
```

That is incompatible with Shopify managed pricing. Shopify Partner `activeSubscription.legacySubscriptionId` is nullable, and subscriptions created natively in managed pricing legitimately have no legacy Admin `AppSubscription` GID. The current Shopify provider adapter therefore correctly exposes `ProviderSubscription.providerSubscriptionId: string | null` and can persist an active recurring subscription with no stable provider subscription reference.

The database must not force Shopify to fabricate a lifecycle-event ID, Moda identifier, request key or other non-provider identity merely to persist command history.

This is a correction to the provider-neutral database contract. It does not change Woo command semantics: Woo application/Background paths must continue requiring the recurring/charge UUIDs their provider workflow actually supplies.

## Scope

Modify only `moda-interact-database` plus the assigned parent task report.

Create one new forward migration after the accepted ARCH-027 migrations. Do not rewrite `20261008110000_arch027_woocommerce_billing_persistence`.

Update the ARCH-027 database validators/PostgreSQL integration coverage necessary to prove the corrected constraints.

## Out of Scope

- Shopify command-handler or reconciliation implementation.
- Woo API/Background command behavior.
- Changing BillingOperation kinds or states.
- Changing request-key/fingerprint semantics.
- Changing provider-reference write-once semantics.
- Adding a provider discriminator to BillingOperation.
- Historical Shopify charge correlation.
- Rewriting accepted historical migrations.

## Requirements

### R1 — Preserve generic optional provider evidence

`BillingOperation.providerReference` remains nullable provider evidence.

The database MUST keep:

```text
providerReference IS NULL
OR btrim(providerReference) <> ''
```

The database MUST NOT require a provider reference merely because an operation is `PLAN_SWITCH` or `CANCEL`.

### R2 — Correct kind-shape constraint

Replace `BillingOperation_kind_shape_check` so the existing shape requirements remain unchanged except for removal of the global provider-reference requirement from:

```text
PLAN_SWITCH
CANCEL
```

All current plan/usage-event/quote/purchase shape constraints must remain intact.

### R3 — Correct state/reference constraint

Remove the global assumption that `AWAITING_CONFIRMATION` and `CONFIRMED` always imply a non-null provider reference.

A provider-neutral operation may reach those states from trusted provider business-outcome evidence even when that provider exposes no stable operation/subscription reference.

The migration MUST drop `BillingOperation_state_provider_reference_check` (or replace it with an equivalent constraint that does not require a provider reference for those generic states).

Provider-specific services remain free to impose stronger requirements. In particular, this correction does not authorize Woo code to omit provider UUIDs it already receives, and it does not change the separate Shopify one-time-charge reconciliation rule that requires a real `Charge.chargeId` before that workflow marks the charge operation confirmed.

### R4 — Preserve write-once semantics

The existing update guard MUST continue to enforce:

```text
NULL -> nonblank value      allowed exactly once
non-null -> same value      allowed
non-null -> different value rejected
non-null -> NULL            rejected
```

The correction MUST NOT make an existing provider reference mutable.

### R5 — No fabricated/backfilled identities

No data migration may populate missing provider references with:

```text
BillingOperation.requestKey
BillingOperation.id
Subscription.id
Shop.id
Shopify lifecycle-event IDs
Shopify App Events idempotency keys
```

Existing null provider references remain null.

### R6 — Forward-only correction

Create a new ARCH-027 migration that alters only the affected checks/validation required by this task. No destructive table rewrite or historical migration edit is required.

## Work Items

- [ ] Add the forward ARCH-027 migration correcting `BillingOperation_kind_shape_check`.
- [ ] Remove/replace the global `BillingOperation_state_provider_reference_check` requirement.
- [ ] Preserve `BillingOperation_providerReference_check` and the existing write-once update guard.
- [ ] Update deterministic schema/migration validation for the corrected contract.
- [ ] Extend disposable PostgreSQL coverage for nullable recurring provider references and write-once behavior.
- [ ] Regenerate schema-derived artifacts only where the repository contract requires them.

## Interfaces / Contracts

Corrected database contract:

```text
BillingOperation.providerReference
    nullable generic provider evidence
    nonblank when present
    write-once once known
```

Provider-specific ownership remains outside the database shape check:

```text
Woo
    command/reconciliation services continue requiring provider UUIDs where Woo supplies them

Shopify managed pricing
    recurring BillingOperation may have providerReference = NULL when legacySubscriptionId is unavailable
```

No Shared runtime contract changes are introduced.

## Dependencies

- `ARCH-027-DATABASE-001`
- `ARCH-027-DATABASE-002`

Both are Complete.

## Enables

- `ARCH-027-SHOPIFY-002`

## Acceptance Criteria

- [ ] `PLAN_SWITCH` can be inserted with `providerReference = NULL` while all existing quote/plan shape rules remain enforced.
- [ ] `CANCEL` can be inserted with `providerReference = NULL` while all existing cancel shape rules remain enforced.
- [ ] `INITIATING`, `AWAITING_CONFIRMATION`, `CONFIRMED`, `OUTCOME_UNKNOWN` and `FAILED` do not globally require `providerReference` merely because of state.
- [ ] Blank provider references remain rejected when non-null.
- [ ] Existing provider-reference write-once semantics remain enforced by PostgreSQL.
- [ ] No existing null provider reference is fabricated or backfilled.
- [ ] Existing Woo-specific application tests/fixtures remain structurally compatible; this task does not change Woo runtime behavior.

## Validation

- [ ] Prisma format/validate as required by the repository.
- [ ] deterministic ARCH-027 schema validator.
- [ ] deterministic ARCH-027 migration validator.
- [ ] disposable PostgreSQL migration/invariant suite proving the corrected nullable-reference cases.
- [ ] PostgreSQL proof that `NULL -> value` is allowed once and `value -> different/NULL` remains rejected.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to `moda_architect` and STOP. Do not begin `ARCH-027-SHOPIFY-002`.

## Implementation Notes

Keep this correction narrow. `providerReference` is provider evidence, not Moda command identity. The database should enforce generic structural integrity and write-once evidence, while provider-specific tasks enforce whether their provider is expected to supply a reference for a particular workflow.

Do not add a cross-table trigger merely to recreate the removed global assumption by inspecting `Shop.platform`; this correction intentionally restores the already-documented provider-neutral optional-reference model.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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

Pending implementation.

### Follow-up

None
