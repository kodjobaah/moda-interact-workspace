---
id: ARCH-028-BACKGROUND-005
architecture_id: ARCH-028
title: Apply Shop-scoped WhatsApp recipient reachability gate
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-DATABASE-003
enables:
  - ARCH-028-BACKGROUND-007
created: 2026-10-07
updated: 2026-10-07
---

# Apply Shop-scoped WhatsApp recipient reachability gate

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Persist terminal-recipient suppression only after successful recovery correction, use it as a zero-billing pre-admission gate for later recoveries, and clear suppression from positive Shop-scoped WhatsApp evidence.

## Context

The exact Shop/recovery for provider failure is already known through durable message/attempt/recovery relations. The attempt's required `recipient` snapshot identifies the failed destination. Reachability must never infer Shop from phone alone.

`PlatformBillingPolicy.whatsappRecipientSuppressionDays` supplies the finite duration (default seven days).

## Scope

- Canonicalize recovery recipients using one Background-owned function: trim, remove non-decimal digits, require at least one digit, store digits only.
- Reorder initial/follow-up recovery admission so recipient is resolved/canonicalized and persisted on `RecoveryOutreachAttempt` before billing/provider send.
- After successful generic/purchased correction outcome, upsert `(shopId, attempt.recipient)` reachability failure evidence and `suppressUntil = failureAt + configured days`.
- Before recovery billing admission, check active reachability; when suppressed, perform zero billing/zero provider call and set `WHATSAPP_RECIPIENT_SUPPRESSED`.
- Use existing bounded Background resume machinery where practical to re-evaluate a DETECTED blocked recovery at/after `suppressUntil` if still valid; do not keep suppressing solely from expired historical evidence.
- Clear active suppression on DELIVERED/READ for the same Shop/attempt recipient.
- Clear active suppression on inbound WhatsApp only after normal routing has established one Shop/conversation/customer owner; ambiguous contextless phone must not clear multiple Shops.
- A new/different current phone is a different recipient and is independently eligible.

## Out of Scope

- Admin UI (ADMIN-001).
- Synchronous provider rejection path (BACKGROUND-006).
- Missing-phone path (BACKGROUND-007).
- Merchant notification (BACKGROUND-008).
- Global phone blacklist or Customer.hasWhatsApp.

## Requirements

- [ ] Suppression is keyed exactly by `(shopId, recipient)`.
- [ ] Same phone in Shop A never suppresses Shop B.
- [ ] Reachability failure is recorded only after required correction/release succeeds; deferred committed-purchased compensation does not yet claim success.
- [ ] Active suppression gates before recovery billing and outbound admission.
- [ ] Suppression expiry stops blocking automatically; positive evidence clears earlier.
- [ ] Recipient snapshot is per outreach attempt and immutable after provider-directed work begins.
- [ ] Provider delivery status never resolves tenant ownership through phone lookup.

## Work Items

- [ ] Add canonical recipient helper and attempt-recipient persistence in initial/follow-up paths.
- [ ] Read platform suppression-day policy.
- [ ] Add reachability failure upsert after successful terminal correction.
- [ ] Add pre-admission suppression lookup/block.
- [ ] Add bounded expiry resume/re-evaluation for eligible DETECTED blocked recoveries.
- [ ] Add DELIVERED/READ positive clearing.
- [ ] Add resolved inbound positive clearing without ambiguous cross-Shop clearing.
- [ ] Add multi-Shop same-number tests.

## Interfaces / Contracts

Consumes DATABASE-001 reachability/policy/block-reason persistence, DATABASE-003 required outreach recipient, and BACKGROUND-004 bounded compensation outcomes.

## Dependencies

- `ARCH-028-BACKGROUND-004`
- `ARCH-028-DATABASE-003`

## Enables

- `ARCH-028-BACKGROUND-007`

## Acceptance Criteria

- [ ] Suppressed recipient reaches no recovery billing admission/provider call.
- [ ] Default policy produces a seven-day `suppressUntil` when Admin has not changed it.
- [ ] Expired suppression is not treated as permanent failure.
- [ ] DELIVERED/READ or safely Shop-resolved inbound evidence clears active suppression.
- [ ] A different phone is immediately evaluated independently.
- [ ] Two Shops sharing the same phone remain isolated.
- [ ] Deferred/uncompensated purchased failure does not emit false restored/suppressed completion side effects.

## Validation

Focused recovery-initiation/follow-up/provider-status/inbound-routing/reachability tests, PostgreSQL integration for concurrent upsert/version behaviour where required, full Background test/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Reuse existing recovery-resume queue/mechanics rather than adding a new service deployment. Do not log full recipient values.

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
