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
status: in_progress
priority: 85
executor: developer
claimed_at: 2026-10-22T21:07:04Z
attempt: 1
depends_on:
  - ARCH-028-BACKGROUND-004
  - ARCH-028-BACKGROUND-008
  - ARCH-027-BACKGROUND-005
enables:
  - ARCH-028-SYSTEM-TEST-001
created: 2026-10-07
updated: 2026-10-22
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

- [ ] Consume accepted ARCH-027 purchase/refund state rather than reconstructing old state.
- [ ] One durable compensation correction/disposition per reservation.
- [ ] Purchased negative compensation inherits the original event's exact Shop/provider on both platforms and is not externally Shopify-reportable.
- [ ] Live refund hold remains held; provider-refunded source remains closed.
- [ ] No second provider refund attempt is created.
- [ ] Reachability/notification only follow successful correction.
- [ ] Non-`131026` errors do not cause purchased-credit compensation under the current contract; a future approved wider predicate must reuse the exact purchased strategy with a truthful reason.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.
- [ ] Five architect-approved baseline-test corrections assert the **existing runtime contract**, including exact Shared `2.5.0`, content-moderation fail-closed, pre-routing raw abuse admission, and withholding of summaries without moderation provenance; no production safeguards are relaxed.

## Work Items

- [ ] Extend compensation orchestrator for committed purchased source.
- [ ] Add active/completed, live-refund, refunded and incoherent-state tests, including provider-aware negative correction attribution for Shopify and Woo.
- [ ] Reuse suppression/notification pipeline.
- [ ] Add provider-status replay/idempotency tests.
- [ ] Test exact recovery-template source lineage (including HUMAN sequence-2 where already durably linked) and reject unrelated HUMAN_TEXT/cross-Shop or ambiguous provider evidence.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.
- [ ] Align the observability startup test with the architecture-approved exact Shared dependency `2.5.0`, without changing `package.json` or installed dependency versions.
- [ ] Isolate the checkout-refresh *history ordering* fixture from platform moderation configuration using explicitly approved synthetic history; retain production moderation fail-closed policy.
- [ ] Replace B011-03/B011-05 obsolete worker source-string checks with behaviour tests exercising raw admission before routing/persistence and denial before all downstream operations.
- [ ] Update recovery-agent-context expectations to preserve `summary: null` for persisted summaries without content-specific moderation provenance.
- [ ] Re-run the five affected suites and full Background suite; document exact validation, build and any remaining failures in this task's Completion Report.

## Interfaces / Contracts

Consumes DATABASE-001 provenance, BACKGROUND-004 orchestrator, BACKGROUND-011/008 post-correction capabilities and final `ARCH-027-BACKGROUND-005` purchase/refund semantics.

## Dependencies

- `ARCH-028-BACKGROUND-004`
- `ARCH-028-BACKGROUND-008`
- `ARCH-027-BACKGROUND-005`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Committed purchased terminal delivery failure is corrected exactly once.
- [ ] Existing refund hold/provider-refunded state remains authoritative.
- [ ] No provider monetary refund is created/reopened.
- [ ] Corrected purchased case reaches the same suppression/merchant-notification ordering as generic cases.
- [ ] Suppression is mandatory only when exact `131026` is the reason; a general FAILED adjustment requires prior separate architecture/Database acceptance and must not spoof recipient-unreachable reason.
- [ ] For both Shopify and Woo, the negative UsageEvent has the original committed `shopId` and `provider`, no Shopify-reporting identifiers, and cannot enter the Shopify publication pipeline; repeat delivery creates no second correction.
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.
- [ ] The five previously failing full-suite cases pass without changing production code or dependency versions: Shared runtime pin, checkout-history ordering fixture, B011-03/B011-05 raw admission gates, and null recovery summary.
- [ ] The complete Background suite is rerun and results documented; test reconciliation must not introduce new failures or remove coverage of the protected behaviours.

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

In Progress — Attempt 1 claimed by developer at 2026-10-22T21:07:04Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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
