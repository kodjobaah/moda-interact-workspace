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
status: complete
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

- [x] Add the forward ARCH-027 migration.
- [x] Remove kind-based `providerReference` requiredness.
- [x] Remove state-based `providerReference` requiredness.
- [x] Preserve nonblank-if-present validation.
- [x] Preserve provider-reference write-once protection.
- [x] Do not introduce provider/platform-specific replacement constraints.
- [x] Update deterministic ARCH-027 schema validation.
- [x] Update deterministic ARCH-027 migration validation.
- [x] Extend disposable PostgreSQL invariant coverage.
- [x] Verify existing unrelated BillingOperation shape constraints remain intact.

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

- [x] An otherwise valid `PLAN_SWITCH` can persist with `providerReference = NULL`.
- [x] An otherwise valid `CANCEL` can persist with `providerReference = NULL`.
- [x] An otherwise valid operation can persist in `AWAITING_CONFIRMATION` with `providerReference = NULL`.
- [x] An otherwise valid operation can persist in `CONFIRMED` with `providerReference = NULL`.
- [x] No BillingOperation kind globally requires `providerReference`.
- [x] No BillingOperation state globally requires `providerReference`.
- [x] Blank or whitespace-only non-null provider references remain rejected.
- [x] `NULL -> nonblank provider reference` remains allowed.
- [x] Existing provider references cannot be changed to another value.
- [x] Existing provider references cannot be cleared.
- [x] No provider-specific CHECK constraint is introduced.
- [x] No provider-specific trigger is introduced.
- [x] Existing null references are not fabricated or backfilled.
- [x] Existing unrelated operation-shape constraints remain enforced.

## Validation

- [ ] Prisma format/validate as required by the repository (standalone CLI output not supplied; Prisma model unchanged).
- [x] Deterministic ARCH-027 schema validator.
- [x] Deterministic ARCH-027 migration validator.
- [x] Disposable PostgreSQL migration/invariant suite.
- [x] PostgreSQL proof: `PLAN_SWITCH + providerReference NULL`.
- [x] PostgreSQL proof: `CANCEL + providerReference NULL`.
- [x] PostgreSQL proof: `AWAITING_CONFIRMATION + providerReference NULL`.
- [x] PostgreSQL proof: `CONFIRMED + providerReference NULL`.
- [x] PostgreSQL proof: blank non-null reference rejected.
- [x] PostgreSQL proof: `NULL -> value` allowed.
- [x] PostgreSQL proof: `value -> different value` rejected.
- [x] PostgreSQL proof: `value -> NULL` rejected.
- [x] `git diff --check`.

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

Developer-delivered implementation accepted by `moda_architect` on 2026-10-12; the canonical task is `complete`. Patch Attempt 1 and its incremental Attempt 2 correction were applied and validated by the developer. This was a direct developer patch workflow, **not** an agent-launcher task claim: `attempt: 0`, `executor: null`, and `claimed_at: null` remain accurate.

### Files Changed

In `moda-interact-database` (implementation source, not modified by this parent-task closeout patch):

- `prisma/migrations/20261012170000_arch027_relax_billing_operation_provider_reference/migration.sql` (new forward migration).
- `scripts/fixtures/arch027-provider-reference-cases.mjs` (new PostgreSQL invariant fixture).
- `scripts/test-arch027-woocommerce-billing-postgres.mjs` (fresh/upgrade coverage and the Attempt 2 TCP-readiness correction).
- `scripts/validate-arch027-woocommerce-billing-migration.mjs` (effective constraint and readiness checks).
- `scripts/validate-arch027-woocommerce-billing-schema.mjs` (schema-contract checks).

### Work Completed

- Removed the state-wide requirement for non-null provider evidence in `AWAITING_CONFIRMATION` and `CONFIRMED`.
- Replaced the kind-shape check so `PLAN_SWITCH` and `CANCEL` no longer require provider references while preserving their independent operation-shape rules.
- Kept `BillingOperation_providerReference_check` and the `arch027_billing_operation_guard` write-once trigger in effect. No provider identities were invented or backfilled.
- Covered four operation kinds across five states, valid nullable references, blank rejection, write-once transitions, purchase/shop ownership, request identity, and unaffected billing-shape constraints.
- Corrected the disposable PostgreSQL readiness probe and `createdb` to use the final TCP listener rather than the temporary initialization socket.

### Validation Results

