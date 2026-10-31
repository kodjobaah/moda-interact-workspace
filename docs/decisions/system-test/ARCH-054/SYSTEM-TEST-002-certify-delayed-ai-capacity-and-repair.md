---
id: ARCH-054-SYSTEM-TEST-002
architecture_id: ARCH-054
title: Certify 10k pending turns and durable Redis/worker recovery
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-054-SYSTEM-TEST-001
  - ARCH-054-BACKGROUND-003
enables: []
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-SYSTEM-TEST-002: Certify 10k pending turns and durable Redis/worker recovery


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Prove concurrency and repair behaviour under a representative burst without occupying workers during delay or duplicating sends.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Add `ARCH054-DELAY-CAPACITY-001` to `catalogue/scenarios.json` and bounded load fixture under `test/harness/arch054/` using existing disposable PostgreSQL, Redis, queue depth/age observations and Meta fake. Use explicit environment-safe client concurrency; do not run in production.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Seed 10,000 valid shop-scoped pending AI conversations with mixed delay 0,7,30, a controlled fake clock, and two independent messaging-worker instances. Show zero workers occupied *waiting* for deadlines. Trigger large due-time burst and prove queue depth drains under configured worker concurrency, with bounded DB queries and no long transaction holds.
- Simulate loss of Redis delayed jobs, worker crash mid-processing, duplicated/missing queue publication and queue retry. Repair must re-enqueue latest-version only and never renew deadlines; conversation claim and original-revision gates block duplicate/out-of-order Meta sends. HOT tenant and different merchant workloads must not starve. Observe queue lag and oldest due age; do not assert an arbitrary throughput target without measured evidence.
- Capture resource usage, DB connection observations, Redis queue depth, original provider faults and cleanup; report throughput as measured/estimated with assumptions.


## Work Items

- [ ] Implement bounded capacity scenario and result assertions; run in disposable environment with two workers, retained evidence and cleanup.


## Interfaces / Contracts

No new runtime contract; uses published delay settings and existing queue job schema.


## Dependencies

- ARCH-054-SYSTEM-TEST-001
- ARCH-054-BACKGROUND-003


## Enables

None


## Acceptance Criteria

- [ ] 10,000 scheduled do not consume 10,000 active workers; overdue work eventually drains with two replicas.
- [ ] Fault injection does not cause early/stale/duplicate provider admission; capacity metrics and cleanup evidence are recorded.


## Validation

- [ ] `npm run validate:catalogue`; focused node harness tests; `node scripts/run-system-tests.js --scenario ARCH054-DELAY-CAPACITY-001 --execute`; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

None

### Worktree and Git Evidence

Not materialised; implementing agent must record launcher-prepared dedicated parent/implementation worktree paths, start-of-attempt sync, branch SHAs, submodule pins and cleanup.


## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
