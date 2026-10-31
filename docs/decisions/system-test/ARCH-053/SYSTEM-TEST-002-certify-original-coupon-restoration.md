---
id: ARCH-053-SYSTEM-TEST-002
architecture_id: ARCH-053
title: Certify original applied-coupon capture persistence and restoration
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-WOOCOMMERCE-004
- ARCH-053-WOOCOMMERCE-006
- ARCH-053-BACKGROUND-003
- ARCH-053-WOOCOMMERCE-003
- ARCH-048-BACKGROUND-011
- ARCH-046-WOOCOMMERCE-003
enables: []
created: 2026-10-29
updated: 2026-10-31
---

# ARCH-053-SYSTEM-TEST-002 — Certify original applied-coupon capture persistence and restoration

## Architecture

Architecture: `ARCH-053`; document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Defined but not materialised**; the author has not created or pushed a developer task branch or implementation worktree.

## Objective

Certify original applied-coupon capture persistence and restoration. This is a bounded, independently reviewable capability owned only by `moda_system_test` in `moda-interact-system-test`.

## Context

The 2026-10-29 snapshot captures products but lacks complete end-to-end original-coupon recovery. `ARCH-052` owns dynamic discount discovery and new offers, **not** previously applied Woo checkout coupons. The ARCH-053 complete restore contract is `woo.cart-restore.v1`, with `appliedCouponCodes: string[]` on the immutable snapshot. Do not design a separate coupon issuance engine or a new database coupon table.

## Scope

- Add coupon-specific e2e fixtures and scenarios in `moda-interact-system-test` using its existing runner and WordPress/Woo Classic and Checkout Blocks; coordinate real API/BullMQ/Background/PostgreSQL paths with provider mocks. Do not modify application repositories.
- Exercise original coupon addition and removal on an observed checkout (including no change to products or totals), canonical HTTP v1→v1 queue payload, updating delayed candidate, immutable coupon evidence at recovery admission, and resolution for the correct generation.
- From WhatsApp-like URL open on another browser, ensure GET does not mutate cart/recovery; confirm POST restores the original products and *attempts* exactly the original codes under current shop policy, recalculates the price, records rejection privately and does **not** display any Moda-originated error or Woo error notice triggered by the plugin.
- Verify coupon-only updates use the **same** `woo.activity.v1` checkout event and that v2/v3 HTTP checkout activity is rejected after pre-production cutover; do not treat missing restoration as an empty coupon list.
- Coupon matrix: zero coupons (`[]`), one valid, expired, deleted, usage exhausted, minimum spend no longer met, product exclusion, stacking conflict, mixed valid/invalid, coupon removed before abandonment, and coupon-only update after a previously stored recovery (new generation).
- Prove invalid coupon does not force previous total, block otherwise-valid products or trigger automatic ARCH-052 incentive replacement; test 2 tenants, stale generation URL and no token/coupon logging.

## Out of Scope

- No ARCH-052 dynamic discount selection, discount creation, extension of coupon expiry, or automatic coupon replacement.
- No changes in other repository-owned source, no Woo production WhatsApp enablement, no bypass of consent/STOP/order or final-send guards.
- No broad refactor, new Generic logger, direct WordPress access to Moda database/Redis, or continuation into enabled tasks.

## Requirements

- Only current WooCommerce policies determine if a historical coupon remains applicable. Business rejection and unexpected platform/restore failure must be separately visible in test reports.
- Both Classic and Blocks must show accurate Woo totals and correctly applied coupon state **without any Moda-generated rejection/errors after redirect**. Ordinary pre-existing Woo notices and errors entered by the shopper directly remain unchanged; do not accept mock-only checkout UI results.
- Only run after every listed implementation dependency is architect-accepted Complete and the developer has had the optional manual-verification checkpoint; system test is terminal and enables no implementation tasks.
- Use exact shared schema from accepted `ARCH-053-SHARED-001` (PHP must match its JSON fixtures, not import Node code). Zod validates wire *shape*, never WooCommerce coupon policy. Preserve stable checkoutKey, tenant scoping and generation semantics.
- Never log original coupon codes, raw restoration URLs/tokens, customer contact details or unbounded exception content. Merchant-side PHP uses existing protected server-side plugin diagnostics only; the Shared npm logger applies to hosted Node services, not WooCommerce PHP. Original safe failure details must be preserved privately, not rendered into storefront HTML/notices.
- Honour launcher-prepared, dedicated synchronised task worktrees and `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`; the repository agent updates only its assigned task metadata and Completion Report. Never mark itself Complete or push main.

