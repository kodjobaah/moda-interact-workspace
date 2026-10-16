---
id: ARCH-033-ADMIN-001
architecture_id: ARCH-033
title: Internal operational incident list and investigation detail
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-033-DATABASE-001
  - ARCH-033-SHARED-003
enables:
  - ARCH-033-ADMIN-002
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-033-ADMIN-001 — Internal operational incident list and investigation detail

## Architecture
ARCH-033. Parent: `docs/architecture/ARCH-033-generic-internal-operational-incidents.md`. Coordinator: `moda_architect`.

## Objective
Internal operational incident list and investigation detail.

## Context
This is one bounded repository-owned step in a generic, internal-only platform incident system. MCP-014 is an existing reference behaviour, not permission to broaden service failure classification.

## Scope
Replace MCP-only incident viewing with an authenticated platform-admin-only generic incident list/detail, filters by source/status/severity/environment, occurrence history, actor attribution, safe correlation identifiers and optional support-thread link. Reuse existing Admin auth/role checks; no merchant-facing endpoint, no support ownership conflation. Display current generic incident history; old MCP-specific incident history need not be migrated under the developer-approved pre-production breaking rollout. Add query, projection and access-control tests.

## Out of Scope
Other repositories' implementation, merchant-facing incident access, a new deployable incident service, unrelated refactors, and any `docs/decisions/**/_index.md` edit.

## Requirements
Preserve platform-admin-only access, safe bounded diagnostics, environment/tenant isolation, auditability, and deterministic retries. The approved pre-production breaking rollout permits removal of legacy MCP incident/event tables without migrating their records. Only explicitly configured producer policies may emit optional merchant-support SYSTEM notifications. Follow repository ownership and existing task launcher/worktree policy.

## Work Items
- [x] Inspect parent architecture, dependencies, ownership rules and existing source in the uploaded snapshot.
- [x] Locate the already implemented bounded capability and its existing focused tests or publication evidence.
- [x] Record available source evidence and unresolved validation limits without inventing execution results.

## Interfaces / Contracts
Canonical package: `@modainteract/moda-interact-shared/incidents` (proposed, created by SHARED-001/002 and published by SHARED-003). Generic `OperationalIncident` and `OperationalIncidentEvent` schema owned by DATABASE-001. Service-local adapters use an injected transaction port; only producer services classify actionable failures.

## Dependencies
- ARCH-033-DATABASE-001
- ARCH-033-SHARED-003

## Enables
- ARCH-033-ADMIN-002

## Acceptance Criteria
- [x] The agreed, revised Scope is present in its owning repository (source-based review).
- [x] Existing source paths implement the relevant security, safe-data and environment contracts; dynamic tests were not rerun.
- [x] Existing implementation and focused coverage were inspected; no fresh test PASS claim is made in this code-based reconciliation.
- [ ] The development-only breaking transition to generic incidents is explicit; unrelated merchant support and billing data remain preserved. The legacy MCP incident/event history need not be migrated.

## Validation
- [x] Existing test/build definitions inspected; fresh execution waived for the developer-directed code-based reconciliation (not reported as passed).
- [x] Applicable PostgreSQL test sources located; execution not rerun during this documentation-only reconciliation.
- [x] Record test-execution limitations in the reconciled Completion Report and Architect Review.

## Stop Condition
When Work Items, Acceptance Criteria and Validation are satisfied, submit Completion Report and set `status: review`; STOP. Developer completion is explicit after architect acceptance, not automatic.

## Implementation Notes
Portable definition: `defined but not materialised`. Do not claim task branches, worktrees, pushes or commits exist. `/moda_developer_create ARCH-033-ADMIN-001` must materialise and claim it in the developer's real workspace. Do not touch any `_index.md` pending explicit user authorisation.

## Completion Report
### Status
Reconciled Complete by explicit developer decision on 2026-10-16; historical `attempt: 0` preserved because no task execution was claimed.

### Files Changed
Existing implementation source inspected:
- `moda-interact-admin/src/app/(protected)/operational-incidents/page.tsx`
- `moda-interact-admin/src/lib/admin/operational-incidents.ts`
- `moda-interact-admin/src/components/admin/sidebar.tsx`

This reconciliation changes documentation only.

### Work Completed
The internal incident list/detail, safe filters and platform-admin access integration are present. It reads the generic incident models, not dropped MCP-specific tables.

### Validation Results
Legacy MCP incident history is intentionally not migrated under the approved development-only breaking rollout; no live tests were rerun. No fresh source tests, migrations, deployment checks or worktree/CI checks are claimed as PASS.

### Deviations
None

### Assumptions
None beyond parent architecture

### Unresolved Issues
Legacy MCP incident history is intentionally not migrated under the approved development-only breaking rollout; no live tests were rerun.

### Architectural Concerns
None recorded

## Architect Review
### Review Status
Accepted — developer-authorised code-based reconciliation (not a retrospective implementation-agent sign-off).

### Review Notes
2026-10-16: Reviewed the uploaded source snapshot and applicable task definition. The internal incident list/detail, safe filters and platform-admin access integration are present. It reads the generic incident models, not dropped MCP-specific tables. Developer explicitly authorised marking implemented ARCH-033 tasks Complete. Historical attempt and worktree evidence are not fabricated.

### Reviewed Files
- `moda-interact-admin/src/app/(protected)/operational-incidents/page.tsx`
- `moda-interact-admin/src/lib/admin/operational-incidents.ts`
- `moda-interact-admin/src/components/admin/sidebar.tsx`

### Validation Reviewed
Legacy MCP incident history is intentionally not migrated under the approved development-only breaking rollout; no live tests were rerun.

### Architecture Conformance
Accepted for the revised pre-production scope. Do not infer completed ARCH-033 terminal black-box certification.

### Follow-up
ARCH-033-SYSTEM-TEST-001 remains a separate terminal validation task. Legacy MCP incident history is intentionally not migrated under the approved development-only breaking rollout; no live tests were rerun.

## 2026-10-16 — Authoritative Reconciliation

The active task contract above supersedes older draft language about preserving MCP-specific incident history, mandatory legacy support projections, unmaterialised portable task definitions, or unperformed validation. Status `complete` is a **developer-requested, source-based closure**; the immutable task `attempt: 0` is retained. No separate runtime test execution, deployment verification, PR merge, Git commit or task worktree creation is claimed here.
