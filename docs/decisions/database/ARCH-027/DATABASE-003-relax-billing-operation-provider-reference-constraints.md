---
id: ARCH-027-DATABASE-003
architecture_id: ARCH-027
title: Remove BillingOperation provider-reference requiredness from database constraints
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

# Remove BillingOperation provider-reference requiredness from database constraints

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Remove provider/workflow-specific `BillingOperation.providerReference` requiredness from PostgreSQL. The database must treat `providerReference` as nullable generic provider evidence, enforce only provider-neutral structural integrity and write-once semantics, and leave the question of whether a particular provider workflow requires a reference to the application/service that owns that workflow.

## Context

`ARCH-027-DATABASE-001` introduced `billing.BillingOperation` as a provider-neutral billing-operation ledger with optional provider evidence.

The accepted migration nevertheless embeds provider/workflow semantics into PostgreSQL by requiring a non-null provider reference for:

```text
PLAN_SWITCH
CANCEL
AWAITING_CONFIRMATION
CONFIRMED
```

Those are not generic database invariants.

Shopify managed pricing demonstrates the problem directly. A valid active Shopify subscription may have `legacySubscriptionId = null`, so a legitimate `PLAN_SWITCH` or `CANCEL` command can exist without a stable Shopify subscription identifier. Other providers may expose different identifiers and impose different requirements.

The correct ownership boundary is:

```text
Database
    providerReference may be NULL
    if present, it must be nonblank
    once present, it is write-once

Application/provider workflow
    decides whether providerReference is required
    for a particular provider operation or state transition
```

PostgreSQL must not encode Shopify, WooCommerce, or any future provider's workflow-specific evidence requirements.

## Scope

Modify only `moda-interact-database` plus the assigned parent task report.

Create one new forward migration after the accepted ARCH-027 migrations. Do not rewrite `20261008110000_arch027_woocommerce_billing_persistence`.

Update the deterministic ARCH-027 validators and disposable PostgreSQL coverage required to prove the corrected provider-neutral contract.

## Out of Scope

- Shopify command-handler implementation.
- Shopify reconciliation implementation.
- Woo API behaviour.
- WooCommerce plugin behaviour.
- Background billing workflow implementation.
- Moving provider-specific validation into application repositories under this database task.
- Adding provider-specific database constraints.
- Adding a provider discriminator to `BillingOperation`.
- Changing BillingOperation kinds or states.
- Changing request-key or request-fingerprint semantics.
- Historical Shopify charge reconciliation.
- Rewriting accepted historical migrations.
- Fabricating or backfilling missing provider references.

## Requirements

### R1 — Provider reference is nullable generic evidence

`BillingOperation.providerReference` remains nullable.

PostgreSQL MUST allow `providerReference = NULL` for any otherwise structurally valid BillingOperation row regardless of provider, operation kind, or operation state.

If `providerReference` is non-null, PostgreSQL MUST continue requiring it to contain a nonblank value.

Equivalent invariant:

```text
providerReference IS NULL
OR btrim(providerReference) <> ''
```

### R2 — Remove kind-based provider-reference requiredness

Correct `BillingOperation_kind_shape_check`.

Existing operation-shape rules must remain intact except any rule whose sole purpose is to require `providerReference`.

PostgreSQL MUST NOT require `providerReference` merely because:

```text
kind = PLAN_SWITCH
kind = CANCEL
```

Existing requirements concerning previous/current plan IDs, usage-event IDs, quote IDs, purchase IDs, amounts, currencies, and other operation-specific columns must remain unchanged unless directly necessary for removing provider-reference requiredness.

### R3 — Remove state-based provider-reference requiredness

Remove the global assumption that `AWAITING_CONFIRMATION` or `CONFIRMED` implies a non-null `providerReference`.

Drop `BillingOperation_state_provider_reference_check`, or replace it only with provider-neutral validation that does not require a reference.

No `BillingOperation` state should globally imply provider-reference presence.

Whether a provider-specific application may enter a state without a reference is an application-layer rule.

### R4 — Do not recreate provider semantics elsewhere in PostgreSQL

The migration MUST NOT replace the removed constraints with:

- provider-specific CHECK constraints;
- triggers that inspect `Shop.platform`;
- triggers that inspect provider-specific tables;
- cross-table provider-reference requiredness;
- operation-kind exceptions designed around Shopify, WooCommerce, or another provider.

The resulting database model must remain provider-neutral.

### R5 — Preserve nonblank-if-present validation

The existing generic rule remains:

```text
NULL       allowed
nonblank   allowed
blank      rejected
whitespace rejected
```

### R6 — Preserve write-once provider evidence

Existing write-once behaviour MUST remain enforced.

Allowed:

```text
NULL -> nonblank provider reference
existing reference -> same reference
```

Rejected:

```text
reference A -> reference B
reference -> NULL
```

The task removes requiredness. It does not make provider evidence mutable.

### R7 — Provider-specific requiredness belongs to application ownership

