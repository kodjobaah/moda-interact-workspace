---
id: ARCH-075-GATEWAY-001
architecture_id: ARCH-075
title: Declare Meta app identity for template workers
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-075-SYSTEM-TEST-001
created: 2026-11-13
updated: 2026-11-13
---

# Declare Meta app identity for template workers

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Declare Meta app identity for template workers.

## Context

Actual staged registration encountered missing worker META_APP_ID before durable creation intent. BLOCKED rows cannot normally recover. Separately Admin confirmation accepts English SOURCE_SAVED while Background correctly requires REVIEWED; reviewing English only after provider approval is circular. These are concrete distinct owned gaps; preserve all accepted content/transport work.

## Scope

Relevant render.test.yaml/render.production.yaml merchant-communications worker envVars and canonical render.yaml only if it declares the same service; matching deployment notes and structural checks.

## Out of Scope

Other repositories, Shared publication/schema, provider guard weakening, uncertain template-create retry, live provider/database/configuration writes, source merges, automatic activation or unrelated refactors.

## Requirements

Declare META_APP_ID with sync:false only on actual merchant-communications worker services in both environments. No hardcoded app IDs/credential values, unrelated services, topology/scaling or env-group changes. Confirm actual upload adapter consumes the variable and startup worker matches declarations. Document setting the existing provider app identity through secure Render env mechanism; no new app/grants or credential rotation. Document preclaim failure recovery dependency instead of direct database repair. No live Render mutation in task.

## Work Items

- [ ] Confirm owning defect and implement only bounded capability.
- [ ] Prove meaningful failure/race/compatibility behavior.
- [ ] Complete checks, mirrored Completion Report and stop.

## Interfaces / Contracts

Existing Admin confirmed Meta registration and Background immutable provider lifecycle; Gateway owns runtime variable declaration. No new cross-service payload, setting, schema or Shared release. Runtime provider config remains server-owned and no secrets enter diagnostics.

## Dependencies

None

## Enables

ARCH-075-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Assigned bounded gap corrected without weakening permission/provider identity or immutable source guards.
- [ ] Negative/race/idempotency behavior and unchanged legacy domain semantics proven where applicable.
- [ ] Canonical physical isolation/synchronization and exact checks documented; no live action by agent.

## Validation

- [ ] Declared YAML/blueprint structural validation and focused service/env assertions: each relevant test/production worker exactly one META_APP_ID sync:false, no value/secrets/unrelated changes. Existing declared lint/checks as appropriate; report baseline unavailable tooling honestly, no app tests or deploy.
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
