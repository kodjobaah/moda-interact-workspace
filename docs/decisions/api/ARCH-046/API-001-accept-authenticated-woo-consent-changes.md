---
id: ARCH-046-API-001
architecture_id: ARCH-046
title: Accept durable authenticated Woo checkout WhatsApp consent changes
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
enables:
  - ARCH-046-WOOCOMMERCE-002
  - ARCH-046-BACKGROUND-003
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Accept durable authenticated Woo checkout WhatsApp consent changes

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Accept purpose-specific explicit Woo checkout GRANT/REVOKE evidence over the authenticated installation API and commit the current decision plus durable change receipt.

## Context

The API already authenticates Woo installation traffic and derives the Shop principal. The existing `woo.activity.v1` endpoint is capture-only and MUST NOT be overloaded with consent state.

## Scope

- Implement an API-owned strict `woo.whatsapp-consent.v1` HTTP contract and bounded POST route (proposed `/v1/woocommerce/whatsapp-consent`), documented with OpenAPI/tests.
- Require active Woo installation auth, `platform=WOOCOMMERCE`; derive `shopId` from principal, reject client shopId, validate eventId, checkoutKey, phone, decision, disclosureVersion, sourceRevision and bounds.
- Canonicalise number consistently with current recovery outbound-recipient handling; record one GRANT/REVOKE evidence transition and durable outbox change in the SAME PostgreSQL transaction.
- Return acknowledgement after DB commit; distinguish idempotent retry, stale revision, conflict, invalid contract, invalid installation and transient database failure. Use shared Node structured logger safely.

## Out of Scope

- No `/v1/woocommerce/activity` change, no recovery start, Shopify consent read/write or external WhatsApp send.
- No PHP/browser installation credentials, no extra Redis producer required on the synchronous write path.
- No consent inferred from checkout/order snapshots, marketing settings or absent Boolean.

## Requirements

- Accept an explicit affirmative action attested by the Woo plugin within a server-validated checkout session; the API MUST NOT claim it cryptographically proves phone ownership or accept anonymous browser calls.
- The event is checkout-scoped; sourceRevision strict ordering and per-event digest/conflict protection stop stale grant replay or cross-phone transfer.
- Incoming POST `shopId` is invalid; old installation/rotated credential fails, across-tenant reads/writes denied.
- API outage cannot create implied grant; no 2xx before durable commit.

## Work Items

- [ ] Define and document strict versioned OpenAPI/HTTP request, responses and error codes.
- [ ] Implement authenticated, bounded consent-write route + injected persistence.
- [ ] Test DB transaction, replay, grant→revoke→old grant, concurrency, revoked installation and tenant isolation.

## Interfaces / Contracts

Producer (later): WOOCOMMERCE-002. Owner/validator: moda_api. `POST /v1/woocommerce/whatsapp-consent`, version `woo.whatsapp-consent.v1`, request fields `{schemaVersion,eventId,sourceRevision,checkoutKey,recipientPhone,decision,disclosureVersion,occurredAt}` with **no shopId**; exact statuses/payload bounded and specified by this API task. State owner DATABASE-001.

## Dependencies

- `ARCH-046-DATABASE-001`

## Enables

- `ARCH-046-WOOCOMMERCE-002`
- `ARCH-046-BACKGROUND-003`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Valid connected-installation GRANT is durable and discoverable by exact DB key before 2xx, without creating a recovery.
- [ ] Same event/payload is idempotent; equal-revision conflict and stale grant after revoke cannot grant consent.
- [ ] Invalid/unauthenticated tenant, phone, purpose, disclosure or oversized payload fails closed.
- [ ] DB failure returns retryable error, never acknowledges non-durable approval.

## Validation

- [ ] API focused authentication/contract tests, disposable PostgreSQL ordering/idempotency tests.
- [ ] Repository declared lint/typecheck/build, error-path tests and `git diff --check`.

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
