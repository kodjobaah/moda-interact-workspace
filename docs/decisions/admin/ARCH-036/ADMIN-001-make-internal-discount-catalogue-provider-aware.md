---
id: ARCH-036-ADMIN-001
architecture_id: ARCH-036
title: "Show provider status and merchant selection separately in Admin"
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-BACKGROUND-001"]
enables: ["ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-11-02
---

# ARCH-036-ADMIN-001 — Show provider-aware discount provenance in Moda Admin

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Canonical parent task definition is published on `task/ARCH-036-ADMIN-001`. Implementation remains unclaimed; prepare it through `/moda_developer_create` before editing application code.

## Objective

Make Admin discount catalogue and recovery policy presentation provider-aware without conflating provider status with merchant selection.

## Context


The existing Admin console reads discount rows and ShopSettings/override FK. BACKGROUND-001 adds **Woo rows only** into the same table. For Woo, `providerStatus` is provider lifecycle and `isAvailable` is merchant selection; for Shopify, accepted ARCH-052-BACKGROUND-009 also makes `isAvailable` merchant selection; provider availability is represented separately. Background owns Woo provider synchronisation; API-002 owns Woo merchant checkbox changes. Admin must keep merchant selection and provider validity distinct on both platforms.

## Scope

Update internal list/filter/badges and recovery override presentation for **Woo**. Display provider, provider status, Woo selected-for-recovery flag and catalogue freshness independently. Preserve existing override actor/reason/audit/expiry behaviour and Shopify single-FK controls without changing Shopify selection/sync.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- For Woo, never interpret `isAvailable=false` as deleted/provider unavailable; show unselected ACTIVE coupons as provider-valid. For Shopify, preserve the accepted ARCH-052-BACKGROUND-009 meaning: `isAvailable` is merchant selection; use provider status/current-catalogue/liveness fields for provider validity.
- Only ACTIVE/current/in-date/fixedSelectable rows can appear as assignable Admin choices. These predicates establish catalogue/code usability, not checkout eligibility or guaranteed redemption. Display expired, removed, unselectable and revoked/stale rows distinctly; missing optional provider facts must not be invented or labelled checkout-valid.
- Admin override FIXED retains one **real same-Shop discount FK** and is independent of Woo merchant checkbox selections; use valid provider/catalogue predicates rather than requiring a Woo checkbox to be checked. Preserve Shopify override behaviour, audit and authorization without inventing multi-coupon override storage or placing Woo namespace in an FK.
- No SQL/schema changes, historical row deletions, security/role expansion or cross-tenant catalogue leakage.

## Work Items

- [ ] Update `src/lib/admin/data.ts` catalogue queries and `src/components/admin/tenant-recovery-settings.tsx` presentation so Woo catalogue validity, assignability and merchant selection are separate; preserve existing Shopify behavior.
- [ ] Preserve Admin single-FK override and audit semantics.
- [ ] Add provider-aware Shop, empty/error and inactive coupon fixtures.
- [ ] Test merchant/Admin isolation and Shopify regression.

## Interfaces / Contracts


Existing Prisma discount/policy rows and shop/role authorisation. No API-001 read proxy or new Shared contract; no new schema.

## Dependencies

- `ARCH-036-BACKGROUND-001`

## Enables

- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Admin shows ACTIVE unselected coupons distinctly from removed/expired coupons.
- [ ] Both list reads and override writes enforce the target Shop/provider; stale, removed, expired, unselectable and foreign-Shop IDs are rejected on the server, including rows invalidated after the list was loaded.
- [ ] Existing Shopify Admin override and audit work **without changing Shopify behaviour**; Woo FIXED override can choose a valid same-Shop coupon independently of the merchant checkbox flags.
- [ ] No database change.

## Validation

- [ ] Focused Admin read/write tests for ACTIVE checked and unchecked Woo rows, stale catalogue, expiry, removed/unselectable rows, foreign-Shop IDs and a stale-choice write; prove unchecked valid Woo coupons remain assignable by Admin while existing Shopify predicates remain unchanged.
- [ ] Verify desktop/narrow layouts, provider/selection labels and existing override actor/reason/audit/expiry behavior; no merchant checkbox-write endpoint or new permissions.
- [ ] Role/tenant constraints, lint, typecheck/build and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Do not change Shopify app, Shopify sync, CommerceAgent, recovery workers, or Woo plugin from Admin. Admin may expose only Woo catalogue status/selection and the existing single-FK override.

For developer execution, use the canonical `/moda_developer_create ARCH-036-ADMIN-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-ADMIN-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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

## Definition reconciliation — 2026-11-02

Admin main 420b86a still filters running/selectable discounts using isAvailable:true in src/lib/admin/data.ts (around lines 342–370), and tenant-recovery-settings.tsx presents Shopify-specific catalogue/override labels. Provider-aware Woo display and checkbox-independent Woo override choices remain unimplemented. Apply the corrected Shopify selection semantics above and run the required tenant/override/regression tests.

## Implementation readiness — 2026-11-02

Ready, Attempt 0, unclaimed. The accepted Background prerequisite is complete. Implement only Admin queries, UI and server-side override validation; neither Commerce work nor new provider fetching is a prerequisite. Keep developer-controlled completion: submit for architect acceptance, then await the explicit developer completion decision.
