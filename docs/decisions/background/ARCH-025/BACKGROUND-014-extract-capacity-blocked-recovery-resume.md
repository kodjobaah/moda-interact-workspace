---
id: ARCH-025-BACKGROUND-014
architecture_id: ARCH-025
title: Extract capacity-blocked recovery resume
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 70
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-013
enables:
  - ARCH-025-BACKGROUND-015
created: 2026-10-02
updated: 2026-10-03
---

# Extract capacity-blocked recovery resume

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract per-recovery durable capacity-blocked resume/terminalisation while retaining `RecoveryCapacityResumeService` as the queue/repair scheduler and reusing canonical snapshot/initiation owners.

## Context

`resumeCapacityBlockedRecovery(...)` is a separate retry lifecycle: it validates durable block state and shop status, checks execution eligibility outside and inside the checkout lock, refreshes current Shopify checkout state, terminalises unrecoverable blocked recoveries atomically, or re-enters the canonical recovery initiation path. Queue/repair scheduling already belongs to `RecoveryCapacityResumeService` and must remain there.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts
tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

RecoveryCapacityResumeService queue/repair implementation; billing admission implementation; snapshot mapping; initial outreach; schema.

## Requirements

### Common ARCH-025 CheckoutRecovery invariants

- This is a **move-only structural refactor**. Do not change recovery eligibility, outreach policy, billing/capacity economics, candidate/order correlation, queue identity, provider protocol, retry behaviour, authorization, durable lifecycle semantics or CommerceAgent context meaning.
- Preserve the exact compatibility surface from `src/services/checkout-recovery.service.ts`: `CheckoutRecoveryService`, `checkoutRecoveryService`, `MaturedCandidateMaterializationResult`, `CheckoutRefreshResult`, and every current public method: `handleCheckoutCreatedContract`, `materializeMaturedCandidate`, `recordExternalActivity`, `handleCheckoutUpdatedContract`, `handleCartActivityContract`, `handleOrderCompletedContract`, `upsertRecovery`, `attachCustomer`, `resolveRecipient`, `markRecoveryMessageSent`, `handleOrderCompleted`, `handleCheckoutCreated`, `processRecoveryOutreachFollowUp`, `markRecoveryCapacityBlocked`, `resumeCapacityBlockedRecovery`, `getAgentContext`, `getAgentContextForStandaloneConversation`.
- Preserve the constructor `(billingService: RecoveryBillingService = recoveryBillingService)`. Existing workers and Commerce callers continue using the `checkoutRecoveryService` singleton; do not migrate worker entrypoints/callers as part of extraction.
- Extracted modules MUST NOT import `checkout-recovery.service.ts`; dependency direction is façade -> collaborator. Symbols moved out of the façade that are currently exported must be compatibility re-exported from it.
- Collaborator constructors are inert wiring only. Do not perform Prisma/provider/Redis/queue/environment I/O or eager model access during construction.
- Any extracted collaborator that performs recovery billing MUST receive and reuse the exact `RecoveryBillingService` instance supplied to the `CheckoutRecoveryService` constructor. Do not silently fall back to the module singleton when a caller supplied a test/custom billing service.
- Continue reusing canonical owners: `RecoveryBillingService`, `RecoveryOutreachAttemptService`, `recoveryOutreachFollowUpService`, `RecoveryPolicyService`, `PendingRecoveryCandidateService`, `ShopExecutionEligibilityService`, `AbandonedCheckoutLookupService`, `RecoveryCapacityResumeService`, `OutboundWhatsAppAdmissionService`, `ConversationService`, `ConversationMessageService`, and `WhatsAppTemplateSelectorService`. Do not duplicate their logic.
- There remains exactly one outbound WhatsApp provider path through `OutboundWhatsAppAdmissionService`; do not create a direct Meta/provider send workflow. Deterministic outreach idempotency remains `recovery-outreach:<attemptId>`.
- Preserve all provider/network versus Prisma transaction boundaries, checkout-scoped lock boundaries, order-processed tombstone timing, status-guarded `updateMany` predicates, generation ordering and post-commit queue/provider ordering exactly. Do not move external calls into a Prisma transaction.
- Preserve stale/duplicate replay behaviour and terminal-state non-reopening. Do not convert durable capacity blocking into in-memory state.
- Preserve current data-source trust: webhook candidate/update basket/customer fields must not become durable recovery snapshot data where current Shopify lookup is authoritative.
- Preserve the integrated ARCH-024 `RecoveryAgentContext` contract: canonical `shopId`, shop domain, conversation ownership checks, language metadata and bounded history/current-message semantics.
- Do not introduce a new generic logger. If diagnostics are added, use the canonical Shared structured logger and bounded identifiers only; do not log whole checkout/customer/provider/message payloads.
- These post-ARCH-024 regression assets are frozen and MUST remain byte-for-byte unchanged:
  - `tests/unit/services/matured-candidate.materialization.test.ts` — SHA-256 `28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb`
  - `tests/unit/services/checkout-refresh.test.ts` — SHA-256 `3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f`
  - `tests/unit/services/order-recovery-correlation.test.ts` — SHA-256 `7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf`
  - `tests/unit/services/checkout-recovery.capacity-resume.test.ts` — SHA-256 `8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1`
