---
id: ARCH-048-BACKGROUND-002
architecture_id: ARCH-048
title: Implement Woo order-reconciliation and terminal-state service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 34
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-048-BACKGROUND-006
- ARCH-035-BACKGROUND-002
- ARCH-035-API-019
enables:
- ARCH-048-BACKGROUND-005
created: '2026-10-23'
updated: 2026-10-24
---

# ARCH-048-BACKGROUND-002 — Implement Woo order-reconciliation and terminal-state service

## Developer Ownership Amendment

On 2026-10-24, `/moda_developer_create ARCH-048-BACKGROUND-002` was invoked
while this task was ready and agent-owned. This is an explicit developer
takeover. `execution_mode` and `completion_mode` are now `developer`;
`assigned_agent: moda_background`, repository ownership, dependencies, scope
and acceptance criteria are unchanged. The task remains at Attempt 0 until
canonical preparation claims Attempt 1.

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Materialised on parent branch `task/ARCH-048-BACKGROUND-002` from the architect proposal. No implementation claim existed before canonical preparation. Before execution re-read canonical dependencies and latest Architect Review in the developer workspace. The developer confirms `ARCH-046-BACKGROUND-004` complete after the snapshot; do not reopen it.

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

- [x] Implement injected service + outcome type. Reuse BG001 cancellation/index public interface; do not update BG001 service to add order business branches.
- [x] Implement status matrix and checkout terminal guard with ordered/duplicate event handling; record existing recovery lifecycle when present.
- [x] Add tests for order-first, paid before maturity, paid/cancelled after first send and removed queue job, placed-unpaid, duplicate, stale, wrong-shop, concurrent materialisation, >1-hour replay.
- [x] Confirm Shopify order guard tests and billing records remain unchanged for old paid sends.
- [x] Inject/use the canonical shared structured logger and emit sanitized order outcome/defer/failure records at the service boundary.
- [x] Add failure-path tests proving Redis, database, candidate cancellation, history transition and lease failures reject `reconcileOrder` rather than returning successful or deferred outcomes.

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

- [x] Known placed, paid or cancelled order suppresses new abandoned recovery even if arrival order is reversed.
- [x] An order event after an already-sent recovery updates existing history and disables later automatic outreach even with no BullMQ job.
- [x] Duplicates/stale events cannot emit repeated status transitions, refunds or change a different tenant.
- [x] Unit/integration tests prove service via direct invocation before BG005 worker wiring.
- [x] All unexpected order-reconciliation infrastructure exceptions propagate to the caller with original cause, remain observable through shared structured logs, and cannot acknowledge a failed operation as successfully reconciled.
- [x] Expected terminal/duplicate/defer results are represented as typed outcomes (not exceptions); logs exclude sensitive data and use stable reason codes.

## Validation

- [x] Unit status-matrix and guard tests, direct service integration using real Postgres and Redis with no-candidate existing recovery.
- [x] Concurrent checkout/order replay and previous-one-hour-marker expiry tests; validate no billing changes.
- [x] Shopify order guard regressions, repository-declared checks and `git diff --check`.
- [x] Inject a fake/shared `StructuredLogger` and failing dependency adapters; assert expected semantic events, rejection propagation, no false success status and safe log fields.

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

Complete — developer-owned **Attempt 1**, claimed at `2026-10-24T01:16:28Z`. Implementation was committed and published on `task/ARCH-048-BACKGROUND-002` at **`9f4e088`** (`feat(ARCH-048-BACKGROUND-002): reconcile WooCommerce order terminal states`). The review passed and the developer explicitly completed the task without merging to `main`. `completion_mode: developer` remains unchanged.

### Files Changed

Implementation repository `moda-interact-background`:

- `src/services/woocommerce-recovery/woo-order-reconciliation.service.ts` — new injected reconciliation service, Redis terminal observation store and coordinator adapter.
- `src/services/pending-recovery-candidate/checkout-order-guard.service.ts` — additive, ownership-checked renewable Woo checkout lease guard; existing Shopify guard retained.
- `tests/unit/services/woocommerce-recovery/woo-order-reconciliation.service.test.ts` — order-state matrix, tenancy, idempotency, lifecycle, shared-logger and failure-path tests.
- `tests/unit/services/woocommerce-recovery/woo-checkout-lease-guard.service.test.ts` — lock ownership, renewal, long callbacks and failure tests.
- `tests/integration/woo-order-reconciliation.integration.test.ts` — direct service validation with disposable PostgreSQL and Redis.

This review submission additionally updates **only this parent-workspace task file**. No `_index.md`, worker, BG001/BG003/BG004 business service, billing implementation or database schema changes are included.

### Work Completed

