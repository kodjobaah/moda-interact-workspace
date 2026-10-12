---
id: ARCH-028-BACKGROUND-010
architecture_id: ARCH-028
title: Gate recovery admission by Shop-scoped recipient suppression
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 53
executor: null
claimed_at: null
attempt: 8
depends_on:
  - ARCH-028-DATABASE-001
  - ARCH-028-BACKGROUND-005
enables:
  - ARCH-028-BACKGROUND-011
created: 2026-10-08
updated: 2026-10-12
---
# Gate recovery admission by Shop-scoped recipient suppression

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Read the existing Shop-scoped recipient reachability evidence before initial or follow-up recovery admission, preventing provider and billing work during active suppression and safely resuming only after its expiry.

## Context

BACKGROUND-005 supplies the exact canonical recipient/attempt snapshot. DATABASE-001 supplies the indexed reachability record, policy duration and `WHATSAPP_RECIPIENT_SUPPRESSED` block reason. Suppression reads are independent of recording terminal failures, which is owned by BACKGROUND-011.

## Scope

- Check `(shopId, canonicalRecipient)` reachability against current time before creating a billable attempt or calling Meta for initial/follow-up outreach.
- For active `suppressUntil`, perform zero recovery admission/billing and zero provider sends; where an already-materialised recovery is eligible for blocking, use `WHATSAPP_RECIPIENT_SUPPRESSED` and existing recovery lifecycle rules.
- On expiry or valid new recipient, re-evaluate eligibility with fresh Shop/customer/checkout state; reuse existing bounded resume scheduling rather than new infrastructure.
- A changed current phone maps to a distinct recipient key and is eligible independently; maintain idempotency under duplicate candidates and multiple workers.

## Out of Scope

- Provider-failure evidence writes, suppression upserts or clearing (BACKGROUND-011).
- Monetary/capacity compensation (BACKGROUND-004/009).
- Missing phone pre-materialisation (BACKGROUND-007).
- Creating a global phone blacklist or a second scheduler.

## Requirements

- [x] One indexed `(shopId, recipient)` lookup determines suppression; a row for another Shop never blocks the current Shop.
- [x] Suppression is checked before recovery billing/outbound admission in both initial and follow-up paths.
- [x] Expiry alone stops blocking; no indefinite suppression or busy polling.
- [x] Re-evaluation preserves checkout/recovery validity and no duplicate sends or charges.
- [x] New production source files target <=200 lines and never exceed 300; keep large existing modules integration-only.

## Work Items

- [x] Add a focused suppression admission policy/reader using DATABASE-001 fields and BACKGROUND-005 snapshot.
- [x] Wire initial and follow-up gating before billing/provider work.
- [x] Reuse bounded recovery-resume scheduling for eligible blocked DETECTED cases.
- [x] Add expiry, changed-recipient, duplicate, multi-Shop and zero-billing tests.
- [x] Check touched production modules remain small and responsibility-focused.

## Interfaces / Contracts

Consumes `WhatsAppRecipientReachability(shopId, recipient)`, `RecoveryAdmissionBlockReason.WHATSAPP_RECIPIENT_SUPPRESSED` from DATABASE-001, and canonical recipient selection/snapshots from BACKGROUND-005. Produces bounded `allow/suppressed(until)` admission outcomes; it does not write failure or success reachability evidence.

## Dependencies

- `ARCH-028-DATABASE-001`
- `ARCH-028-BACKGROUND-005`

## Enables

- `ARCH-028-BACKGROUND-011`

## Acceptance Criteria

- [x] Active suppression never causes a billable admission or provider call.
- [x] A different Shop or recipient is not blocked by another reachability key.
- [x] Expired suppression is re-evaluated safely; stale/duplicate resume cannot double-charge.
- [x] No new runtime source file exceeds 300 lines, and large existing source files receive only bounded wiring.

## Validation

Focused unit/integration/PostgreSQL checks for suppression, expiry/resume, concurrency, initial/follow-up zero-charge behaviour; repository-declared Background tests/build and `git diff --check`.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

Keep the gate a thin reusable Background capability rather than mixing persistence writers, compensation and queue orchestration into one service. Do not log the full canonical phone number.

## Completion Report

### Status

Ready for Architect review (Attempt 7, 2026-10-11). Attempt 1–6 reports and the complete Architect Review history below are retained as historical evidence.

### Files Changed

Added `src/services/checkout-recovery/recovery-recipient-suppression-admission.service.ts`; updated initial/follow-up admission and the existing targeted capacity-resume/follow-up scheduling paths; added focused unit and PostgreSQL integration coverage. No schema or migration changed.

### Work Completed

Initial and follow-up recovery admission now read the exact canonical `(shopId, recipient)` reachability key before creating the applicable outreach attempt or entering billing/provider admission. An active suppression prevents billing and provider calls. Initial DETECTED recoveries receive `WHATSAPP_RECIPIENT_SUPPRESSED` and one deterministic delayed resume; follow-ups reuse their existing delayed queue with deadline-specific job identity.

After expiry, initial resume rechecks durable state under the existing checkout lock, performs the existing fresh abandoned-checkout lookup, and re-enters normal recovery initiation. A changed current recipient is evaluated by its distinct key. Periodic repair and generic resume batches remain capacity-only, avoiding suppression polling. Duplicate resumes retain the existing lock, attempt identity, and outbound idempotency protections.

The new runtime module is 69 lines. Existing production modules received bounded wiring; the largest directly touched existing recovery modules remain below 300 lines.

Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-010`, branch `task/ARCH-028-BACKGROUND-010`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-010`, same task branch. Shared workspace and implementation checkouts were not switched or mutated; no other task worktree was reused.

Start-of-attempt synchronization: parent task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `already-current`; implementation task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `already-current`.

Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` resolved to `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

### Validation Results

PASS: focused recovery unit matrix, 161 tests across 16 files.

PASS: disposable PostgreSQL `tests/integration/recovery-outreach-recipient.integration.test.ts`, 2 tests, covering active exact-key suppression, other-Shop isolation, changed recipient, and expiry boundary.

PASS: `pnpm run build`, including Prisma Client generation and TypeScript compilation.

PASS: `pnpm run prisma:validate` and `git diff --check`.

The complete repository test suite was not run; validation was focused on task-owned recovery admission/resume paths.

### Deviations

None. Suppression expiry uses a per-recovery delayed job; periodic repair and generic resume batches remain capacity-only to avoid busy polling.

### Assumptions

The existing deterministic BullMQ job IDs, retry policy, checkout lock, fresh abandoned-checkout lookup, and recovery/attempt idempotency are the approved bounded resume mechanisms; no additional scheduler or persistence model is needed.

### Unresolved Issues

None.

### Architectural Concerns

None identified within BACKGROUND-010 scope. Suppression evidence writes and positive-evidence clearing remain owned by BACKGROUND-011.

### Attempt 2 — Architect Corrections and Validation

#### Corrections

- **A1-R1:** Suppression-expiry resume now resolves the current recipient from the fresh checkout seed through `recoveryRecipientResolverService.resolve(seed)`, with a fallback only to the recovery's current Shop-scoped `CustomerPhone`. It forwards that exact canonical recipient, together with the recovery generation, through the resume adapter into initial suppression evaluation and the immutable attempt snapshot. If no current recipient exists, it clears only the still-DETECTED suppression block and returns `no-recipient`; it creates no attempt and performs no billing/provider admission. Regression coverage verifies a null checkout phone with a persisted current phone, a changed phone, and an absent current phone.
- **A1-R2:** Targeted expiry scheduling now completes before the durable `WHATSAPP_RECIPIENT_SUPPRESSED` block is written. If BullMQ enqueue fails, the error propagates before the block update, leaving the DETECTED recovery eligible for a later normal materialisation retry; initial admission returns before attempt creation, billing, or provider send. If the guarded block update loses a race after scheduling, the delayed job is harmless and observes the no-longer-blocked recovery. This uses the existing delayed resume queue and checkout-lock lifecycle; no polling or second scheduler was added.
- Existing checkout-resume/materialisation unit fixtures now model the suppression-read delegate and recipient resolver introduced by this task. No schema, migration, immutable recipient evidence, provider-status behavior, compensation, reachability writer, or index file changed.

#### Files Changed

Updated `src/services/checkout-recovery.service.ts`, `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`, and `src/services/checkout-recovery/recovery-recipient-suppression-admission.service.ts`; added/updated focused recovery resume, suppression enqueue-failure, initiation, checkout-refresh, and matured-materialisation test doubles/regressions. No database submodule gitlink was staged.

#### Validation Results

PASS: task-owned recovery unit matrix, 173 tests across 13 files, including resume, follow-up, recipient resolution, suppression admission, enqueue failure, checkout refresh, and matured materialisation.

PASS: disposable PostgreSQL `tests/integration/recovery-outreach-recipient.integration.test.ts`, 2 tests.

PASS: `pnpm run build` (Prisma Client generation and TypeScript compilation).

PASS: `pnpm run prisma:validate`, `git diff --check`, and focused editor diagnostics on the changed implementation/test files (no errors).

An initial integration-wrapper invocation mistakenly included a literal `--` and ran the repository default selection (226 files); unrelated suites failed, so that result is not counted as task validation. The task-owned PostgreSQL integration was rerun with the wrapper's positional test-path argument and passed. The complete repository suite was not run.

Production source sizes: suppression admission service 68 lines; resume processor 219 lines; checkout recovery service 204 lines. No new production module was added; existing touched modules remain below the 300-line task limit.

#### Attempt 2 Preparation Evidence

Claimed attempt: 2 (`copilot`, 2026-10-11T16:18:53Z), claim commit `7f02512526cc0d765258db75f2aa1d1fd7c58a4f`, pushed by the launcher.

Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-010`, branch `task/ARCH-028-BACKGROUND-010`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-010`, same task branch. Shared workspace and implementation checkouts were not switched or mutated; no other task worktree was reused.

Start-of-attempt synchronization: parent task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `already-current`; implementation task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `yes`.

Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` resolved to `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

Implementation correction commit: `43d14e7355f2027958ccb982b484017b14fce825` (Attempt 2, pushed to `task/ARCH-028-BACKGROUND-010`). Parent report commit: `task/ARCH-028-BACKGROUND-010` (Attempt 2 report update).

### Attempt 3 — Enqueue Liveness Corrections and Validation

#### Corrections

