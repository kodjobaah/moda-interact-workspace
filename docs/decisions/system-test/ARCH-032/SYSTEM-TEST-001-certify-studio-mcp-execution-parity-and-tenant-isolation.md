---
id: ARCH-032-SYSTEM-TEST-001
architecture_id: ARCH-032
title: Certify Commerce Studio preview parity against standalone MCP before deleting embedded execution code
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-SYSTEM-TEST-001 — Certify Commerce Studio preview parity against standalone MCP before deleting embedded execution code

## Historical execution hold — 2026-10-12

**DO NOT CLAIM OR IMPLEMENT IN THIS PHASE.** Deferred: remote Studio/Background execution parity follows a future architecture decision, not mock-first removal. Earlier remote-first descriptions and dependencies are superseded by ARCH-032-COMMERCE-001 through COMMERCE-005. Reassess under a new approved future plan before unblocking.

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Certify Commerce Studio preview parity against standalone MCP before deleting embedded execution code.

## Context

Commerce Studio selected-feature conversations use Shared runCommerceTurn and can select inactive published features. Individual tool-tests use drafts, fixtures and response samples. Background must never discover or invoke these isolated previews.

## Scope

Black-box, disposable test-environment evidence for Studio published-active, published-inactive and draft selected-feature paths; single tool fixture and External HTTP samples; Shared runner parity; owner/shop/environment isolation; revision freezing; closed/revoked reference; MCP outage fails closed; platform policy missing/invalid incidents via ARCH-033; normal Background tools/list unchanged. Confirm remote execution provider audit and absence of Commerce-local provider calls. Retain reproducible evidence paths and fixtures.

## Out of Scope

No implementation source changes; do not require real production credentials or treat unverified Render claims as proof. No `_index.md` edits.

## Requirements

Require real Redis, PostgreSQL and MCP test boundaries where specified; do not certify by mocks alone. Ensure no untrusted preview definition is executable through normal Background capability discovery.

## Work Items

- [ ] Create black-box fixtures/clients for normal published and isolated preview paths.
- [ ] Compare tool results, failure codes and side-effect boundaries across Studio and Background.
- [ ] Capture evidence for missing-policy incident, MCP outage, tenant isolation, fixture no-network and preview close.

## Interfaces / Contracts

Existing private MCP JSON-RPC with SHARED-002 preview ref; system tests assert behavior, not direct implementation imports.

## Dependencies

- ARCH-032-COMMERCE-001
- ARCH-032-MCP-016

## Enables

- ARCH-032-COMMERCE-002

## Acceptance Criteria

- [ ] Selected-feature conversation and tool-editor test UX retain parity.
- [ ] Background cannot list/call draft or inactive preview capabilities.
- [ ] Fail-closed and generic incident evidence recorded.

## Validation

- [ ] System-test focused and integrated suite with retained evidence, git diff --check.

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This task is **defined but not materialised**: no branches, commits, pushes, claims or worktrees were created by this artifact. Run `/moda_developer_create ARCH-032-SYSTEM-TEST-001` only after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the developer explicitly closes architecture reconciliation.

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

**Superseded, not completed:** Legacy frozen remote-preview system test is replaced by terminal SYSTEM-TEST-002 for the approved three-mode design. This task must not be executed or used to promote a dependant. Historical original references are preserved below. Historical metadata before reconciliation: `depends_on`: `ARCH-032-COMMERCE-001`, `ARCH-032-MCP-016`; `enables`: `ARCH-032-COMMERCE-002`.

Active `status`: `superseded`. Active `depends_on`: None. Active `enables`: None.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
