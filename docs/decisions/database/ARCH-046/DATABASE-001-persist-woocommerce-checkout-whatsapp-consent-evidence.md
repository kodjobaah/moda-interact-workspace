---
id: ARCH-046-DATABASE-001
architecture_id: ARCH-046
title: Persist Woo checkout-scoped WhatsApp consent evidence and change receipts
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-046-API-001
  - ARCH-046-BACKGROUND-001
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Persist Woo checkout-scoped WhatsApp consent evidence and change receipts

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Create transactional, tenant-scoped durable current WhatsApp recovery consent and minimal immutable change evidence for Woo checkout/recipient pairs.

## Context

Woo has no native Shopify-style WhatsApp consent authority. WordPress checkout sessions and Redis queue retention are not durable consent proof. Current `commerce.CheckoutRecovery` and its Shopify-only status do not store opt-in.

## Scope

- Create a minimal `WooWhatsAppRecoveryConsent` current projection keyed by `(shopId,checkoutKey,recipientCanonical,purpose)`, with decision GRANTED/REVOKED, monotonic sourceRevision, lastEvidenceEventId and server timestamps; absence means not authorised.
- Create a narrow immutable `WooWhatsAppConsentChange`/outbox receipt model with unique shop/event ID and shop/checkout/sourceRevision, evidence source+version/decision, bounded processing/lease/retry fields for later Background wakeups.
- Preserve FK/shop isolation, database timestamps, appropriate bounded-index query paths for exact consent, receipt claim and terminalised records; write Prisma migration and fresh/upgraded PostgreSQL rehearsal.
- Document limited customer data retention/export/erasure and terminal removal/revocation behaviour without introducing speculative tracking data.

## Out of Scope

- Do not add or duplicate `RecoveryAdmissionBlockReason.WHATSAPP_CONSENT_MISSING` (owned by ARCH-045-DATABASE-001).
- No Shopify consent object, PHP WP table, recovery materialisation or queue protocol implementation.
- No production data deletion or unsafe migration.

## Requirements

- Atomic projection + change record under one transaction; same `(shopId,eventId)` exact retry idempotent; conflicting replay rejected.
- Checkout-scoped `sourceRevision` monotonicity: older grant retry cannot overwrite newer revoke; distinct phone does not inherit previous grant.
- Do not store full checkout payload, HTML, browser tracking or arbitrary marketing flags; preserve evidence with bounded retention/privacy handling.
- Index claims without introducing unbounded hot scans; model finite pending receipt retirement before any live consent publishing is enabled, even while Woo recovery consumers are blocked. Use real table/column naming selected by Database and exposed through Prisma.

## Work Items

- [ ] Author Prisma models, keys, explicit enum/purpose, migration.
- [ ] Rehearse fresh and upgrade migration, event replay and concurrent grant/revoke.
- [ ] Verify exact-reader/outbox query plans, bounded expiration/retirement of no-op pending receipts, and document retention/erasure decisions.

## Interfaces / Contracts

Database/Prisma `WooWhatsAppRecoveryConsent` and `WooWhatsAppConsentChange` are canonical; producer API-001 owns transaction semantics; consumer BACKGROUND-001/003 imports Prisma models. No Shared queue contract.

## Dependencies

None

## Enables

- `ARCH-046-API-001`
- `ARCH-046-BACKGROUND-001`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] A duplicated event creates no second evidence/projection transition; conflicting same-ID payload fails.
- [ ] A late GRANT after newer REVOKE cannot change current state to GRANTED.
- [ ] `(shopId,checkoutKey,recipientCanonical)` uniqueness, tenant FK and bounded indexes are proven on disposable PostgreSQL.
- [ ] Pending receipts have a bounded retirement/expiry mechanism and cannot accumulate indefinitely during the pre-recovery phase.
- [ ] No modification of existing Shopify recovery enum/queue and no inferred legacy opt-ins.

## Validation

- [ ] Prisma format/validate, migration diff and fresh/upgrade disposable PostgreSQL tests.
- [ ] Query/idempotency/concurrency proof and `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Keep evidence minimal and queryable. Do not attach consent truth to a Woo order alone: checkout can be abandoned before the order is placed.

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
