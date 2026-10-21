---
id: ARCH-046-DATABASE-001
architecture_id: ARCH-046
title: Add Woo consent source and immutable customer-phone evidence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-046-API-003
  - ARCH-046-API-001
  - ARCH-046-BACKGROUND-001
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-21
---

# Add Woo consent source and immutable customer-phone evidence

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

On top of the shared `CustomerPhone` current-consent schema from **ARCH-045-DATABASE-002**, add Woo merchant consent-source settings to existing `WooCommerceInstallation` and **one immutable Woo grant/withdrawal evidence table**. Do not add a consent-event recovery worklist.

## Context

The snapshot has Customer/CustomerPhone but no current consent fields, WooInstallation source setting or reusable WhatsApp consent decision audit history. The current-state fields belong to ARCH-045-DATABASE-002 for both platforms. ARCH-046 needs a durable evidence fact for explicit Woo visitor decisions and idempotent API retries, not a queue/outbox to re-evaluate old carts.

## Scope

- Extend existing `woocommerce.WooCommerceInstallation` with default `NOT_CONFIGURED` source mode, optional explicitly approved provider ID and monotonic source epoch/revision; no new merchant config table.
- Add exactly one `WooWhatsAppConsentEvidence`-equivalent immutable event model: shop/customer/active-phone identity, canonical number/purpose, GRANT/REVOKE, source/provider/epoch, verified disclosure wording/version/locale, event ID/revision, server time, optional verified checkout collection context, and uniqueness `(shopId,eventId)` for replay detection. No phone-only customer creation or unverified consent.
- Preserve evidence facts across ordinary later grants, withdrawals or source switches (with explicit privacy export/erasure policy). Do **not** create `READY`, `NOT_ACTIONABLE`, claim/lease/retry/ack state or indexes for background evidence polling.
- Reuse ARCH-045-DATABASE-002 `commerce.CustomerPhone` current decision/source/ordering fields and `commerce.Customer` identity: **do not duplicate** them or create a consent current-state/history projection elsewhere.
- Write additive Prisma migration, fresh+upgrade PostgreSQL tests and correctness coverage for exact phone/customer/shop, source epoch/revision, duplicate vs conflicting event, immutable audit data and GDPR/privacy export/erasure.

## Out of Scope

- No `CustomerPhone` current-state schema ownership (ARCH-045-DATABASE-002).
- No new recovery enum, `CheckoutRecovery` for lack of consent, checkout-specific consent projection, consent expiry or 72-hour wait.
- No worklist/outbox, actionable evidence receipt processing state, Shared queue schema, background poller or wakeup retry.

## Requirements

- [ ] Merchant source choice lives only on existing WooInstallation.
- [ ] Current Woo consent lives only on shared CustomerPhone; one immutable record per genuine accepted decision provides audit/replay history.
- [ ] Evidence rows never schedule recovery or represent current sending authority; privacy erasure is explicit and independent of consent validity.
- [ ] No automatic GRANT by migration, generic marketing flag or external checkbox.

## Work Items

- [ ] Add WooInstallation source/epoch and one minimal append-only consent evidence Prisma model, consuming ARCH-045-DATABASE-002 fields.
- [ ] Add fresh/upgrade PostgreSQL tests for uniqueness, exact shop/customer/active phone, source fencing, grant/revoke ordering, audit immutability and privacy operations.
- [ ] Validate that evidence schema has **no** claim/ack/worklist fields and does not encode checkout wakeups.

## Interfaces / Contracts

**Current-state owner:** ARCH-045-DATABASE-002 (`commerce.CustomerPhone`). **Woo-specific DB owner:** this task (`WooCommerceInstallation` merchant source/epoch and `WooWhatsAppConsentEvidence`). **API-003** changes installation; **API-001** atomically writes current phone + evidence on consent POST; **BACKGROUND-001** reads only current phone plus installation during ordinary recovery reconciliation. No Background-003 poller/Shared queue.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-046-API-003`
- `ARCH-046-API-001`
- `ARCH-046-BACKGROUND-001`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Current consent on shared CustomerPhone; merchant mode on existing WooInstallation; exactly one immutable Woo evidence table, no other consent current/config tables.
- [ ] No pending/worklist/wakeup status, lease/claim/ack/retry columns, queue schema or polling indexes.
- [ ] Stored grant/withdrawal evidence and source epoch are immutable under ordinary writes, with deliberate privacy export/erasure semantics.
- [ ] Disposable PostgreSQL migration/idempotency/identity tests pass, no default grants or recovery creation.

## Validation

- [ ] Prisma validate/migration tests (fresh and upgrade), customer/phone/source idempotency and evidence immutability database tests, `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Keep evidence minimal, immutable and privacy-aware. `CommerceAuditEvent` is not a generic substitute for customer consent. Make the event ID, server decision timestamp, exact disclosure proof and verified recipient binding durable; do not add mutable claim/ack columns: no delivery worklist is authorised for consent events. Do not attach permission to a Woo order alone: checkout can be abandoned before order placement.

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