- Developer-reported `npm run test:arch027-woocommerce-billing-migration`: **PASS** (`ARCH-027 WooCommerce billing migration scope checks passed`).
- Developer-reported `npm run test:arch027-woocommerce-billing:postgres`: completed with **no errors** after Attempt 2. Supplied output explicitly confirms the PostgreSQL 17 upgrade rehearsal passed and shows successful null-reference state transitions, nonblank rejection, write-once rejection, shop/purchase ownership checks, request-fingerprint checks, and billing intent immutability. The command's clean completion is reported by the developer; a separately quoted fresh-install PASS line was not supplied.
- The previous patch-delivery verification reported ARCH-027 static schema/migration validators, JavaScript syntax and `git apply --check --whitespace=error-all`, actual scratch application, and `git diff --check` passing against the exact 2026-10-12 snapshot. These are not claimed as independent runs on the developer's final checkout.
- Standalone `npm run validate` / Prisma CLI output was not supplied; the Prisma model was unchanged. No persistent-environment migration deployment is evidenced by disposable tests.

### Deviations

- The developer elected incremental, directly applied patches rather than canonical launcher-prepared mirrored task branches/worktrees. No task claim, implementation Git commit, branch push, or parent-report commit is invented. Historical `attempt: 0` is preserved.
- A temporary PostgreSQL initialization/shutdown race blocked the first local rehearsal; the Attempt 2 test-harness correction resolved it and the subsequent rehearsal completed without reported errors.

### Assumptions

- The developer's final successful PostgreSQL rehearsal used both implementation patches and the database revision intended for Shopify consumption.
- The output and explicit developer confirmation of no errors refer to the final patched rehearsal.

### Unresolved Issues

- Database implementation Git commit and canonical parent/Shopify nested-database gitlink synchronization have not been supplied for review. Shopify execution must verify the corrected migration is present in its dedicated implementation worktree.
- Persistent development/production migration deployment is not demonstrated by the disposable PostgreSQL tests.
- A separate Prisma CLI validation result and a separately quoted fresh-install PASS line were not supplied; this evidence limitation is recorded rather than fabricated.

### Architectural Concerns

- The provider-specific obligation to obtain and attribute subscription references stays in the Shopify/Woo application boundary. Relaxed database requiredness does not authorize fabricated identities or ambiguous outcome confirmation.

## Architect Review

### Review Status

Accepted — developer-directed closeout, 2026-10-12. `status: complete` enables the dependent Shopify task. Evidence limitations and the manual-worktree deviation are recorded above.

### Review Notes

- The forward SQL replaces `BillingOperation_kind_shape_check`, drops `BillingOperation_state_provider_reference_check`, and leaves nonblank-if-present / provider-reference write-once integrity intact.
- The accepted test design exercises effective PostgreSQL constraints and all relevant structural invariants; the developer has reported a successful final disposable PostgreSQL rehearsal after the Attempt 2 TCP-readiness correction.
- No historical ARCH-027 migration was rewritten, and this task introduces no Shopify, Woo or other service runtime changes.

### Reviewed Files

- The five database implementation paths recorded in the Completion Report above, as supplied in the previously delivered Attempt 1 and Attempt 2 patches.
- `docs/decisions/database/ARCH-027/DATABASE-003-relax-billing-operation-provider-reference-constraints.md`.
- `docs/decisions/shopify/ARCH-027/SHOPIFY-002-record-shopify-billing-operation-history.md` and its existing Attempt 3 architect review.

### Validation Reviewed

- Reported deterministic ARCH-027 validator success and final developer-run PostgreSQL 17 upgrade rehearsal, including nonblank, write-once, null state transitions, unchanged kind shape and purchase ownership.
- The developer reported a clean end to the PostgreSQL test command; this architect did not rerun Docker/PostgreSQL in the review environment.
- No claim is made that Prisma CLI validation, a persistent database migration, or Git worktree synchronization was independently verified.

### Architecture Conformance

- Accepted: provider-neutral nullable evidence with nonblank-if-present and write-once constraints preserved. Provider-specific requiredness remains with the owning application.
- Task completion is approved at the developer's direction despite the recorded standalone Prisma CLI and materialisation evidence gaps; neither gap is silently represented as a passing validation.

### Follow-up

- Unblock `ARCH-027-SHOPIFY-002` as `ready`, preserving its Attempt 3 history; the next claim is Attempt 4.
- Before attempting Shopify execution or integration tests, incorporate the Database commit containing the new migration into Shopify's nested `database` submodule and verify the target database has received the migration where required.
- Do not begin any system-test work as part of this acceptance; it remains terminal and separately gated.
- Defer all `docs/decisions/**/_index.md` updates until explicitly authorized.
