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
status: in_progress
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

- [ ] Background ingestion requires current plan entitlement and explicit merchant ON preference.
- [ ] OFF leaves durable PENDING/ACTIVE data untouched.
- [ ] Existing periodic reconciliation starts eligible PENDING work after ON without another queue type.
- [ ] Existing deterministic job identity is preserved.

## Validation

- [ ] focused entitlement/reconciliation tests
- [ ] disposable PostgreSQL transition proof
- [ ] `npm run build`
- [ ] changed-file diagnostics
- [ ] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
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
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