## Work Items

- [ ] Build deterministic cross-service coupon fixtures for checkout events, candidate maturity, immutable recovery and WhatsApp link resolution.
- [ ] Exercise original coupons under current valid/expired/restricted/stacking rules on Classic and Blocks; assert the exact Woo totals, **absence of Moda/Woo plugin-induced error notices**, preservation of pre-existing Woo notices and protected server log details.
- [ ] Test replay, coupon-only updates, generational identity, consent/STOP, never-issue-new-coupon and no loss of successfully restored products.
- [ ] Produce a matrix in Completion Report linking each required scenario to command, evidence and pass/fail; report defects to owning agent task, not fix implementation.

## Interfaces / Contracts

Consumes ARCH-053 Shared v1 restore snapshot, API v1 ingest with Shared-validated restoration, Background candidates/admission, API resolve v1 and WordPress coupon-restoration + private-outcome tasks; ARCH-048 owns closure/new-generation rules. No new system contract.

## Dependencies

- `ARCH-053-WOOCOMMERCE-004` — must be architect-accepted Complete
- `ARCH-053-WOOCOMMERCE-006` — must be architect-accepted Complete
- `ARCH-053-BACKGROUND-003` — must be architect-accepted Complete
- `ARCH-053-WOOCOMMERCE-003` — must be architect-accepted Complete
- `ARCH-048-BACKGROUND-011` — must be architect-accepted Complete
- `ARCH-046-WOOCOMMERCE-003` — must be architect-accepted Complete

## Enables

None.

## Acceptance Criteria

- [ ] A valid applied original coupon survives capture→queue→candidate→recovery→resolve→native reapplication and shows the current approved discount.
- [ ] Expired/exhausted/ineligible coupon does not apply, old total is not restored, a private rejection diagnostic exists without a Moda/Woo plugin-generated error notice after redirect and customer can still pay for valid products.
- [ ] Multiple coupons and coupon add/remove events yield the exact current Woo results with no dropped codes or duplicate sends.
- [ ] Superseded generation, token failure, preview GET and cross-tenant access never restore or mutate any shopper cart.
- [ ] ARCH-052 dynamic discount creation is not used anywhere in coupon restoration.
- [ ] No new discounts/coupon extension, no automatic replacement of a previously applied invalid coupon, no silent omission from internal diagnostic evidence or falsification of the actual Woo total.
- [ ] Failed/invalid/replayed operations do not create duplicate recovery generations, outbound attempts or billings.
- [ ] Only owning repository implementation and authorised task metadata are changed; ARCH-052 remains untouched.

## Validation

- [ ] Run system-test repository declared e2e suite against real supported Woo Classic and Blocks, API, Redis and Postgres
- [ ] Run failure injection/replay tests for candidate and generation identity
- [ ] Record command, environment, evidence matrix and `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, record the exact commands/evidence, files, deviations and unresolved issues in `## Completion Report`, set the task to `review`, return to `moda_architect` and STOP. Do not implement another task.

## Implementation Notes

This task is separate from SYSTEM-TEST-001, which certifies core link/product restoration. Both are terminal; neither should gate an application task. ARCH-053 is not Implemented until both pass.

## Completion Report

### Status

Not Started

### Files Changed

None — task is defined but not materialised.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

Codebase snapshot dated 2026-10-29; inspect actual HEAD after launcher preparation before implementing.

### Unresolved Issues

None asserted until work is claimed.

### Architectural Concerns

Return schema, lifecycle and multi-repository discrepancies to `moda_architect` rather than improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet assessed.

### Follow-up

None.
