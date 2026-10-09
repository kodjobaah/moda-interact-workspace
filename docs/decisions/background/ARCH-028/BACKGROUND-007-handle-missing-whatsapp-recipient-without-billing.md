---
id: ARCH-028-BACKGROUND-007
architecture_id: ARCH-028
title: Require current WhatsApp recipient before recovery materialisation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 25
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-028-BACKGROUND-005
  - ARCH-028-BACKGROUND-012
created: 2026-10-07
updated: 2026-10-09
---

# Require current WhatsApp recipient before recovery materialisation

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Require a canonical, Shop-scoped current `CustomerPhone` before materialising a `CheckoutRecovery`; when the number is missing, finish the candidate with no recovery, billing or Meta work. Ensure the resolved recipient passed to the initial send is the same one that passed this prerequisite. Checkout-update re-entry is a separate task (BACKGROUND-012).

## Context

The current recovery initiator creates `CheckoutRecovery` before recipient resolution and then throws when no customer phone/test recipient exists. `PendingRecoveryCandidate` already represents a checkout that may later become recoverable, so a missing phone should stop materialisation before a durable recovery exists. No DATABASE-003 required-recipient field, provider status or compensation contract is needed for this prerequisite.

The fresh abandoned-checkout lookup may contain a phone that Customer resolution persists through `CustomerPhoneService`; otherwise an already-current Shop-scoped `CustomerPhone` may still exist. Only the absence of an active usable `CustomerPhone` after that resolution is a true missing-recipient outcome. `Customer.phone` is not authoritative.

## Scope

- At matured-candidate materialisation, use the fresh abandoned-checkout snapshot to resolve/update the Shop-scoped Customer and `CustomerPhone` history before deciding recipient availability.
- If no active usable current `CustomerPhone` exists, return a bounded `no-recipient`/deferred outcome **without creating `CheckoutRecovery`**, `RecoveryOutreachAttempt`, UsageReservation/UsageEvent, outbound message or provider call.
- Preserve the normal matured-candidate cleanup; do not keep a fake blocked recovery solely as a waiting record.
- Pass the same canonical digits-only `CustomerPhone` recipient into the initial recovery-send path; it must not silently fall back to stale `Customer.phone`, checkout customer fields or a non-test WhatsApp recipient override.
- If a current `CustomerPhone` exists even when `Customer.phone` is null/stale, treat the recipient as present and continue with the existing admission path. BACKGROUND-005 will separately enforce durable per-attempt recipient snapshots once DATABASE-003 is integrated.
- Do not add aggressive polling solely for missing phone.

## Out of Scope

- Later `CHECKOUTS_UPDATE` re-entry, its Shared/Shopify producer/Background consumer contracts (BACKGROUND-012, SHARED-003/004, SHOPIFY-001).
- Recipient suppression TTL and mandatory attempt-recipient schema adoption.
- Provider error classification.
- Synchronous failure.
- Merchant notification.

## Requirements

- [x] Missing recipient is zero billing and zero provider work.
- [x] It is not persisted as a permanent Customer property.
- [x] A later usable phone is eligible when another valid candidate is evaluated; this task does not manufacture a retry event.
- [x] Test-only recipient behaviour remains explicitly development/test scoped and must not become production identity state.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Move the missing-recipient decision to the pending-candidate materialisation boundary before `CheckoutRecovery` creation.
- [x] Resolve/update Customer + current `CustomerPhone` from the fresh checkout snapshot and use current `CustomerPhone` as the authoritative source.
- [x] Return a bounded deferred/no-recipient result without recovery/attempt/billing/provider state.
- [x] Ensure initial provider send receives exactly the canonical recipient validated at materialisation, not a stale original webhook/customer field.
- [x] Ensure a null/stale `Customer.phone` does not block when an active `CustomerPhone` exists.
- [x] Add focused tests.
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes existing Customer/CustomerPhone resolution and pending-candidate materialisation services. Provides a bounded canonical recipient prerequisite for BACKGROUND-005 and BACKGROUND-012. No new database enum/state or required attempt-recipient field is introduced here.

## Dependencies

None.

## Enables

- `ARCH-028-BACKGROUND-005`
- `ARCH-028-BACKGROUND-012`

## Acceptance Criteria

