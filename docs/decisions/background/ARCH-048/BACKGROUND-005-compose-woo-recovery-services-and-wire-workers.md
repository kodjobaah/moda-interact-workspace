---
id: ARCH-048-BACKGROUND-005
architecture_id: ARCH-048
title: Compose Woo recovery services and wire event/maturity/outbound workers
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 54
executor: null
claimed_at: null
attempt: 2
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
updated: 2026-10-26
---

# ARCH-048-BACKGROUND-005 — Compose Woo recovery services and wire event/maturity/outbound workers

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Materialised in the canonical parent task worktree on `task/ARCH-048-BACKGROUND-005`. Attempt 2 is complete after all six declared dependencies were verified Complete, including developer-completed `ARCH-046-BACKGROUND-004` with its accepted Architect Review. The implementation and parent task record are published on their dedicated task branches; no merge to `main` or live WhatsApp send is implied.

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
- Integrate accepted ARCH-046-BACKGROUND-002 via its `WooDeniedAdmissionNotifier` factory and inject it into BG003 `onDeniedAdmission`. Inject the **concrete accepted** ARCH-046-BACKGROUND-004 `WooGuardedInitialSender` into `createWooRecoveryOutreachService`; do not substitute the generic outbound `sendTemplate` or an unguarded preflight. BG004 is now architect-accepted and Complete; preserve the merged shared merchant-notice writer and do not duplicate it.
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

- [x] Compose four already accepted services using the unchanged BG006 Background-local interface types through a small orchestrator, one code module and explicit constructor/factory injection; reuse existing deployed worker entrypoints.
- [x] Wire checkout capture worker to BG001, order capture worker to BG002, pending candidate worker to BG003→BG004 routing with explicit Woo source marker and Shopify legacy fallback.
- [x] Wire existing initial outbound processor to ARCH-048 BG004; compose the accepted ARCH-046-BG004 `WooGuardedInitialSender`, and inject ARCH-046-BG002 notice callback at BG003 admission. Reject missing guard dependencies (no live or test fallback to generic unguarded sending). Retain correct queue ack/failure/cleanup behaviour.
- [x] Add tests for Woo vs Shopify routing, nil job+existing recovery, checkout after first send, order after first send, duplicate/failed job, DB insert→enqueue interruption, disabled Woo send and no Woo follow-ups.
- [x] Run existing Shopify worker/maturity regressions and entrypoint startup/build checks on the synchronized task branch; record exact changed files per orchestration boundary. Six focused integration suites, build and lint pass on Attempt 2.
- [x] Wire the shared structured logger into the orchestrator and each affected worker path; record safe started/completed/deferred/failed events without duplicate business rule logging.
- [x] Add worker-level fault-injection tests for rejected BG001, BG002, BG003, BG004, merchant-notice, Redis and enqueue dependencies; confirm BullMQ failure/retry rather than silent success or candidate deletion.

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

- [x] Woo checkout/order capture workers invoke the new orchestrator, and no business decision is implemented inside workers.
- [x] Woo maturity candidates route exclusively to Woo admission and initial-send pipeline; existing Shopify/legacy candidates route unchanged.
- [x] `created` only queues one initial send; `already-exists`, denial and retry are safe; order-after-send / no candidate updates durable status and suppresses further outreach.
- [x] No active Woo send with default-off switch, no Woo sequence-two follow-ups, and accepted ARCH-046-BG004 consent/STOP/Marketing final provider guard is wired on **every** actual initial-send/reentry path. Runtime composition fails closed if the guarded sender is unavailable.
- [x] All runnable integration tests and existing Shopify worker regressions pass; work stops without enabling live send.
- [x] Unexpected failures from any injected service propagate through the awaited worker callback and are visible as failed/retried BullMQ jobs with a structured error log; neither candidates nor billing are silently advanced or discarded.
- [x] Known domain outcomes and `failed-retryable` receive intentionally distinct queue semantics; successful logging cannot occur after a rejected operation, and safe structured correlation fields contain no PII.

