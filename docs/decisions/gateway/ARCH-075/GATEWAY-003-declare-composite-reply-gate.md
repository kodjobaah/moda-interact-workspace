---
id: ARCH-075-GATEWAY-003
architecture_id: ARCH-075
title: Declare default-off composite reply deployment gate
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-BACKGROUND-014
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Declare default-off composite reply deployment gate

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Codify the new defaultOFF composite writer gate and safe reader-first activation procedure without changing deployment topology.

## Context

Single-bubble composite uses distinct RECOVERY_COMPOSITE_REPLY_ENABLED so current branded-main gate stays unchanged. Source branch implementation is separately tested; no live activation requested by task author.

## Scope

Canonical test/production Render Blueprint messagingworker service-level env declaration sync:false, existing bounded Blueprint negative validation and deployment documentation.

## Out of Scope

Application implementation, secrets/hardcodedtrue, other workers/services topology/cost/scaling, live Render changes/sends, npm publication.

## Requirements

- Declare exact composite gate service-level sync:false for messagingworker in test/production only. Do not hardcode enable or groupinheritance; absent/invalid/false remains OFF under Background.
- Document deployed reader-first with compositeOFF: verify actual runtime inventory, every old reader drained, safe startup boolean proof, then root separately authorizes ON and actual one-bubble media/caption. Rollback writerOFF preservingnewreader/frozenplans; noqueueclear/reset.
- Existing branded-main flag unaffected. No secret values, new services or cost. Preserve current Blueprint validations and existing rollout docs.

## Work Items

- [ ] Add narrow declarations/negative validation.
- [ ] Document exact OFF→readerdrain→authorizedON and rollback.
- [ ] Run bounded Blueprint checks and publish report.

## Interfaces / Contracts

Accepted Background014 gate exact literaltrue and safe startupboolean; existing canonical Render IaC.

## Dependencies

BACKGROUND014 accepted/integrated before normal preparation. No implementation worktree/claim/live change at definition time.

## Enables

Separately authorized root activation after source/readers/visual checks, not automatic.

## Acceptance Criteria

- [ ] Exact declaration scoped service-level to two messagingworkers, no enabledvalue/secrets.
- [ ] Existing topology/commands unchanged; reader-first and rollback documented.
- [ ] Positive/negative Blueprint checks and clean mirrored evidence.

## Validation

- [ ] Existing declared Blueprint syntax/negative gate validation and appropriate bounded regression checks.
- [ ] Diff/privacy and no application/topology change.

## Stop Condition

Publish exact mirrored source/report, set review and return architect. No main merge, live mutation, enabled consumer or npm publication without release-specific authorization.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others and primary. Original approved mock is schematic only: small contained logo alongside shop details, divider, product beneath. Root owns operational/visual review and integration; no live sends.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root owns final integration and live authorization.

### Unresolved Issues

Publication and consumer/live proof remain gated.

### Architectural Concerns

Return gaps before widening.

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

No architectural/live completion claim.
