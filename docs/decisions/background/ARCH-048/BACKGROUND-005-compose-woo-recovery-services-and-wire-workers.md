---
id: ARCH-048-BACKGROUND-005
architecture_id: ARCH-048
title: Compose Woo recovery services and wire event/maturity/outbound workers
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 54
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-048-BACKGROUND-001
- ARCH-048-BACKGROUND-002
- ARCH-048-BACKGROUND-003
- ARCH-048-BACKGROUND-004
- ARCH-046-BACKGROUND-002
- ARCH-046-BACKGROUND-004
enables:
- ARCH-048-SYSTEM-TEST-001
created: '2026-10-23'
updated: '2026-10-25'
---

# ARCH-048-BACKGROUND-005 — Compose Woo recovery services and wire event/maturity/outbound workers

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **architect proposal**, Attempt 5, based on the 23 October 2026 snapshot and Attempt 2 task definitions. Defined but not materialised: no remote branch, worktree, implementation commit, review acceptance or release is claimed. Before execution re-read canonical dependencies and latest Architect Review in the developer workspace. In the 2026-10-25 13:36 snapshot `ARCH-046-BACKGROUND-004` is **blocked** and awaiting its own approved initial-send final guard; it is NOT Complete. BG005 must not start until that task and ARCH-046-BG002 have both been accepted Complete.

## Objective

Implement one thin `WooRecoveryOrchestratorService` and the **only ARCH-048 Background worker/composition wiring**, consuming the BG006 canonical interfaces implemented by the four accepted Woo business services while preserving the existing Shopify recovery path unchanged.

## Context

BG006 first freezes cross-service interfaces; BG001–BG004 independently implement domain services without editing workers. Woo producer enhancements have their own execution paths and are required by end-to-end system testing, not by this wiring task. Today both Woo capture workers are capture-only, and `pending-recovery-candidate.worker.ts` routes all candidates through Shopify-oriented `checkoutRecoveryService.materializeMaturedCandidate`. This task is required to make Woo work at runtime, prevent Woo jobs entering Shopify lookup/materialisation, and keep distinct service responsibilities independently reviewable.

## Scope

- Own `src/services/woocommerce-recovery/woo-recovery-orchestrator.service.ts`, dependency-composition/registration, and the minimal required modifications to `src/workers/woo-checkout-capture.worker.ts`, `woo-order-capture.worker.ts`, `pending-recovery-candidate.worker.ts`, and actual Background entrypoint(s). BG001–BG004 service files are read-only consumers for this task except architect-approved narrow interface defect fixes.
- Implement an orchestration facade with `onCheckout(event)`, `onOrder(event)`, `onCandidateMatured(candidate, jobContext)` and `onInitialDispatch(id)` (or equivalent existing outbound processor integration). Each method delegates to exactly the appropriate domain service; no embedded maturity, order policy, DB INSERT, consent or credit business logic.
- Keep authentication/digest/schema validation at the existing capture-worker boundary. Only after a strictly parsed `WooCheckoutCapture`/`WooOrderCapture` reaches the orchestrator should the worker acknowledge business processing; do not acknowledge if domain processing failed and needs BullMQ retry.
- Route pending-recovery candidates using an **explicit internal Woo source discriminator** populated by BG001. `source === "woocommerce"` calls Woo admission; absent source remains the backward-compatible existing Shopify path; unknown source fails safely. Verify shop platform/tenant, do not infer routing merely from opaque checkoutKey prefixes or shopDomain.
- On a mature Woo candidate, call BG003; for `created { recoveryId }`, enqueue initial outreach through BG004. For `already-exists { recoveryId, status }`, invoke **only** BG004's idempotent eligible-pending recovery/reenqueue path when a prior row INSERT succeeded but scheduling failed; BG004 must prove there is no previously sent or in-flight initial attempt. Denied/deferred/superseded cases never enqueue. This handles DB-insert → enqueue crash/retry without a new table.
- Wire BG002 on Woo order events so known terminal outcomes cancel pending candidates **and** reconcile durable recoveries even when no candidate job exists. Wire BG001 on checkout updates; no worker may contain copied business branching.
- Integrate accepted ARCH-046-BACKGROUND-002 via its `WooDeniedAdmissionNotifier` factory and inject it into BG003 `onDeniedAdmission`. Inject the **concrete accepted** ARCH-046-BACKGROUND-004 `WooGuardedInitialSender` into `createWooRecoveryOutreachService`; do not substitute the generic outbound `sendTemplate` or an unguarded preflight. At this snapshot BG004 is not implemented/accepted, so this is a hard integration dependency. Preserve the merged shared merchant-notice writer and do not duplicate it.
- Preserve existing job cleanup/retry semantics and candidate index on success/defer/failure, including distinct Woo vs Shopify materialisation results; do not silently remove a retryable Woo candidate. Ensure the default-off Woo send gate cannot be bypassed by alternative worker/resume paths.
- Build integration tests using actual worker entrypoints, test-injected service interfaces and Redis/Postgres fixtures for routing, failure, idempotency and source isolation. No unrelated worker rewrite.

