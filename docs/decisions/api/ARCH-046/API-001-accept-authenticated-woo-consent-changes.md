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

## Out of Scope

- No checkout-specific current-consent table, recovery creation, Shopify consent mutation, third-party generic checkbox detection or WordPress direct database access.

## Requirements

- [ ] Current permission is shop/customer/exact phone/purpose scoped and source-epoch fenced; not a checkout-specific recovery flag.
- [ ] A recorded grant or revocation by itself creates no CheckoutRecovery and no next-run job.
- [ ] Duplicate/stale/forged consent input cannot grant permission or overwrite later withdrawal; no charge/Meta send.

## Work Items

- [ ] Add verified Woo consent controller/validation and atomic CustomerPhone + immutable evidence transaction.
- [ ] Ensure no queue/broker/outbox/evidence wakeup side effect from the route.
- [ ] Test fresh grant, withdrawal, regrant, source switch, guest/account/phone binding, duplicate conflict, stale revision, host outage and no recovery side effects.

## Interfaces / Contracts

Consumes ARCH-045-DATABASE-002 shared `CustomerPhone` consent and ARCH-046-DATABASE-001 installation/evidence schema, plus API-003 merchant source selection. `WOOCOMMERCE-002/003` are producers of authenticated versioned HTTP decisions. `BACKGROUND-001` reads current phone and merchant mode during **normal checkout reconciliation**, not evidence worklist. No Shared Redis queue.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-046-DATABASE-001`
- `ARCH-046-API-003`

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Exact current CustomerPhone reflects latest verified decision and one immutable evidence fact is written atomically.
- [ ] Duplicate identical event is idempotent; conflicting or older event, wrong phone/customer/source/epoch is rejected.
- [ ] API never queues/reconciles old checkouts, constructs CheckoutRecovery, charges or sends when customer opts in/out.

## Validation

- [ ] Hosted API authenticated integration tests with disposable PostgreSQL transaction, idempotent replay, source switch, guest security, provider outage and no job/sends, `git diff --check`.

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
