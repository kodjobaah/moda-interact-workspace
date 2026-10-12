---
id: ARCH-036-BACKGROUND-002
architecture_id: ARCH-036
title: Resolve provider-aware recovery offer candidates
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
depends_on: ["ARCH-036-DATABASE-002", "ARCH-036-SHARED-003", "ARCH-036-BACKGROUND-001"]
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

Resolve NONE, FIXED multi-selection and AI candidate sets per Shop without altering checkout recovery or proactive outreach billing lifecycles.

## Context

`src/services/recovery-policy.service.ts` currently looks up `fixedShopifyDiscount` and snapshots a single Shopify record. Outreach attempts already contain immutable `offerSnapshot` JSON and bill by attempted proactive outreach.

## Scope

Change Background policy reader and candidate resolver to use mapped provider-neutral discount rows, merchant versus admin override source, and selected Woo discount sets. Keep Shopify single-discount compatibility and the existing outreach attempt identity and sequence.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

NONE returns no offer. Woo FIXED enumerates only same-Shop selected IDs, removes unavailable/currently invalid candidates without modifying persisted preference. Woo AI enumerates only current supported shop catalogue. Return bounded candidates for deterministic evaluation; do not claim chosen coupon or send WhatsApp until BACKGROUND-003 send-time proof. Admin override takes precedence, follow-up rules preserved and no additional recovery credit consumed by merely evaluating candidate sets.

## Work Items

- [ ] Resolve provider-aware effective policy and configured merchant selection.
- [ ] Build bounded FIXED/AI candidate collection and fail-closed outcomes.
- [ ] Preserve existing Shopify and follow-up attempt snapshots.
- [ ] Add cross-shop/revoked catalogue/admin override unit tests.

## Interfaces / Contracts

Existing policy service and `RecoveryOutreachAttempt.offerSnapshot`; provider-neutral DB and Shared v1 policy/evidence DTO.

## Dependencies

- `ARCH-036-DATABASE-002`
- `ARCH-036-SHARED-003`
- `ARCH-036-BACKGROUND-001`

## Enables

- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] NONE never yields candidate; FIXED only merchant/admin approved IDs; AI never includes unsupported/unavailable provider rows.
- [ ] Shopify single-discount behaviour preserved.
- [ ] No new sends, billing/attempt duplication or private provider API calls.
- [ ] Stale/current generation checks and same-Shop enforcement are tested.

## Validation

- [ ] Background policy and outreach-attempt focused unit tests
- [ ] Disposable PostgreSQL shop-scoped policy/override/generation tests
- [ ] Background typecheck/build and `git diff --check`

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
