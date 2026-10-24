---
id: ARCH-048-BACKGROUND-002
architecture_id: ARCH-048
title: Implement Woo order-reconciliation and terminal-state service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 34
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-048-BACKGROUND-006
- ARCH-035-BACKGROUND-002
- ARCH-035-API-019
enables:
- ARCH-048-BACKGROUND-005
created: '2026-10-23'
updated: '2026-10-24'
---

# ARCH-048-BACKGROUND-002 — Implement Woo order-reconciliation and terminal-state service

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **architect proposal**, Attempt 5, based on the 23 October 2026 snapshot and Attempt 2 task definitions. Defined but not materialised: no remote branch, worktree, implementation commit, review acceptance or release is claimed. Before execution re-read canonical dependencies and latest Architect Review in the developer workspace. The developer confirms `ARCH-046-BACKGROUND-004` complete after the snapshot; do not reopen it.

## Objective

Implement a dedicated `WooOrderReconciliationService` that applies authenticated checkout-linked order events to pending candidate state and existing `CheckoutRecovery` lifecycle, independently of BullMQ worker implementation, messaging and billing.

## Context

ARCH-035 order worker currently only validates/logs `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED`. BG006 defines the `WooCandidateManager` and coordination contracts. BG001 implements candidate lookup/cancel independently; this task consumes that interface through injection and implements the `WooObservedOrderStateReader` without waiting for the BG001 implementation. The orchestrator wires the real adapters in BG005.

## Scope

- Own `src/services/woocommerce-recovery/woo-order-reconciliation.service.ts` and tests. Own any bounded change needed to `src/services/pending-recovery-candidate/checkout-order-guard.service.ts` for Woo terminal coordination; consume the BG006-owned `WooCandidateManager` with fakes in focused tests; do not rewrite BG001 candidate scheduling.
- Expose `reconcileOrder(event: WooOrderCapture): Promise<WooOrderReconciliationOutcome>` with explicit `placed-suppressed`, `paid-terminal`, `cancelled-terminal`, `already-terminal`, `ignored-duplicate`, `ignored-stale`, `deferred-conflict` outcomes; no send or charge.
- Correlate strictly by authenticated `shopId` and exact `checkoutKey === order.checkoutKey` and recorded orderId; never derive identity from customer email/phone, or access another shop.
- On `ORDER_PLACED`, suppress abandoned-basket recovery for that checkout, including unpaid/on-hold; do not call it `PAID`. On `ORDER_PAID` or `ORDER_CANCELLED`, cancel pending candidate and guard against in-progress admission/sending. Older event replay cannot reverse known terminal decisions.
- Always lookup any existing PostgreSQL `CheckoutRecovery` even if the delayed BullMQ job has completed/disappeared; transition/reconcile existing recovery using approved status/history rules, and mark future automatic outreach ineligible. Preserve delivered initial message and accurate charged usage.
- For pre-recovery order-first events, maintain bounded checkout-scoped Redis terminal evidence/fencing using the same coordination contract as BG001. Retention/replay/freshness must account for configured delay and retries; do not claim permanent evidence without a durable row.
- Implement or reuse the BG006 `WooCheckoutCoordinator` and its checkout-scoped ownership/locking discipline without requiring the other business services to be implemented first. BG005 will compose the same lock adapter for all four services. If a lock lease expires while asynchronous work runs, fail closed or renew/fence; release only the owned lease.
- Treat paid, cancelled and placed order outcomes as distinct but all suppress initial abandoned-checkout outreach in v1; document precedence for repeated/late callbacks without changing an already delivered charge.

## Out of Scope

- No worker, recovery maturity, new recovery INSERT, phone/consent reader, Meta dispatch, refunds/billing policy or separate unpaid-order product.
- No new durable order table, query to WooCommerce, API route or Shopify-global guard rewrite.

## Requirements

