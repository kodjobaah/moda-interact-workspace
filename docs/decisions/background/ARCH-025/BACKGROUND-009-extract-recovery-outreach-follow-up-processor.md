---
id: ARCH-025-BACKGROUND-009
architecture_id: ARCH-025
title: Extract recovery outreach follow-up processor
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-025-BACKGROUND-008
enables:
  - ARCH-025-BACKGROUND-010
created: 2026-10-02
updated: 2026-10-03
---

# Extract recovery outreach follow-up processor

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract execution of a due no-response recovery follow-up into a bounded processor that reuses the existing follow-up scheduler and BACKGROUND-008 confirmed-send finalisation without changing admission, engagement or duplicate-send semantics.

## Context

`processRecoveryOutreachFollowUp(...)` is a distinct lifecycle from initial outreach: it runs under a checkout lock, determines due/terminal/engaged state, CAS-claims the initial attempt as no-response, creates sequence 2, re-checks shop execution eligibility and then repeats billing/template/provider admission for the follow-up. The existing `recoveryOutreachFollowUpService` remains the queue scheduling owner.

## Scope

Authorised implementation surface:

```text
src/services/checkout-recovery.service.ts
src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts
tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts
```

A directly adjacent repository-internal types file is permitted only where required to keep the extracted capability coherent.

## Out of Scope

follow-up queue scheduling service; initial outreach; snapshot mapping; materialisation; checkout/order/capacity/agent-context flows.

## Requirements

### Common ARCH-025 CheckoutRecovery invariants

- This is a **move-only structural refactor**. Do not change recovery eligibility, outreach policy, billing/capacity economics, candidate/order correlation, queue identity, provider protocol, retry behaviour, authorization, durable lifecycle semantics or CommerceAgent context meaning.
- Preserve the exact compatibility surface from `src/services/checkout-recovery.service.ts`: `CheckoutRecoveryService`, `checkoutRecoveryService`, `MaturedCandidateMaterializationResult`, `CheckoutRefreshResult`, and every current public method: `handleCheckoutCreatedContract`, `materializeMaturedCandidate`, `recordExternalActivity`, `handleCheckoutUpdatedContract`, `handleCartActivityContract`, `handleOrderCompletedContract`, `upsertRecovery`, `attachCustomer`, `resolveRecipient`, `markRecoveryMessageSent`, `handleOrderCompleted`, `handleCheckoutCreated`, `processRecoveryOutreachFollowUp`, `markRecoveryCapacityBlocked`, `resumeCapacityBlockedRecovery`, `getAgentContext`, `getAgentContextForStandaloneConversation`.
- Preserve the constructor `(billingService: RecoveryBillingService = recoveryBillingService)`. Existing workers and Commerce callers continue using the `checkoutRecoveryService` singleton; do not migrate worker entrypoints/callers as part of extraction.
- Extracted modules MUST NOT import `checkout-recovery.service.ts`; dependency direction is façade -> collaborator. Symbols moved out of the façade that are currently exported must be compatibility re-exported from it.
- Collaborator constructors are inert wiring only. Do not perform Prisma/provider/Redis/queue/environment I/O or eager model access during construction.
- Any extracted collaborator/finaliser that performs recovery billing MUST receive and reuse the exact `RecoveryBillingService` instance supplied to the `CheckoutRecoveryService` constructor. Do not silently fall back to the module singleton when a caller supplied a custom/test billing service.
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

### R1 — preserve checkout-scoped execution

Load only the durable lock target first and retain `PendingRecoveryCandidateService.withCheckoutLock(shopId, checkoutToken, ...)` around the due-state reread and all follow-up decisions. Missing recovery remains `suppressed/missing-recovery`.

### R2 — preserve due/engagement decision order

Within the lock preserve: recovery + ordered attempts + conversation/customer load; `not-due`; terminal suppression; already-sent sequence-2 suppression; inbound-message lookup from `initial.sentAt`; engaged marking; `markNoResponseIfWaiting(...)` CAS; lost-CAS reread via `getOrCreate(...)`; then sequence-2 creation. Do not move customer-response detection after the no-response claim.

The current `not-due` prerequisite also requires a recovery conversation and a durable `customer.phone`; follow-up does **not** fall back to `TEST_WHATSAPP_RECIPIENT`. The `already-sent` guard is specifically a sequence-2 attempt in `WAITING_FOR_RESPONSE`; do not broaden it to all sequence-2 statuses. Preserve the current terminal list/order (`COMPLETED`, `EXPIRED`, `CANCELLED`) after the not-due prerequisites.

### R3 — preserve admission/provider flow

Execution eligibility is rechecked after the sequence-2 attempt exists and before template/billing/provider work; denial marks that attempt `CANCELLED` with the exact execution-denial code. Template-unavailable marks the follow-up attempt `FAILED` with fixed failure code `TEMPLATE_UNAVAILABLE`. Billing admission and revalidation retain their current attempt-level `CAPACITY_BLOCKED` outcomes with the returned reason as `failureCode`; this follow-up path does **not** newly call `markRecoveryCapacityBlocked(...)` on the durable recovery. Template selection continues using the durable conversation language/country rather than the initial-outreach null-language/shop-fallback rule. Provider send uses the same deterministic idempotency key and BACKGROUND-008 finalisation. Preserve the current `providerSendCompleted` distinction: it becomes true as soon as `sendTemplate(...)` returns (including suppressed results), so errors during duplicate/suppression/finalisation handling after that point are not routed to `handleProviderFailure(...)`.

