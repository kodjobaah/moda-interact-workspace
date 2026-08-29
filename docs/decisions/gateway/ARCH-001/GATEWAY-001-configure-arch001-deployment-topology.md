---
id: ARCH-001-GATEWAY-001
architecture_id: ARCH-001
title: Configure deployable ARCH-001 service topology
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-001-SHARED-001
  - ARCH-001-SHOPIFY-001
  - ARCH-001-BACKGROUND-001
enables: []
created: 2026-08-29
updated: 2026-08-29
---

# Configure Deployable ARCH-001 Service Topology

## Architecture

Architecture ID:

ARCH-001

Architecture document:

`docs/architecture/ARCH-001-shopify-checkout-recovery-webhook-processing.md`

Coordinator:

`moda_architect`

## Objective

Make the current ARCH-001 application/background topology deployable and operationally explicit without changing Shopify/recovery business logic.

## Context

Architect review found infrastructure work that is currently implicit:

- both `moda-interact` and `moda-interact-background` depend on `@modainteract/moda-interact-shared` using `file:../moda-interact-shared`;
- their Dockerfiles install dependencies from the individual service directory;
- no ARCH-001 gateway/Render topology is currently documented;
- the background process hosts all current workers plus `/health` in one process.

The infrastructure owner must establish how these services build, connect and scale in the actual deployment environment.

## Scope

- Inspect the actual Render/source-repository/build-context model used for:
  - `moda-interact`;
  - `moda-interact-background`;
  - `moda-interact-shared`;
  - `moda-interact-gateway` where applicable.
- Ensure a clean production build can resolve the canonical shared package.
- Define/configure the ARCH-001 service topology and deployment configuration.
- Preserve `moda-interact` as the Shopify application/webhook business ingress unless the parent architecture is explicitly changed.
- Configure/document background worker service startup and health/readiness.
- Configure/document Redis Cloud and PostgreSQL environment wiring using secret references, never committed secret values.
- Document horizontal worker scaling knobs and the current all-workers-in-one-process limitation.
- Add infrastructure validation commands/scripts where useful.
- Document deployment order for the pre-production breaking rollout.

## Out of Scope

- Shopify webhook business logic.
- Recovery/candidate/order business logic.
- Publishing the shared package to a registry without architect approval.
- Splitting background workers into new application entrypoints unless a separate `moda_background` task is created.
- Database schema changes.
- Live production rollout.

## Requirements

Do not assume a build context that does not match the actual Render/source setup.

The existing `file:../moda-interact-shared` dependency must be proven to work in the configured production build context or returned as an architectural blocker.

If package distribution or a missing application entrypoint is required, stop and report the exact missing capability to `moda_architect`; do not silently implement another repository's business/application ownership.

No secret values may be committed.

Infrastructure configuration must preserve independent scaling of the Shopify web service and the background worker service.

## Work Items

- [ ] Inspect current repository/build/deployment topology.
- [ ] Verify how the shared package is resolved in clean production builds.
- [ ] Add/update Render/Docker/gateway configuration within authorised infrastructure scope.
- [ ] Document public/private service exposure.
- [ ] Document Redis/PostgreSQL/environment wiring.
- [ ] Verify health/readiness behaviour.
- [ ] Document background scaling knobs and limitations.
- [ ] Record pre-production deployment order.
- [ ] Run available infrastructure/build validation.

## Interfaces / Contracts

Consumes the deployable outputs of:

- `ARCH-001-SHARED-001`
- `ARCH-001-SHOPIFY-001`
- `ARCH-001-BACKGROUND-001`

No business runtime contract is owned by this task.

## Dependencies

- ARCH-001-SHARED-001
- ARCH-001-SHOPIFY-001
- ARCH-001-BACKGROUND-001

## Enables

The later ARCH-001 system-test task once all business implementation dependencies are also Complete.

## Acceptance Criteria

- [ ] Actual Render/source/build-context assumptions are documented.
- [ ] Clean app/background production builds have a valid way to resolve `@modainteract/moda-interact-shared`.
- [ ] Shopify web service and background worker service remain independently scalable.
- [ ] Health/readiness configuration is explicit.
- [ ] Redis/PostgreSQL/env wiring is explicit and contains no committed secrets.
- [ ] Deployment order is documented for the pre-production breaking rollout.
- [ ] Missing application capabilities, if any, are returned to `moda_architect` rather than implemented across ownership boundaries.

## Validation

- [ ] clean production build or equivalent build-context validation
- [ ] background health check
- [ ] infrastructure configuration validation
- [ ] deployment topology review

## Implementation Notes

This task may inspect affected repositories. It may modify Docker/Render/infrastructure files outside `moda-interact-gateway/` only where the task scope and `moda_gateway` agent definition explicitly authorise infrastructure configuration.

If the real deployment model cannot support the local shared-package dependency without an additional publishing/distribution decision, return this task Blocked with evidence.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None. The task must inspect the actual deployment topology rather than assume it.

### Unresolved Issues

Current production build resolution of `file:../moda-interact-shared` is unverified.

### Architectural Concerns

None beyond the issue above; return any discovered cross-repository capability gap to `moda_architect`.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
