---
id: ARCH-048-BACKGROUND-011
architecture_id: ARCH-048
title: Integrate Woo multi-generation recovery into the existing workers
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 52
executor: codex
claimed_at: 2026-10-30T11:53:20Z
attempt: 1
depends_on:
  - ARCH-048-BACKGROUND-007
  - ARCH-048-BACKGROUND-008
  - ARCH-048-BACKGROUND-009
  - ARCH-048-BACKGROUND-010
enables:
  - ARCH-048-SYSTEM-TEST-001
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-048-BACKGROUND-011 — Integrate Woo multi-generation recovery into the existing workers

## Architecture

Architecture ID: `ARCH-048`.

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.

Coordinator: `moda_architect`.

## Objective

Wire the already accepted generation-aware Woo checkout, admission, old-outreach settlement and conversation-routing capabilities into **one existing Background worker pipeline** without introducing new business decisions at the orchestration layer.

## Context

The current `WooRecoveryOrchestratorService.onCheckout()` calls `outreach.enqueueInitial()` whenever BG001 returns `existing-recovery`; that will be wrong after BG007 changes the meaning of a new activity event. `onCandidateMatured()` currently sends for **every** `already-exists`, regardless of generation provenance; `clearMatured()` currently checks only token/event/timestamp. The existing `pending-recovery-candidate.worker.ts` verifies the old `wooCandidateJobId(candidate)` identity; the generator becomes generation-aware under BG007. BG011 is the **only worker/composition owner** of this change.

## Scope

**Permitted implementation files in `moda-interact-background/`:**

- `src/services/woocommerce-recovery/woo-recovery-orchestrator.service.ts` — consume BG007–BG009 canonical discriminants/ports, no new core business branching beyond dispatch/retry/cleanup coordination.
- `src/services/woocommerce-recovery/woo-recovery-composition.ts` — inject the accepted BG007–BG010 services/ports and generator-specific index cleanup.
- `src/workers/pending-recovery-candidate.worker.ts`, `woo-checkout-capture.worker.ts`, `woo-order-capture.worker.ts` and relevant existing Background entrypoints only as needed for the v2 candidate validator and service delegation.
- Focused integration tests: `tests/integration/woo-recovery-composed-services.integration.test.ts`, `woo-recovery-worker-wiring.integration.test.ts`, `woo-recovery-worker-faults.integration.test.ts`, `woo-recovery-shopify-legacy.integration.test.ts`, plus required new crash/race fixtures.

All BG007–BG010 **business-service** files, Prisma schema, plugin/API/Shared schemas, messaging ingress and billing ledgers are **read-only** for this task. **Narrow explicit exception:** `src/services/woocommerce-recovery/contracts.ts` may be changed **only** to tighten BG007 staging types to mandatory `WooPendingCandidate.generation`, `WooActivityWatermark.generation` (watermark type remains in its BG007-owned module: coordinate this single type-only tightening there), `WooAdmissionOutcome.generation` and `.repairInitial`, `WooRecoveryOutreachDispatcher.settleResumed`, and the `wooCandidateJobId` explicit generation signature. Runtime business logic in BG007 files stays read-only; update only necessary fixture/test constructors for type compliance. No new contracts, outcomes, or service methods may be introduced under this exception. A missing promised implementation must be returned to the architect.

## Out of Scope

No new public API, WordPress plugin changes, Woo checkout-state read, new worker process, reimplementation of checkout/admission/billing/WhatsApp decisions, default-on production Woo sending or Woo follow-ups.

## Requirements

