---
id: ARCH-046-API-001
architecture_id: ARCH-046
title: Accept verified Woo customer-phone consent changes
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-DATABASE-001
  - ARCH-046-API-003
enables:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-BACKGROUND-003
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Accept verified Woo customer-phone consent changes

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Accept authenticated, explicitly affirmed or withdrawn Woo WhatsApp recovery consent for the **verified customer and exact phone**, storing current state on `CustomerPhone` and atomic evidence/re-evaluation receipt.

## Context

The hosted API already authenticates Woo installations. `woo.activity.v1` captures checkout events but is **not** a consent-write API; the same purchase checkout may be abandoned before order submission. DATABASE-001 owns Customer/CustomerPhone linkage, installation source and evidence schema.

## Scope

- Implement strict versioned `woo.whatsapp-consent.v1` POST contract over existing installation authentication. Derive `shopId` from installation; validate event ID, verified server-bound Woo account or guest checkout/session identity, exact current canonical phone, explicit GRANT/REVOKE, disclosureVersion, monotonic revision, source/provider/epoch and optional checkoutKey as **collection context**, not consent ownership.
- Resolve/create only the proven shop customer and matching `CustomerPhone` row; do not merge by phone/email or use client-selected customer IDs. An identity proof or source absent/ambiguous is **not** permission.
- Atomically check **current** installation source/provider/epoch, apply revision/order-safe current `CustomerPhone` transition and insert one minimal evidence/change receipt with immutable decision evidence. **While Woo recovery is not approved/enabled, mark the receipt non-actionable for wakeup at insertion**; do not create an indefinitely pending event for an absent consumer. A future approved engine can enable new actionable receipts. Unique shop/event ID makes retries idempotent, outdated grant after revocation/source switch fails closed. Respond after PostgreSQL commit; no synchronous Redis dependency.
- Reject unapproved external provider, forged checkbox/phone/customer/session, disabled source, wrong purpose, conflicting event or malformed request. Use Node Shared logger without PII/secrets. Ensure denied/unavailable writes do not block order placement at caller.

## Out of Scope

- No checkout-specific current-consent table, recovery creation, Shopify consent mutation, third-party generic checkbox detection or WordPress direct database access.

## Requirements

- [ ] A verified grant applies to the same customer/shop/phone and disclosed abandoned-checkout purpose (across checkouts only where disclosure permits); unknown/default is not granted.
- [ ] A phone change or revoked record never inherits a previous grant; a source switch invalidates former-epoch send eligibility.
- [ ] Unique event/revision and concurrency contract prevents grant resurrection. Pre-recovery events leave no pending wakeup backlog.

## Work Items

- [ ] Implement authenticated controller, strict input validation, current phone/evidence transaction and clear error mapping.
- [ ] Test guest/registered identity and source mode, phone changes, grant/revoke, old replay, duplicate retries, checkout context, disclosure mismatch, outages and logging.

## Interfaces / Contracts

Consumes DATABASE-001 Customer/CustomerPhone, WooCommerceInstallation and minimal evidence model plus API-003 source settings. Hosted route ownership resides in API repository; WordPress WOOCOMMERCE-002 is producer, Background-001/003 are current-state/evidence consumers.

## Dependencies

- `ARCH-046-DATABASE-001`
- `ARCH-046-API-003`

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-BACKGROUND-003`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Current decision is on correct CustomerPhone; audit/change receipt is immutable and deduplicated.
- [ ] Verified same customer exact phone only; old source/epoch, spoofed guest, phone-only or unauthorised provider fail closed.
- [ ] No CheckoutRecovery/credit/provider operation on consent ingestion and no forced checkout failure on Moda outage.

## Validation

- [ ] API authenticated/PostgreSQL transaction integration with stale/duplicate/revocation cases, repository-declared build/typecheck and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

No new Shared v1 JS package is justified by the PHP→HTTP integration. Use API-owned OpenAPI fixtures and PHP contract tests, not an independent duplicate of the wire schema. Do not enable live merchant publishing while an unbounded PENDING outbox could accumulate because the later recovery consumer is absent.

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
