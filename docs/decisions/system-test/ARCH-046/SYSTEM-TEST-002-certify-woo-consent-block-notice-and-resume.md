---
id: ARCH-046-SYSTEM-TEST-002
architecture_id: ARCH-046
title: Certify Woo absent-consent notice and later-grant recovery end-to-end
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
  - ARCH-045-DATABASE-001
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

# Certify Woo absent-consent notice and later-grant recovery end-to-end

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

**System test is terminal:** No implementation task depends on this task. Execute only after its own implementation dependencies are accepted and the developer has an opportunity for manual LocalWP validation.

## Objective

Certify business-initiated Woo recovery is consent-gated and can safely resume on a later legitimate checkout opt-in, with merchant notice and zero charges when blocked.

## Context

This scenario requires a complete and separately approved Woo recovery/order state engine, which does not exist in the supplied capture-only snapshot. Therefore the system-test task is BLOCKED.

## Scope

- Run LocalWP shopper checkout/abandonment with complete approved Woo recovery materialisation; verify no consent→DETECTED block and exactly one merchant Support notice, no Meta send/credit.
- Later return to the same checkout and grant; verify authoritative checkout still abandoned and fresh exact consent, original recovery/generation resumes once; paid/completed/expired checkout never sends.
- Test revoke, wrong phone/checkout, merchant disconnect, **consent-source switch, unsupported external adapter and stale provider/epoch evidence**, duplicate/out-of-order events, DB outage, notice-write failure, worker race, expired repair, follow-ups and credit compensation.
- Check read-only Woo Support UI under `WooCommerce > Moda Interact` + nested `Support` and bounded redacted structured logs.

## Out of Scope

- No use of Shopify test identity for Woo consent, no simulated authorisation from a phone-only match or tracking cookie flag.
- No creation/implementation of missing Woo recovery engine inside system test.

## Requirements

- **Execution gate:** all dependencies architect-accepted Complete **plus** previously approved and verified Woo recovery lifecycle/live checkout-state reader and orders; developer manual validation completed before invocation.
- Black-box merchant/customer workflows and observable provider/billing outcomes, not a synthetic unit-only green test.
- Retain negative evidence and no production customer data.

## Work Items

- [ ] Verify external Woo recovery engine approval/readiness before claiming.
- [ ] Run no-consent merchant notification and later-consent eligible-resume cases.
- [ ] Run stale/paid/expired/duplicate/revoked/cross-shop/billing/follow-up negative cases and record evidence.

## Interfaces / Contracts

Uses API-001 write, API-002/WOOCOMMERCE-004 notices, DATABASE-001 consent, ARCH-045 generic admission reason, BACKGROUND-001..004 and separately approved Woo recovery runtime.

## Dependencies

- `ARCH-045-DATABASE-001`
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

- [ ] No consent: exactly one merchant notice and no provider sends, recovery credits or billable attempts.
- [ ] Later explicit grant: exact current recipient and checkout eligible→original recovery sent once; no duplicate charge.
- [ ] Paid/order-complete, expired, revoked/changed phone, unconfigured/source-switched/external-unapproved and stale/forged event never send.
- [ ] Woo admin UI reflects accurate system notice; no bypass; merchant isolation and 20 locale smoke checks verified.

## Validation

- [ ] Disposable LocalWP + hosted API/PostgreSQL/Redis/Background black-box log/evidence bundle.
- [ ] Failure/replay/race validation with real provider stub, credit ledger assertions and diff check.

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
