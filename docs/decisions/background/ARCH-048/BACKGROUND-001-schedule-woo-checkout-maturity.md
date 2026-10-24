---
id: ARCH-048-BACKGROUND-001
architecture_id: ARCH-048
title: Implement Woo checkout-activity and candidate-scheduling service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-048-BACKGROUND-006
- ARCH-035-BACKGROUND-001
- ARCH-035-API-008
enables:
- ARCH-048-BACKGROUND-005
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-BACKGROUND-001 — Implement Woo checkout-activity and candidate-scheduling service

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **architect proposal**, Attempt 5, based on the 23 October 2026 snapshot and Attempt 2 task definitions. Defined but not materialised: no remote branch, worktree, implementation commit, review acceptance or release is claimed. Before execution re-read canonical dependencies and latest Architect Review in the developer workspace. The developer confirms `ARCH-046-BACKGROUND-004` complete after the snapshot; do not reopen it.

## Objective

Implement an independently testable `WooCheckoutActivityService` that reconciles an authenticated Woo checkout event against the existing durable recovery and order-guard state, then schedules, reschedules or cancels a pending maturity candidate **without touching any BullMQ worker or dispatching a message**.

## Context

The current `woo-checkout-capture.worker.ts` only validates/logs events. Shopify's existing `PendingRecoveryCandidateService` is a reusable queue/index mechanism but its event adapters and maturity consumer assume Shopify. ARCH-048-BACKGROUND-006 defines the canonical Background-local `WooPendingCandidate`, cancellation/guard interfaces and typed outcomes before this service is implemented. The Woo service implements those contracts, without owning worker orchestration. Absence of a candidate job is not absence of a `CheckoutRecovery`.

## Scope

- Own `src/services/woocommerce-recovery/woo-checkout-activity.service.ts` (or equivalently named cohesive module), focused unit/integration tests, and the smallest required **candidate lifecycle/index and internal Woo candidate type** extensions. The internal candidate must carry an explicit `source: "woocommerce"`; existing jobs without a source retain their current Shopify meaning. No wire/API schema change.
- Expose an injected `handleCheckout(event: WooCheckoutCapture): Promise<WooCheckoutActivityOutcome>` service method, with typed outcomes for `scheduled`, `rescheduled`, `cancelled-empty`, `existing-recovery`, `ignored-terminal`, `ignored-stale`, `deferred-ambiguous`, and `not-eligible`. Outcomes are service results, not instructions to send WhatsApp.
- Resolve `shopId` solely from the already authenticated queue event and confirm Woo installation/platform execution eligibility. Use `(shopId, checkoutKey)` as the immutable checkout lineage; resolve shopDomain from the trusted Shop, never the untrusted event.
- Under checkout-scoped coordination, query `CheckoutRecovery` by shop and checkout key **whether or not a BullMQ candidate is present**. If a first recovery exists, reconcile permitted external activity metadata but never create a new first-generation candidate or attempt; completed/removed BullMQ job is irrelevant.
- For no existing recovery, use existing candidate scheduling/index APIs and merchant abandonment delay. Explicit `items: []` cancels; missing items (including 51+ line snapshot omission) are unknown, never interpreted as empty or admissible.
- Capture the minimum bounded **latest successfully received** Woo event evidence required at maturity (checkout currency/total, bounded items, exact contact and source event identity) in the existing approved transient Redis/BullMQ candidate facilities, with expiration covering maturity + retries/replay. Do not add a table or log customer PII.
- Dedupe stable eventId, preserve event-time watermark and immutable terminal precedence; conflicting same-second versions cannot be ordered reliably and must suspend/fail closed rather than select a preferred basket.
- Consume the `WooObservedOrderStateReader` and checkout coordination interface defined by BG006 through dependency injection. BG002 owns the concrete terminal order policy; do not implement a competing terminal state store. Use existing checkout-scoped locking; do not independently rewrite terminal guard internals.

## Out of Scope

- No worker imports, worker `process` callbacks, queue/entrypoint registration, `CheckoutRecovery` INSERT, WhatsApp/attempt/billing code or merchant notices. All worker wiring belongs to BG005.
- No new public WordPress/Moda API route, guest-session verification or Background→Woo HTTP request. No rewrite of Shopify checkout service.

## Requirements

- **Business boundary:** own scheduling + candidate evidence only. Treat injected order guard and DB repository as dependencies; never decide consent, charge or send.
- Existing first recovery wins even if a job is delayed/active/missing. No second initial recovery for the same checkout key merely because a new hook fires.
- Output candidate must be explicitly attributable to Woo without prefix guessing. A legacy Shopify candidate must retain original shape/processing.
- Lock-protected operations must not permit a delayed duplicate to resurrect a terminal checkout; unresolved ordering fails closed.
- Don’t claim Woo source-state verification if the event never reached Moda; retain event-only limitation.

