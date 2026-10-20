---
id: ARCH-046-BACKGROUND-003
architecture_id: ARCH-046
title: Re-evaluate Woo checkout after later customer-phone grant
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

# Re-evaluate Woo checkout after later customer-phone grant

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

On Woo customer-phone consent change, safely re-evaluate linked **currently eligible abandoned checkouts** and create a **first** recovery only when permission is current and the separately approved Woo engine confirms checkout state.

## Context

The old design resumed a consent-blocked `DETECTED` recovery and expired it 72 hours later. Under the corrected model **no recovery exists** while consent is absent. A change receipt is a wakeup hint, not consent or checkout authority. ARCH-035 capture-only cannot supply this functionality; task remains BLOCKED.

## Scope

- Consume the minimal DATABASE-001 evidence/change receipt with bounded claim/lease, retry, terminal ack and pre-recovery no-op drainage; do not accumulate an unbounded pending outbox while Woo recovery runtime is disabled. Re-read current `CustomerPhone` + merchant source/epoch through BACKGROUND-001; never trust the receipt as current permission.
- Resolve still-addressable checkout(s) linked to the **verified customer ID and current phone** by the separately approved live Woo checkout-state/capture relation; checkoutKey from evidence is context, **not** a new current-consent projection. For guests prove legitimate session link; never search by phone alone.
- On current valid grant: under existing checkout-scoped lock and normal abandonment/maturity/payment/expiry/entitlement/suppression checks, materialise a **first** recovery exactly once, then existing normal billable/provider admission. On REVOKE or source/provider/epoch change, prevent new proactive sends and leave missing-consent checkouts without recovery rows.
- If checkout was paid, expired, not retrievable or not safely correlated, no-op; do not revive a terminal checkout/recovery, introduce a 72-hour consent wait, create a waiting recovery or poll every guest/cart indefinitely. If existing checkout references cannot support the promised wakeup, return gap to architect.

## Out of Scope

- No new Woo recovery engine, cross-shop/phone-only correlation, consent-specific status/expiry job, new queue contract or permanent wait table.

## Requirements

- **Execution gate:** requires architect-accepted independent Woo recovery and authoritative checkout-state reader; do not promote based on ARCH-035 capture-only completion.
- [ ] A grant/change receipt cannot authorise a send without **current** customer-phone consent and valid checkout.
- [ ] Consent itself never expires at 72 hours; normal checkout validity controls recoverability.
- [ ] Reprocessing and ordered grants/withdrawals never duplicate a new recovery or credit.

## Work Items

- [ ] Record approved Woo recovery-state dependency then implement bounded evidence wakeup and customer->checkout linkage.
- [ ] Re-enter normal pre-materialisation path on current consent, with checkout/order/phone rechecks.
- [ ] Test legitimate later grant and first creation, unlinked guest/no-op, completed checkout, duplicates, revoke/source change, DB outage and receipt cleanup.

## Interfaces / Contracts

Consumes DATABASE-001 minimal evidence receipt, API-001 writer, BACKGROUND-001 reader and BACKGROUND-002 pre-creation admission in approved Woo engine. No `WHATSAPP_CONSENT_MISSING` enum or same-generation recovery resume.

## Dependencies

- `ARCH-046-BACKGROUND-002`
- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-002`

## Enables

- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Later valid customer+phone grant with linked still-abandoned checkout -> **first recovery created once**, not an old blocked recovery resumed.
- [ ] Revoked/wrong identity/phone, unavailable/stale checkout, paid order, old epoch or provider mismatch -> no new recovery/send/credit.
- [ ] Bounded evidence delivery, duplicate processing and source-change cancellation do not create indefinite backlog or alter the customer's consent lifetime.

## Validation

- [ ] Disposable PostgreSQL evidence/outbox lease tests; approved Woo live checkout-state fixtures, actual Meta/credit side-effect assertions and `git diff --check`.

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

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline.

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
