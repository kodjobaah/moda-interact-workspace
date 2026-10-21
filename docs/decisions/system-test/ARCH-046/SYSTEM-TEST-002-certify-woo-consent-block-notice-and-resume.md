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
  - ARCH-045-DATABASE-002
  - ARCH-046-API-001
  - ARCH-046-API-002
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-WOOCOMMERCE-003
  - ARCH-046-WOOCOMMERCE-004
  - ARCH-046-BACKGROUND-001
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-045-SHARED-002
  - ARCH-045-BACKGROUND-005
  - ARCH-046-API-005
  - ARCH-046-WOOCOMMERCE-007
enables: []
created: 2026-10-20
updated: 2026-10-21
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

When a separately approved live Woo recovery engine exists, certify that no recovery is created without current customer-phone consent and that a **later normal checkout reconciliation** can create a first recovery after a grant.

## Context

ARCH-035 is currently capture-only and cannot prove abandoned Woo checkouts remain identifiable or unpaid. This system test remains **BLOCKED** until the authoritative checkout/order state and all required Background implementation tasks are architect-accepted Complete.

## Scope

- With the approved Woo live checkout/order reader and recovery engine, exercise an unconsented abandoned checkout: zero CheckoutRecovery/attempt/credit/Meta send and one checkout-keyed merchant Support SYSTEM notice, distinguishing disabled consent collection, not authorised and temporary verification unavailable.
- Submit later verified grant for exact same shop/customer/phone: assert CustomerPhone and immutable `commerce.WhatsAppConsentEvidence` update **but no immediate recovery, candidate job, credit or notice**. Next deliver an actual ordinary Woo checkout update/reconciliation for the still-abandoned, unpaid and otherwise eligible checkout: assert **one first recovery** with correct provider/billing idempotency.
- Test **no further checkout event -> no guaranteed recovery**, completed/expired/removed checkout, ambiguous within-shop or cross-tenant canonical-phone match, phone/installation change, revoke before send, duplicate ordinary checkout event, merchant Support read UI, scheduled/human follow-up and credit compensation.
- Verify no evidence claim/ack processing columns or polling jobs, no 72-hour consent deadline and no reliance on ARCH-046-BACKGROUND-003 (superseded).

- **Release gate:** Do not run against ARCH-035 capture-only stub. First obtain separately approved live Woo reconciliation reader/engine and checkout/order status tests; ensure implementation dependency actually exists rather than treating consent capture as a recovery engine.
- Include first creation before insert, existing DETECTED first-send reentry, capacity/suppression resume, authenticated merchant plus exact canonical-phone lookup, E.164 recipient, local STOP, merchant-recorded opt-out, installation deactivation, paid checkout, delivery/compensation and no consent-triggered wakeup.
- Verify merchant suppression, customer STOP and that a stale grant/retry cannot resurrect proactive outreach; validate shop-scoped Support notice dedupe/volume.

## Out of Scope

- No Woo recovery engine implementation in the system-test repo, no Shopify consent reuse, no cross-shop phone match or permission granted by lookup alone.

## Requirements

- **Execution gate:** all platform, Woo live checkout/recovery and ARCH-046 implementation prerequisites must be completed and accepted, then developer manual verification before terminal system test.
- [ ] Durable provider/DB/billing evidence, tenant-specific keys and realistic failure injection.

## Work Items

- [ ] Reconfirm missing external recovery-engine task dependency before marking Ready.
- [ ] Run no-consent/no-row, later-consent/first-row and strict no-send/no-credit cases.
- [ ] Publish structured validation evidence and separate mock/provider contract proof from actual live Woo checkout testing.

## Interfaces / Contracts

Consolidated ARCH-045-DATABASE-002, API-001/002, WOOCOMMERCE-001/002/003/004, BACKGROUND-001/002/004 and separately architect-accepted Woo recovery engine. No ARCH-046-BACKGROUND-003 dependency or evidence worklist.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-046-API-001`
- `ARCH-046-API-002`
- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-046-WOOCOMMERCE-004`
- `ARCH-046-BACKGROUND-001`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-045-SHARED-002`
- `ARCH-045-BACKGROUND-005`
- `ARCH-046-API-005`
- `ARCH-046-WOOCOMMERCE-007`

## Enables

None

## Acceptance Criteria

- [ ] No consent -> no initial recovery/charge/send; one correct checkout-keyed merchant notice.
- [ ] Later grant alone only changes CustomerPhone/evidence; **next actual ordinary checkout reconciliation** can create one recovery if valid.
- [ ] Without subsequent event, no guaranteed revisit; paid/expired/removed/foreign checkout or revoked/installation-invalid grant causes no provider send.
- [ ] No polling immutable evidence/worklist, consent-specific queue, arbitrary 72-hour consent timer or duplicate billing.

- [ ] No live recovery claim without actual approved Woo recovery engine; when approved, all proactive send entry points recheck current consent and no-contact at a short transaction fence with no committed credit on refusal.

## Validation

- [ ] Real approved Woo recovery engine + LocalWP/API/PostgreSQL/Meta controlled system tests with event-timing assertions, idempotency, Support, credit and redacted diagnostics; `git diff --check`.

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
