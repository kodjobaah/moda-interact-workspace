---
id: ARCH-035-SYSTEM-TEST-007
architecture_id: ARCH-035
title: Certify real WooCommerce current and past usage history
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-022
  - ARCH-035-WOOCOMMERCE-018
enables: []
created: 2026-10-22
updated: 2026-10-22
---
# ARCH-035-SYSTEM-TEST-007: Certify real WooCommerce current and past usage history

## Architecture

Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.

## Objective

Independently prove that WooCommerce Usage History retrieves real, correct tenant-owned usage and entitlement periods through the deployed plugin and hosted API.

## Context

`SYSTEM-TEST-001` covers UI-only parity, while this task certifies live data and provider-correct usage. Billing Purchase History remains separate.

## Scope

Black-box authenticated Woo WP admin → hosted usage-history route → actual usage/period records, with separate Free lifetime and paid entitlement test cases; validate filtering, totals, period cursor, event paging, correction and same-Shop links.

## Out of Scope

Writing new usage events as a product feature, PSP charging, changing credit metering, backend implementation, customer recovery execution, `_index.md` changes.

## Requirements

- Use isolated seeded actual `UsageEvent`, `BillingPeriod` and recovery records for two shops and real Free/paid subscription configurations.
- Validate paid current 30-day entitlement and historical closed periods separately from payment-provider billing months; prove Free lifetime works without synthetic BillingPeriod.
- Validate `ALL`/`RECOVERY_CONVERSATION`, page sizes 10/25/50/100, sort tie cases, totals, 25-period cursors, invalid cursor/foreign period, corrections/compensations and no cross-Shop customer names/recovery links.
- Confirm WP nonce/capability denial, disconnected/revoked credentials, hosted outage, stale page change and true empty state.
- Check Billing Purchase History and Shopify usage regressions remain unchanged.

## Work Items

- [ ] Define reproducible fixtures/executors/assertions and separate provider/entitlement cases.
- [ ] Exercise real Woo admin page and hosted endpoint for current/past/Free/correction cases.
- [ ] Exercise paging, denied/tampered/foreign-store and disconnect/outage cases.
- [ ] Record DB/API/UI consistency and precise evidence paths for architect review.

## Interfaces / Contracts

API-022 GET usage-history; WOO-018 WordPress same-origin proxy and React view. DB is observed by test infrastructure only.

## Dependencies

- `ARCH-035-API-022` Complete.
- `ARCH-035-WOOCOMMERCE-018` Complete.

## Enables

None; terminal functional certification.

## Acceptance Criteria

- [ ] Real usage events, entitled periods, Free lifetime and compensation totals match source records and visible table.
- [ ] Cross-Shop, invalid cursor/period, permission, reconnect and outage cases demonstrably fail closed.
- [ ] No success is claimed on the strength of unavailable-state UI fixtures alone.

## Validation

- [ ] Isolated black-box WordPress/hosted/DB test evidence; deterministic fixture cleanup.
- [ ] `git diff --check`, launcher worktree evidence, Completion Report and reviewer reproducibility.

## Stop Condition

Set `status: review`, return to architect and STOP; certification does not implement new features.

## Implementation Notes

Test API/UI/source independently; make result evidence distinguish Free, paid and historical; keep tests modular and tenant-scoped.

## Completion Report

### Status

Not Started — portable definition, not claimed or materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No Git worktree, branch, implementation commit, provider credentials, deployment or acceptance is created by this task definition.

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
