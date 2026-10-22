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
  - ARCH-045-SHARED-002
enables:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-22
---

# Accept verified Woo customer-phone consent changes

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Accept explicit authenticated Woo customer-phone GRANT/REVOKE decisions, **atomically updating current `CustomerPhone` and appending immutable `commerce.WhatsAppConsentEvidence`**, without publishing or scheduling recovery work.

## Context

The hosted API already authenticates Woo installation calls. Woo checkout activity capture is separate from visitor permission, which can be given before order submission. The consolidated ARCH-045-DATABASE-002 owns shared CustomerPhone state, WooInstallation authentication/lifecycle and `commerce.WhatsAppConsentEvidence`.

## Scope

- Implement versioned `woo.whatsapp-consent.v1` authenticated POST with shop inferred from installation, server-validated Woo checkout/checkbox action, exact current canonical phone and installation-derived merchant scope, Moda-checkbox disclosure, explicit decision GRANT/REVOKE and stable event ID/revision.
- Treat the captured permission as **WhatsApp abandoned-checkout marketing** consent, not general transactional/utility notification permission. Validate the disclosure version and merchant identity; retained `WhatsAppConsentEvidence` shows which marketing description was affirmatively accepted. Do not create a new schema or evidence table for message classification.
- In a **single PostgreSQL transaction**, verify active installation credentials/status, existing checkout-recovery feature eligibility, deliberate checkbox action and `(Customer.shopId, active CustomerPhone canonical phone)` lookup; reuse the single unambiguous customer/phone match, create an ordinary Customer/CustomerPhone when none exists, and fail closed on multiple matches. Reject new grants from feature-disabled or inactive installations, stale decisions, forged checkbox actions or forged disclosure.
- Write the latest effective decision to shared CustomerPhone and exactly one **immutable** `commerce.WhatsAppConsentEvidence` fact. Identical `(shopId,eventId)` retry returns idempotently; conflicting replay fails and cannot roll back a later withdrawal. Return success after DB commit.
- **Stop at the consent write**: no BullMQ publication, database evidence `READY`/`NOT_ACTIONABLE` state, recovery task, checkout scan, merchant notice, send or billing. Later normal checkout reconciliation reads the updated phone if it runs.
- Do not block storefront order placement if Moda API is unavailable; unacknowledged consent remains unverified. A checkout page left open across merchant feature-disable cannot grant permission merely because its checkbox was previously visible. Authenticated withdrawals and negative opt-outs must remain possible through their approved routes. Use safe structured logging without phone/PII/secrets.

- When the Woo checkout-activity v1 envelope cannot carry the authenticated installation/shop and canonical recipient consistently with the consent POST, **API-001 owns the minimal versioned API capture-contract correction**; WOOCOMMERCE-002 owns plugin production. No persistent checkout-identity model is required. Contact text alone is never a consent GRANT.

## Out of Scope

- No checkout-specific current-consent table, recovery creation, Shopify consent mutation, third-party generic checkbox detection or WordPress direct database access.

## Requirements

- [ ] Current permission is shop and exact active canonical phone scoped through existing Customer/CustomerPhone, with purpose and monotonic revision; not a checkout-specific flag. No GRANT follows from lookup alone.
- [ ] A recorded grant or revocation by itself creates no CheckoutRecovery and no next-run job.
- [ ] A GRANT is backed by an explicit merchant-specific WhatsApp recovery **marketing** disclosure, not customer phone collection or a general service message agreement.
- [ ] Duplicate/stale/forged consent input cannot grant permission or overwrite later withdrawal; no charge/Meta send.

- **C4 revised:** Authenticate the existing Woo installation and derive `shopId` server-side. Validate that the checkbox choice originated from the active Woo checkout/WordPress request using the existing server-side hooks, nonce/session protections and install credentials. Resolve or create the existing Customer/CustomerPhone by merchant-scoped canonical phone. Never trust a browser-supplied `customerId` or unverified checkbox flag; never identify a *different merchant* by the same number. One safe match may be reused; ambiguous duplicates fail closed. The phone match is **identity lookup, not consent evidence**; a GRANT additionally requires a deliberate authenticated opt-in action.
- **H3/H4:** Define an acknowledgement ordering contract: a positive pre-submit grant is eligible for a following normal checkout observation **only after the hosted transaction commits and acknowledgement returns**. If normal capture overtakes it, the candidate may miss recovery by design; neither API retries nor an eventual grant may start a consent wake-up. Require monotonic server-enforced decision ordering; an older separately named GRANT cannot overwrite a later REVOKE, including concurrent tabs, changed phone and installation/session credential rotation.
- Use the published Shared canonical phone helper; reject ambiguous country context or inconsistencies between the canonical number the Woo server observed and the number the hosted request describes. No customer phone-ownership verification or persistent guest identity table is invented here. Neither a merchant no-contact restriction nor WhatsApp `CUSTOMER_STOP` can be cleared by the Woo checkbox grant; STOP is not a consent source and cannot be reset by this API.
- Consent-task retries must be idempotent and respect newer revoke/STOP decisions.

## Work Items

- [ ] Add verified Woo consent controller/validation and atomic CustomerPhone + immutable evidence transaction.
- [ ] Ensure no queue/broker/outbox/evidence wakeup side effect from the route.
- [ ] Test fresh grant, withdrawal, regrant, installation revocation, merchant/phone matching, feature-disabled stale checkout, duplicate conflict, stale revision, host outage and no recovery side effects.

- [ ] Validate the server-owned Woo checkout action (including guest CSRF/session protections), derive shop from the installation, resolve `(shopId, canonicalPhone)` safely, then atomically update consent plus `WhatsAppConsentEvidence`.
- [ ] Test two-tab GRANT/REVOKE interleaving, same ID/different body, lost ACK/retry, changed number, host outage, installation revoke/reconnect, login/logout and STOP race.

## Interfaces / Contracts

Consumes the consolidated ARCH-045-DATABASE-002 `CustomerPhone`, installation authentication/lifecycle and `commerce.WhatsAppConsentEvidence` schema. `WOOCOMMERCE-002/003` are producers of authenticated versioned HTTP decisions. `BACKGROUND-001` reads current phone and current active installation during **normal checkout reconciliation**, not evidence worklist. No Shared Redis queue.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Exact current CustomerPhone reflects latest verified decision and one immutable evidence record is written atomically.
- [ ] Duplicate identical event is idempotent; conflicting or older event, cross-shop phone or ambiguous duplicate customer/phone matches are rejected; no phone lookup silently changes permission.
- [ ] API never queues/reconciles old checkouts, constructs CheckoutRecovery, charges or sends when customer opts in/out.

- [ ] The Woo consent POST may resolve by the sole merchant-scoped active canonical phone, but does **not grant from that match alone**: a validated deliberate Moda-checkbox opt-in and durable commit are required. No checkout reconciliation job is enqueued.
- [ ] A newer revoke or customer STOP always defeats delayed grants, different event IDs and retries. A newly verified Woo checkbox grant may update the consent decision/evidence but **cannot clear a previously recorded WhatsApp `CUSTOMER_STOP`**; any STOP removal requires a separate authorised and verified customer request to Moda, outside API-001.

## Validation

- [ ] Hosted API authenticated integration tests with disposable PostgreSQL transaction, idempotent replay, revoked installation, guest security, hosted-API outage and no job/sends, `git diff --check`.

- [ ] Authenticated API/PostgreSQL race tests for guest checkout CSRF, cross-shop canonical phone, one/no/multiple phone matches, explicit opt-in vs mere lookup, concurrent tabs, installation credential rotation and STOP precedence with no recovery or outbound side effects.

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
