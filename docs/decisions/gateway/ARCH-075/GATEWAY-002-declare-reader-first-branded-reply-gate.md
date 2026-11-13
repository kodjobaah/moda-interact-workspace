---
id: ARCH-075-GATEWAY-002
architecture_id: ARCH-075
title: Declare reader-first branded reply rollout gate
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 5
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-BACKGROUND-010
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Declare reader-first branded reply rollout gate

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Codify the reader-first/new-writer-off deployment gate for consolidated branded replies.

## Context

Commonlayoutalreadyactive; BG010 must not emit newHEADER-only during overlap with oldShared5.13.9 readers. Background implements RECOVERY_BRANDED_MAIN_REPLY_ENABLED defaultoff. Canonical deployment declaration and operator-controlled PhaseA/B sequence must reflect this explicitly.

## Scope

Gateway Render test/production Blueprint declarations and bounded rollout/drift documentation/tests only.

## Out of Scope

Background implementation, environment/live mutation, provider sends, new services/secrets/paidresources, lost-event platformpauses, source/main merges.

## Requirements

- Inspect actual BG010 implementation/env parsing and all producer messaging workers before declaring. Declare RECOVERY_BRANDED_MAIN_REPLY_ENABLED consistently in test/prod canonical Blueprints for relevant workers. Operator-owned activation sync:false or existing approved mechanism must not let Blueprint hardcodedfalse overwrite deliberatePhaseBtrue; document actual unsupported setting owner if required.
- Initial absent/false PhaseA deploys compatible readers with legacywriter. Root verifies ALL oldworkers stopped/drained and allrelevantqueues/frozenjobs preserved, then enablestrue PhaseB; overlapsafe because allreadersnew. Never pause ingress or discard jobs.
- Document exact rootreadback/rollback/driftchecks and environmentisolation. RollbackturnwriterOFF whilekeepingnewreader for alreadyfrozenHEADERplans; do not rollback to oldreader with newjobs.
- No secret value added; no business implementation or liveactions.

## Work Items

- [ ] Inspect acceptedBG010 env/entrypoint and canonicalBlueprint topology.
- [ ] Declare operator gate and exactreader-first/drain/enable/rollback checks.
- [ ] Validate actualdeclaredBlueprint/configtests and publishsource/report.

## Interfaces / Contracts

Background-owned RECOVERY_BRANDED_MAIN_REPLY_ENABLED gate; Gatewayowns Render IaC. No crossservicewire/schema change.

## Dependencies

ARCH-075-BACKGROUND-010 accepted Complete before execution.

## Enables

Root executes PhaseA/B only after accepted topology/source, no implicitoperation.

## Acceptance Criteria

- [ ] Test/prod relevant worker gate declarations matchactualruntime and preserveoperatorenable.
- [ ] Drain/preservejobs/PhaseB/rollback/drift sequence explicit withoutlostevents.
- [ ] Focused declared configuration checks/privacy and preparedisolationevidence pass, no live mutation.

## Validation

- [ ] Existing relevant Blueprint/YAML/config tests and documented envname/default/worker parity; inspectactualpackagescripts.
- [ ] Diff/secret/privacy and normaldedicatedworktreepublicationevidence. Noapplication/provider tests repeated.

## Stop Condition

Publish exactsource/report, setreview, returnarchitectandstop; no main/livechanges.

## Implementation Notes

Normal launcher dedicatedmirroredworktrees, youarenotalonepreservecurrentmain/others. ReturngenuineBGgate mismatch before widening.

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

Root controls live activation.

### Unresolved Issues

PhaseA/B verification remains root-owned.

### Architectural Concerns

Return gaps before expanding.

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

No live rollout or architecture completion claim.