- Add separate focused tests for each extracted owner. Do not move assertions out of frozen files, skip tests, weaken assertions or change expected behaviour to make an extraction pass.
- Full `npm test` must introduce no regression. If a synchronized baseline failure exists, follow the durable baseline protocol; do not silently redefine expected failures inside the task.

### R1 — durable admission-block authority

Only a durable `DETECTED` recovery with `admissionBlockReason = RECOVERY_CAPACITY_EXHAUSTED` is eligible. Preserve inactive-shop and execution-eligibility short-circuits before provider work. Preserve the checkout lock and durable reread after lock; an already transitioned/cleared recovery remains a no-op.

### R2 — provider lookup outcomes

Lookup uses the durable recovery's shop/checkout/cart/url/detectedAt. `provider-error`, `ambiguous` and `bounded-limit-exceeded` retain current thrown/retryable behaviour. `not-found` or a completed checkout terminalises the blocked recovery. Preserve the current externally returned terminal reason quirk: not-found returns `{ kind: "terminal", reason: "not-found" }`, while a found-but-completed checkout returns `{ kind: "terminal", reason: "found" }`; do not normalise the latter to `completed`.

### R3 — terminalisation transaction

Move `terminalizeUnrecoverableBlockedRecovery(...)` with this processor. Preserve one Prisma transaction with status/block CAS, `CANCELLED`, `expiredAt = new Date()`, clearing block fields and status-history creation only when update count is one. Keep source `recovery-capacity-resume` and current reason strings.

### R4 — canonical re-entry with frozen façade-call compatibility

For a still-abandoned checkout, reuse BACKGROUND-010 snapshot mapping and BACKGROUND-008 initiation using the current generation. The frozen capacity-resume suite replaces `service.handleCheckoutCreated` and expects `resumeCapacityBlockedRecovery(...)` to invoke that **current replaceable façade method**. Preserve that observable relationship with a narrow dynamic callback/port that resolves `this.handleCheckoutCreated` at invocation time; do not eagerly bind the original method in the constructor and do not reverse-import the façade from the processor.

Preserve call arity exactly: generation 1 calls `handleCheckoutCreated(seed)` with one argument; only later generations call `handleCheckoutCreated(seed, generation)`. After initiation, preserve the durable reread that distinguishes `capacity-exhausted` from `initiated`. If the reread is missing, current behaviour still returns `initiated` with fallback status `DETECTED`; do not turn that into an error. Do not duplicate the initial send path.

### R5 — first-block timestamp semantics

`markRecoveryCapacityBlocked(...)` remains the BACKGROUND-008 compatibility operation that only marks an unblocked `DETECTED` recovery, preserving the original block timestamp on repeats. `markRecoveryMessageSent(...)` continues clearing capacity-block fields.

## Work Items