## Work Items

- [ ] Implement test-injected WooCheckoutActivityService and typed outcomes; add at most the local candidate metadata/evidence required for later maturity.
- [ ] Add missing-job + existing MESSAGE_SENT recovery path, and candidate-present + existing recovery path; assert no scheduling in either.
- [ ] Add tests: new checkout, update/reschedule, empty, refill, duplicate event, out-of-order, same-second conflict, oversized/missing items, order-first terminal fence, independent tenants and concurrent processing.
- [ ] Confirm Shopify default legacy candidate shape and existing index scheduling still work.

## Interfaces / Contracts

**Owned capability interface (declared only in BG006; implemented by this task; not published Shared):**

```ts
interface WooCheckoutActivityHandler {
  handleCheckout(event: WooCheckoutCapture): Promise<WooCheckoutActivityOutcome>;
}
// WooCheckoutActivityOutcome is a discriminated union of named domain outcomes.
```

**Inputs:** existing strictly parsed `WooCheckoutCapture` from ARCH-035 capture job; `shopId` from trusted API queue projection, `checkoutKey` used as recovery `checkoutToken`, `eventId`, `occurredAt`, bounded checkout snapshot.

**Outputs:** scheduling/result only; a `WooPendingCandidate` carries `source: "woocommerce"`, shop+checkout identity, activity watermark, bounded evidence and timeout/retry TTL. Do not construct an abandoned-checkout URL that was not captured.

**Dependencies consumed:** existing `PendingRecoveryCandidateLifecycleService`, `PendingRecoveryCandidateIndexStore`, `CheckoutRecovery` lookup, and BG006-defined `WooObservedOrderStateReader`, `WooCheckoutCoordinator`. BG002 supplies the concrete terminal implementation only when BG005 composes the accepted services. BG001 supplies the BG006-defined `WooCandidateManager` to order reconciliation at composition. **BG005 alone imports this service into workers.**

**File-boundary rule:** This task may change Woo service module, transient candidate type/index/lifecycle helpers and its own tests, but may not redefine the BG006 contract module. It must not change `src/workers/*`, `src/entrypoints/*`, `recovery-initiation.service.ts` or order-guard policy implementation; BG002/BG003/BG004/BG005 own those.

## Dependencies

- `ARCH-048-BACKGROUND-006`
- `ARCH-035-BACKGROUND-001`
- `ARCH-035-API-008`

## Enables

- `ARCH-048-BACKGROUND-005`

## Acceptance Criteria

- [ ] Under no-candidate, existing `CheckoutRecovery` lookup prevents candidate creation for all existing first-send states; race recheck is under checkout-scoped guard.
- [ ] Update reschedules one delayed candidate; empty event cancels; missing/oversized basket evidence and conflicting timestamps cannot become send-eligible.
- [ ] Woo candidate is visibly typed and routed by source; no Shopify candidate/regression change.
- [ ] Task is complete when business service and tests pass even though existing Woo capture worker remains capture-only until BG005.

## Validation

- [ ] Focused service unit tests with injected queue/DB/order guard and deterministic clocks; no unrelated messaging/consent mocks.
- [ ] PostgreSQL + Redis lifecycle tests including removed job/existing recovery and same-lineage concurrency.
- [ ] Existing Shopify candidate index tests, repository-declared typecheck/lint/tests for touched modules and `git diff --check`.

## Stop Condition

After completing only the task's scoped service, tests, Acceptance Criteria and Validation, populate the Completion Report, set status to `review`, return control to `moda_architect`, and **STOP**. Do not wire a worker or start a dependent task. Record launcher-prepared parent and implementation dedicated worktree paths, physical isolation, synchronisation, submodule state and both task branch revisions in the Completion Report.

## Implementation Notes

All input/output types must have reasoned explicit outcomes; no boolean `success` result that hides scheduling vs suppression. Use bounded retention, and explain retention calculations in Completion Report.

- Use `/moda-task` launcher preparation and the actual task worktrees on the developer's machine; a portable ZIP is not an execution claim or Git baseline.
- Respect service/file ownership and cross-repository boundaries in this task and the parent architecture. Do not modify `docs/decisions/**/_index.md` before explicit architect session closure.
- Reuse approved shared logging and existing domain infrastructure; inspect actual repository `package.json` and perform only relevant declared checks. Record exact evidence and any impossible test rather than inventing a pass.
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
