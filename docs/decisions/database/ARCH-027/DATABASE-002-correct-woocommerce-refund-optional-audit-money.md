---
id: ARCH-027-DATABASE-002
architecture_id: ARCH-027
title: Correct Woo completed-refund monetary audit optionality
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: automatic
status: complete
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

- [x] Inspect the effective DATABASE-001 `RecoveryCreditRefund_woocommerce_settlement_check` and the accepted DATABASE-001 PostgreSQL fixtures.
- [x] Add one bounded forward-only migration preserving completed-refund identity/quantity and audit-pair rules while permitting both monetary fields NULL.
- [x] Update relevant static migration/contract validator(s) to enforce effective final DDL without invalidating legitimate historical migration checks.
- [x] Add PostgreSQL positive fixtures for Woo `COMPLETED` with both money fields NULL and with both populated, including provider-action/reference/confirmation evidence.
- [x] Add independent negative fixtures for only amount, only currency, negative amount, malformed currency, missing provider reference/action/confirmation or nonpositive final quantity.
- [x] Prove existing Shopify refund constraints and Woo purchase-Shop/provider ownership guards remain intact.
- [x] Run fresh and accepted-baseline upgrade rehearsals on disposable PostgreSQL; record SQLSTATE/errors and cleanup evidence.

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

- [x] Completed Woo refund with valid provider identity/action/confirmation and positive finalCreditQuantity succeeds with both monetary fields NULL.
- [x] Completed Woo refund with a valid populated audit pair succeeds.
- [x] Exactly one monetary field populated is rejected in both orientations, including non-COMPLETED Woo states.
- [x] Invalid amount/currency and missing required completed-refund identity/quantity evidence are rejected.
- [x] Shopify refund lifecycle constraints and all accepted purchase/shop/provider/operation guards remain enforced.
- [x] Historical DATABASE-001 migration is byte-identical; only the new forward migration and necessary test/validator files change.
- [x] Fresh and accepted-baseline upgrade PostgreSQL rehearsals pass, including the effective final constraint on both paths.
- [x] No Background/API/Admin/Woo/Shared runtime code or `_index.md` changes.

## Validation

- [x] `npm run prisma:validate` in `moda-interact-database`.
- [x] `npm run test:arch027-woocommerce-billing-schema`.
- [x] `npm run test:arch027-woocommerce-billing-migration` (expanded effective-contract validation).
- [x] `npm run test:arch027-woocommerce-billing:postgres` with fresh and accepted-baseline upgrade fixture evidence, using the repository's actual harness options.
- [x] `git diff --check` and migration-file scope check.

If Docker/PostgreSQL cannot run in the agent environment, record the blocker and obtain developer-run evidence under the normal task validation policy; do not mark the task review-ready without required PostgreSQL proof.

## Stop Condition

After all scoped Work Items, Acceptance Criteria and required Validation are satisfied, set status `review`, finish the Completion Report and return control to `moda_architect`. Do not modify Background code or begin downstream tasks.

## Implementation Notes

The already-accepted DATABASE-001 check is the historical starting point. A forward-only migration should remove only the extra condition that forces both `providerAmount` and `providerCurrency` non-NULL for `COMPLETED`, while retaining the existing equality-of-nullness, nonnegative amount, three-letter currency, positive `finalCreditQuantity`, `providerReference`, `providerActionKind`, and `providerConfirmedAt` checks. Do not change Shopify's branch of the constraint.

Do not confuse "optional audit data" with "unverified provider refund". A verified, authenticated `refunded` webhook and exact local hold must still be established by Background; the database enforces durable row-level evidence invariants independently.

## Completion Report

### Status

Developer implementation delivered and reviewed. No agent claim was made; `attempt: 0` remains historically accurate. Implementation and migration are committed directly on Database `main` at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

### Files Changed

- `prisma/migrations/20261011110000_arch027_woocommerce_refund_optional_audit_money/migration.sql` (new forward-only migration).
- `scripts/test-arch027-woocommerce-billing-postgres.mjs` (self-provisioning disposable PostgreSQL 17 fresh/upgrade fixtures and settlement regressions).
- `scripts/validate-arch027-woocommerce-billing-migration.mjs` (effective final constraint checks).

### Work Completed

