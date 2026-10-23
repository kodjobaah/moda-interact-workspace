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
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-046-BACKGROUND-004
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-22
---

# Skip unconsented Woo recovery creation and notify merchant

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

Once a **separately approved Woo recovery engine** exists, guard the first `CheckoutRecovery` creation during ordinary Woo checkout reconciliation and notify the merchant when verified WhatsApp permission is absent; never create a consent-wait recovery.

## Context

ARCH-035 currently stops at **capture-only**. This task remains `blocked` even if listed dependencies complete until the architect approves an actual Woo checkout-state/materialisation/billing workflow. `ARCH-046-BACKGROUND-001` provides the reusable current-permission reader; a consent update by itself never initiates checkout evaluation.

## Scope

- Wire BACKGROUND-001's injected exact-recipient consent policy into the **approved** normal Woo checkout-to-recovery seam **before the first CheckoutRecovery INSERT**, initial attempt reservation and billing. Check active installation, authoritative unpaid/abandoned checkout state, exact current customer/phone, mature policy and entitlement independently.
- On missing/revoked/unknown/ambiguous consent, local STOP or merchant suppression, create no first recovery row, attempt, WhatsApp send or credit. A stored `GRANTED` decision never overrides STOP; BACKGROUND-005 owns the merchant STOP notice so do not duplicate it as a missing-consent notice. Treat installation inactive and database/provider availability as distinct technical/configuration failures, not proof that the customer declined consent.
- Write one idempotent `MerchantSupportMessage(kind=SYSTEM)` for the shop + **hashed** checkout reference + reason using the existing Support schema; do not require a nonexistent recovery ID or expose phone data. Preserve bounded notices and existing billing/idempotency behaviour.
- Reuse the policy on any approved `DETECTED` initial retry, capacity resume or suppression re-entry; BACKGROUND-004 owns final pre-provider dispatch enforcement. A later customer grant can be considered **only** if a subsequent normal Woo checkout reconciliation event independently occurs.
- Do not implement the unavailable Woo recovery engine as part of this task or interpret ARCH-035 capture activity as an approved recovery trigger.

## Out of Scope

- No Woo recovery-engine/state-reader implementation, consent-specific poll/queue, evidence wakeups, 72-hour timer, `DETECTED` consent waiting row, new Support table, installation consent-source configuration or privacy-erasure fence.

## Requirements

- [ ] The Woo initial abandoned-basket reminder is business-initiated direct marketing and uses only a Meta-approved **Marketing** recovery template; Utility/Authentication/unknown categories are not eligible. BACKGROUND-004 owns the final category check. Missing or invalid category must fail closed with no Meta send or credit.

- [ ] Stay `blocked` until the separately approved Woo recovery state reader, initial materialisation and billing admission contracts are architect-accepted.
- [ ] No verified current permission means no first CheckoutRecovery, credit or Meta send, regardless of which approved normal checkout entry invokes the policy.
- [ ] Missing customer consent, ambiguous identity, inactive installation and verification unavailable produce truthful, deduplicated merchant/operational outcomes.

## Work Items

- [ ] Once explicitly unblocked, integrate BACKGROUND-001 policy before first Woo recovery materialisation and all approved initial reentries.
- [ ] Add existing checkout-keyed SYSTEM Support notices and distinct failure/denial reasons.
- [ ] Test valid grant, unknown/revoked/ambiguous, installation inactive, paid checkout, no-event/later-event, retries, billing and zero Meta sends on denial.

## Interfaces / Contracts

Consumes ARCH-046-BACKGROUND-001 local consent reader, existing WooInstallation and the **external, independently approved** live Woo recovery contract. Reuses Support and billing contracts. Does not depend on superseded ARCH-046-BACKGROUND-003 or read `WhatsAppConsentEvidence` as a recovery worklist.

## Dependencies

- `ARCH-046-BACKGROUND-001`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Initial Woo recovery admission requires a customer-authorised WhatsApp **marketing** opt-in from current CustomerPhone and does not treat collected checkout phone/details as permission; approved Marketing template eligibility is checked before outbound.

- [ ] No newly created recovery, attempt, Meta send or charge on missing/revoked/ambiguous permission, no-contact or inactive installation; checkout-keyed merchant notices are deduplicated.
- [ ] A later valid opt-in by itself creates/schedules nothing; only a new normal reconciliation may create the first recovery under current paid/checkout eligibility.
- [ ] First-send reentries reuse the same policy without circumventing the separate final dispatch fence; no new recovery state or queue is introduced.
- [ ] Task remains Blocked until a real approved Woo recovery engine and checkout state reader are available.

## Validation

- [ ] **Only after engine approval:** focused Woo checkout-to-recovery/materialisation, initial retries, paid-order races, Support notice, installation revoke, local STOP/merchant suppression, idempotent billing and no-event/next-event tests.
- [ ] Verify no evidence worklist, consent-wakeup or unapproved capture-only send path; repository-declared checks and `git diff --check`.

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