- **A2-R1:** A resume-queue publish error is wrapped with the stable `RECIPIENT_SUPPRESSION_RESUME_ENQUEUE_FAILED` marker. The existing pending-candidate BullMQ job retains its bounded three-attempt policy; its worker forwards `retrySuppressionAdmission: true` only for a retried job whose recorded failure reason matches that marker. Materialization then re-reads current Shop/checkout/recipient state under the checkout lock and re-enters only an existing DETECTED recovery at its original generation. The actual `RecoveryInitiationService.upsertRecovery` path returns the same durable row; active suppression is checked again before attempts, billing, or provider work. The cross-component regression drives the candidate worker through first enqueue failure and tagged retry, proving the same recovery proceeds to a delayed suppression wait without attempt creation, billing, or send. Arbitrary failures and first executions retain the existing `no-op-existing` behavior.
- **A2-R2:** A targeted suppression wake-up now carries its trigger through the resume worker, processor, initiation, and deferral path. The processor accepts an unblocked DETECTED recovery only when the targeted job carries the suppression trigger for that recovery; it then performs the same locked fresh-checkout and canonical-recipient re-evaluation. If suppression remains active, deferral schedules a deterministic child trigger derived from the active trigger before writing the durable block. Thus the child job has a distinct ID from the currently executing wake-up, while duplicate workers deriving from the same wake-up converge on the same child ID. A controlled interleaving pauses the original database block write, runs the targeted processor, verifies a distinct child was enqueued and the active suppression still prevents admission, then releases the original write.
- No periodic polling, second scheduler, schema/migration change, capacity-block reason reuse, immutable recipient evidence change, provider-status/compensation change, reachability writer, or index-file change was introduced.

#### Files Changed

Updated recovery initiation/materialization, targeted resume processing and worker forwarding, plus pending-candidate retry routing. Added cross-component candidate-worker retry and deterministic wake-up interleaving tests, with direct trigger-lineage and child-ID regressions. No database submodule gitlink was staged.

#### Validation Results

PASS: focused recovery/follow-up unit matrix, 178 tests across 14 files.

PASS: disposable PostgreSQL `tests/integration/recovery-outreach-recipient.integration.test.ts`, 2 tests.

PASS: `pnpm run build` (Prisma Client generation and TypeScript compilation) and `pnpm run prisma:validate`.

PASS: changed-file editor diagnostics (no errors) and `git diff --check`.

Production source sizes: suppression admission service 76 lines; capacity-resume processor 228 lines; recovery materialization service 144 lines; checkout recovery service 216 lines. No new production module was added and all touched production modules remain below 300 lines.

#### Attempt 3 Preparation Evidence

Claimed attempt: 3 (`copilot`, 2026-10-11T17:16:51Z), claim commit `dd47c00e983351dfd8a4d73bc3dc537fc0aad1f7`, pushed by the launcher.

Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-010`, branch `task/ARCH-028-BACKGROUND-010`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-010`, same task branch. Shared workspace and implementation checkouts were not switched or mutated; no other task worktree was reused.

Start-of-attempt synchronization: parent task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `already-current`; implementation task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `already-current`.

Recursive implementation submodules: launcher `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` resolved to `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

Implementation correction commit: `b9860933581cc2f4998b950a348a9f031f745c2c` (pushed to `task/ARCH-028-BACKGROUND-010`). Parent report commit: this Attempt 3 report update on `task/ARCH-028-BACKGROUND-010`.

### Attempt 4 — Early-Wakeup State Handoff and Retry Error Preservation

#### Corrections

- **A3-R1:** When a targeted suppression wake-up overtakes the original durable block write, a terminal/missing checkout now compare-and-sets the still-DETECTED recovery to CANCELLED even when the suppression block has not yet landed. Likewise, a no-current-recipient early wake-up terminalizes only the unblocked targeted suppression case; already-blocked no-recipient behavior continues to clear only the still-DETECTED suppression block. Both paths create no attempt, billing admission, or provider send. The later original suppression update remains guarded by `status: DETECTED`, so it cannot re-block a recovery already terminalized by the wake-up. Controlled deferred-write regressions cover both no-recipient and terminal-checkout outcomes and assert the late update affects zero rows.
- **A3-R2:** `CheckoutOrderGuardService.withCheckoutLock()` now composes a callback failure with a Redis GET/DEL cleanup failure rather than allowing `finally` to replace the primary error. The pending-candidate worker similarly composes materialization and candidate-index cleanup errors. The composed error preserves `RECIPIENT_SUPPRESSION_RESUME_ENQUEUE_FAILED` at the beginning of its message, which the retry classifier recognizes on BullMQ's next attempt, and retains both failures in nested `AggregateError` causes for diagnostics. The worker-level regression uses the real checkout lock guard, injects suppression-resume enqueue failure plus lock-release and candidate cleanup failures, then verifies the tagged retry re-enters the same DETECTED generation, schedules the delayed suppression wake-up, and performs no attempt/billing/provider admission.
- No schema, queue, scheduler, polling, reachability-writer, immutable attempt-recipient, provider-status, compensation, or `_index.md` changes were made.

#### Files Changed

Updated `recovery-capacity-resume-processor.service.ts`, `pending-recovery-candidate/checkout-order-guard.service.ts`, and `pending-recovery-candidate.worker.ts`. Added deferred-write no-recipient/terminal regressions, a checkout-lock error-preservation regression, and a combined enqueue/Redis-cleanup candidate-retry regression.

#### Validation Results

PASS: focused recovery/follow-up and checkout-lock unit matrix, 184 tests across 15 files.

PASS: disposable PostgreSQL `tests/integration/recovery-outreach-recipient.integration.test.ts`, 2 tests.

PASS: `pnpm run build` (Prisma Client generation and TypeScript compilation) and `pnpm run prisma:validate`.

PASS: changed-file editor diagnostics (no errors) and `git diff --check`.

Touched production module sizes: capacity-resume processor 251 lines; checkout-order guard 88 lines; pending-candidate worker 100 lines. No new production module or database migration was added.

#### Attempt 4 Preparation Evidence

Claimed attempt: 4 (`copilot`, 2026-10-11T18:20:09Z), launcher claim commit `b51b2329c4304e97e1cc611f720929e7b2fd34ec`, pushed by the launcher. Parent starting head `cc9d2d8f38fc496da638c5dbbd55740a138c7098`; implementation starting head `b9860933581cc2f4998b950a348a9f031f745c2c`.

The launcher reused the canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-010` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-010`, both on `task/ARCH-028-BACKGROUND-010`; canonical workspace resolution returned `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent and implementation `origin/main` synchronization passed; task branch fast-forwards were not needed. Recursive submodule sync/update passed and `database` remained at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

Implementation correction commit: `03fd86794694a0231b390fa6f9d87c45918b005b` (pushed to `task/ARCH-028-BACKGROUND-010`). Parent report commit: this Attempt 4 report update on `task/ARCH-028-BACKGROUND-010`.

### Attempt 5 — Preserve Re-entry for Temporarily Missing Recipients

#### Corrections

- **A4-R1:** A targeted suppression wake-up that finds an open checkout but no current canonical recipient now leaves the recovery `DETECTED` and clears/touches only a still-DETECTED suppression or unblocked row. The existing `updatedAt` field is used as a compare-and-set token: suppression deferral captures the row version before enqueue, and the durable block write succeeds only if the wake-up has not since advanced that version. This prevents the delayed original write from restoring a stale suppression block after the early wake-up clears it. Completed/not-found checkout cancellation remains unchanged.
- A later checkout update for a `DETECTED` recovery that is unblocked or suppression-blocked now schedules a recovery-specific targeted job on the existing capacity-resume queue. The processor performs its normal checkout lock, fresh Shopify lookup, current Shop-scoped recipient resolution and suppression recheck before any attempt, billing or provider work. The controlled regression exercises the deferred original write, absent-recipient wake-up, later checkout-update re-entry with a valid changed recipient, active-suppression zero-admission behavior, and one post-expiry attempt/charge/send. A contrasting terminal-checkout case remains cancelled. Attempt 4's A3-R2 combined-error retry handling is unchanged.
- No schema/migration, second scheduler, suppression poller, BACKGROUND-011 evidence write, provider-status/compensation behavior, immutable attempt recipient, or `_index.md` change.

#### Files Changed

Updated `checkout-event-orchestrator.service.ts`, `recovery-capacity-resume-processor.service.ts`, and `recovery-recipient-suppression-admission.service.ts`, with focused checkout-update, deferred-write, admission and worker fixture regressions. No database submodule gitlink was staged.

#### Validation Results

PASS: focused recovery/materialization/expiry/worker/checkout-lock unit matrix, 174 tests across 17 files (`pnpm exec vitest run tests/unit/services/checkout-recovery tests/unit/services/recovery-capacity-resume.service.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts tests/unit/runtime/recovery-entrypoint.capacity-resume.test.ts tests/unit/workers/pending-recovery-candidate.worker.test.ts tests/unit/workers/recovery-capacity-resume.worker.test.ts tests/unit/services/pending-recovery-candidate/checkout-order-guard.service.test.ts`).

PASS: disposable PostgreSQL `tests/integration/recovery-outreach-recipient.integration.test.ts`, 2 tests (`pnpm run test:integration tests/integration/recovery-outreach-recipient.integration.test.ts`).

PASS: `pnpm run build` (Prisma Client generation and TypeScript compilation) and `pnpm run prisma:validate`.

PASS: changed-file diagnostics (no errors) and `git diff --check`.

The first unit pass exposed stale test doubles missing the new recovery-version read; those fixtures were updated and the final matrix passed. The first build also caught Prisma's rejection of `null` in an enum `in` filter; the nullable predicate was expressed as `OR` and the build and focused tests then passed. The full repository suite was not run.

#### Attempt 5 Preparation and Publication Evidence

Claimed attempt: 5 (`copilot`, 2026-10-11T19:15:23Z), launcher claim commit `0b3961b2589237feda3d386c982612d402cc79a7`, pushed by the launcher. Parent starting head `33e43482776f613d8b625b1b3c88670d9865dcb9`; implementation starting head `03fd86794694a0231b390fa6f9d87c45918b005b`.

