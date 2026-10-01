---
id: ARCH-025-SHOPIFY-007
architecture_id: ARCH-025
title: Extract hosted plan-change verification workflow
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 70
executor: copilot
claimed_at: 2026-10-01T23:36:30Z
attempt: 1
depends_on:
  - ARCH-025-SHOPIFY-006
enables:
  - ARCH-025-SHOPIFY-008
created: 2026-10-01
updated: 2026-10-02
---

# Extract hosted plan-change verification workflow

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract hosted billing-return verification fencing and retry-state updates into `HostedPlanChangeService` while preserving the exact pre-provider/post-provider durable fence semantics.

## Context

The callback workflow has its own concurrency contract and regression coverage. It should be independently reviewable rather than remain mixed with subscription reads/sync.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/hosted-plan-change.service.ts              # new
tests/unit/services/billing/hosted-plan-change.service.test.ts  # new
```

No callback route edits are authorised. Consume `subscription-locks.ts` and `billing-retry-policy.ts` created by SHOPIFY-006 without modifying their semantics.

## Out of Scope

- provider subscription read/mapping service.
- activation.
- plan-change business redesign.
- changing retry delay/error code.
- edits to frozen `billing.service.test.ts`.

## Requirements

### Common ARCH-025 invariants

- Preserve `BillingService` constructor compatibility: `new BillingService(provider, database, dispatchTranslation)`.
- Preserve every existing public `BillingService` method signature and the `billingService` singleton export.
- Preserve all current public exports from `app/services/billing/billing.service.ts`; moved symbols must be compatibility re-exported from that file.
- Do not change routes/callers as part of extraction.
- Extracted modules MUST NOT import `billing.service.ts`; dependency direction is façade/coordinator -> collaborator.
- Do not change billing rules, error codes/strings, transaction boundaries, lock order, provider call order, retry semantics, idempotency, CAS/fencing, entitlement arithmetic or durable lifecycle state.
- Do not add provider/API calls or database round trips to the equivalent path solely because code moved.
- Extracted collaborator constructors must be side-effect-free: store/wire dependencies only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during `new BillingService(...)`; the frozen suite constructs the façade with many partial test doubles.
- This is move-only refactoring: do not remove, coalesce, reorder or otherwise optimise away an existing provider/database read, write, lock or transaction as an incidental cleanup. Any intentional I/O change is outside this task.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The proven pre-task failure set is `ARCH025-TEST-001`; the task must introduce no additional failing identifier.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — move exact hosted workflow

Move implementation ownership for:

```text
getHostedPlanVerificationFence
recordHostedPlanChangeReturn
recordHostedPlanVerificationFailure
sameHostedPlanVerificationFence / sameFenceDate
```

and the exact locked/reread state required by these methods. The lock SQL itself remains owned by SHOPIFY-006 `subscription-locks.ts`.

### R2 — preserve compatibility exports

`HostedPlanChangeReturnResult` and `HostedPlanVerificationFence` remain exported from `billing.service.ts` with compatible shapes.

### R3 — preserve fence semantics

The durable state captured before provider verification must be compared against the locked/reread state before commit. Any changed protected fact must fence the write even when wall-clock `updatedAt` is equal/older.

### R4 — preserve failure semantics

Provider verification failure updates only existing retry metadata under the same unchanged fence, uses the same `PARTNER_API_ERROR` semantics, and does not manufacture Subscription state when none exists.

### R5 — preserve lock order through the shared lock owner

Reuse SHOPIFY-006 `lockInitialFreeActivationState` from `subscription-locks.ts`. Keep the current accepted settings/subscription locking order and transaction boundaries exactly; do not copy the lock SQL into this service.

### R6 — preserve shared retry policy

`recordHostedPlanVerificationFailure` must use SHOPIFY-006 `INITIAL_BILLING_RETRY_DELAY_MS` from `billing-retry-policy.ts`. Do not introduce a second `60_000` literal or change the callback route's compatibility import.

## Work Items

- [x] Create `HostedPlanChangeService` and move fence/result types/helpers/method bodies while consuming the shared lock/retry modules from SHOPIFY-006.
- [x] Re-export public types through `billing.service.ts`.
- [x] Leave façade public methods as delegates.
- [x] Add focused tests for null fence, current/pending/mismatch/no-active, changed-fence no-op, identical-updatedAt changed-content fence, failure retry and lock order.
- [x] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Repository-internal service. It consumes the shared subscription lock and retry policy created by SHOPIFY-006. Existing callback route continues calling `billingService` only; no new route contract.

## Dependencies

- `ARCH-025-SHOPIFY-006`

## Enables

- `ARCH-025-SHOPIFY-008`

## Acceptance Criteria

- [x] Hosted verification has one owner outside the façade.
- [x] Fence comparison protects the same complete durable projection.
- [x] Retry/error behaviour and lock order are unchanged, with no duplicated lock SQL or retry literal.
- [x] Callback route is untouched.
- [x] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [x] `npm run prisma:generate` passed.
- [x] Frozen test hash is `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; `git diff -- tests/unit/services/billing.service.test.ts` is empty.
- [x] Frozen façade suite: 195 passed, 18 failed; all 18 identifiers match `ARCH025-TEST-001`.
- [x] Focused hosted-plan-change suite: 8 passed.
- [x] Full `npm test`: 991 passed, 24 failed, 33 skipped across 93 files; all 24 identifiers match `ARCH025-TEST-001`.
- [x] `npm run typecheck` passed.
- [x] Task-scoped ESLint passed (existing TypeScript parser compatibility warning only).
- [x] `npm run build` passed (existing large-chunk warning).
- [x] `git diff --check` passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