No application implementation is part of this database task.

The architecture boundary after this task is explicitly:

```text
moda-interact-database
    owns nullable storage
    owns nonblank-if-present validation
    owns write-once evidence integrity

provider-owning application/service
    decides whether providerReference is required
    before a particular command or state transition
```

Examples:

```text
Shopify recurring operation
    stable subscription reference may legitimately be unavailable;
    Shopify application logic decides whether available provider
    outcome evidence is sufficient to advance the operation.

Shopify ONE_TIME_CHARGE
    INITIATING + providerReference NULL is valid;
    later Historical Events reconciliation may attach Charge.chargeId.

Woo / another provider
    if its workflow requires a provider UUID/reference before a
    particular transition, the owning application validates that requirement.
```

The database must not impose those rules globally.

### R8 — No fabricated identities

No migration may populate a missing `providerReference` with:

```text
BillingOperation.requestKey
BillingOperation.id
Subscription.id
Shop.id
Shopify lifecycle-event ID
Shopify App Events idempotency key
Woo local request identifier
any other Moda-generated identity
```

Existing null references remain null.

### R9 — Forward-only correction

Create a new ARCH-027 migration.

Do not edit accepted migration history.

The migration should narrowly:

```text
drop or replace affected CHECK constraints
preserve generic structural checks
preserve write-once protection
```

## Work Items

- [ ] Add the forward ARCH-027 migration.
- [ ] Remove kind-based `providerReference` requiredness.
- [ ] Remove state-based `providerReference` requiredness.
- [ ] Preserve nonblank-if-present validation.
- [ ] Preserve provider-reference write-once protection.
- [ ] Do not introduce provider/platform-specific replacement constraints.
- [ ] Update deterministic ARCH-027 schema validation.
- [ ] Update deterministic ARCH-027 migration validation.
- [ ] Extend disposable PostgreSQL invariant coverage.
- [ ] Verify existing unrelated BillingOperation shape constraints remain intact.

## Interfaces / Contracts

Corrected database contract:

```text
BillingOperation.providerReference
    nullable generic provider evidence
    nonblank when present
    write-once once populated
```

Provider-specific requiredness is owned by the application/service implementing that provider workflow.

No Shared runtime contract change is introduced.

## Dependencies

- `ARCH-027-DATABASE-001`
- `ARCH-027-DATABASE-002`

Both must be Complete before execution.

## Enables

- `ARCH-027-SHOPIFY-002`

## Acceptance Criteria

- [ ] An otherwise valid `PLAN_SWITCH` can persist with `providerReference = NULL`.
- [ ] An otherwise valid `CANCEL` can persist with `providerReference = NULL`.
- [ ] An otherwise valid operation can persist in `AWAITING_CONFIRMATION` with `providerReference = NULL`.
- [ ] An otherwise valid operation can persist in `CONFIRMED` with `providerReference = NULL`.
- [ ] No BillingOperation kind globally requires `providerReference`.
- [ ] No BillingOperation state globally requires `providerReference`.
- [ ] Blank or whitespace-only non-null provider references remain rejected.
- [ ] `NULL -> nonblank provider reference` remains allowed.
- [ ] Existing provider references cannot be changed to another value.
- [ ] Existing provider references cannot be cleared.
- [ ] No provider-specific CHECK constraint is introduced.
- [ ] No provider-specific trigger is introduced.
- [ ] Existing null references are not fabricated or backfilled.
- [ ] Existing unrelated operation-shape constraints remain enforced.

## Validation

- [ ] Prisma format/validate as required by the repository.
- [ ] Deterministic ARCH-027 schema validator.
- [ ] Deterministic ARCH-027 migration validator.
- [ ] Disposable PostgreSQL migration/invariant suite.
- [ ] PostgreSQL proof: `PLAN_SWITCH + providerReference NULL`.
- [ ] PostgreSQL proof: `CANCEL + providerReference NULL`.
- [ ] PostgreSQL proof: `AWAITING_CONFIRMATION + providerReference NULL`.
- [ ] PostgreSQL proof: `CONFIRMED + providerReference NULL`.
- [ ] PostgreSQL proof: blank non-null reference rejected.
- [ ] PostgreSQL proof: `NULL -> value` allowed.
- [ ] PostgreSQL proof: `value -> different value` rejected.
- [ ] PostgreSQL proof: `value -> NULL` rejected.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, finish the Completion Report, set the task to review, return control to `moda_architect`, and STOP.

Do not begin `ARCH-027-SHOPIFY-002`.

## Implementation Notes

Keep the migration deliberately narrow.

The target boundary is:

```text
DATABASE
    structural integrity

APPLICATION
    provider semantics
```

Do not add `Shop.platform` checks or any database mechanism that decides when Shopify, WooCommerce, or a future provider must supply a provider reference.

The provider-reference write-once rule remains appropriate at database level because it protects durable evidence integrity independently of provider semantics.

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
