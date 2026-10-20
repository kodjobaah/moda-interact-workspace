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

Transmit explicit Woo checkout WhatsApp grants and revocations **only from the merchant's currently approved source** from Classic/Blocks to the hosted consent API before order placement while preserving checkout performance.

## Context

WOOCOMMERCE-007 owns the stable `checkoutKey`; API-001 owns the contract/DB receipt. Checking a Woo additional field that is only inspected after purchase does not protect abandoned checkout recovery.

## Scope

- For `MODA_CHECKBOX`, observe actual affirmative Moda checkbox changes using supported Classic and Checkout Blocks pre-submit pathways (Woo Store API extension callback where appropriate). For `SUPPORTED_EXTERNAL`, accept only a separately architect-approved **provider-specific adapter** with a verifiable explicit customer action, recipient, disclosure, opt-out and checkout identity; **no adapter is currently approved** and that mode must not be activated via generic plugin flags.
- Derive checkoutKey and then-current phone from the **server-resolved Woo checkout session**, not arbitrary browser-provided identifiers; verify session nonce/CSRF and bind an explicit choice to exact recipient.
- Store short-lived pending events safely in existing WP session/Action Scheduler retry facilities; use immutable eventId+monotonic checkout sourceRevision, **active acknowledged provider/source and configurationEpoch** and server-to-server ModaApiClient installation auth. A source switch makes older events stale; never map a previous provider grant into a new mode.
- Prevent phone edit from transferring a previous grant to a new number; require a new affirmative user action for new number and emit revocation of the old checkout/recipient if required by current state.
- Only represent a grant as hosted-accepted after API durable acknowledgement for the **matching current host source and epoch**; do not block shopper checkout if the API is temporarily unavailable. `NOT_CONFIGURED`, unknown or unavailable provider and plugin disconnection produce no accepted grant.

## Out of Scope

- No direct JS-to-Moda API, raw WP credential in browser, PHP PostgreSQL/Redis access, new WordPress consent table, automatic integration with arbitrary checkout plugins or inferred opt-in from order meta.
- No Woo recovery materialisation or customer outreach.
- Do not duplicate or modify ARCH-035's capture-only activity queue to convey consent.

## Requirements

- Capture works even when visitor abandons **before placing order**. Verify in real LocalWP with no order creation.
- Initial unchecked state is unknown (not revoke); deliberate grant/revoke changes preserve source revision across retry and are not overwritten by out-of-order network responses. Mode/provider mismatch, former epoch or unsupported external adapter never create a grant.
- Strict session/nonce/cart-token identity, bounded bot/rate-abuse guards, no unverified phone-only writes.
- API outages never prevent checkout; pending grant never authorises send; fix conflict by explicit user action, not silent success.

## Work Items

- [ ] Implement Classic and Blocks consent change capture backed by actual Woo session and stable checkoutKey.
- [ ] Add small install-authenticated PHP client/Action Scheduler publisher with source/provider/epoch and bounded immutable retry identity.
- [ ] Test checkout abandonment, phone edits, invalid sessions, grant/revoke order, API outage, plugin reinstall/upgrade/HPOS.

## Interfaces / Contracts

Consumes API-001's `woo.whatsapp-consent.v1` OpenAPI/HTTP contract and Woo `ARCH-035-WOOCOMMERCE-007` checkoutKey. Crosses PHP→hosted API only with installation credential kept in server-side PHP.

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

- [ ] Under Moda source, grant on Classic and Blocks reaches hosted DB **without order placement** and matches exact checkoutKey/phone; no false grant from unchecked/failed request, disabled source or arbitrary third-party field.
- [ ] Phone changed after grant cannot authorise a different recipient without another affirmative choice.
- [ ] Multiple retries preserve event identity and order; stale retry cannot restore revoked grant.
- [ ] API unavailable: checkout succeeds; no hosted opt-in is fabricated and retries are bounded/visible.

## Validation

- [ ] Real LocalWP Classic/Blocks/HPOS guest and logged-in integration with API fixture; deliberately abandon before clicking Place Order.
- [ ] PHPUnit, JS tests, PHP lint, production ZIP and 20-locale assets; `git diff --check`.

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
