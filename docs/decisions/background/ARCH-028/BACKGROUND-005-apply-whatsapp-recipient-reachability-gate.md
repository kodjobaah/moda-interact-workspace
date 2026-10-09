---
id: ARCH-028-BACKGROUND-005
architecture_id: ARCH-028
title: Snapshot the exact WhatsApp recipient for every outreach attempt
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 47
executor: copilot
claimed_at: 2026-10-09T11:45:38Z
attempt: 2
depends_on:
  - ARCH-028-DATABASE-003
  - ARCH-028-BACKGROUND-007
enables:
  - ARCH-028-BACKGROUND-010
created: 2026-10-07
updated: 2026-10-09
---

# Snapshot the exact WhatsApp recipient for every outreach attempt

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Adopt DATABASE-003 required `RecoveryOutreachAttempt.recipient` in every initial and follow-up send path, persisting the canonical, actual destination before billing/Meta admission. Do not implement suppression policy or reachability writes in this task.

## Context

The exact Shop/recovery for provider failure is already known through durable message/attempt/recovery relations. The attempt's required `recipient` snapshot identifies the failed destination. BACKGROUND-007 resolves the initial recipient before recovery creation; this task adopts the strict DATABASE-003 field on all attempt-creation paths, including follow-ups and sends to a changed current phone.

The current refactored `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` still checks `!recovery.customer?.phone` as part of its early due guard and uses `to: recovery.customer.phone` for the provider send. Both are stale for ARCH-028 when `CustomerPhone` is authoritative: `Customer.phone` may be null or out of date while a usable current Shop-scoped `CustomerPhone` exists.

## Scope

- Reuse BACKGROUND-007's canonical current-`CustomerPhone` prerequisite for initial sends; resolve the current Shop-scoped phone again when creating each follow-up, not from a stale `Customer.phone` field. Replace the follow-up processor's `!recovery.customer?.phone` early guard and `to: recovery.customer.phone` destination with the current canonical resolution result; do not turn an absent/stale legacy `Customer.phone` into a false suppression outcome.
- Centralise bounded digits-only recipient canonicalization in a small Background-owned helper (not a duplicate phone-identity model).
- Populate required `RecoveryOutreachAttempt.recipient` before initial and follow-up outbound admission/Meta send; pass the same number to the provider. Treat the stored recipient as immutable after provider-directed work begins.
- Ensure all attempt writers, test fixtures and relevant Prisma consumers adopt the breaking DATABASE-003 revision together. Record the exact database gitlink/version adopted.
- If current recipient is absent when initiating a follow-up, do not admit/send/bill; return a bounded safe outcome rather than inventing a recipient.
- Preserve Shop isolation and existing attempt idempotency. No recipient is inferred from a provider status webhook.

## Out of Scope

- Candidate no-recipient prerequisite (BACKGROUND-007), except its typed initial-recipient handoff.
- Reachability policy, suppression lookups/resume (BACKGROUND-010).
- Post-compensation failure reachability and positive-evidence clearing (BACKGROUND-011).
- Synchronous provider rejection (BACKGROUND-006) and merchant notification (BACKGROUND-008).
- Global phone blacklist or Customer.hasWhatsApp.

## Requirements

- [x] Every initial and follow-up attempt has a required canonical digits-only recipient matching the actual Meta destination.
- [x] Recipient selection uses current Shop-scoped `CustomerPhone`, never stale `Customer.phone`; BACKGROUND-007 remains the initial materialisation guard. A null/stale `Customer.phone` does not block an otherwise eligible follow-up with a current usable `CustomerPhone`.
- [x] Attempt recipient is immutable after provider-directed work; a new current phone requires a separate attempt snapshot.
- [x] Provider delivery status never resolves tenant ownership through phone lookup.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Reuse BACKGROUND-007 recipient-prerequisite output for initial attempt creation and send.
- [x] Add canonical current-`CustomerPhone` selection and per-attempt recipient snapshots for follow-ups.
- [x] Adopt DATABASE-003 across all attempt creation paths and fixtures.
- [ ] Verify persisted recipient equals the actual provider destination even when current phone changes (production-writer PostgreSQL regression is authored but awaits developer execution).
- [x] Add initial/follow-up and multi-Shop same-number tests, including null and stale `Customer.phone` with a valid current `CustomerPhone` and actual Meta destination parity.
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes DATABASE-003 required outreach recipient and BACKGROUND-007 canonical initial recipient. Exposes the immutable per-attempt recipient to BACKGROUND-010 and BACKGROUND-011; does not consume compensation outcomes.

