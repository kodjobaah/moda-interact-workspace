---
id: ARCH-036-DATABASE-002
architecture_id: ARCH-036
title: Store bounded merchant and override discount selections on existing rows
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-001"]
enables: ["ARCH-036-SHOPIFY-001", "ARCH-036-API-002", "ARCH-036-BACKGROUND-002", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-DATABASE-002 — Bounded discount selections without new tables

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_database` / `moda-interact-database`.
- **Defined but not materialised.** This task cannot start until `ARCH-036-DATABASE-001` is architect-accepted **Complete**. It has no developer task worktree or claimed attempt yet.

## Objective

Represent a merchant's **set of alternative WooCommerce coupon IDs** (and a distinct Admin override selection) on the **existing recovery-policy records**, retaining Shopify's working single-discount FK and immutable per-attempt offer evidence. No selection/join/staging/proof table may be created.

## Context

Inspected models and migration:

| Existing record | Current relevant fields | Actual ARCH-016 SQL invariant |
|---|---|---|
| `shopify.ShopSettings` | `recoveryOfferMode`, `fixedShopifyDiscountId` FK, `updatedAt` | `ck_arch016_shop_settings_fixed_offer`: `FIXED` requires non-null FK; every other mode requires null FK |
| `shopify.ShopRecoveryPolicyOverride` | Same mode/FK; `reason`, `expiresAt`, `updatedByPlatformAdminId`, `updatedAt` | `ck_arch016_policy_override_fixed_offer`: same requirement |
| `commerce.RecoveryOutreachAttempt` | `configuredOfferMode`, `fixedShopifyDiscountId` FK, `offerSnapshot`, sequence/status | `ck_arch016_outreach_fixed_offer`: `FIXED` attempt currently requires a **single** chosen FK |
| `shopify.ShopRecoveryPolicyOverrideAuditEvent` | Before/after policy JSON, actor, reason/time | Existing audit history must remain intact |

Woo `FIXED` means **the merchant checks several permitted coupon alternatives**, from which a later recovery selects **at most one** eligible coupon. It does not mean stack every checked coupon. Shopify `FIXED` retains the existing singular FK until a separate Shopify UI/consumer migration. `NONE` always offers no coupon; `AI_BEST_APPLICABLE` evaluates supported current catalogue candidates without using a manually curated selection.

**Critical migration gap:** merely adding a JSON array does not work. Both existing ARCH-016 policy `FIXED` check constraints would reject Woo's `FIXED` policy with `fixedShopifyDiscountId=NULL`. This task must replace them in a **new forward migration**, while maintaining every valid Shopify legacy row.

## Scope

Within `moda-interact-database/` only:

1. Add exactly one `selectedDiscountIds` field to each of the **existing** `ShopSettings` and `ShopRecoveryPolicyOverride` Prisma models: `Json @default("[]")` stored as `JSONB NOT NULL DEFAULT '[]'::jsonb`.
2. Create a **new additive migration** under `prisma/migrations/<new-timestamp>_arch036_selected_discount_ids/migration.sql`, after DATABASE-001. Do not edit ARCH-016 or any historical migration.
3. Replace the two legacy **policy** fixed-offer checks with mode-aware XOR constraints accepting either legacy Shopify single FK **or** a nonempty Woo selection array, never both.
4. Add a tightly scoped database JSON validation helper/check for array type, bounded count, element type/length and duplicates. SQL helper functions/constraints are permitted; **new tables are not**.
5. Add schema, fresh/upgrade/re-run and disposable PostgreSQL negative/concurrency regression tests. Do not implement the actual API selected-ID write or merchant UI here.

### Explicit non-changes

- `ShopSettings.fixedShopifyDiscountId`, `ShopRecoveryPolicyOverride.fixedShopifyDiscountId`, all old relations, `ShopRecoveryPolicyOverrideAuditEvent` and `RecoveryOutreachAttempt.offerSnapshot` stay physically present.
- Preserve the existing `RecoveryOfferMode` enum (`NONE`, `FIXED`, `AI_BEST_APPLICABLE`); do not add `WOO_FIXED`.
- **Do not alter** `ck_arch016_outreach_fixed_offer` within this database task: an outreach attempt still stores **one resolved discount FK** when configured as `FIXED`, not a list. Background must resolve a single eligible discount (or fail closed) before attempting that insert. Any desired no-coupon fallback representation inconsistent with that check is a **separate Architect decision**, not permission to loosen it silently.

## Out of Scope

- No new selection, coupon, snapshot, join, provider-proof or audit tables.
- No new provider API, outgoing message format, background candidate ranking, Shopify merchant settings change or admin UI implementation.
- No creation of an immutable evidence/proof ledger; existing outreach `offerSnapshot` remains authoritative for a particular attempt.
- No history rewrite, data reset, deletion of missing/expired selected discount IDs, or `_index.md` update.
- No work on tasks listed under Enables.

## Requirements

### A. Exact storage contract

| Column on each existing policy model | Storage | Rule |
|---|---|---|
| `selectedDiscountIds` | `JSONB NOT NULL DEFAULT '[]'::jsonb` | Canonical **set** of discount row `id` strings; 0–**50** IDs; unique; each nonempty, max **128** characters. No objects, numbers, booleans or null elements |
| `recoveryOfferMode` | Existing enum | Remains unchanged; mutually exclusive `NONE`, `FIXED`, `AI_BEST_APPLICABLE` |
| `fixedShopifyDiscountId` | Existing nullable FK | Retained for Shopify `FIXED` and existing row relations. Must be null for Woo multi-selection configuration |
| `updatedAt` | Existing `@updatedAt` | Retain as the revision/CAS source; don't add a competing revision counter |

Use a single narrowly scoped immutable PostgreSQL validation function (e.g. `shopify.arch036_valid_selected_discount_ids(jsonb)`) or an equally verifiable constraint that rejects malformed arrays, more than 50 entries, duplicate IDs, wrong JSON element types and overlong/empty IDs. A simple `jsonb_typeof(...)='array'` check alone is insufficient; avoid using `jsonb_array_length` unsafely on non-arrays. Validate identical semantics in Prisma-facing fixtures.

**Canonical ordering:** the API will sort/deduplicate only when constructing an explicitly validated *set*; it must **reject** duplicate IDs sent by the merchant rather than silently discard them. Database storage need not enforce input ordering, but identical permutations are semantically the same set. Do not use JSON array order to determine which coupon a recovery promises.

### B. Replace exactly the two policy checks

Implement the following truth table for **both** `ShopSettings` and `ShopRecoveryPolicyOverride`. This is the required behaviour of the new constraints, not an instruction to paste unchecked SQL verbatim:

| Mode | Existing `fixedShopifyDiscountId` | New `selectedDiscountIds` | Result |
|---|---|---|---|
| `NONE` | NULL | `[]` | **Allowed** |
| `AI_BEST_APPLICABLE` | NULL | `[]` | **Allowed** |
| `FIXED` on Shopify | Non-null | `[]` | **Allowed** (legacy path) |
| `FIXED` on Woo | NULL | 1–50 distinct valid IDs | **Allowed** (Woo path) |
| `FIXED` | NULL | `[]` | **Rejected** |
| `FIXED` | Non-null | Nonempty array | **Rejected** (ambiguous double selection) |
| `NONE` or `AI_BEST_APPLICABLE` | Any ID or nonempty array | Any conflicting value | **Rejected** |

Replace `ck_arch016_shop_settings_fixed_offer` and `ck_arch016_policy_override_fixed_offer` using a new migration, with deterministic new constraint names such as `ck_arch036_shop_settings_offer_selection` / `ck_arch036_override_offer_selection`. Keep the original recovery-delay and follow-up checks untouched. The check's `FIXED` branches can validate **shape/XOR** without inspecting `Shop.platform`; **API-002** enforces that Shopify uses the legacy FK and Woo uses the selected set. Do not pretend a row-only `CHECK` can inspect a different table's provider.

### C. Same-shop and provider validation — explicit ownership boundary

Individual JSON elements cannot have PostgreSQL FKs. This is a deliberate consequence of the **no-new-table** requirement, not a reason to omit tenant checks. Define the complete write contract required of `ARCH-036-API-002`:

1. Authenticate the Woo installation and resolve the Shop from its server-side principal, not a caller-supplied `shopId`.
2. Lock that Shop (matching existing `ARCH-035-API-002` policy-write ordering), re-read the current settings/override and require the current `updatedAt`/expected revision before mutation.
3. Require `Shop.platform = WOOCOMMERCE`; when mode is `FIXED`, resolve **every distinct selected ID** against `ShopifyDiscount` from DATABASE-001 with `discount.shopId=principal.shopId` and `discount.provider=WOOCOMMERCE`. Invalid/foreign/deleted IDs cause the **entire** save to fail atomically.
4. On a *new* fixed-selection save, require that every chosen discount exists in a successfully completed current same-Shop catalogue and passes the explicitly supported merchant-selectability checks. This does **not** constitute send-time checkout eligibility.
5. Persist the new set and `recoveryOfferMode` together with the same Shop lock/revision check; update only the merchant policy row, never silently overwrite `ShopRecoveryPolicyOverride` or its audit trail.
6. An already saved selected coupon may later be expired, revoked, removed from the catalogue or unavailable. **Retain its ID for truthful merchant editing/audit** until an explicit merchant/admin change; do not send it. Read/display can classify it as unavailable. A new attempt to select it must be rejected.
7. Same-shop checks must be repeated for Admin override writes by `moda_admin`; the API producer must not assume JSON membership is enforced by a relational FK.

The database task provides the schema and negative SQL/transaction fixtures; it does not implement these API/Admin procedures. Document the unavoidable lack of JSON-element referential integrity prominently in handoff notes to API-002 and ADMIN-001.

### D. Active overrides, concurrency and outbound history

- The merchant's `selectedDiscountIds` and the admin override's `selectedDiscountIds` are **separate** fields. An active override takes precedence at read/processing time but does not replace merchant preference. Expiring/clearing the override reveals the merchant's unchanged set.
- Existing `ShopSettings.updatedAt` and `ShopRecoveryPolicyOverride.updatedAt` are the respective optimistic-concurrency revisions. No new revision column. `ARCH-035-API-002` already uses `ShopSettings.updatedAt` and Shop-row locking, so `ARCH-036-API-002` must coordinate with those same writes, not introduce a second unsynchronised policy store.
- No snapshot of a previously committed `RecoveryOutreachAttempt` can be rewritten because a coupon expires, is removed from a selected set, or changes in Woo. Existing `offerSnapshot` remains the per-attempt evidence; a Woo `FIXED` attempt must resolve **one** discount (the legacy single FK points into the now-shared table) before insertion under the existing check.
- Do not broaden `fixedShopifyDiscountId` to represent **the selected array** or allow multiple coupon IDs per attempt. Multiple checkboxes are alternative **configuration** candidates; the attempt is one outcome.
- Foreign-shop identity, incomplete/failed catalogue generations, unsupported restrictions, revoked read grant and unknown send-time proof must never be interpreted as an eligible coupon simply because an ID is persisted in JSON. Background and Commerce owners apply those runtime gates later.

### E. Migration and deployment

- Run preflight checks of existing `FIXED` policy rows and related discount FKs. Existing valid Shopify singular selections remain byte-for-byte unchanged; migration must not convert them into JSON or reset their offer mode.
- Add `selectedDiscountIds NOT NULL DEFAULT []` on both existing tables; all old rows become `[]`. Add JSON shape validation; replace only the two named policy checks. Preserve the old `RecoveryOutreachAttempt` check and its `fixedShopifyDiscountId` foreign key.
- Application consumers must be deployed in a safe order after DATABASE-001; until API/Shopify/Background consumers recognise JSON sets, Woo's UI still must not activate provider coupon promises.
- Document rollback as disabling the new multi-selection save/send paths while leaving additional JSON columns in place. No physical down-migration that drops existing selections or changes past outreach evidence.

## Work Items

- [ ] Inventory `ShopSettings`, `ShopRecoveryPolicyOverride`, their audit model and `RecoveryOutreachAttempt` fields/constraints in the real schema and ARCH-016 migration.
- [ ] Add `selectedDiscountIds` to exactly the two policy models and create **one new** forward migration with `JSONB NOT NULL DEFAULT []` and validation function/check.
- [ ] Replace **both** existing policy fixed-offer constraints with the XOR truth table above; retain every other recovery, outreach and FK constraint.
- [ ] Verify legacy Shopify single-FK rows migrate unchanged; independently create Woo multi-selection fixtures and override fixtures.
- [ ] Write and execute fresh/upgrade/re-run PostgreSQL tests for JSON shape, SQL modes, separate override state and update conflict simulation.
- [ ] Record transaction-level tenant membership limitation and handoff to API-002/Admin, with references to the existing `updatedAt` CAS path.
- [ ] Complete the task report with changed files, commands, results, worktrees/branches and unresolved architecture concerns.

## Interfaces / Contracts

- **Schema produced:** `ShopSettings.selectedDiscountIds`, `ShopRecoveryPolicyOverride.selectedDiscountIds` (`Json` in Prisma, `JSONB` in PostgreSQL); original `fixedShopifyDiscountId` fields and FK targets remain.
- **DB contract consumer:** `ARCH-036-API-002` handles revision-safe merchant writes and same-shop/provider membership checks. `ARCH-036-SHOPIFY-001` preserves singular Shopify reads/writes. `ARCH-036-BACKGROUND-002` evaluates the effective candidate set. `ARCH-036-ADMIN-001` must preserve admin override precedence and validate tenant membership on any new selection writes.
- **Shared contract owner:** `ARCH-036-SHARED-002`; this task stores **discount row IDs**, not coupon codes or arbitrary provider URLs, and does not redefine the wire schema.
- **Existing attempt:** `RecoveryOutreachAttempt.fixedShopifyDiscountId` remains one chosen discount FK; `offerSnapshot` remains the evidence JSON. No new attempt columns or tables in this task.

## Dependencies

- `ARCH-036-DATABASE-001` must be architect-accepted `Complete` (not merely implemented/pushed). The existing discount IDs, providers and per-shop catalogue are then authoritative for set membership.

## Enables

- `ARCH-036-SHOPIFY-001`
- `ARCH-036-API-002`
- `ARCH-036-BACKGROUND-002`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Zero new physical tables; only the two existing policy rows receive new selected-ID JSON columns, with `[]` defaults.
- [ ] All 3 legacy values `NONE`/`FIXED`/`AI_BEST_APPLICABLE` and existing Shopify fixed FK data survive migration; both original policy checks are deliberately replaced in **new** migration SQL.
- [ ] Valid Woo `FIXED` set of 1–50 distinct same-shop Woo discount IDs is representable with `fixedShopifyDiscountId=NULL`; `NONE`/`AI_BEST_APPLICABLE` require `[]` and null legacy FK.
- [ ] Malformed object, scalar, null, non-string, empty ID, >128-character ID, duplicate ID, 51-element set, invalid mode and both-single-plus-array examples fail at the proper DB validation boundary.
- [ ] JSON membership cannot be described as an FK; the test report explicitly demonstrates/records transaction-level same-Shop/provider validation needed by API-002 and Admin. A foreign-Shop ID is **rejected by the application write contract**, not falsely claimed to be excluded by a row-only SQL check.
- [ ] Active override retains its own set/expiry/audit data; clearing it does not overwrite merchant settings.
- [ ] A previously selected coupon becoming unavailable does not cause silent removal from persisted settings; no stale/foreign ID becomes an eligible offer by virtue of storage alone.
- [ ] Existing `ck_arch016_outreach_fixed_offer`, attempt FKs and immutable `offerSnapshot` persisted history remain intact.
- [ ] Disposable PostgreSQL fresh/upgrade/re-run proof, Prisma validation and current Shopify recovery-policy schema regressions pass.

## Validation

- [ ] `npm run validate`, `npm run prisma:generate` and `npm run test:arch016-recovery-schema` in `moda-interact-database`.
- [ ] New ARCH-036 schema/migration fixture validation; inspect resulting `pg_constraint` and `information_schema` output to prove old constraint replacements/new checks.
- [ ] Disposable PostgreSQL **fresh, existing-data upgrade and repeat deploy**, with seeded Shopify `FIXED` rows, Woo `FIXED` multi-ID policy, separate admin override and previously committed outreach attempt.
- [ ] Negative SQL inputs: object/scalar/null JSON, duplicate/oversized array, wrong mode, both branches set, malformed IDs, 51 items; transaction fixture demonstrates foreign-shop ID selection must fail under the API-required membership query.
- [ ] Two concurrent Shop-locked writer transactions with stale expected revisions; show winner/loser semantics without inventing new schema CAS fields. Audit/outreach rows are unchanged.
- [ ] Existing Shopify policy/override FK tests plus `git diff --check`. Use only scripts that actually exist in the repo or are created explicitly by this task; do not assume a repository-wide `npm test` target.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are complete, submit the Completion Report for Architect review and **STOP**. Do not implement API-002 or change any non-database repository in the same task.

## Implementation Notes

- The XOR policy CHECK protects **shape and exclusive storage mode**; tenant/provider membership of JSON IDs is a transactional **application** responsibility. Do not create a join table or pretend JSON has native element foreign keys to solve it.
- Offer mode `FIXED` with several checked coupons is **not** a new enum. One eligible coupon per recovery remains the agreed selection semantics.
- Preserve historical migrations and discount/outreach PK/FK identities. Additive PostgreSQL helper functions/check constraints are in scope; new tables are not.
- If enforcing the chosen semantics uncovers an unhandled `FIXED` no-offer background attempt path, record the conflict and return to `moda_architect`; do not silently weaken the historical attempt check or substitute an invented offer claim.
- This is a **developer-executed** task with `completion_mode: developer`; materialise/start only via `/moda_developer_create ARCH-036-DATABASE-002` when eligible. Use the launcher-resolved independent parent/implementation worktrees and record mirrored task branch, start-of-attempt synchronisation, recursive submodule evidence, tests and completion handoff. This task definition itself created no branch, worktree, commit or push.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

No unreviewed assumption may relax the array bound, legacy Shopify FK path or app-owned tenant membership validation.

### Unresolved Issues

None recorded; return any migration/Prisma incompatibility or missing same-shop enforcement contract to the architect.

### Architectural Concerns

Any proposed new table, changed outreach semantics, shared contract adjustment or consumer-breaking schema rename requires a separate Architect decision.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable task definition only; no implementation review performed.

### Reviewed Files

Existing schema, ARCH-016 migration and current ShopSettings / RecoveryOutreachAttempt consumer shapes reviewed in task design.

### Validation Reviewed

None from this task.

### Architecture Conformance

Pending code/migration and disposable PostgreSQL evidence.

### Follow-up

After DATABASE-001 is accepted, materialise via the canonical task workflow, complete independently and return for review.
