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
  - ARCH-045-DATABASE-002
  - ARCH-046-DATABASE-001
  - ARCH-046-API-003
  - ARCH-045-SHARED-002
enables:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-21
---

# Accept verified Woo customer-phone consent changes

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Accept explicit authenticated Woo customer-phone GRANT/REVOKE decisions, **atomically updating current `CustomerPhone` and appending immutable Woo evidence**, without publishing or scheduling recovery work.

## Context

The hosted API already authenticates Woo installation calls. Woo checkout activity capture is separate from visitor permission, which can be given before order submission. The shared CustomerPhone state is owned by ARCH-045-DATABASE-002; WooInstallation/evidence fields are owned by ARCH-046-DATABASE-001.

## Scope

- Implement versioned `woo.whatsapp-consent.v1` authenticated POST with shop inferred from installation, verified logged-in Woo customer or active guest checkout/session identity, exact current canonical phone, source/provider/epoch and disclosure, explicit decision GRANT/REVOKE and stable event ID/revision.
- In a **single PostgreSQL transaction**, verify selected installation source/provider/current epoch and customer-phone ownership; reject ambiguous guest/phone-only identity, unsupported integration, stale/old-epoch writes or forged disclosure.
- Write the latest effective decision to shared CustomerPhone and exactly one **immutable** Woo evidence fact. Identical `(shopId,eventId)` retry returns idempotently; conflicting replay fails and cannot roll back a later withdrawal. Return success after DB commit.
- **Stop at the consent write**: no BullMQ publication, database evidence `READY`/`NOT_ACTIONABLE` state, recovery task, checkout scan, merchant notice, send or billing. Later normal checkout reconciliation reads the updated phone if it runs.
- Do not block storefront order placement if Moda API is unavailable; unacknowledged consent remains unverified. Use safe structured logging without phone/PII/secrets.

- When the current Woo checkout-activity v1 envelope cannot convey the same verified account/guest identity as the consent POST, **API-001 owns the narrowly versioned API capture-contract change** (and compatibility/replay tests); WOOCOMMERCE-002 owns matching plugin event production. No checkout eligibility inference from contact text alone.

## Out of Scope

- No checkout-specific current-consent table, recovery creation, Shopify consent mutation, third-party generic checkbox detection or WordPress direct database access.

## Requirements

- [ ] Current permission is shop/customer/exact phone/purpose scoped and source-epoch fenced; not a checkout-specific recovery flag.
- [ ] A recorded grant or revocation by itself creates no CheckoutRecovery and no next-run job.
- [ ] Duplicate/stale/forged consent input cannot grant permission or overwrite later withdrawal; no charge/Meta send.

- **C4:** Resolve the authenticated installation, verified Woo account or server-bound guest session, exact checkout association, and current canonical recipient using the DATABASE-001 identity link. Do not trust client-provided `customerId`, `phone`, `checkoutKey` or browser session as proof; unsigned/replayed/cross-shop/session-rotated bindings fail closed.
- **H3/H4:** Define an acknowledgement ordering contract: a positive pre-submit grant is eligible for a following normal checkout observation **only after the hosted transaction commits and acknowledgement returns**. If normal capture overtakes it, the candidate may miss recovery by design; neither API retries nor an eventual grant may start a consent wake-up. Require monotonic server-enforced decision ordering; an older separately named GRANT cannot overwrite a later REVOKE, including concurrent tabs, changed phone and installation source epoch ABA.
- Use published Shared Node E.164 canonicalisation; reject ambiguous locale/country or mismatched authenticated session phone. A merchant no-contact override cannot be cleared by a stale checkout grant; explicit newer, independently verified affirmative grant is required.
- Under privacy erasure fence, prevent delayed Action Scheduler retries from re-creating removed personal consent evidence or current phone state.

## Work Items

- [ ] Add verified Woo consent controller/validation and atomic CustomerPhone + immutable evidence transaction.
- [ ] Ensure no queue/broker/outbox/evidence wakeup side effect from the route.
- [ ] Test fresh grant, withdrawal, regrant, source switch, guest/account/phone binding, duplicate conflict, stale revision, host outage and no recovery side effects.

- [ ] Implement validated account/guest/checkout identity proof from trusted Woo server with nonce/session rotation protection, then atomic consent state plus immutable evidence write.
- [ ] Test two-tab GRANT/REVOKE interleaving, same ID/different body, lost ACK/retry, changed number, host outage, source-switch away/back, login/logout and deletion race.

## Interfaces / Contracts

Consumes ARCH-045-DATABASE-002 shared `CustomerPhone` consent and ARCH-046-DATABASE-001 installation/evidence schema, plus API-003 merchant source selection. `WOOCOMMERCE-002/003` are producers of authenticated versioned HTTP decisions. `BACKGROUND-001` reads current phone and merchant mode during **normal checkout reconciliation**, not evidence worklist. No Shared Redis queue.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-046-DATABASE-001`
- `ARCH-046-API-003`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Exact current CustomerPhone reflects latest verified decision and one immutable evidence fact is written atomically.
- [ ] Duplicate identical event is idempotent; conflicting or older event, wrong phone/customer/source/epoch is rejected.
- [ ] API never queues/reconciles old checkouts, constructs CheckoutRecovery, charges or sends when customer opts in/out.

- [ ] The Woo consent POST never grants on phone alone or unverified guest session and does not enqueue checkout reconciliation; consent only becomes usable after durable commit.
- [ ] A newer revoke/STOP/erasure always defeats delayed grants, different event IDs and retries, while a demonstrably newer explicit opt-in can restore consent.

## Validation

- [ ] Hosted API authenticated integration tests with disposable PostgreSQL transaction, idempotent replay, source switch, guest security, provider outage and no job/sends, `git diff --check`.

- [ ] Authenticated API/PostgreSQL race tests for guest hijack, account swap, cross-shop, canonical phone, concurrent tabs, source epoch ABA and privacy erasure with no recovery or outbound side effects.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

No new Shared v1 JS package is justified by the PHP→HTTP integration. Use API-owned OpenAPI fixtures and PHP contract tests, not an independent duplicate of the wire schema. Preserve consent audit facts without any actionability/status field, polling consumer, recovery wakeup, outbox or Shared queue contract, even after Woo recovery is enabled.

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
