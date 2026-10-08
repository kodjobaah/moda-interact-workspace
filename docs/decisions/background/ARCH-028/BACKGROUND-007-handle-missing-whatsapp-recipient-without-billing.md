---
id: ARCH-028-BACKGROUND-007
architecture_id: ARCH-028
title: Require current WhatsApp recipient before recovery materialisation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-028-BACKGROUND-005
  - ARCH-028-BACKGROUND-012
created: 2026-10-07
updated: 2026-10-08
---

# Require current WhatsApp recipient before recovery materialisation

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Require a canonical, Shop-scoped current `CustomerPhone` before materialising a `CheckoutRecovery`; when the number is missing, finish the candidate with no recovery, billing or Meta work. Ensure the resolved recipient passed to the initial send is the same one that passed this prerequisite. Checkout-update re-entry is a separate task (BACKGROUND-012).

## Context

The current recovery initiator creates `CheckoutRecovery` before recipient resolution and then throws when no customer phone/test recipient exists. `PendingRecoveryCandidate` already represents a checkout that may later become recoverable, so a missing phone should stop materialisation before a durable recovery exists. No DATABASE-003 required-recipient field, provider status or compensation contract is needed for this prerequisite.

The fresh abandoned-checkout lookup may contain a phone that Customer resolution persists through `CustomerPhoneService`; otherwise an already-current Shop-scoped `CustomerPhone` may still exist. Only the absence of an active usable `CustomerPhone` after that resolution is a true missing-recipient outcome. `Customer.phone` is not authoritative.

## Scope

- At matured-candidate materialisation, use the fresh abandoned-checkout snapshot to resolve/update the Shop-scoped Customer and `CustomerPhone` history before deciding recipient availability.
- If no active usable current `CustomerPhone` exists, return a bounded `no-recipient`/deferred outcome **without creating `CheckoutRecovery`**, `RecoveryOutreachAttempt`, UsageReservation/UsageEvent, outbound message or provider call.
- Preserve the normal matured-candidate cleanup; do not keep a fake blocked recovery solely as a waiting record.
- Pass the same canonical digits-only `CustomerPhone` recipient into the initial recovery-send path; it must not silently fall back to stale `Customer.phone`, checkout customer fields or a non-test WhatsApp recipient override.
- If a current `CustomerPhone` exists even when `Customer.phone` is null/stale, treat the recipient as present and continue with the existing admission path. BACKGROUND-005 will separately enforce durable per-attempt recipient snapshots once DATABASE-003 is integrated.
- Do not add aggressive polling solely for missing phone.

## Out of Scope

- Later `CHECKOUTS_UPDATE` re-entry, its Shared/Shopify producer/Background consumer contracts (BACKGROUND-012, SHARED-003/004, SHOPIFY-001).
- Recipient suppression TTL and mandatory attempt-recipient schema adoption.
- Provider error classification.
- Synchronous failure.
- Merchant notification.

## Requirements

- [ ] Missing recipient is zero billing and zero provider work.
- [ ] It is not persisted as a permanent Customer property.
- [ ] A later usable phone is eligible when another valid candidate is evaluated; this task does not manufacture a retry event.
- [ ] Test-only recipient behaviour remains explicitly development/test scoped and must not become production identity state.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Move the missing-recipient decision to the pending-candidate materialisation boundary before `CheckoutRecovery` creation.
- [ ] Resolve/update Customer + current `CustomerPhone` from the fresh checkout snapshot and use current `CustomerPhone` as the authoritative source.
- [ ] Return a bounded deferred/no-recipient result without recovery/attempt/billing/provider state.
- [ ] Ensure initial provider send receives exactly the canonical recipient validated at materialisation, not a stale original webhook/customer field.
- [ ] Ensure a null/stale `Customer.phone` does not block when an active `CustomerPhone` exists.
- [ ] Add focused tests.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes existing Customer/CustomerPhone resolution and pending-candidate materialisation services. Provides a bounded canonical recipient prerequisite for BACKGROUND-005 and BACKGROUND-012. No new database enum/state or required attempt-recipient field is introduced here.

## Dependencies

None.

## Enables

- `ARCH-028-BACKGROUND-005`
- `ARCH-028-BACKGROUND-012`

## Acceptance Criteria

- [ ] Missing recipient produces no `CheckoutRecovery`, outreach attempt, billing reservation, outbound UsageEvent/message or Meta call.
- [ ] Existing current `CustomerPhone` is honored even when `Customer.phone` is null/stale.
- [ ] The exact validated current `CustomerPhone` recipient is supplied to the initial Meta send; production cannot silently substitute `TEST_WHATSAPP_RECIPIENT` or a stale snapshot.
- [ ] Duplicate candidate execution remains idempotent and current non-missing recipients retain existing recovery behaviour.
- [ ] No polling loop or durable no-recipient recovery block is introduced.
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused recovery-initiation tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not conflate missing recipient with `WHATSAPP_RECIPIENT_SUPPRESSED`. Suppression is a durable policy block on a known recipient and may remain on a materialised recovery; missing recipient means there is no executable recovery yet.

Prefer a bounded candidate-materialisation recipient prerequisite and reuse existing Customer/CustomerPhone services. Keep `recovery-initiation.service.ts` thin; the separate BACKGROUND-012 task handles checkout-update re-entry after the Shared contract and producer/consumer rollout are defined.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

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
