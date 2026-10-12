---
id: ARCH-032-SHARED-001
architecture_id: ARCH-032
title: Define a versioned, bounded Shared contract for immutable Studio execution snapshots and opaque references
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: blocked
priority: 42
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-032-SHARED-002
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-SHARED-001 — Define a versioned, bounded Shared contract for immutable Studio execution snapshots and opaque references

## Execution hold — 2026-10-12

**DO NOT CLAIM OR IMPLEMENT IN THIS PHASE.** Deferred: no cross-service frozen-preview contract is needed for mock-first Commerce removal. Earlier remote-first descriptions and dependencies are superseded by ARCH-032-COMMERCE-001 through COMMERCE-005. Reassess under a new approved future plan before unblocking.

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Define a versioned, bounded Shared contract for immutable Studio execution snapshots and opaque references.

## Context

Shared already controls CommerceAgent tool-call workflow via runCommerceTurn(). The contract must carry Studio-frozen executable selection without embedding a second execution workflow or exposing a draft as a published capability.

## Scope

Define strict schemas for preview reference identity (opaque ID), environment, selected shop, authenticated Studio administrator, selected capability/revision/descriptor identity, immutable definition payload and content hashes; distinguish selected-feature conversation tests from saved-draft/fixture tests. Define ACTIVE/CLOSED lifecycle and revision/hash consistency. Explicit close/invalidation, no automatic 30-minute TTL. Support bounded fixture data and External HTTP response samples as test inputs without network calls. Preserve existing Shared published commerce.v1 contracts. Schema cap must be justified and consistent with storage limits.

## Out of Scope

No MCP transport, persistence, provider execution, new runner, authorisation bypass, or `_index.md` changes.

## Requirements

Do not alter runCommerceTurn or its injected tool.execute contract. A snapshot reference is minted by authenticated Commerce server and independently checked by MCP reader. No arbitrary executor definitions may be supplied by the LLM or browser at tool-call time.

## Work Items

- [ ] Inspect Shared Commerce manifest, tool descriptor, tool definition and fixture schemas.
- [ ] Implement documented versioned schemas and public exports with strict parse and payload/hash validation.
- [ ] Test missing/extra fields, cross-environment identity, draft selection, revision mismatch and fixture bounds.

## Interfaces / Contracts

Cross-service immutable preview schema and short reference. Exact package export/version is settled by SHARED-002; no duplicate definitions in Commerce/MCP.

## Dependencies

None

## Enables

- ARCH-032-SHARED-002

## Acceptance Criteria

- [ ] Canonical published descriptors and runCommerceTurn unchanged.
- [ ] Snapshot and reference schemas enforce identity, hash, size and strict object validation.
- [ ] Fixture and External HTTP response samples are expressible without treating them as trusted provider responses.

## Validation

- [ ] Shared focused tests, typecheck, lint, build and git diff --check.

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This task is **defined but not materialised**: no branches, commits, pushes, claims or worktrees were created by this artifact. Run `/moda_developer_create ARCH-032-SHARED-001` only after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the developer explicitly closes architecture reconciliation.

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