- Implemented the BG006 `WooOrderReconciler` / `WooObservedOrderStateReader` interfaces using injected `WooCandidateManager`, `WooCheckoutCoordinator`, PostgreSQL, Redis and `StructuredLogger`. BG005 remains the composition/worker owner.
- Processed distinct `ORDER_PLACED`, `ORDER_PAID`, and `ORDER_CANCELLED` outcomes with strict verified `shopId` + matching checkout keys and recorded order identity; refused mismatched or conflicting identities and stale/duplicate demotions.
- Persisted checkout-scoped terminal evidence in Redis with a bounded **nine-day** retention window (maximum seven-day configured recovery delay plus 48 hours of retries/replays). Cancellation of pending candidates does **not** bypass the independent PostgreSQL recovery lookup.
- Reconciled existing `CheckoutRecovery` rows using compare-and-set status changes and one status-history record, cancelling only unsent attempts. Kept already-sent outbound identity and prior charged usage intact; repeated callbacks do not repeat transitions or refunds.
- Added a Woo-specific checkout-scoped lease that renews while work runs, uses atomic ownership-checked Redis operations and surfaces acquisition, renewal, release or primary-operation errors. Left the legacy Shopify guard path intact.
- Emitted `woocommerce.recovery.order.reconciled`, `.deferred`, and `.failed` through the canonical shared structured logger. Tested error propagation and bounded, non-sensitive log fields.
- Corrected unit-test fake lookup snapshots and a disposable integration fixture requiring a real sent outbound message linked to the recovery conversation; the final validation rerun passed. Patch-artifact corrections did **not** represent additional task execution claims: this remains developer Attempt 1.

### Validation Results

Evidence: developer terminal captures from **2026-10-24**, including `typescript(20261024-013645)` (final passing suite) and `typescript(20261024-013903)` (commit/push). Results are reported from the developer's worktree, **not rerun inside this portable review environment**.

| Check | Developer command / evidence | Result |
| --- | --- | --- |
| Focused unit and existing guard regression tests | `npx vitest run tests/unit/services/woocommerce-recovery/ tests/unit/services/pending-recovery-candidate/checkout-order-guard.service.test.ts` | **3 test files; 40/40 passed** |
| Real PostgreSQL/Redis integration | `npm run test:integration -- tests/integration/woo-order-reconciliation.integration.test.ts` | **2/2 passed** (order-first evidence TTL; already-delivered, no-candidate, concurrent reconciliation) |
| Repository build | `npm run build` | **Passed**; Prisma Client v6.19.3 generated, TypeScript compiled without reported error |
| Working-tree whitespace | `git diff --check` | **Passed** (no output) |
| Staged whitespace | `git diff --cached --check` | **Passed** (no output before commit) |
| Implementation publication | `git commit` then `git push -u origin task/ARCH-048-BACKGROUND-002` | **Passed**; commit `9f4e088`, new remote branch and upstream confirmed |

Prior validation attempts identified test-harness issues (mutable test fake and invalid sent-attempt fixture); the developer's **final** run passed. No additional runtime defects are established by the supplied final logs.

### Worktree, Synchronisation and Branch Evidence

- Canonical **parent** dedicated worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-002` (identified by the task archive helper on 2026-10-24).
- Canonical **implementation** dedicated worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-002` (developer shell transcript and archive helper).
- Implementation branch: `task/ARCH-048-BACKGROUND-002`; task-specific physical worktree and published commit `9f4e088` are supported by the provided transcript.
- Parent task branch: `task/ARCH-048-BACKGROUND-002`; review commit `2e2363c2` is published and this explicit completion decision is being published on the same parent branch.
- Preparation evidence was verified during review using the canonical route and dedicated parent/implementation worktrees; both branches were clean and the implementation was published.

### Deviations

None from the assigned runtime/file scope. BG005 worker wiring and other Woo recovery services remain separate tasks.

### Assumptions

- The incoming `WooOrderCapture` is parsed and tenant-authenticated by the existing upstream Woo API/capture boundary; BG002 does not authenticate network requests or query WooCommerce.
- BG005 will inject the real BG001 `WooCandidateManager` and one shared checkout coordinator for maturity, reconciliation, admission and initial outreach; this task validates its interface with fakes and direct service invocation.
- Order observations are authoritative for events successfully received; absence of an event is not proof that an order is unpaid.

### Unresolved Issues

- No remaining failures in the **reported focused tests**. Worker composition and end-to-end ingress validation are explicitly deferred to BG005 and the ARCH-048 system-test task.
- Start-of-attempt synchronization and recursive submodule-preparation evidence were not contained in the supplied archive/log and require verification from the developer's canonical task environment before architect acceptance.

### Architectural Concerns

- Bounded Redis-only order-first evidence is **not permanent**; no recovery can be prevented on the basis of an event Moda never received, and a pre-recovery marker is only guaranteed during its defined retention horizon. This constraint remains part of ARCH-048 and is not remedied by inventing a new durable order table.
- This task intentionally does **not** wire order workers or enable outbound Woo recovery. BG005 must compose the same checkout coordination and terminal reader with BG001/BG003/BG004 before integrated operation.

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

## Developer Self-Review Accepted

Review completed on 2026-10-24 against Attempt 1 and implementation commit `9f4e088`.

- The implementation branch is clean, committed and published at `9f4e088`.
- The parent task branch is clean and the review record is durable.
- Focused validation passed: 40/40 unit and guard tests across 3 files, repository TypeScript check, touched-file ESLint, and 2/2 PostgreSQL/Redis integration tests.
- The implementation remains within BG002 scope: no worker or entrypoint wiring, new recovery insertion, billing/refund policy, network API, or database schema changes.
- Work Items and Acceptance Criteria are complete for this attempt. Shared structured logging, failure propagation, terminal fencing, and the event-received limitation are covered in the implementation and tests.

Developer self-review passed before the explicit completion decision recorded below.

## Developer Completion Decision

On 2026-10-24, the developer explicitly completed ARCH-048-BACKGROUND-002 after the durable passing self-review. Attempt 1 is accepted without increment. The implementation and parent task records are committed and published; no merge to `main` is required. Downstream eligibility is recalculated from this completion.
