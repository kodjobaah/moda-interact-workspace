---
id: ARCH-028-BACKGROUND-002
architecture_id: ARCH-028
title: Converge recipient-undeliverable WhatsApp delivery failures
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-028-BACKGROUND-001
  - ARCH-028-MESSAGING-001
enables:
  - ARCH-028-BACKGROUND-004
created: 2026-10-03
updated: 2026-10-12
---

# Converge recipient-undeliverable WhatsApp delivery failures

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Classify exact bounded Meta code `131026` as the ARCH-028 terminal recipient-delivery condition, converge linked recovery/follow-up state safely, and make later compensation eligibility independent of `RecoveryOutreachAttempt.status`.

## Context

A delayed provider failure can arrive after the follow-up processor has already moved the initial attempt to `NO_RESPONSE`. Provider delivery authority therefore belongs to `ConversationMessage`, not the attempt response-lifecycle enum.

## Scope

- Add one pure classifier: `131026 -> RECIPIENT_UNDELIVERABLE`, other/absent -> unclassified.
- Resolve the exact linked `RecoveryOutreachAttempt` through `outboundMessageId`; never correlate by phone/customer/timestamp.
- If the exact attempt is still `WAITING_FOR_RESPONSE`, guardedly move it to `FAILED` with `WHATSAPP_RECIPIENT_UNDELIVERABLE` inside the existing provider-status transaction.
- If attempt is already `NO_RESPONSE`, `ENGAGED`, `CANCELLED`, `CAPACITY_BLOCKED` or `FAILED`, do not overwrite its response lifecycle merely to make compensation possible.
- Make due follow-up processing consult authoritative failed-message evidence before `markNoResponseIfWaiting`, billing or provider work.

## Out of Scope

- Usage release/compensation.
- Recipient suppression.
- Hard-limit correction.
- Synchronous HTTP rejection.
- Missing phone.
- Merchant notification.

## Requirements

- [x] Exact `131026` is the only terminal-recipient code in ARCH-028 v1.
- [x] A provider FAILED message linked to a recovery can be financially compensatable regardless of attempt status.
- [x] `WAITING_FOR_RESPONSE -> FAILED` remains a useful convergence transition but is not a financial eligibility precondition.
- [x] `NO_RESPONSE` race cannot permanently block later compensation.
- [x] DELIVERED/READ wins before compensation and prevents terminal classification from acting.
- [x] A due follow-up whose initial message is durably FAILED/131026 performs no policy/billing/provider send.
- [x] No permanent `hasWhatsApp` assertion is created.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Add pure provider-code classifier/tests.
- [x] Resolve linked attempt/recovery from message relation.
- [x] Guard WAITING -> FAILED convergence in the provider-status transaction.
- [x] Preserve other attempt lifecycle states without using them as compensation gates.
- [x] Add failed-message follow-up suppression before no-response/billing/provider work.
- [x] Add NO_RESPONSE race and duplicate/out-of-order tests.
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes v3 `failure.providerCode`; introduces repository-local classification `RECIPIENT_UNDELIVERABLE` and stable attempt failure code `WHATSAPP_RECIPIENT_UNDELIVERABLE` when WAITING can be converged.

## Dependencies

- `ARCH-028-BACKGROUND-001`
- `ARCH-028-MESSAGING-001`

## Enables

- `ARCH-028-BACKGROUND-004`

## Acceptance Criteria

- [x] `131026` classifies terminal-recipient; other/absent codes do not.
- [x] Linked WAITING attempt can become FAILED idempotently.
- [x] Existing NO_RESPONSE/ENGAGED/etc. state is not overwritten solely for compensation.
- [x] Later compensation can use FAILED/131026 message + exact reservation lineage even when attempt is not FAILED.
- [x] Due follow-up no-ops before billing/provider work when authoritative initial delivery failed.
- [x] Positive delivery/read and unrelated failures retain existing behaviour.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Run focused classifier/provider-status/follow-up tests, repository unit/full test/build gates and `git diff --check` as declared by the current repository.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not redesign `RecoveryOutreachStatus` to carry two independent dimensions. Message delivery and attempt response lifecycle stay separate; later compensation reads both durable associations without requiring an artificial state rewrite.

Keep terminal-recipient classification and recovery/attempt convergence as focused units. Do not bury the provider-code classifier or NO_RESPONSE race policy inside the follow-up processor or provider-status consumer.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Ready for Architect review (Attempt 1, 2026-10-12). Implementation commit: `3a48d4eb974bcde1835050d0cd8fdcb8b67b98d4`.

### Files Changed
Added `src/domain/whatsapp-recipient-failure.ts` and `tests/unit/domain/whatsapp-recipient-failure.test.ts`. Updated `src/services/whatsapp-provider-status.service.ts`, `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`, and their focused tests.

### Work Completed
Added a pure exact-match classifier: only `131026` maps to `RECIPIENT_UNDELIVERABLE`; all other, absent, or non-exact codes remain unclassified.

