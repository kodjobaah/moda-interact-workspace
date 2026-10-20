---
id: ARCH-046-BACKGROUND-002
architecture_id: ARCH-046
title: Block unconsented Woo recovery and notify merchant once
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-001
  - ARCH-046-BACKGROUND-001
enables:
  - ARCH-046-BACKGROUND-003
  - ARCH-046-BACKGROUND-004
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Block unconsented Woo recovery and notify merchant once

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

When an approved Woo recovery action becomes eligible, retain DETECTED with a consent block and one merchant Support system notice instead of billing or sending.

## Context

The current ARCH-035 Woo worker is **capture-only**, not a recovery engine. This task is **BLOCKED** pending a separately agreed authoritative Woo checkout-state reader, materialisation, order-completion fencing and recovery admission architecture. ARCH-045 owns generic block enum.

## Scope

- At the approved Woo initial proactive admission boundary, check current exact consent with BACKGROUND-001 **before** sequence-one attempt/billing reservation/provider send.
- For absent or revoked consent, persist existing `DETECTED` recovery and `admissionBlockReason=WHATSAPP_CONSENT_MISSING` (from accepted ARCH-045-DATABASE-001); leave other block reasons and no-recipient cases distinct.
- Create exactly one idempotent `MerchantSupportMessage` SYSTEM in shop-unique thread using `sourceKey=arch046:consent-missing:<recoveryId>` and truthful expiry/no-credit copy; retry failed notice without allowing send.
- Enforce earliest valid expiry: immutable `detectedAt+72h` **or** earlier known Woo checkout terminal/expiry; do not invent Woo state from BullMQ retained events.

## Out of Scope

- No Woo recovery engine build, Shopify Checkout GraphQL calls, order-state inference, provider send path redesign or website consent UI.
- No merchant force-send/bypass, new notification channel or duplicate enum migration.

## Requirements

- **Execution gate:** cannot be claimed Ready until architect accepts a separate real Woo recovery lifecycle and current live checkout-state reader with a stable checkoutKey mapping; record the new fully qualified prerequisite before Ready transition.
- Check after true abandoned recovery determined; no recovery row/merchant notice from raw capture-only events.
- No sequence-one attempt, credit hold/commit or provider operation on absence of consent.
- Fail closed on verification outage without falsely calling a transient DB error a customer opt-out.

## Work Items

- [ ] Architect first resolves external Woo recovery lifecycle dependency and promotes task from Blocked.
- [ ] Integrate exact consent reader in real Woo initial admission only.
- [ ] Persist block/notice transactionally/idempotently and test no-charge under duplicate/race/failure.

## Interfaces / Contracts

Consumes ARCH-045-DATABASE-001 enum, BACKGROUND-001 reader and existing `MerchantSupportMessage` unique sourceKey. Requires externally approved Woo CheckoutRecovery lifecycle not present in current snapshot.

## Dependencies

- `ARCH-045-DATABASE-001`
- `ARCH-046-BACKGROUND-001`

## Enables

- `ARCH-046-BACKGROUND-003`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Missing consent -> DETECTED+specific block+one merchant notice and zero attempted provider sends/credit usage.
- [ ] Duplicate workers, failed notification and retried checkout events do not double-notify or accidentally send.
- [ ] Exact recipient with valid consent follows independently approved normal Woo recovery once; no Shopify codepath spoofing.
- [ ] External Woo checkout-state reader/engine approval and acceptance evidence are attached to Completion Report.

## Validation

- [ ] Focused Woo recovery-admission test plus disposable PostgreSQL notice/idempotency race test.
- [ ] Provider and billing spies prove no sends/charges; real approved Woo checkout-state fixture and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Do not execute from this snapshot. Source currently does not have the required Woo recovery engine. Marking this Ready solely because ARCH-045 enum/reader exist would violate ARCH-035 capture-only boundary.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None — no runtime implementation in this documentation patch.

### Work Completed

None.

### Validation Results

Not run by a repository agent; no developer worktree/remote access is available from this snapshot.

### Deviations

None.

### Assumptions

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Fixed provisional 72-hour consent wait from `detectedAt`, always shortened by actual earlier Woo checkout expiration/paid-order state.

### Unresolved Issues

External approved Woo recovery lifecycle/live checkout-state reader and independently accepted send/billing admission are currently missing; task remains Blocked.

### Architectural Concerns

None recorded beyond explicit context and gates.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
