---
id: ARCH-028-BACKGROUND-004
architecture_id: ARCH-028
title: Compensate generic terminally undelivered recovery usage
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 60
executor: developer
claimed_at: 2026-10-22T12:56:07Z
attempt: 1
depends_on:
  - ARCH-028-BACKGROUND-002
  - ARCH-028-DATABASE-001
  - ARCH-027-BACKGROUND-001
enables:
  - ARCH-028-BACKGROUND-011
  - ARCH-028-BACKGROUND-009
created: 2026-10-05
updated: 2026-10-22
---

# Compensate generic terminally undelivered recovery usage

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

### Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-028-BACKGROUND-004`, taking over execution and completion authority from the prior `execution_mode: agent`, `completion_mode: automatic` definition. Execution/completion modes are now `developer`/`developer`; logical ownership remains `assigned_agent: moda_background`, and task scope, dependencies, acceptance criteria and validation requirements are unchanged. The parent task metadata now records the developer claim for Attempt 1 at `2026-10-22T12:56:07Z`. The launcher preparation packet and start-of-attempt synchronization evidence must still be checked during review.

## Objective

Make the provider-status job idempotently release/compensate the exact terminally undelivered recovery source for every non-committed-purchased case, and remove the exact undelivered outbound automated-message hard-limit usage.

## Context

Compensation authority is durable FAILED/131026 `ConversationMessage` evidence plus the exact linked recovery/UsageReservation lineage. `RecoveryOutreachAttempt.status` is not an eligibility gate because it may already be `NO_RESPONSE`.

The provider-status job must call the compensation orchestrator after its status transaction on every relevant replay. If correction fails, the job fails/retries; if the message is already FAILED the retry still calls compensation.

Committed purchased-credit compensation is deliberately deferred to BACKGROUND-009 because it requires final ARCH-027 refund state. A still-RESERVED purchased source can be safely released here because no provider monetary refund exists yet.

ARCH-027-BACKGROUND-001 makes positive recovery `UsageEvent.provider` explicit for Shopify and Woo. Each new negative correction must preserve the *original committed UsageEvent* `shopId` and `provider` (and exact original correction lineage), not inherit Prisma's default `SHOPIFY` provider. Corrections must remain non-reportable to Shopify regardless of the positive source's reporting state.

## Scope

- Re-lock/re-read exact message/attempt/recovery/reservation after provider-status convergence.
- Eligibility: durable `ConversationMessage.status=FAILED`, provider code `131026`, exact recovery source; no attempt-status requirement.
- Release any eligible still-RESERVED reservation through its existing source owner.
- Compensate COMMITTED lifetime-Free, paid-included and promotional sources with one exact negative UsageEvent/counter correction and DATABASE-001 disposition. Write the correction's `shopId` and `provider` explicitly from the locked original committed recovery UsageEvent; keep its `shopifyReportState=NOT_APPLICABLE` and all Shopify-reporting identifiers null, including when the original was Shopify-reportable.
- For COMMITTED purchased source return a stable bounded `PURCHASED_COMPENSATION_REQUIRED`/equivalent result without suppression/notification side effects; BACKGROUND-009 completes it.
- Idempotently remove/delete the exact `OUTBOUND_AUTOMATED_MESSAGE` UsageEvent associated with the undelivered message so the hard limit is not consumed.
- Integrate this orchestrator into the provider-status job after the status transaction.

## Out of Scope

- COMMITTED purchased-credit source adjustment/refund holds (BACKGROUND-009).
- Provider monetary refunds.
- Reachability writes/pre-admission gate.
- Synchronous HTTP failure path.
- Missing phone.
- Merchant notification.

## Requirements

- [x] Attempt status is not compensation eligibility authority.
- [x] Message DELIVERED/READ before compensation prevents correction.
- [x] RESERVED release creates no negative UsageEvent.
- [x] COMMITTED lifetime-Free/paid-included/promotional correction is exact and idempotent.
- [x] Every negative correction preserves the original committed recovery UsageEvent's Shop and `provider` (`SHOPIFY` or `WOOCOMMERCE`), rather than a schema default, and is never submitted for Shopify external reporting.
- [x] Closed/expired source uses Option A historical-only semantics, never a cross-period make-good credit.
- [x] COMMITTED purchased returns deferred bounded outcome and does not guess ARCH-027 monetary state.
- [x] Terminally undelivered outbound message no longer consumes `OUTBOUND_AUTOMATED_MESSAGE` hard-limit usage.
- [x] Provider-status replay always re-invokes the idempotent orchestrator when durable terminal evidence still exists.
- [x] Late positive delivery after completed compensation does not claw compensation back.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Add generic compensation orchestrator using existing reservation source owners.
- [x] Add post-status provider-job invocation and retry semantics.
- [x] Implement RESERVED release all sources.
- [x] Implement lifetime-Free, paid-included and promotional COMMITTED correction/disposition with explicit original Shop/provider lineage and non-reportable correction fields.
- [x] Add committed-purchased deferred result.
- [x] Add exact outbound hard-limit usage correction/removal.
- [x] Add NO_RESPONSE eligibility, replay and late-delivery race tests.
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes DATABASE-001 compensation lineage and ARCH-027 provider-correct recovery UsageEvent semantics. Produces bounded outcomes for later reachability/notification, including release/restoration/historical/deferred-purchased results.

