---
id: ARCH-035-DATABASE-002
architecture_id: ARCH-035
title: Store Woo recovery-offer selection and immutable evidence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 39
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-011
enables:
  - ARCH-035-API-012
  - ARCH-035-BACKGROUND-003
  - ARCH-035-WOOCOMMERCE-011
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-DATABASE-002: Store Woo recovery-offer selection and immutable evidence

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Add only required provider-scoped fields/relations for Woo fixed coupon selection and immutable recovery offer provenance without reusing ShopifyDiscount IDs.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Design is fixed; do not leave a “possibly no migration” choice to the implementing agent.** Reuse
`commerce.RecoveryOutreachAttempt.offerSnapshot` as the already-existing immutable-by-business-rule outbound offer
snapshot. It is not a new JSON column and must never contain a ShopifyDiscount ID for a Woo Shop. Add only the Woo
coupon **merchant selection identity** missing from the baseline.

**Exact files:** `moda-interact-database/prisma/schema.prisma`, new
`prisma/migrations/20261011200000_arch035_woo_recovery_coupon_selection/migration.sql`, new
`scripts/validate-arch035-woo-coupon-selection.mjs`/Postgres regression fixture. No changes to prior migrations or
the existing `ShopSettings.fixedShopifyDiscountId`, `ShopRecoveryPolicyOverride.fixedShopifyDiscountId`,
`RecoveryOutreachAttempt.fixedShopifyDiscountId` columns.

**Create one model `WooCommerceRecoveryCouponSelection`, in `@@schema("woocommerce")`:**

```prisma
model WooCommerceRecoveryCouponSelection {
  shopId            String   @id @db.Text
  providerCouponId  String?  @db.VarChar(64)
  couponCode        String?  @db.VarChar(191)
  evidenceSha256    String?  @db.Char(64)
  verifiedAt        DateTime? @db.Timestamptz(3)
  evidenceExpiresAt DateTime? @db.Timestamptz(3)
  revision          Int      @default(0)
  lastActionId      String?  @db.Uuid
  lastActionSha256  String?  @db.Char(64)
  createdAt         DateTime @default(now()) @db.Timestamptz(3)
  updatedAt         DateTime @default(now()) @updatedAt @db.Timestamptz(3)
  shop              Shop     @relation(fields:[shopId],references:[id],onDelete:Cascade,onUpdate:Restrict)
  @@index([shopId, verifiedAt])
  @@schema("woocommerce")
}
```

Add exactly one inverse optional relation on `Shop`. `ShopSettings.recoveryOfferMode` remains the single desired
policy mode; this new row stores **only** the Woo provider coupon identity, last verified decision hash and CAS
revision. The row persists with coupon fields all null when a merchant chooses NONE/AI mode (no delete/recreate
revision reset). SQL checks: revision nonnegative; coupon identity/code/hash/verification timestamps all-null or
all-present; `lastActionId`/`lastActionSha256` both null or both non-null; SHA-256 lowercase hex; bounded positive
provider ID; evidence expiry strictly after verification. `lastActionId` and `lastActionSha256` persist the last
successful mutation replay proof required by API-012, not an additional ledger. No raw full provider coupon
object/PII/secret; coupon code is not a Shopify node identifier.

**Schema checklist:** exactly **one** new `WooCommerceRecoveryCouponSelection` model, **one** optional inverse field
`Shop.wooRecoveryCouponSelection`, **no** additional `ShopSettings` or `RecoveryOutreachAttempt` columns. Primary key
is Shop ID (one row per Woo Shop). `providerCouponId`, `couponCode`, `evidenceSha256`, `verifiedAt` and
`evidenceExpiresAt` become null together on NONE; `revision` increments on every distinct accepted selection
mutation; `lastActionId` and `lastActionSha256` allow a same-actionId replay without issuing a second revision. A
CHECK forbids a partial coupon identity. The foreign key is required `(shopId)->commerce.Shop(id)` with CASCADE
delete/RESTRICT update. Keep existing ShopifyDiscount references untouched even if their historical schema name is
`shopify`.

**Freeze outbound provenance using existing field:** BACKGROUND-003 writes an exact `offerSnapshot` shape, for Woo
only,
`{"contractVersion":"woo.offer.v1","provider":"WOOCOMMERCE","decision":"NONE"|"FIXED","providerCouponId":string|null,"couponCode":string|null,"selectionRevision":integer|null,"evidenceSha256":string|null,"verifiedAt":ISO|null}`.
NULL fields for NONE. Persist with compare-and-swap `UPDATE ... WHERE "offerSnapshot" IS NULL`; when already set,
replay must return the same snapshot, never overwrite it. Add a **Woo-only database trigger** preventing change of a
non-null `offerSnapshot` on existing `RecoveryOutreachAttempt` rows (derive platform through
`CheckoutRecovery`→`Shop`), while leaving Shopify attempt behaviour intact. This trigger does **not** need a new FK
on `RecoveryOutreachAttempt` or a duplicated `shopId` column.

**Producer/consumer boundaries:** API-011 verifies coupon/provider/read-grant evidence; WOOCOMMERCE-011 persists
selection and `ShopSettings.recoveryOfferMode` in one Shop-locked transaction with `revision` CAS. BACKGROUND-003
revalidates the same coupon for the exact recovery/cart before dispatch; an expired/stale/revoked/unsupported proof
forces `decision=NONE`. `ShopRecoveryPolicyOverride` remains admin-only; a Shopify-fixed override for a Woo shop may
never be treated as a Woo coupon. No new free-form policy status enums.

**Mandatory proofs:** same `lastActionId`/SHA replay versus same ID with different SHA, fresh/upgrade/no-op second
migration, schema/Prisma generation, two shops selecting the same providerCouponId without cross-shop relation,
wrong-Shop coupons denied by caller, all-null-vs-all-present CHECK, revision replay/race, immutable Woo snapshot
trigger, existing Shopify attempt updating unaffected, zero migration of Shopify discount evidence, mocked revoked
read-grant with no coupon snapshot, and `git diff --check`. If `API-011`'s accepted evidence schema disagrees with
these frozen fields, STOP and request an architect correction rather than silently changing the table.

## High-level scope (non-authoritative summary)

- Preserve existing ShopSettings, ShopRecoveryPolicyOverride, RecoveryOutreachAttempt and ShopifyDiscount semantics and Shopify migration history.
- Bind Woo coupon identity and selection to one Shop/platform with required provenance and unique constraints; no cross-Shop discount FK/ID interpretation.
- Freeze approved offer evidence for a recovery attempt so later provider catalogue changes cannot retroactively authorize another coupon.
- If safe existing data shape suffices, document that result and avoid unnecessary schema churn.

## Out of Scope

- Unrelated Shopify or Woo Billing feature changes; changing another repository in this task.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-database`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-API-011` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-API-012`
- `ARCH-035-BACKGROUND-003`
- `ARCH-035-WOOCOMMERCE-011`

## Acceptance Criteria

- [ ] Fresh/upgrade/replay migration and ownership constraint tests.
- [ ] Shopify fixed discount regression and Woo shop mismatch rejection.
- [ ] Disposable Postgres verification including no SQL drift.
- [ ] Scope stays within `moda-interact-database` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

**Superseded by ARCH-035 UI-only scope revision (11 October 2026).** This definition is historical and MUST NOT be claimed or executed under ARCH-035. Backend/data/event/coupon capabilities require a separately agreed architecture if ever authorised. No implementation was reviewed or accepted.

Return to architect on implementation submission.
