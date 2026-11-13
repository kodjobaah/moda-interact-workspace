---
id: ARCH-075-SHARED-003
architecture_id: ARCH-075
title: Add canonical website binding for common recovery layout
task_kind: implementation
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
  - ARCH-075-SHARED-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Add canonical website binding for common recovery layout

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Add canonical website binding for common recovery layout.

## Context

The user explicitly requires all Meta templates, AI replies and HUMAN messages to share one shop header and checkout footer, with product images separate. Existing Admin-owned SHARED wrapper definition/slot is the common immutable content authority; family-specific body/offer/opt-out content stays intact. No duplicate hardcoded frame builders.

## Scope

Add only shop.websiteUrl to canonical recovery-template semantic keys and wrapper variables/parser; public exports/types, compatibility tests and candidate5.13.9 exact artifact. Reuse existing prepared wrapper token contracts/rendering, no new frame/content builder.

## Out of Scope

Other repositories, new database tables/settings, provider permissions, live registrations/activation, source merges, unapproved publication, changing billing/cap semantics, arbitrary source refactors, automatic mutation of approved templates. Background engine001 remains on published5.13.8 and producer-disabled.

## Requirements

The website is a separate semantic value, never overload shop.name or insert multi-line arbitrary text into one Meta parameter. Host supplies verified saved shop origin; Shared does not read environment/database or derive authorization. Existing old projections, unknown-key rejection and checkout conditional restrictions stay intact. New website token may appear wherever the corresponding shop.name text token is valid, subject to existing family-specific Admin rules. No new template-part transport contract. Build exact immutable5.13.9 only if available; no publication in this task.

## Work Items

- [ ] Complete assigned bounded capability only.
- [ ] Prove compatibility and meaningful negative/failure behavior.
- [ ] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-SHARED-002

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [ ] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [ ] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [ ] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [ ] Focused semantic key/wrapper projection positive/unknown-key/legacy/digest tests.
- [ ] Full declared package tests, typecheck, ESM/DTS build and exact packed installed JS/types/browser exports.
- [ ] Immutable artifact hashes and privacy/diff checks.

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
