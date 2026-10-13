---
id: ARCH-036-BACKGROUND-004
architecture_id: ARCH-036
title: Stop Shopify sync from overwriting merchant selection flags
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: 2026-10-13
---

# ARCH-036-BACKGROUND-004 — Stop Shopify catalogue sync from overwriting selection flags

> **Superseded — do not execute or claim.** Superseded in Attempt 7: Shopify `isAvailable` continues to represent provider availability and Shopify sync is unchanged. No one-time flag alignment or Shopify schema/data update is authorised.
> The following original description is retained only as historical context; its Work Items, Dependencies and Acceptance Criteria are not operative.

## Architecture

- Architecture: `ARCH-036`, `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Owner: `moda_background`, repository `moda-interact-background`, coordinator `moda_architect`.
- Defined but not materialised; no task branch, worktree, implementation or acceptance yet.

## Objective

Preserve existing Shopify discount synchronisation while changing `ShopifyDiscount.isAvailable` from provider availability to **merchant-selected** state without any database schema change.

## Context

The current `shopify-discount-catalogue.service.ts` upsert unconditionally sets `isAvailable=true` for every discovered discount, clears it for missing discounts and clears all flags on catalogue access failure. These writes conflict with checkbox selection semantics. Other existing writers, including `billing-subscription-reconciliation/reinstall-reconciliation.service.ts`, also clear the same flag and must be audited for intentional selection-reset semantics. Existing Shopify settings have a single `fixedShopifyDiscountId` FK; current historical `isAvailable=true` rows may just mean present at Shopify, not selected.

## Scope

Modify only `moda-interact-background` Shopify discount synchronisation and provide an idempotent, explicitly invoked one-time **data alignment** using existing `ShopSettings.fixedShopifyDiscountId`, for Shopify Shops only. Preserve existing generation token/retry fencing, provider status, catalogue permissions and all physical Prisma/SQL schema.

## Out of Scope

- No Woo coupon REST reads or new provider API; BACKGROUND-001 owns those.
- No database model/column/constraint/migration changes, new sync tables or new queue platform.
- No Shopify merchant UI changes; SHOPIFY-001 owns those.
- No automatically authorising unselected discounts or modifying historical outbound attempts.
- No `_index.md` changes or downstream task execution.

## Requirements

1. **Selection separation:** ordinary Shopify sync must never set `isAvailable=true` merely because a provider reports a discount. A new discount defaults false; valid active-row re-sync preserves its existing merchant selection. `providerStatus`, `fixedSelectable`, catalogue status and expiry remain provider-derived.
2. **Explicit invalidation:** on verified, completed lifecycle transition to REMOVED/EXPIRED/INACTIVE/EXHAUSTED, `isAvailable` may be cleared false to prevent automatic reactivation without new merchant selection. Never clear selections on transient sync failure/revoked scope; mark catalogue non-current and fail closed using existing catalogue status.
3. **Safe one-time Shopify alignment:** with an explicit, opt-in dry-run/apply script or bounded controlled administrative operation, set each Shopify Shop's true bit **only** on the row named by its current merchant `ShopSettings.fixedShopifyDiscountId` when FIXED, false on other Shopify discount rows. Admin override FK does not become merchant selection. Limit to `Shop.platform=SHOPIFY`, never touch Woo Shops. The operation must be safe to rerun after Shopify settings changes because it reflects the current single FK; record pre/post counts and tenant evidence.
4. **No provider spoofing:** do not change GraphQL IDs into Woo keys, invent status values or fetch Woo coupons. Remove SQL/Prisma queries that conflate selected flag with provider availability; retain Shopify current/expiry/fixedSelectable predicates.
5. **Coordinated rollout:** Shopify application consumer SHOPIFY-001 must be updated/accepted and deployed coherently before using new semantics live. Production data state remains preserved; no implicit destructive reset.

## Work Items

- [ ] Audit **all** Background writers of `ShopifyDiscount.isAvailable` (including reinstall/subscription reconciliation); remove provider-presence writes and explicitly document legitimate selection resets.
- [ ] Preserve current generation status/fencing, update verified inactive provider states and stable-row selection.
- [ ] Build one-time Shopify FK-to-selection alignment with dry-run, idempotent repeat and cross-tenant guards.
- [ ] Add initial/second sync, selected/unselected, invalidation, outage, two-Shop, override and alignment regression tests.

## Interfaces / Contracts

Existing `ShopifyDiscountCatalogue`, `ShopifyDiscount`, `ShopSettings`, `Shop.platform` and Shopify provider read permission. No new Shared/runtime contract and no database schema changes.

## Dependencies

None.

## Enables


- `ARCH-036-BACKGROUND-001`
- `ARCH-036-SHOPIFY-001`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Repeated full Shopify sync does not reselect unchecked coupons.
- [ ] A new discount is unselected until merchant chooses it.
- [ ] Temporary provider outage keeps merchant selections but marks catalogue non-current.
- [ ] Verified removed/expired discounts cannot be offered or silently reselected after reactivation.
- [ ] One-time Shopify alignment preserves the existing chosen FK, is repeatable and never updates Woo shops.
- [ ] Existing Shopify sync worker and discount catalogue security/race regressions pass.

## Validation

- [ ] Focused Shopify discount sync tests plus rerun of existing policy/permission regressions.
- [ ] Disposable PostgreSQL with existing migration-current schema: one-time dry-run/apply/reapply plus two shops and FK references.
- [ ] Declared Background typecheck, lint, test/build and `git diff --check`.

## Stop Condition

After the bounded changes, required Validation and Completion Report, set the task `review` and STOP. Do not execute BACKGROUND-001 or SHOPIFY-001 without explicit Architect promotion.

## Implementation Notes

This task is developer-executed: use `/moda_developer_create ARCH-036-BACKGROUND-004` in the canonical primary workspace when Ready. Record launcher-resolved dedicated parent + implementation worktrees, start-of-attempt sync, recursive submodule evidence, clean task branches and real validation. No branch, push or worktree was created by this portable definition. Do not modify shared/default checkouts or domain `_index.md`.

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

The new flag semantics apply to both providers only after coordinated consumer updates.

### Unresolved Issues

None recorded; return lifecycle/reinstall conflicts to the architect.

### Architectural Concerns

Any requirement for schema changes, new tables, provider access or ownership changes must return to moda_architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable task only; no code review or acceptance.

### Reviewed Files

Existing Shopify discount sync and ShopSettings/ShopifyDiscount schema were inspected for task design.

### Validation Reviewed

None for this task.

### Architecture Conformance

To be determined after implementation.

### Follow-up

Await task materialisation and independent review.
