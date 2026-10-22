---
id: ARCH-028-BACKGROUND-009
architecture_id: ARCH-028
title: Compensate committed purchased recovery credit after terminal delivery failure
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 85
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-BACKGROUND-008
  - ARCH-027-BACKGROUND-005
enables:
  - ARCH-028-SYSTEM-TEST-001
created: 2026-10-07
updated: 2026-10-23
---

**2026-10-22 dependency reconciliation:** Promoted `pending -> ready` after ARCH-028-BACKGROUND-008 completed. All explicit dependencies (ARCH-028-BACKGROUND-004, ARCH-028-BACKGROUND-008 and ARCH-027-BACKGROUND-005) are complete. This is eligibility only; the task remains unclaimed (`executor: null`, `claimed_at: null`, `attempt: 0`).

## Developer Takeover

The developer explicitly invoked `/moda_developer_create ARCH-028-BACKGROUND-009`, taking execution and completion authority from the agent-owned definition. The task scope, dependencies, acceptance criteria and validation expectations are unchanged; `assigned_agent: moda_background` remains the logical repository owner. The takeover preserves the ready, attempt-0 state; canonical preparation will claim Attempt 1 as `developer` only after synchronization and dependency gates pass.

# Compensate committed purchased recovery credit after terminal delivery failure

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Extend the accepted generic ARCH-028 compensation orchestrator to correct a COMMITTED purchased recovery-credit source using the final authoritative ARCH-027 purchase/refund state, then continue the same suppression/notification pipeline.

## Context

Generic compensation is intentionally not gated by ARCH-027-BACKGROUND-005. Only committed purchased-credit cases need final provider-refund semantics. RESERVED purchased sources were already releasable by BACKGROUND-004. The purchased negative correction follows the same provider-attribution invariant as BACKGROUND-004: copy the original committed `UsageEvent.shopId` and `provider` explicitly; never rely on the Prisma default `SHOPIFY`, and never make a correction Shopify-reportable.

The current trigger remains correlated `FAILED/131026` under the approved ARCH-028 policy. BACKGROUND-013 must call this purchased-source owner for any eventual *separately approved* general delivery-failure correction, not create a new refund/credit ledger. Its uncertain-send commitment/repair is a different lifecycle operation.

## Scope

For the exact purchased lot linked by the original reservation:

- if ACTIVE/COMPLETED and not held/refunded, decrement committed and restore exact lot/currentAmount; completed lot may become ACTIVE; disposition `RESTORED_SPENDABLE`;
- if held by one live ARCH-027 refund, correct usage while keeping restored quantity unavailable in the existing refund hold; disposition `HELD_FOR_REFUND`;
- if already provider-refunded/terminal, perform historical aggregate correction only without reopening lot/refund; disposition `HISTORICAL_ONLY`;
- incoherent purchase/refund states fail closed for operator attention;
- never create/reopen a provider monetary refund because delivery failed;
- after successful correction, reuse BACKGROUND-011 reachability and BACKGROUND-008 notification owners;
- use the reachability writer only for exact `131026`; future approved non-`131026` financial corrections receive a bounded `not-applicable` reachability outcome and can be notified without claiming recipient suppression;
- accept only exact, Shop-checked message -> recovery attempt -> purchased reservation/lot lineage for automated and recovery-linked merchant follow-up templates; exclude unlinked HUMAN_TEXT;
- for every committed purchased negative `UsageEvent`, preserve the exact original committed event's Shop/provider/correction lineage and set Shopify-reporting state to `NOT_APPLICABLE`, with no Shopify-reporting identifiers.
- **Architect-approved, 2026-10-22:** reconcile five independently identified pre-existing Background full-suite test failures **within BG009** while completing this task. Limit the change to exact Shared runtime pin assertion, checkout history-ordering test moderation fixture, inbound raw-admission behavioural assertions, and recovery context's unproven summary expectation. These are test-only corrections; do not change production behaviour, database schema, dependencies, or the purchased compensation policy.

## Out of Scope

