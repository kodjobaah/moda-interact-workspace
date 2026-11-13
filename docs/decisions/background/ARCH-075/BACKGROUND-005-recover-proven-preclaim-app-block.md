---
id: ARCH-075-BACKGROUND-005
architecture_id: ARCH-075
title: Recover proven preclaim missing-app registration blocks
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-BACKGROUND-004
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Recover proven preclaim missing-app registration blocks

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Recover proven preclaim missing-app registration blocks.

## Context

Actual staged registration encountered missing worker META_APP_ID before durable creation intent. BLOCKED rows cannot normally recover. Separately Admin confirmation accepts English SOURCE_SAVED while Background correctly requires REVIEWED; reviewing English only after provider approval is circular. These are concrete distinct owned gaps; preserve all accepted content/transport work.

## Scope

Existing Meta management repository/service and a bounded operator-only dry-run/apply recovery command/domain method; immutable manifest/audit and focused unit/PostgreSQL tests. No automatic broad retry of BLOCKED rows.

## Out of Scope

Other repositories, Shared publication/schema, provider guard weakening, uncertain template-create retry, live provider/database/configuration writes, source merges, automatic activation or unrelated refactors.

## Requirements

Recover only exact BLOCKED/META_APP_ID_MISSING_OR_INVALID registrations in reviewed bounded manifest (at most20 IDs per operation), repaired trusted app/WABA configuration and current unchanged frozen reviewed source. Require providerTemplateId/lastSubmittedAt absent and no historical CREATE_INTENT, POST_INTENT or other evidence of submission claim/HTTP creation. Lock/CAS exact id,WABA,state,reason,updatedAt and expected immutable snapshot identity; any mismatch/otherfailure/unknown/submitted row refuses. Atomically audit truthful preclaim recovery and set READY_TO_SUBMIT/due through domain method, without resetting history/counters, sending provider requests or creating a new registration. Dry-run default, explicit apply+manifest digest; repeat no duplicate transition/audit. Keep ordinary claim/reconciliation/provider-absence guards unchanged. Live historical20 recovery root-owned only after source acceptance, trusted config and English review repair; task agent does not execute it.

## Work Items

- [ ] Confirm owning defect and implement only bounded capability.
- [ ] Prove meaningful failure/race/compatibility behavior.
- [ ] Complete checks, mirrored Completion Report and stop.

## Interfaces / Contracts

Existing Admin confirmed Meta registration and Background immutable provider lifecycle; Gateway owns runtime variable declaration. No new cross-service payload, setting, schema or Shared release. Runtime provider config remains server-owned and no secrets enter diagnostics.

## Dependencies

ARCH-075-BACKGROUND-004

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Assigned bounded gap corrected without weakening permission/provider identity or immutable source guards.
- [ ] Negative/race/idempotency behavior and unchanged legacy domain semantics proven where applicable.
- [ ] Canonical physical isolation/synchronization and exact checks documented; no live action by agent.

## Validation

- [ ] Red/green exact missing-app preclaim blocked recovery; dry-run/no mutation, digest/config/source/WABA mismatch, CREATE/POST intent, providerId/lastSubmitted, foreign/uncertain/otherblocked refusal, concurrency/CAS/replay and audit rollback. Real PostgreSQL proof plus focused Meta-management tests/types/scopedlint/exact-head full CI.
- [ ] Diff/privacy hygiene and no unauthorized external mutation.

## Stop Condition

After required scope/checks, submit review and STOP. Do not execute live repair, register providers, deploy, merge or begin follow-on tasks.

## Implementation Notes

You are not alone; preserve others. Canonical launcher packet owns startup/claim. Root owns all final integration and live operations. Generic logging uses published shared logging if changed. Return actual dependency gaps rather than inventing alternate protocol or local generic primitives.

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

None beyond the approved existing contracts.

### Unresolved Issues

None currently.

### Architectural Concerns

Return concrete gaps before widening scope.

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