The launcher reused the canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-010` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-010`, both on `task/ARCH-028-BACKGROUND-010`; canonical workspace resolution returned `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent and implementation synchronization passed; task-branch fast-forwards were not needed. Recursive submodule sync/update passed and `database` remained at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

Implementation correction commit: `6c3fd349bd7a1832c9988e6f619d37bdf224a221` (pushed to `task/ARCH-028-BACKGROUND-010`). Parent report commit: this Attempt 5 report update on `task/ARCH-028-BACKGROUND-010`.

### Attempt 6 — A5 Review Corrections and Validation

#### Corrections

- **A5-R1:** Checkout updates for eligible `DETECTED` recoveries retain the established Shopify lookup and explicit provider-error, not-found, ambiguous/bounded-result, and recovery-terminal handling. A found open checkout refreshes durable `currency`, `totalPrice`, `checkoutUrl`, and serialized `lineItems` through the status-guarded transaction before targeted re-entry is scheduled. The regression uses fresh values distinct from the prior durable snapshot and asserts the refresh write precedes scheduling.
- **A5-R2:** Checkout-update re-entry is scheduled for the latest persisted activity plus the resolved `recoveryDelayMinutes`. A targeted job rechecks latest activity and policy under the existing checkout lock; if the maturity time is still in the future, it schedules a deterministic maturity child and performs no checkout lookup or initiation. Controlled-time coverage verifies newer activity supersedes a stale job, admission occurs once after maturity, and duplicate maturity execution does not initiate again. Active suppression remains ahead of attempt, billing and provider admission.
- **A5-R3:** The pre-enqueue `updatedAt` version-read failure now throws the distinct `RECIPIENT_SUPPRESSION_ADMISSION_RETRY_REQUIRED` marker with the underlying database error as `cause`. The pending-candidate worker recognizes this marker only on a retried job and re-enters the already-persisted `DETECTED` generation. Cross-component coverage fails the read once after recovery creation, then verifies the retry schedules the suppression wake-up without creating an attempt, billing admission or provider send.
- No schema/migration, new queue, scheduler, suppression polling, reachability evidence writer, compensation, provider-status change, or `_index.md` edit was introduced. Prior A4-R1, A3-R2, suppression CAS, canonical-recipient and terminal-checkout behavior remain covered.

#### Files Changed

Updated `checkout-event-orchestrator.service.ts`, `recovery-capacity-resume-processor.service.ts`, `recovery-recipient-suppression-admission.service.ts`, and `pending-recovery-candidate.worker.ts`, with focused checkout-update, maturity, version-read retry and projection-aware Prisma test-double regressions. No database submodule gitlink was staged.

#### Validation Results

PASS: task-owned recovery/maturity/worker/checkout-lock unit matrix, 175 tests across 17 files (`pnpm exec vitest run tests/unit/services/checkout-recovery tests/unit/services/recovery-capacity-resume.service.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts tests/unit/runtime/recovery-entrypoint.capacity-resume.test.ts tests/unit/workers/pending-recovery-candidate.worker.test.ts tests/unit/workers/recovery-capacity-resume.worker.test.ts tests/unit/services/pending-recovery-candidate/checkout-order-guard.service.test.ts`). The narrower A5 regression slice also passed, 50 tests across 4 files.

PASS: disposable PostgreSQL `tests/integration/recovery-outreach-recipient.integration.test.ts`, 2 tests (`pnpm run test:integration tests/integration/recovery-outreach-recipient.integration.test.ts`).

PASS: `pnpm run build` (Prisma Client generation and TypeScript compilation), `pnpm run prisma:validate`, changed-file diagnostics on all seven changed files (no errors), and `git diff --check`.

The complete repository test suite was not run. Touched production module sizes are: checkout event orchestrator 282 lines; capacity-resume processor 271; suppression admission service 110; pending-candidate worker 107. All remain below the task's 300-line ceiling.

#### Attempt 6 Preparation and Publication Evidence

Claimed attempt: 6 (`copilot`, 2026-10-11T19:51:50Z), launcher claim commit `d60892c4cb2785a8ee4535d2de975c3864dd7ca9`, pushed by the launcher. Parent starting head `72f01c4bb453026b6323273806a74d06854efe72`; implementation starting head `6c3fd349bd7a1832c9988e6f619d37bdf224a221`.

Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-010`, branch `task/ARCH-028-BACKGROUND-010`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-010`, same task branch. The implementation database submodule remained at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

Implementation correction commit: `398fbb56a1753e41d56e3ebd93d60bb06e916116`, pushed to `task/ARCH-028-BACKGROUND-010`. Parent report commit: this Attempt 6 report update on `task/ARCH-028-BACKGROUND-010`.

### Attempt 7 — Distinct Maturity Successors and Activity-Serialized Admission

#### Corrections

- **A6-R1:** Maturity successors now include a stable hash of the active trigger in their deterministic identity, alongside recovery and latest activity identity. Duplicate active-trigger retries still derive the same child, while a child that re-defers derives a different ID. Controlled-time coverage extends policy from 30 to 60 minutes, verifies the distinct successor and exact deadline, then verifies once-only admission at the extended deadline.
- **A6-R2:** Checkout activity writes and resume's final admission decision now share the same Shop/checkout-scoped lock. Resume keeps Shopify lookup, snapshot construction and recipient resolution outside the lock, then reacquires it and re-reads durable status, block reason, execution eligibility and latest activity/maturity before terminalization, suppression handling or initiation. A controlled interleaving commits newer checkout activity during the unlocked lookup and proves the resume defers until the newer maturity, then admits once.
- Extracted unlocked checkout preparation and maturity scheduling into focused modules so the processor remains within the 300-line production-source ceiling. Existing A5-R1/A5-R3, A4-R1, A3-R2, canonical recipient, terminal-checkout, retry and suppression behavior remains covered. No schema, queue, poller, reachability writer, compensation, provider-status, or `_index.md` changes were made.

#### Files Changed

Updated `src/domain/recovery-capacity-resume.ts`, `src/services/checkout-recovery/checkout-event-orchestrator.service.ts`, and `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`; added `recovery-capacity-resume-checkout-preparation.ts` and `recovery-capacity-resume-maturity.ts`; updated the deterministic successor, activity interleaving, processor maturity, and service-level capacity-resume tests.

#### Validation Results

PASS: task-owned unit matrix — 18 files, 179 tests (`pnpm exec vitest run tests/unit/services/checkout-recovery tests/unit/services/recovery-capacity-resume.service.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts tests/unit/runtime/recovery-entrypoint.capacity-resume.test.ts tests/unit/workers/pending-recovery-candidate.worker.test.ts tests/unit/workers/recovery-capacity-resume.worker.test.ts tests/unit/services/pending-recovery-candidate/checkout-order-guard.service.test.ts tests/unit/domain/recovery-capacity-resume.test.ts`).

PASS: disposable PostgreSQL/Redis integration `tests/integration/recovery-outreach-recipient.integration.test.ts` — 2 tests.

PASS: `pnpm run build` (Prisma Client generation and TypeScript compilation), `pnpm run prisma:validate`, changed-file diagnostics for all nine changed files, and `git diff --check`.

Production source sizes: capacity-resume processor 289 lines; checkout-preparation helper 65; maturity helper 48; checkout event orchestrator 299; recovery-capacity-resume domain module 41. The complete repository suite was not run.

#### Attempt 7 Preparation and Publication Evidence

Claimed attempt: 7 (`copilot`, 2026-10-11T21:14:11Z), launcher claim commit `f4e79a7c438c4ccf156c3d29142f5aa4195769f6`, pushed by the launcher. Parent starting head `63fbc08e6fa5ab01a7d072a37bfb354a73a530b3`; implementation starting head `398fbb56a1753e41d56e3ebd93d60bb06e916116`.

Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-010`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-010`. Both use branch `task/ARCH-028-BACKGROUND-010`. The launcher dependency gate passed; parent and implementation task-branch fast-forwards were `not-needed`, and `origin/main` was already incorporated. Recursive submodule sync/update passed; the implementation database submodule remained at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

Implementation correction commit `29d0039f2435e646165c11b48f0fe263d32ae916` is pushed to `origin/task/ARCH-028-BACKGROUND-010`; the remote task ref matches this SHA and the implementation worktree is clean. This Attempt 7 report update is committed and pushed on the parent `task/ARCH-028-BACKGROUND-010` branch. The task is returned with `status: review`, `attempt: 7`, `executor: null`, and `claimed_at: null`.

### Attempt 8 — Bounded Checkout Admission Lock and Validation

#### Corrections

- **A7-R1:** The final checkout-scoped admission decision now runs through a short callback immediately before outreach-attempt creation. Checkout snapshot preparation, initiation work, billing, and provider I/O execute outside the non-renewed Redis checkout lease. The gate re-reads recovery status, block reason, and latest external activity while holding the Shop/checkout lock; if the latest activity has not matured, it schedules the existing deterministic maturity successor after releasing the lock. Checkout activity recording therefore does not wait behind slow billing/provider work, while activity persisted before the gate prevents stale admission.
- The gate runs before `RecoveryOutreachAttempt` creation, billing admission, or provider send. The controlled interleaving uses the production `CheckoutOrderGuardService` and a Redis test double implementing its `NX`/`PX` lease semantics. It records checkout activity while initiation is paused, advances beyond the 10-second lease horizon, records a further update, then verifies deferral to the newest maturity and bounded once-only admission after maturity.
- The existing terminalization transaction was moved unchanged into a focused module to keep the resume processor below the 300-line task limit. No schema, migration, queue, poller, reachability writer, compensation, provider-status behavior, or `_index.md` changed. Prior maturity-successor, two-phase revalidation, canonical-recipient, suppression retry, terminal checkout, and combined cleanup-error corrections are retained.

#### Files Changed

Updated `src/services/checkout-recovery.service.ts`, `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`, and `src/services/checkout-recovery/recovery-initiation.service.ts`; added `recovery-capacity-resume-admission-gate.ts` and `recovery-capacity-resume-terminalization.ts`; updated the resume processor and initiation unit tests.

#### Validation Results

PASS: task-owned unit matrix, 181 tests across 18 files (`pnpm exec vitest run tests/unit/services/checkout-recovery tests/unit/services/recovery-capacity-resume.service.test.ts tests/unit/services/checkout-recovery.capacity-resume.test.ts tests/unit/runtime/recovery-entrypoint.capacity-resume.test.ts tests/unit/workers/pending-recovery-candidate.worker.test.ts tests/unit/workers/recovery-capacity-resume.worker.test.ts tests/unit/services/pending-recovery-candidate/checkout-order-guard.service.test.ts tests/unit/domain/recovery-capacity-resume.test.ts`).

PASS: focused resume/initiation/checkout-lock matrix, 42 tests across 3 files (`pnpm exec vitest run tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/pending-recovery-candidate/checkout-order-guard.service.test.ts`).

PASS: disposable PostgreSQL/Redis `tests/integration/recovery-outreach-recipient.integration.test.ts`, 2 tests (`pnpm run test:integration tests/integration/recovery-outreach-recipient.integration.test.ts`).

PASS: `pnpm run build` (Prisma Client generation and TypeScript compilation), `pnpm run prisma:validate`, changed-file diagnostics (no errors), and `git diff --check`.

The full repository unit suite was not run. Production module sizes: admission gate 112 lines; terminalization helper 43; resume processor 269; checkout event orchestrator 299. No new production source file exceeds 200 lines.

#### Preparation and Publication Evidence

Claimed attempt: 8 (`copilot`, `2026-10-11T22:27:51Z`), launcher claim commit `5847759f460eeafcbe344153042457fed19a5b0d`, committed and pushed by the launcher.

Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-010`, branch `task/ARCH-028-BACKGROUND-010`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-010`, same branch. Shared workspace and implementation checkouts were not switched or mutated; no other task worktree was reused.

Start-of-attempt synchronization: parent task branch fast-forwarded `not-needed`, parent `origin/main` incorporated `yes`; implementation task branch fast-forwarded `not-needed`, implementation `origin/main` incorporated `already-current`.

Recursive implementation submodules: launcher `git submodule sync --recursive` and `git submodule update --init --recursive` passed; `database` resolved to `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