- **Business boundary:** authoritative for *successfully received* order events only. BG001 owns candidate scheduling; BG002 owns terminal policy and existing-row transition. The two tasks depend on BG006 contract types rather than on each other; contract changes must return to the architect.
- Cancellation must be effective against both pending jobs and already-created recoveries; a missing candidate never short-circuits DB lookup.
- Known terminal events are monotonic for abandoned-outreach suppression; replay cannot reopen. For an event that never arrived, no positive paid-state assertion is possible.
- Reconciliation is idempotent: duplicate callbacks produce no duplicate status history, billing compensation or contact changes.
- For concurrent maturity and order processing, terminal/candidate/recovery checks must use shared narrow checkout scope, not per-shop/global serialization.

### Mandatory shared logging and failure propagation

- Use the existing process-level structured logger from `@modainteract/moda-interact-shared/logging` (inject `StructuredLogger`, optionally with a component `child(...)`). Follow `docs/observability/shared-logging.md`; do not create a service-local generic logger, custom JSON sink, `console.*` logger or a duplicate redactor. The shared logging export is already consumed by the ARCH-035 Woo capture workers; check the pinned installed package before coding and escalate a missing export rather than substituting a local logger.
- Emit stable, structured semantic events: `woocommerce.recovery.order.reconciled` (completed business outcome), `woocommerce.recovery.order.deferred` (expected conflict/defer), and `woocommerce.recovery.order.failed` (unexpected failure). Include only safe fields such as `shopId`, `eventId`, verified `orderId`, operation/stage, outcome or bounded reason, and retry attempt where available. Do not log raw `checkoutKey`/session tokens, customer details, basket payloads, credentials, authorization headers or unbounded provider errors. Preserve error cause/stack in the thrown error; sanitize logging fields as necessary.
- `placed-suppressed`, `paid-terminal`, `cancelled-terminal`, `already-terminal`, `ignored-duplicate`, `ignored-stale` and `deferred-conflict` are **normal domain results only when confirmed**. A thrown PostgreSQL, Redis, candidate-cancellation, status-history or lock/lease error is **not** an `ignored`/`deferred` result. On unexpected failure, emit bounded error context and **rethrow the original error**, so the caller's job fails/retries according to policy. Do not use empty `catch`, `catch`→success/defer, `.catch(() => undefined)`, unobserved async side effects or ignored rejected `Promise.allSettled` results.
- Cleanup in `finally` may release only an owned lock; any cleanup failure must remain visible and must not silently replace or erase the primary failure. Shared logger **sink** failure isolation is intentional and is not permission to suppress business exceptions.

## Work Items

- [ ] Implement injected service + outcome type. Reuse BG001 cancellation/index public interface; do not update BG001 service to add order business branches.
- [ ] Implement status matrix and checkout terminal guard with ordered/duplicate event handling; record existing recovery lifecycle when present.
- [ ] Add tests for order-first, paid before maturity, paid/cancelled after first send and removed queue job, placed-unpaid, duplicate, stale, wrong-shop, concurrent materialisation, >1-hour replay.
- [ ] Confirm Shopify order guard tests and billing records remain unchanged for old paid sends.
- [ ] Inject/use the canonical shared structured logger and emit sanitized order outcome/defer/failure records at the service boundary.
- [ ] Add failure-path tests proving Redis, database, candidate cancellation, history transition and lease failures reject `reconcileOrder` rather than returning successful or deferred outcomes.

## Interfaces / Contracts

**Owned capability interface (canonical definition in BG006):**

```ts
interface WooOrderReconciler {
  reconcileOrder(event: WooOrderCapture): Promise<WooOrderReconciliationOutcome>;
}
```

**Inputs:** existing parsed `WooOrderCapture` with `shopId` injected by authenticated API projection; `eventId`, `occurredAt`, `checkoutKey`, `order.orderId`, `order.status`, `order.checkoutKey`.

**Dependencies:** BG006 `WooCandidateManager` (BG001 implementation injected by BG005); shared `CheckoutOrderGuardService` checkout lock; PostgreSQL `CheckoutRecovery`, status history and current attempt records where needed; existing recovery lifecycle transitions.

