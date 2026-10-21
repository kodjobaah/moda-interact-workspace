---
id: ARCH-046-BACKGROUND-002
architecture_id: ARCH-046
title: Skip unconsented Woo recovery creation and notify merchant
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
  - ARCH-046-BACKGROUND-001
enables:
  - ARCH-046-BACKGROUND-004
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-21
---

# Skip unconsented Woo recovery creation and notify merchant

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

When a separately approved Woo checkout recovery engine performs **ordinary** checkout reconciliation, check current `CustomerPhone` consent before any first `CheckoutRecovery` and notify the merchant if no valid opt-in exists.

## Context

ARCH-035 is capture-only. This task stays **Blocked** until a separate actual Woo checkout state reader/materialisation and billing contract are architect-accepted. ARCH-046-BACKGROUND-001 already supplies current phone/installation policy; consent events themselves do not initiate reconciliation.

## Scope

- Inject BACKGROUND-001 consent reader into the future approved normal Woo checkout evaluation before first recovery write/usage admission. Independently verify current unpaid/abandoned checkout, shop/customer/phone, source epoch, maturity and merchant entitlement.
- When consent is absent, revoked, wrong phone/source or unavailable, create no recovery, attempt, provider send or committed credit. Insert one existing checkout-keyed MerchantSupportMessage SYSTEM notice without fabricating recoveryId, distinguish customer permission from merchant NOT_CONFIGURED and transient failure.
- If a later ordinary Woo checkout update/reconciliation actually runs after a new grant, the same gate can permit **first** recovery creation if checkout is still eligible. A consent grant alone never schedules or polls for that checkout; no new retention mechanism or waiting recovery.
- Preserve authorised recovery idempotency, provider/billing compensation, suppression and checkout locks.

## Out of Scope

- No implementation of the missing Woo recovery engine/state reader, consent-expiry timer, recovery block enum, `DETECTED` waiting row, custom notice table or merchant force-send.

## Requirements

- [ ] This task remains blocked until approved Woo recovery engine/checkout-state reader exists; no feature enablement from consent capture alone.
- [ ] No consent means no CheckoutRecovery/credit/message; later opt-in requires actual normal reconciliation.
- [ ] No evidence claim/ack processing, consent wakeup, 72-hour timer or recovery admission enum.

## Work Items

- [ ] Integrate reader at approved normal checkout-to-recovery materialisation seam only after architecture gate.
- [ ] Implement checkout-keyed merchant notice via existing Support schema.
- [ ] Test no grant/no recovery, later grant + real normal checkout event vs no event, paid/expired cart, source epoch, notice deduplication and credits.

## Interfaces / Contracts

Consumes ARCH-046-BACKGROUND-001 current phone-source consent and a **separately approved** Woo recovery engine. Existing Support system notice keyed to shop+checkout, existing credit/billing semantics. Does not consume ARCH-046-BACKGROUND-003 or audit evidence worklist.

## Dependencies

- `ARCH-046-BACKGROUND-001`

## Enables

- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Initial invalid consent creates no recovery, provider send or charge; merchant notice is idempotent and truthful.
- [ ] Later valid phone grant alone does nothing; a real normal checkout reconciliation event can create first recovery under all business gates.
- [ ] No new queue, evidence polling or consent-specific checkout hold; approval gate observed.

## Validation

- [ ] Once approved engine available, focused live Woo checkout/candidate, Support notice, billing/Meta, source epoch and no-event/next-event tests, `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Do not execute from this snapshot. Source currently does not have the required Woo recovery engine. Marking this Ready merely because ARCH-045-DATABASE-002 or ARCH-046-BACKGROUND-001 is complete would violate ARCH-035 capture-only boundary.

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
