---
id: ARCH-035-SYSTEM-TEST-006
architecture_id: ARCH-035
title: Certify live WooCommerce Promotions selection and history
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-021
  - ARCH-035-WOOCOMMERCE-017
enables: []
created: 2026-10-22
updated: 2026-10-22
---
# ARCH-035-SYSTEM-TEST-006: Certify live WooCommerce Promotions selection and history

## Architecture

Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.

## Objective

Independently demonstrate real WooCommerce merchant Promotions reads, selection and history end to end against the hosted API and authoritative billing records.

## Context

`SYSTEM-TEST-001` certifies UI-only parity; it does not prove promotional-credit selection works. This test is terminal and is intentionally separate from Support and Usage History certification.

## Scope

Black-box Woo WP merchant → authenticated hosted API → real campaign/grant/selection records. Use disposable or approved test Shop fixtures and repeatable browser/API observations. Validate offers, eligibility, pagination, selection, history, locked state, tenant isolation, retry safety and Shopify regression.

## Out of Scope

New production code, credit campaign authoring features, Woo coupon discount selection, system-test-first execution, `_index.md` changes.

## Requirements

- Seed two Woo shops with distinct plan scopes and campaigns (active, expired, closed, Shop-only, Plan-only, exhausted) and real grant reservations/consumption; independently inspect durable records before/after.
- Prove GET and PUT through real WordPress nonce/capability installation boundary; verify selection once under duplicate/concurrent requests and stale revision.
- Prove second Shop cannot see/select foreign Shop promotion; confirm merchant locale fallback, correct credit balances and history paging.
- Verify disconnect/revoke, API outage/5xx, denied permission and stale client responses do not display fabricated successful selection.
- Confirm existing Shopify selection and billing remain unchanged.

## Work Items

- [ ] Define isolated fixtures, executors, assertions and evidence paths.
- [ ] Validate reads/history and first successful selection.
- [ ] Validate duplicate/stale/conflicting selections with DB-grant invariant.
- [ ] Validate cross-shop and denied/outage states plus Shopify regression.
- [ ] Publish reproducible consolidated system-test evidence.

## Interfaces / Contracts

API-021 hosted response/command; WOO-017 privileged WordPress proxy. DB inspection is system-test-only evidence, not production Woo direct DB access.

## Dependencies

- `ARCH-035-API-021` Complete.
- `ARCH-035-WOOCOMMERCE-017` Complete.

## Enables

None; terminal functional certification.

## Acceptance Criteria

- [ ] Real persistence and real UI agree; selection grants exactly once; balances/reservations are stable across retry/concurrency.
- [ ] Tenant, nonce, plan, locale, outage and locked/expired tests have grounded results and artifact paths.
- [ ] No assertion of functional parity rests on fixture-only React component data.

## Validation

- [ ] Real black-box hosted/WP integration tests against isolated state with preserved fixtures/logs and rollback/cleanup.
- [ ] `git diff --check`, canonical task isolation and Completion Report with pass/fail/blocked evidence.

## Stop Condition

Submit results with `status: review` to architect and STOP; do not mark ARCH-035 Implemented.

## Implementation Notes

Split executors/fixtures/assertions/orchestration, avoid oversized catch-all test files and never infer provider availability from mocks.

## Completion Report

### Status

Dependency-ready and manual-gated — `ARCH-035-API-021` and `ARCH-035-WOOCOMMERCE-017` are Complete. The WooCommerce implementation task was explicitly completed at Attempt 2 and its completion record was published on parent task branch commit `49a77c1d`; no task branches were merged to `main`. This system-test task remains unclaimed at Attempt 0. Promotion to `ready` does not authorize execution; the developer must explicitly invoke this terminal system-test task.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The canonical parent task worktree and `task/ARCH-035-SYSTEM-TEST-006` branch are materialized for dependency-frontier reconciliation. The implementation task worktree remains uncreated; no system-test claim, provider credentials, deployment or acceptance is implied.

### Unresolved Issues

None recorded at definition time; report concrete schema/contract gaps to the architect rather than broadening scope.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed. This is a new task definition, not an accepted implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed from implementation and test evidence.

### Follow-up

Architect acceptance required before enabling dependants.