Duplicate handling retains BACKGROUND-008 semantics: confirmed durable admission can converge; `PENDING` and missing durable admission throw; other non-confirmed durable statuses release the admission and mark the attempt `FAILED` with suppression reason `duplicate`.

### R4 — add missing characterization coverage

Add focused coverage for at least: missing/not-due, terminal, already-sent, engaged-before-due, lost no-response CAS, shop ineligible, template unavailable, admission block, revalidation block, provider failure, duplicate confirmed send, duplicate pending/missing durable message and successful sequence-2 send.

## Work Items

- [x] Extract the follow-up processor and leave `processRecoveryOutreachFollowUp` as façade delegate.
- [x] Reuse BACKGROUND-008 confirmed-send finalisation.
- [x] Keep `recoveryOutreachFollowUpService` as scheduling-only canonical owner.
- [x] Add focused state/race/provider characterization tests.
- [ ] Prove frozen assets remain byte-identical and pass. Hashes and diffs prove byte identity; the combined run retains the documented matured-candidate baseline failure.

## Interfaces / Contracts

Repository-internal extraction only. The public worker/application contract remains `CheckoutRecoveryService` / `checkoutRecoveryService`; canonical adjacent service contracts are consumed rather than redefined.

## Dependencies

- `ARCH-025-BACKGROUND-008`

## Enables

- `ARCH-025-BACKGROUND-010`

## Acceptance Criteria

- [x] Follow-up execution is isolated from initial outreach and queue scheduling.
- [x] Checkout lock and no-response CAS/engagement race semantics are unchanged.
- [x] No second billing, scheduling or provider-send implementation is introduced.
- [x] Existing worker call through `checkoutRecoveryService.processRecoveryOutreachFollowUp` remains compatible.

## Validation

- [x] `npm run prisma:generate` (also run by `npm run build`)
- [x] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/unit/services/matured-candidate.materialization.test.ts':'28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb','tests/unit/services/checkout-refresh.test.ts':'3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f','tests/unit/services/order-recovery-correlation.test.ts':'7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf','tests/unit/services/checkout-recovery.capacity-resume.test.ts':'8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected SHA-256 values
- [x] Frozen regression hashes all match the specified SHA-256 values.
- [x] `git diff` for all four frozen files is empty.
- [ ] Combined frozen regression command passes; the unchanged matured-candidate test has its documented baseline failure, while the other three files pass.
- [x] `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts` passes (10/10).
- [x] Full `npm test` introduces no new persistent failing test/suite identity; existing baseline and isolated timeout results are documented below.
- [x] `npm run build` succeeds.
- [x] `git diff --check` passes.
- [x] `npm test -- tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts` passes (17/17).

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Background task.

## Implementation Notes

None

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`
- `tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts`

### Work Completed

- Extracted the existing follow-up execution body into `RecoveryOutreachFollowUpProcessorService`; `CheckoutRecoveryService.processRecoveryOutreachFollowUp(...)` remains the compatibility delegate used by the existing worker.
- The processor receives the exact façade `RecoveryBillingService` instance and shared BACKGROUND-008 `RecoveryOutreachFinalizationService`. It does not import the façade or duplicate confirmed-send validation/finalisation.
- Preserved the initial lock-target read and `withCheckoutLock(shopId, checkoutToken, ...)` boundary, due/terminal/already-sent/engagement ordering, no-response CAS and lost-CAS reread, sequence-2 creation, eligibility/template/billing/provider order, deterministic `recovery-outreach:<attemptId>` idempotency, and `providerSendCompleted` error classification.
- Left `recoveryOutreachFollowUpService` as scheduling owner. The extracted sequence-2 path does not call it directly or newly durably block the recovery on capacity failures.
- Added 17 focused tests for missing/not-due, terminal and already-sent suppression, sequence-2 status guard, inbound engagement before CAS, lost-CAS convergence, shop denial, template unavailability, admission/revalidation blocks, provider failure, confirmed/pending/missing/non-confirmed duplicate messages, successful sequence-2 finalisation, and checkout-lock scope.

### Execution Provenance

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-BACKGROUND-009
parent branch: task/ARCH-025-BACKGROUND-009
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-BACKGROUND-009
implementation branch: task/ARCH-025-BACKGROUND-009
shared workspace checkout mutated/switched for this task: no
another task worktree reused: no

launcher preparation: passed; Attempt 1 claimed by copilot at 2026-10-03T01:14:13Z
parent claim commit: 7cc59106d6a1d976152b02ca4095fdd6593ed3de
implementation commit: 5264114 (refactor(background): extract recovery follow-up processor)
implementation task branch pushed: origin/task/ARCH-025-BACKGROUND-009, explicit non-force refspec
dependency ARCH-025-BACKGROUND-008: Complete; gate passed
launcher preparation recorded origin/main as already current; task-branch fast-forward was not needed then
origin/main subsequently advanced after worktree creation; implementation remained on launcher-created base b49ffa0 and did not merge concurrent main changes
recursive submodule sync/update: passed
database submodule: cfeeb12456b4e05067a96857a8c47837d7e33bbd
```

