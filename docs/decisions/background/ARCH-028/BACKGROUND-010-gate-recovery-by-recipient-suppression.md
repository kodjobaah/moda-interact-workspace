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
status: review
priority: 53
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-028-DATABASE-001
  - ARCH-028-BACKGROUND-005
enables:
  - ARCH-028-BACKGROUND-011
created: 2026-10-08
updated: 2026-10-11
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

Ready for Architect review (Attempt 3, 2026-10-11). Attempt 1/2 reports and the complete Changes Requested Architect Review below are retained as historical evidence.

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

## Architect Review

### Review Status

Changes Requested — Attempt 2 (2026-10-11). A1-R1 is resolved; A1-R2 remains open because queue-publish failure and schedule/write races can still strand a materialised DETECTED recovery. Return the SAME task to `ready` with `attempt: 2` preserved and claim cleared. `ARCH-028-BACKGROUND-011` remains Pending; no implementation acceptance is claimed.

### Review Notes

#### Attempt 2 — current architect correction contract (2026-10-11)

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

- `src/services/checkout-recovery/recovery-recipient-suppression-admission.service.ts` and its focused unit tests.
- `src/services/checkout-recovery/recovery-initiation.service.ts`, `recovery-capacity-resume-processor.service.ts`, `recovery-outreach-follow-up-processor.service.ts`, `recovery-materialization.service.ts`, `recovery-recipient-resolver.service.ts`, and `recovery-snapshot-builder.service.ts`.
- `src/services/recovery-capacity-resume.service.ts`, `recovery-outreach-follow-up.service.ts`, associated job-ID domain helpers and recovery workers.
- `tests/integration/recovery-outreach-recipient.integration.test.ts` and task-owned initial/follow-up/resume unit regressions.
- Canonical `ARCH-028-BACKGROUND-010` task contract and `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md` from the uploaded parent snapshot.

### Validation Reviewed

- **Attempt 2 review (2026-10-11):** Verified remote implementation `43d14e7355f2027958ccb982b484017b14fce825` and parent report `7eca3cce45ccf7463b2a73c543f6b7ac98a76020`; the uploaded task document matches its GitHub blob. Exact approved Database gitlink is `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. Task branch compared with Background main was ahead three commits and not behind at review time.
- **Agent-reported Attempt 2 PASS:** 173 focused unit tests across 13 files, 2 disposable PostgreSQL integration tests, `pnpm run build`, Prisma validation, focused diagnostics and `git diff --check`. These suites were not rerun by the Architect. An accidentally mis-invoked broader wrapper run reported unrelated failures; do not count it as a passing complete repository suite.
- **Evidence gap:** the service-level scheduling-failure test verifies no immediate suppressed block write, but does not execute the persisted DETECTED/materialisation-worker/no-op retry chain. No test proves the delayed job cannot run before a slow DB block update. Both liveness paths are required before acceptance; success of the 173 existing unit cases does not establish them.

- Verified pushed Background implementation `97ca7703acfe8e9ca1c86e8c61e60a637935738a` and parent report `e5ee5c1b5926aa76b813f5697500e392c21eba0c` as the exact remote task refs; the uploaded task document matches the GitHub blob SHA.
- Agent-reported PASS: 161 focused unit tests across 16 files; 2 disposable PostgreSQL tests; build, Prisma validation, focused diagnostics and `git diff --check`. Those commands were **not rerun** by the architect in this review. A repository-wide suite was not claimed.
- The PostgreSQL tests establish exact Shop/recipient suppression lookup, another-Shop isolation, changed recipient and expiry boundary. They do **not** execute the production suppression-expiry job through canonical CustomerPhone resolution or test BullMQ enqueue failure after the persisted DETECTED block. The new requested regressions are required before acceptance.
- Background task branch is one implementation commit ahead of its common baseline and currently behind newer `main` changes in WhatsApp provider-status handling. Those intervening changes do not overlap the task's touched recovery-admission files; final integration remains developer-owned.

### Architecture Conformance

- **Attempt 2:** Canonical recipient and zero-billing admission safeguards now conform. Suppression wake-up liveness remains nonconformant under queue-add rejection after durable creation and when expiry job consumption overtakes persistence. Both are sequencing concerns within BACKGROUND-010, not grounds for a new database task or for introducing reachability writes.

- The read-only exact `(shopId, recipient)` lookup, active suppression zero-billing behaviour, no periodic suppression scan, and use of existing delayed queues conform to the intended ARCH-028 boundaries.
- **Not fully conformant until A1-R1/A1-R2 are corrected:** expiry re-entry must use the current canonical recipient instead of a checkout phone fallback, and finite suppression must retain a recoverable expiry path if its queue publish fails.

### Follow-up

- **Current Attempt 2 decision:** Apply this review to the parent `task/ARCH-028-BACKGROUND-010` branch, commit/push, and reclaim the SAME task through `/moda-task ARCH-028-BACKGROUND-010` for **Attempt 3**. Correct A2-R1/A2-R2 only; preserve A1-R1, earlier reports and historical decisions. Submit new cross-component failure/re-entry tests and evidence, then return at `status: review`. `ARCH-028-BACKGROUND-011` remains Pending.
- **Historical note:** the older Attempt 1 follow-up bullets below are retained verbatim as audit history and do not direct the next claim.

- Commit/push this architect review on the parent `task/ARCH-028-BACKGROUND-010` branch. Reinvoke the same task through `/moda-task ARCH-028-BACKGROUND-010`; the launcher should claim **Attempt 2**. Keep the Attempt 1 Completion Report and review historical evidence intact when updating the report with the two focused corrections.
- Re-run focused unit, integration/PostgreSQL as appropriate, build, Prisma validation, diagnostics and `git diff --check`; record executed evidence and exact task SHAs. Return at `status: review` for architect reassessment.
- `ARCH-028-BACKGROUND-011` remains Pending until BACKGROUND-010 is architect-accepted Complete; no dependent task is promoted by this changes-requested review.