## Validation

- [x] Worker+orchestrator integration tests with real BullMQ/Redis, injected deterministic service results and explicit candidate discriminator fixtures.
- [x] End-to-end local Background/Postgres test for Woo checkout→maturity→recovery→initial attempt and late order/update (Meta mocked/controlled).
- [x] Shopify pre-existing candidate/recovery worker regression including legacy unmarked jobs; test crash after INSERT before enqueue and retry behaviour.
- [x] All entrypoint typecheck, declared build/lint/test suites relevant to touched worker code and `git diff --check`. Attempt 2 build, lint, focused unit/integration tests and diff checks pass.
- [x] Test real BullMQ failed/retry states and deterministic injected exceptions from all four services; verify no `job.completed` on failure, preserved cause, retry attempt visibility and no unhandled promise rejections.
- [x] Inject a failing logger sink where practical to verify shared logger's own sink-failure isolation does not convert a genuine worker exception into success or break otherwise successful processing.

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

Complete — Attempt 2 passed developer self-review, received the developer-supplied Architect Review Accepted decision, and was explicitly completed on 2026-10-26. Attempt 1 review history is preserved below.

### Files Changed

**Implementation repository:** `moda-interact-background`; branch `task/ARCH-048-BACKGROUND-005`.

- `6ed1ee7` — original orchestrator, worker composition/routing, internal initial dispatch and focused tests (pushed). Original Git output: 17 files, 1,087 insertions and 190 deletions.
- `e0342e6` — subsequent outstanding-validation and legacy-cleanup corrections (reported pushed in the developer's earlier terminal evidence).
- `71c0070` — corrected terminal-order assertions to retain an unadmitted attempt as `PENDING`, release its reservation, and prove replay is suppressed.
- `e66750e` — added test-only `messaging.sender` configuration for the disposable initial-outreach fixture after mainline template preparation began requiring it. Both commits are pushed; no uncommitted implementation changes remain.

Initial implementation source files:

- `src/entrypoints/recovery.ts`
- `src/entrypoints/shopify-event.ts`
- `src/index.ts`
- `src/services/woocommerce-recovery/woo-initial-dispatch.queue.ts`
- `src/services/woocommerce-recovery/woo-recovery-composition.ts`
- `src/services/woocommerce-recovery/woo-recovery-orchestrator.service.ts`
- `src/workers/pending-recovery-candidate.worker.ts`
- `src/workers/woo-checkout-capture.worker.ts`
- `src/workers/woo-order-capture.worker.ts`

Initial focused test files:

- `tests/integration/woo-checkout-capture.integration.test.ts`
- `tests/integration/woo-order-capture.integration.test.ts`
- `tests/integration/woo-recovery-worker-wiring.integration.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-initial-dispatch.queue.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-recovery-orchestrator.service.test.ts`
- `tests/unit/workers/woo-checkout-capture.worker.test.ts`
- `tests/unit/workers/woo-order-capture.worker.test.ts`
- `tests/unit/workers/woo-recovery-routing.worker.test.ts`

Additional BG005 validation/cleanup files confirmed present in the supplied worktree:

- `tests/integration/woo-recovery-composed-services.integration.test.ts`
- `tests/integration/woo-recovery-worker-faults.integration.test.ts`
- `tests/integration/woo-recovery-shopify-legacy.integration.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-recovery-orchestrator-faults.test.ts`
- `src/workers/woo-checkout-capture.worker.ts` and `src/workers/woo-order-capture.worker.ts` (remove obsolete optional-orchestrator construction paths)
- `tests/unit/workers/woo-checkout-capture.worker.test.ts` and `tests/unit/workers/woo-order-capture.worker.test.ts` (mandatory dependency coverage)

The final changed-file set and complete commit ancestry should be reconciled with `git diff origin/main...HEAD` (or the canonical task baseline) during developer self-review; the ZIP is not a Git history record.

### Work Completed

- Implemented thin `WooRecoveryOrchestratorService` composition of accepted BG001 checkout, BG002 terminal order, BG003 recovery admission, BG004 initial outreach, ARCH-046-BG002 consent-denial notice and ARCH-046-BG004 concrete guarded sender, with no generic unguarded sender fallback.
- Wired Woo checkout/order capture, explicitly marked Woo maturity and initial dispatch into existing Background entrypoints. Unmarked Shopify candidates continue down the existing materialiser; unknown sources fail safely. Insert-before-enqueue replay uses the same durable recovery, not a second initial send.
- Preserved default-off Woo outbound sending, local STOP/final SQL provider permit, consent, terminal order and credit accounting guards, and no Woo sequence-two follow-up. Business logic remains in BG001–BG004.
- Removed the obsolete Woo capture-worker construction mode that allowed a missing orchestrator. Required composition now fails closed. The live Shopify compatibility path is **not** dead code and remains supported.
- Used `@modainteract/moda-interact-shared/logging` in changed worker/orchestrator paths. Tests exercise bounded identifiers, sink-failure isolation, awaited failure propagation and BullMQ failure/retry states; no exceptions are intentionally swallowed.
- Added small, separated tests for composed service execution, worker faults/retries, legacy Shopify routing, and logger failure isolation. The Meta provider is mocked/controlled; tests do not send real WhatsApp messages.
- Corrected the three obsolete terminal-order regression assertions: unadmitted initial attempts remain `PENDING`/retryable, the credit reservation is released, and replay is denied by terminal-order evidence without sending or charging.

### Validation Results

**Prior developer terminal evidence in this conversation (26 October 2026):**

- Original BG005 unit group: **34/34 PASS** across five files; Redis/BullMQ/PostgreSQL wiring/capture integration: **4/4 PASS** across three files; lint, `npx tsc --noEmit`, and build passed.
- Additional BG005 cleanup/fault unit group: **25/25 PASS**; composed-service, worker-fault, Shopify legacy and worker-wiring integration group: **9/9 PASS**, four suites; lint/typecheck/build passed after the test corrections. `e0342e6` was pushed on the implementation task branch.
- Existing pending-candidate and Woo outreach unit regressions: **67/67 PASS**. The first run of Woo initial-outreach integration exposed 3 obsolete expected `FAILED` states; these were corrected to the accepted `PENDING`/credit-release contract and retested below.

**Earlier uploaded developer terminal evidence:** `typescript(20261026-091609)` (26 October, test run began 09:04 UTC; superseded for current repository state):

- `npm run test:integration -- tests/integration/arch048-woo-initial-outreach.integration.test.ts tests/integration/woo-initial-send-fence.integration.test.ts`: **12/12 PASS across 2 files**, including all seven initial-outreach scenarios and all five final SQL permit scenarios. These verify placed/paid/cancelled orders block replay without provider send, STOP after reservation, default-off, concurrent permit idempotency and billing/credit assertions.
- `npm run lint` (`eslint .`): **PASS** (no errors in terminal output).
- `npx tsc --noEmit`: **PASS** (no errors in terminal output).
- `npm run build` (`npm run prisma:generate && tsc`): **PASS**, Prisma Client v6.19.3 generated.
- At that snapshot, Git showed one modified integration test and an untracked terminal recording. The test correction was subsequently committed and pushed; see current review evidence below. The terminal recording remains excluded from Git.

**Current developer review evidence (26 October 2026, canonical BG005 worktrees):**

- Implementation branch: `task/ARCH-048-BACKGROUND-005`, clean and published through `e66750e9d71eb38854cecec5adf0fbeca46531a0`, matching its remote before the latest forward synchronization. Latest `origin/main` (`d9504f5`) was merged forward locally in `6db7e6d`; it is an ancestor of the implementation task tip. The merge commit is pending publication as part of this review handoff. `git diff --check origin/main...HEAD` passes.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-005`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-005`. They are distinct registered physical worktrees on matching `task/ARCH-048-BACKGROUND-005` branches, with parent and Background submodule Git common directories respectively. The recursive `database` submodule is initialized at `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`.
- The parent worktree has current `origin/main` (`e8759d6`) merged forward in `56ff357`; its task branch is 8 commits ahead of the remote only because that synchronization merge has not yet been published. The merge and this review update will be published together.
- `npm run lint` — PASS.
- Before the latest mainline merge, `npm run test:integration -- tests/integration/woo-recovery-composed-services.integration.test.ts tests/integration/woo-recovery-shopify-legacy.integration.test.ts tests/integration/woo-recovery-worker-faults.integration.test.ts tests/integration/woo-recovery-worker-wiring.integration.test.ts tests/integration/arch048-woo-initial-outreach.integration.test.ts tests/integration/woo-initial-send-fence.integration.test.ts` passed: 6 files, 21 tests.
- On latest synchronized `origin/main` (`d9504f5`), the same six-file integration command — FAIL: 3 files passed, 3 failed; 12 tests passed, 9 failed. The composed Woo lifecycle fixture retries to failure with `PlatformConfigurationFailure`; initial outreach and final-send-fence fixtures receive `suppressed` outcomes where their assertions expect dispatch/permit results. These disposable fixtures do not yet satisfy the newly merged prepared-template/registration contract. No BG001–BG004 service implementation was changed by BG005 to bypass that contract.
- `npm test -- --run tests/unit/services/woocommerce-recovery/woo-initial-dispatch.queue.test.ts tests/unit/services/woocommerce-recovery/woo-recovery-orchestrator.service.test.ts tests/unit/services/woocommerce-recovery/woo-recovery-orchestrator-faults.test.ts tests/unit/workers/woo-checkout-capture.worker.test.ts tests/unit/workers/woo-order-capture.worker.test.ts tests/unit/workers/woo-recovery-routing.worker.test.ts` — PASS: 6 files, 44 tests.
- `npm run test:integration -- tests/integration/arch048-woo-initial-outreach.integration.test.ts` — PASS: 1 file, 7 tests after the fixture correction.
- `npm run build` — FAIL after Prisma Client generation. TypeScript reports TS2307 in `src/services/meta-template-management/status-job.ts` and `src/workers/whatsapp.worker.ts` for `@modainteract/moda-interact-shared/whatsapp-template-events`. Both files arrived from synchronized `origin/main`; installed Shared `2.5.0` has no matching export or dist file. The affected files are outside BG005's declared worker/composition scope and were not edited. This same build failure remains after latest `origin/main` (`d9504f5`).
- Earlier shell history included commands launched from the prior BG006 worktree; those runs are not counted here. All current review validations above were executed with an explicit `cd` into the canonical BG005 implementation worktree. The original start-of-attempt launcher packet remains unavailable; current isolation/synchronization evidence is not presented as historical launcher output.

**Scope/limits:** Earlier BG005 tests cover real PostgreSQL, Redis and BullMQ and either injected domain services or a composed Woo lifecycle with controlled provider. Final SQL-permit tests cover the accepted consent/STOP/send fence. These are not a live Meta/WhatsApp production end-to-end test. Test results from different invocations are not aggregated into one fictional single-suite run.

### Deviations

- Removed only the obsolete optional-orchestrator capture worker construction mode. Active unmarked Shopify candidate routing is retained intentionally.
- The terminal-order and sender-configuration fixture corrections are committed/pushed in `71c0070` and `e66750e`; the implementation worktree is clean.

### Assumptions

- Accepted BG001–BG004 and ARCH-046 notifier/guard interfaces remain authoritative. No independent Woo sequence-two sending is enabled.
- `completion_mode: developer` requires an explicit developer completion action **after** authorized review; the implementation commit does not complete the task.

### Unresolved Issues

1. **Restore focused integration validity on current main:** update BG005's disposable composed-outreach and final-permit fixtures to provide the current prepared/approved template registration and any other required configuration, then verify expected admitted/suppressed behavior against the current contract. Keep production BG001–BG004 code and final permit safeguards unchanged.
2. **Resolve the synchronized build blocker:** publish the `whatsapp-template-events` Shared entrypoint consumed by the mainline Background imports, or route those imports through the appropriate owner/task. Do not modify those files within BG005 without an architect-approved scope change. Then rerun `npm run build` and the focused regressions.
3. **Historical preparation packet:** the original launcher start-of-attempt packet is unavailable. Current dedicated worktree paths, mappings, branch publication, synchronization and recursive submodule state were independently verified; no historical packet is fabricated.
4. **Next attempt:** after both blockers are resolved/authorized, `/moda_developer_create ARCH-048-BACKGROUND-005` may claim Attempt 2. This review does not increment the attempt.

### Architectural Concerns

- None newly demonstrated by the final validation runs. The system still depends on Woo producer events arriving; this implementation does not provide external provider polling or permit live Meta sending by itself.
- The synchronized build mismatch is the current review blocker; focused behavior tests pass. The original launcher packet remains unavailable. Preserve Attempt 1; do not mark this task complete or architect-accepted.

## Developer Self-Review - Changes Requested

### Review Decision

Attempt 1 is returned to `ready`. The task-owned implementation and fixture corrections are published; focused unit tests (44/44) and lint pass. On current main, 9 of 21 focused integration tests fail because the composed, initial-outreach and final-permit fixtures do not satisfy the newly merged prepared-template/registration contract. The full build also fails because mainline-added `status-job.ts` and `whatsapp.worker.ts` import an entrypoint absent from installed `@modainteract/moda-interact-shared@2.5.0`. Those production files are outside BG005's declared ownership, so the developer did not edit them. Correct the BG005 fixtures and resolve the Shared publication/import contract under its owner or obtain an architect-approved scope amendment; rerun focused validation afterward.

### Required Correction

- Update the composed Woo, initial-outreach and send-fence disposable fixtures to meet current template-preparation/final-registration requirements, and make all six focused integration suites pass without weakening production guards.
- Ensure `@modainteract/moda-interact-shared/whatsapp-template-events` is published and available to the Background package, or route the two upstream imports through an authorized owner/task. Do not complete BG005 while the synchronized build fails.
- After both corrections are available, rerun `npm run build`, the six focused integration suites, the focused unit group, lint and `git diff --check` from the canonical BG005 implementation worktree. Preserve the default-off send gate and do not enable live WhatsApp traffic.

### State Transition

Set `status: ready`, `executor: null`, and `claimed_at: null`; Attempt 1 remains unchanged. Implementation is clean at synchronized task tip `6db7e6d`, with forward synchronization merge pending push. No Attempt 2 is claimed.

## Architect Review

### Review Status

Accepted — the developer explicitly supplied “Architect Review Accepted” with the completion instruction on 2026-10-26. This acceptance applies to Attempt 2 and its recorded validation evidence.

### Review Notes

Accepted for Attempt 2. The prepared-template fixture correction restores current integration behavior without weakening the production admission, consent, STOP or send guards. The previously reported Shared export build error no longer reproduces; current build and focused validations pass.

### Reviewed Files

Implementation and test changes are recorded in the Attempt 2 developer self-review above. No production BG001–BG004 service internals were changed by this correction.

### Validation Reviewed

Six focused integration suites (21/21), six focused unit files (44/44), `npm run build`, `npm run lint`, and both `git diff --check` invocations passed on the canonical implementation worktree.

### Architecture Conformance

Conforms to the task scope and preserves the default-off send gate, accepted final permit and Shopify legacy route. No live WhatsApp traffic was enabled.

### Follow-up

ARCH-048-SYSTEM-TEST-001 remains pending because its other declared dependencies are not all complete; its manual gate is unchanged.

## Execution Ownership Amendment

- Date: 2026-10-26.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-048-BACKGROUND-005` for this Ready agent-owned task. Execution ownership transfers to the developer and completion mode is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, dependencies, task scope, acceptance criteria and validation requirements.
- Dependency check: `ARCH-048-BACKGROUND-001`, `ARCH-048-BACKGROUND-002`, `ARCH-048-BACKGROUND-003`, `ARCH-048-BACKGROUND-004`, `ARCH-046-BACKGROUND-002`, and `ARCH-046-BACKGROUND-004` each route as `complete` in their canonical task records. The latest Architect Review headings in the four ARCH-048 developer-completed service records remain Pending; their developer completion state is not represented as architect acceptance. `ARCH-046-BACKGROUND-004` has explicit Architect Review Accepted.
- State before claim: `ready`, Attempt 0, `executor: null`, `claimed_at: null`. The canonical developer preparation workflow will create/reuse and synchronize the implementation worktree, then claim Attempt 1. No implementation or merge to `main` is performed by this ownership amendment.

## Developer Self-Review - Attempt 2 Passed

### Review Decision

Attempt 2 passes developer self-review. The prepared/approved template registration fixture correction resolves the six focused integration-suite failures recorded in Attempt 1 without modifying production BG001–BG004 guards. The previously recorded Shared import build failure no longer reproduces on this synchronized branch. No live WhatsApp traffic was enabled. The developer explicitly completed the task after supplying Architect Review Accepted.

### Corrections and Files

- `tests/integration/fixtures/woo-approved-initial-template.fixture.ts` — added a persisted approved initial Woo template registration fixture.
- `tests/integration/fixtures/arch048-woo-outreach.fixture.ts` — seed the approved registration in the composed outreach fixture.
- `tests/integration/fixtures/woo-initial-send-fence.fixture.ts` — use the persisted registration identity for final-permit setup.
- `tests/integration/arch048-woo-initial-outreach.integration.test.ts` — use the test WABA and real persisted template selection rather than mocking the selector.
- `tests/integration/woo-recovery-composed-services.integration.test.ts` — use the same approved-registration contract and WABA setup.

Implementation commit `16c8df64347948dec14490fbf32343146996f1a1` is pushed to `origin/task/ARCH-048-BACKGROUND-005`. The implementation worktree is clean and its task branch contains the synchronized `origin/main` tip `d9504f5`.

### Validation

- Six focused integration suites — **21/21 passed**: composed services, Shopify legacy routing, worker faults, worker wiring, initial outreach, and initial-send fence.
- Six focused unit files — **44/44 passed**: dispatch queue, orchestrator, orchestrator faults, checkout worker, order worker, and recovery routing.
- `npm run build` — passed, including Prisma Client generation and TypeScript compilation; the prior `whatsapp-template-events` TS2307 errors did not recur.
- `npm run lint` — passed.
- `git diff --check origin/main...HEAD` and `git diff --check origin/task/ARCH-048-BACKGROUND-005..HEAD` — passed.

### Worktree and Synchronization Evidence

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-005`, branch `task/ARCH-048-BACKGROUND-005`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-005`, branch `task/ARCH-048-BACKGROUND-005`.
- Both are distinct canonical physical worktrees. Launcher preparation reused both and reported task branches already current with `origin/main` incorporated.
- Recursive submodule preparation passed; `database` is initialized at `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`.
- No task branch was merged to `main`.

### State Transition

Set `status: complete`, `executor: null`, `claimed_at: null`, and preserve Attempt 2. This passing review is followed by the explicit developer completion decision below.

## Developer Completion Decision - Attempt 2

On 2026-10-26, the developer explicitly completed ARCH-048-BACKGROUND-005 after the passing Attempt 2 self-review and explicit Architect Review Accepted. All required work items and acceptance criteria are complete; the implementation commit and this parent task record are pushed on their respective task branches. Attempt remains 2. No merge to `main` was performed. The system-test dependent remains pending behind its other incomplete dependencies and its normal manual gate.
