---
id: ARCH-032-MCP-020
architecture_id: ARCH-032
title: Return canonical structured Commerce results from MCP tools/call
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 18
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-019
enables:
- ARCH-032-BACKGROUND-001
- ARCH-032-COMMERCE-006
- ARCH-032-SYSTEM-TEST-002
created: '2026-10-15'
updated: '2026-10-15'
---

# ARCH-032-MCP-020 — Return canonical structured Commerce results from MCP tools/call

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`. Coordinator: `moda_architect`.

## Objective

Return the validated `CommerceToolResult` through SDK `structuredContent` while preserving existing content, error semantics and tool identity.

## Context

The snapshot MCP `src/mcp/registration.ts` only sends JSON text content; Background and Commerce Live Test read `structuredContent` using published `CommerceToolResultSchema`. This independent MCP provider defect follows manifest registration, not system-test changes.

## Scope

- Add canonical `structuredContent` to MCP tool call responses after validating against published Shared commerce schema.
- Preserve text `content` for legacy consumers and the exact `isError` relation to the result status.
- Cover success, denial, provider errors, schema mismatch and zero-tool negative cases with SDK tests.

## Out of Scope

- No tool alias changes; no Background/Commerce source changes.
- No reinterpretation of errors, broad JSON text fallback or local schema copies.

## Requirements

- MCP protocol must expose valid structured JSON object without leaking raw failures.
- Error handling remains fail-closed and bounded.

## Work Items

- [ ] Inspect current SDK response type and runner result shape.
- [ ] Add schema-validated structured result envelope.
- [ ] Extend SDK and focused unit tests.

## Interfaces / Contracts

- `@modainteract/moda-interact-shared/commerce` `CommerceToolResultSchema` (published).
- `tools/call` returns `structuredContent`, `content`, `isError`.

## Dependencies

- `ARCH-032-MCP-019`

## Enables

Calculated from `depends_on` in the 2026-10-15 reconciliation metadata; dependent work is never automatically claimed.

## Acceptance Criteria

- [ ] Success and error results parse as published `CommerceToolResult`.
- [ ] Structured and legacy text representations agree; errors never imply success.
- [ ] No change to MCP advertised capability-key transport identity.

## Validation

- [ ] npm run typecheck
- [ ] npm run lint
- [ ] focused MCP tools/call SDK tests
- [ ] npm test
- [ ] npm run build

## Stop Condition

Finish the bounded task, record the evidence in the Completion Report, move to `review`, return to `moda_architect`, and STOP. Repository agents do not close their own tasks. For developer-completion tasks, explicit developer completion remains required after acceptance.

## Implementation Notes

Do not alter MCP-019 resource contract or patch system-test fixtures. Accept MCP-019 first.

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

**Separate correction:** do not claim this task until every listed dependency has an accepted Complete decision. It is not permission to alter any sibling repository. Earlier `depends_on`: `ARCH-032-MCP-019`. Earlier `enables`: None.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-019`. Active `enables`: `ARCH-032-BACKGROUND-001`, `ARCH-032-COMMERCE-006`, `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