The existing serializable provider-status transaction now loads the exact linked `recoveryOutreachAttempt` relation from the `ConversationMessage`. For accepted FAILED/131026 evidence, it compare-and-sets only a `WAITING_FOR_RESPONSE` attempt to `FAILED`, recording `WHATSAPP_RECIPIENT_UNDELIVERABLE` and the failure time. Other attempt lifecycle states are not rewritten; the durable failed message, provider code, and exact attempt/recovery link remain available independently of attempt status. Later DELIVERED/READ evidence remains authoritative at the message layer.

Due follow-up processing now checks the initial attempt's exact `outboundMessageId` before no-response claiming. A durably FAILED message with exact provider code 131026 is suppressed before policy resolution, further attempt creation, billing, template selection, or provider send. Unrelated codes and positive delivery states retain the existing path. No compensation execution, schema/migration, reachability, hard-limit, or merchant-notification behavior was added; compensation remains outside this task's scope.

### Validation Results
PASS: focused classifier/provider-status/follow-up suite, 52 tests across 3 files.

PASS: `npm run build` (Prisma Client generation and TypeScript compilation), `npm run prisma:validate`, changed-file diagnostics (no errors), and `git diff --check`.

NOT PASS: `npm run test:unit` and `npm test` each reported 2,084 passed and 6 failed across 204 files. The same six failures are confined to untouched `tests/unit/services/checkout-refresh.test.ts`; its fixture lacks `pendingRecoveryCandidateService.withCheckoutLock`, so execution fails before the checkout-refresh assertions. No test in the changed provider-status/follow-up paths failed. Both full repository gates were run and the failures are reported for Architect review.

### Deviations
The fresh implementation worktree initially had no Prisma Client. A `pnpm exec` invocation attempted dependency setup and hit pnpm's ignored-build-script gate; Prisma Client was generated using the repository-declared Prisma CLI, after which focused tests and the build passed. The generated untracked pnpm YAML files were removed; no dependency manifest or lockfile change remains.

### Assumptions
ARCH-028-BACKGROUND-004 owns compensation execution. BACKGROUND-002 preserves durable FAILED/131026 message evidence and exact attempt/recovery lineage without using the mutable attempt status as an eligibility condition.

### Unresolved Issues
The full repository unit/test gates have six unrelated failures in `tests/unit/services/checkout-refresh.test.ts` because the fixture does not implement the current checkout-lock port. The task-owned focused suite, build, schema validation, diagnostics, and diff checks pass.

### Architectural Concerns
No new architecture concerns identified. The classifier is 6 lines; touched existing production modules are 270 lines (`whatsapp-provider-status.service.ts`) and 194 lines (`recovery-outreach-follow-up-processor.service.ts`), both below the 300-line ceiling.

### Attempt 2 — Workflow Evidence Correction

#### Status

Evidence-only correction complete; returned for Architect review. No implementation source or test files were changed in Attempt 2. Attempt 1's implementation commit remains `3a48d4eb974bcde1835050d0cd8fdcb8b67b98d4`.

#### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-002`, branch `task/ARCH-028-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-002`, branch `task/ARCH-028-BACKGROUND-002`.
- Attempt 2 used only these launcher-resolved dedicated worktrees. The shared workspace checkout and shared implementation source checkout were not switched or mutated, and no other task worktree was reused.
- The launcher reused the canonical worktrees. The implementation worktree began at `3a48d4eb974bcde1835050d0cd8fdcb8b67b98d4`, matching the reviewed Attempt 1 implementation commit. Attempt 1's report omitted physical paths, so its historical execution location cannot be independently reconstructed beyond this launcher evidence.

#### Start-of-Attempt Synchronization

- Parent `task/ARCH-028-BACKGROUND-002`: remote task-branch fast-forward `not-needed`; `origin/main` incorporation `already-current`; prepared HEAD `258ebd674bd4d807c77abede1206549a8e3ca452`.
- Implementation `task/ARCH-028-BACKGROUND-002`: remote task-branch fast-forward `not-needed`; `origin/main` incorporation `already-current`; prepared HEAD `3a48d4eb974bcde1835050d0cd8fdcb8b67b98d4`.
- The launcher claim for Attempt 2 was committed and pushed as `521e6e0a456022c6e201541c5751ec0c1692226e`.

#### Recursive Submodules

- `git submodule sync --recursive`: passed.
- `git submodule update --init --recursive`: passed.
- Recursive status: ready; initialized `database` at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

#### Validation Results

- Focused classifier/provider-status/follow-up suites: passed, 52 tests across 3 files.
- `npm run build`: passed (Prisma Client generation and TypeScript compilation).
- `npm run prisma:validate`: passed.
- `npm run test:unit`: not passed; 2,084 passed and the same 6 failed across 204 files in untouched `tests/unit/services/checkout-refresh.test.ts`.
- `npm test`: not passed; 2,084 passed and the same 6 failed across 204 files in untouched `tests/unit/services/checkout-refresh.test.ts`.
- Each of the six failures occurs before its checkout-refresh assertion because the test fixture lacks `pendingRecoveryCandidateService.withCheckoutLock`; no fixture change was made, per review scope.
- Diagnostics for the classifier, provider-status service, and follow-up processor: no errors. `git diff --check`: passed.
- Both task worktrees were clean after validation; no implementation diff or new implementation commit was created in Attempt 2.

