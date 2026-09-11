---
id: ARCH-010-SHARED-004
architecture_id: ARCH-010
title: Publish recovery-capacity-exhausted Shared contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 52
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHARED-003
enables:
  - ARCH-010-BACKGROUND-009
  - ARCH-010-SHOPIFY-008
created: 2026-09-11
updated: 2026-09-11T17:05:05Z
---

# ARCH-010-SHARED-004: Publish recovery-capacity-exhausted Shared contract

## Objective

Publish the architect-accepted additive Shared billing-system-code change from `ARCH-010-SHARED-003` so Background and Shopify app consumers use one canonical runtime/type contract.

## Publication rule

Before editing version metadata, inspect:

```text
package.json
package-lock.json
npm registry current published version/dist-tag
```

Determine the next valid additive pre-1.0 package version from the **actual state after ARCH-010-SHARED-002**, not from this task document. Do not assume a version number if another release has intervened.

This is publication-only. Do not change implementation semantics beyond version/lock/package publication metadata required for the already accepted source.

Verify the published tarball/runtime/declarations expose `BILLING_RECOVERY_CAPACITY_EXHAUSTED` through the canonical billing entrypoint.

## Validation

Follow the repository's established Shared release workflow. Verify registry version/dist-tag plus runtime/declaration exports and run:

```bash
git diff --check
```

## Non-goals

Do not edit consumer repositories in this task.

## Stop conditions

STOP if the registry/package state differs from the expected task-branch baseline in a way that makes the next version ambiguous.

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