- Generic lifetime-Free/paid/promotional compensation.
- New refund attempt/provider API call.
- New make-good bucket.
- Broader non-`131026` compensation until the parent architecture and Database compensation-reason contract are accepted; uncertain-send commitment and crash repair (BACKGROUND-013).
- Production changes to inbound abuse admission, moderation policy/credential fail-closed enforcement, conversation summary provenance, or Shared package version merely to satisfy baseline tests.

## Requirements

- [x] Consume accepted ARCH-027 purchase/refund state rather than reconstructing old state.
- [x] One durable compensation correction/disposition per reservation.
- [x] Purchased negative compensation inherits the original event's exact Shop/provider on both platforms and is not externally Shopify-reportable.
- [x] Live refund hold remains held; provider-refunded source remains closed.
- [x] No second provider refund attempt is created.
- [x] Reachability/notification only follow successful correction.
- [x] Non-`131026` errors do not cause purchased-credit compensation under the current contract; a future approved wider predicate must reuse the exact purchased strategy with a truthful reason.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.
- [x] Five architect-approved baseline-test corrections assert the **existing runtime contract**, including exact Shared `2.5.0`, content-moderation fail-closed, pre-routing raw abuse admission, and withholding of summaries without moderation provenance; no production safeguards are relaxed.

## Work Items

- [x] Extend compensation orchestrator for committed purchased source.
- [x] Add active/completed, live-refund, refunded and incoherent-state tests, including provider-aware negative correction attribution for Shopify and Woo.
- [x] Reuse suppression/notification pipeline.
- [x] Add provider-status replay/idempotency tests.
- [x] Test exact recovery-template source lineage (including HUMAN sequence-2 where already durably linked) and reject unrelated HUMAN_TEXT/cross-Shop or ambiguous provider evidence.
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.
- [x] Align the observability startup test with the architecture-approved exact Shared dependency `2.5.0`, without changing `package.json` or installed dependency versions.
- [x] Isolate the checkout-refresh *history ordering* fixture from platform moderation configuration using explicitly approved synthetic history; retain production moderation fail-closed policy.
- [x] Replace B011-03/B011-05 obsolete worker source-string checks with behaviour tests exercising raw admission before routing/persistence and denial before all downstream operations.
- [x] Update recovery-agent-context expectations to preserve `summary: null` for persisted summaries without content-specific moderation provenance.
- [x] Re-run the five affected suites and full Background suite; document exact validation, build and any remaining failures in this task's Completion Report.

## Interfaces / Contracts

Consumes DATABASE-001 provenance, BACKGROUND-004 orchestrator, BACKGROUND-011/008 post-correction capabilities and final `ARCH-027-BACKGROUND-005` purchase/refund semantics.

## Dependencies

- `ARCH-028-BACKGROUND-004`
- `ARCH-028-BACKGROUND-008`
- `ARCH-027-BACKGROUND-005`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Committed purchased terminal delivery failure is corrected exactly once.
- [x] Existing refund hold/provider-refunded state remains authoritative.
- [x] No provider monetary refund is created/reopened.
- [x] Corrected purchased case reaches the same suppression/merchant-notification ordering as generic cases.
- [x] Suppression is mandatory only when exact `131026` is the reason; a general FAILED adjustment requires prior separate architecture/Database acceptance and must not spoof recipient-unreachable reason.
- [x] For both Shopify and Woo, the negative UsageEvent has the original committed `shopId` and `provider`, no Shopify-reporting identifiers, and cannot enter the Shopify publication pipeline; repeat delivery creates no second correction.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.
- [x] The five previously failing full-suite cases pass without changing production code or dependency versions: Shared runtime pin, checkout-history ordering fixture, B011-03/B011-05 raw admission gates, and null recovery summary.
- [x] The complete Background suite is rerun and results documented; test reconciliation must not introduce new failures or remove coverage of the protected behaviours.

## Validation

Focused purchased/refund PostgreSQL integration across all accepted ARCH-027 states, **Shopify/Woo original-to-negative Shop/provider and non-publication parity**, replay tests, full Background tests/build and `git diff --check`.

Architect-approved baseline-test reconciliation requires focused Vitest on:

