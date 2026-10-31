---
id: ARCH-054-SHARED-002
architecture_id: ARCH-054
title: Publish accepted ARCH-054 v1 delay contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-10-31T20:28:56Z
attempt: 1
depends_on:
  - ARCH-054-SHARED-001
enables:
  - ARCH-054-API-001
  - ARCH-054-SHOPIFY-001
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-SHARED-002: Publish accepted ARCH-054 v1 delay contract


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


## Objective

Publish an accepted build of `@modainteract/moda-interact-shared/ai-response-delay` so consumers use one package version.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Only Shared package version/release metadata, approved lockfile edits required for publishing, and release evidence. No implementation code changes.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Only proceed after SHARED-001 is architect-accepted Complete. Choose next actually available registry version greater than pinned `3.0.0`, without overwriting an existing tag. Run approved publishing mechanism and confirm exact version and `./ai-response-delay` import from the registry. Record the immutable version used by API/Shopify and publish commit evidence. No tests/build/lint reruns of already accepted implementation.


## Work Items

- [ ] Verify accepted task and release version; publish; record package/version/import proof. Stop before editing consumer repositories.


## Interfaces / Contracts

Published npm subpath `@modainteract/moda-interact-shared/ai-response-delay`; contains `MerchantAiResponseDelayReadV1Schema`, `MerchantAiResponseDelayWriteV1Schema`, `AiResponseDelayMinutesSchema` and inferred types.


## Dependencies

- ARCH-054-SHARED-001


## Enables

- ARCH-054-API-001
- ARCH-054-SHOPIFY-001


## Acceptance Criteria

- [ ] Correct approved version published and resolvable; no implementation source edits or consumer changes; full error and publication evidence recorded.


## Validation

- [ ] Registry visibility check and declared package-version check only; no unit test/build/lint in publication task.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Implement only the identified repository-owned changes; preserve original provider/SDK errors in shared structured logs and rethrow failures to the owning retry/admission boundary.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

None

### Worktree and Git Evidence

Not materialised; implementing agent must record launcher-prepared dedicated parent/implementation worktree paths, start-of-attempt sync, branch SHAs, submodule pins and cleanup.


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

None