- [x] Missing recipient produces no `CheckoutRecovery`, outreach attempt, billing reservation, outbound UsageEvent/message or Meta call.
- [x] Existing current `CustomerPhone` is honored even when `Customer.phone` is null/stale.
- [x] The exact validated current `CustomerPhone` recipient is supplied to the initial Meta send; production cannot silently substitute `TEST_WHATSAPP_RECIPIENT` or a stale snapshot.
- [x] Duplicate candidate execution remains idempotent and current non-missing recipients retain existing recovery behaviour.
- [x] No polling loop or durable no-recipient recovery block is introduced.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused recovery-initiation tests, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not conflate missing recipient with `WHATSAPP_RECIPIENT_SUPPRESSED`. Suppression is a durable policy block on a known recipient and may remain on a materialised recovery; missing recipient means there is no executable recovery yet.

Prefer a bounded candidate-materialisation recipient prerequisite and reuse existing Customer/CustomerPhone services. Keep `recovery-initiation.service.ts` thin; the separate BACKGROUND-012 task handles checkout-update re-entry after the Shared contract and producer/consumer rollout are defined.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation repository:

- `src/services/checkout-recovery/recovery-recipient-resolver.service.ts`
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery.service.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`

Parent task record: this task file only.

### Work Completed

- Added a focused `RecoveryRecipientResolverService` that resolves/updates the Customer from the fresh abandoned-checkout seed, reads that Customer's active Shop-scoped `CustomerPhone`, and returns its digits-only number or `null`.
- The matured-candidate materialisation path now resolves the recipient before initiation. Missing/empty current phone returns `deferred-no-recipient` before creating a CheckoutRecovery, outreach attempt, billing admission/reservation, outbound message or provider call.
- Passed the exact resolved recipient through recovery initiation to the outbound send. A checkout snapshot's phone and `Customer.phone` are not fallback identities for this path.
- Restricted the legacy `TEST_WHATSAPP_RECIPIENT` override to explicit `development` or `test` `NODE_ENV` values; production cannot use it.
- Candidate index cleanup remains in the worker's existing `finally` path for the new deferred result. No polling or durable no-recipient recovery state was added.
- Added focused regressions for no-recipient side-effect absence, current CustomerPhone precedence when snapshot/Customer phone is absent or stale, digits-only send recipient, bounded materialisation outcome, and production rejection of the test override.
- Production source sizes: new resolver 17 lines; recovery materialisation 134; recovery initiation 253; checkout recovery composition 206. No new production module exceeds 300 lines; the new resolver is below the 200-line target.

### Validation Results

- `npm ci`: passed; installed 496 packages. npm reported 9 audit findings (3 moderate, 6 high) and install-script approval notices; package manifests/lockfiles were not changed.
- Focused materialisation and initiation suites: 55 tests passed across `matured-candidate.materialization.test.ts`, `recovery-materialization.service.test.ts` and `recovery-initiation.service.test.ts`.
- `npm exec -- vitest run tests/unit/runtime/observability-startup.test.ts`: 10 passed when run in isolation.
- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `git diff --check`: passed. Editor diagnostics reported no errors in the changed production modules/tests.
- Full `npm test`: 1,922 passed, 40 skipped, 9 failed. Four translation-enum PostgreSQL integration cases could not connect to `localhost:5432`; three unrelated voice-workflow integration cases failed because their worker test jobs have undefined `job.opts`; two observability-startup cases timed out under the full-suite load, although that file's 10 tests passed in isolation.
- `npm run test:unit`: 1,873 passed, 40 skipped, 4 failed; all four failures were 5-second timeouts in the unchanged `observability-startup.test.ts`. That file passed when run alone. These failures are outside the task's changed files; no shared PostgreSQL service was started or modified.

### Deviations

The repository-wide unit/full suite could not be made entirely green within this bounded task: its existing observability startup tests time out under suite load, its translation-enum integration tests require an unavailable local PostgreSQL at `localhost:5432`, and its voice-workflow integration fixtures omit `job.opts`. The focused recovery tests and production build pass; unrelated tests/files were not changed.

### Assumptions

- `CustomerService.resolveCustomer` remains the authoritative Shop-scoped identity resolver for a fresh abandoned-checkout snapshot; `CustomerPhoneService.getCurrentPhone` returns only the active phone for that resolved Customer.
- Stripping all non-digits from the active `CustomerPhone.phone` is the required canonical outbound recipient representation.

### Unresolved Issues

Repository-wide test failures described above remain for their owning integration/test-fixture surfaces; no task-local validation failure remains in the focused recipient/materialisation suites or build.

### Architectural Concerns

None within this task's bounded missing-recipient prerequisite. Durable per-attempt recipient snapshots and checkout-update re-entry remain with their separately assigned ARCH-028 tasks.

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
