---
id: ARCH-007-BACKGROUND-002
architecture_id: ARCH-007
title: Implement concurrency-safe Free recovery reservation, commit and release
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 70
executor: null
claimed_at: null
attempt: 2
depends_on: 
  - ARCH-007-BACKGROUND-001
enables: 
  - ARCH-007-BACKGROUND-003
created: 2026-09-07
updated: 2026-09-08T00:21:00+01:00
---

# ARCH-007-BACKGROUND-002: Implement concurrency-safe Free recovery reservation, commit and release

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Implement the Prisma-only admission mutation that prevents concurrent workers from overspending the final Free lifetime recovery credit and commits/releases one deterministic reservation safely.

## Context

ARCH-007 explicitly forbids aggregate-then-send races. Prisma has no need for raw SQL here: use ShopEntitlementCounter.version with conditional `updateMany` CAS inside bounded interactive transactions/retries.

## Scope

New Background reservation service and focused unit + disposable PostgreSQL concurrency tests. No recovery worker integration yet.

## Out of Scope

- Sending WhatsApp messages.
- Creating merchant notifications.
- Shopify App Events.
- Paid overage logic beyond returning non-Free admission semantics.

## Requirements

- Input includes shopId and deterministic recovery reservation sourceKey. Same sourceKey replay must return the existing terminal/current reservation outcome.
- Inside transaction resolve/verify Free policy and effective allowance, load/create counter safely, read version/committed/reserved, and only reserve if `committed + reserved + quantity <= allowance`.
- Perform conditional counter update using Prisma `updateMany` matching key/version and atomic increment reserved/version. Count=0 is a concurrency conflict; retry the whole bounded operation with a small fixed maximum. Do not spin indefinitely.
- Persist UsageReservation in same correctness boundary. Handle unique-source race by re-reading existing reservation rather than creating another capacity unit.
- Commit transition RESERVED->COMMITTED must atomically decrement reserved, increment committed, update version, create/link exactly one NOT_REPORTABLE Free RECOVERY_CONVERSATION UsageEvent and set reservation COMMITTED.
- Release transition RESERVED->RELEASED must atomically decrement reserved/update version and never decrement committed. Releasing COMMITTED is not allowed through this API.
- Ambiguous provider outcome can transition reservation to AMBIGUOUS without releasing capacity; reconciliation is BACKGROUND-003/008 as applicable.
- Signed allowance adjustment reduction must not corrupt counters even if effective allowance falls below already committed usage; it simply prevents further reservation.
- Use serializable isolation if supported by current Prisma/runtime in addition to CAS where useful, but correctness must be explicit and tested. No raw SQL/DB advisory lock.

## Work Items

- [x] Implement reserve/commit/release/markAmbiguous APIs.
- [x] Add deterministic idempotency usage identity generation using Shared helper.
- [x] Add unit tests for terminal replay and invalid transitions.
- [x] Add disposable PostgreSQL test launching at least two concurrent final-credit reservations and prove at most one succeeds.
- [x] Test CAS conflict retry bound.

## Interfaces / Contracts

State machine:

```text
RESERVED -> COMMITTED
RESERVED -> RELEASED
RESERVED -> AMBIGUOUS
COMMITTED/RELEASED are terminal for automatic replay
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-003

## Acceptance Criteria

- [x] Two simultaneous attempts for one remaining credit produce exactly one reserved capacity unit.
- [x] Same sourceKey replay never double-reserves/commits.
- [x] Commit atomically creates one usage event and counter transition.
- [x] Release restores reserved capacity exactly once.
- [x] No raw SQL is introduced.
- [x] Disposable PostgreSQL concurrency proof and repository validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes

Exact Shared dependency for this task: `@modainteract/moda-interact-shared@0.7.3`. Provider-status v2/Shared `0.7.4` is not required by this reservation task.


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-BACKGROUND-002` branch and the mirrored parent-workspace `task/ARCH-007-BACKGROUND-002` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/services/effective-billing-policy.service.ts`
- `moda-interact-background/src/services/free-recovery-reservation.service.ts`
- `moda-interact-background/tests/unit/services/free-recovery-reservation.service.test.ts`
- `moda-interact-background/tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
- `moda-interact-background/scripts/test-integration.mjs`

### Work Completed

