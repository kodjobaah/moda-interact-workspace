---
id: ARCH-046-WOOCOMMERCE-003
architecture_id: ARCH-046
title: Allow later opt-in and withdrawal on a returning Woo checkout
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-WOOCOMMERCE-002
enables:
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Allow later opt-in and withdrawal on a returning Woo checkout

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Make a deliberate later opt-in or revocation on the same verified returning Woo checkout create a fresh ordered consent event rather than silently using stale cached checkbox state.

## Context

Customer may return to an incomplete checkout after its first recovery was blocked. v1 consent is checkout-scoped; there is no general phone-number subscription manager or trustworthy cross-session lookup.

## Scope

- On re-entry to an actually existing Woo checkout session, preserve/resolve the exact stable checkoutKey and current phone, but never pre-check a new grant without an explicit action.
- When shopper explicitly checks to opt in later, emit fresh GRANT with new sourceRevision; explicit withdrawal after an accepted grant emits REVOKE, including changed phone/recipient handling.
- Handle guest/account sessions via supported Woo APIs and refuse unlinked checkout impersonation or expired session reuse; show safe confirmation/failure language while the hosted acknowledgement is pending.
- Keep consent UI accessible and WordPress-native i18n; no unsolicited reminders or account-wide consent promotion.

## Out of Scope

- No separate publicly writable opt-in-by-phone page, no verification-code provider, no new global marketing subscription.
- No Background resume implementation or merchant Support notification.
- Do not revive a Woo session the platform says has expired.

## Requirements

- An explicit later action tied to same checkout is sufficient to produce a new event; a cached state or auto-populated field is not.
- Never silently grant new phone/account checkout by copying previous checkout consent.
- An explicit revoke wins over late retries of old grant; no consent cross-shop.

## Work Items

- [ ] Implement returning-checkout lifecycle and explicit change controller.
- [ ] Test abandoned guest return, signed-in return, changed number, expired session and revoke-before-old-grant-retry.
- [ ] Update localized UI feedback and plugin regression tests.

## Interfaces / Contracts

Reuses only WOOCOMMERCE-002 authenticated transport and API-001 contract; source scope `(shopId,checkoutKey,recipient,purpose)` unchanged.

## Dependencies

- `ARCH-046-WOOCOMMERCE-002`

## Enables

- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Returning same legitimate checkout can create new GRANT after initial absence without completing an order.
- [ ] Explicit withdrawal records REVOKED and cannot be beaten by an older request retry.
- [ ] Unknown/expired/different checkout cannot grant permission to a blocked prior recovery by phone alone.

## Validation

- [ ] LocalWP guest/account return-to-checkout paths and PHP/JS tests with fake hosted API.
- [ ] Production build, 20-locale translation checks and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

No standalone My Account/global consent feature is authorised by v1. If the session is no longer verifiable, old recovery must expire rather than guess customer identity.

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