1. **Checkout dispatch:** `onCheckout(event)` authenticates/validates as today and delegates once to `checkout.handleCheckout(event)`. On `resumed` call and **await** `outreach.settleResumed(previousRecoveryId)` even for replay of the original resumption event. Do **not** enqueue the old generation's initial. If settlement fails, throw to retry the checkout job; BG007 must make closure/candidate scheduling replay-safe. On `repair-existing-initial`, call `outreach.enqueueInitial(recoveryId)` **only** for the exact proven admission-origin event; BG009 independently rechecks `DETECTED`/attempt/provider status. On ordinary `scheduled`, `rescheduled`, empty, terminal, duplicate or ambiguous outcome, never enqueue initial outreach.
2. **Mature candidate:** `onCandidateMatured(candidate, context)` calls BG008 `evaluateMatured`. For `created` enqueue exactly the returned `recoveryId`; for `already-exists` enqueue **only when `repairInitial === true`** and `candidate.generation === outcome.generation`, otherwise no enqueue. `superseded`/`denied`/safe non-action never enqueue; `deferred` and technical `failed-retryable` must propagate using existing `WooRecoveryRetryRequired` policy. No direct provider call or charge in this method.
3. **Exact generation cleanup:** after an admission/send enqueue succeeds or is conclusively not applicable, clear only the candidate index/job whose **source, shop, checkout, generation, event ID, activity time and BullMQ job ID** equal the completed candidate. Consume BG007's conditional compare-and-delete index API. An old completed/failed/active job must not erase the next generation's candidate/index. Retriable enqueue/admission/settlement failures must preserve necessary retry evidence, not silently acknowledge.
4. **Worker identity, mandatory v2 typing and backward isolation:** finalize the staged internal type contracts described by BG007: all new Woo candidate/watermark generations and admission result fields required at compile time, `settleResumed` required on its dispatcher, and **no** implicit generation default in `wooCandidateJobId(ref, generation)`. Update all relevant Background Woo unit/integration fixture constructors, typed ports and workers **without editing BG007–BG010 business methods**. Update `pending-recovery-candidate.worker.ts` Woo validator to call `wooCandidateJobId(ref, candidate.generation)`, reject missing/invalid generation and malformed Woo identities. Strict `source === "woocommerce"` routes only to Woo; unmarked Shopify jobs still route to unchanged Shopify materialisation; unknown sources are rejected. Woo initial dispatch jobs still have exact `recoveryId`+`attemptId` binding. Preserve standard job retries, concurrency, logging and queue metrics. Do not infer provider from shop domain or token prefix.
5. **Order event wiring:** keep BG002's existing observed `ORDER_PLACED`/`ORDER_PAID`/`ORDER_CANCELLED` suppression, latest-row reconciliation, and candidate cancellation, including the case where generation 1 was previously closed and generation 2 is pending. Do not treat ORDER_PLACED as proof of payment. If terminal order evidence becomes inconsistent with generation status, report an architectural gap rather than reopen a paid checkout or blindly create a new send.
6. **Crash windows:** test closure SQL commit→candidate Redis failure; candidate admission INSERT→initial enqueue failure; provider permit→closure; old maturity job completing after new generation candidate; idempotent replay of same activity. Every retry must act on the **same intended generation**, never advance generation twice or re-send another old initial. No Redis/Meta operation inside SQL transaction.
7. **Shared logging:** use only `@modainteract/moda-interact-shared/logging`. Emit bounded `shopId`, recovery ID, generation, hashed event/job ID, stage, outcome, reason and errors where appropriate; do not log cart, raw checkout token, phone, access credentials or full customer payload. Exceptions must be logged/rethrown for BullMQ's bounded failure path, never silently swallowed.
8. **No outreach policy drift:** each distinct admitted recovery can independently obtain its initial (and only its own initial for now), but each `(recoveryId, sequence=1)` remains provider/billing idempotent. No cross-generation cap or cooldown. Production Woo outbound **remains disabled**; test-only enablement must require the accepted injection seam. The ARCH-046 consent/STOP/final SQL MARKETING checks remain mandatory, and Woo follow-ups remain disabled.
9. **Source-controlled rollout:** this patch changes internal queued Woo candidate data and deterministic job IDs. Document a **test/staging** queue-drain/recreate strategy before upgrading consumers, explicitly excluding Shopify candidates and existing PostgreSQL durable rows. The task must not delete queue data in a live environment or declare production activation. If production/backwards compatibility is discovered, stop for an architect-authored compatible rollout instead of inventing an adapter.

## Work Items

- [x] Finalize BG007 staged local TypeScript contracts to **required** generation, admission provenance and settlement members; remove implicit generation=1 job-ID default and fix typed fixtures.
- [x] Update `onCheckout` for `resumed` settlement and proven `repair-existing-initial` only.
- [x] Update maturity dispatch for `created` and `already-exists.repairInitial` exact-generation cases.
- [x] Wire BG007's generation job identity/index ownership to maturity worker and `clearMatured`.
- [x] Preserve Woo order routing and Shopify source isolation in all worker entrypoints.
- [x] Implement multi-service crash/retry, provider fence, generation 2 initial, queue-index and order racing tests.
- [x] Document observed rollout/queue state and Completion Report; stop for architect review.

## Interfaces / Contracts