### Validation Results

`npm ci` installed the checked-in lockfile dependencies into the fresh implementation worktree; no dependency manifest or lockfile changes were made.

- `npm run prisma:generate`: passed as part of the production build.
- Focused follow-up processor suite: 17/17 passed.
- `npm test -- tests/unit/runtime/entrypoint-isolation.test.ts`: 10/10 passed.
- All four frozen asset hashes match their required values and their Git diff is empty.
- Combined four-file frozen regression command: 77/78 tests passed; the sole failure is the documented `ARCH025-BACKGROUND-TEST-001` matured-candidate language-metadata assertion. The other three frozen suites passed.
- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `git diff --check`: passed.
- Final full `npm test`: 9 failed, 1,446 passed, 38 skipped across 118 files (one suite-loading failure). The eight durable failing test identities and missing ARCH-020 fixture failure match `ARCH025-BACKGROUND-TEST-001`. One observability-startup case also timed out in the full suite; the full startup file subsequently passed 10/10 in isolation. A GenAI metrics timeout from the preceding full run passed 1/1 in isolation and did not recur in the final run. These intermittent timeouts introduced no persistent failing identity. No follow-up-processor test failed.

### Deviations

The literal requirement that all frozen tests pass remains unmet solely because the unchanged matured-candidate frozen test has its durable baseline failure. Frozen-file identity and no-diff requirements are satisfied, and the three other frozen suites pass. The full suite remains non-green for the documented baseline plus one isolated-only observability-startup timeout. No task-local test failure or persistent new failure identity was observed.

### Assumptions

`ARCH025-BACKGROUND-TEST-001` remains the authoritative baseline for the eight durable Background failure identities and missing ARCH-020 fixture. Intermittent full-suite timeouts are treated as transient only where the affected test file passes in isolation.

### Unresolved Issues

The full suite and combined frozen suite remain baseline-red as detailed above. No implementation blocker remains for architect review.

### Architectural Concerns

None identified.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

Reviewed implementation `5264114a967d87929a31d48f14b611ad58be59a7` against launcher base `b49ffa0db70c7fd555e9821f512bb0863fbc51fd` and parent report `6b06309a571dbc98d5277c9243fa2fa48adda322`. The implementation is a move-only extraction of `processRecoveryOutreachFollowUp(...)`: the initial durable lock-target read, checkout-scoped lock, due/terminal/already-sent/engagement ordering, no-response CAS and lost-CAS reread, sequence-2 creation, execution-eligibility/template/billing/provider order, deterministic idempotency key, duplicate convergence, and `providerSendCompleted` error boundary are preserved.

`CheckoutRecoveryService.processRecoveryOutreachFollowUp(...)` remains the worker-facing façade delegate. The extracted processor receives the exact `RecoveryBillingService` supplied to the façade and reuses the same BACKGROUND-008 `RecoveryOutreachFinalizationService`; it introduces no second billing/provider/follow-up scheduling implementation and does not durably block the recovery on follow-up capacity failures.

The four frozen assets remain byte-identical. Their combined run is truthfully 77/78 because the unchanged matured-candidate language-metadata assertion is governed by `ARCH025-BACKGROUND-TEST-001`; the other three frozen suites pass. Full `npm test` contains the eight durable baseline failures plus the known missing ARCH-020 fixture and one observability-startup timeout that passes 10/10 when rerun in isolation. That isolated timeout is not added to the durable baseline. No changed follow-up-processor test failed and no persistent new failure identity is accepted.

### Reviewed Files

- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`
- `tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts`
- `docs/decisions/background/ARCH-025/BACKGROUND-009-extract-recovery-outreach-follow-up-processor.md`

### Validation Reviewed

- focused follow-up processor suite: 17/17 passed
- entrypoint isolation: 10/10 passed
- frozen hashes: all four required SHA-256 values matched and frozen diffs were empty
- combined frozen run: 77/78; sole failure is the durable matured-candidate baseline identity
- production build / Prisma generation: passed
- `git diff --check`: passed
- full suite: 1,446 passed, 9 failed, 38 skipped plus the known fixture-loading failure; eight durable failing test identities match `ARCH025-BACKGROUND-TEST-001`, and the one extra observability timeout passed on isolated rerun

### Architecture Conformance

Conformant. The follow-up execution owner is bounded, façade compatibility and injected billing identity are preserved, scheduling remains with the existing canonical owner, and provider/billing/durable lifecycle semantics are unchanged.

### Follow-up

Promote `ARCH-025-BACKGROUND-010` to Ready. Leave the literal combined frozen-suite pass claim unchecked while the durable matured-candidate baseline failure exists; later tasks must use the no-regression baseline rather than rewriting the frozen assertion.