Implementation correction commit `61a40a7` is pushed to `origin/task/ARCH-028-BACKGROUND-010`. This Attempt 8 parent report update is committed and pushed to the same task branch. The task is returned to `review`; Architect acceptance remains pending.

## Architect Review

### Review Status

Changes Requested — Attempt 8 (2026-10-12). The shortened checkout-locked admission gate addresses A7-R1's lease-lifetime design in isolated processor tests, but the production `CheckoutRecoveryService` initiation adapter drops its fifth `admissionGate` argument. Thus production resume bypasses the final maturity/eligibility gate and can admit early. A8-R1 is the sole blocking correction. Return this SAME task to `ready` with `attempt: 8`, `executor: null`, and `claimed_at: null`; `ARCH-028-BACKGROUND-011` remains Pending. No architect acceptance has occurred.

### Review Notes

#### Attempt 8 — current Architect correction contract (2026-10-12)

- **Disposition: Changes Requested; bounded Attempt 9.** Background implementation `61a40a7c9cd2abceba0a46cfd33c53362e0fefee` and parent task report `eaf9e0cad60fceb7ad2dfe6b9833397a103c8199` match the remote `task/ARCH-028-BACKGROUND-010` branch tips. The uploaded parent task document Git blob `6f146c6fdf4e41b5294dd5648f5481e86e1dcb70` matches its remote blob, and all seven changed implementation-file blobs match the published implementation. Task YAML was `status: review`, `attempt: 8`, claim cleared. Prepared worktree/synchronization/recursive-submodule evidence is recorded in the Completion Report; local developer-machine worktree cleanliness cannot be independently verified from an archive.
- **A7-R1 — Bounded-lock design fixed in isolation.** The resume processor now completes Shopify lookup and other slow preparation outside the checkout mutex. Its late activity/maturity decision is moved into `recovery-capacity-resume-admission-gate.ts`, executed only when an initiation callback explicitly forwards/invokes the gate. The controlled test uses the production checkout lock class with a fake NX/PX Redis lease, persists newer activity while initiation is paused, crosses the former 10-second lease window, and proves no premature mock admission when the gate is supplied. Previous maturity successor, snapshot refresh, suppression CAS/retry, recipient and terminal safeguards remain intact. These tests do not prove actual runtime callback wiring.
- **A8-R1 — Blocking: production initiation adapter silently drops the new gate.** In `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts` lines 248–254 the processor passes five arguments, including `admissionGate.check`, to its `initiate` port. But the real wiring in `src/services/checkout-recovery.service.ts` lines 93–101 constructs the processor with an arrow callback accepting only `(seed, generation, recipient, wakeupTrigger)` and calling `this.handleCheckoutCreated(...)` with those four arguments. Although `CheckoutRecoveryService.handleCheckoutCreated()` itself accepts and forwards an optional fifth gate argument, this construction loses it. The target `RecoveryInitiationService.handleCheckoutCreated()` then sees `admissionGate === undefined` at line 158 and unconditionally continues to `RecoveryOutreachAttempt.getOrCreate()`, billing admission and provider work. In particular, an activity update persisted while initiation prepares may be disregarded despite not having matured. **Required:** forward `admissionGate` through the production adapter into `CheckoutRecoveryService.handleCheckoutCreated()`; add a *production-composition/wiring* regression (not another processor-only injected-spy test) proving that a targeted resume invokes the gate and that newer durable activity defers before `RecoveryOutreachAttempt` creation, billing or WhatsApp provider admission. Retain the current short checkout-lock boundary and all previously accepted fixes.
- **Scope and validation:** A8-R1 belongs to the SAME BACKGROUND-010 task and should require only narrow service-composition wiring and focused test coverage. Do not change database schema, shared contracts, queue infrastructure, compensations, reachability writers, task dependencies, other domains or any `docs/decisions/**/_index.md`. The agent reports 181 task-owned unit tests (including 42 focused), two disposable PostgreSQL/Redis integration tests, build, Prisma validation, diagnostics and `git diff --check` passing; architect inspected changed source and relevant tests but did **not** independently rerun those suites because the archive lacks installed dependencies. The full repository suite was not run.

#### Attempt 7 — historical Architect correction contract (2026-10-11)