## Out of Scope

- No implementation of checkout/order/admission/outreach business rules, new queue schema/endpoint, WordPress remote read, new SQL schema, new sending/billing system or Shopify refactor.
- No changing business-service code to hide a missing interface without architect review; no domain `_index.md` updates.

## Requirements

- **Composition only.** Orchestrator chooses and coordinates existing services; each service owns its own state transitions and validation.
- All Woo capture events are passed to appropriate service only after existing validation. A failure must follow existing bounded BullMQ retry/dead-letter semantics.
- Existing unmarked Shopify pending candidates remain processed by their original materialiser, including jobs already present during rolling deployment. Marked Woo candidates must not reach Shopify provider lookup.
- Exactly one Woo first recovery and at most one initial message; an already-created recovery from an earlier maturity execution must still be recoverable by existing retry/resume handling (do not issue a second first send).
- Default-off sending and consent/STOP/terminal/follow-up gates are honored at every runtime entrypoint.
- No new DB table, exposed merchant endpoint or Background↔Moda API call.

### Mandatory shared logging and BullMQ exception propagation

- Use the current process logger from `@modainteract/moda-interact-shared/logging` (create once for the worker process or inject the existing `StructuredLogger`; use `.child(...)` for safe component/queue context). Reuse the approved logging envelope, redaction and `Error` handling; no new generic logger, `console.*` logger, custom serializer or duplicate OpenTelemetry HTTP/BullMQ metric.
- Log structured orchestration/worker outcomes with stable event names: `woocommerce.recovery.job.started`, `woocommerce.recovery.job.completed`, `woocommerce.recovery.job.deferred` and `woocommerce.recovery.job.failed`. Include bounded `jobId`, `eventId`, `shopId`, queue, stage, source, attempt count and outcome/reason; never raw checkout/session key, customer information, message body, full job payload, secrets or unsafe error strings. Do not log success when work failed; avoid unnecessary duplicate failure logs between the service and job boundaries.
- Every BullMQ worker callback must `await` the orchestrator and all required async effects. When BG001–BG004, the consent notice hook, or a queue/DB dependency **throws**, log failure context (at the appropriate boundary) and **rethrow the original error** so BullMQ marks the job failed and applies its existing bounded retry/failure handling. No `catch`→`return`, `catch`→`deferred`, `.catch(() => {})`, fire-and-forget side effects or silently ignored `Promise.allSettled` rejections. Preserve lock ownership and cleanup without masking primary errors.
- Map only known **business** results to completed/deferred handling. `failed-retryable` must lead to an explicit BullMQ retry/failure signal or a proven existing durable retry mechanism—not a successful job acknowledgement. Invalid/unknown-source jobs must fail visibly with an appropriate typed error rather than disappearing; protect the legacy Shopify route. The intentional sink-failure isolation in the shared logging package is not an exception-swallowing policy for orchestrator operations.

## Work Items

- [ ] Compose four already accepted services using the unchanged BG006 Background-local interface types through a small orchestrator, one code module and explicit constructor/factory injection; reuse existing deployed worker entrypoints.
- [ ] Wire checkout capture worker to BG001, order capture worker to BG002, pending candidate worker to BG003→BG004 routing with explicit Woo source marker and Shopify legacy fallback.
- [ ] Wire existing initial outbound processor to ARCH-048 BG004; compose the accepted ARCH-046-BG004 `WooGuardedInitialSender`, and inject ARCH-046-BG002 notice callback at BG003 admission. Reject missing guard dependencies (no live or test fallback to generic unguarded sending). Retain correct queue ack/failure/cleanup behaviour.
- [ ] Add tests for Woo vs Shopify routing, nil job+existing recovery, checkout after first send, order after first send, duplicate/failed job, DB insert→enqueue interruption, disabled Woo send and no Woo follow-ups.
- [ ] Run existing Shopify worker/maturity regressions and entrypoint startup/build checks; record exact changed files per orchestration boundary.
- [ ] Wire the shared structured logger into the orchestrator and each affected worker path; record safe started/completed/deferred/failed events without duplicate business rule logging.
- [ ] Add worker-level fault-injection tests for rejected BG001, BG002, BG003, BG004, merchant-notice, Redis and enqueue dependencies; confirm BullMQ failure/retry rather than silent success or candidate deletion.

## Interfaces / Contracts

**Optional worker-facing orchestrator interface (use only when needed for worker/test injection; concrete class: `WooRecoveryOrchestratorService`):**

```ts
interface WooRecoveryOrchestrator {
  onCheckout(event: WooCheckoutCapture): Promise<WooCheckoutActivityOutcome>;
  onOrder(event: WooOrderCapture): Promise<WooOrderReconciliationOutcome>;
  onCandidateMatured(candidate: WooPendingCandidate, context: { jobId?: string }): Promise<WooAdmissionOutcome>;
  onInitialDispatch(recoveryId: string): Promise<WooOutreachDispatchOutcome>;
}
```