- Implemented serializable Prisma transactions with bounded retries around versioned `ShopEntitlementCounter` CAS updates.
- Added deterministic source-key replay, tenant validation, terminal transition handling, and `markAmbiguous` capacity retention.
- Commit atomically moves reserved to committed capacity and creates/links one Free `RECOVERY_CONVERSATION` usage event using the Shared deterministic recovery idempotency helper.
- Release decrements reserved capacity only; committed release is rejected.
- Added unit coverage for reservation, commit/release/ambiguous behavior, replay, invalid transitions, CAS retry bounds, and cross-shop source reuse.
- Added disposable PostgreSQL concurrency coverage for two simultaneous attempts against one remaining credit.
- Added P2002 loser retry/replay coverage with same-shop ownership enforcement, bounded retry exhaustion coverage, and allowance-reduction coverage below committed/reserved usage.
- Explicitly persisted the accepted Prisma `ShopifyReportState.NOT_APPLICABLE` state for committed Free recovery usage events and asserted the metric/idempotency/event state.

### Validation Results

- `npm run build` passed, including Prisma generation and TypeScript compilation.
- `npm run prisma:validate` passed.
- Focused reservation unit suite passed: 9 tests.
- Disposable PostgreSQL concurrency test passed: 1 test.
- Default `npm test`: 252 passed, 6 skipped, with the same 3 pre-existing unrelated failures in recovery-routing and pending-recovery-candidate tests.
- `git diff --check` passed.

### Deviations

- The disposable PostgreSQL integration test remains gated behind the existing `scripts/test-integration.mjs` wrapper so the default Vitest run does not execute it against an ambient, potentially non-migrated database.
- The full repository suite retains three unrelated baseline failures; no unrelated production code was changed to address them.

### Assumptions

- `@modainteract/moda-interact-shared@0.7.3` remains the authoritative dependency for this task.
- Reservation callers provide deterministic, shop-scoped source keys.

### Unresolved Issues

- The existing recovery-routing and pending-recovery-candidate baseline failures remain for architect review.

### Architectural Concerns

- None identified within BACKGROUND-002 scope. Recovery worker integration and reconciliation remain BACKGROUND-003/008 work.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 Changes Requested required four bounded corrections:

- Recover a concurrent duplicate `sourceKey` after `P2002` by allowing the losing transaction to roll back, re-reading the winning reservation, enforcing same-shop ownership, and replaying it without consuming another capacity unit.
- Explicitly persist committed Free `RECOVERY_CONVERSATION` usage as `ShopifyReportState.NOT_APPLICABLE` and assert that state.
- Prove repeated retryable `P2034`/CAS conflicts stop at the configured retry maximum.
- Prove an allowance reduction below already committed/reserved usage returns allowance exhausted without corrupting the counter.

Attempt 2 satisfies the correction contract. `reserve()` retries the complete serializable transaction for `P2002`, `P2034`, and internal CAS conflicts; replay reuses the existing reservation and applies shop ownership validation. Commit writes `ShopifyReportState.NOT_APPLICABLE` in the same transaction as the committed counter/reservation transition. Focused tests cover P2002 replay, bounded retry exhaustion, the explicit usage-event report state, and allowance-reduction safety. The existing disposable PostgreSQL final-credit concurrency proof remains in place. No raw SQL was introduced.

### Reviewed Files

- `moda-interact-background/src/services/free-recovery-reservation.service.ts`
- `moda-interact-background/src/services/effective-billing-policy.service.ts`
- `moda-interact-background/tests/unit/services/free-recovery-reservation.service.test.ts`
- `moda-interact-background/tests/integration/free-recovery-reservation.concurrency.integration.test.ts`
- `moda-interact-background/scripts/test-integration.mjs`
- `docs/decisions/background/ARCH-007/BACKGROUND-002-free-recovery-reservation-service.md`

### Validation Reviewed

- Build/typecheck: passed per Completion Report.
- Prisma validation: passed per Completion Report.
- Focused reservation tests: 9 passed.
- Disposable PostgreSQL concurrency test: passed.
- Full suite: 252 passed, 6 skipped, 3 documented pre-existing baseline failures.
- `git diff --check`: passed.
- Architect source inspection confirmed bounded retry handling, rollback-safe replay structure, explicit `NOT_APPLICABLE`, counter-preserving allowance exhaustion, and absence of raw SQL in the task slice.

### Architecture Conformance

Accepted. The implementation conforms to ARCH-007's Prisma-only, serializable/CAS, deterministic-idempotency and Free-lifetime-capacity invariants for this task boundary.

### Follow-up

`ARCH-007-BACKGROUND-003` is unblocked because `ARCH-007-BACKGROUND-002` and `ARCH-007-SHOPIFY-001` are Complete; mark it Ready. Recovery-path integration remains owned by BACKGROUND-003 and must not be folded into this completed task.