This extraction is structural. Do not simplify the fence by comparing fewer fields or by replacing explicit durable-state fencing with timestamps alone.


## Completion Report

### Status

Review

### Files Changed

Implementation repository (`moda-interact`):

- `app/services/billing/billing.service.ts`
- `app/services/billing/hosted-plan-change.service.ts` (new)
- `tests/unit/services/billing/hosted-plan-change.service.test.ts` (new)

Parent workspace: this task report only.

### Work Completed

- Moved hosted verification fence capture, locked return reconciliation, retry-state recording, complete durable-fence comparison, and compatibility types into `HostedPlanChangeService`; the `BillingService` methods preserve their signatures and delegate.
- Kept the callback route unchanged and reused SHOPIFY-006's lock and retry-policy modules without modifying them.
- Added eight focused tests for fence capture, current/pending/mismatch classification, absent no-active state, identical-timestamp changed-content fencing, guarded provider-error retry, and shared lock order.
- Preserved all 18 frozen façade failures as the existing `ARCH025-TEST-001` baseline; the frozen test file remains byte-identical.

### Validation Results

Passed: Prisma generation, focused hosted-plan-change suite (8/8), typecheck, task-scoped ESLint, production build, frozen test hash/diff verification, and `git diff --check`.

The frozen façade suite ran 213 tests: 195 passed and 18 failed. All 18 failing identifiers match `ARCH025-TEST-001`. The final full suite ran 1,048 tests across 93 files: 991 passed, 24 failed, and 33 skipped. The 24 failing identifiers match the documented 18 frozen plus six unrelated full-suite baseline failures. One initial full-suite run also timed out in an unrelated observability test; that test passed in isolation (2/2), and the final full-suite rerun returned to the 24-failure baseline.

ESLint emitted the existing TypeScript parser compatibility warning; build emitted the existing large-chunk warning. Neither command failed.

### Deviations

The first full-suite run had a transient 5-second timeout in an unrelated observability test. The isolated test passed and a full-suite retry completed with exactly the documented baseline failures.

### Assumptions

None.

### Unresolved Issues

None task-introduced. The unchanged `ARCH025-TEST-001` baseline failures remain documented.

### Architectural Concerns

None identified. Hosted workflow ownership is outside the façade; the durable fence projection, shared lock order, retry delay, retry error semantics, and callback imports remain unchanged.

### Launcher and VCS Evidence

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-007
parent branch: task/ARCH-025-SHOPIFY-007
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-007
implementation branch: task/ARCH-025-SHOPIFY-007
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recorded database submodule commit: cfeeb12456b4e05067a96857a8c47837d7e33bbd
launcher claim commit: 4600adcb3c5fcd334387c7b107c8ccb0e2f24d6d
implementation commit: a72bd153f3cafd0e8301d64172421cfe066b801b (pushed to origin/task/ARCH-025-SHOPIFY-007)
```

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