## Dependencies

- `ARCH-028-DATABASE-003`
- `ARCH-028-BACKGROUND-007`

## Enables

- `ARCH-028-BACKGROUND-010`

## Acceptance Criteria

- [x] All attempt-creation paths satisfy mandatory DATABASE-003 recipient without a nullable/default escape hatch.
- [x] Initial and follow-up sends target their own immutable per-attempt stored digits-only recipient.
- [ ] A changed phone never mutates an earlier attempt recipient (verify through the real PostgreSQL attempt-writer regression).
- [x] Missing follow-up recipient creates no new admission or provider call.
- [x] A due follow-up with null or stale `Customer.phone` but a valid current Shop-scoped `CustomerPhone` is not falsely suppressed and sends to the stored per-attempt current recipient.
- [x] Two Shops sharing the same phone remain isolated.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused initial/follow-up recipient-selection and attempt-write tests including missing/changed current phone, null/stale `Customer.phone` positive follow-up admission, required-field PostgreSQL integration, Meta destination/snapshot parity, full Background test/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Reuse existing recipient resolution and do not log full recipient values. Avoid making `recovery-initiation.service.ts` own phone-history selection and all future reachability policy. The stricter database revision and attempt writers must be integrated together; do not independently deploy the mandatory-field migration to running incompatible Background code.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Attempt 2 source/test corrections and fast validation are complete. The task remains in progress until developer-owned disposable PostgreSQL integration evidence is recorded, as required by the Architect Review follow-up.

### Files Changed

 - `moda-interact-background/src/services/checkout-recovery/recovery-recipient-canonicalization.ts` (new bounded digits-only canonicalizer).
 - `moda-interact-background/src/services/checkout-recovery/recovery-recipient-resolver.service.ts` and `moda-interact-background/src/services/customer.phone.service.ts` (canonical initial handoff and current phone lookup constrained by customer and Shop).
 - `moda-interact-background/src/services/recovery-outreach-attempt.service.ts`, `moda-interact-background/src/services/checkout-recovery/recovery-initiation.service.ts`, and `moda-interact-background/src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` (persist the immutable recipient snapshot before outbound admission and use it as the provider destination).
 - Focused unit tests for initial/follow-up parity, missing/current phone behavior, canonicalization bounds, Shop scoping, and immutable upsert replay; new `moda-interact-background/tests/integration/recovery-outreach-recipient.integration.test.ts` for actual PostgreSQL persistence.
 - Background database gitlink updated from `ef51500b2728bc0c894e627dfa1c9e6c9d4d9a13` to accepted DATABASE-003 commit `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce`.

