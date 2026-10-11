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
status: in_progress
priority: 53
executor: copilot
claimed_at: 2026-10-11T16:18:53Z
attempt: 2
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

Ready for Architect review (Attempt 1, 2026-10-11).

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

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-11). Return the same task to `ready` with `attempt: 1` preserved, claim cleared, and `ARCH-028-BACKGROUND-011` still Pending. No architect acceptance of the implementation is claimed.

### Review Notes

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

- Verified pushed Background implementation `97ca7703acfe8e9ca1c86e8c61e60a637935738a` and parent report `e5ee5c1b5926aa76b813f5697500e392c21eba0c` as the exact remote task refs; the uploaded task document matches the GitHub blob SHA.
- Agent-reported PASS: 161 focused unit tests across 16 files; 2 disposable PostgreSQL tests; build, Prisma validation, focused diagnostics and `git diff --check`. Those commands were **not rerun** by the architect in this review. A repository-wide suite was not claimed.
- The PostgreSQL tests establish exact Shop/recipient suppression lookup, another-Shop isolation, changed recipient and expiry boundary. They do **not** execute the production suppression-expiry job through canonical CustomerPhone resolution or test BullMQ enqueue failure after the persisted DETECTED block. The new requested regressions are required before acceptance.
- Background task branch is one implementation commit ahead of its common baseline and currently behind newer `main` changes in WhatsApp provider-status handling. Those intervening changes do not overlap the task's touched recovery-admission files; final integration remains developer-owned.

### Architecture Conformance

- The read-only exact `(shopId, recipient)` lookup, active suppression zero-billing behaviour, no periodic suppression scan, and use of existing delayed queues conform to the intended ARCH-028 boundaries.
- **Not fully conformant until A1-R1/A1-R2 are corrected:** expiry re-entry must use the current canonical recipient instead of a checkout phone fallback, and finite suppression must retain a recoverable expiry path if its queue publish fails.

### Follow-up

- Commit/push this architect review on the parent `task/ARCH-028-BACKGROUND-010` branch. Reinvoke the same task through `/moda-task ARCH-028-BACKGROUND-010`; the launcher should claim **Attempt 2**. Keep the Attempt 1 Completion Report and review historical evidence intact when updating the report with the two focused corrections.
- Re-run focused unit, integration/PostgreSQL as appropriate, build, Prisma validation, diagnostics and `git diff --check`; record executed evidence and exact task SHAs. Return at `status: review` for architect reassessment.
- `ARCH-028-BACKGROUND-011` remains Pending until BACKGROUND-010 is architect-accepted Complete; no dependent task is promoted by this changes-requested review.
