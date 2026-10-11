---
id: ARCH-027-DATABASE-002
architecture_id: ARCH-027
title: Correct Woo completed-refund monetary audit optionality
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-DATABASE-001
enables:
  - ARCH-027-BACKGROUND-005
created: 2026-10-11
updated: 2026-10-11
---

# Correct Woo completed-refund monetary audit optionality

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

Restore the agreed ARCH-027 invariant that a verified Woo refund completes the exact previously held recovery-credit allowance without depending on optional provider monetary audit fields, while retaining every actual provider-settlement identity, state, format and ownership guard.

## Context

`ARCH-027-DATABASE-001` Attempt 2 was previously accepted and its PostgreSQL migration is immutable historical evidence. It added `billing."RecoveryCreditRefund"` constraint `RecoveryCreditRefund_woocommerce_settlement_check`, requiring `providerAmount` and `providerCurrency` to be non-NULL on Woo `COMPLETED` rows. That requirement conflicts with the canonical ARCH-027 refund design and `ARCH-027-BACKGROUND-005` R11/R13: signed `saas_billing_contract.refunded` status and exact local hold determine credit settlement; `amount_refunded` is optional audit-only evidence. In BACKGROUND-005 Attempt 2, malformed optional money is correctly treated as unavailable (`NULL`), but the database rejects `COMPLETED` with SQLSTATE `23514`.

This is a **bounded database contract correction**, not a reopening or rejection of the accepted DATABASE-001 task. No fallback amount or synthetic currency may be invented.

## Scope

Only `moda-interact-database` owns the implementation and validation changes necessary to reconcile the effective Woo refund check constraint:

- Add a new forward-only Prisma SQL migration that replaces the effective `RecoveryCreditRefund_woocommerce_settlement_check` with the corrected form.
- Preserve the existing field types and all other billing constraints, triggers, ownership guards and provider-specific rules.
- Extend the ARCH-027 migration/static validators as necessary to check the **effective post-migration contract**, not just the historical DATABASE-001 migration text.
- Extend disposable PostgreSQL fresh/upgrade fixtures to prove the corrected positive and negative invariants.

## Out of Scope

- Editing the already accepted `20261008110000_arch027_woocommerce_billing_persistence/migration.sql`.
- Removing either `providerAmount` or `providerCurrency`, adding a Woo-specific refund table or status, changing Shopify refund checks or monetary correction behaviour.
- Changing BACKGROUND-005 parsing, receipt processing or allowance accounting, which remain owned by `moda_background`.
- Changing API, WooCommerce plugin, Admin, Shared or provider network code.
- Inventing/refilling provider monetary audit values to pass validation.
- Updating any `docs/decisions/**/_index.md` or architecture `_index.md` file.

## Requirements

1. For `provider = 'WOOCOMMERCE'`, `providerAmount` and `providerCurrency` **must both be NULL or both non-NULL** on every row, regardless of status.
2. When provided, amount must be nonnegative and currency must be an uppercase ISO-like three-letter code (preserve the existing PostgreSQL `COLLATE "C"` pattern check).
3. `status = 'COMPLETED'` must retain `finalCreditQuantity > 0`, a nonblank `providerReference`, `providerActionKind = 'REFUND'` and non-NULL `providerConfirmedAt`.
4. `status = 'COMPLETED'` with both monetary fields NULL must now be permitted when the other completed-refund invariants hold; similarly, a valid populated pair remains permitted.
5. The change must not weaken Shopify refund constraints or alter provider-vs-purchase/shop ownership triggers and billing-operation identity rules.
6. Existing rows that satisfy the accepted constraint must continue to satisfy the corrected constraint; no data rewrite, bulk status update or forced value is needed.
7. The new migration must be safe on a fresh schema and an upgrade from the accepted DATABASE-001 state. Keep the historical migration unchanged, and rely on an atomic `ALTER TABLE` constraint replacement where supported.

## Work Items

