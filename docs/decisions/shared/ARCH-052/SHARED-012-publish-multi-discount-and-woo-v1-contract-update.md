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
- [x] Publish one version and record exact package release+registry evidence; check no source changed except authorised release metadata.

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

- [x] The published registry artifact contains both additions and is visible at the recorded exact version.
- [x] No implementation source changes or tests were performed. The existing package `prepack` build ran solely to create the publishable artifact, with explicit user authorization on 2026-10-31.

## Validation

- [x] Publication permission and registry visibility.
- [x] Exact published version and source tree diff inspection.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Ready for Architect review. Attempt 1. Published `@modainteract/moda-interact-shared@2.8.1` after the user explicitly authorized the existing `prepack` build needed to create the package artifact.

### Files Changed

- `package.json` — version set to candidate `2.8.1`.
- `package-lock.json` — root package version set to candidate `2.8.1`.
- No implementation source files were changed. The generated `dist` output and installed dependencies are ignored build artifacts and are not part of the release-metadata commit.

### Work Completed

- Verified ARCH-052-SHARED-011 and ARCH-053-SHARED-003 are both Architect Accepted and Complete.
- Confirmed their reviewed implementation SHAs are included in the current release source tree:
  - SHARED-011: `cba9decf56e6cf22c8973e814c713330412db8c1`.
  - ARCH-053-SHARED-003: `fec2be64b148e48b328816632fa7b3ba3ae1565c`.
- Verified the source exports include the accepted discount combination facts, initial outreach offer set, `offer.codes` binding and Woo `CHECKOUT_OFFERS` resolver branch.
- Queried the public npm registry: latest published version is `2.8.0`; `2.8.1` is the next candidate. Confirmed the configured npm identity is authenticated and listed as a package owner.
- Prepared only the candidate version metadata and lockfile. No source, tests or builds were changed/run.
- Confirmed `package.json` `prepack` runs the repository's declared `npm run build` script. The task initially prohibited builds; after the conflict was explained, the user explicitly authorized the existing `prepack` build as necessary for this publication.
- Installed the exact lockfile dependencies with `npm ci`, then published through the declared npm workflow. The prepack TypeScript/ESM and declaration build completed successfully. No tests were run and no implementation source was edited.
- Verified the registry artifact itself by downloading `@modainteract/moda-interact-shared@2.8.1` with scripts disabled and inspecting its tarball metadata, export map and declarations. It includes the `./commerce`, `./woocommerce` and `./recovery-template-bindings` subpaths, `CommerceDiscountCombinationFactsSchema`, `InitialOutreachCheckoutOfferSetSchema`, `WooRestoreOutreachOfferV1Schema` with `CHECKOUT_OFFERS`, and `RecoveryTemplateSemanticKeySchema` with `offer.codes`.

### Validation Results

- Prerequisite status and Architect acceptance: passed.
- Reviewed SHA inclusion in release source tree: passed.
- Pre-release registry check: latest was `2.8.0`; `2.8.1` was available.
- Registry owner access: passed.
- Release metadata diff: limited to `package.json` and `package-lock.json`, both set to `2.8.1`.
- Declared `npm publish --access public` workflow: passed; existing prepack build completed successfully.
- Published registry version: `2.8.1`, latest tag; tarball: `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-2.8.1.tgz`.
- Registry integrity: `sha512-wvYK8jLGPiLEoOU9biPpCZmJFRloJ5SgdpeCsIkENPev16c6WOViKMjqDTcoMnymVmNybOIc/e1otti80EDaug==`; shasum `20f54b250b6a6ec9659b3c33bf128f4a354009db`.
- Downloaded artifact inspection: passed; 128 files, including the exact entrypoints and declarations listed above.
- Source-tree diff after release metadata: no implementation source changes; no tests run. Build output remained ignored and uncommitted.

### Deviations

The task's original no-build wording conflicted with its requirement to publish a complete artifact through the package's declared `prepack` workflow. The user explicitly authorized this existing prepack build before release. No other task scope was changed.

### Assumptions

The release is visible as version `2.8.1` in the npm registry, with the integrity recorded above.

### Unresolved Issues

None. The build restriction conflict was resolved by the user's explicit authorization, and registry publication plus artifact inspection passed.

### Architectural Concerns

No source or contract gap was found. The original conflict between the publication requirement and the build restriction was resolved when the user authorized the package's existing `prepack` build.

### Synchronization and Version Control

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; unchanged.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-012`, branch `task/ARCH-052-SHARED-012`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-012`, branch `task/ARCH-052-SHARED-012`; shared implementation checkout unchanged.
- Another task worktree reused: no.
- Start synchronization: parent and implementation remote task branch fast-forwards were `not-needed`; `origin/main` was `already-current` in both worktrees.
- Recursive implementation submodules: sync passed; update/init passed; ready, no entries.
- Parent claim commit: `2afa020403a4aed48d8a8d437448272e5dae608e`, pushed by launcher.
- Implementation release-metadata commit: `21b9434e4d14d8dcb17b8c74090d0e59d595eab7`; pushed to `task/ARCH-052-SHARED-012` after user authorization.
- Final parent report commit: `a9be8f083dfa5f62cd9d28d9b03e2dbe09417dc6`; pushed to `origin/task/ARCH-052-SHARED-012`. This report records the successful publication and registry artifact verification.
- Package version `2.8.1` published to npm; no main-branch update was made.
- No main-branch update was made.

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
