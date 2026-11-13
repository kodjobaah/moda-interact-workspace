---
id: ARCH-075-ADMIN-002
architecture_id: ARCH-075
title: Coordinate approved common-layout activation
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-ADMIN-001
  - ARCH-075-BACKGROUND-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Coordinate approved common-layout activation

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Coordinate approved common-layout activation.

## Context

The user explicitly requires all Meta templates, AI replies and HUMAN messages to share one shop header and checkout footer, with product images separate. Existing Admin-owned SHARED wrapper definition/slot is the common immutable content authority; family-specific body/offer/opt-out content stays intact. No duplicate hardcoded frame builders.

## Scope

Existing Admin approved-source/publication preview, SHARED wrapper activation/CAS/audit and registered replacement readiness. Source capability only; no live provider publication or activation.

## Out of Scope

Other repositories, new database tables/settings, provider permissions, live registrations/activation, source merges, unapproved publication, changing billing/cap semantics, arbitrary source refactors, automatic mutation of approved templates. Background engine001 remains on published5.13.8 and producer-disabled.

## Requirements

Use existing publication operation/target snapshots, SHARED slot version CAS and audit in bounded serializable transactions; no new setting/table. Preview exact affected active Meta stage/offer/locale/shop slots and selected common revision. Every required replacement must have provider APPROVED/content-equivalent registration and matching canonical commonRef; stale/missing locale, approval, source, active-pointer or current slot mismatch refuses activation. Do not claim cross-shop atomicity from existing per-shop operations/global SHARED slot. Before implementing, return any actual inability to coordinate global common pointer with target assignments safely. Required behavior is one reviewed common revision across newly sent Meta/AI/HUMAN, not silent mixed versions.

Source/approval workflows must keep existing Meta snapshots immutable, clone/register/review replacements; live provider submission/activation remains root-owned after concrete review. Background consumer must be deployed before selecting new projections. Existing approved outreach outside customer window remains a template send only, no new product freeform tail. Runtime mismatches fail closed before provider. Preserve compatible legacy frozen messages. Test concurrent Admin/slot/provider drift, all-or-no-switch per intended transaction boundary, idempotent replay and audit. Stop with explicit architectural gap if broader schema/contract change is necessary.

## Work Items

- [ ] Complete assigned bounded capability only.
- [ ] Prove compatibility and meaningful negative/failure behavior.
- [ ] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-ADMIN-001, ARCH-075-BACKGROUND-002

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [ ] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [ ] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [ ] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [ ] Actual PostgreSQL coordinated activation, stale source/slot/approval/locale and concurrent conflict/replay tests.
- [ ] Declared relevant tests/types/lint/build and exact-head CI; no live registration mutation.

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