- `tests/unit/runtime/observability-startup.test.ts`
- `tests/unit/services/checkout-refresh.test.ts`
- `tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`
- `tests/unit/services/checkout-recovery/recovery-agent-context.service.test.ts`

Then run the **full** `pnpm test`, `pnpm exec tsc6 --noEmit`, task-scoped ESLint, the repository-declared build, and `git diff --check`. Record toolchain/baseline limitations truthfully; do not assert a pass without running the check.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

This task exists solely because its dependency differs from generic compensation. Do not move unrelated generic correction policy here.

Implement purchased-credit correction as a focused compensation strategy/module plugged into the generic coordinator. Do not move generic compensation or ARCH-027 refund orchestration into this task.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

### Architect-approved test-baseline scope amendment (2026-10-22)

**Decision: Approved as part of ARCH-028-BACKGROUND-009 at the developer's explicit request.** This is a bounded reconciliation of five pre-existing full-suite test failures detected during BG009 validation. Evidence from the Background `main` branch showed the same mismatches before this task: an exact Shared version assertion stuck at `2.4.1` despite the pinned `2.5.0`, a checkout-ordering unit test missing a moderation-history fixture, two B011 tests scanning the former WhatsApp worker instead of asserting the extracted inbound processor behaviour, and a recovery-agent-context test expecting an unproven stored summary. Resolve these failures in the BG009 implementation branch rather than creating a separate Background task.

Keep changes confined to the corresponding unit-test files and the existing worker test harness. **Do not** change the Shared dependency, weaken moderation admission or fail-closed behaviour, reintroduce unsafe summary text, or adjust the purchased-credit correction ledger. Prove raw admission order and denied-message short-circuit behaviour via execution, not brittle source text. The task's existing architectural requirements and dependencies remain unchanged.

This decision authorizes the **additional task scope only**. It does not mark the implementation architect-accepted, change the claimed attempt, override `completion_mode: developer`, or mark the task Complete. Actual test/build results and any residual failures belong in the Completion Report and subsequent review.

## Completion Report

### Status

Implementation and validation complete for the developer's formally claimed **Attempt 1** (claim timestamp `2026-10-22T21:07:04Z`). Developer self-review passed and the developer has now explicitly completed the task under `completion_mode: developer`. Attempt remains 1; `executor` and `claimed_at` are null. This is the developer completion decision, not an architect review record.

Implementation pushed as `2870da84fc55727a6ebfd378ae3da096d35d35b0` to `origin/task/ARCH-028-BACKGROUND-009`. The latest user-supplied Git status confirms the task branch tracks the matching origin task branch and all tracked implementation changes are committed.

### Files Changed

Implementation commit changes 13 task-scoped Background files:

- `src/services/recipient-reachability-failure.service.ts`
- `src/services/recovery-delivery-compensation/committed-usage.ts` (new)
- `src/services/recovery-delivery-compensation/committed.ts`
- `src/services/recovery-delivery-compensation/purchased-credit-state.ts` (new)
- `src/services/recovery-delivery-compensation/purchased.ts` (new)
- `src/services/recovery-delivery-compensation/types.ts`
- `tests/integration/arch028-recovery-delivery-compensation.integration.test.ts`
- `tests/unit/services/recovery-delivery-compensation/purchased-credit-state.test.ts` (new)
- `tests/unit/runtime/observability-startup.test.ts`
- `tests/unit/services/checkout-refresh.test.ts`
- `tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`
- `tests/unit/services/checkout-recovery/recovery-agent-context.service.test.ts`

### Work Completed

- Implemented the COMMITTED purchased-credit correction strategy using existing ARCH-027 authoritative purchase/refund states, preserving exact purchase-lot and original UsageEvent lineage and tenant/provider attribution.
- Corrects eligible spendable purchased lots; preserves live refund holds; treats already-refunded credit as historical-only; preserves provider-actionable frozen monetary evidence and routes inconsistent states for attention without issuing another provider refund.
- Persists idempotent, non-Shopify-reportable negative usage corrections; keeps exact `131026` reachability suppression and merchant notice downstream of successful correction and excludes unrelated HUMAN_TEXT.
- Kept policy, usage-ledger update and refund-state classification in separate focused modules. No unrelated production moderation/WhatsApp/shared-contract edits were made to resolve tests.
- Applied the **architect-approved 2026-10-22 baseline-test scope amendment** in the same task: aligned the exact Shared `2.5.0` test, isolated checkout history-ordering moderation fixtures, replaced the obsolete B011 worker source inspections with raw-admission behavioural checks, and asserted `summary: null` when summary moderation provenance is absent.
- Preserved production fail-closed moderation, admission-before-routing requirements, withholding of unproven summaries and the original Shared dependency version.

