---
id: ARCH-033-BACKGROUND-001
architecture_id: ARCH-033
title: Adopt generic incidents for one actionable worker failure
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-033-DATABASE-001
  - ARCH-033-SHARED-003
enables: []
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-033-BACKGROUND-001 — Adopt generic incidents for one actionable worker failure

## Architecture
ARCH-033. Parent: `docs/architecture/ARCH-033-generic-internal-operational-incidents.md`. Coordinator: `moda_architect`.

## Objective
Adopt generic incidents for one actionable worker failure.

## Context
This is one bounded repository-owned step in a generic, internal-only platform incident system. MCP-014 is an existing reference behaviour, not permission to broaden service failure classification.

## Scope
Identify one existing objectively actionable Background failure (e.g. permanently revoked provider grant), prove it is not transient retries/input error, and call the published Shared reporter via Background persistence adapter. Define bounded grouping and occurrence identity, tenant/environment isolation, original failure preservation and no notification flood. Add unit and disposable PostgreSQL integration tests; do not report all job failures or change business retry decisions.

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
- ARCH-033-DATABASE-001
- ARCH-033-SHARED-003

## Enables
- ARCH-033-SYSTEM-TEST-001

## Acceptance Criteria
- [ ] The Scope is implemented without cross-repository ownership violations.
- [ ] Internal-only security, sensitive-data exclusion and environment isolation are demonstrated.
- [ ] Relevant idempotency/concurrency/failure-isolation behaviour is covered and all required checks pass.
- [ ] Existing MCP-014 behaviour and historical records are not silently lost or duplicated.

## Validation
- [ ] Run relevant repository-defined focused tests, typecheck/lint/build where supported and required.
- [ ] Run disposable PostgreSQL fresh/upgrade/integration scenarios when database behaviour is involved.
- [ ] Report exact unrun checks instead of claiming PASS.

## Stop Condition
When Work Items, Acceptance Criteria and Validation are satisfied, submit Completion Report and set `status: review`; STOP. Developer completion is explicit after architect acceptance, not automatic.

## Implementation Notes
Portable definition: `defined but not materialised`. Do not claim task branches, worktrees, pushes or commits exist. `/moda_developer_create ARCH-033-BACKGROUND-001` must materialise and claim it in the developer's real workspace. Do not touch any `_index.md` pending explicit user authorisation.

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

## 2026-10-16 — Supersession Decision

**Status: Superseded by explicit developer decision.** ARCH-033 does not require a Background producer pilot. No Background implementation is claimed, and no successor task is invented. The task is not a prerequisite for ARCH-033-SYSTEM-TEST-001, which will validate the MCP → generic incident → Admin path. Historical task content and attempt 0 are retained for traceability.
