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
  - ARCH-046-WOOCOMMERCE-005
enables:
  - ARCH-046-WOOCOMMERCE-003

  - ARCH-046-BACKGROUND-003
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Capture affirmative pre-submit Woo consent and publish durable evidence

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Securely publish an explicit Woo WhatsApp recovery opt-in/withdrawal **before order placement** and bind it to a verified customer and exact phone at the active merchant consent source.

## Context

Classic/Blocks additional checkout field persistence at order completion does not guarantee Moda can recognise consent before abandonment. Hosted API-001 records current customer-phone permission; Woo registered/guest sessions and checkout keys must be resolved server-side.

## Scope

- In both Classic and Blocks, capture **deliberate customer action** (grant/revoke) via supported checkout integration and server-verified live cart/phone; do not infer from unchecked defaults or completed order metadata. Respect active hosted mode/provider/epoch; Woo Moda collector can write only when selected.
- For logged-in Woo customer resolve authenticated Woo account identity; for guests bind to current checkout/session `checkoutKey` and secure Woo nonce/session state, allowing Moda to resolve safe Customer identity. The checkout key is **collection context** and later checkout match, not scope of a reusable phone consent. Never trust browser-submitted shop/customerId or phone without current server-side check.
- Through existing WordPress server-to-server installation credentials, call hosted API-001 using stable event ID/source revision across retries. Send exact phone, disclosureVersion and purpose with authenticated customer/session evidence. No JS-to-hosted API credentials or PHP PostgreSQL access. Checkout must remain functional on API outage, but do not report uncommitted consent as stored.
- When account customer already has a verified grant, display/handle current preference without silently emitting a new GRANT on default/prechecked render. Switching phone requires a fresh positive grant for that recipient.

## Out of Scope

- No recovery creation, Shopify code, new WP consent table, arbitrary third-party checkbox integration or unilateral consent grants from admin.

## Requirements

- [ ] Positive action is persisted in hosted CustomerPhone before abandonment when connectivity succeeds; mere completed-order field does not suffice.
- [ ] Guest identity is server-bound; phone alone cannot reuse another customer's grant. Unavailable host allows checkout but not outbound permission.

## Work Items

- [ ] Implement isolated Classic/Blocks pre-submit change capture, server-bound customer/phone resolution and server-to-server retry.
- [ ] Test abandon-before-order, guest/registered identity, new phone, withdrawn consent, disabled source, retries, API outage, HPOS and active locale.

## Interfaces / Contracts

Consumes WOOCOMMERCE-001 field, WOOCOMMERCE-005 acknowledged collector mode, ARCH-035 checkoutKey support and API-001 versioned customer-phone consent contract.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-001`
- `ARCH-046-WOOCOMMERCE-005`

## Enables

- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-046-BACKGROUND-003`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Abandoned checkout with checked/accepted consent leaves shop-correct CustomerPhone grant/evidence, but **no CheckoutRecovery** in capture-only phase.
- [ ] Duplicate/retry/late phone change cannot turn unverified consent into a sendable grant or block checkout.
- [ ] No source-mode bypass or raw installation credential exposed to browser.

## Validation

- [ ] LocalWP guest/registered Classic/Blocks pre-order integration and API/PostgreSQL assertion, PHP/JS unit tests, declared lint/build and `git diff --check`.

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