- [x] Extract per-recovery capacity resume/terminalisation and façade delegate.
- [x] Keep RecoveryCapacityResumeService unchanged as scheduling/repair owner.
- [x] Reuse snapshot builder and initiation service for re-entry.
- [x] Add focused tests for eligibility/lock reread/provider outcomes/terminalisation/re-entry and duplicate replay.
- [x] Run capacity-resume worker tests and frozen capacity suite.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-013`

## Enables

- `ARCH-025-BACKGROUND-015`

## Acceptance Criteria

- [x] Capacity-blocked recovery state remains durable and race-safe.
- [x] Provider failure/unrecoverable outcomes preserve current retry/terminal behaviour.
- [x] Re-entry uses the one canonical initiation workflow through the replaceable façade compatibility port, including current generation-1 call arity.
- [x] Queue/repair scheduling is not duplicated or moved.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/services/matured-candidate.materialization.test.ts':'28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb','tests/unit/services/checkout-refresh.test.ts':'3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f','tests/unit/services/order-recovery-correlation.test.ts':'7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf','tests/unit/services/checkout-recovery.capacity-resume.test.ts':'8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}" prints all expected SHA-256 values
- [x] `git diff -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` is empty
- [ ] `npm test -- tests/unit/services/matured-candidate.materialization.test.ts tests/unit/services/checkout-refresh.test.ts tests/unit/services/order-recovery-correlation.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts` passes (77/78; frozen materialization language-context assertion fails)
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes (10/10)
- [x] `npm test` introduces no new regression compared with the preceding B013 full-suite validation; current unresolved failures are listed below
- [x] `npm run build` succeeds
- [x] `git diff --check` passes
- [x] `npm test -- tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts tests/unit/workers/recovery-capacity-resume.worker.test.ts` passes (19/19)

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Review

### Files Changed

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`
- `tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts`

### Work Completed

- Extracted durable per-recovery resume and terminalisation into `RecoveryCapacityResumeProcessorService`; the façade method delegates to it and the existing constructor/public compatibility surface remains unchanged.
- Preserved durable eligibility checks before and after checkout lock, durable reread after lock, provider retry/terminal outcomes, terminal CAS and atomic status history, current Shopify lookup data, and canonical snapshot/initiation ownership.
- The processor receives a narrow initiation callback from the façade that resolves `this.handleCheckoutCreated` at invocation time. Generation 1/default still invokes it with one argument; later generations pass the generation. The frozen façade spy test passes.
- Kept `RecoveryCapacityResumeService` and `recovery-capacity-resume.worker.ts` unchanged as queue/repair scheduling owners.
- Added 11 direct processor tests covering admission gates, locked reread/recheck, retryable failures, terminalisation, return-reason compatibility, generation arity, capacity-block persistence, and replay.

### Validation Results

- PASS: `npm run prisma:generate`.
- PASS: `npm run build`.
- PASS: new processor and capacity-resume worker suites, 19/19; frozen `checkout-recovery.capacity-resume.test.ts`, 19/19.
- PASS: entrypoint isolation, 10/10.
- PASS: all four frozen regression asset hashes match and the protected test-file `git diff` is empty.
- PASS: `git diff --check`; the queue/repair scheduler service and worker have no diff.
- FAIL: required four-suite frozen group, 77/78. `matured-candidate.materialization.test.ts` expects Shopify language metadata `fr-CA`/`shopify` but receives null values. That asset remains byte-identical and B014 does not touch materialization behavior.
- Full `npm test`: 1,571 passed, 38 skipped, 12 failed tests across four files, plus one suite collection error. The failures are three billing-reconciliation assertions; the same frozen materialization language assertion; four PostgreSQL translation integration tests unable to connect to `localhost:5432`; four observability-startup timeouts; and `tests/unit/commerce/evidence.test.ts` failing to find the ARCH-020-BACKGROUND-002 fixture in its task-worktree path. These are the same failure categories recorded in the preceding B013 full-suite run; the previously failing Commerce host deadline assertion passed in this run, and no new failing category appeared.

### Execution Evidence

- Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-014` on `task/ARCH-025-BACKGROUND-014`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-014` on `task/ARCH-025-BACKGROUND-014`.
- Shared workspace checkout switched/mutated: no. Shared implementation checkout switched/mutated: no. Another task worktree reused: no.
- Start synchronization: parent remote task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `already-current`; implementation remote task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `already-current`.
- Recursive implementation submodules: sync and update/init passed; `database` initialized at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Launcher claim: attempt 1, executor `copilot`; claim commit `b526c3dc5ca0fcbaa2785b7fc6e0baabc4eb8cd0` was committed and pushed.
- Implementation commit `4fa2a60` was pushed to `origin/task/ARCH-025-BACKGROUND-014`; implementation worktree is clean and tracks that task branch.

### Deviations

- The frozen grouped/full suite is not entirely green due to the validation findings above. No unrelated tests, baselines, fixtures, scheduling code, or production behavior were changed to mask them.

### Assumptions

None

### Unresolved Issues

- Architect disposition is requested for the previously reported frozen materialization language-context assertion, billing reconciliation assertions, unavailable local PostgreSQL service, observability timeouts and missing ARCH-020 task-worktree fixture. No existing durable baseline ID covers these background suite outcomes.

### Architectural Concerns

