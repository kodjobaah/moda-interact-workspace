---
id: ARCH-075-SHARED-004
architecture_id: ARCH-075
title: Publish accepted common-layout binding artifact
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-SHARED-003
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Publish accepted common-layout binding artifact

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Publish accepted common-layout binding artifact.

## Context

The user explicitly requires all Meta templates, AI replies and HUMAN messages to share one shop header and checkout footer, with product images separate. Existing Admin-owned SHARED wrapper definition/slot is the common immutable content authority; family-specific body/offer/opt-out content stays intact. No duplicate hardcoded frame builders.

## Scope

Release exact architect-accepted candidate5.13.9 only, canonical existing public npm/latest after explicit tested-artifact user approval.

## Out of Scope

Other repositories, new database tables/settings, provider permissions, live registrations/activation, source merges, unapproved publication, changing billing/cap semantics, arbitrary source refactors, automatic mutation of approved templates. Background engine001 remains on published5.13.8 and producer-disabled.

## Requirements

Prerequisite accepted/Complete and root source merge verified. Publish once after explicit approval; no code edits, rebuild, repack, tests/lint/typecheck repetition. Verify canonical metadata plus actual downloaded bytes SHA256/SHA1/SHA512; never republish on propagation. Stop before consumer work.

## Work Items

- [ ] Complete assigned bounded capability only.
- [ ] Prove compatibility and meaningful negative/failure behavior.
- [ ] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-SHARED-003

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [ ] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [ ] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [ ] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [ ] Accepted exact source/artifact, merge and explicit user approval verified.
- [ ] One canonical receipt and exact version/latest plus actual byte hashes.
- [ ] No source edits or repeated implementation validation.

## Stop Condition

After required work and validation, submit review and STOP. No enabled-task execution, merge, live mutation or unapproved public release.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet is startup/isolation authority. Report actual cross-owner gaps rather than inventing a setting/schema or weakening strict validation.

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

None beyond approved contracts.

### Unresolved Issues

None currently; return concrete gaps.

### Architectural Concerns

Preserve one common content authority and immutable prior registrations.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