- Replaced only `RecoveryCreditRefund_woocommerce_settlement_check`; provider monetary fields remain a matched optional pair.
- Preserved the completed Woo refund's non-NULL positive `finalCreditQuantity`, nonblank provider reference, `REFUND` action and provider confirmation, plus the existing one-completed-refund-per-purchase rule.
- Kept historical DATABASE-001 migrations and Prisma models unchanged.
- Reused the existing Docker-based PostgreSQL 17 test approach, with invocation-owned container/database setup and cleanup.
- Corrected the rehearsal fixtures to avoid duplicate completed refunds and added explicit NULL-safety checks for required settlement fields.

### Validation Results

- Developer-reported PASS: both PostgreSQL 17 migration rehearsals (fresh and accepted-baseline upgrade), after incremental fixture/NULL-guard corrections.
- Previously checked: `prisma:validate`, ARCH-027 schema/migration static validators, JavaScript syntax, `git apply --check --whitespace=error-all`, actual patch application, and `git diff --check` against exact baselines. No repeat of these commands by the reviewing architect is claimed.
- GitHub independently verified the final pushed commit `b9cb77a74c5fffa250dc65ed34de23113738d8e8`, based on `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`, changes only the three intended files.
- Deployment of the migration to any persistent database is **not** evidenced by the Git push or disposable test results; it must be verified separately with `prisma migrate deploy/status` in the intended environment.

### Deviations

- The developer applied this bounded correction directly to `moda-interact-database/main` by explicit request rather than creating launcher-prepared mirrored `task/ARCH-027-DATABASE-002` implementation and report branches. This is a documented workflow exception; no dedicated implementation worktree, launcher claim, or task-branch push is fabricated.

### Assumptions

- The accepted DATABASE-001 migration remains immutable; the upgrade fixture starts with its effective contract.
- The user/developer's fresh and upgrade PostgreSQL test results refer to the final submitted migration.

### Unresolved Issues

- Parent-workspace Database gitlink must be advanced to the final Database-main commit, and Background's nested database gitlink must be updated before retrying B005's blocked PostgreSQL settlement case.
- Persistent-environment migration deployment must be verified before using the updated contract against persistent Woo refund data.

### Architectural Concerns

- The direct-main execution path bypassed the ordinary mirrored task worktree protocol; this historical deviation is explicitly recorded rather than misrepresented as an agent execution.

## Architect Review

### Review Status

Accepted — direct developer implementation (2026-10-11); `status: complete` following the developer's supplied validation and commit evidence. Historical `attempt: 0` is preserved because there was no task launcher claim.

### Review Notes

- The scoped forward migration is committed and pushed to Database `main` at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. The developer explicitly chose a direct patch and reported both PostgreSQL 17 fresh and upgrade rehearsals passing.
- The migration relaxes only the completed Woo refund requirement for non-NULL `providerAmount`/`providerCurrency`; matched-nullness, monetary validity, positive credit quantity, provider reference/action/confirmation and other purchase/provider ownership constraints remain enforced.
- The existing historical DATABASE-001 migration, Prisma schema, Shopify contract and Background application source remain unchanged.
- This manual execution was outside the normal mirrored-agent implementation protocol. The architect records the deviation transparently; no task worktree, agent claim or additional Git commit is invented.

### Reviewed Files

- `prisma/migrations/20261011110000_arch027_woocommerce_refund_optional_audit_money/migration.sql`.
- `scripts/test-arch027-woocommerce-billing-postgres.mjs` and `scripts/validate-arch027-woocommerce-billing-migration.mjs`.
- Database `b9cb77a` Git commit scope and parent canonical task definition.

### Validation Reviewed

- Developer-reported PostgreSQL 17 fresh/upgrade success; earlier ARCH-027 static and syntax checks reported passed. These were not rerun by the architect in this environment.
- GitHub commit diff independently confirms only the three expected files changed. Migration deployment to persistent databases has not been verified.

### Architecture Conformance

- Accepted bounded correction of the Woo refund monetary-audit contract. No fabricated provider money or change to monetary settlement authority, idempotency or tenant/provider isolation.

### Follow-up

- Developer integrates Database `b9cb77a` into the parent workspace gitlink and Background's nested Database gitlink, using clean Git worktrees; do not merge an unreviewed Background implementation into main simply to move the pointer.
- Reconcile and re-gate `ARCH-027-BACKGROUND-005` only after its runtime uses the new Database revision. Rerun its malformed-money PostgreSQL settlement scenario and then submit for final architect review.
- Continue to withhold dependent API-006 and ADMIN-001 until BACKGROUND-005 is architect-accepted Complete. Defer every `docs/decisions/**/_index.md` edit.