- **Disposition: Changes Requested; bounded Attempt 8.** Background implementation `29d0039f2435e646165c11b48f0fe263d32ae916` and parent report `5529b32050d7ff83bda05698fbbab93ae23d2e36` independently match their remote `task/ARCH-028-BACKGROUND-010` refs. The uploaded parent document Git blob `1a1f9fb155f955b008af35320c6de1b84188ec0b` matches the remote task document. The task is correctly `review`, Attempt 7, claim cleared; reported physical task worktree evidence is recorded, not directly verified on the developer machine.
- **A6-R1 — Resolved.** `createRecoveryCapacityResumeMaturitySuccessor()` hashes the active trigger into the next deterministic job identity. Duplicate retries of that trigger converge, and successive early maturity jobs no longer collide with their currently active parent. Unit tests cover a 30-to-60-minute policy extension and once-only admission; the Architect independently executed the standalone domain helper and verified same-source/different-successor identity.
- **A6-R2 — Targeted lookup interleaving resolved, but lock-lifetime gap remains.** The processor now separates slow Shopify lookup/recipient preparation from final revalidation; checkout update activity writes use the same Shop/checkout lock. The controlled test establishes that a newer update persisted during Shopify lookup causes maturity deferral rather than early admission. Preserve this two-phase flow and the accepted snapshot/retry/canonical-recipient/terminal safeguards.
- **A7-R1 — Blocking: final admission holds a non-renewed short-lived checkout lock across slow initiation.** `recovery-capacity-resume-processor.service.ts` lines 155–231 keeps the second `withCheckoutLock` callback active while awaiting `this.initiate(...)` at line 219. The actual `RecoveryInitiationService.handleCheckoutCreated()` awaits customer/policy work, billing admission and `outboundWhatsAppAdmissionService.sendTemplate()`, which in turn awaits a WhatsApp provider network call. `CheckoutOrderGuardService` grants an unrenewed Redis mutex with `CHECKOUT_LOCK_TTL_MS = 10_000`, and another caller exhausts `CHECKOUT_LOCK_RETRIES = 30` × `CHECKOUT_LOCK_RETRY_DELAY_MS = 100` (roughly three seconds). Attempt 7 now routes `CheckoutEventOrchestratorService.recordExternalActivity()` through that same lock. Therefore a legitimate checkout-update job can fail its activity write while slow initiation still owns the lock; if initiation outlives ten seconds, another writer can acquire an expired lease while the original callback continues towards attempt/billing/provider work without checking lease ownership or later persisted activity. The in-memory interleaving test uses an indefinitely held mock mutex and cannot prove real Redis lease/timeout behavior. **Required:** preserve a valid checkout-scoped admission linearization point without making activity recording depend upon an unbounded provider/billing operation under a ten-second non-renewed lease. Keep slow provider I/O outside the bounded lock, or establish an equivalently safe explicit lease/fencing mechanism; ensure the activity event is retriable without silently losing its maturity effect. Add a controlled slow-initiation/lease-expiry test (covering the activity writer's acquisition timeout and an expired lease) that proves no stale/duplicate billable/provider admission and preserves bounded eventual re-entry. Do not introduce a new queue, poller, schema change or cross-repository contract change solely for this correction.
- **Scope and evidence:** Correct A7-R1 in the SAME BACKGROUND-010 task. Preserve the fixed maturity successor, two-phase snapshot preparation/recheck, previous A5-R1/R3, A4-R1, A3-R2, suppression and tenant-safe recipient behavior. Run focused real-lock or faithful lease-expiry tests, the existing maturity/interleaving/suppression regressions, disposable PostgreSQL integration, build, Prisma validation, diagnostics and `git diff --check`. Do not promote BACKGROUND-011 or update any `_index.md` file before architect-accepted completion and the user's authorization.

#### Attempt 6 — current Architect correction contract (2026-10-11)

- **Disposition: Changes Requested; bounded Attempt 7.** Background implementation `398fbb56a1753e41d56e3ebd93d60bb06e916116` and parent report `676463226864a660c6417439b4bb49d67645b7d5` match their remote `task/ARCH-028-BACKGROUND-010` branch tips. The uploaded parent file Git blob `467b2379c804d515c5eb560b9b1eddf7928eb25a` matches remote, as do the four modified production-module blobs. Source review identified only the two bounded findings below; earlier Completion Reports and Architect Review entries remain historical, including their then-current labels.
- **A5-R1 — Resolved.** `CheckoutEventOrchestratorService.handleCheckoutUpdatedContract()` retains the previous Shopify lookup/provider-error/bounded-result handling and status-guarded refresh of currency, total price, checkout URL and serialized line items before targeted scheduling. The new regression asserts changed durable values and write-before-schedule ordering. Preserve this behaviour.
- **A5-R3 — Resolved.** `RecoveryRecipientSuppressionAdmissionService.deferDetectedRecovery()` wraps a failed pre-enqueue version read as `RECIPIENT_SUPPRESSION_ADMISSION_RETRY_REQUIRED` with the underlying exception in `cause`. The pending-candidate worker recognises that marker only for a retried job; the cross-component test re-enters the same DETECTED generation and schedules the suppression resume with no attempt, billing or provider send. Preserve the earlier combined Redis cleanup-error handling.
- **A5-R2 — Partially resolved.** Checkout-update re-entry supplies `dueAt` based on the latest persisted activity and the merchant's policy. Targeted resume re-reads activity and policy after locking and schedules a maturity successor if still early. The existing test covers an older job after a newer activity timestamp *already exists*, but does not cover active successor-ID collision or concurrent activity committed after the locked read.
- **A6-R1 — Blocking: an active maturity job can silently swallow its own successor.** `recovery-capacity-resume-processor.service.ts` lines 120-132 generates `recipient-suppression-${recovery.id}-maturity-${lastExternalActivityAtMs}` whenever due time is still in the future. `createRecoveryCapacityResumeJobId()` uses the trigger as the job identity, and BullMQ does not enqueue a duplicate ID while the original job is active. If a merchant extends `recoveryDelayMinutes` after a maturity child has been scheduled, that child can execute early relative to the revised policy and attempt to enqueue **itself**. `schedule()` can resolve without a new delayed job; the current worker completes and is removed, leaving the open DETECTED recovery with no future wake-up. **Required:** derive a deterministic successor identity distinct from the currently executing trigger (including when policy changes or an early worker re-defers), retaining duplicate-worker deduplication; do not introduce a poller or second queue. Add a regression that fires a maturity child after a 30-to-60-minute policy extension, verifies a distinct queued child and exact later deadline, then proves bounded once-only admission when the extended deadline is reached.
- **A6-R2 — Blocking: checkout activity is not serialized with resume admission.** `checkout-event-orchestrator.service.ts` line 183 calls `recordExternalActivity()` outside the checkout lock. `recovery-capacity-resume-processor.service.ts` checks `lastExternalActivityAt` once inside its lock (lines 89-132), then awaits the remote checkout lookup/build/initiation without a further activity-based admission gate. A checkout update can persist newer T1 while that lookup is pending; the resume can then perform attempt, billing and provider admission using the old T0 maturity decision before T1's inactivity period expires. The checkout lock alone does not protect the activity writer. **Required:** establish a checkout-scoped admission linearization/revalidation boundary such that activity committed before the admission decision prevents premature outreach and leaves an appropriate future wake-up; preserve tenant scope, no external I/O inside a DB transaction, and no global serialization. Add a controlled interleaving: pause resume after old maturity passes, persist a newer checkout activity during the lookup, release the lookup, and prove zero early attempt/billing/provider call plus eventual once-only admission after new maturity.
- **Scope and evidence:** Correct A6-R1/A6-R2 in the SAME BACKGROUND-010 task; retain all A5-R1/A5-R3, A4-R1, A3-R2 and canonical-recipient/suppression safety corrections. No schema/migration, new queue, polling, merchant reachability writer, compensation, provider-status, or `_index.md` edits. Run focused queue-identity/maturity/interleaving regression tests, accepted suppression retry and terminal tests, disposable PostgreSQL integration, declared build/Prisma validation, diagnostics and `git diff --check`. Do not start BACKGROUND-011 before architect-accepted completion.

#### Attempt 5 — current Architect correction contract (2026-10-11)

- **Disposition: Changes Requested; bounded Attempt 6.** Verified Background implementation commit `6c3fd349bd7a1832c9988e6f619d37bdf224a221` and parent Completion Report commit `f0255ccd96df492a93629ad3ec970bd9e9e09ffb` are the respective remote `task/ARCH-028-BACKGROUND-010` branch tips. Uploaded parent task blob `82f255d196dc86b8190df68cd4457b09fb410560` matches remote, as do the three modified runtime-module blobs. Preserve all prior Completion Reports and Architect Review history. `ARCH-028-BACKGROUND-011` remains Pending.
- **A4-R1 — Resolved.** A targeted wake-up with an open checkout but absent current recipient now retains the `DETECTED` recovery and touches/clears only its eligible suppression state. The guarded `updatedAt` write prevents the original delayed suppression deferral from restoring a stale block after that wake-up. The controlled regression later supplies a current recipient, re-evaluates Shop-scoped active suppression, and exercises expiry admission. Actual terminal checkout cancellation is preserved. **A3-R2 remains resolved:** Redis enqueue/lock/index-cleanup failures retain the tagged bounded retry marker and diagnostic causes. Do not regress these corrections.
- **A5-R1 — Blocking: durable checkout snapshot refresh is skipped for DETECTED recoveries.** `checkout-event-orchestrator.service.ts` lines 150–163 now return after recording activity and queuing a resume whenever `DETECTED` has a null or WhatsApp-suppression admission reason. This bypasses the previously shared Shopify lookup and persisted `currency`, `totalPrice`, `checkoutUrl`, and `lineItems` refresh at lines 184–225. The resume path fetches a current checkout only for recipient/seed resolution; `recovery-initiation.service.ts` lines 39–64 returns the already-existing recovery on the unique-key conflict without refreshing its durable fields. `recovery-agent-context.service.ts` consumes the stored recovery `totalPrice`. **Required:** preserve the established checkout-update snapshot refresh for open DETECTED recoveries while adding eligible recipient re-entry; keep current Shopify lookup errors/terminal handling explicit. Prove a changed checkout price, URL and line items reach durable recovery state and that re-entry does not silently discard those updates. Do not weaken canonical recipient, suppression or tenant constraints.
- **A5-R2 — Blocking: checkout-update re-entry bypasses recovery inactivity/maturity.** The new `recoveryResumeScheduler.schedule({shopId,recoveryId,trigger})` call passes no `dueAt`; the existing resume service enqueues it immediately, and `RecoveryCapacityResumeProcessorService.resume()` does not check the policy's `recoveryDelayMinutes` against the latest `lastExternalActivityAt` before initiating. This turns an active checkout update (including unrelated/duplicate updates on eligible DETECTED rows) into an immediately actionable recovery, whereas the normal pending-candidate path matures only after the configured inactivity window. **Required:** preserve checkout-activity/maturity policy for jobs triggered by checkout updates. Use the existing delayed resume queue where appropriate, and recheck the latest durable activity at execution so an older delayed job cannot send before a newer update's maturity. Retain correct suppression expiry and already-terminal behavior. Prove controlled-time newer-activity/stale-job and post-maturity cases, with zero pre-maturity attempt, charge or provider send and bounded idempotent admission after maturity. No new scheduler or busy polling.
- **A5-R3 — Blocking: a newly added read can fail before any wake-up is scheduled without enabling the targeted retry.** `RecoveryRecipientSuppressionAdmissionService.deferDetectedRecovery()` now calls `checkoutRecovery.findUnique()` (lines 42–45) **before** the try/catch that tags `RECIPIENT_SUPPRESSION_RESUME_ENQUEUE_FAILED` for queue failures. If the initial recovery was already materialised, a transient error during this version read produces an untagged pending-candidate job failure. `pending-recovery-candidate.worker.ts` retries that job with `retrySuppressionAdmission: false`, so `RecoveryMaterializationService` treats the existing DETECTED recovery as `no-op-existing`; no suppression wake-up was enqueued and the retry can silently finish. **Required:** make failures of the new pre-enqueue version read use a diagnostic, unambiguous bounded suppression-admission re-entry signal recognized by the existing worker; preserve the underlying cause and do not reopen unrelated DETECTED recoveries. Add a cross-component test where the version read fails once after durable recovery creation, then succeeds on tagged retry, scheduling the delayed wake-up with no early attempt, billing or Meta send.
- **Scope and validation:** Keep the existing Shop-scoped reachability key, `CustomerPhone` recipient resolution, suppression CAS, actual-terminal cancellation, Retry A3-R2 aggregate causes, attempt generation and idempotency. No schema/migration changes, reachability evidence writers (BACKGROUND-011), compensation, provider-status logic, additional queue or suppression poller. Validate checkout refresh/re-entry timing and error-marker regressions, existing controlled overtaking-write/terminal tests, worker tests, the disposable PostgreSQL matrix, declared build and Prisma validation, changed-file diagnostics and `git diff --check`. Preserve the complete historical Architect Review and all Completion Reports. Do not update `docs/decisions/**/_index.md` or start BACKGROUND-011.

#### Attempt 4 — current Architect correction contract (2026-10-11)

- **Disposition: Changes Requested; bounded Attempt 5.** The remote Background task branch resolves to implementation `03fd86794694a0231b390fa6f9d87c45918b005b`; the remote parent task branch resolves to report `08f3a565c27aaa5801a283b829303d8d7adf9c67`. The submitted task document is the same Git blob as the remote task branch (`49c334b982497ee56b97fd440643be62ac37f805`). Preserve all Completion Reports and all historical Architect Review content. `ARCH-028-BACKGROUND-011` remains Pending.
- **A3-R2 — Resolved.** `checkout-order-guard.service.ts` and `pending-recovery-candidate.worker.ts` retain the original `RECIPIENT_SUPPRESSION_RESUME_ENQUEUE_FAILED` prefix through simultaneous Redis lock-release/index-cleanup failures. Both failures remain available via nested `AggregateError` causes and the exception messages. The tagged worker retry re-enters the original `DETECTED` generation and schedules the existing delayed wake-up, without an attempt, billing or Meta send. The focused combined-failure regression covers this path. Retain these changes.
- **A3-R1 terminal checkout — Resolved.** A targeted wake-up that overtakes the original suppression write can conditionally terminalize a checkout already completed or not found. Its status compare-and-set prevents the late original write from restoring a suppression block, and the deferred-write terminal regression exercises this.
- **A4-R1 — Blocking: no-current-recipient is not a terminal checkout condition.** `recovery-capacity-resume-processor.service.ts` now calls `terminalizeUnrecoverableBlockedRecovery(..., true)` when the targeted wake-up finds a still-open checkout but no current canonical recipient (lines 162–171). This changes the recovery from `DETECTED` to `CANCELLED` (lines 190–229). The new test asserts `CANCELLED` rather than later re-entry. However `checkout-event-orchestrator.service.ts` ignores all checkout updates for `CANCELLED` recoveries (lines 133–143), and `recovery-materialization.service.ts` refuses candidate materialization for `CANCELLED` (lines 83–106). A temporarily missing recipient therefore becomes a permanent rejection of that checkout, even if a usable changed recipient appears later. The proposed BACKGROUND-012 handoff explicitly applies to *no recovery* and preserves terminal-recovery handling; it will not repair this path. This conflicts with ARCH-028's finite, recipient-dependent suppression and later recipient re-entry intent. **Required:** preserve a valid future re-entry route for an otherwise still-open checkout without allowing the delayed original suppression write to strand a block. Do not equate absence of a current phone with a terminal checkout. Keep actual completed/not-found checkout cancellation and the A3-R2 combined-error retry correction unchanged.
- **Proof required:** Add a controlled overtaking-write/no-current-recipient test that subsequently supplies a valid Shop-scoped recipient and demonstrates a bounded re-entry through the approved existing lifecycle; no stale suppression block, duplicate attempt or charge, provider send during absent/active suppression, second scheduler, polling or schema change. Include a contrasting terminal-checkout regression. Run focused relevant units/worker tests, the disposable PostgreSQL test, build, Prisma validation, diagnostics and `git diff --check`. Do not modify `_index.md` files or start BACKGROUND-011.

#### Attempt 3 — current Architect correction contract (2026-10-11)

- **Disposition: Changes Requested; bounded Attempt 4.** The pushed implementation `b9860933581cc2f4998b950a348a9f031f745c2c` and parent report `c244cebc39374aea4806abce10e2aa696e8851d2` match their remote `task/ARCH-028-BACKGROUND-010` refs. Database remains `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. Preserve all three Completion Reports and the complete historical Architect Review. `ARCH-028-BACKGROUND-011` remains Pending.
- **A2-R1 and A2-R2 — demonstrated ordinary paths corrected.** The pending-candidate worker now recognizes a tagged suppression-resume enqueue failure and permits only that retry to re-enter the already materialized `DETECTED` recovery at its original generation, with a fresh checkout/recipient/suppression read and no attempt/billing/provider admission during suppression. A targeted wake-up can initiate a distinct deterministic child job while an earlier suppression write is pending. Cross-component tests now exercise a successful tagged worker retry and an active-suppression early-wake-up interleaving. These improvements are retained; the remaining findings are narrower failure branches, not a request to undo them.
- **A3-R1 — Overtaking wake-up with absent recipient or terminal checkout can still strand the original block.** `RecoveryCapacityResumeProcessorService.resume()` accepts an unblocked `DETECTED` row for a targeted suppression trigger. If current canonical recipient resolution returns `null`, the `!recipient` branch returns `no-recipient` without scheduling a child; if the checkout is not found or already completed, `terminalizeUnrecoverableBlockedRecovery()` only updates rows already marked capacity/suppression blocked and therefore cannot terminalize that still-unblocked row. A slow original `deferDetectedRecovery()` update can then persist `WHATSAPP_RECIPIENT_SUPPRESSED` **after** the only targeted wake-up has been consumed, leaving no replacement job. The Attempt 3 interleaving regression tests only the active-recipient, still-suppressed branch. **Required:** make the overtaking-job/state-write handoff fail-safe across the no-current-recipient and terminal-checkout branches as well, using the existing lock/queue/state contracts, and assert that no late durable suppression block can be stranded. When there is no current recipient, continue to create no attempt, billing admission or provider send; when checkout is terminal, do not resurrect it. Include controlled deferred-write regressions for these branches.
- **A3-R2 — Redis cleanup can hide the tagged enqueue failure and disable re-entry.** `RecoveryRecipientSuppressionAdmissionService.deferDetectedRecovery()` correctly throws `RECIPIENT_SUPPRESSION_RESUME_ENQUEUE_FAILED` when BullMQ scheduling rejects, and `pending-recovery-candidate.worker.ts` enables retry re-entry only if `job.failedReason` equals that exact marker. However, `CheckoutOrderGuardService.withCheckoutLock()` performs Redis GET/DEL in `finally`, and the candidate worker calls `pendingRecoveryCandidateService.handleCandidateMatured()` (Redis index DEL/ZREM) in its own `finally`. If queue publishing fails because Redis is unavailable, either cleanup can also fail, overriding the marked error in JavaScript; the next BullMQ attempt then sees a different `failedReason`, treats the existing `DETECTED` recovery as `no-op-existing`, and can complete without any wake-up. The Attempt 3 cross-component test stubs both cleanups as always successful. **Required:** preserve an unambiguous recoverable retry indication across a combined scheduling + lock/index-cleanup failure, without automatically reopening unrelated existing recoveries. Prove the original `DETECTED` recovery/generation is retried and a delayed wake-up is scheduled when Redis recovers, with zero premature attempt, billing or provider send. Do not silently discard cleanup failures; keep cleanup behaviour safe and diagnostically visible.
- **Scope and validation:** This remains BACKGROUND-010 liveness work. Keep A1-R1 canonical-recipient resolution, exact Shop-scoped suppression matching, follow-up admission, immutable attempt recipient evidence and accepted Database schema unchanged. Use existing queues/checkout locks only; no suppression polling or second scheduler. Run focused worker/materialization/expiry interleaving tests, disposable PostgreSQL tests, build, Prisma validation, diagnostics and `git diff --check`. Do not modify `docs/decisions/**/_index.md` and do not begin BACKGROUND-011.

#### Attempt 2 — historical Architect correction contract (2026-10-11)


- **Disposition: Changes Requested, bounded Attempt 3.** The implementation and parent report remote task refs were verified at `43d14e7355f2027958ccb982b484017b14fce825` and `7eca3cce45ccf7463b2a73c543f6b7ac98a76020` respectively. Preserve the full Attempt 1/2 Completion Report and the historical review below. `ARCH-028-BACKGROUND-011` stays Pending.
- **A1-R1 — Resolved.** `recovery-capacity-resume-processor.service.ts` now obtains the current canonical recipient from the fresh checkout resolution path, falls back only to the owning Shop's current CustomerPhone when needed, and forwards the resolved number and generation to initiation. For genuinely absent current phone it conditionally clears the still-DETECTED suppression block and skips attempt creation, billing and provider admission. The changed-number, stored-phone and absent-phone tests address the original finding. Do not reopen this behaviour without new evidence.
- **A2-R1 — Enqueue failure still strands an existing DETECTED recovery (A1-R2 incomplete).** `recovery-initiation.service.ts` creates/loads a durable DETECTED recovery before calling `deferDetectedRecovery()`. Attempt 2 schedules before writing the block: on `Queue.add` rejection, `updateMany` is skipped, but the DETECTED recovery is already persisted. `pending-recovery-candidate.worker.ts` always calls `handleCandidateMatured()` in `finally`, and `recovery-materialization.service.ts` returns `no-op-existing` for DETECTED recoveries. The generic `recovery-capacity-resume.service.ts` repair query selects only `RECOVERY_CAPACITY_EXHAUSTED`, not these unblocked DETECTED rows. Therefore ordinary BullMQ job retry, candidate replay and capacity repair do not prove a path back to admission after a transient scheduling failure. **Required:** establish an idempotent, bounded re-entry/retry route for this already-created DETECTED recovery that re-reads the current Shop/canonical-recipient/suppression state before any attempt or billing. Prove transient queue failure followed by recovery of the existing queue eventually reaches the appropriate delayed suppression wait or valid initiation, without an early paid/provider attempt. Do not rely on `admissionBlockReason: null` alone as recovery evidence and do not abuse the capacity-exhaustion reason.
- **A2-R2 — Schedule-before-persist permits an overtaking expiry job.** `recovery-recipient-suppression-admission.service.ts` now awaits the delayed BullMQ add before persisting `WHATSAPP_RECIPIENT_SUPPRESSED`. The job may become executable before the subsequent database update commits (near-expiry deadline, slow database or process pause). `recovery-capacity-resume-processor.service.ts` then ignores the still-unblocked recovery, after which the write can leave a suppressed row with no remaining wake-up. The `+1_000 ms` queue delay is a grace interval, not a correctness guarantee. **Required:** make this ordering fail-safe using the existing queue/checkout-lock lifecycle or an equivalent bounded retryable state path; demonstrate, with deterministic deferred promises/a controlled worker interleaving, that a wake-up overtaking the DB write does not strand the recovery, duplicate an attempt, or bill/send during active suppression. No new periodic suppression poller or second scheduler.
- **Scope/validation:** Keep the accepted Shop/recipient exact-match read, immutable attempt recipient evidence, follow-up gate, database constraints and BACKGROUND-011 reachability-writer boundary unchanged. Add cross-component tests that exercise the actual `upsertRecovery` -> suppression enqueue -> candidate worker retry/no-op and targeted resume sequence, not just a service-level assertion that an enqueue failure avoids `updateMany`. Re-run relevant focused unit/disposable PostgreSQL checks, build, Prisma validation, diagnostics and `git diff --check`; report actual failures and commands.

#### Attempt 1 — historical Architect Review (preserved below)

- **Historical disposition:** Changes Requested — Attempt 1 (2026-10-11); task returned to ready at `attempt: 1` after A1-R1 and A1-R2 were raised. The current decision above supersedes the historical follow-up instructions below.

- **A1-R1 — Canonical recipient resolution must survive suppression-expiry re-entry.** Normal materialisation (`recovery-materialization.service.ts`) resolves the current recipient with `recoveryRecipientResolverService.resolve(seed)` and passes that exact Shop-scoped canonical phone to `handleCheckoutCreated(seed, generation, recipient)`. By contrast, `recovery-capacity-resume-processor.service.ts` calls its `initiate(seed)` or `initiate(seed, generation)` port without a recipient, and `recovery-initiation.service.ts` then falls back to `event.customer.phone` or the test-only recipient. A fresh Shopify checkout may omit `customer.phone` while the owning Shop's durable `CustomerPhone` is populated, so the suppression-expiry job can fail even though the normal materialisation path would admit the correct recipient. Do not select a stale/fallback phone for billing. Reuse the canonical current-recipient resolver at this resume boundary and supply the same recipient into the existing initial-admission check and attempt snapshot. Maintain generation, lock, checkout lookup, no-recipient zero-billing and idempotency semantics; handle a missing current recipient safely without a permanent expired suppression block. Add targeted regressions for null checkout phone plus valid current Shop-scoped CustomerPhone, a changed current number using its independent suppression key, and genuinely absent current phone.
- **A1-R2 — An enqueue failure must not strand a durable suppression block.** `RecoveryRecipientSuppressionAdmissionService.deferDetectedRecovery()` first updates a DETECTED recovery to `WHATSAPP_RECIPIENT_SUPPRESSED` and only then awaits `recoveryCapacityResumeService.schedule()`. If BullMQ add fails, that row remains blocked without a targeted expiry job. The existing repair query and generic resume batches intentionally select only `RECOVERY_CAPACITY_EXHAUSTED`; a retry of matured candidate materialisation returns `no-op-existing` for DETECTED recoveries. Consequently a temporary queue failure can leave this recovery indefinitely blocked despite finite `suppressUntil`. Ensure durable admission state and expiry wake-up cannot diverge into a nonrecoverable state; use the existing queues/checkout-lock lifecycle, with no new periodic suppression polling or second scheduler. Add a failure-injection regression proving enqueue failure is recoverable and does not allow a billable attempt or provider call during active suppression. Document the chosen recovery mechanism.
- **Scope discipline:** Keep immutable attempt-recipient evidence and the accepted ARCH-028-DATABASE-001/003 schema unchanged. Do not implement reachability evidence writes/clearing (BACKGROUND-011), compensation or provider-status mutation, and do not change `docs/**/_index.md`.

### Reviewed Files

- **Attempt 8:** `src/services/checkout-recovery.service.ts`, `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`, `src/services/checkout-recovery/recovery-capacity-resume-admission-gate.ts`, `src/services/checkout-recovery/recovery-initiation.service.ts`, `src/services/checkout-recovery/recovery-capacity-resume-terminalization.ts`, `tests/unit/services/checkout-recovery/recovery-capacity-resume-processor.service.test.ts`, `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`, and the parent task report/ARCH-028 contract. The production constructor adapter, not the processor-injected mock, is the untested failure point.

- **Attempt 7:** `src/domain/recovery-capacity-resume.ts`; `src/services/checkout-recovery/{recovery-capacity-resume-maturity.ts,recovery-capacity-resume-checkout-preparation.ts,recovery-capacity-resume-processor.service.ts,checkout-event-orchestrator.service.ts}`; `src/services/pending-recovery-candidate/checkout-order-guard.service.ts` (lock policy; unchanged); `src/services/checkout-recovery/recovery-initiation.service.ts` and `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts` (actual slow admission path); corresponding domain/processor/orchestrator unit tests.

- **Attempt 6:** `src/services/checkout-recovery/checkout-event-orchestrator.service.ts`; `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`; `src/services/checkout-recovery/recovery-recipient-suppression-admission.service.ts`; `src/workers/pending-recovery-candidate.worker.ts`; associated checkout-update, maturity, and candidate-worker unit regressions; `src/domain/recovery-capacity-resume.ts`, `src/services/recovery-capacity-resume.service.ts`, `src/services/checkout-recovery/recovery-initiation.service.ts`, `src/services/checkout-recovery/recovery-materialization.service.ts`, and checkout lock implementation as relevant integration boundaries; parent task, ARCH-028 architecture and isolation policy.

- **Attempt 5:** `checkout-event-orchestrator.service.ts`, `recovery-capacity-resume-processor.service.ts`, `recovery-recipient-suppression-admission.service.ts`, `recovery-initiation.service.ts`, `recovery-materialization.service.ts`, `recovery-agent-context.service.ts`, `pending-recovery-candidate.worker.ts`, `recovery-capacity-resume.service.ts`, `pending-recovery-candidate.service.ts`, the five relevant changed unit test files, `tests/integration/recovery-outreach-recipient.integration.test.ts`, task and parent ARCH-028 architecture contracts.

- **Attempt 4:** `src/services/checkout-recovery/recovery-capacity-resume-processor.service.ts`, `src/services/pending-recovery-candidate/checkout-order-guard.service.ts`, `src/workers/pending-recovery-candidate.worker.ts`, relevant suppression/materialization/checkout-update admission paths, the three touched unit test files, and the parent ARCH-028/BACKGROUND-010/012 contracts.

- **Attempt 3:** `recovery-materialization.service.ts`, `recovery-initiation.service.ts`, `recovery-recipient-suppression-admission.service.ts`, `recovery-capacity-resume-processor.service.ts`, `checkout-recovery.service.ts`, `pending-recovery-candidate.worker.ts`, `recovery-capacity-resume.worker.ts`, `pending-recovery-candidate.service.ts`, its Redis `candidate-index.store.ts` and `checkout-order-guard.service.ts`.
- **Attempt 3 tests:** worker cross-component tagged retry; suppression-admission scheduling; early targeted wake-up/deferred original write; recipient/no-recipient resume; the two existing disposable PostgreSQL reachability tests.

- `src/services/checkout-recovery/recovery-recipient-suppression-admission.service.ts` and its focused unit tests.
- `src/services/checkout-recovery/recovery-initiation.service.ts`, `recovery-capacity-resume-processor.service.ts`, `recovery-outreach-follow-up-processor.service.ts`, `recovery-materialization.service.ts`, `recovery-recipient-resolver.service.ts`, and `recovery-snapshot-builder.service.ts`.
- `src/services/recovery-capacity-resume.service.ts`, `recovery-outreach-follow-up.service.ts`, associated job-ID domain helpers and recovery workers.
- `tests/integration/recovery-outreach-recipient.integration.test.ts` and task-owned initial/follow-up/resume unit regressions.
- Canonical `ARCH-028-BACKGROUND-010` task contract and `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md` from the uploaded parent snapshot.

### Validation Reviewed

- **Attempt 8:** Independently verified both remote branch tips against `61a40a7c9cd2abceba0a46cfd33c53362e0fefee` (implementation) and `eaf9e0cad60fceb7ad2dfe6b9833397a103c8199` (parent report). Exact Git-blob matching passed for the parent task and all seven changed Background implementation/test files in the uploaded snapshot. Inspected the injected-processor regression (direct five-argument mock) and the initiation-service gate test (direct five-argument call); neither exercises the real four-argument production adapter. Agent-reported PASS: 181 focused unit tests (18 files); 42 targeted tests; two disposable PostgreSQL/Redis integration tests; build, Prisma validation, changed-file diagnostics, `git diff --check`. The architect did **not** rerun these suites, and the full repository suite was not run.

- **Attempt 7 Architect source and validation review:** Verified both remote task-branch commit tips, parent Git blob and relevant uploaded source/test assertions. Independently ran the zero-dependency TypeScript domain helper using Node 22 type stripping: deterministic same-trigger deduplication and distinct child/grandchild job identities passed. Agent-reported 179 focused unit tests across 18 files, two disposable PostgreSQL integration tests, build, Prisma validation, diagnostics and `git diff --check` were **not rerun** here: the uploaded snapshot lacks `node_modules` and pnpm. Full repository suite was not run. A6-R1 and the measured A6-R2 lookup-interleaving test conform on their tested paths; no duration/Redis lease-exhaustion test was supplied.

- **Attempt 6 independent verification:** Submitted implementation SHA `398fbb56a1753e41d56e3ebd93d60bb06e916116` and parent report SHA `676463226864a660c6417439b4bb49d67645b7d5` match remote task branch refs. Parent file and four modified runtime modules in the uploaded snapshot match their remote Git blobs. The source and test assertions were reviewed; the claimed physical worktrees/synchronisation are report evidence, not a direct inspection of the developer machine.
- **Agent-reported Attempt 6 PASS, not independently rerun:** 175 focused unit tests across 17 files, 2 disposable PostgreSQL integration tests, build, Prisma validation, changed-file diagnostics and `git diff --check`. No full repository suite was run. Existing maturity tests cover a newer persisted activity timestamp, not maturity-job self-deduplication after policy extension or an update committed between the resume maturity read and admission.
- **Independent architectural evidence:** `createRecoveryCapacityResumeJobId()` derives only `shopId` and `trigger`; the maturity trigger does not change when policy deadline changes but activity time does not. BullMQ's documented custom-job-ID rule ignores a duplicate ID while a job exists. The checkout-update activity writer does not use the lock used by resume and initiation contains no later maturity gate.

- **Attempt 5 remote and snapshot verification:** Background `6c3fd349bd7a1832c9988e6f619d37bdf224a221` and parent `f0255ccd96df492a93629ad3ec970bd9e9e09ffb` match remote task-branch tips. Uploaded task blob SHA `82f255d196dc86b8190df68cd4457b09fb410560` and changed runtime-file SHA values match remote Git. Database pin and physical task worktree/synchronisation evidence are recorded in the agent's Attempt 5 Completion Report; developer workstation Git worktree cleanliness/isolation was not independently inspected from the ZIP (no `.git` metadata).
- **Agent-reported Attempt 5 PASS:** 174 focused unit tests across 17 files, 2 disposable PostgreSQL integration cases, build, Prisma validation, changed-file diagnostics and `git diff --check`. The Architect inspected code and selected assertions but did **not** rerun these suites here because the uploaded snapshot lacks installed dependencies and pnpm; the complete repository suite was not run and cannot be claimed to pass.
- **Uncovered regressions:** The new checkout-update unit test asserts job scheduling but not continued durable price/line-item refresh or last-activity maturity. The cross-component late-write test uses mocked attempt/charge/send counters; it does not exercise delayed checkout-activity admission or the new pre-enqueue version-read failure/retry.

- **Attempt 4 remote verification:** implementation SHA `03fd86794694a0231b390fa6f9d87c45918b005b` and parent SHA `08f3a565c27aaa5801a283b829303d8d7adf9c67` both match their remote task branch refs. Parent task file blob matches uploaded snapshot (`49c334b982497ee56b97fd440643be62ac37f805`). Local snapshot has no `.git` directory, so developer-machine worktree cleanliness/isolation is report evidence, not independently inspected.
- **Agent-reported Attempt 4 PASS:** 184 focused unit tests across 15 files; two disposable PostgreSQL integration cases; build, Prisma validation, changed-file diagnostics and `git diff --check`. The Architect inspected the actual changes and test assertions but did not rerun the suites here. The full repository suite was not run and is not claimed to pass.
- **Residual proof gap:** the new no-recipient deferred-write test asserts `CANCELLED` but does not validate a later usable recipient or re-entry for the still-open checkout; existing event/materialization paths explicitly reject that state.

- **Attempt 3 remote/source verification:** parent report `c244cebc39374aea4806abce10e2aa696e8851d2`; implementation `b9860933581cc2f4998b950a348a9f031f745c2c`; task status `review`, `attempt: 3`, claim cleared; accepted Database pin `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. The uploaded task document is Git blob `2e1295943131e60d66daede58ef9cc013a96dd69`, matching the remote task document exactly.
- **Agent-reported PASS:** 178 focused unit tests across 14 files, two disposable PostgreSQL integration tests, `pnpm run build`, Prisma validation, changed-file diagnostics and `git diff --check`. I inspected code/test assertions but did **not** rerun those suites in this review container. The repository-wide suite was not run and must not be represented as passing.
- **Remaining evidence gaps:** the deferred-write test initiates with an available recipient and active suppression, so it does not cover absent recipient or terminal-checkout overtaking. The tagged candidate-worker retry test mocks Redis lock/index cleanup as successful; it cannot establish that a simultaneous queue/cleanup failure preserves the error marker needed on retry.

- **Attempt 2 review (2026-10-11):** Verified remote implementation `43d14e7355f2027958ccb982b484017b14fce825` and parent report `7eca3cce45ccf7463b2a73c543f6b7ac98a76020`; the uploaded task document matches its GitHub blob. Exact approved Database gitlink is `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. Task branch compared with Background main was ahead three commits and not behind at review time.
- **Agent-reported Attempt 2 PASS:** 173 focused unit tests across 13 files, 2 disposable PostgreSQL integration tests, `pnpm run build`, Prisma validation, focused diagnostics and `git diff --check`. These suites were not rerun by the Architect. An accidentally mis-invoked broader wrapper run reported unrelated failures; do not count it as a passing complete repository suite.
- **Evidence gap:** the service-level scheduling-failure test verifies no immediate suppressed block write, but does not execute the persisted DETECTED/materialisation-worker/no-op retry chain. No test proves the delayed job cannot run before a slow DB block update. Both liveness paths are required before acceptance; success of the 173 existing unit cases does not establish them.

- Verified pushed Background implementation `97ca7703acfe8e9ca1c86e8c61e60a637935738a` and parent report `e5ee5c1b5926aa76b813f5697500e392c21eba0c` as the exact remote task refs; the uploaded task document matches the GitHub blob SHA.
- Agent-reported PASS: 161 focused unit tests across 16 files; 2 disposable PostgreSQL tests; build, Prisma validation, focused diagnostics and `git diff --check`. Those commands were **not rerun** by the architect in this review. A repository-wide suite was not claimed.
- The PostgreSQL tests establish exact Shop/recipient suppression lookup, another-Shop isolation, changed recipient and expiry boundary. They do **not** execute the production suppression-expiry job through canonical CustomerPhone resolution or test BullMQ enqueue failure after the persisted DETECTED block. The new requested regressions are required before acceptance.
- Background task branch is one implementation commit ahead of its common baseline and currently behind newer `main` changes in WhatsApp provider-status handling. Those intervening changes do not overlap the task's touched recovery-admission files; final integration remains developer-owned.

### Architecture Conformance

- **Attempt 8:** Bounded checkout lock scope and the targeted in-lock maturity decision conform when `admissionGate.check` is actually called; however the production service constructor drops that callback, so the final recovery activity check is never enforced on the real resume path. This is a local Background wiring and test-coverage regression, not a need for another architectural mechanism, migration or additional task. Until A8-R1 is corrected, suppression-expiry re-entry remains capable of premature attempt/billing/provider admission.

- **Attempt 7:** A6-R1 maturity successor collision and A6-R2's tested lookup/activity interleaving are resolved without cross-service changes. The new `recordExternalActivity()` dependency on the existing ten-second Redis lease, combined with initiation holding that lease for potentially slow external provider work, does not yet establish reliable activity persistence or a fenced admission decision under long-running work. A7-R1 is a bounded Background concurrency/liveness correction; no new architecture ID or infrastructure is justified.

- **Attempt 6:** A5-R1 checkout snapshot freshness and A5-R3 tagged pre-enqueue retry conform. A5-R2's scheduled due time and locked persisted-activity recheck are directionally correct, but its maturity-successor identity is not live under policy extension, and its admission check is not ordered against a concurrent checkout activity write. These A6-R1/A6-R2 defects violate bounded eventual re-entry and inactivity-before-admission, respectively. They are narrow Background implementation issues and do not require schema, new infrastructure or cross-service contract work.

- **Attempt 5:** The bounded suppression-version CAS, recoverable missing-recipient state, targeted same-recovery wake-up and unchanged terminal-checkout handling conform to A4-R1. The new unconditional DETECTED checkout-update branch does **not** conform to the ARCH-028 current-recovery-refresh boundary or the established inactivity-before-recovery policy; the additional pre-enqueue version read also opens a tagged-retry liveness gap. The implementation remains within Background ownership and does not justify new schema/infrastructure tasks; it requires bounded A5-R1/R2/R3 corrections inside the existing task.

- **Attempt 4:** Retains exact Shop-scoped suppression and zero-billing/provider admission. Redis enqueue+cleanup failure retry and actual-terminal wake-up interleavings conform. Still not conformant for missing-current-recipient overtaking: converting a recoverable open checkout to `CANCELLED` prevents future recipient eligibility under existing checkout update and materialization flows. No schema, new queue or cross-repository implementation task is justified.

- **Attempt 3:** Canonical Shop-scoped recipient admission, suppression-before-billing, tagged normal retry and deterministic child scheduling conform on the tested paths. Full expiry liveness is not yet proven across the no-recipient/terminal early-wake-up branches or simultaneous Redis scheduling/cleanup failures. These are bounded implementation-level safety/liveness issues; no new migration or reachability-writer task is justified.

- **Attempt 2:** Canonical recipient and zero-billing admission safeguards now conform. Suppression wake-up liveness remains nonconformant under queue-add rejection after durable creation and when expiry job consumption overtakes persistence. Both are sequencing concerns within BACKGROUND-010, not grounds for a new database task or for introducing reachability writes.

- The read-only exact `(shopId, recipient)` lookup, active suppression zero-billing behaviour, no periodic suppression scan, and use of existing delayed queues conform to the intended ARCH-028 boundaries.
- **Not fully conformant until A1-R1/A1-R2 are corrected:** expiry re-entry must use the current canonical recipient instead of a checkout phone fallback, and finite suppression must retain a recoverable expiry path if its queue publish fails.

### Follow-up

- **Current Attempt 8 decision:** Apply this review-only patch to the parent `task/ARCH-028-BACKGROUND-010` worktree, commit/push it, and reclaim the SAME task through `/moda-task ARCH-028-BACKGROUND-010` for **Attempt 9**. Correct A8-R1 only; include a connected service-composition regression that proves the actual `CheckoutRecoveryService` forwards and enforces the gate. Preserve all previous code fixes, reports and Architect Review history. Return in `review` after focused validation. `ARCH-028-BACKGROUND-011` remains `pending`; no `_index.md` reconciliation is authorised.
- **Historical note:** All prior Attempt 1–7 follow-up labels are archival and do not supersede the Attempt 8 correction contract above.

- **Current Attempt 7 decision:** Apply this Architect review on the parent `task/ARCH-028-BACKGROUND-010` worktree, commit and push it, and reclaim the SAME task through `/moda-task ARCH-028-BACKGROUND-010` for **Attempt 8**. Correct A7-R1 only, retain the resolved Attempt 7 code and all historical Completion Reports/Architect Reviews, then return at `status: review` with the required focused validation. `ARCH-028-BACKGROUND-011` remains Pending. Do not reconcile `_index.md` documents until the user explicitly authorises it.
- **Historical note:** Previous Attempt 1–6 follow-up instructions are archival and do not supersede this Attempt 7 correction contract.

- **Current Attempt 6 decision:** Apply this parent Architect review on `task/ARCH-028-BACKGROUND-010`, commit/push, and reclaim the SAME task with `/moda-task ARCH-028-BACKGROUND-010` for **Attempt 7**. Correct A6-R1/A6-R2 only and preserve earlier reports, accepted implementation and review history. Return at `status: review` after required evidence. `ARCH-028-BACKGROUND-011` remains Pending; no `_index.md` reconciliation until the user explicitly authorises it.
- **Historical note:** All earlier Attempt 1–5 follow-up instructions below are archival and do not supersede the Attempt 6 correction contract above.

- **Current Attempt 5 decision:** Apply this Architect review in the parent `task/ARCH-028-BACKGROUND-010` worktree, commit/push, and reclaim the SAME task with `/moda-task ARCH-028-BACKGROUND-010` for **Attempt 6**. Implement A5-R1/R2/R3 only, with focused proof; preserve all historical reports/reviews and the accepted A4-R1/A3-R2 work. Return to `status: review` after required validation. Leave `ARCH-028-BACKGROUND-011` Pending until BACKGROUND-010 is architect-accepted Complete.

- **Current Attempt 4 decision:** Apply this Architect review on the parent `task/ARCH-028-BACKGROUND-010` branch, commit/push, and reclaim the SAME task through `/moda-task ARCH-028-BACKGROUND-010` for Attempt 5. Correct A4-R1 only; retain A3-R2 and terminal-checkout fixes, all earlier reports and Architect Review history. Return `status: review` after bounded re-entry and deferred-write proof. Leave `ARCH-028-BACKGROUND-011` Pending.
- **Earlier Attempt 3/2/1 follow-ups below are historical; only the current Attempt 4 correction is executable.**

- **Current Attempt 3 decision:** Apply this Architect review on the parent `task/ARCH-028-BACKGROUND-010` branch, commit/push, and use `/moda-task ARCH-028-BACKGROUND-010` to claim Attempt 4. Correct A3-R1/A3-R2 with bounded cross-component tests, preserving the existing admission/recipient/refund/compensation boundaries and the historical report/review. Return `status: review` only after task-owned proof. BACKGROUND-011 remains Pending.
- **Historical follow-up instructions:** The previous Attempt 2 and Attempt 1 directions below are archival; they are not the instructions for the next claim.

- **Current Attempt 2 decision:** Apply this review to the parent `task/ARCH-028-BACKGROUND-010` branch, commit/push, and reclaim the SAME task through `/moda-task ARCH-028-BACKGROUND-010` for **Attempt 3**. Correct A2-R1/A2-R2 only; preserve A1-R1, earlier reports and historical decisions. Submit new cross-component failure/re-entry tests and evidence, then return at `status: review`. `ARCH-028-BACKGROUND-011` remains Pending.
- **Historical note:** the older Attempt 1 follow-up bullets below are retained verbatim as audit history and do not direct the next claim.

- Commit/push this architect review on the parent `task/ARCH-028-BACKGROUND-010` branch. Reinvoke the same task through `/moda-task ARCH-028-BACKGROUND-010`; the launcher should claim **Attempt 2**. Keep the Attempt 1 Completion Report and review historical evidence intact when updating the report with the two focused corrections.
- Re-run focused unit, integration/PostgreSQL as appropriate, build, Prisma validation, diagnostics and `git diff --check`; record executed evidence and exact task SHAs. Return at `status: review` for architect reassessment.
- `ARCH-028-BACKGROUND-011` remains Pending until BACKGROUND-010 is architect-accepted Complete; no dependent task is promoted by this changes-requested review.
