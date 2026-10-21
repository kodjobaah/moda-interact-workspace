---
id: ARCH-046-BACKGROUND-001
architecture_id: ARCH-046
title: Read current Woo customer-phone consent for exact recipient
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 27
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-21
---

# Read current Woo customer-phone consent for exact recipient

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Provide one fail-closed Woo WhatsApp recovery-consent reader for a **verified customer and exact phone**, using current `CustomerPhone` plus active WooInstallation identity/status **only when ordinary recovery reconciliation runs**.

## Context

The consolidated ARCH-045-DATABASE-002 owns shared current-state phone fields, active Woo installation identity and audit evidence. The evidence table is **history only**, never the current consent reader or a queued recovery trigger. This reader can be implemented while ARCH-035 is capture-only.

## Scope

- Implement typed injectable reader accepting shop/verified customer/recipient/purpose and optional checkout ownership context, returning allowed/not-authorised/unavailable; use canonical phone exact-match and active CustomerPhone record.
- Check that the installation is currently active and the exact current CustomerPhone grant has `WOO_MODA_CHECKBOX` provenance for `WHATSAPP_CHECKOUT_RECOVERY`. Inactive installation, changed phone, revoked/unknown, ambiguous guest, no-contact/erasure or DB outage fails closed.
- Read no immutable evidence history for current permission, no worklist or queue. This reader is called at **normal** checkout reconciliation and existing proactive send admission by future approved Woo recovery engine.
- Test tenant/customer/active phone identity, installation lifecycle, guest/account, changed number, grant/revoke and injected DB errors; use Shared logging without PII.

## Out of Scope

- No Woo checkout recovery engine/materialisation (BACKGROUND-002), no consent-event consumer/poller (BACKGROUND-003 is superseded), no Shared queue or API capture.

## Requirements

- [ ] Only latest verified exact customer/phone/purpose grant from the authenticated Moda-checkbox flow is allowed.
- [ ] Inactive installation, revoked/unknown, foreign/changed phone, invalid provenance and DB errors cannot grant.
- [ ] A consent-change event does not call the reader to create recovery; normal reconciliation does.

- **C4:** Reconciliation must prove that the current checkoutKey/checkout activity belongs to the same server-verified Woo account or live guest session associated with Customer/CustomerPhone; never resolve customer solely from billing phone/contact. Reject expired/taken-over/rotated sessions and mixed Woo installations.
- **C2/C6:** Compare Shared-canonical exact phone plus active installation status and local no-contact revision; local STOP overrides a still-GRANTED checkbox. If the identity association, consent record or installation is unavailable, fail closed without creating CheckoutRecovery.
- **H5:** Return a short-transaction consent revision/snapshot used by approved future initial-send and follow-up fences; Woo does not need Shopify HTTP preflight.

- Always evaluate the shop/recipient STOP safety fence in existing WhatsAppRecipientReachability as well as CustomerPhone current consent; an unmatched inbound STOP cannot be bypassed by a later checkout event with an apparently granted customer row.

## Work Items

- [ ] Implement injected current CustomerPhone + installation consent reader.
- [ ] Add consent-state, installation disconnect, guest identity, wrong phone and failure tests.

## Interfaces / Contracts

Reads current CustomerPhone and WooInstallation identity/status from the consolidated ARCH-045-DATABASE-002 schema only. API-001 is phone-consent writer. Background-002/004 are future normal reconciliation/proactive send consumers. ARCH-046-BACKGROUND-003 is superseded.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Actual active CustomerPhone and Woo installation active status determine sending eligibility, not old evidence events.
- [ ] Safe default-deny and no guest phone-only merge; no queue/consent-wakeup.
- [ ] Reader can be tested without enabling an unapproved Woo recovery engine.

- [ ] Reconciliation is incapable of consuming another customer's permission even when phone numbers or checkoutKey strings coincide, and it denies an active local STOP.

## Validation

- [ ] Focused Background local consent provenance/installation state, exact recipient, guest identity, stale state and DB-failure tests, `git diff --check`.

- [ ] DB-backed cross-shop, guest takeover, account logout, country ambiguity, installation revoke/reconnect and opt-out tests.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

This task is safe to implement before a Woo recovery engine exists; do not include admission integration here.

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

None recorded at definition time; raise actual missing cross-repository contract/rollout dependencies to moda_architect before scope drift.

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
