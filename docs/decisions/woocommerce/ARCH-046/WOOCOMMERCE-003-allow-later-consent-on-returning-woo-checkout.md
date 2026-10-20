---
id: ARCH-046-WOOCOMMERCE-003
architecture_id: ARCH-046
title: Handle later Woo customer-phone consent and withdrawal
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

# Handle later Woo customer-phone consent and withdrawal

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Allow a verified Woo customer to give or withdraw WhatsApp unfinished-checkout consent later, updating the **same current customer-phone permission** without requiring a pre-existing `CheckoutRecovery`.

## Context

A customer can return to a legitimate still-valid checkout or use another verified checkout while logged in after first refusing/not seeing opt-in. Consent is a customer/phone/purpose preference, not a 72-hour checkout permission or `DETECTED` recovery state.

## Scope

- Support later explicit GRANT or REVOKE through a verified returning Woo checkout/session or another checkout linked to an authenticated Woo account using the currently selected approved collector; bind the exact current `CustomerPhone` and source/epoch and publish API-001 ordered events.
- Preserve/verify session checkoutKey when a later grant is intended to trigger old checkout re-evaluation, but **do not make current consent valid only for that checkout**. Invalid/expired/foreign session cannot be used to recover that old checkout; a verified account can retain its consent preference independently of whether any checkout remains.
- Display existing consent accurately, avoid auto-grant/prechecking a new choice, support opt-out, changed phone and 20-locale accessible text. Pending hosted write is not successful until acknowledged.

## Out of Scope

- No new My Account preference page, unauthenticated consent-by-phone page, global marketing campaign opt-in, guest cross-session identity guessing, new Woo recovery engine or forced old checkout recreation.

## Requirements

- [ ] Later legitimate GRANT/REVOKE changes the same customer-phone-purpose state, not a new checkout-specific projection.
- [ ] Consent remains effective until withdrawal/source invalidation/other applicable rules; no arbitrary 72-hour timer.

## Work Items

- [ ] Implement verified returning/successive checkout grant and withdrawal via existing plugin boundaries.
- [ ] Test new checkout for already-consented verified account, expired guest session, changed phone, grant/revoke ordering, and hosted outage.

## Interfaces / Contracts

Uses API-001 source-bound events and WOOCOMMERCE-002 verified customer/session/phone integration; no new hosted auth mechanism or recovery queue.

## Dependencies

- `ARCH-046-WOOCOMMERCE-002`

## Enables

- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] A returning verified customer can revoke or grant current phone permission; no cross-guest reuse from shared phone.
- [ ] Later opt-in does not itself create a recovery, and invalid checkout cannot be resurrected.

## Validation

- [ ] Focused Woo/LocalWP returning guest/account and API/PostgreSQL persistence evidence; declared lint/build and `git diff --check`.

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
