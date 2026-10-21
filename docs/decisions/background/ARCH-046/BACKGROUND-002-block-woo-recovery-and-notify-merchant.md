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
  - ARCH-046-BACKGROUND-003
  - ARCH-046-BACKGROUND-004
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Skip unconsented Woo recovery creation and notify merchant

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

When a **separately approved** Woo abandoned-checkout recovery runtime evaluates a checkout, refuse **initial CheckoutRecovery creation** without current WhatsApp consent and notify the merchant once by checkout identity.

## Context

ARCH-035 currently captures Woo checkout/order updates only; its events are not an authorised recovery engine or live checkout-state reader. This task remains **BLOCKED** until a distinct approved Woo recovery lifecycle is implemented. ARCH-045-DATABASE-001 is superseded; there is no consent-specific recovery enum.

## Scope

- At a future approved Woo **pre-materialisation** seam, resolve stable checkoutKey, verified Woo customer/guest identity, exact phone, maturity, unpaid/abandoned state and entitlement; inject BACKGROUND-001 consent policy **before** any `CheckoutRecovery` persistence, attempt, reservation or Meta dispatch.
- Missing/revoked customer consent, unconfigured or unsupported source, changed phone or unverifiable identity -> **no CheckoutRecovery row, attempt, billable credit or provider send**. Verification unavailable is a distinct fail-closed retryable operational result, not an assertion of refusal.
- Add one shop-scoped existing Support SYSTEM notice with deterministic `sourceKey` derived from `shopId + checkoutKey + reason`, **not recovery ID**. Distinguish unconfigured collection, unverified customer consent and transient API failure; no fabricated 72-hour expiry promise. Retry notice independently and avoid duplicate notices on raw updates.
- Preserve missing-phone handling separately and existing recovery/provider/billing protections for a positively consented eligible checkout, including final pre-provider recheck.

## Out of Scope

- No implementation of the missing Woo recovery engine/state reader, consent-expiry timer, recovery block enum, `DETECTED` waiting row, custom notice table or merchant force-send.

## Requirements

- **Execution gate:** architect must record and accept separate Woo live checkout-state, order completion and initial materialisation contract before changing `blocked` to `ready`.
- Missing consent never creates a CheckoutRecovery, whether reason is non-affirmative customer action or missing setup.
- Merchant notice must not itself be used as authoritative checkout persistence.

## Work Items

- [ ] Reconcile approved Woo recovery engine dependency in canonical task and claim only when unblocked by architect.
- [ ] Inject pre-creation consent gate and idempotent checkout-keyed Support writer.
- [ ] Test exact customer/phone verification, zero-row/zero-credit, duplicate/failed notice and valid subscribed path.

## Interfaces / Contracts

ARCH-046-BACKGROUND-001 current customer-phone reader and existing `MerchantSupportMessage.sourceKey`; relies on separately approved Woo recovery engine. **No ARCH-045 database enum.**

## Dependencies

- `ARCH-046-BACKGROUND-001`

## Enables

- `ARCH-046-BACKGROUND-003`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] No consent means **no CheckoutRecovery**, only one merchant checkout notice, no attempt/credit/provider send.
- [ ] Source unconfigured is reported correctly, not labelled as customer refusal; out-of-order/duplicate capture cannot double-notify or send.
- [ ] Consent verified and checkout eligible uses approved ordinary first recovery admission; no 72-hour waiting recovery.

## Validation

- [ ] Approved Woo checkout engine fixture, fresh consent API/DB, disposable PostgreSQL credit/send/race assertions and `git diff --check`; record absent engine as blocked, not PASS.

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