### Validation Results

- Earlier focused purchased/related unit validation: **64/64 passed**, as previously supplied in the developer's terminal log.
- Disposable PostgreSQL integration for `arch028-recovery-delivery-compensation.integration.test.ts`: **28/28 passed**, as previously supplied, covering provider attribution, refund states, replay/idempotency, reachability and notification ordering.
- Latest architect-approved baseline test matrix: **81/81 passed across 5 files** (`pnpm exec vitest run`), per terminal recording dated `2026-10-23 00:26–00:29` local time.
- Latest full Background suite: **2,473/2,473 tests passed across 246/246 test files** (`pnpm test`). The five previous full-suite failures were not reproduced after the approved test changes.
- `pnpm exec tsc6 --noEmit`: run in the latest validation sequence; no TypeScript errors appeared.
- `pnpm run build`: executed `npm run prisma:generate && tsc`; Prisma Client v6.19.3 generation succeeded and the command returned without reported compilation errors.
- `git diff --check`: executed with no whitespace diagnostics visible in the terminal recording.
- Task-scoped ESLint: passed on all 13 changed implementation/test files using the existing `node_modules/.bin/eslint` binary. Corepack pnpm was also checked, but its dependency setup stopped at the repository minimum-release-age policy because Shared `2.5.0` is newer than the configured cutoff; no dependency install or lockfile change was made.
- Current implementation branch `2870da84fc55727a6ebfd378ae3da096d35d35b0` equals `origin/task/ARCH-028-BACKGROUND-009`; current implementation worktree is clean. `git diff --check origin/main...HEAD` passed during review.
- Implementation branch push and commit `2870da84fc55727a6ebfd378ae3da096d35d35b0` confirmed by the developer's Git output.

### Deviations

- Five pre-existing full-suite test mismatches were resolved within BG009 following the explicit architect-approved scope amendment. Production behaviour and dependencies were unchanged by those test reconciliations.
- Full-suite baseline failures previously documented during BG009 were eliminated in the final 2,473-test run.

### Assumptions

- The provided focused and PostgreSQL integration results are from this BG009 implementation worktree and the same implementation change series as the published commit.
- The test log is the authoritative record of final local execution; no independent rerun on the developer's Mac is claimed here.

### Unresolved Issues

None blocking developer completion. The current canonical implementation worktree is clean; the previously observed local untracked `pnpm-lock.yaml`, `pnpm-workspace.yaml` and `typescript` artifacts are absent from current status and were not included in task commits.

### Physical Worktree / Preparation Evidence

Canonical launcher packet for Attempt 1 (`2026-10-22T21:07:04Z`):

```text
Canonical workspace:                  /Users/kwadwoadomafriyie/project/moda-interact-workspace
Parent task worktree:                  /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-009
Parent branch:                         task/ARCH-028-BACKGROUND-009
Parent worktree created/reused:        reused
Parent remote task fast-forward:       not-needed
Parent origin/main incorporated:      already-current
Parent start HEAD:                     0741121004e1df241ebf13ca2e288094032c0e80
Implementation worktree:               /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-009
Implementation branch:                 task/ARCH-028-BACKGROUND-009
Implementation worktree created/reused: created
Implementation remote task fast-forward: not-needed
Implementation origin/main incorporated: already-current
Implementation start HEAD:             3f753b175d67e308c2259de5335c73663e0ea968
Recursive submodule sync/update:        passed / passed
Initialized submodule:                 database at e0ab833d2e2395e3ed3cfe4aee6d07c716173e44
Dependency gate:                       passed (BACKGROUND-004, BACKGROUND-008, ARCH-027-BACKGROUND-005 complete)
Claim commit:                          6843fab1a75956d0d1c60489139fb02ab130a5f8; pushed
```

