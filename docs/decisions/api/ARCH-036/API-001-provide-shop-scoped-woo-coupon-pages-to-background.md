---
id: ARCH-036-API-001
architecture_id: ARCH-036
title: "ARCH-036-API-001 — Superseded: Background reads Woo coupon pages directly"
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: 2026-10-12
---
# ARCH-036-API-001 — Superseded: Background reads Woo coupon pages directly


## Architecture

- Architecture: `ARCH-036` — `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`; owner: `moda_api` / `moda-interact-api`.
- **Defined but not materialised.** No task branch, dedicated worktree, implementation commit or push has been created.

## Objective


**SUPERSEDED.** No API coupon-page proxy is needed because Background has PostgreSQL access to the verified encrypted read grant and owns the bounded Woo REST sync client. This task must not be claimed, materialised or implemented.

## Context


ARCH-036 Attempt 5 assigns this capability to `ARCH-036-BACKGROUND-001` and removes the earlier independent task or Shared/package boundary. The prior definition is retained only for historical traceability.

## Scope


None. Implementation ownership is `ARCH-036-BACKGROUND-001` under the revised parent architecture.

## Out of Scope

No WordPress-to-Moda snapshot push, sync begin/page/complete ingestion, coupon DB writes, sync-generation ownership, merchant browser endpoint, generic provider REST proxy, arbitrary origin/URL, new credential store or plugin code.

## Requirements


Do not implement any code, endpoint, package schema, publication, queue or configuration from this superseded task. No task depends on it.

## Work Items


None — superseded without execution.

## Interfaces / Contracts


None — the previous proposed contract/endpoint is no longer authorised.

## Dependencies


None — superseded.

## Enables


None — superseded.

## Acceptance Criteria


Not applicable — superseded task.

## Validation


Not applicable — no implementation.

## Stop Condition

After bounded work, acceptance checks and required validation: document the Completion Report, set the task to `review` and STOP. Do not begin dependent tasks. For `superseded` tasks, do not execute or claim.

## Implementation Notes


Do not run `/moda-task` or `/moda_developer_create` for this task. Refer to `ARCH-036-BACKGROUND-001` and the ARCH-036 Attempt 5 architecture instead. No `_index.md` updates.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The executor will verify checkout, actual dependencies, task worktrees and available toolchain at claim time.

### Unresolved Issues

None recorded.

### Architectural Concerns

Stop and return cross-repository, credential, provider compatibility or schema deviations to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable revised definition; no implementation submitted or accepted.

### Reviewed Files

Source snapshot and task contract only. No execution files reviewed.

### Validation Reviewed

No implementation tests have run as part of this definition.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Await real task materialisation, execution, Completion Report and Architect review.
