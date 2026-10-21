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
updated: 2026-10-21
---

# Handle later Woo customer-phone consent and withdrawal

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Allow a verified Woo customer to grant or withdraw WhatsApp recovery consent on a later eligible checkout/session, changing the **same current CustomerPhone preference** with no consent-driven recovery wakeup.

## Context

A customer can return to a legitimate still-valid checkout or use another verified checkout while logged in after first refusing/not seeing opt-in. Consent is a customer/phone/purpose preference, not a 72-hour checkout permission or `DETECTED` recovery state.

## Scope

- Support later deliberate GRANT/REVOKE through an authenticated returning Woo account or securely bound live guest checkout/session; verify current phone and active source/epoch and publish new ordered API-001 decisions with stable retry event IDs.
- An existing recorded preference may be displayed accurately but must not be treated as a fresh opt-in. A changed phone or unverified/expired guest session cannot reuse an older grant across customers.
- Never try to find or retry an earlier abandoned checkout when the decision is submitted. The **next ordinary Woo reconciliation event**, if one occurs for an eligible checkout, reads current CustomerPhone and may then create a recovery through BACKGROUND-002. No 72-hour consent timer.
- Keep clear 20-locale accessible opt-in/out language and failure feedback only after hosted write acknowledgement.

## Out of Scope

- No new My Account preference page, unauthenticated consent-by-phone page, global marketing campaign opt-in, guest cross-session identity guessing, new Woo recovery engine or forced old checkout recreation.

## Requirements

- [ ] Later grant/revoke writes the same exact customer-phone-purpose preference, not a checkout-specific record or recovery trigger.
- [ ] No automatic old-checkout recovery promise and no inherited grant on phone/source change.

- Returning/changed-identity interactions must reprove checkout/session ownership and canonical phone; old grant does not follow account logout, phone rotation, stale source or a shared family mobile. Any newer local STOP requires a fresh explicit grant before clearing.
- Use the same monotonic decision revision and identity proof as WOOCOMMERCE-002; session/login changes invalidate earlier unacknowledged retries.

## Work Items

- [ ] Update returning checkout/account consent choice via existing verified Woo checkout session and API-001.
- [ ] Test grants/withdrawals, multiple later checkouts, changed phone, expired guest identity and absence of candidate/recovery side effects.

## Interfaces / Contracts

Uses API-001 current CustomerPhone + immutable evidence write and WOOCOMMERCE-002 verified checkout transport. No recovery queue or evidence wakeup; BACKGROUND-002 is invoked only by future ordinary checkout reconciliation.

## Dependencies

- `ARCH-046-WOOCOMMERCE-002`

## Enables

- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Later verified decision correctly changes current CustomerPhone and audit record; unsafe guest/phone reuse prevented.
- [ ] No new recovery or re-evaluation job from consent alone; any recovery requires a separate ordinary checkout event.

## Validation

- [ ] Focused Woo/LocalWP returning guest/account and API/PostgreSQL persistence evidence; declared lint/build and `git diff --check`.

- [ ] Two-tab logout/login, consent regrant after STOP, switched provider and changed-number tests.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

No standalone My Account/global consent feature is authorised by v1. If the session is no longer verifiable, reject the consent write for that claimed identity rather than guess customer identity or schedule old recovery work.

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
