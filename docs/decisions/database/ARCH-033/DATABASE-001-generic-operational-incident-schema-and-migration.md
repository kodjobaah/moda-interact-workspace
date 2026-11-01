---
id: ARCH-033-DATABASE-001
architecture_id: ARCH-033
title: Generic operational incident schema and migration
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-033-SHARED-002
  - ARCH-033-ADMIN-001
  - ARCH-033-ADMIN-002
  - ARCH-033-MCP-001
  - ARCH-033-BACKGROUND-001
created: 2026-10-11
updated: 2026-10-16
---

# ARCH-033-DATABASE-001 — Generic operational incident schema and migration

## Architecture
ARCH-033. Parent: `docs/architecture/ARCH-033-generic-internal-operational-incidents.md`. Coordinator: `moda_architect`.

## Objective
Generic operational incident schema and migration.

## Context
This is one bounded repository-owned step in a generic, internal-only platform incident system. MCP-014 is an existing reference behaviour, not permission to broaden service failure classification.

## Scope
Create support-scoped generic incident and append-only event Prisma models, ownership attribution, FK/index/unique/transition constraints and safe upgrade migration. For the approved pre-production breaking rollout, legacy MCP incident/event tables and their records may be dropped without backfill. Preserve unrelated MerchantSupportMessage and billing data; do not drop unrelated support tables. Test disposable PostgreSQL fresh and upgrade migrations, repeat occurrence uniqueness, concurrent ownership, resolution race, explicit legacy MCP table cleanup, unrelated data preservation and rollback constraints.

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
None

## Enables
- ARCH-033-SHARED-002
- ARCH-033-ADMIN-001
- ARCH-033-ADMIN-002
- ARCH-033-MCP-001
- ARCH-033-BACKGROUND-001

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
Portable definition: `defined but not materialised`. Do not claim task branches, worktrees, pushes or commits exist. `/moda_developer_create ARCH-033-DATABASE-001` must materialise and claim it in the developer's real workspace. Do not touch any `_index.md` pending explicit user authorisation.

## Completion Report
### Status
Reconciled Complete by explicit developer decision on 2026-10-16; historical `attempt: 0` preserved because no task execution was claimed.

### Files Changed
Existing implementation source inspected:
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261011160000_arch033_generic_operational_incidents/migration.sql`
- `moda-interact-database/prisma/migrations/20261011210000_arch033_drop_legacy_mcp_operational_incidents/migration.sql`
- `moda-interact-database/scripts/test-arch033-operational-incidents-postgres.mjs`

This reconciliation changes documentation only.

### Work Completed
The new generic tables, uniqueness, ownership, event audit protections and disposable-PostgreSQL test harness exist. Pre-production breaking cleanup of old MCP incident/event tables is expressly approved; no historical MCP incident backfill is required.

### Validation Results
Tests were inspected as source but not executed in this reconciliation. No fresh source tests, migrations, deployment checks or worktree/CI checks are claimed as PASS.

### Deviations
None

### Assumptions
None beyond parent architecture

### Unresolved Issues
Tests were inspected as source but not executed in this reconciliation.

### Architectural Concerns
None recorded

## Architect Review
### Review Status
Accepted — developer-authorised code-based reconciliation (not a retrospective implementation-agent sign-off).

### Review Notes
2026-10-16: Reviewed the uploaded source snapshot and applicable task definition. The new generic tables, uniqueness, ownership, event audit protections and disposable-PostgreSQL test harness exist. Pre-production breaking cleanup of old MCP incident/event tables is expressly approved; no historical MCP incident backfill is required. Developer explicitly authorised marking implemented ARCH-033 tasks Complete. Historical attempt and worktree evidence are not fabricated.

### Reviewed Files
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261011160000_arch033_generic_operational_incidents/migration.sql`
- `moda-interact-database/prisma/migrations/20261011210000_arch033_drop_legacy_mcp_operational_incidents/migration.sql`
- `moda-interact-database/scripts/test-arch033-operational-incidents-postgres.mjs`

### Validation Reviewed
Tests were inspected as source but not executed in this reconciliation.

### Architecture Conformance
Accepted for the revised pre-production scope. Do not infer completed ARCH-033 terminal black-box certification.

### Follow-up
ARCH-033-SYSTEM-TEST-001 remains a separate terminal validation task. Tests were inspected as source but not executed in this reconciliation.

## 2026-10-16 — Authoritative Reconciliation

The active task contract above supersedes older draft language about preserving MCP-specific incident history, mandatory legacy support projections, unmaterialised portable task definitions, or unperformed validation. Status `complete` is a **developer-requested, source-based closure**; the immutable task `attempt: 0` is retained. No separate runtime test execution, deployment verification, PR merge, Git commit or task worktree creation is claimed here.
