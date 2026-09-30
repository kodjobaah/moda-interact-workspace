---
id: ARCH-023-BACKGROUND-006
architecture_id: ARCH-023
title: Respect Merchant Knowledge merchant activation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 31
executor: copilot
claimed_at: 2026-09-30T22:54:05Z
attempt: 1
depends_on:
  - ARCH-023-BACKGROUND-001
  - ARCH-023-ADMIN-004
enables:
  - ARCH-023-BACKGROUND-004
created: 2026-09-30
updated: 2026-09-30
---

# Respect Merchant Knowledge merchant activation

## Objective

Extend the accepted BACKGROUND-001 entitlement/PENDING-reconciliation boundary so Merchant Knowledge ingestion is permitted only when both:

```text
planEntitled == true
merchantEnabled == true
```

using the existing `ShopFeaturePreference` state for Feature key `merchant_knowledge`.

This is a bounded follow-up to accepted BACKGROUND-001; do not redesign its queue, job identity or source entitlement algorithm.

## Scope

```text
src/services/merchant-knowledge-entitlement.service.ts
src/services/merchant-knowledge-reconciliation.service.ts   # only tests/wiring if needed

tests/unit/services/merchant-knowledge-entitlement.service.test.ts
tests/unit/services/merchant-knowledge-reconciliation.service.test.ts
bounded PostgreSQL integration proof
```

## Requirements

### R1 — preserve commercial entitlement calculation

Keep BACKGROUND-001 current Subscription/current BillingPlan/C2/source-type/source-count calculations unchanged.

### R2 — require exact merchant opt-in

For the current `merchant_knowledge` Feature require:

```text
Feature.active = true
Feature.activationMode = MERCHANT_OPT_IN
ShopFeaturePreference(shopId, featureId).enabled = true
```

Missing preference is false.

Expose activation state explicitly in the entitlement/source-eligibility result or fold it into `eligible`, but callers must be able to distinguish merchant-disabled dormancy for bounded diagnostics/tests.

### R3 — PENDING reconciliation while OFF

Existing PENDING reconciliation must:

```text
merchant disabled -> skip enqueue, leave revision PENDING
merchant enabled  -> apply existing source entitlement rules and enqueue if eligible
```

No new queue/job/scheduler is introduced. When the merchant turns ON, the existing periodic PENDING reconciliation naturally discovers and enqueues eligible work.

### R4 — processing-race safety

The final processing task (BACKGROUND-004) reuses this activation-aware eligibility before acquisition and before promotion. Therefore an already-queued job must not ingest/promote after the merchant disables Merchant Knowledge.

### R5 — non-destructive OFF state

Turning OFF must not mutate/delete:

```text
sources
revisions
ACTIVE normalized content
chunks/vectors
uploaded assets
```

This task only changes effective processing eligibility.

### R6 — tests

Prove:

```text
plan entitled + missing preference -> ineligible, PENDING not enqueued
plan entitled + false preference -> ineligible, PENDING not enqueued
plan entitled + true preference -> existing eligibility semantics apply
preference true -> false before processing -> eligibility fails closed
preference false -> true -> next reconciliation enqueues same deterministic C4 job id
plan/source-type/source-count rules remain unchanged
no preference row is created by Background
```

Use a disposable PostgreSQL proof for the false->true PENDING reconciliation transition.

## Dependencies

- `ARCH-023-BACKGROUND-001`
- `ARCH-023-ADMIN-004`

## Enables

- `ARCH-023-BACKGROUND-004`

## Acceptance Criteria

- [x] Background ingestion requires current plan entitlement and explicit merchant ON preference.
- [x] OFF leaves durable PENDING/ACTIVE data untouched.
- [x] Existing periodic reconciliation starts eligible PENDING work after ON without another queue type.
- [x] Existing deterministic job identity is preserved.

## Validation

- [x] focused entitlement/reconciliation tests
- [x] disposable PostgreSQL transition proof
- [x] `npm run build`
- [x] changed-file diagnostics
- [x] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Ready for architect review.
### Files Changed
Implementation commit `00176555dfe0278f665c6c602621e18a894c0c3e` changed:
- `src/services/merchant-knowledge-entitlement.service.ts`
- `tests/unit/services/merchant-knowledge-entitlement.service.test.ts`
- `tests/unit/services/merchant-knowledge-reconciliation.service.test.ts`
- `tests/integration/merchant-knowledge-reconciliation.integration.test.ts`

This parent task report is the only parent-worktree file changed.
### Work Completed
Merchant Knowledge eligibility now preserves the existing subscription, plan, C2 and source rules while additionally requiring an active `MERCHANT_OPT_IN` Feature and an explicitly enabled `ShopFeaturePreference`. Missing/disabled preferences fail closed and are exposed as dormant eligibility. PENDING reconciliation skips dormant sources without changing their revisions or creating preferences; when enabled, the existing periodic reconciliation publishes the same deterministic job identity. No new queue or scheduler was added, and no source, revision, ACTIVE content, chunk/vector or asset data is mutated by the OFF path.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-BACKGROUND-006`
  parent branch: `task/ARCH-023-BACKGROUND-006`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-BACKGROUND-006`
  implementation branch: `task/ARCH-023-BACKGROUND-006`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded submodule commits: `database` at `2eb17ee910491e8f9df82736fc0a843844415947`
### Validation Results
  focused entitlement/reconciliation unit tests: passed, 20 tests
  disposable PostgreSQL PENDING OFF-to-ON transition proof: passed, 1 test; confirmed stable deterministic job ID
  `npm run build`: passed (Prisma Client generation and TypeScript compilation)
  changed-file diagnostics: passed, no errors in the four changed implementation files
  `git diff --check`: passed

The repository integration wrapper's default `postgres:17.6-alpine` image could not apply the existing pgvector migration. The same disposable-infrastructure helper was rerun with `pgvector/pgvector:pg17`; migrations and the required integration test then passed, and the disposable services were cleaned up.
### Deviations
The PostgreSQL proof used the helper's supported PostgreSQL image option because the wrapper's default image lacks the repository-required `vector` extension. No repository test, migration, or production code was changed to work around the image mismatch.
### Assumptions
The existing periodic PENDING reconciliation remains the intended mechanism for discovering sources after merchant opt-in; no additional scheduler or queue is required.
### Unresolved Issues
None.
### Architectural Concerns
None. The activation-aware eligibility result is available for the downstream processing task to check before acquisition and promotion; processing implementation remains outside this task's scope.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
