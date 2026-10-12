---
id: ARCH-036-SHARED-002
architecture_id: ARCH-036
title: Define provider-neutral selected-offer and proof contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: ["ARCH-036-SHARED-003"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-SHARED-002 — Define provider-neutral selected-offer and proof contracts

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Define portable selected-discount IDs and immutable per-attempt offer proof formats for Shopify and WooCommerce.

## Context

Existing `recovery-policy` Shared schema assumes a single `fixedShopifyDiscountId`. New Woo FIXED mode permits multiple selected coupons; at send time the system must choose one and produce a provider-aware offer snapshot.

## Scope

Add a new versioned provider-neutral policy/selection contract, normalized coupon rule/evidence result, and immutable offer-snapshot envelope. Keep compatibility with the published Shopify recovery-policy schema during consumer transition. Do not change database schema or services.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Offer modes remain `NONE`, `FIXED`, `AI_BEST_APPLICABLE`; `NONE` never mentions coupons, `FIXED` requires a selected allowed set, AI draws only from demonstrably applicable current coupons. A send outcome chooses one coupon, never stacks several selected coupons. Evidence includes provider, shop, coupon ID/code, evaluated basket provenance, rules digest, currency, verified time, expiry and `QUALIFIES`/`UNKNOWN`/`DENIED`. Unknown/unsupported/stale evidence cannot be sent. Preserve legacy immutable outbound attempts and supported Shared package versions.

## Work Items

- [ ] Author bounded normalized selection, candidate and proof contracts.
- [ ] Define versioned legacy Shopify mapping and outbound attempt snapshot rules.
- [ ] Test mode matrix, unknown/restricted coupons, stale evidence and cross-shop IDs.
- [ ] Document provider/customer/basket scope and TTL semantics without inventing remote-proof method.

## Interfaces / Contracts

`@modainteract/moda-interact-shared/recovery-policy` compatibility plus proposed `/discounts` v1 exports; consumers: API, Background, Woo data client, Commerce evaluator; Shopify compatibility fixtures.

## Dependencies

None.

## Enables

- `ARCH-036-SHARED-003`

## Acceptance Criteria

- [ ] No duplicate service-local wire schema definitions for the same boundary.
- [ ] One selected coupon is the maximum per outreach; AI has no authority to manufacture codes.
- [ ] Existing Shopify FIXED policy and historical snapshots still parse.
- [ ] Every unsuccessful eligibility branch is fail closed.

## Validation

- [ ] Shared validators, compatibility golden fixtures and negative cases
- [ ] Typecheck/lint/build and `git diff --check`

## Implementation Notes

Do not publish or integrate this task; SHARED-003 is the release gate.

For developer execution, use the canonical `/moda_developer_create ARCH-036-SHARED-002` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-SHARED-002`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
