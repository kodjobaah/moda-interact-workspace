---
id: ARCH-046-SYSTEM-TEST-002
architecture_id: ARCH-046
title: Certify Woo consent-gated first recovery creation and later opt-in
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-DATABASE-001
  - ARCH-046-API-001
  - ARCH-046-API-002
  - ARCH-046-API-003
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-WOOCOMMERCE-003
  - ARCH-046-WOOCOMMERCE-004
  - ARCH-046-WOOCOMMERCE-005
  - ARCH-046-BACKGROUND-001
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-003
  - ARCH-046-BACKGROUND-004
enables: []
created: 2026-10-20
updated: 2026-10-20
---

# Certify Woo consent-gated first recovery creation and later opt-in

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

**System test is terminal:** No implementation task depends on this task. Execute only after its own implementation dependencies are accepted and the developer has an opportunity for manual LocalWP validation.

## Objective

Once a separately approved Woo recovery engine is live, certify **no initial recovery without consent**, an idempotent checkout-based merchant notice and first recovery creation after later verified customer-phone opt-in.

## Context

ARCH-035 is currently capture-only and cannot prove abandoned Woo checkouts remain identifiable or unpaid. This system test remains **BLOCKED** until the authoritative checkout/order state and all required Background implementation tasks are architect-accepted Complete.

## Scope

- Exercise approved live Woo checkout evaluator with unconsented abandon: assert **zero CheckoutRecovery**, zero attempt/credit/provider send, exactly one Support notice derived from shop+checkout identity, and correct distinction between not configured, denied and verification unavailable.
- Later explicit current GRANT to same safely identified customer+phone: check normal checkout maturity, live unpaid/abandoned/expiry state and source epoch, then assert **one first CheckoutRecovery** and ordinary billable/provider result. Consent itself has no 72-hour timer; absence of a retrievable checkout yields no recovery.
- Exercise paid/expired/removed checkout, missing/guest session link, phone change, revoked source, duplicate events, notice failure, third-party mode/provider switch, partial DB failure, scheduled/human follow-ups, credit refund/release and redacted diagnostics.
- Confirm read-only Woo Support UI under existing navigation; do not fake availability of unknown Woo recovery methods.

## Out of Scope

- No Woo recovery engine implementation in the system-test repo, no Shopify consent reuse, no phone-only customer lookup.

## Requirements

- **Execution gate:** all platform, Woo live checkout/recovery and ARCH-046 implementation prerequisites must be completed and accepted, then developer manual verification before terminal system test.
- [ ] Durable provider/DB/billing evidence, tenant-specific keys and realistic failure injection.

## Work Items

- [ ] Reconfirm missing external recovery-engine task dependency before marking Ready.
- [ ] Run no-consent/no-row, later-consent/first-row and strict no-send/no-credit cases.
- [ ] Publish structured validation evidence and separate mock/provider contract proof from actual live Woo checkout testing.

## Interfaces / Contracts

ARCH-046-DATABASE-001, API-001/002/003, WOOCOMMERCE-002/003/004/005, BACKGROUND-001/002/003/004 and separately approved Woo recovery engine; **no ARCH-045-DATABASE-001**.

## Dependencies

- `ARCH-046-DATABASE-001`
- `ARCH-046-API-001`
- `ARCH-046-API-002`
- `ARCH-046-API-003`
- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-046-WOOCOMMERCE-004`
- `ARCH-046-WOOCOMMERCE-005`
- `ARCH-046-BACKGROUND-001`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-003`
- `ARCH-046-BACKGROUND-004`

## Enables

None

## Acceptance Criteria

- [ ] Missing consent -> **zero** initial recovery and charge, with checkout-keyed merchant notice.
- [ ] Later consent + safe still-abandoned checkout -> exactly one newly created recovery and correct usage charge.
- [ ] Invalid/expired/completed checkout, changed number/provider/source or withdrawn consent -> no outbound sends; no invented consent expiry.
- [ ] Read-only Woo Support and follow-ups function without consent bypass or duplicate messages.

## Validation

- [ ] Real LocalWP Woo integrated checkout/order state and provider-admission/billing system tests after engine approval; `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Terminal full-architecture system test; no non-system-test task may depend on it. The architect must keep ARCH-046 Proposed/In Progress, **not** Implemented, until all required implementation and this test are accepted.

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