`WooPendingCandidate.source === "woocommerce"` is required; unmarked legacy candidates are Shopify and use their unchanged existing worker flow. The orchestrator calls `evaluateMatured` on its injected `WooRecoveryAdmissionEvaluator`; `created` enqueues through BG004. An `already-exists` result may recover a previously missed initial enqueue **only** via BG004's idempotent still-pending recovery/attempt guard. A `MESSAGE_SENT`, in-flight, terminal or otherwise ineligible recovery must not enqueue another initial attempt. If existing attempt/resume infrastructure handles dispatch, `onInitialDispatch` may be an adapter rather than a new worker/job.

**Worker ownership (exclusive for ARCH-048):** `woo-checkout-capture.worker.ts`, `woo-order-capture.worker.ts`, `pending-recovery-candidate.worker.ts`, necessary worker composition/entrypoint registration and worker integration tests. No edits to BG001–BG004 business rules or merchant plugin/API runtime beyond their separately accepted tasks.

**Observability:** Use shared structured logger and existing BullMQ instrumentation. Emit bounded `stage`, `shopId`, redacted checkout reference, `eventId`, `outcome` and retry count; no PII or full payloads. Correctly distinguish an undelivered event limitation from delivery/job failures.

## Dependencies

- `ARCH-048-BACKGROUND-001`
- `ARCH-048-BACKGROUND-002`
- `ARCH-048-BACKGROUND-003`
- `ARCH-048-BACKGROUND-004`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`

## Enables

- `ARCH-048-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Woo checkout/order capture workers invoke the new orchestrator, and no business decision is implemented inside workers.
- [ ] Woo maturity candidates route exclusively to Woo admission and initial-send pipeline; existing Shopify/legacy candidates route unchanged.
- [ ] `created` only queues one initial send; `already-exists`, denial and retry are safe; order-after-send / no candidate updates durable status and suppresses further outreach.
- [ ] No active Woo send with default-off switch, no Woo sequence-two follow-ups, and accepted ARCH-046-BG004 consent/STOP/Marketing final provider guard is wired on **every** actual initial-send/reentry path. Runtime composition fails closed if the guarded sender is unavailable.
- [ ] All runnable integration tests and existing Shopify worker regressions pass; work stops without enabling live send.
- [ ] Unexpected failures from any injected service propagate through the awaited worker callback and are visible as failed/retried BullMQ jobs with a structured error log; neither candidates nor billing are silently advanced or discarded.
- [ ] Known domain outcomes and `failed-retryable` receive intentionally distinct queue semantics; successful logging cannot occur after a rejected operation, and safe structured correlation fields contain no PII.

## Validation

- [ ] Worker+orchestrator integration tests with real BullMQ/Redis, injected deterministic service results and explicit candidate discriminator fixtures.
- [ ] End-to-end local Background/Postgres test for Woo checkout→maturity→recovery→initial attempt and late order/update (Meta mocked/controlled).
- [ ] Shopify pre-existing candidate/recovery worker regression including legacy unmarked jobs; test crash after INSERT before enqueue and retry behaviour.
- [ ] All entrypoint typecheck, declared build/lint/test suites relevant to touched worker code and `git diff --check`.
- [ ] Test real BullMQ failed/retry states and deterministic injected exceptions from all four services; verify no `job.completed` on failure, preserved cause, retry attempt visibility and no unhandled promise rejections.
- [ ] Inject a failing logger sink where practical to verify shared logger's own sink-failure isolation does not convert a genuine worker exception into success or break otherwise successful processing.

## Stop Condition

After completing only the task's scoped service, tests, Acceptance Criteria and Validation, populate the Completion Report, set status to `review`, return control to `moda_architect`, and **STOP**. Do not start a dependent task, enable live Woo sends, or change unrelated worker flows. Record launcher-prepared parent and implementation dedicated worktree paths, physical isolation, synchronisation, submodule state and both task branch revisions in the Completion Report.

## Implementation Notes

File-diff review gate: BG005 should primarily change wiring/orchestrator/tests and consume BG006's capability interfaces unchanged; changes to BG001–BG004 service internals signal a service-contract regression and require an explicit architect-reviewed correction rather than an opportunistic refactor.

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

Latest uploaded ZIP and proposed task files may lag active developer branches. Latest dependency state must be checked before materialisation. This 2026-10-25 snapshot records `ARCH-046-BACKGROUND-004` as blocked; do not infer completion from older conversation reports. Wait for the narrowed initial-send final guard to be implemented and accepted.

### Unresolved Issues

Wait for both ARCH-046-BACKGROUND-002 and the narrowed ARCH-046-BACKGROUND-004 to become Complete. Confirm their accepted interfaces before worker composition; raise missing canonical contracts or unimplementable guards instead of inventing bypasses.

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