### Work Completed

 - Initial attempts consume BACKGROUND-007's resolved recipient, canonicalize it to 1–64 ASCII digits, persist it before billing/provider admission, and send to the stored attempt recipient.
 - Follow-ups resolve the current `CustomerPhone` by recovery customer ID and Shop ID, independent of legacy `Customer.phone`; a missing current recipient returns `suppressed/no-recipient` before state claim, attempt creation, billing, or send.
 - Follow-up attempt creation persists that current canonical recipient; provider sends use `attempt.recipient`. Upsert replay uses an empty update so the original attempt snapshot cannot be overwritten.
 - Added direct coverage for null/stale legacy phone with a valid current phone, no-recipient side effects, exact snapshot/provider parity, canonicalization bounds, Shop query isolation, and required PostgreSQL attempt persistence.
 - Audited attempt creation call sites; both production writers use the updated required-recipient service inputs. All touched production modules are below 300 physical lines.
 - A1-R2: removed the synthetic initial/follow-up attempt fallbacks. `RecoveryOutreachAttemptService` now throws `Recovery outreach attempt persistence is unavailable` when the Prisma attempt delegate is absent, before billing/admission/provider work. Added focused rejection coverage for both creation methods and updated successful-flow Prisma mocks to model durable upsert and status writes.
 - A1-R1: expanded the PostgreSQL integration test to call the production `RecoveryOutreachAttemptService` with a real Prisma client; it writes initial and follow-up rows, replays both with a different recipient, and asserts persisted distinct recipients and Shop/recovery lineage. This integration test is authored but has not yet been executed.
 - Attempt 2 files: `src/services/recovery-outreach-attempt.service.ts`, `tests/unit/recovery-outreach-follow-up.test.ts`, `tests/unit/services/matured-candidate.materialization.test.ts`, `tests/unit/services/checkout-refresh.test.ts`, and `tests/integration/recovery-outreach-recipient.integration.test.ts`.

### Validation Results

 Agent-executed validation passed:

 - `npx vitest run tests/unit/services/customer.phone.service.test.ts tests/unit/services/checkout-recovery/recovery-recipient-resolver.service.test.ts tests/unit/recovery-outreach-follow-up.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts` — 5 files, 42 tests passed.
 - `npm run test:unit` — 176 files, 1,888 tests passed.
 - `npm run prisma:validate` — valid against DATABASE-003.
 - `npm run build` — Prisma Client generated from DATABASE-003 and TypeScript build passed.
 - `npx tsc --noEmit` — passed after adding the PostgreSQL integration test.
 - `git diff --check` — passed.

Attempt 2 validation:

 - Focused recipient suite: `npx vitest run tests/unit/services/customer.phone.service.test.ts tests/unit/services/checkout-recovery/recovery-recipient-resolver.service.test.ts tests/unit/recovery-outreach-follow-up.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts` — 5 files, 43 tests passed.
 - `npm run test:unit` — 176 files, 1,889 tests passed.
 - `npm run prisma:validate` — passed against DATABASE-003.
 - `npm run build` — passed; Prisma Client generated from DATABASE-003 and TypeScript compilation passed.
 - `git diff --check` — passed. Modified attempt service: 191 physical lines.

 Developer validation required:

 - `npm run test:integration -- tests/integration/recovery-outreach-recipient.integration.test.ts` — execute the production-writer PostgreSQL replay regression through the disposable PostgreSQL/Redis harness. Not run by this agent; record exact exit status, result, environment and container cleanup before acceptance.

### Deviations

 The disposable PostgreSQL integration test was added but not executed by the agent under the workspace validation policy. The initial build also exposed that the prepared Background gitlink pointed to DATABASE-001; the task branch now adopts the accepted DATABASE-003 implementation commit exactly.

### Assumptions

 The accepted DATABASE-003 commit `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce` is the database revision intended for this task's compatible runtime adoption.

### Unresolved Issues

 Developer-owned disposable PostgreSQL integration command above remains to be run and reviewed. The changed-phone immutability Acceptance Criterion remains unchecked until this real-PostgreSQL regression passes.

### Architectural Concerns

 No architectural concern identified. The breaking recipient schema and compatible attempt writers are represented together on this task branch.

### Attempt 2 Execution Evidence

