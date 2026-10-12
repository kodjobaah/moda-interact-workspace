---
id: ARCH-036-SYSTEM-TEST-001
architecture_id: ARCH-036
title: Certify shared catalogue sync and merchant selection
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
depends_on: ["ARCH-036-BACKGROUND-001", "ARCH-036-BACKGROUND-004", "ARCH-036-SHOPIFY-001", "ARCH-036-API-002", "ARCH-036-WOOCOMMERCE-003", "ARCH-036-ADMIN-001"]
enables: ["ARCH-036-SYSTEM-TEST-002"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-SYSTEM-TEST-001 — Certify shared catalogue sync and merchant selection

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Independently certify provider-aware coupon catalogue synchronisation and multi-checkbox merchant selections on the **unchanged** existing database schema, including Shopify compatibility.

## Context

This is a terminal architecture-level test after its implementation dependencies are accepted; developer manual LocalWP testing may happen before invoking it.

## Scope

Black-box Background + authenticated API-owned provider connection + database + Woo merchant UI tests for initial sync, cross-shop page reads, unstable/retried pages, stale generation, deletes, identity, selection CAS, 20-language UI and Shopify compatibility. Keep independent test fixtures and reproducible evidence.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements


- Exercise full multi-page background-provider coupon fetching with verified Woo REST read grant, direct outbound canonical URL/TLS/SSRF constraints, expired/removed/restricted coupon handling and incomplete generation fail-closed.
- Assert real Woo rows use `woo:coupon:<id>`, `providerSnapshot` JSONB, provider lifecycle status separate from `isAvailable` merchant flags. New rows unchecked, active resync preserves checkboxes; transient provider error cannot clear selections.
- Test two Woo merchants plus Shopify: shop isolation, current ACTIVE/fixedSelectable checked and unchecked UI rows, paging/search and 20 locales.
- Save multiple checkbox selections through API-002 with one real same-Shop FK anchor for Woo FIXED; reject invalid/foreign/conflicting/empty FIXED writes atomically. Prove Shopify one-time flag alignment and existing one-FK merchant behavior on **unchanged SQL schema**.
- Confirm grant revocation, rotation/missing keyring and LocalWP unreachable-host constraints have honest blocked/unavailable outcomes; never present provider failure as an empty successful catalogue. Run system tests only after all listed implementation tasks are accepted.

## Work Items

- [ ] Fixture three shops and multi-page coupons with changing provider state.
- [ ] Prove stable provider fetch, persisted CURRENT generation and provider-status filtering.
- [ ] Exercise checkbox CAS, real-FK anchor, conflict and stale grant cases.
- [ ] Check Shopify one-time alignment and current UI/regressions on unchanged SQL schema.
- [ ] Record screenshots and database read-only assertions with reproducible evidence.

## Interfaces / Contracts


Real or simulatable reachable WooCommerce `wc/v3/coupons` over authorised, Background-held read-only grant; existing Prisma discount/policy models; API-002 merchant selection read/write through the WordPress facade. No new Shared contract or API coupon proxy.

## Dependencies


- `ARCH-036-BACKGROUND-001`
- `ARCH-036-BACKGROUND-004`
- `ARCH-036-SHOPIFY-001`
- `ARCH-036-API-002`
- `ARCH-036-WOOCOMMERCE-003`
- `ARCH-036-ADMIN-001`

## Enables

- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Selection flags and provider availability are independent and never conflated.
- [ ] Active unselected coupons are visible; expired/removed coupons cannot be selected.
- [ ] `FIXED` FK/constraint pass with one real Woo row while multiple flags are selected.
- [ ] All provider/data isolation and Shopify compatibility checks pass.
- [ ] Zero migrations/tables/columns/constraints introduced.

## Validation

- [ ] Black-box and integration harness with disposable Postgres and LocalWP fixtures
- [ ] 20-language UI and shop/auth boundary evidence, `git diff --check`

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Terminal test only: no implementation task depends on SYSTEM-TEST-001.

For developer execution, use the canonical `/moda_developer_create ARCH-036-SYSTEM-TEST-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-SYSTEM-TEST-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