## Dependencies

- `ARCH-028-BACKGROUND-002`
- `ARCH-028-DATABASE-001`
- `ARCH-027-BACKGROUND-001`

## Enables

- `ARCH-028-BACKGROUND-011`
- `ARCH-028-BACKGROUND-009`

## Acceptance Criteria

- [x] WAITING/NO_RESPONSE/etc. attempt state cannot block otherwise eligible compensation.
- [x] RESERVED source is released exactly once.
- [x] Generic COMMITTED source creates exactly one negative correction and source adjustment.
- [x] On both Shopify and Woo, negative compensation uses the exact original committed UsageEvent's `shopId` and `provider`; Woo corrections are never mislabelled SHOPIFY by default, and no correction enters Shopify publication.
- [x] Closed/expired source is historical-only; no make-good credit is created.
- [x] COMMITTED purchased source is not modified by this task and returns deferred outcome.
- [x] Outbound automated-message hard-limit usage is removed exactly once for terminally undelivered message.
- [x] Provider-status job retry after prior message convergence still executes compensation.
- [x] Compensation failure makes the job retryable; duplicate retries cannot double-adjust accounting.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused unit/PostgreSQL integration for each generic source, RESERVED release, NO_RESPONSE race, replay, hard-limit correction, late-delivery race, **positive/negative UsageEvent Shop/provider parity on Shopify and Woo**, correction non-publication and duplicate replay, full Background tests/build and `git diff --check`.

Execution evidence (22 October 2026; submitted for review, not yet accepted):

- [x] Provider-status focused unit tests: 32/32 passed.
- [x] PostgreSQL compensation integration suite: 17/17 passed (including Shopify/Woo source parity, RESERVED release and replay/race cases).
- [x] `npm run build`: Prisma Client v6.19.3 generation and TypeScript compilation passed.
- [x] `git diff --check`: no whitespace errors reported after the implementation commit.
- [ ] Full Background unit suite passes or known-baseline exceptions are approved: 2,325 passed; 3 failed in files unchanged by this task. Baseline classification has not been independently verified.
- [ ] Dedicated worktree isolation, start-of-attempt synchronization and recursive implementation-submodule preparation verified against launcher evidence during review.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not make the provider-status database transaction perform external/queue work. Commit message/attempt convergence first, then invoke the idempotent compensation owner; job failure/retry supplies recovery.

Prefer a thin compensation coordinator delegating to focused eligibility, usage-source correction and outbound-hard-limit correction modules. Source-specific accounting branches must not accumulate into one large switch-heavy service.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Ready for Review — developer-executed Attempt 1, claimed at `2026-10-22T12:56:07Z`. The implementation is committed and pushed; architect review is pending. The developer has not made the explicit completion decision required by `completion_mode: developer`.

### Files Changed

Implementation repository: `moda-interact-background`, commit `6a4e4e1` (`feat(background)`), 14 files:

- `src/services/free-recovery-reservation.service.ts`
- `src/services/paid-included-recovery-reservation.service.ts`
- `src/services/promotional-recovery-reservation.service.ts`
- `src/services/purchased-recovery-reservation.service.ts`
- `src/services/recovery-delivery-compensation/automated-usage.ts`
- `src/services/recovery-delivery-compensation/committed.ts`
- `src/services/recovery-delivery-compensation/counter-adjustment.ts`
- `src/services/recovery-delivery-compensation/lineage.ts`
- `src/services/recovery-delivery-compensation/reconcile.service.ts`
- `src/services/recovery-delivery-compensation/reserved.ts`
- `src/services/recovery-delivery-compensation/types.ts`
- `src/services/whatsapp-provider-status.service.ts`
- `tests/integration/arch028-recovery-delivery-compensation.integration.test.ts`
- `tests/unit/services/whatsapp-provider-status.service.test.ts`

Parent workspace review submission: this task-definition file only. No domain `_index.md`, parent architecture file, or implementation submodule gitlink update is included.

### Work Completed

