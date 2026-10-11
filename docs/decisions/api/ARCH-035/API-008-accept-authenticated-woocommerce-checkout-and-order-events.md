---
id: ARCH-035-API-008
architecture_id: ARCH-035
title: Accept durable Woo checkout and order events
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-SHARED-001
  - ARCH-035-DATABASE-001
enables:
  - ARCH-035-BACKGROUND-001
  - ARCH-035-WOOCOMMERCE-007
  - ARCH-035-WOOCOMMERCE-008
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-008: Accept durable Woo checkout and order events

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Extend Moda API with the authenticated, bounded Woo plugin-to-API commerce-event ingress, durable acceptance and asynchronous processing handoff.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Files:** new `src/woocommerce/activity/{routes,ingest.service,claim.service,contract}.ts`, bounded Jest/tsx unit
and Postgres tests and `openapi/woocommerce-activity-v1.yaml`; wire once into
`src/woocommerce/installation/routes.ts` (thin route dispatch only) and `src/index.ts`. Use the exact published
Shared `woo.activity.v1` schema, and accepted DATABASE-001 `WooCommerceActivityReceipt`/`WooCommerceCheckoutLineage`;
no additional migration.

**Endpoint:** `POST /v1/woocommerce/activity` with an exact Shared v1 body and `Authorization: Bearer <installation
credential>`, `X-Moda-Installation-Id` existing header; no query string, no WordPress REST nonce (server-to-server).
Require active verified Woo Shop/installation and current credential version **before any body processing**. Reject
16-KiB+ payload, unknown event field, foreign origin in checkoutUrl and invalid consent/phone. Return 202
`{schemaVersion:1,receiptId,acceptance:"RECORDED"}` on first event and 200 `{...,acceptance:"REPLAY"}` for same
`(shopId,eventId,digest)`; 409 `activity_event_conflict` for same eventId/different digest. Never accept shopId in
request.

**Transaction:** lock Shop then `(shopId,checkoutKey)` lineage; insert receipt (`PENDING`, digest of canonical
Shared-normalized body) and upsert lineage in one serializable/retry-safe transaction. When order event arrives,
establish terminalState and terminalOrderId before 202 response; do not allow a later checkout upsert to downgrade
the terminal. `lastRevision` is **acceptance** high-water; `lastAppliedRevision` is owned by Background-001 and remains unchanged on HTTP ingress; stale lower-revision snapshots remain recorded but will be IGNORED
downstream. For ORDER_PAID, irrevocably fence the lineage. If persistence fails, return failure and do not
acknowledge; Redis/BullMQ publication, if used, is an **optional hint** after commit and the Background DB claim loop
must pick up rows on loss. Do not create CheckoutRecovery, refund, usage credit or WhatsApp outbound in this HTTP
handler.

**Negative matrix:** active vs revoked/rotated installation; forged shop in body; same eventId replay/changed digest;
cross-Shop equal checkoutKey; order-before-checkout; two concurrent paid events; order after abandoned checkout;
invalid URL/PII/bytes; Redis unavailable; DB commit failure. Prove a pending durable receipt remains discoverable
with no Redis queue. Log eventId/kind/shopId/status/latency only, never PII or snapshot.

## High-level scope (non-authoritative summary)

- Authenticate active installation credential before parsing/processing; derive shopId only from principal and strict Shared v1 envelope.
- Persist idempotent event receipts and order correlation before acknowledging; enqueue/reconcile via existing approved background mechanism with retry-safe outbox/claim semantics.
- Reject foreign identities, invalid transitions, oversized payloads, stale credentials and malformed PII; log only safe event IDs/types and outcomes.
- Do not instantiate CheckoutRecovery or send WhatsApp from the HTTP request, and do not expose the commerce ingest route in browser/WordPress JS.

## Out of Scope

- Unrelated Shopify or Woo Billing feature changes; changing another repository in this task.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-api`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-SHARED-001` must be architect-accepted Complete before this task is claimed.
- `ARCH-035-DATABASE-001` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-BACKGROUND-001`
- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-035-WOOCOMMERCE-008`

## Acceptance Criteria

- [ ] Auth/reconnect/revoke, replay/out-of-order, bad payload and concurrent duplicate integration tests.
- [ ] Durable receive-before-ack, queue failure/retry and tenant-boundary proofs.
- [ ] No Shopify ingress or billing API regression.
- [ ] Scope stays within `moda-interact-api` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect on implementation submission.
