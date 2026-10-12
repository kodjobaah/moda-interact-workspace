---
id: ARCH-036-BACKGROUND-001
architecture_id: ARCH-036
title: "Preload active Woo coupons into the existing catalogue without selecting them"
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-API-001", "ARCH-036-SHARED-003", "ARCH-036-BACKGROUND-004"]
enables: ["ARCH-036-BACKGROUND-002", "ARCH-036-ADMIN-001", "ARCH-036-SYSTEM-TEST-001", "ARCH-036-API-002"]
created: 2026-10-12
updated: 2026-10-12
---
# ARCH-036-BACKGROUND-001 — Reconcile Woo coupon catalogue by Background-pulled pages

## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_background` / `moda-interact-background`.
- **Defined but not materialised.** No task branch, dedicated worktree, implementation commit or push has been created.

## Objective

Fetch and reconcile WooCommerce coupons in the existing `ShopifyDiscountCatalogue`/`ShopifyDiscount` rows. Set provider-derived status and applicability metadata, **not** merchant checkbox selection.

## Context

The existing fields suffice; no schema/migration. The required `shopifyDiscountNodeId` carries `woo:coupon:<stable-positive-provider-id>` (not mutable code); `providerSnapshot` already stores JSONB rules; `isAvailable` now means selected. ARCH-036-BACKGROUND-004 first removes Shopify sync writes that formerly treated `isAvailable` as provider availability.

## Scope

Create a Woo-only scheduled reconciliation handler using the existing shop locks, generation fencing and BullMQ patterns. Call API-001's private paginated Woo reader (not direct Woo credentials), validate all pages, upsert same-Shop rows with required existing fields, and advance catalogue state only after a stable complete scan.

## Out of Scope

No new database table/column/migration for catalogues, no Woo plugin upload/hooks, direct provider credentials in Background, new queue platform, merchant-selected discount write or outbound offer sending.

## Requirements

- **Required existing-field mapping** (no DDL): `shopId` = real Woo Shop ID; `shopifyDiscountNodeId` = `woo:coupon:<positive provider id>`; `providerType` = bounded Woo type label; `method=CODE`; `providerStatus` = normalized `ACTIVE`, `EXPIRED`, `REMOVED`, `INACTIVE` or `EXHAUSTED` as warranted by verified facts; `title` = safe code/title; `singleRedeemCode` = actual mutable coupon code; `providerSnapshot` = non-null safe JSON restrictions/type/amount; `lastSeenSyncGeneration` = actual claimed generation; `lastSyncedAt` = actual UTC sync time; `fixedSelectable` = supported-rule flag. Never fill genuine required facts with fake placeholders. Optional dates/summary may be null when unknown.
- New rows start `isAvailable=false`; existing active-row selection flags are retained across ordinary refreshes and code changes. Do **not** set true from provider discovery. When a coupon becomes terminally non-ACTIVE after a verified complete scan, clear `isAvailable=false` as a safety invalidation; later reactivation must require merchant re-selection. On transient provider outage/incomplete scan, **do not** clear selections or falsely mark REMOVED; set catalogue non-current and fail closed.
- Only ACTIVE, fixedSelectable, in-date, positive-valued rows in a fresh CURRENT catalogue appear as selectable; providerStatus is provider-derived, `isAvailable` selection. Coupon listing alone never proves checkout applicability. Expiry/time-of-use must be rechecked at reads and send time.
- Use validated full-generation fencing, bounded pagination, stable scan detection, missing-row REMOVED handling, retry and retention. Preserve foreign Shop rows and never hard-delete referenced discount/history rows. Provider failure cannot complete an empty sync.
- No Woo uploader, WordPress Action Scheduler integration, new table/column, or direct Woo credentials in Background.

## Work Items

- [ ] Use published API-001 read-page contract to enumerate 0/120+ Woo coupons safely.
- [ ] Map required Woo values into existing mandatory Prisma fields and JSONB snapshot.
- [ ] Preserve `isAvailable` selections on active refresh; never auto-select; clear only upon verified terminal invalidation, not network failure.
- [ ] Fence generations and mark missing as REMOVED without destructive row deletion.
- [ ] Cover code rename, expiry, exhausted, reinstatement requiring reselect, invalid page, duplicate job, no grant and Shopify sync regressions.

## Interfaces / Contracts

API-001 Woo read pages (published SHARED-001), existing Prisma discount/catalogue rows, existing BullMQ. `providerStatus` controls provider availability; `isAvailable` is a selected boolean. All required fields receive real Woo-compatible values.

## Dependencies

- `ARCH-036-API-001`
- `ARCH-036-SHARED-003`
- `ARCH-036-BACKGROUND-004`

## Enables

- `ARCH-036-BACKGROUND-002`
- `ARCH-036-ADMIN-001`
- `ARCH-036-SYSTEM-TEST-001`
- `ARCH-036-API-002`

## Acceptance Criteria

- [ ] Preloading 120 coupons uses existing tables and real, deterministic Woo keys with no non-null constraint failure.
- [ ] Sync never checks a merchant checkbox; it preserves active selections and invalidates only conclusively non-ACTIVE rows.
- [ ] Removed/expired/unselectable rows are excluded from active merchant reads; history remains.
- [ ] Failed/incomplete scan does not erase choices or produce phantom active offers.
- [ ] Shopify sync behavior and all tenant isolation invariants pass.

## Validation

- [ ] Focused Woo provider normaliser, generation, missing and expiry cases.
- [ ] Disposable PostgreSQL with original schema; no DDL and FK/constraint checks.
- [ ] Background test/typecheck/build and `git diff --check`.

## Stop Condition

After bounded work, acceptance checks and required validation: document the Completion Report, set the task to `review` and STOP. Do not begin dependent tasks. For `superseded` tasks, do not execute or claim.

## Implementation Notes

Maintain **existing Prisma model names**. A new service named WooDiscountCatalogueService is acceptable; a competing generic logger or duplicate catalogue table is not. If the existing lock allows only one provider per Shop, this is correct because each Shop has exactly one platform.

For developer execution, materialise/prepare the canonical `task/<TASK_ID>` parent and implementation worktrees through `/moda_developer_create`; for agent execution use `/moda-task`. Record launcher-resolved paths, start-of-attempt sync, recursive submodule evidence, branch/commit and actual test results. Do not edit shared/default checkouts or domain `_index.md` files.

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

The executor will verify checkout, actual dependencies, task worktrees and available toolchain at claim time.

### Unresolved Issues

None recorded.

### Architectural Concerns

Stop and return cross-repository, credential, provider compatibility or schema deviations to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable revised definition; no implementation submitted or accepted.

### Reviewed Files

Source snapshot and task contract only. No execution files reviewed.

### Validation Reviewed

No implementation tests have run as part of this definition.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Await real task materialisation, execution, Completion Report and Architect review.
