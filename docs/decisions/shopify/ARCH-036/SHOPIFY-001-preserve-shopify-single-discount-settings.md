---
id: ARCH-036-SHOPIFY-001
architecture_id: ARCH-036
title: Preserve Shopify single-discount merchant settings
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-002", "ARCH-036-SHARED-003", "ARCH-036-BACKGROUND-001"]
enables: ["ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-SHOPIFY-001 — Preserve Shopify single-discount merchant settings

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Keep Shopify Recovery Settings and selected discount saves compatible with the provider-neutral catalogue while Woo gains multiple selections.

## Context

`app/services/recovery-policy/recovery-policy.server.ts`, `app/routes/app/recovery-settings/RecoverySettingsView.tsx` and settings-save route are tied to the single `fixedShopifyDiscountId` and Shopify discount catalogue.

## Scope

Adjust only Shopify merchant readers, policy saving and displayed catalogue projections for mapped provider-neutral DB records and compatible Shared contract. Keep Shopify one-discount selection and existing active/pending/error catalogue display unchanged.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

No new Shopify checkbox multi-selection unless separately authorised. Existing Shopify FIXED validator checks same shop, provider=SHOPIFY, active/fixed-selectable/current catalogue. NONE and AI modes retain prior semantics. Admin override remains authoritative; no accidental Woo coupon exposure in Shopify menus. Preserve existing localization.

## Work Items

- [ ] Adapt server readers and Shopify save validation to neutral models.
- [ ] Preserve Shopify UX, revision conflict and discount statuses.
- [ ] Run Shopify merchant settings, override, catalogue and regression suites.

## Interfaces / Contracts

Existing `/app/recovery-settings`, `/app/settings-save`, `@modainteract/moda-interact-shared/recovery-policy`, mapped DB discount rows.

## Dependencies

- `ARCH-036-DATABASE-002`
- `ARCH-036-SHARED-003`
- `ARCH-036-BACKGROUND-001`

## Enables

- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] All Shopify supported modes have unchanged behaviour; existing selected discount IDs still resolve.
- [ ] Woo coupons never appear for Shopify shops or pass the Shopify fixed discount validator.
- [ ] No Shopify webhook or queue contract changes.
- [ ] No untranslated Shopify labels.

## Validation

- [ ] Shopify settings/recovery-policy unit and integration tests
- [ ] Declared Shopify typecheck, lint, build and `git diff --check`

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
