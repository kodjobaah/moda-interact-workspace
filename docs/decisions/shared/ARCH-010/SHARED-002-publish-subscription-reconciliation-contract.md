---
id: ARCH-010-SHARED-002
architecture_id: ARCH-010
title: Publish subscription reconciliation Shared contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 21
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHARED-001
enables:
  - ARCH-010-BACKGROUND-001
  - ARCH-010-BACKGROUND-003
  - ARCH-010-BACKGROUND-006
  - ARCH-010-BACKGROUND-007
  - ARCH-010-BACKGROUND-008
  - ARCH-010-BACKGROUND-010
  - ARCH-010-BACKGROUND-012
  - ARCH-010-BACKGROUND-016
  - ARCH-010-SHOPIFY-002
  - ARCH-010-SHOPIFY-006
  - ARCH-010-SHOPIFY-007
  - ARCH-010-SHOPIFY-015
created: 2026-09-11
updated: 2026-09-11T16:50:27Z
---

# ARCH-010-SHARED-002: Publish subscription reconciliation Shared contract

## Objective

Publish the architect-accepted `ARCH-010-SHARED-001` additive billing queue contract for use by Shopify and Background repositories.

## Publication rule

Before editing version metadata, inspect the exact current accepted/published package version in `package.json`, lockfile and npm registry. If `0.8.0` is still current and no intervening accepted release exists, the expected additive pre-1.0 release is `0.9.0`. If repository/registry state has advanced, STOP and return the observed versions to `moda_architect` rather than guessing or overwriting another release.

This is publication-only. Allowed changes are version/package-lock metadata required by the accepted source plus publication mechanics. Do not alter contract implementation.

Verify the published tarball/runtime/declarations expose the ARCH-010 reconciliation constants, schema/parser and deterministic job-ID helper.

Do not modify consumer repositories in this task.

## Validation

Use publication mechanics only, following the repository's established Shared release workflow. Verify registry version/dist-tag and exported declarations/runtime symbols. Run `git diff --check`.

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

## Non-goals

Do not change the accepted contract implementation, edit consumer repositories, create deployment configuration, or publish unrelated Shared work without architect coordination.

## Stop conditions

STOP if the registry/repository version has advanced unexpectedly, the accepted SHARED-001 source is not present, or publication would overwrite/co-release an unreviewed Shared change. Return the observed state to `moda_architect`.
