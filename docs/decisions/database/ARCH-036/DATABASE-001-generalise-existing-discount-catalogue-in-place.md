---
id: ARCH-036-DATABASE-001
architecture_id: ARCH-036
title: Generalise existing discount catalogue in place without breaking Shopify
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-036-DATABASE-002", "ARCH-036-BACKGROUND-001", "ARCH-036-API-001", "ARCH-036-API-003", "ARCH-036-COMMERCE-001", "ARCH-036-ADMIN-001", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-DATABASE-001 — Generalise existing discount catalogue in place

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_database` / `moda-interact-database`.
- **Defined but not materialised.** This is an implementation specification, not authorisation to alter the developer's primary checkout; no branches, worktrees, commits or pushes were created during task authorship.

## Objective

Add **provider-aware identity and bounded WooCommerce full-snapshot progress** to the two **existing** physical discount tables, while keeping every Shopify row ID, foreign key, existing Prisma client delegate and historical migration usable.

## Context

The inspected source of truth is `moda-interact-database/prisma/schema.prisma` from `moda-interact-workspace(20261012-161540).zip` and migration `20260916150000_arch016_recovery_policy_discounts_outreach_generations/migration.sql`.

The actual present schema is:

| Physical location | Present keys / behaviour | Compatibility requirement |
|---|---|---|
| `shopify.ShopifyDiscountCatalogue` | `id` PK; `shopId` unique; `status`, `syncGeneration`, `activeSyncToken`, timing/error fields | Still **one catalogue per Shop**; Shopify's worker uses those columns today |
| `shopify.ShopifyDiscount` | `id` PK; required `shopifyDiscountNodeId`; `UNIQUE(shopId, shopifyDiscountNodeId)`; `providerType` is **discount subtype**, not commerce provider; `method`, `providerSnapshot`, availability and generation fields | Preserve every existing ID, reference, catalogue link, `providerType` meaning and old unique key |
| `commerce.Shop` | `platform` is existing `commerce.ShopPlatform` (`SHOPIFY`, `WOOCOMMERCE`) | Platform is authoritative for tenant/provider identity; no impersonation |
| Existing referencing rows | `ShopSettings.fixedShopifyDiscountId`, `ShopRecoveryPolicyOverride.fixedShopifyDiscountId`, `RecoveryOutreachAttempt.fixedShopifyDiscountId` reference discount `id` | Preserve the physical target table and existing values/FKs |

The live Shopify writer in `moda-interact-background/src/services/shopify-discount-catalogue.service.ts` still upserts by `(shopId, shopifyDiscountNodeId)` **without supplying a generic provider ID**. Changing the nullability of that field, making a generic provider ID mandatory for Shopify, or renaming its Prisma delegate risks breaking the existing compound-unique selector and its typed callers. Provider-neutral **semantics** are required now, not a breaking logical rename.

## Scope

Changes are limited to `moda-interact-database/`:

1. `prisma/schema.prisma`, modifying the existing models/relations and indexes only.
2. **One new additive migration** under `prisma/migrations/<new-timestamp>_arch036_shared_discount_catalogue_in_place/migration.sql` (actual timestamp chosen at implementation; do not edit any historical migration).
3. Focused schema/migration validators and disposable PostgreSQL fresh/upgrade/repeat/negative-case scripts under `scripts/`, with an optional corresponding `package.json` script.
4. Short repository-local fixture/test usage instructions when required to run those checks.

**Do not** rename/move the physical tables, re-key discounts, create a separate Woo catalogue, or add a staging/page-receipt table. Do not rename the Prisma `ShopifyDiscountCatalogue` and `ShopifyDiscount` models or existing field names **in this task**. Those delegates are still consumed by Shopify, Background, Admin and Commerce; coordinated logical renaming can be considered after consumer migration.

## Out of Scope

- No new PostgreSQL discount/coupon/selection/sync/proof tables or a new Redis correctness store.
- No producer/API implementation, Shared package modification, Shopify query change, coupon eligibility evaluator or outbound messaging change.
- No additions to merchant-selected discount sets; that is `ARCH-036-DATABASE-002`.
- No historical migration edits, destructive drops, discount ID regeneration, cross-repository source edits or `_index.md` updates.
- No execution of tasks listed under Enables.

## Requirements

### A. Exact additive persistence contract

These are the required **logical Prisma fields** and physical column semantics; keep pre-existing names and relations. Database agent must verify SQL type/default compatibility with the existing migration history.

| Existing model | Add/change | Type and required semantics |
|---|---|---|
| `ShopifyDiscountCatalogue` | `provider` | `ShopPlatform`, `NOT NULL DEFAULT SHOPIFY`, using the existing `commerce.ShopPlatform` enum; Woo catalogue creation must explicitly set `WOOCOMMERCE` |
| `ShopifyDiscountCatalogue` | `syncExpectedPages` | Nullable integer, only for Woo uploads; 0 represents a legitimately empty catalogue; when set, between 0 and **500** |
| `ShopifyDiscountCatalogue` | `syncExpectedItems` | Nullable integer, only for Woo uploads; when set, between 0 and **50,000** |
| `ShopifyDiscountCatalogue` | `syncNextPageIndex` | Nonnegative integer, default 0; zero-based next expected upload page |
| `ShopifyDiscountCatalogue` | `syncPageDigests` | `JSONB NOT NULL DEFAULT '{}'::jsonb`; bounded map from zero-based page index string to lowercase SHA-256 hex digest; max **500 entries / 64 KiB** |
| `ShopifyDiscount` | `provider` | `ShopPlatform`, `NOT NULL DEFAULT SHOPIFY`; do not repurpose existing `providerType` |
| `ShopifyDiscount` | `externalDiscountId` | Nullable text: Shopify external GID when supplied; Woo stable positive decimal `WC_Coupon::get_id()` (1–20 digits). Nullable temporarily for **legacy Shopify writer compatibility** |
| `ShopifyDiscount` | `shopifyDiscountNodeId` | **Keep required and unchanged**. For Woo, store the deterministic compatibility key `woo:coupon:<externalDiscountId>`; this is **never** a real Shopify GID and must not be exposed as one |

`shopId`, row `id`, `method`, `providerStatus`, `providerType`, `singleRedeemCode`, `providerSnapshot`, `lastSeenSyncGeneration`, `isAvailable`, `fixedSelectable`, time fields and all existing FKs remain available. `ShopifyDiscountMethod.CODE` represents Woo coupon codes; do not introduce a new enum merely to store `percent`/`fixed_cart`/`fixed_product` — those provider types belong in `providerType` and the bounded provider snapshot.

### B. Identity, uniqueness and same-shop/provider rules

1. Retain the required `shopifyDiscountNodeId` and `UNIQUE(shopId, shopifyDiscountNodeId)` **exactly**, including Shopify's current `upsert` selector and generated Prisma client type. Woo rows use the reserved deterministic `woo:coupon:<externalDiscountId>` compatibility key, so no nullable compound-key migration is necessary. This is an internal compatibility key, **not** a Shopify API node ID.
2. Add unique `(shopId, provider, externalDiscountId)` for non-null external IDs. Identical Woo coupon IDs in **different shops** are legal; identical Woo coupon IDs within the **same shop** are not. Old Shopify inserts with `externalDiscountId=NULL` must still be uniquely protected by the retained non-null legacy key. Never synthesize a Woo key from a merchant-editable coupon code (which can change); use its immutable numeric Woo ID.
3. Backfill all existing Shopify discount rows with `provider=SHOPIFY` and `externalDiscountId=shopifyDiscountNodeId`; preserve `id`, payloads, generations and timestamp evidence unchanged. Existing catalogue rows are Shopify; if preflight finds a catalogue belonging to a non-Shopify Shop, **stop and report** rather than misclassifying it.
4. For `SHOPIFY`, `shopifyDiscountNodeId` stays a real nonempty Shopify GID and must not use the reserved `woo:coupon:` prefix; `externalDiscountId` is `NULL` (legacy writer) or equals that GID. For `WOOCOMMERCE`, `externalDiscountId` must be a positive decimal coupon ID and `shopifyDiscountNodeId` must be **exactly** `woo:coupon:` concatenated with it; the row must represent a code-based coupon (`method=CODE`, one nonblank `singleRedeemCode`, `codeCount=1`). Enforce this conditional identity check without relaxing ARCH-016's existing code/method constraints.
5. A catalogue's provider must equal its `Shop.platform`, and every discount's `(shopId, provider)` must agree with its catalogue. Prefer **additive composite unique/FK protection** over application-only assertions: unique `(commerce.Shop.id, commerce.Shop.platform)` and `(ShopifyDiscountCatalogue.shopId, provider)` plus matching composite FKs, while preserving the old Shop and catalogue references. Include correct Prisma relation representation and safe `ON UPDATE` policy; never silently drop a legacy FK to make this pass. If Prisma cannot represent the additive constraints without breaking existing delegates, stop for an Architect decision before migrating.
6. Disallow changing a Shop's platform underneath an existing provider catalogue rather than silently changing provider ownership. Preserve all original discount IDs and their references.

### C. Durable paginated Woo generation state — no staging table

- The existing single catalogue row remains the synchronisation coordinator. `syncGeneration` and `activeSyncToken` continue to identify the claimed generation; `status=SYNCING` requires a token/start timestamp under the existing ARCH-016 check.
- On Woo `start`: initialise bounded expected counts, `syncNextPageIndex=0`, `syncPageDigests={}`, and the new server-owned active token/generation. New uploads are **not CURRENT**.
- On Woo `page`: `API-001` atomically writes that page's discount upserts **and** advances the existing catalogue progress row under a shop/catalogue lock. Page N is only accepted when N equals `syncNextPageIndex`; an exact digest replay is idempotent, but a changed replay or skipped page fails. All uploaded discount rows are marked with the active generation.
- On Woo `complete`: `API-001` checks token, expected page/item counts and received digests, then in **one transaction** marks absent rows unavailable and the catalogue `CURRENT`, clears active state and records `lastSuccessfulSyncAt`. An empty full generation must be able to invalidate all prior Woo rows.
- A failed, abandoned, superseded or partially received generation remains `SYNCING`/`ERROR`/otherwise non-CURRENT: **no producer or consumer may treat partially updated `isAvailable` rows as current**. Readers must gate on catalogue status, provider, generation, availability and freshness. A later successful generation reconciles the same physical rows.
- Database guards enforce structural bounds, platform identity and valid state shape. **API-001**, not this migration, owns digest comparison, page ordering, record-count verification, leases and atomic publish logic. Do not claim DB constraints alone prove an upload complete.
- Shopify's current worker still uses its existing single-transaction GraphQL snapshot reconciliation with the original fields. New Woo-only progress-field requirements **must not reject** Shopify `SYNCING` rows.

### D. Migration and rollback requirements

- New forward migration only. Add nullable external-ID/progress columns/defaults and nonbreaking indexes; **retain the required legacy Shopify node-ID column**; backfill; validate existing FKs and original IDs; then add the conditional constraints. Use a safe order for an upgraded database, not a fresh-only schema assumption.
- Run explicit preflight queries for invalid `Shop.platform`/discount-catalogue associations and duplicate generic external identities; failure must be intelligible, not silent deletion or forced reassignment.
- Preserve `shopify` physical PostgreSQL schema, primary keys, constraints/relation names where possible, and the existing ARCH-016 migration checksums.
- No automatic down-migration that drops original coupon/Shopify data. Rollback means **disable Woo sync/send** while retaining additive fields; document how old Shopify binary/Prisma clients remain functional throughout deployment.

## Work Items

- [ ] Inventory the exact schema, ARCH-016 migration, `ShopifyDiscountCatalogue`/`ShopifyDiscount` indexes, `Shop.platform`, all three discount FK consumers and existing Shopify writer queries.
- [ ] Implement the provider/additional external-ID columns, legacy-key **preservation**, defaults and Shopify backfill without changing row IDs, legacy required/unique semantics or existing FK targets.
- [ ] Add the provider/external-ID uniqueness and shop/catalogue provider consistency constraints; prove each legacy relation still exists and queries still succeed.
- [ ] Add bounded Woo progress columns with structural SQL guards and a new migration only; distinguish Woo and Shopify `SYNCING` checks.
- [ ] Write and run fresh, populated-upgrade and idempotent re-run migration rehearsals plus negative SQL fixtures.
- [ ] Record exact schema changes, migration path, applied validation commands/results, old-reader compatibility and any unresolved issue in the Completion Report.

## Interfaces / Contracts

- **Produced for API-001:** `provider`, `externalDiscountId`, `syncExpectedPages`, `syncExpectedItems`, `syncNextPageIndex`, `syncPageDigests`, pre-existing `syncGeneration`, `activeSyncToken`, `status`, `lastSeenSyncGeneration`.
- **Consumed by Shopify/Background/Commerce/Admin:** **unchanged** Prisma delegates `shopifyDiscountCatalogue`, `shopifyDiscount`, existing `(shopId,shopifyDiscountNodeId)` upsert, old `fixedShopifyDiscountId` FKs.
- **Provider source:** existing `commerce.Shop.platform` enum (`SHOPIFY`/`WOOCOMMERCE`); existing physical schema `shopify` is intentionally retained.
- **Shared wire owner:** `ARCH-036-SHARED-001` defines `woo.discounts.sync.v1`; SQL storage bounds above must not be exceeded by that contract. If wire bounds conflict, refer to Architect **before implementation** rather than silently selecting a different limit.
- This task does **not** publish `@modainteract/moda-interact-shared`, implement producer calls or change other repository imports.

## Dependencies

None. Independent of Shared schema implementation, but cross-check the agreed numerical bounds at review before approving consumers.

## Enables

- `ARCH-036-DATABASE-002`
- `ARCH-036-BACKGROUND-001`
- `ARCH-036-API-001`
- `ARCH-036-API-003`
- `ARCH-036-COMMERCE-001`
- `ARCH-036-ADMIN-001`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] **Zero new physical tables**, no changed historical migration, no physical table/schema relocation or lost Shopify discount IDs.
- [ ] Original 3 discount FK consumers still reference all their existing values; required `shopifyDiscountNodeId` and the compound Prisma upsert selector are **unchanged**, including when a new Shopify row has `externalDiscountId=NULL`.
- [ ] All pre-existing rows retain original ID, provider subtype, snapshot, sync generation, availability and lifecycle timestamps after upgrade.
- [ ] Woo coupon ID 719 can exist in Shop A and Shop B (internal key `woo:coupon:719`), but cannot appear twice in Shop A; a Woo ID cannot be misrepresented as a genuine Shopify GID.
- [ ] Shop-platform/provider mismatch and catalogue/discount-provider mismatch fail; no cross-tenant row assignment succeeds.
- [ ] Empty (0-page) Woo snapshot is representable; negative/over-limit page progress and malformed digest shapes are rejected.
- [ ] An incomplete snapshot remains unusable; a completed, fully reconciled snapshot can be represented `CURRENT` with matching generation metadata. Finalization is left to API-001.
- [ ] Existing Shopify `SYNCING` state and current reader queries remain valid.
- [ ] Fresh, populated-upgrade and repeat migration runs pass against disposable PostgreSQL; no unreviewed `migrate reset` or existing durable-state deletion.

## Validation

- [ ] `npm run validate` and `npm run prisma:generate` in `moda-interact-database` with supported Node/Prisma dependencies.
- [ ] `npm run test:arch016-recovery-schema` (unchanged legacy invariants), plus an ARCH-036 schema/migration fixture validator created by this task.
- [ ] Disposable PostgreSQL fresh apply, pre-ARCH-036 populated upgrade and repeat `migrate deploy` (or an equivalent tested migration harness); record command, connection-target safety and outcomes.
- [ ] SQL negative cases: provider spoof, duplicate same-shop coupon ID, differing-shop same coupon ID, malformed Woo ID, bad synthetic compatibility key, missing Woo code, invalid page counters/JSON, legacy new Shopify insert and existing FKs.
- [ ] Re-run focused legacy Shopify catalogue and recovery-policy schema assertions and `git diff --check`. Do not invent a `npm test` command if the database repository does not declare one.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, fill the Completion Report, submit the task for architect review and **STOP**. Do not begin DATABASE-002, API-001 or another enabled task. Repository agent/developer follows the configured developer completion authority.

## Implementation Notes

- Implementation is **database-owned only**. The existing physical models remain `ShopifyDiscountCatalogue` / `ShopifyDiscount` throughout ARCH-036's compatibility phase. Any future Prisma logical rename is a separate, coordinated cross-repository decision; do not introduce duplicate Prisma models mapped to the same physical table.
- A `providerType` value like Shopify `DiscountCodeBasic` or Woo `fixed_cart` is **not** `ShopPlatform`. Do not confuse them in backfill, indexes or checks.
- When adding composite FKs, verify unique-key prerequisites, cascading behaviour, Prisma relation mapping and the existing physical FKs rather than blindly accepting generated migration SQL.
- Validation harnesses must never target production or a developer's existing non-disposable database. Disclose any missing Docker/PostgreSQL prerequisite as blocked evidence, not a passing test.
- Materialisation/execution: parent and implementation `task/ARCH-036-DATABASE-001` branches plus launcher-resolved **isolated** worktrees; `/moda_developer_create ARCH-036-DATABASE-001` for developer execution. Record preparation packet, start sync and recursive submodules. This portable definition itself created no Git branches/worktrees/commits/pushes.

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

No unstated assumption may weaken Shopify compatibility, tenant isolation or the no-new-table rule.

### Unresolved Issues

None recorded; report unexpected catalogue/provider data and Prisma composite-FK incompatibilities before writing a migration.

### Architectural Concerns

Return cross-service contract, non-additive schema and compatibility gaps to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition; architect has not inspected an implementation or accepted completion.

### Reviewed Files

Source schema, ARCH-016 migration and Shopify discount worker reviewed for task definition; no implementation reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

Pending actual code, migration and PostgreSQL evidence.

### Follow-up

Materialise using the official task workflow once the definition has been agreed.
