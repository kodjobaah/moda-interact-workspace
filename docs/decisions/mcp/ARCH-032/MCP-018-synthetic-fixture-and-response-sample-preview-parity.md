---
id: ARCH-032-MCP-018
architecture_id: ARCH-032
title: Support Studio single-tool synthetic fixture and External HTTP response-sample tests through standalone MCP without live provider calls
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 62
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-MCP-018 — Support Studio single-tool synthetic fixture and External HTTP response-sample tests through standalone MCP without live provider calls

## Execution hold — 2026-10-12

**DO NOT CLAIM OR IMPLEMENT IN THIS PHASE.** Deferred: standalone MCP synthetic fixture / response-sample execution is not part of this phase. Earlier remote-first descriptions and dependencies are superseded by ARCH-032-COMMERCE-001 through COMMERCE-005. Reassess under a new approved future plan before unblocking.

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Support Studio single-tool synthetic fixture and External HTTP response-sample tests through standalone MCP without live provider calls.

## Context

Current Commerce createPreviewToolExecutor uses synthetic Shopify fixtures and injected External HTTP responses, unlike selected-shop conversation execution. Removing Commerce local execution before replacing these workflows would regress the Tool Editor.

## Scope

Extend the isolated server-resolved preview reference to specify fixture-only execution inputs. Adapt existing MCP input validation, pinned definition, policy-operation and rendering/transform implementations to accept a trusted test-data provider port; never make a real outbound provider request in fixture mode. Process bounded supplied External HTTP response samples through the canonical renderer. Apply mandatory MCP execution platform policy and preserve cancellation. No separate Commerce execution engine.

## Out of Scope

No browser-supplied direct executable definitions, live Shopify/Woo/HTTP calls from fixture mode, fake publication grants, or changes to published tools/list.

## Requirements

Fixture payloads must come exclusively from an authenticated, immutable server-side snapshot with source/trust classification. Test mode cannot be inferred from model arguments; do not convert synthetic data into real provider credentials or network destinations.

## Work Items

- [ ] Inspect existing Commerce fixture and response-sample tests for required parity.
- [ ] Implement MCP fixture adapter using the shared published preview contract and existing execution/render pipeline.
- [ ] Prove deterministic results, no provider network calls, invalid payload refusal, isolation and cancellation.

## Interfaces / Contracts

SHARED-002 fixture payload and MCP-017 isolated preview protocol; normal background published calls unchanged.

## Dependencies

- ARCH-032-MCP-017
- ARCH-032-SHARED-002

## Enables

- ARCH-032-COMMERCE-001

## Acceptance Criteria

- [ ] Individual saved-tool tests and response-sample tests have remote equivalents.
- [ ] Fixture mode never accesses live providers or bypasses result validation.
- [ ] No duplicate Commerce tool execution implementation required.

## Validation

- [ ] Focused fixture/HTTP sample parity tests, npm run typecheck, npm test, npm run build and git diff --check.

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This task is **defined but not materialised**: no branches, commits, pushes, claims or worktrees were created by this artifact. Run `/moda_developer_create ARCH-032-MCP-018` only after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the developer explicitly closes architecture reconciliation.

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

**Superseded, not completed:** Remote synthetic-fixture/reference parity is replaced by Commerce-local Fixture mode. This task must not be executed or used to promote a dependant. Historical original references are preserved below. Historical metadata before reconciliation: `depends_on`: `ARCH-032-MCP-017`, `ARCH-032-SHARED-002`; `enables`: `ARCH-032-COMMERCE-001`.

Active `status`: `superseded`. Active `depends_on`: None. Active `enables`: None.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
