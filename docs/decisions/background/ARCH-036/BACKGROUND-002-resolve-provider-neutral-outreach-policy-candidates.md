---
id: ARCH-036-BACKGROUND-002
architecture_id: ARCH-036
title: "Resolve selected Woo coupon candidates from existing flags"
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-SHARED-003", "ARCH-036-BACKGROUND-001", "ARCH-036-BACKGROUND-004", "ARCH-036-SHOPIFY-001"]
enables: ["ARCH-036-BACKGROUND-003", "ARCH-036-SYSTEM-TEST-002"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-BACKGROUND-002 — Resolve provider-aware recovery offer candidates

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Resolve provider-aware NONE/FIXED/AI recovery offer candidates using the existing coupon rows, `providerStatus`, `fixedSelectable`, `isAvailable` and existing policy FK, without new storage.

## Context

The existing Background policy reader uses `fixedShopifyDiscountId` and `isAvailable` under the older provider-availability interpretation. Under ARCH-036, Shopify FIXED still uses its single valid FK; Woo FIXED draws from the **multiple** active/current same-Shop rows with `isAvailable=true`, not just the FK compatibility anchor. AI considers supported active rows irrespective of merchant-selected flags.

## Scope

Refactor Background policy resolution and candidate query only. Preserve existing attempt sequence, recipient snapshot, provider billing and immutable `offerSnapshot`. Do not execute send-time API proof or send messages in this task.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- `NONE` => no coupon. `FIXED` Woo => selected (`isAvailable=true`) AND `providerStatus='ACTIVE'` AND `fixedSelectable=true`, in-date, positive-value/current same-Shop. `AI_BEST_APPLICABLE` => same active/supported checks but **ignore selection flag**.
- Merchant FIXED FK anchor is a real same-Shop selected row but only satisfies the existing policy CHECK. Do not interpret it as the sole candidate. Admin FIXED override remains its existing single FK and may intentionally override merchant selections; its coupon still requires live status/eligibility proof.
- If FIXED configured but no viable candidate, fail closed without creating an invalid `RecoveryOutreachAttempt(configuredOfferMode=FIXED,fixedShopifyDiscountId=NULL)` or inventing a coupon/false NONE configuration. Record a deterministic unavailable resolution and return for an explicit fallback decision where needed.
- A Shop whose catalogue is not CURRENT/fresh cannot supply discount candidates; use shop-scoped queries and bounded candidate counts. Retain Shopify single-selection behaviour with its explicit FK.
- Never change Prisma schema, historic SQL constraints, or completed outreach attempts.

## Work Items

- [ ] Read provider-aware effective merchant/admin policy and current catalogue safely.
- [ ] Resolve Woo FIXED selected rows and AI all-active rows; preserve Shopify existing FK path.
- [ ] Enforce stale/expired/removed/no-selection fail-closed semantics and existing attempt constraint.
- [ ] Test override precedence, two shops, multiple flags, invalid anchor, no eligible coupon and cost/order regressions.

## Interfaces / Contracts

Existing `ShopSettings`, `ShopRecoveryPolicyOverride`, `ShopifyDiscount`, `RecoveryOutreachAttempt` and Shared proof contract; no new policy fields.

## Dependencies

- `ARCH-036-SHARED-003`
- `ARCH-036-BACKGROUND-001`
- `ARCH-036-BACKGROUND-004`
- `ARCH-036-SHOPIFY-001`

## Enables

- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Woo FIXED selects from multiple merchant-checked alternatives, never coupon stacks.
- [ ] AI ignores merchant flags but filters ACTIVE supported coupons.
- [ ] Legacy Shopify and Admin fixed FK semantics retained.
- [ ] No invalid FIXED attempt inserted and no false coupon promise.

## Validation

- [ ] Focused provider-aware policy resolution and no-candidate tests.
- [ ] Existing attempt SQL CHECK fixture on unchanged schema; retry/order/billing tests.
- [ ] Background declared tests/typecheck/build and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Candidate resolution is not definitive checkout eligibility and must not send a discount.

For developer execution, use the canonical `/moda_developer_create ARCH-036-BACKGROUND-002` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-BACKGROUND-002`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