- Added a focused post-provider-status compensation coordinator with exact Shop/message/recovery/attempt/reservation/usage lineage matching and fail-closed rejection of ambiguous or cross-Shop evidence.
- Released still-RESERVED Free, paid-included, promotional and purchased sources through their existing source owners; no negative UsageEvent is created for RESERVED release.
- Added idempotent negative UsageEvent and counter correction for COMMITTED generic Free, paid-included and promotional credits, preserving the source UsageEvent's Shop/provider and excluding the correction from Shopify reporting.
- Preserved historical-only accounting for closed/expired sources; deferred COMMITTED purchased compensation to `ARCH-028-BACKGROUND-009` without provider monetary-refund or merchant-notification side effects.
- Removed the exact undelivered `OUTBOUND_AUTOMATED_MESSAGE` hard-limit usage and invoked idempotent compensation after provider-status convergence, including FAILED/131026 replay and `NO_RESPONSE` attempts.
- Added focused unit and PostgreSQL integration tests for source types, Shopify/Woo parity, HUMAN recovery-template linkage, cross-Shop rejection, replays and late-delivery ordering.
- Combined the Attempt 1 implementation patch and the Attempt 2 fixture-only correction into one developer implementation commit. The patch iterations do not imply a second task claim: task attempt remains `1`.

### Validation Results

- `npm run test -- tests/unit/services/whatsapp-provider-status.service.test.ts` — PASS (32/32).
- `npm run test:integration -- tests/integration/arch028-recovery-delivery-compensation.integration.test.ts` — PASS (17/17 PostgreSQL tests; observed 22 October 2026, 14:57 local run).
- `npm run build` — PASS (Prisma Client v6.19.3 generated; TypeScript compilation exited successfully).
- `npm run test:unit` — NOT GREEN: 2,325 passed, 3 failed (2,328 total, 231 files). Reported failing tests: `tests/unit/runtime/observability-startup.test.ts` (Shared version expectation), `tests/unit/services/checkout-refresh.test.ts` (platform-configuration `DB_UNAVAILABLE`) and `tests/unit/services/checkout-recovery/recovery-agent-context.service.test.ts` (summary expectation). None was changed by this task, but independent baseline attribution is still pending.
- `git diff --check` — PASS (no errors/output in post-commit terminal log).
- `git status --short` — only an untracked `typescript` terminal file remained in the implementation worktree; it was **not** committed.
- Authorised architect/developer review must still inspect the actual implementation branch and Completion Report rather than infer acceptance solely from these results.

### Deviations

- The Attempt 2 correction changed integration-test fixtures only, to satisfy existing database constraints. No production source needed correction from that failure set.
- Implementation changes were applied from portable patches. Source-level tests are evidenced, but the launcher preparation packet, complete start-of-attempt synchronization and recursive submodule preparation have not been supplied for independent verification.
- Full Background unit validation is not green. The three failures are disclosed rather than assumed to be accepted baseline conditions.

### Assumptions

- The original committed recovery UsageEvent owns the authoritative Shop/provider/accounting lineage.
- FAILED/131026 remains the exact provider-terminal compensation eligibility contract for this task; uncertain dispatch is separately owned by `ARCH-028-BACKGROUND-013`.
- COMMITTED purchased-credit monetary handling remains the responsibility of `ARCH-028-BACKGROUND-009`.

### Unresolved Issues

- Review must establish whether the three unit failures are pre-existing documented baseline conditions or require separate corrections before acceptance.
- Launcher-resolved physical parent/implementation isolation, parent/implementation branch synchronization, and recursive submodule-preparation evidence require verification. The developer claim itself is recorded in task metadata; the preparation packet is not part of the supplied logs.
- Parent task-branch commit and push of this review submission remain developer actions.

### Architectural Concerns

- No request is made to extend compensation to other provider codes or committed purchased-credit monetary flows. Their existing ARCH-028 task boundaries remain unchanged.
- Do not mark this task Accepted/Complete solely because the focused suites pass; review the code and outstanding validation/worktree evidence.

### Git / VCS

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-004`, shown in the developer's shell and supplied ZIP; branch `task/ARCH-028-BACKGROUND-004` confirmed by the developer's `git branch --show-current` output.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-004`, shown in the execution logs; implementation branch `task/ARCH-028-BACKGROUND-004` confirmed after commit.
- Developer task claim: `executor: developer`, `claimed_at: 2026-10-22T12:56:07Z`, `attempt: 1`, taken from this parent task definition; no new claim or attempt increment is requested by this submission.
- Implementation commit: `6a4e4e1` (`feat(background)`); `git push -u origin task/ARCH-028-BACKGROUND-004` succeeded on 22 October 2026.
- Actual launcher-resolved canonical primary workspace root, start-of-attempt sync logs, and submodule preparation evidence: not supplied; verify before acceptance. Correct worktree names/branches alone do not prove the full isolation policy.
- Parent branch review-submission commit/push: pending. Do not stage an implementation submodule gitlink or merge to `main` as part of this task-definition-only patch.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
