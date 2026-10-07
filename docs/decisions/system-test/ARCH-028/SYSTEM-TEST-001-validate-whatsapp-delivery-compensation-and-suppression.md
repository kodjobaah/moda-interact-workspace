---
id: ARCH-028-SYSTEM-TEST-001
architecture_id: ARCH-028
title: Validate WhatsApp delivery compensation and recipient suppression
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-ADMIN-001
  - ARCH-028-BACKGROUND-007
  - ARCH-028-BACKGROUND-009
enables: []
created: 2026-10-07
updated: 2026-10-07
---

# Validate WhatsApp delivery compensation and recipient suppression

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Validate the integrated ARCH-028 async/sync terminal WhatsApp failure, exact recovery compensation, outbound hard-limit correction, Shop-scoped suppression, missing-recipient and merchant-notification behaviour across supported recovery capacity sources.

## Context

This is terminal system validation. It executes only after every required implementation dependency is Complete/architect-accepted. Developer manual testing may occur before invocation; no implementation task depends on this task.

## Scope

At minimum validate:

1. FAILED/131026 async status resolves exact message/attempt/recovery/Shop without phone-to-Shop lookup.
2. FAILED -> late SENT is ignored; FAILED -> DELIVERED/READ is allowed as positive evidence.
3. NO_RESPONSE race still compensates the exact recovery.
4. Provider-status replay retries compensation even when message is already FAILED and cannot double-correct.
5. RESERVED release and COMMITTED lifetime-Free/paid-included/promotional correction.
6. Committed purchased source follows ARCH-027 purchase/refund states through BACKGROUND-009.
7. Terminally undelivered automated message does not consume outbound hard limit.
8. Reachability `(shopId, recipient)` suppresses pre-admission billing/provider work for default seven days.
9. Admin policy change affects newly computed suppression duration.
10. Same phone under two Shops remains isolated.
11. DELIVERED/READ and safely Shop-routed inbound evidence clear active suppression.
12. Suppression expiry permits eligibility again; it is not permanent identity state.
13. Different/new recipient is independently eligible.
14. Synchronous `131026` follows async terminal policy; other synchronous provider errors do not.
15. A matured candidate with no active usable current `CustomerPhone` creates no `CheckoutRecovery`/attempt/billing/provider work; a later `CHECKOUTS_UPDATE` can schedule a fresh candidate and proceed once a usable phone exists.
16. Null/stale `Customer.phone` does not produce a false missing-recipient result when an active Shop-scoped `CustomerPhone` exists.
16. Merchant SYSTEM notification appears once and only after correction/suppression success; wording matches compensation disposition.

## Out of Scope

- New implementation fixes inside system-test task.
- Provider-code policy beyond `131026`.
- Meta production certification beyond available integration fixture/provider test boundary unless explicitly configured by the developer.

## Requirements

- [ ] Tests use architecture-owned fixtures/evidence and tenant-isolated Shops.
- [ ] Evidence identifies actual durable rows/counters/UsageEvents/messages, not only HTTP/queue success.
- [ ] No scenario relies on a universal Customer/phone identity.
- [ ] Failures are routed to owning implementation task; do not patch repositories from system-test ownership.

## Work Items

- [ ] Build deterministic async status fixtures including duplicate/out-of-order delivery.
- [ ] Build pending-candidate fixtures for no-current-phone, later `CHECKOUTS_UPDATE` with phone, and stale/null `Customer.phone` with valid current `CustomerPhone`.
- [ ] Build synchronous provider rejection fixture.
- [ ] Seed two Shops with same canonical recipient.
- [ ] Validate each capacity source/disposition including purchased ARCH-027 states.
- [ ] Validate Admin-configured suppression duration/default.
- [ ] Validate hard-limit and merchant notification ordering/dedup.
- [ ] Produce architecture-level evidence report.

## Interfaces / Contracts

Consumes completed ARCH-028 and ARCH-027 implementation state only.

## Dependencies

- `ARCH-028-ADMIN-001`
- `ARCH-028-BACKGROUND-007`
- `ARCH-028-BACKGROUND-009`

These terminal dependencies transitively require all ARCH-028 Shared, Messaging, Database and Background implementation tasks plus `ARCH-027-BACKGROUND-005`.

## Enables

None.

## Acceptance Criteria

- [ ] Every scoped scenario passes with durable database/accounting evidence.
- [ ] Duplicate/out-of-order provider statuses are idempotent.
- [ ] Cross-Shop same-number suppression isolation is proven.
- [ ] No terminally undelivered recovery ultimately consumes recovery capacity or outbound hard-limit usage contrary to its disposition.
- [ ] No merchant notification precedes durable correction.
- [ ] Missing-recipient candidate materialisation creates no `CheckoutRecovery` or prohibited billing/provider work, and later checkout update/current-phone evidence can materialise normally.
- [ ] A current `CustomerPhone` remains authoritative even when `Customer.phone` is null/stale.

## Validation

Run the system-test repository's declared focused/integrated commands and record environment/fixture evidence. Do not invent green live-provider evidence if unavailable.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

This is architecture-level validation, not a repository implementation task. A failure identifies the owning ARCH-028 task for correction.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
