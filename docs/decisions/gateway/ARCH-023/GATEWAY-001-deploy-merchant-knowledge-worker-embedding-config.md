---
id: ARCH-023-GATEWAY-001
architecture_id: ARCH-023
title: Deploy Merchant Knowledge worker and embedding configuration
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-BACKGROUND-003
  - ARCH-023-BACKGROUND-004
  - ARCH-023-COMMERCE-002
enables:
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Deploy Merchant Knowledge worker and embedding configuration

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Codify the ARCH-023 Merchant Knowledge Background worker deployment and identical platform-wide embedding configuration for Background ingestion and Commerce lookup in the canonical Render Blueprints.

## Context

No new Commerce ingestion service/route is needed. A new Background worker entrypoint does need deployment, and both that worker and the private Commerce service must receive the same embedding provider/model/dimensions/index-version configuration while credentials remain secret.

## Scope

- Declare the Merchant Knowledge worker using the implemented Background start command/readiness contract.
- Add architecture-approved environment variables `EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`, `EMBEDDING_DIMENSIONS`, `EMBEDDING_INDEX_VERSION`, and server-only `EMBEDDING_API_KEY` (or an exact provider-secret mapping approved by the implementation) to both worker and Commerce service.
- Use Render secret placeholders (`sync: false`) for secret values and appropriate non-secret configuration representation.
- Update production/test Blueprint validation and deployment documentation.

## Out of Scope

- Choosing/changing embedding model through Admin/database.
- A new Redis/database/service.
- A public/private ingestion route.
- Secret values in source control.

## Requirements

- Background and Commerce receive identical provider/model/dimensions/index-version values.
- Credential values are never committed.
- Existing translation/preview credentials remain independent unless deliberately reused by deployment configuration.
- No other worker is forced to carry embedding credentials without need.

## Work Items

- [ ] Update canonical Render production/test topology.
- [ ] Extend Blueprint validators/negative fixtures.
- [ ] Document deployment secret/config requirements and rollback.

## Interfaces / Contracts

Deploys ARCH-023-BACKGROUND-003/004 worker entrypoint and configuration consumed by ARCH-023-COMMERCE-002.

## Dependencies

- ARCH-023-BACKGROUND-003
- ARCH-023-BACKGROUND-004
- ARCH-023-COMMERCE-002

## Enables

- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Blueprint declares runnable Merchant Knowledge worker.
- [ ] Commerce and worker have matching non-secret embedding config keys.
- [ ] No secret value appears in repository.

## Validation

- [ ] Gateway Blueprint validation scripts.
- [ ] Negative secret/topology validation where applicable.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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

Pending.

### Follow-up

None
