---
id: ARCH-032-MCP-002
architecture_id: ARCH-032
title: Reconcile standalone MCP protocol/OpenAPI extraction evidence
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 2
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-001
enables:
- ARCH-032-MCP-003
created: '2026-10-15'
updated: '2026-10-15'
---

# ARCH-032-MCP-002 — Reconcile standalone MCP protocol/OpenAPI extraction evidence

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`. Coordinator: `moda_architect`.

## Objective

Recover or reproduce verifiable acceptance evidence for the historical standalone MCP transport and OpenAPI boundary.

## Context

The MCP README documents MCP-002 transport/OpenAPI implementation, and MCP-003 depends on MCP-002. The original task file is absent from the uploaded workspace. This is an explicit provenance gate, not a claim of historical acceptance or permission for opportunistic reimplementation.

## Scope

- Inspect the existing `src/mcp/` protocol and `GET /openapi.json` code and associated tests.
- Recover the original task file, relevant worktree commits, test/validation and architect/developer completion decision if available.
- If evidence cannot be recovered, scope a narrowly bounded verification of existing MCP protocol, OpenAPI, private ingress, zero-tools and fail-closed behaviour; return any required source fix to the architect.

## Out of Scope

- No automatic code rewrite; no published-grant or application-side implementation.
- No activation of production routing or inference of successful historical tests.

## Requirements

- Historical readiness/acceptance cannot be inferred from present source files.
- Retain service-private authentication and negative/malformed request checks.

## Work Items

- [ ] Record source provenance and exact historical claims.
- [ ] Run or inspect bounded transport, OpenAPI and SDK initialization evidence.
- [ ] Send task back for review with explicit provenance gaps rather than inventing historical commits.

## Interfaces / Contracts

- Standalone SDK MCP transport; OpenAPI 3.1 HTTP description.
- Does not own Shopify/Woo provider connections or database migrations.

## Dependencies

- `ARCH-032-MCP-001`

## Enables

Calculated from `depends_on` in the 2026-10-15 reconciliation metadata; dependent work is never automatically claimed.

## Acceptance Criteria

- [ ] Provenance and present-state tests demonstrate the protocol boundary.
- [ ] No unverified `complete` status or release approval recorded.

## Validation

- [ ] MCP focused protocol/unit tests and typecheck/build if source validation is needed.
- [ ] Task-worktree/Git evidence review.

## Stop Condition

Finish the bounded task, record the evidence in the Completion Report, move to `review`, return to `moda_architect`, and STOP. Repository agents do not close their own tasks. For developer-completion tasks, explicit developer completion remains required after acceptance.

## Implementation Notes

Blocked until missing historical task evidence is recovered or a deliberate verification path is approved. Preserve older task IDs; no blanket rework of functioning source.

## Completion Report

### Status

Not Started — portable task definition; not materialised in developer worktrees.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; do not infer passing tests or accepted implementation from this definition.

### Deviations

None.

### Assumptions

None beyond the inspected 2026-10-15 snapshot.

### Unresolved Issues

Dependent implementation tasks and canonical task-worktree evidence remain unverified.

### Architectural Concerns

No new cross-repository ownership is granted by this definition.

## Architect Review

### Review Status

Pending.

### Review Notes

No independent implementation review or acceptance recorded by this definition.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation and evidence review.

### Follow-up

Only through the canonical task lifecycle.

## 2026-10-15 — Architect dependency reconciliation

**Blocked provenance recovery:** this recovered task identifier is a documentary/evidence gate. Its creation does not establish historical implementation acceptance. An architect/developer review must reconcile the missing original task before promotion. Earlier `depends_on`: `ARCH-032-MCP-001`. Earlier `enables`: None.

Active `status`: `blocked`. Active `depends_on`: `ARCH-032-MCP-001`. Active `enables`: `ARCH-032-MCP-003`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** MCP transport/request registration, HTTP ingress, OpenAPI specification, and protocol tests are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/mcp/registration.ts`
- `src/mcp/node-handler.ts`
- `src/openapi/spec.ts`
- `tests/unit/openapi/spec.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
