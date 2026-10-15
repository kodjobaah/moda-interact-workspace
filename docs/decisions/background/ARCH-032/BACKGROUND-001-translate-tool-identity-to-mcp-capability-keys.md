---
id: ARCH-032-BACKGROUND-001
architecture_id: ARCH-032
title: Translate authorised runner tools into MCP capability keys
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-019
- ARCH-032-MCP-020
enables:
- ARCH-032-GATEWAY-002
- ARCH-032-SYSTEM-TEST-002
created: '2026-10-15'
updated: '2026-10-15'
---

# ARCH-032-BACKGROUND-001 — Translate authorised runner tools into MCP capability keys

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`. Coordinator: `moda_architect`.

## Objective

Make Background call the eligible published MCP capability key while retaining Shared runner descriptor identity and per-conversation grant protections.

## Context

`moda-interact-background/src/commerce/host.ts` currently matches `tools/list` names to `toolDescriptor.name` and invokes the underlying descriptor name. Standalone MCP advertises `CommerceCapability.key`, which may differ, including when several capability keys reference a single published tool revision.

## Scope

- Build a deterministic grant-checked mapping from published manifest capabilities and current MCP `tools/list` to transport capability keys.
- Retain Shared runner tool descriptors, exact granted revisions and selected capability keys; reject absent, revoked, wrong-tenant or ambiguous identities.
- Use the mapped capability key for `tools/call`, parse only validated canonical structured results; preserve conversation locking and existing queue semantics.

## Out of Scope

- No MCP service changes, Commerce Live Test changes or queue contract redesign.
- No weakening conversation grants, eligibility, revision pins or fail-closed behaviour.

## Requirements

- Mapping cannot use underlying descriptor name alone as the MCP transport identity.
- Multiple capability keys referencing one tool must be deterministic and cannot inflate grants.
- Reject unlisted capability or changed release before execution.

## Work Items

- [ ] Inspect current host runner callback and conversation grants.
- [ ] Implement capability-key translation with exact grant checks.
- [ ] Add one-capability, multi-capability, revoked, empty, wrong-shop and error-result focused tests.

## Interfaces / Contracts

- Shared `CommerceManifestSchema`, `CommerceToolResultSchema`, existing grant descriptors.
- MCP `tools/list` exposes capability keys; `tools/call` accepts a key.

## Dependencies

- `ARCH-032-MCP-019`
- `ARCH-032-MCP-020`

## Enables

Calculated from `depends_on` in the 2026-10-15 reconciliation metadata; dependent work is never automatically claimed.

## Acceptance Criteria

- [ ] Eligible tool execution succeeds when names differ.
- [ ] No revoked/cross-tenant/ungranted tool execution.
- [ ] Shared descriptor remains the published runner identity.

## Validation

- [ ] Relevant Background commerce unit tests
- [ ] npm run typecheck if declared
- [ ] required lint/build commands from Background package.json
- [ ] git diff --check

## Stop Condition

Finish the bounded task, record the evidence in the Completion Report, move to `review`, return to `moda_architect`, and STOP. Repository agents do not close their own tasks. For developer-completion tasks, explicit developer completion remains required after acceptance.

## Implementation Notes

This task changes only Background-owned code. Reuse published Shared contracts; require MCP-019 and MCP-020 architect-accepted completion.

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

**Separate correction:** do not claim this task until every listed dependency has an accepted Complete decision. It is not permission to alter any sibling repository. Earlier `depends_on`: `ARCH-032-MCP-019`, `ARCH-032-MCP-020`. Earlier `enables`: None.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-019`, `ARCH-032-MCP-020`. Active `enables`: `ARCH-032-GATEWAY-002`, `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