- [ ] Inspect the effective DATABASE-001 `RecoveryCreditRefund_woocommerce_settlement_check` and the accepted DATABASE-001 PostgreSQL fixtures.
- [ ] Add one bounded forward-only migration preserving completed-refund identity/quantity and audit-pair rules while permitting both monetary fields NULL.
- [ ] Update relevant static migration/contract validator(s) to enforce effective final DDL without invalidating legitimate historical migration checks.
- [ ] Add PostgreSQL positive fixtures for Woo `COMPLETED` with both money fields NULL and with both populated, including provider-action/reference/confirmation evidence.
- [ ] Add independent negative fixtures for only amount, only currency, negative amount, malformed currency, missing provider reference/action/confirmation or nonpositive final quantity.
- [ ] Prove existing Shopify refund constraints and Woo purchase-Shop/provider ownership guards remain intact.
- [ ] Run fresh and accepted-baseline upgrade rehearsals on disposable PostgreSQL; record SQLSTATE/errors and cleanup evidence.

## Interfaces / Contracts

Affected table: `billing."RecoveryCreditRefund"`.

Effective constraint: `RecoveryCreditRefund_woocommerce_settlement_check`.

For Woo `COMPLETED` rows: accepted signed provider refund plus exact frozen credit quantity is required, but `providerAmount` and `providerCurrency` are an **optional matched audit pair**, not an acceptance gate. Their values may neither determine nor validate `finalCreditQuantity`.

Producer/consumer: `moda-interact-background` owns BACKGROUND-005 processing and consumes the migrated PostgreSQL contract via the canonical Prisma database submodule. No new Shared runtime contract or published package is required.

## Dependencies

- `ARCH-027-DATABASE-001` — Complete and architect accepted.

## Enables

- `ARCH-027-BACKGROUND-005` — Currently Blocked at Attempt 2; it may be re-gated only after this task is accepted **and the new Database-main gitlink is integrated into Background**.

## Acceptance Criteria

- [ ] Completed Woo refund with valid provider identity/action/confirmation and positive finalCreditQuantity succeeds with both monetary fields NULL.
- [ ] Completed Woo refund with a valid populated audit pair succeeds.
- [ ] Exactly one monetary field populated is rejected in both orientations, including non-COMPLETED Woo states.
- [ ] Invalid amount/currency and missing required completed-refund identity/quantity evidence are rejected.
- [ ] Shopify refund lifecycle constraints and all accepted purchase/shop/provider/operation guards remain enforced.
- [ ] Historical DATABASE-001 migration is byte-identical; only the new forward migration and necessary test/validator files change.
- [ ] Fresh and accepted-baseline upgrade PostgreSQL rehearsals pass, including the effective final constraint on both paths.
- [ ] No Background/API/Admin/Woo/Shared runtime code or `_index.md` changes.

## Validation

- [ ] `npm run prisma:validate` in `moda-interact-database`.
- [ ] `npm run test:arch027-woocommerce-billing-schema`.
- [ ] `npm run test:arch027-woocommerce-billing-migration` (expanded effective-contract validation).
- [ ] `npm run test:arch027-woocommerce-billing:postgres` with fresh and accepted-baseline upgrade fixture evidence, using the repository's actual harness options.
- [ ] `git diff --check` and migration-file scope check.

If Docker/PostgreSQL cannot run in the agent environment, record the blocker and obtain developer-run evidence under the normal task validation policy; do not mark the task review-ready without required PostgreSQL proof.

## Stop Condition

After all scoped Work Items, Acceptance Criteria and required Validation are satisfied, set status `review`, finish the Completion Report and return control to `moda_architect`. Do not modify Background code or begin downstream tasks.

## Implementation Notes

The already-accepted DATABASE-001 check is the historical starting point. A forward-only migration should remove only the extra condition that forces both `providerAmount` and `providerCurrency` non-NULL for `COMPLETED`, while retaining the existing equality-of-nullness, nonnegative amount, three-letter currency, positive `finalCreditQuantity`, `providerReference`, `providerActionKind`, and `providerConfirmedAt` checks. Do not change Shopify's branch of the constraint.

Do not confuse "optional audit data" with "unverified provider refund". A verified, authenticated `refunded` webhook and exact local hold must still be established by Background; the database enforces durable row-level evidence invariants independently.

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

- Accepted DATABASE-001 migration is installed on the upgrade fixture and is immutable.

### Unresolved Issues

None beyond execution of the bounded migration and its tests.

### Architectural Concerns

None beyond this documented correction.

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