At review, parent HEAD `f6754bc7258e4466c2b7754c095f621339268479` contains the remote task branch at `7b303dd0d297e9287fa2e7c3e3636af3ed6a49db` and a merge of current `origin/main`; its 16 commits ahead of the remote task branch are already reachable from `origin/main`. The implementation HEAD `2870da84fc55727a6ebfd378ae3da096d35d35b0` equals its remote task branch. Both worktrees are clean apart from this parent report edit; the implementation worktree still maps to the canonical task path. The shared/default checkout was not used for implementation.

### Architectural Concerns

None identified from the verified task scope. Existing purchase/refund ownership, reusable correction services, Shared contracts, Meta recipient policy and repository isolation boundaries are preserved. The architect-approved five-test reconciliation is documented above and in the task's scope amendment.

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

## Developer Self-Review Passed (Attempt 1)

### Review Outcome

Passed. The purchased-credit compensation behavior and architect-approved test-baseline reconciliation satisfy the task scope and acceptance criteria. Focused purchased-credit unit tests, the PostgreSQL integration matrix, all five approved test corrections, the full Background suite, typecheck, build, task-scoped ESLint and whitespace validation have passing evidence. The task transitions to `review`; explicit developer completion remains pending under `completion_mode: developer`.

### Evidence Reviewed

- The implementation diff contains 13 task-scoped files. New production modules are `committed-usage.ts` (95 lines), `purchased-credit-state.ts` (44 lines), and `purchased.ts` (89 lines), within the approved <=200-line target and below the 300-line ceiling. Production changes to the existing recipient reachability service are minimal; the approved baseline reconciliation is confined to the five named tests and their harness.
- Integration coverage records 28/28 PostgreSQL cases passed for Shopify/Woo provider attribution, purchase/refund states, replay/idempotency, reachability and notification ordering. Focused purchased/related unit validation records 64/64 passed.
- The five architect-approved baseline tests passed 81/81 across five files. Full Background validation records 2,473/2,473 tests across 246 files, `pnpm exec tsc6 --noEmit` without reported errors, and `pnpm run build` completing after Prisma Client generation.
- Direct task-scoped ESLint passed for all 13 changed files. `git diff --check origin/main...HEAD` passed. Implementation HEAD `2870da84fc55727a6ebfd378ae3da096d35d35b0` equals `origin/task/ARCH-028-BACKGROUND-009` and the implementation worktree is clean.
- The original canonical Attempt 1 launcher packet is retained above; all three dependencies passed, the parent task worktree was reused, the implementation worktree was created, and recursive database submodule initialization passed.

### Lifecycle

Attempt 1 is the reviewed and explicitly completed attempt. Transitioned to `status: complete`, `executor: null`, and `claimed_at: null`; attempt remains 1. The implementation was previously integrated into `main` by PR #636; this completion action made no merge to or push of `main`.

## Developer Completion Decision (Attempt 1)

The developer explicitly invoked `/moda_developer_update ARCH-028-BACKGROUND-009 complete` on 2026-10-23. The durable passing `Developer Self-Review Passed (Attempt 1)` record is present; all required Work Items and Acceptance Criteria are checked; the implementation commit `2870da84fc55727a6ebfd378ae3da096d35d35b0` is committed and pushed; and the parent task/report branch can be committed and pushed. The task is therefore `complete`, with `executor: null`, `claimed_at: null`, and `attempt: 1` unchanged. No merge to `main` was required or performed by this action.

### Dependency Frontier

`ARCH-028-SYSTEM-TEST-001` was pending only because BG009 was its last incomplete explicit dependency; its other declared dependencies (`ARCH-028-ADMIN-001`, `ARCH-028-BACKGROUND-007`, and `ARCH-028-SHOPIFY-001`) are complete. It is promoted to dependency-ready `ready` at Attempt 0. It remains terminal/manual-gated, unclaimed, and not started; promotion does not authorize system-test execution.
