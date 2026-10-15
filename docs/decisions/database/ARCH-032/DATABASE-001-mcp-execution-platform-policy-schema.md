---
id: ARCH-032-DATABASE-001
architecture_id: ARCH-032
title: Persist required environment-scoped MCP execution policy
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-032-ADMIN-001
- ARCH-032-MCP-015
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-DATABASE-001 — Persist required environment-scoped MCP execution policy

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Introduce the canonical environment-scoped, mandatory MCP execution-policy record and forward-only migration.

## Context

The standalone MCP runtime currently hardcodes TOOL_DEADLINE_MS=10000, MAX_PROVIDER_REQUESTS=12 and MAX_RESPONSE_BYTES=256 KiB. The user requires database-backed platform policy without execution fallbacks. This task owns persistence, not runtime enforcement.

## Scope

Add a Prisma model, unique environment identity, version/concurrency field, positive bounded numeric fields for toolDeadlineMs, providerResponseTimeoutMs, maxProviderRequests and maxResponseBytes; enforce provider timeout not exceeding the total deadline. Supply a forward-only migration. No automatic default-row insertion or policy backfill. Cover environment isolation and read/update patterns. Use canonical existing Commerce environment labels, not a competing environment enum.

## Out of Scope

Do not add MCP runtime calls, Admin UI, Shared incident runtime or policy default constants. No schema edits in implementation repositories, no _index.md changes.

## Requirements

A missing row is intentionally possible and must remain distinguishable from a valid row. Reject null/nonpositive/overflow values at database and/or Prisma integrity boundary as appropriate, with exact declared numeric caps justified by the actual runtime and persisted in the task report. Model should allow atomic versioned Admin updates.

## Work Items

- [ ] Inspect existing database policy models and environment enums.
- [ ] Implement Prisma schema and forward-only migration.
- [ ] Implement fresh and upgrade disposable PostgreSQL tests, including no default row and concurrency/constraint checks.

## Interfaces / Contracts

Canonical Prisma policy model, one record per Commerce environment. Four mandatory positive fields: toolDeadlineMs, providerResponseTimeoutMs, maxProviderRequests and maxResponseBytes. No secrets or shop-specific credentials.

## Dependencies

None

## Enables

- ARCH-032-ADMIN-001
- ARCH-032-MCP-015

## Acceptance Criteria

- [ ] Fresh migration succeeds on empty PostgreSQL and creates no policy implicitly.
- [ ] Upgrade migration preserves unrelated tables and existing policy data.
- [ ] Missing or invalid values cannot be mistaken for a valid policy.
- [ ] Unique environment and version-based update semantics are test-covered.

## Validation

- [ ] npm run validate (if declared by repository)
- [ ] Disposable PostgreSQL fresh and upgrade policy tests
- [ ] git apply --check --whitespace=error-all; git diff --check

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This is a **portable task definition**, `defined but not materialised`: no branches, commits, pushes, claims or worktrees have been created by this artifact. Run `/moda_developer_create ARCH-032-DATABASE-001` after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

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
None recorded

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

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `ready`. Active `depends_on`: None. Active `enables`: `ARCH-032-ADMIN-001`, `ARCH-032-MCP-015`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