- **Input:** unchanged parsed `WooCheckoutCapture` and `WooOrderCapture` from ARCH-035; BG007 `WooPendingCandidate.generation` on internal delayed jobs.
- **Local services:** BG007 **staged** `WooCheckoutActivityHandler`/new `WooCheckoutActivityOutcome`, BG008 `WooRecoveryAdmissionEvaluator`/`WooAdmissionOutcome.repairInitial`, BG009 `WooRecoveryOutreachDispatcher.settleResumed` (all mandatory after this task), existing `WooOrderReconciler`; BG010's inbound routing is an independent runtime path, so validate it in regression rather than invoking it from this orchestrator.
- **Queue:** existing `PENDING_RECOVERY_CANDIDATE_QUEUE`, `EVALUATE_PENDING_RECOVERY_JOB`, `WOO_INITIAL_DISPATCH_JOB`; Woo candidate job IDs now include generation, initial job IDs continue using recovery+attempt.
- **DB:** existing durable recovery, status history, attempt, provider message and billing records; no migration.

## Dependencies

- `ARCH-048-BACKGROUND-007` — accepted Complete.
- `ARCH-048-BACKGROUND-008` — accepted Complete.
- `ARCH-048-BACKGROUND-009` — accepted Complete.
- `ARCH-048-BACKGROUND-010` — accepted Complete.

## Enables

- `ARCH-048-SYSTEM-TEST-001` — terminal integrated certification, also gated by existing ARCH-046 Woo returning-consent task and other prerequisites.

## Acceptance Criteria

- [x] Resumption event cannot enqueue old recovery, and cleanup failure retries without creating a third generation.
- [x] Generation 2 matures with latest items and enqueues only its own initial (test-only enabled); generation 1's sent billing/history is untouched.
- [x] Admission-origin crash replay repairs only same-generation pending initial; arbitrary `already-exists` or late old maturity never sends.
- [x] Old job cleanup never drops new generation index; generation-bearing candidate is **required in the final TypeScript contract**, type-checked/validated at the worker, and all new creators/fixtures supply generation explicitly.
- [x] Shopify, unknown-source and Woo candidate routing remain strictly isolated.
- [x] STOP, missing/revoked consent, known order, ambiguity, disabled production outbound and Woo no-follow-up policy remain in effect.
- [x] All technical exceptions preserve retry evidence and are logged; no custom logging framework or unowned files modified.

## Validation

- [x] Selected Woo orchestrator/worker unit suites: 49 passed. Broader Woo recovery unit set: 317 passed, one pre-existing BG009 logging assertion failed because it expects a raw database error message while the service intentionally emits `PERSISTENCE_FAILURE`.
- [x] `node scripts/test-integration.mjs tests/integration/woo-recovery-composed-services.integration.test.ts tests/integration/woo-recovery-worker-wiring.integration.test.ts tests/integration/woo-recovery-worker-faults.integration.test.ts tests/integration/woo-recovery-shopify-legacy.integration.test.ts`: 4 files, 9 tests passed.
- [x] Applicable Woo checkout/order/admission/outreach regression tests: 6 files, 31 tests passed. No system-test execution.
- [x] `npm run build` passed; focused ESLint and `git diff --check` results recorded below.

## Stop Condition

After this **wiring-only** implementation and its focused validation, complete the Completion Report, change to `status: review`, return to `moda_architect` and **STOP**. Do not execute the terminal system test or activate live Woo outbound.

## Implementation Notes

The launcher must prepare matching mirrored `task/ARCH-048-BACKGROUND-011` branches in separate dedicated parent and Background worktrees, with synchronized start revisions. Verify BG007–BG010 are actually Complete and their implementation merged/available; a task-file state alone is not proof code is in the implementation base. Do not edit `_index.md`, architecture document, another task, or merged business-service implementation without an explicit architect Changes Requested correction. Use existing package test scripts; record exception and baseline evidence precisely.

## Completion Report

### Status

Ready for Review.

### Files Changed

Implementation is limited to the permitted Background contract bridge, Woo recovery orchestration/composition, pending candidate worker, and related Woo unit/integration/typecheck fixtures. No BG007–BG010 business-service behavior, database schema, other repository, architecture document, index, or system-test source was changed.

### Work Completed

- Required generation and admission provenance at compile time; required resumed-outreach settlement; made the candidate job ID require explicit generation.
- Resumption awaits settlement and never enqueues the old generation. Admission-origin repair is the only checkout replay that may enqueue initial outreach, and it is gated by the exact event outcome. Matured candidates enqueue only the exact created recovery or a proven same-generation repair.
- Matured candidate cleanup verifies Woo source, shop, checkout, generation, event, activity time, and job identity while holding the checkout lock, then uses compare-and-remove so an older completion cannot erase a successor index.
- The worker validates Woo v2 identity and generation, keeps unmarked Shopify materialisation isolated, and rejects unknown source markers.
- Added composed real-service coverage that resumes generation 1, stages/matures generation 2 with the latest basket, sends its own initial under test-only enablement, and verifies generation 1 history/billing remains intact. Added cleanup race/retry and worker-routing coverage.
- Rollout strategy for test/staging: before upgrading candidate consumers, stop/drain the Woo candidate queue and let known test/staging Woo jobs complete or explicitly recreate only disposable `source: "woocommerce"` candidate jobs from current committed activity. Record affected Woo job IDs/counts. Preserve all unmarked Shopify queue entries, all other queue entries, and every PostgreSQL recovery, attempt, message, status-history and reservation row. Resume consumers only after the new worker is installed and verify generation-bearing Woo jobs are being consumed. Do not delete/recreate production queue data; if any live old-format Woo candidate is present, block rollout and request an architect-authored compatibility plan.

