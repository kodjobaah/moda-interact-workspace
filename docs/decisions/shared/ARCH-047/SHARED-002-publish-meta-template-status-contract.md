---
id: ARCH-047-SHARED-002
architecture_id: ARCH-047
title: Publish canonical Meta template status queue contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-25T21:54:15Z
attempt: 1
depends_on:
  - ARCH-047-SHARED-001
enables:
  - ARCH-047-MESSAGING-001
  - ARCH-047-BACKGROUND-003
created: 2026-10-25
updated: 2026-10-25
---

# Publish canonical Meta template status queue contract

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

## Objective

Publish the architect-accepted, already tested `@modainteract/moda-interact-shared/whatsapp-template-events` v2 contract for use by Messaging and Background.

## Context

ARCH-047-SHARED-001 owns implementation/tests. Consumer repositories must depend on a published package rather than unpublished sibling source code or separate local event schemas.

## Scope

Release-specific package/version metadata and registry publication only, after architect acceptance of SHARED-001.

## Out of Scope

No source implementation changes, dependency redesign, tests/lint/typecheck re-runs, Admin AST/translation work, consumer integration, queue operations or database changes.

## Requirements

- R1. Verify `ARCH-047-SHARED-001` status `complete` and accepted Architect Review before publication.
- R2. Select and apply the architecture-approved new package version, update only release metadata/lockfile if required and run the repository-declared publication command.
- R3. Verify that the exact version, including `./whatsapp-template-events` subpath, is available from the intended registry. Record version, publication command, registry verification and source commit; do not claim publication from local build files alone.
- R4. No source/behaviour changes beyond release-specific metadata; if a code defect is discovered, return to the architect for a correction task rather than fixing it during publication.

## Work Items

- [ ] Verify prerequisite acceptance and choose approved release version.
- [ ] Publish the precise accepted package/version using the repository's release path.
- [ ] Verify the published subpath, capture evidence and complete report.

## Interfaces / Contracts

Published package `@modainteract/moda-interact-shared/whatsapp-template-events` — exact v2 schema, identity and job format from SHARED-001. Publishing does not create another contract.

## Dependencies

- `ARCH-047-SHARED-001` — architect-accepted and Complete. SHARED-001 Attempt 1 is complete and its Architect Review was accepted on 2026-10-25 (parent task commit `7ba6066f`).

## Enables

- `ARCH-047-MESSAGING-001` and `ARCH-047-BACKGROUND-003` may consume published version once their other task dependencies are satisfied.

## Acceptance Criteria

- [ ] Source implementation accepted before publication.
- [ ] Approved package version available from registry and exact new export present.
- [ ] Release evidence recorded and no implementation behaviour altered.

## Validation

- [ ] Publication command and success receipt.
- [ ] Exact version available at registry and published tarball/export check.
- [ ] `git diff --check` on allowed metadata-only changes.

## Stop Condition

Record the released version and Completion Report, set task to `review`, then STOP. Do not start consumer implementation or rerun prior implementation tests.

## Implementation Notes

Use the repository's existing publication workflow and mirrored isolated task branches. No `_index.md` changes.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-25T21:54:15Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.

## Execution Ownership Amendment

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-SHARED-002` for this ready agent-owned publication task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_shared`, coordinator, repository, dependency set, publication-only scope, acceptance criteria and validation requirements.
- Dependency verification: SHARED-001 is Complete with Architect Review Accepted (parent task record commit `7ba6066f`; current frontier reconciliation `9c616a4a`).
- Claim: This amendment does not increment or claim an attempt. The canonical launcher will claim Attempt 1 after worktree synchronization and dependency verification.
