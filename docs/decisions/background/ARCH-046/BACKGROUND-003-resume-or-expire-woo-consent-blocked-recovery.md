---
id: ARCH-046-BACKGROUND-003
architecture_id: ARCH-046
title: Wake, resume or expire Woo consent-blocked recoveries after later grant
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-BACKGROUND-002
  - ARCH-046-API-001
  - ARCH-046-WOOCOMMERCE-002
enables:
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Wake, resume or expire Woo consent-blocked recoveries after later grant

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

Process durable Woo consent-change receipts idempotently to resume an eligible existing recovery on later explicit opt-in, otherwise expire it without sending.

## Context

The Database consent outbox creates a durable wakeup, but current ARCH-035 capture-only processing is not authoritative for checkout/order status; this task remains BLOCKED until real Woo recovery engine approved.

## Scope

- Claim bounded pending consent change receipts with durable lease/ack/retry, not a global active-checkout scan or a new standalone Queue/Shared event contract.
- On GRANT, correlate blocked existing recovery by exact `(shopId, approved checkoutKey mapping, recipient)` and current recovery generation, then re-read latest **hosted source configuration plus consent**, reject former source/epoch, and revalidate live Woo checkout, order payment/completion, checkout expiry, entitlement, capacity, suppressions, original delay, human mode and latest outbound recipient.
- Resume the **same** recovery's existing sequence-one admission once if before fixed 72h deadline and independently approved checkout validity; never create another generation or reply by phone-only match.
- On REVOKE, NOT_CONFIGURED, unsupported provider, source switch or stale/older grant do not send. Schedule expiry and bounded repair of expired blocks; retain completion/retry idempotency and merchant-notice deduplication.

## Out of Scope

- No new engine/materialisation, no phone-based guest search, no global CMS subscription feature and no assumption BullMQ capture events reflect current order state.
- No Redis operation inside a PostgreSQL transaction or unbounded polling all pending checkouts.

## Requirements

- **Execution gate:** architect must define and accept the separate authoritative Woo live checkout-state and order fencing/recovery lifecycle before this task becomes Ready.
- A consent receipt only triggers re-evaluation; it does not itself authorise send. Revoke and duplicate/late events fail closed.
- Earliest of detectedAt+72h, known Woo cart/session expiry, paid/completed order and normal recovery terminal status wins.
- One initial attempt/credit/provider send at most; do not revive EXPIRED/COMPLETED/CANCELLED.

## Work Items

- [ ] Resolve/record external Woo recovery-engine dependency and checkoutKey mapping.
- [ ] Consume bounded DB outbox/lease and existing targeted resume under appropriate locks.
- [ ] Add deterministic expiry and repair, duplicate-event/out-of-order/cancel/charge tests.

## Interfaces / Contracts

Consumes DATABASE-001 durable change receipts (through Prisma), API-001 writer output, BACKGROUND-002 block and existing Woo recovery machine once separately approved. No new cross-service Shared event schema.

## Dependencies

- `ARCH-046-BACKGROUND-002`
- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-002`

## Enables

- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Later valid grant on same checkout+recipient resumes still-abandoned in-window recovery once.
- [ ] Missing/expired session, paid order, revoked/current mismatch, disabled source, changed mode/provider/epoch or old grant cannot trigger message.
- [ ] Durable change retries and expired-block repair converge without double credits/provider sends.
- [ ] No wakeup from a foreign shop/checkout or phone-only match.

## Validation

- [ ] Disposable PostgreSQL outbox lease concurrency and crash/retry test; approved live Woo state-reader fixtures.
- [ ] Black-box integration evidence for real queued event→resume→Meta/credit protections and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Do not make this task depend on ARCH-046-SYSTEM-TEST-001. System tests validate after implementation, never gate implementation.

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
