---
id: ARCH-033-SHARED-003
architecture_id: ARCH-033
title: Publish accepted incident package
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-033-SHARED-001
  - ARCH-033-SHARED-002
enables:
  - ARCH-033-MCP-001
  - ARCH-033-BACKGROUND-001
  - ARCH-033-ADMIN-001
  - ARCH-033-ADMIN-002
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-033-SHARED-003 — Publish accepted incident package

## Architecture
ARCH-033. Parent: `docs/architecture/ARCH-033-generic-internal-operational-incidents.md`. Coordinator: `moda_architect`.

## Objective
Publish accepted incident package.

## Context
This is one bounded repository-owned step in a generic, internal-only platform incident system. MCP-014 is an existing reference behaviour, not permission to broaden service failure classification.

## Scope
Publication-only: after architect acceptance of Shared implementation, select and publish the approved package version; verify registry tarball integrity, expected /incidents import and clean-install resolution; record exact version and ensure no runtime implementation changes. Do NOT rerun implementation tests, lint, typecheck or builds as release validation.

## Out of Scope
Other repositories' implementation, merchant-facing incident access, a new deployable incident service, unrelated refactors, and any `docs/decisions/**/_index.md` edit.

## Requirements
Preserve platform-admin-only access, safe bounded diagnostics, environment/tenant isolation, auditability, deterministic retries and existing MCP-014 behaviour. Follow repository ownership and existing task launcher/worktree policy.

## Work Items
- [ ] Inspect parent architecture, dependency tasks, ownership rules and actual affected repository.
- [ ] Implement the bounded Scope and required focused test coverage.
- [ ] Record measured results, deviations and remaining risks in Completion Report.

## Interfaces / Contracts
Canonical package: `@modainteract/moda-interact-shared/incidents` (proposed, created by SHARED-001/002 and published by SHARED-003). Generic `OperationalIncident` and `OperationalIncidentEvent` schema owned by DATABASE-001. Service-local adapters use an injected transaction port; only producer services classify actionable failures.

## Dependencies
- ARCH-033-SHARED-001
- ARCH-033-SHARED-002

## Enables
- ARCH-033-MCP-001
- ARCH-033-BACKGROUND-001
- ARCH-033-ADMIN-001
- ARCH-033-ADMIN-002

## Acceptance Criteria
- [ ] The Scope is implemented without cross-repository ownership violations.
- [ ] Internal-only security, sensitive-data exclusion and environment isolation are demonstrated.
- [ ] Relevant idempotency/concurrency/failure-isolation behaviour is covered and all required checks pass.
- [ ] Existing MCP-014 behaviour and historical records are not silently lost or duplicated.

## Validation
- [ ] Accepted implementation tasks confirmed; correct package/version published and clean-install import verified; no repeat implementation validation.

## Stop Condition
When Work Items, Acceptance Criteria and Validation are satisfied, submit Completion Report and set `status: review`; STOP. Developer completion is explicit after architect acceptance, not automatic.

## Implementation Notes
Portable definition: `defined but not materialised`. Do not claim task branches, worktrees, pushes or commits exist. `/moda_developer_create ARCH-033-SHARED-003` must materialise and claim it in the developer's real workspace. Do not touch any `_index.md` pending explicit user authorisation.

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
None beyond parent architecture

### Unresolved Issues
None recorded

### Architectural Concerns
None recorded

## Architect Review
### Review Status
Pending

### Review Notes
Not reviewed

### Reviewed Files
None

### Validation Reviewed
None

### Architecture Conformance
Pending

### Follow-up
None