None. The extraction remains within the background repository and introduces no new durable state or scheduling owner.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

- Reviewed implementation commit `4fa2a60125e793944f943be244ca9668bb2be0b5` and parent report commit `fc8a7541279c98f59def222f26ccb85756c5d50b` as published on their `task/ARCH-025-BACKGROUND-014` branches.
- The extraction is move-only: `RecoveryCapacityResumeProcessorService` owns the existing durable capacity-blocked resume/terminalisation lifecycle while `CheckoutRecoveryService.resumeCapacityBlockedRecovery(...)` remains the compatibility delegate. Constructor wiring is inert and the processor does not reverse-import the façade.
- R1 is preserved exactly: only durable `DETECTED` + `RECOVERY_CAPACITY_EXHAUSTED` recoveries are eligible; inactive Shop and execution eligibility short-circuit before provider work; checkout-scoped locking, durable reread and the second eligibility check remain in the same order.
- R2/R3 are preserved exactly: lookup is built only from durable recovery shop/checkout/cart/url/detectedAt; provider-error/ambiguous/bounded-limit outcomes remain thrown and retryable; not-found and found-but-completed terminalise through the same guarded transaction; the externally visible completed-checkout result intentionally remains `{ kind: "terminal", reason: "found" }`. Terminalisation still CASes only blocked `DETECTED`, writes `CANCELLED`, stamps `expiredAt`, clears block fields and creates history only after a successful update with source `recovery-capacity-resume`.
- R4 is preserved through a dynamic façade port. The constructor receives an arrow callback that resolves `this.handleCheckoutCreated` at invocation time rather than eagerly binding the original method, so existing tests/callers may replace the façade method after construction. Generation 1 calls the current façade method with one argument; later generations pass the explicit generation. Snapshot construction remains owned by BACKGROUND-010 and initiation remains owned by BACKGROUND-008.
- Post-initiation reread semantics are unchanged: a still-blocked recovery returns `capacity-exhausted`; otherwise `initiated` returns the durable status and falls back to `DETECTED` when the reread is missing. Replay after the block clears remains a no-op.
- `RecoveryCapacityResumeService` and `recovery-capacity-resume.worker.ts` are unchanged, so queue identity, repair scheduling and scheduler ownership remain outside this processor. `markRecoveryCapacityBlocked(...)` remains the BACKGROUND-008 compatibility operation and `markRecoveryMessageSent(...)` still clears the durable block fields.
- The Completion Report statement that no durable baseline covers the recurring suite outcomes is superseded by Architect review: the three billing-reconciliation failures, matured-candidate language assertion, four PostgreSQL translation failures and missing ARCH-020 fixture remain covered by `ARCH025-BACKGROUND-TEST-001`. The four observability-startup timeouts are the previously triaged preload/runtime class and cannot execute B014 code; they are not added to the durable Background baseline.

### Reviewed Files

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`
- `tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts`

### Validation Reviewed

- `npm run prisma:generate` — passed.
- `npm run build` — passed.
- Processor + capacity-resume worker suites — 19/19 passed.
- Frozen `checkout-recovery.capacity-resume.test.ts` — 19/19 passed, including replaceable-façade callback compatibility.
- `tests/unit/runtime/entrypoint-isolation.test.ts` — 10/10 passed.
- All four frozen CheckoutRecovery SHA-256 values match and frozen-file diff is empty.
- Required four-suite frozen aggregate — 77/78; the sole failure is the unchanged matured-candidate language assertion documented by `ARCH025-BACKGROUND-TEST-001`.
- Full `npm test` — 1,571 passed / 38 skipped / 12 failed plus one collection failure. Eight recurring failed identities plus the collection failure are covered by `ARCH025-BACKGROUND-TEST-001`; the four observability-preload timeouts are execution-path independent from B014 and do not block this extraction.
- `git diff --check` — passed.

### Architecture Conformance

Accepted. BACKGROUND-014 establishes one bounded owner for durable capacity-blocked resume and terminalisation without changing durable block authority, eligibility ordering, checkout locking, provider retry semantics, terminalisation transaction semantics, canonical snapshot/initiation ownership or queue/repair scheduling.

### Follow-up

`ARCH-025-BACKGROUND-015` is promoted to Ready as the final CheckoutRecovery façade task. The unrelated observability-preload/runtime timeouts remain outside B014 ownership and are not incorporated into `ARCH025-BACKGROUND-TEST-001` without same-environment baseline proof.