**Outputs:** distinct order decision + controlled suppression/transition side effects; **never** an initial attempt, usage reservation or message. BG005 wires this into `woo-order-capture.worker.ts`.

**File boundary:** owned Woo order service, guard helper and own tests. Do not edit BG001's scheduling module, BG003/004 services, `src/workers/*` or `src/entrypoints/*`.

## Dependencies

- `ARCH-048-BACKGROUND-006`
- `ARCH-035-BACKGROUND-002`
- `ARCH-035-API-019`

## Enables

- `ARCH-048-BACKGROUND-005`

## Acceptance Criteria

- [ ] Known placed, paid or cancelled order suppresses new abandoned recovery even if arrival order is reversed.
- [ ] An order event after an already-sent recovery updates existing history and disables later automatic outreach even with no BullMQ job.
- [ ] Duplicates/stale events cannot emit repeated status transitions, refunds or change a different tenant.
- [ ] Unit/integration tests prove service via direct invocation before BG005 worker wiring.
- [ ] All unexpected order-reconciliation infrastructure exceptions propagate to the caller with original cause, remain observable through shared structured logs, and cannot acknowledge a failed operation as successfully reconciled.
- [ ] Expected terminal/duplicate/defer results are represented as typed outcomes (not exceptions); logs exclude sensitive data and use stable reason codes.

## Validation

- [ ] Unit status-matrix and guard tests, direct service integration using real Postgres and Redis with no-candidate existing recovery.
- [ ] Concurrent checkout/order replay and previous-one-hour-marker expiry tests; validate no billing changes.
- [ ] Shopify order guard regressions, repository-declared checks and `git diff --check`.
- [ ] Inject a fake/shared `StructuredLogger` and failing dependency adapters; assert expected semantic events, rejection propagation, no false success status and safe log fields.

## Stop Condition

After completing only the task's scoped service, tests, Acceptance Criteria and Validation, populate the Completion Report, set status to `review`, return control to `moda_architect`, and **STOP**. Do not wire a worker or start a dependent task. Record launcher-prepared parent and implementation dedicated worktree paths, physical isolation, synchronisation, submodule state and both task branch revisions in the Completion Report.

## Implementation Notes

BG002 depends on BG006 interfaces, not on a completed BG001 implementation. Unit tests use an injected fake WooCandidateManager; BG005 later supplies the accepted BG001 implementation. Unexpected shared guard or candidate changes require architect review, not opportunistic edits.

- Use `/moda-task` launcher preparation and the actual task worktrees on the developer's machine; a portable ZIP is not an execution claim or Git baseline.
- Respect service/file ownership and cross-repository boundaries in this task and the parent architecture. Do not modify `docs/decisions/**/_index.md` before explicit architect session closure.
- Apply the mandatory shared structured-logging and exception-propagation contract in Requirements; inspect the repository `package.json`, use existing domain infrastructure, run only relevant declared checks and record exact evidence (including checks that cannot run).
- All checkout/session/phone/order logging must exclude raw PII, secrets, session tokens and full basket data; record bounded reason codes and structured correlation IDs only.

## Completion Report

### Status

Not Started — portable task definition only.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run by repository implementer; no developer repository worktree or remote is accessible from this review package.

### Deviations

None.

### Assumptions

Latest uploaded ZIP and proposed task files may lag active developer branches. Latest dependency state must be checked before materialisation. The developer reports `ARCH-046-BACKGROUND-004` complete; reuse accepted implementation without editing its task definition.

### Unresolved Issues

Confirm actual approved cross-task dependency versions before implementation; raise missing canonical shared contracts or unimplementable business guarantees to the architect rather than inventing substitutes.

### Architectural Concerns

The outbound-only event design cannot identify Woo updates/payments whose events never arrive; this limitation must remain explicit and Woo outbound disabled until reviewed.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
