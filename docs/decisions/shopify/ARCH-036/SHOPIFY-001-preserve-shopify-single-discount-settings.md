---
id: ARCH-036-SHOPIFY-001
architecture_id: ARCH-036
title: "Preserve Shopify fixed discount UX under selected-flag semantics"
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: 2026-10-13
---

# ARCH-036-SHOPIFY-001 — Preserve Shopify single-discount merchant settings

> **Superseded — do not execute or claim.** Superseded in Attempt 7: existing Shopify single-discount settings and Shopify `isAvailable` semantics are preserved unchanged. No Shopify merchant UI or selection-flag migration is authorised.
> The following original description is retained only as historical context; its Work Items, Dependencies and Acceptance Criteria are not operative.

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Preserve Shopify's existing **single FIXED discount** merchant and Admin behaviour while `ShopifyDiscount.isAvailable` becomes the explicit selection flag for both providers.

## Context

Existing Shopify settings use `ShopSettings.fixedShopifyDiscountId` as their only merchant choice. Older Shopify sync sets `isAvailable=true` for every discovered discount, and the Shopify Recovery Settings reader treats this as provider availability. BACKGROUND-004 removes sync writes and provides a safe one-time flag reconciliation keyed by the existing Shopify FK. This task updates the Shopify app's reads/validation/UI accordingly.

## Scope

Inspect and update Shopify merchant policy selection/read paths in `moda-interact/` to require genuine same-Shop ACTIVE/current/fixedSelectable status rather than taking `isAvailable` as provider availability; set/synchronise the single selected flag when the Shopify merchant chooses or changes its FIXED coupon. Preserve Admin override FK behaviour and legacy form affordances.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- Existing single `fixedShopifyDiscountId` FK and `EffectiveRecoveryPolicySchema` stay unchanged. When Shopify merchant saves a different FIXED discount, update the old/new `isAvailable` bits consistently with the FK under existing transaction/locking contract; NONE/AI cannot claim a coupon.
- Active selectable Shopify discounts must appear in the merchant dropdown whether selected or not; filter using `providerStatus='ACTIVE'`, `fixedSelectable`, dates and catalogue current, **not** `isAvailable=true`.
- Preserve capability/read_discounts checks, admin override, shop scoping and form validation. Never inadvertently treat a Woo compatibility ID as a Shopify GraphQL GID.
- No Prisma schema, migration, provider ID column or extra selection JSON.

## Work Items

- [ ] Update Shopify merchant list/selection predicates and saved state interpretation.
- [ ] Preserve single selected FK and transactionally maintain Shopify selection flags.
- [ ] Cover legacy rows, mode NONE/FIXED/AI, fresh selection, admin override and current/expired catalogue.
- [ ] Verify interoperability with BACKGROUND-004 one-time Shopify flag alignment.

## Interfaces / Contracts

Existing `ShopSettings.fixedShopifyDiscountId`, `ShopifyDiscount.isAvailable` and unchanged Shared recovery-policy validators.

## Dependencies

- `ARCH-036-BACKGROUND-004`

## Enables


- `ARCH-036-SYSTEM-TEST-001`
- `ARCH-036-BACKGROUND-003`
- `ARCH-036-ADMIN-001`

## Acceptance Criteria

- [ ] Shopify merchant still selects exactly one discount and FIXED stores existing FK.
- [ ] Shopify list includes active unselected discounts and excludes inactive providers.
- [ ] Shopify checkout recovery still uses only the configured discount, with no bulk selections introduced.
- [ ] No Woo-specific provider identity leaks into Shopify API calls.

## Validation

- [ ] Existing Shopify merchant discount list/policy form tests.
- [ ] Disposable Postgres same-Shop FK and flag consistency proof.
- [ ] Shopify production build/lint/regressions and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Only Shopify repository source may change.

For developer execution, use the canonical `/moda_developer_create ARCH-036-SHOPIFY-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-SHOPIFY-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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

The implementation executor will verify local checkout, dependencies and available toolchain at claim time.

### Unresolved Issues

None recorded by an implementation executor.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only, not implementation acceptance.

### Reviewed Files

Current 12 October 2026 source snapshot used to define ownership; implementation not yet reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

To be determined after implementation inspection.

### Follow-up

Await canonical materialisation, execution and review.
