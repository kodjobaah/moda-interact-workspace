---
id: ARCH-075-SYSTEM-TEST-002
architecture_id: ARCH-075
title: Validate durable sample throttle across replicas
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-ADMIN-006
  - ARCH-075-DATABASE-002
  - ARCH-075-BACKGROUND-007
  - ARCH-075-SYSTEM-TEST-001
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Validate durable sample throttle across replicas

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Validate durable sample throttle across replicas.

## Context

Actual Meta sample_session HTTP403/code4 app request limit was classified as permanent blocked. One upload perlocale plus60second local polling and replica overlap can amplify calls; changing classification alone does not give durable cooldown. Existing scheduler leases/config/audit rows are not proper app-scoped lifecycle state. Generic historical rejection events do not carry code4 evidence.

## Scope

Terminal independent disposable PostgreSQL/worker/provider-simulator validation of the accepted new app throttle capability only. Preserve SystemTest001 accepted proof/history.

## Out of Scope

Other repositories except explicit accepted submodule adoption, provider credentials/grants, live sends/repair/deployment, Shared publication, blind create retry, unsupported caching, generic refactors or implementation-source merges.

## Requirements

Also reconcile accepted Admin006 repeated-retry audit proof using actual domain fixtures where appropriate; preserve original SystemTest001 acceptance and do not duplicate unrelated full delivery validation.

Exercise actual accepted sample/provider/submit path and dedicated durable app state across two independent workers/processes: one evidenced code4 produces persistent backoff, stops remaining same-app uploads across cycle/restart/replica and leaves template creation unclaimed; current auth403 remains nonretryable; other app/environment cannot inherit authority. Verify exact operator-evidenced recovery refuses ambiguous/intent-bearing historical blocks and cannot bypass cooldown. Reuse source/image provenance strategy only with explicit accepted-source manifests and Linux runtime Prisma generation for the new model; no host native clients copied. No production build-parity/live/fleet/provider approval claim. No implementation task depends on this terminal task; execute only after accepted prerequisites and root manual checkpoint.

## Work Items

- [ ] Implement only the owning bounded outcome and final contract.
- [ ] Prove meaningful failure/concurrency/compatibility behavior.
- [ ] Complete mirrored report/checks, return review and stop.

## Interfaces / Contracts

Database002 owns durable Prisma/SQL state. Background007 consumes exact accepted schema and owns provider policy/leases/recovery; no new Shared contract. SystemTest002 is terminal validation. Root owns migration/deployment/operational evidence; no network inside transaction.

## Dependencies

ARCH-075-DATABASE-002, ARCH-075-BACKGROUND-007, ARCH-075-SYSTEM-TEST-001

## Enables

None

## Acceptance Criteria

- [ ] Assigned bounded capability/invariants and explicit negative behavior satisfied.
- [ ] Existing provider-intent, tenant/environment, immutable source and legacy lifecycle guards remain intact.
- [ ] Canonical matching physical isolation/sync and exact validation evidence reported; no live mutation.

## Validation

- [ ] Deterministic real PostgreSQL/replica/provider fault scenarios, exact source/migration/image identities and bounded captured telemetry/privacy; relevant harness/static checks. No broad rerun of unchanged ordered-layout scenarios or real API requests.
- [ ] Diff/privacy hygiene; no secrets/private production identifiers or unsupported capability claim.

## Stop Condition

When scope/checks complete, submit Completion Report/status review and STOP. No enabled task, source merge, hosted migration or live recovery/provider action.

## Implementation Notes

You are not alone; preserve other work. Canonical launcher packet owns start/claim. Root owns all final merges, test/prod migration, worker rollout/drain and protected live evidence. New domain logs reuse published Shared logging; do not duplicate generic telemetry. Return genuine contract gaps before widening scope.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

No provider reset guarantee; timing bounds are explicit internal policy.

### Unresolved Issues

None currently.

### Architectural Concerns

Return actual cross-owner gaps before workaround.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