#### Deviations and Unresolved Issues

No implementation deviation. Attempt 1's six full-suite fixture failures remain unchanged and are reported as failures, not passes. Attempt 1's physical worktree paths were not recorded in its report; the prepared Attempt 2 packet confirms the reviewed implementation commit is present in the canonical implementation worktree, but does not provide retrospective observation of where Attempt 1 commands were originally run.

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-12); evidence-only correction.

### Review Notes

The task-owned implementation is architecturally conformant on source inspection. The exact Meta `131026` classifier is pure and bounded; provider-status processing resolves the precise recovery outreach attempt through the ConversationMessage relation and applies a guarded WAITING_FOR_RESPONSE -> FAILED transition in the existing Serializable transaction. Other attempt response lifecycle statuses remain unchanged, preserving FAILED/131026 message evidence for later compensation independent of the mutable attempt status. The due follow-up checks its initial outbound message before no-response claiming, policy, billing, and provider actions. Positive DELIVERED/READ precedence and unrelated codes are respected. Production file sizes meet the task's maintainability requirement. No source/test change is required by this review.

The Completion Report does NOT record the mandatory launcher-resolved physical isolation, start-of-attempt synchronization, or recursive implementation-submodule preparation evidence. This is a workflow-evidence deficiency under docs/agent-worktree-isolation-policy.md and the architect role policy; the developer's statement that the branches are clean and synchronized does not replace that evidence.

### Reviewed Files

- src/domain/whatsapp-recipient-failure.ts
- src/services/whatsapp-provider-status.service.ts
- src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts
- tests/unit/domain/whatsapp-recipient-failure.test.ts
- tests/unit/services/whatsapp-provider-status.service.test.ts
- tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts
- tests/unit/services/checkout-refresh.test.ts (untouched full-suite failure fixture)
- src/services/checkout-recovery/checkout-event-orchestrator.service.ts (untouched checkout-lock caller)
- ARCH-028 parent architecture and this task's Completion Report

### Validation Reviewed

Agent-reported: focused 52 tests passed; npm run build, npm run prisma:validate, changed-file diagnostics, and git diff --check passed. Both npm run test:unit and npm test reported 2,084 passing and six failing tests, all in untouched tests/unit/services/checkout-refresh.test.ts. Static inspection confirms its pendingRecoveryCandidateService mock lacks withCheckoutLock, which the existing checkout-event orchestrator calls. No task-changed module is responsible for that port; the failures remain an explicitly documented, unresolved separate fixture issue, not a task-owned regression. The pre-task suite was not independently rerun, and these full suites are not claimed to pass.

Remote verification: implementation commit 3a48d4eb974bcde1835050d0cd8fdcb8b67b98d4 and parent report commit e1f517d435afe656d9857e86018b1033a9782ebe each match the corresponding origin/task/ARCH-028-BACKGROUND-002 branch tip. Reviewed file Git blobs match the submitted archive. Developer-machine worktree paths and physical isolation were not independently observed.

### Architecture Conformance

Code: conforms to ARCH-028-BACKGROUND-002 scope, repository ownership, exact linked-message authority, response-lifecycle separation, bounded provider-code classification, idempotent convergence, and focused modularity. Compensation/reachability/hard-limit correction remain correctly outside this task.

Workflow: pending the required Completion Report evidence. No implementation rework is requested solely to produce a new code commit.

### Follow-up

A1-R1 — Workflow-evidence correction (no runtime code or test edits requested):

1. Reclaim this SAME task via the canonical `/moda-task ARCH-028-BACKGROUND-002` launcher only after this review patch has been committed/pushed; preserve the existing accepted source and historical Attempt 1 report. The next claim increments to Attempt 2.
2. In the Attempt 2 Completion Report, record the launcher-resolved canonical workspace root, parent task worktree path and matching branch, implementation task worktree path and matching branch; explicitly attest that neither shared/default checkout nor another task worktree was used for task execution.
3. Record for BOTH task worktrees whether the remote task-branch fast-forward and origin/main incorporation were performed or unnecessary. Record the prepared execution packet's recursive implementation-submodule sync/update/status results, or faithfully reproduce equivalent verified evidence if the original packet is unavailable.
4. If the prior execution was actually performed in a shared/default or incorrect task worktree, report non-conformance, restore the canonical launcher-resolved worktrees, check out the already-pushed task branch there, rerun required validation there, and record the truthful results; do not create unrelated code churn or fabricate a new implementation commit.
5. Reconcile and report the six unchanged checkout-refresh fixture failures without fixing that unrelated fixture within BACKGROUND-002. Leave full-suite checks marked as failures, not passes.
6. Submit Attempt 2 with the updated Completion Report, status review, claim cleared, both required task branches pushed, and Architect Review left unchanged. STOP; do not begin BACKGROUND-004 or edit any _index.md.

Return the task to ready at attempt 1, with executor and claimed_at null. BACKGROUND-004 remains gated by its complete dependency set.
