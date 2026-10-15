---
id: ARCH-032-COMMERCE-006
architecture_id: ARCH-032
title: Reconcile Commerce Live Test with the standalone MCP contract
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-COMMERCE-005
- ARCH-032-MCP-019
- ARCH-032-MCP-020
enables:
- ARCH-032-GATEWAY-002
- ARCH-032-SYSTEM-TEST-002
created: '2026-10-15'
updated: '2026-10-15'
---

# ARCH-032-COMMERCE-006 — Reconcile Commerce Live Test with the standalone MCP contract

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`. Coordinator: `moda_architect`.

## Objective

Make published Commerce Studio Live Test discover/call capability-key MCP tools using an SDK-compatible initialized private client and validate structured results.

## Context

The existing `remote-studio-tool-client.ts` sends raw JSON-RPC `tools/list`/`tools/call` without a demonstrated MCP initialize sequence, compares tool names to `toolDescriptor.name`, and requires structured results. Local Preview real-provider and Fixture paths must remain unchanged.

## Scope

- Use a supported protocol handshake and bounded request transport for live published tools.
- Derive the eligible MCP capability-key transport identity from the shop published manifest and match published descriptors without weakening shop/scope checks.
- Preserve deterministic behaviour when capabilities share an underlying tool; fail closed for ambiguous, unpublished, revoked or cross-shop keys.
- Validate `structuredContent` against Shared schema; add protocol and mode-isolation tests.

## Out of Scope

- No reintroduction of embedded MCP server.
- No replacing Local Preview real provider execution with remote preview references.
- No draft/fixture publication into MCP `tools/list` or Browser-accessible MCP credentials.

## Requirements

- Local Preview, Live Test and Fixture remain distinct.
- Use private trusted shop context and no insecure fallback on MCP failure.

## Work Items

- [ ] Inspect existing Studio tool-client selection.
- [ ] Implement MCP-protocol compatibility and capability mapping.
- [ ] Test successful published call, zero tools, shared tool revisions, denied shop/release, MCP outage and unchanged other modes.

## Interfaces / Contracts

- Shared runner tool descriptor versus MCP capability-key name.
- `CommerceToolResultSchema`; private MCP SDK protocol.

## Dependencies

- `ARCH-032-COMMERCE-005`
- `ARCH-032-MCP-019`
- `ARCH-032-MCP-020`

## Enables

Calculated from `depends_on` in the 2026-10-15 reconciliation metadata; dependent work is never automatically claimed.

## Acceptance Criteria

- [ ] Live Test reaches published MCP and executes with validated result.
- [ ] No raw JSON-RPC shortcut relying on uninitialized server state.
- [ ] No regressions to Local Preview real requests or Fixture mode.

## Validation

- [ ] Relevant Commerce focused tests
- [ ] Typecheck, lint, build and full test suite per task validation
- [ ] Private MCP SDK-compatible integration test
- [ ] git diff --check

## Stop Condition

Finish the bounded task, record the evidence in the Completion Report, move to `review`, return to `moda_architect`, and STOP. Repository agents do not close their own tasks. For developer-completion tasks, explicit developer completion remains required after acceptance.

## Implementation Notes

Historical COMMERCE-001..005 complete metadata is retained as administrative closure, not treated as passing full-suite certification. This is new bounded correction work.

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

**Separate correction:** do not claim this task until every listed dependency has an accepted Complete decision. It is not permission to alter any sibling repository. Earlier `depends_on`: `ARCH-032-COMMERCE-005`, `ARCH-032-MCP-019`, `ARCH-032-MCP-020`. Earlier `enables`: None.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-COMMERCE-005`, `ARCH-032-MCP-019`, `ARCH-032-MCP-020`. Active `enables`: `ARCH-032-GATEWAY-002`, `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