- Launcher prepared and claimed Attempt 2 for executor `copilot` at `2026-10-09T11:45:38Z`; durable parent claim commit `a6c69e02207a1441b24fc43f90c40e8342ddce33` was committed and pushed. The dependency gate passed for DATABASE-003 and BACKGROUND-007.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-005`, branch `task/ARCH-028-BACKGROUND-005`. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-005`, same task branch.
- Parent start head: `61e52d89f4a48d3c22d5be0b2d40981ef9740790`. Implementation start head: `f42d2867d30639cfc9d8b7cb4b87c1843017eb5f`. For both worktrees, remote task-branch fast-forward was `not-needed` and `origin/main` was `already-current`.
- Recursive submodule sync and update passed; recursive status was `ready`. The database submodule was initialized at accepted DATABASE-003 commit `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce`.
- Dedicated canonical task worktrees were reused. Neither the default/shared workspace checkout nor shared implementation checkout was switched or mutated; no other task worktree was reused. No database submodule content was modified.
- Attempt 2 remains `status: in_progress`, `executor: copilot`, and `claimed_at: 2026-10-09T11:45:38Z` pending the developer-owned PostgreSQL evidence required before resubmission. The original Architect Review section below is preserved unchanged.

### Attempt 1 Execution Evidence (historical)

 - Launcher prepared Attempt 1 for executor `copilot`; dependencies DATABASE-003 and BACKGROUND-007 passed.
 - Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-005`, branch `task/ARCH-028-BACKGROUND-005`.
 - Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-005`, branch `task/ARCH-028-BACKGROUND-005`.
- Implementation commits `c36434f5812b605aba7b930f9603db141d3cf143` and `f42d2867d30639cfc9d8b7cb4b87c1843017eb5f` adopt database commit `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce`.
 - Parent claim commit: `c5c9eccb4de487fa9457defca88b37ae9e3efa8f`; prepared parent head `845e108175d6b3dad14c21d815b4d83c274cf53d`; prepared implementation head `5e40e7aa4e5ce4bb4802b52c7d6b149eb4217130`.
 - The database submodule working tree is clean at the exact accepted DATABASE-003 commit; no database submodule content was modified.

### Attempt 2 Publication

- Implementation source/test changes are committed as `eab08a74bbb37d20783f2a68f5275fef70a1d046` (`task(ARCH-028-BACKGROUND-005): address attempt review findings`) and pushed on `origin/task/ARCH-028-BACKGROUND-005`.
- Parent task/report changes are limited to this task file and are committed and pushed on the mirrored `origin/task/ARCH-028-BACKGROUND-005` branch.
## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-09).

### Review Notes

Reviewed submitted ARCH-028-BACKGROUND-005 source, parent ARCH-028 architecture, this task and Completion Report. Verified implementation commits `c36434f5812b605aba7b930f9603db141d3cf143` and `f42d2867d30639cfc9d8b7cb4b87c1843017eb5f`, parent report commit `9ac2e549a703a94cfefd9955dfb5fed1d41fe268`, and DATABASE-003 gitlink `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce`. The current-`CustomerPhone` selection, Shop-scoped follow-up lookup, bounded canonicalization, missing-recipient early exit, immutable upsert `update: {}`, and `to: attempt.recipient` send wiring conform at source/unit-test level. The following bounded corrections are required:

**A1-R1 — Run meaningful real-Prisma persistence tests (test correction and developer execution required).**

`tests/integration/recovery-outreach-recipient.integration.test.ts` currently calls `PrismaClient.recoveryOutreachAttempt.create()` directly and checks only the returned `recipient`. That repeats a DATABASE-003 schema capability rather than exercising the BACKGROUND-005 production attempt writer. Extend the disposable PostgreSQL test to call `RecoveryOutreachAttemptService.getOrCreate()` and `getOrCreateFollowUp()` with an actual Prisma client, inspect both persisted rows, and replay with a different current phone to prove the original recipient is not overwritten. Assert both attempts retain their distinct canonical recipients and the proper Shop/recovery lineage. Keep the separate unit tests for provider destination/snapshot parity. Execute `npm run test:integration -- tests/integration/recovery-outreach-recipient.integration.test.ts` through the existing disposable PostgreSQL/Redis harness; record exact pass/fail, environment and container cleanup. The new integration test was expressly **not run** in Attempt 1; do not check or claim it as passing until execution evidence exists. Developer-owned execution is permitted, but its results must be recorded in this task report before acceptance.

**A1-R2 — Remove the synthetic non-durable attempt fallback (source/test correction required).**

