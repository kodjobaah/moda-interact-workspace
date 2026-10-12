---
id: ARCH-032-SHARED-002
architecture_id: ARCH-032
title: Publish the architect-accepted immutable preview-reference Shared contract for Commerce and MCP consumers
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: blocked
priority: 43
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-SHARED-001
enables:
  - ARCH-032-DATABASE-002
  - ARCH-032-COMMERCE-003
  - ARCH-032-MCP-017
  - ARCH-032-MCP-018
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-SHARED-002 — Publish the architect-accepted immutable preview-reference Shared contract for Commerce and MCP consumers

## Execution hold — 2026-10-12

**DO NOT CLAIM OR IMPLEMENT IN THIS PHASE.** Deferred: do not publish a remote-preview contract during mock-first extraction. Earlier remote-first descriptions and dependencies are superseded by ARCH-032-COMMERCE-001 through COMMERCE-005. Reassess under a new approved future plan before unblocking.

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Publish the architect-accepted immutable preview-reference Shared contract for Commerce and MCP consumers.

## Context

Consumer implementations must pin a real published Shared version and cannot rely on workspace-only imports.

## Scope

Follow the canonical Shared publication protocol. Inspect current registry version and exact source, publish accepted additive exports and verify npm tarball import/types. Record exact version and dist-tag. Stop if registry state has advanced unexpectedly or unreconciled changes must be co-released.

## Out of Scope

Do not change accepted contract semantics or modify Commerce, MCP, Database or Background code.

## Requirements

Published package must preserve existing Commerce runner API and manifest compatibility; never assume a version number in advance.

## Work Items

- [ ] Verify accepted SHARED-001 source and test output.
- [ ] Publish accepted contract with registry version check.
- [ ] Confirm runtime and declarations imports from the published tarball; record exact version.

## Interfaces / Contracts

New frozen-preview Shared export. Existing @modainteract/moda-interact-shared/commerce and runner exports remain backwards-compatible.

## Dependencies

- ARCH-032-SHARED-001

## Enables

- ARCH-032-DATABASE-002
- ARCH-032-COMMERCE-003
- ARCH-032-MCP-017
- ARCH-032-MCP-018

## Acceptance Criteria

- [ ] Exact published package with typed and runtime imports verified.
- [ ] Existing Shared functionality and runner contract remain intact.

## Validation

- [ ] npm view of published version/export, package test/build and git diff --check.

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This task is **defined but not materialised**: no branches, commits, pushes, claims or worktrees were created by this artifact. Run `/moda_developer_create ARCH-032-SHARED-002` only after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the developer explicitly closes architecture reconciliation.

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
