---
id: ARCH-032-DATABASE-002
architecture_id: ARCH-032
title: Persist immutable Studio preview execution snapshots independent of Commerce Redis run state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 44
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-DATABASE-002 — Persist immutable Studio preview execution snapshots independent of Commerce Redis run state

## Execution hold — 2026-10-12

**DO NOT CLAIM OR IMPLEMENT IN THIS PHASE.** Deferred: Commerce preview Redis state stays Commerce-owned; no immutable preview snapshot table in this phase. Earlier remote-first descriptions and dependencies are superseded by ARCH-032-COMMERCE-001 through COMMERCE-005. Reassess under a new approved future plan before unblocking.

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Persist immutable Studio preview execution snapshots independent of Commerce Redis run state.

## Context

Commerce Redis stores an aggregate of conversations, runs and tool tests with 24-hour retention; MCP must not import or decode that private format. An independent, versioned persisted snapshot is required for an opaque reference.

## Scope

Introduce a bounded preview snapshot record indexed by opaque reference, environment, shopId and Studio administrator. Persist a schema-versioned canonical immutable payload/hash and ACTIVE/CLOSED state with explicit close/invalidate timestamps. Use forward-only migration, tenant/environment indexes, immutability semantics and fixed snapshot size limits; no implicit 30-minute expiry. Store no provider access tokens, OAuth credentials, model secrets or unrelated conversations. Choose referential integrity consistent with existing Shop and administrative identity models; document any admin identity boundary.

## Out of Scope

No merchant feature entitlement changes, no activation of drafts, no direct Redis aggregate access, no MCP protocol, no `_index.md` changes.

## Requirements

Readers must be able to verify the snapshot against the Shared contract without trusting client-supplied executable JSON. Snapshot closing is explicit; independent store lifecycle must not silently expire a live Studio test. Guard against mutation of frozen definitions.

## Work Items

- [ ] Inspect canonical schema, Shop linkage and Shared published contract.
- [ ] Add immutable snapshot table, constraints, forward-only migration and explicit CLOSE semantics.
- [ ] Test fresh/upgrade Postgres, shop/environment isolation, immutability and repeated close.

## Interfaces / Contracts

Prisma immutable preview snapshot and reader/writer indexes. Snapshot content adheres to SHARED-002; no duplicate bespoke payload contract.

## Dependencies

- ARCH-032-SHARED-002

## Enables

- ARCH-032-COMMERCE-003
- ARCH-032-MCP-017

## Acceptance Criteria

- [ ] A referenced frozen snapshot cannot be edited after creation.
- [ ] No automatic TTL, implicit draft publication or default execution policy.
- [ ] Fresh/upgrade and cross-shop isolation tests pass.

## Validation

- [ ] Prisma validate/generate, disposable PostgreSQL integration and git diff --check.

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This task is **defined but not materialised**: no branches, commits, pushes, claims or worktrees were created by this artifact. Run `/moda_developer_create ARCH-032-DATABASE-002` only after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the developer explicitly closes architecture reconciliation.

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

**Superseded, not completed:** Immutable remote Studio preview snapshot storage is no longer required by the final Studio execution model. This task must not be executed or used to promote a dependant. Historical original references are preserved below. Historical metadata before reconciliation: `depends_on`: `ARCH-032-SHARED-002`; `enables`: `ARCH-032-COMMERCE-003`, `ARCH-032-MCP-017`.

Active `status`: `superseded`. Active `depends_on`: None. Active `enables`: None.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
