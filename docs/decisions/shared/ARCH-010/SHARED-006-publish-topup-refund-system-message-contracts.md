---
id: ARCH-010-SHARED-006
architecture_id: ARCH-010
title: Publish top-up refund Shared message contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 23
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHARED-005
enables:
  - ARCH-010-ADMIN-002
  - ARCH-010-ADMIN-003
  - ARCH-010-SHOPIFY-017
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHARED-006: Publish top-up refund Shared message contracts

## Objective

Publish the architect-accepted additive Shared billing-message change from ARCH-010-SHARED-005 for Admin/Shopify consumers.

## Publication rule

Before changing version metadata, inspect:

```text
package.json
package-lock.json
npm registry current version/dist-tag
```

Choose the next valid additive pre-1.0 release from the actual accepted/published state.

Do not assume a version number from this task document. If repository/registry state has advanced or another accepted unpublished Shared change must be co-released, STOP and return the observed state to `moda_architect` rather than overwriting/guessing.

Publication-only: do not alter contract implementation except version/package metadata required by the accepted source.

Verify the published tarball/runtime/declarations expose the three refund codes through the canonical billing export.

Run established Shared publication validation and `git diff --check`.

## Validation

Use only the repository's established publication workflow. Verify the published tarball/runtime/declarations expose the three accepted refund message codes through the canonical billing export, confirm registry version/dist-tag, and run `git diff --check`.

## Non-goals

Do not alter the accepted SHARED-005 contract implementation, edit consumer repositories, create provider refund APIs, or publish unrelated unreviewed Shared changes.

## Stop conditions

STOP if the registry/repository version has advanced unexpectedly, SHARED-005 is not the source being published, or another accepted-but-unpublished Shared change must be co-released without architect reconciliation.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