`src/services/recovery-outreach-attempt.service.ts` still returns an invented `{ id: 'recovery-outreach:...', recipient, status: PENDING }` from both `getOrCreate()` and `getOrCreateFollowUp()` when `this.attemptModel` is absent. In the new required-recipient architecture, an attempt must be durably written **before** outbound admission/billing/provider work. Faking a successful write when the Prisma delegate is unavailable violates that fail-closed invariant, whether because of stale generated client wiring or an incomplete dependency. Fail explicitly and without provider/billing side effects instead. Add a focused regression for missing attempt persistence capability and keep the existing immutability/replay behavior with a real attempt model. Do not introduce a replacement in-memory ledger.

**A1-R3 — Reconcile task checklists and start-of-attempt evidence (documentation correction required).**

All seven Requirements and six Work Items remain unchecked despite the Completion Report claiming completion; reconcile each against the corrected source and actual tests, keeping unexecuted validation clearly outstanding. The previously defined Acceptance Criterion **"A changed phone never mutates an earlier attempt recipient"** was removed from the submitted report; it has been restored above, pending real-PostgreSQL replay verification. The current execution report contains the worktree paths, initial heads and claim commit but does not explicitly record launcher packet evidence for **both** task-worktree remote-branch synchronization / `origin/main` incorporation, recursive submodule sync/update/status, and confirmation that neither default/shared checkout nor another task worktree was used. Recover that evidence from the prepared launcher packet, or if physical isolation did not hold, re-establish the correct canonical worktrees, revalidate and report non-conformance. A clean task branch alone is not sufficient; do not manufacture another source commit solely to improve the report.

The reported 1,888 unit tests, 42 focused tests, Prisma validation, TypeScript build and diff check are acknowledged. No unrelated feature or refactor is requested. The task correctly isolates required DATABASE-003 adoption from later suppression and provider-failure convergence tasks.

### Reviewed Files

- `src/services/checkout-recovery/recovery-recipient-canonicalization.ts`
- `src/services/checkout-recovery/recovery-recipient-resolver.service.ts`
- `src/services/customer.phone.service.ts`
- `src/services/recovery-outreach-attempt.service.ts`
- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`
- Focused initial/follow-up/Shop-scoping/replay unit tests
- `tests/integration/recovery-outreach-recipient.integration.test.ts`
- `scripts/test-integration.mjs`, `package.json`, nested DATABASE-003 Prisma schema
- Parent ARCH-028 architecture and BACKGROUND-005 task/Completion Report

### Validation Reviewed

Implementer reports `npm run test:unit` 1,888 passing tests, focused recipient tests 42/42, `npm run prisma:validate`, `npm run build`, `npx tsc --noEmit`, and `git diff --check` successful. Read and checked those test sources and the integration-runner configuration. PostgreSQL persistence test was not run, as stated in the report. The uploaded code snapshot does not include installed `node_modules` and this review container lacks Docker/psql; no independent executable DB run is claimed. Pushed Git object identities were checked against the submitted snapshot.

### Architecture Conformance

Partially conforming pending A1-R1 to A1-R3. Core recipient selection and attempted durable send-path wiring match ARCH-028, and the DATABASE-003 gitlink is correct. A1-R2 leaves an avoidable non-durable failure branch at the exact persistence boundary. A1-R1 leaves real writer persistence/immutability unproven, and the task's execution/checklist record needs reconciliation.

### Follow-up

Return **the same** `ARCH-028-BACKGROUND-005` task to `ready` for Attempt 2. Clear executor/claim and preserve `attempt: 1` until launcher preparation claims Attempt 2. `moda_background` owns the bounded service/test correction and updated Completion Report; the developer may execute the existing disposable PostgreSQL integration command and provide its results. Preserve this original Architect Review as the historical correction contract, and resubmit only after the required evidence is present. `ARCH-028-BACKGROUND-010` remains dependency-gated until BACKGROUND-005 is Accepted and Complete. Do not create or modify any `docs/decisions/**/_index.md` before explicit final architecture reconciliation.
