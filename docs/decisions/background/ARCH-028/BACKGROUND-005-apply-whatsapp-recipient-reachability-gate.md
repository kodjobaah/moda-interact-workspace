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
status: review
priority: 47
executor: null
claimed_at: null
attempt: 1
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

- [ ] Every initial and follow-up attempt has a required canonical digits-only recipient matching the actual Meta destination.
- [ ] Recipient selection uses current Shop-scoped `CustomerPhone`, never stale `Customer.phone`; BACKGROUND-007 remains the initial materialisation guard. A null/stale `Customer.phone` does not block an otherwise eligible follow-up with a current usable `CustomerPhone`.
- [ ] Attempt recipient is immutable after provider-directed work; a new current phone requires a separate attempt snapshot.
- [ ] Provider delivery status never resolves tenant ownership through phone lookup.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Reuse BACKGROUND-007 recipient-prerequisite output for initial attempt creation and send.
- [ ] Add canonical current-`CustomerPhone` selection and per-attempt recipient snapshots for follow-ups.
- [ ] Adopt DATABASE-003 across all attempt creation paths and fixtures.
- [ ] Verify persisted recipient equals the actual provider destination even when current phone changes.
- [ ] Add initial/follow-up and multi-Shop same-number tests, including null and stale `Customer.phone` with a valid current `CustomerPhone` and actual Meta destination parity.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

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

 Ready for Architect Review. Developer-owned disposable PostgreSQL integration remains required before acceptance.

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

### Validation Results

 Agent-executed validation passed:

 - `npx vitest run tests/unit/services/customer.phone.service.test.ts tests/unit/services/checkout-recovery/recovery-recipient-resolver.service.test.ts tests/unit/recovery-outreach-follow-up.test.ts tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts` — 5 files, 42 tests passed.
 - `npm run test:unit` — 176 files, 1,888 tests passed.
 - `npm run prisma:validate` — valid against DATABASE-003.
 - `npm run build` — Prisma Client generated from DATABASE-003 and TypeScript build passed.
 - `npx tsc --noEmit` — passed after adding the PostgreSQL integration test.
 - `git diff --check` — passed.

 Developer validation required:

 - `npm run test:integration -- tests/integration/recovery-outreach-recipient.integration.test.ts` — run the repository-owned disposable PostgreSQL/Redis harness and verify the real attempt row persists the required canonical recipient. Not run by this agent because workspace policy reserves multi-container integration execution for the developer unless explicitly authorized.

### Deviations

 The disposable PostgreSQL integration test was added but not executed by the agent under the workspace validation policy. The initial build also exposed that the prepared Background gitlink pointed to DATABASE-001; the task branch now adopts the accepted DATABASE-003 implementation commit exactly.

### Assumptions

 The accepted DATABASE-003 commit `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce` is the database revision intended for this task's compatible runtime adoption.

### Unresolved Issues

 Developer-owned disposable PostgreSQL integration command above remains to be run and reviewed.

### Architectural Concerns

 No architectural concern identified. The breaking recipient schema and compatible attempt writers are represented together on this task branch.

 ### Execution Evidence

 - Launcher prepared Attempt 1 for executor `copilot`; dependencies DATABASE-003 and BACKGROUND-007 passed.
 - Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-005`, branch `task/ARCH-028-BACKGROUND-005`.
 - Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-005`, branch `task/ARCH-028-BACKGROUND-005`.
- Implementation commits `c36434f5812b605aba7b930f9603db141d3cf143` and `f42d2867d30639cfc9d8b7cb4b87c1843017eb5f` adopt database commit `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce`.
 - Parent claim commit: `c5c9eccb4de487fa9457defca88b37ae9e3efa8f`; prepared parent head `845e108175d6b3dad14c21d815b4d83c274cf53d`; prepared implementation head `5e40e7aa4e5ce4bb4802b52c7d6b149eb4217130`.
 - The database submodule working tree is clean at the exact accepted DATABASE-003 commit; no database submodule content was modified.
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
