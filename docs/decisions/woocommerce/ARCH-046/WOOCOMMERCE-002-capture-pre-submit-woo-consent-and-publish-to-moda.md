---
id: ARCH-046-WOOCOMMERCE-002
architecture_id: ARCH-046
title: Capture affirmative pre-submit Woo consent and publish durable evidence
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 27
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-WOOCOMMERCE-007
  - ARCH-046-API-001
  - ARCH-046-WOOCOMMERCE-001
enables:
  - ARCH-046-WOOCOMMERCE-003
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-21
---

# Capture affirmative pre-submit Woo consent and publish durable evidence

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Securely publish an explicit Woo WhatsApp recovery opt-in/withdrawal **before order placement** and bind it to a verified customer and exact phone through Moda’s own optional checkout field.

## Context

Classic/Blocks additional checkout field persistence at order completion does not guarantee Moda can recognise consent before abandonment. Hosted API-001 records current customer-phone permission; Woo registered/guest sessions and checkout keys must be resolved server-side.

## Scope

- In Classic and Blocks, capture a deliberate checkbox GRANT or withdrawal through supported UI hooks and server-verified live Woo cart/checkout/session with exact customer/phone. Do not infer opt-in from a default checked field or completed order metadata.
- Use the existing verified WordPress installation authentication to POST to API-001, with stable event ID on retry; bind guest to authenticated server-side Woo session, never mobile number alone.
- Persist consent **before order placement** when the hosted API is available; on outage checkout may proceed but current permission remains unverified. Consent submission itself never schedules a recovery/reconciliation job.
- Preserve 20-locale opt-in wording, both checkout implementations, and Moda checkbox registration controlled by existing installation/feature eligibility.

- Update the existing Woo plugin checkout activity publisher to carry the *same server-verified customer/account or protected guest session binding* accepted by API-001, under an agreed version/compatibility transition. Do not change ARCH-035 capture-only business semantics or turn consent submission into checkout reconciliation.

## Out of Scope

- No recovery creation, Shopify code, new WP consent table, arbitrary third-party checkbox integration or unilateral consent grants from admin.

## Requirements

- [ ] Positive action is persisted in hosted CustomerPhone before abandonment when connectivity succeeds; mere completed-order field does not suffice.
- [ ] Guest identity is server-bound; phone alone cannot reuse another customer's grant. Unavailable host allows checkout but not outbound permission.

- **C4/H3:** For Classic and Blocks, use a server-verified Woo account principal or protected guest checkout/session binding that the hosted API can independently validate and later join to the **same** normal checkout event. Never transport or persist raw browser session bearer in the audit payload; rotate/fence on logout, login, session expiry and phone edits.
- Choose and document the pre-submit consent publication point independently for each checkout mode. The UI must not show success or allow recovery eligibility until the hosted API acknowledges a durable consent write; normal checkout activity published before ACK must remain potentially ineligible. Do not fabricate consent from order-meta/checkbox render state or schedule a special recovery wake-up to fix races.
- Make retried HTTP publication idempotent with stable event ID and server-ordered decision revision; a revoke must not be overtaken by late GRANT after a multi-tab or Action Scheduler retry. Woo checkout itself must remain usable on hosted outage.

## Work Items

- [ ] Implement isolated Classic/Blocks pre-submit change capture, server-bound customer/phone resolution and server-to-server retry.
- [ ] Test abandon-before-order, guest/registered identity, new phone, withdrawn consent, disabled recovery feature, retries, API outage, HPOS and active locale.

- [ ] Implement checkout/session identity proof transport and logged-in/guest rotation tests in Classic and Blocks with independently observable API ACK vs checkout event ordering.
- [ ] Test abandonment before Place Order, API delayed/failure, lost ACK/retry, Blocks Store API nonce/cart-token, Classic CSRF, new phone, logout and cross-device ambiguous guest.

## Interfaces / Contracts

Consumes WOOCOMMERCE-001 Moda field, ARCH-035 checkoutKey support and API-001 versioned customer-phone consent contract.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-001`

## Enables

- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Verified explicit pre-submit phone consent updates hosted CustomerPhone with immutable evidence exactly once per decision.
- [ ] Unselected checkbox, inactive installation or hosted outage does not grant consent or block Woo order submission.
- [ ] Consent change alone causes no checkout candidate/recovery enqueue or WhatsApp/billing action.

- [ ] With ACK first, a subsequent normal checkout reconciliation sees the same consent and customer; with checkout first/no ACK, no recovery is promised, no wake-up invented, and order placement remains unaffected.

## Validation

- [ ] LocalWP guest/registered Classic/Blocks pre-order integration and API/PostgreSQL assertion, PHP/JS unit tests, declared lint/build and `git diff --check`.

- [ ] End-to-end LocalWP Classic/Blocks pre-submit ordering tests with queued checkout activity and hosted API captured independently.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Keep session binding, field observation and remote publication in separate small classes/modules. Avoid one large `Runtime.php` or `page.js` handler; use existing server transport and Action Scheduler where available.

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