### Validation Results

- `./node_modules/.bin/tsc --noEmit -p tests/typecheck/tsconfig.arch048-bg006.json` — passed.
- Focused Woo unit suites — 49 passed. Broader Woo recovery unit selection — 317 passed, 1 failed on existing BG009 redaction expectation (`connection unavailable` expected versus `PERSISTENCE_FAILURE` emitted); no assertion points to changed BG011 behavior.
- Four required composed integration suites (composed services, worker wiring, worker faults, Shopify legacy) — 4 files / 9 tests passed using Colima.
- Woo checkout activity, recovery admission, admission races, initial outreach, consent reader, and order capture regression set — 6 files / 31 tests passed using Colima.
- `npm run build` — passed.
- Focused ESLint over changed production and test files — passed.
- `git diff --check` — passed.
- Runtime: Node 24.19.0, npm 11.17.0, Colima-backed disposable PostgreSQL/Redis integration harness. No system test, live sender activation, deployment, or production queue operation was performed.

### Deviations

One unrelated existing BG009 unit assertion fails in the broader unit selection because it expects the unredacted raw database error string. No change was made to BG009-owned implementation or tests. The first regression integration attempt was denied access to Colima's Docker socket by the sandbox; the same suites were rerun with approved access and passed.

### Assumptions

Launcher confirmed BG007–BG010 dependencies complete and available at the prepared implementation base; test/staging queue instructions above assume a controlled maintenance window with known disposable Woo candidate events.

### Unresolved Issues

The broader selected unit suite retains the unrelated BG009 redaction assertion mismatch described above. Architect review should decide whether that pre-existing test needs reconciliation.

### Git / VCS

Task branch: `task/ARCH-048-BACKGROUND-011`.

Physical worktree isolation:

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-011`, branch `task/ARCH-048-BACKGROUND-011`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-011`, branch `task/ARCH-048-BACKGROUND-011`.
- Shared workspace checkout switched/mutated for task work: no. Shared implementation checkout switched/mutated for task work: no. Another task worktree reused: no.

Start-of-attempt synchronization evidence:

- Parent task branch claim was already at the remote claim commit `e4cf6bc5050bb78c8c670beddeb68adfd3059711`; no remote task fast-forward was needed. At implementation start, its history did not yet include the then-current `origin/main` tip, which had advanced with unrelated ARCH-052 task commits. Latest `origin/main` (`a7c32fdc2de0c3dbc0dff447afb69be4d61012a5`) was merged into the parent task branch at review submission in merge commit `e7b7e16d9dd4cfa9e31710b5ee4d874e1a1ee09d`.
- Implementation task branch started at `86d9736727a8527bcdf0b271593575f39e7e6950`, equal to its `origin/main` base; no remote task fast-forward was needed and `origin/main` was already included.

Implementation repository:

- Commit: `fd780e32e9a3f3f22940f58f9e10678d85bfd1af`.
- Remote branch: `origin/task/ARCH-048-BACKGROUND-011`.
- Push: successful after explicit user authorization; push output confirmed the new remote task branch and configured upstream.

Parent workspace:

- Task file: `docs/decisions/background/ARCH-048/BACKGROUND-011-compose-multi-generation-woo-recovery-workers.md`.
- Report commit: `d11fd042dbd88507937224e890e517b34cdc5e97`; latest parent branch commit after the mainline merge: `e7b7e16d9dd4cfa9e31710b5ee4d874e1a1ee09d`.
- Remote branch: `origin/task/ARCH-048-BACKGROUND-011`; review-report branch push succeeded after explicit user authorization. Push output confirmed the remote fast-forward from the prepared claim commit to the report branch head.
- Submodule gitlink staged: no.

Merged to implementation `main`: no. Merged to workspace `main`: no.

### Architectural Concerns

Event-only Woo capture cannot discover a never-delivered checkout/order change; this must remain a deployment gate.

## Architect Review

### Review Status

Pending architect review.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
