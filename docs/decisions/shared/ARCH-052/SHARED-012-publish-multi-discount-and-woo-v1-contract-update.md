---
id: ARCH-052-SHARED-012
architecture_id: ARCH-052
title: Publish accepted multi-discount and Woo v1 contract update
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 22
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-052-SHARED-011
- ARCH-053-SHARED-003
enables:
- ARCH-052-MCP-002
- ARCH-052-BACKGROUND-010
- ARCH-052-ADMIN-003
- ARCH-053-API-003
created: 2026-10-30
updated: 2026-10-31
---

# ARCH-052-SHARED-012 — Publish accepted multi-discount and Woo v1 contract update

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Publication attempt is materialised on the dedicated task branches and returned for Architect direction.

## Objective

Publish the two architect-accepted Shared implementations as ONE newly versioned package release, consumable by MCP, Background, Admin, API and WooCommerce.

## Context

SHARED-010 is Complete and its 2.7.0 version must not be overwritten. SHARED-011 owns combination facts and outreach receipt, while ARCH-053-SHARED-003 extends the first-release Woo restore v1 union. One unified publication avoids conflicting package pins.

## Scope

- Check accepted statuses and reviewed SHAs of BOTH implementation tasks before release.
- Perform only version/release metadata and lockfile work, publish by the current Shared registry workflow, verify exact published version and exports, record the resulting version and integrity evidence.
- Leave consumer repository upgrades to their owning tasks.

## Out of Scope

- No implementation changes, code fixes, test/lint/typecheck/build reruns, provider queries, rollout or consumer commits.

## Requirements

- `task_kind: publication` overrides the general implementation metadata for this task.
- Do not reuse or republish 2.7.0; select the next available package version based on registry state.
- This publication gate is shared by ARCH-052 and ARCH-053; no second ARCH-053 publication task is needed for the same source commit.

## Work Items

- [x] Verify both prerequisite Architect Reviews are Accepted and status Complete, and their reviewed SHAs are included in the release source tree.
- [ ] Publish one version and record exact package release+registry evidence; check no source changed except authorised release metadata.

## Interfaces / Contracts

Existing `@modainteract/moda-interact-shared/commerce` and `/woocommerce` subpaths. Exports: `CommerceDiscountCombinationFactsSchema`, `InitialOutreachCheckoutOfferSetSchema`, `WooRestoreOutreachOfferV1Schema` (with CHECKOUT_OFFERS) and `RecoveryTemplateSemanticKeySchema` supporting `offer.codes`. Consumers must update their own manifest/lockfiles and verify the exact pinned version.

## Dependencies

- ARCH-052-SHARED-011
- ARCH-053-SHARED-003

## Enables

- ARCH-052-MCP-002
- ARCH-052-BACKGROUND-010
- ARCH-052-ADMIN-003
- ARCH-053-API-003

## Acceptance Criteria

- [ ] The published registry artifact contains both additions and is visible at the recorded exact version.
- [x] No implementation source changes, tests or builds were performed during this attempt.

## Validation

- [ ] Publication permission and registry visibility.
- [ ] Exact published version and source tree diff inspection.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Returned for Architect direction. Attempt 1. Release metadata is prepared, but publication was not performed because the only available package workflow would require a build prohibited by this task.

### Files Changed

- `package.json` — version set to candidate `2.8.1`.
- `package-lock.json` — root package version set to candidate `2.8.1`.

### Work Completed

- Verified ARCH-052-SHARED-011 and ARCH-053-SHARED-003 are both Architect Accepted and Complete.
- Confirmed their reviewed implementation SHAs are included in the current release source tree:
  - SHARED-011: `cba9decf56e6cf22c8973e814c713330412db8c1`.
  - ARCH-053-SHARED-003: `fec2be64b148e48b328816632fa7b3ba3ae1565c`.
- Verified the source exports include the accepted discount combination facts, initial outreach offer set, `offer.codes` binding and Woo `CHECKOUT_OFFERS` resolver branch.
- Queried the public npm registry: latest published version is `2.8.0`; `2.8.1` is the next candidate. Confirmed the configured npm identity is authenticated and listed as a package owner.
- Prepared only the candidate version metadata and lockfile. No source, tests or builds were changed/run.
- Inspected the package `prepack` script: it runs `npm run build`. A no-script pack dry run confirmed the current checkout has no `dist` artifact and would package no exported JavaScript or declaration files. Publishing that artifact would be unusable; running the prepack build would conflict with this task's explicit no-build requirement.

### Validation Results

- Prerequisite status and Architect acceptance: passed.
- Reviewed SHA inclusion in release source tree: passed.
- Registry visibility and current latest version: passed (`2.8.0`).
- Registry owner access: passed.
- Candidate metadata diff: limited to `package.json` and `package-lock.json`, both `2.8.1`.
- No package was published. The no-script pack dry run showed no `dist` output; standard `npm publish` invokes the prohibited prepack build.

### Deviations

Publication was not performed. The task requires a valid published artifact but forbids the build needed to produce `dist`; no alternative release workflow or prebuilt combined artifact exists in this checkout.

### Assumptions

None beyond the task. The candidate remains `2.8.1` based on the registry state observed on 2026-10-31 and must be rechecked before any later publication.

### Unresolved Issues

Architect direction is required: either authorize the package's existing `prepack` build as part of publication or provide an approved, prebuilt artifact/release workflow that includes both accepted implementations without running a build in this task.

### Architectural Concerns

No source or contract gap was found. The blocker is the conflict between the publication requirement and the explicit prohibition on builds.

### Synchronization and Version Control

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; unchanged.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-012`, branch `task/ARCH-052-SHARED-012`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-012`, branch `task/ARCH-052-SHARED-012`; shared implementation checkout unchanged.
- Another task worktree reused: no.
- Start synchronization: parent and implementation remote task branch fast-forwards were `not-needed`; `origin/main` was `already-current` in both worktrees.
- Recursive implementation submodules: sync passed; update/init passed; ready, no entries.
- Parent claim commit: `2afa020403a4aed48d8a8d437448272e5dae608e`, pushed by launcher.
- Implementation release-metadata commit: `21b9434e4d14d8dcb17b8c74090d0e59d595eab7`; publication not performed.
- Parent report commit: this report is being committed locally; package publication remains pending Architect direction.
- No npm release or main-branch update was made.

## Architect Review

### Review Status

Pending.

### Review Notes

New multi-discount feature task; no implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

No implementation validation yet.

### Architecture Conformance

Pending implementation and review.

### Follow-up

None.
