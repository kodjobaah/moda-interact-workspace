---
id: ARCH-052-SHARED-014
architecture_id: ARCH-052
title: Publish accepted subtotal-threshold currency wire update
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 24
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-052-SHARED-013
enables:
- ARCH-052-MCP-002
- ARCH-052-BACKGROUND-010
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-SHARED-014 — Publish accepted threshold-currency Shared contract

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Materialised and completed in the launcher-resolved task worktrees.**

## Objective

Publish the already architect-accepted SHARED-013 structural wire update to a **new immutable npm version later than `2.8.1`** so MCP and Background use the same source-backed currency field.

## Context

`@modainteract/moda-interact-shared@2.8.1` was already published by SHARED-012, and must not be overwritten or republished in place. MCP-002 cannot implement the exact new field until a new version is available. Do not duplicate contract code locally.

## Scope

- Within `moda-interact-shared/`, after SHARED-013 is Complete, select a fresh semver version permitted by the repository's publishing rules; update release metadata (`package.json` and the repo's actual lockfile) and publish to the established npm destination.
- Confirm the registry tarball and its published TypeScript/JS exports contain `CommerceDiscountConditionFactsSchema` with **required nullable** `subtotalRequirementCurrency` as well as the previously accepted combination and Woo `v1` offer-group schemas.
- Record exact version, registry artifact, package integrity and implementation SHA provenance in this task's Completion Report.

## Out of Scope

No new runtime code, tests, lint, typecheck, unrelated builds, schema change, consumer dependency updates, duplicate local wire contracts, database migration, new Woo response version, or ARCH-053 checkout URL work.

## Requirements

- Publication may begin **only** after SHARED-013 has `status: complete` and an Accepted architect review. Do not infer completion from a successful implementation push.
- Do not overwrite `2.8.1`. Follow the repository's declared release workflow. If package `prepack` performs a build, handle it as a required packaging mechanism, not a new implementation-validation pass; record its effect and authorisation as required.
- Verify the exact published tarball has the fields and existing exports; make **no** unpublished sibling-source assumptions. No compatibility adapter for the pre-production wire is required.
- On publish failure or discovered code defect, log/report the exact error and stop; return the correction to SHARED-013 rather than changing source here.

## Work Items

- [x] Check accepted SHARED-013 review and final SHA.
- [x] Select a new available package version strictly later than `2.8.1` and update release-only metadata.
- [x] Publish via the established npm release mechanism and verify the actual tarball/export declarations.
- [x] Record version, integrity, commands and evidence, then STOP before MCP or Background consumer work.

## Interfaces / Contracts

`@modainteract/moda-interact-shared/commerce`: required nullable `CommerceDiscountConditionFactsSchema.subtotalRequirementCurrency`; retain every existing `CommerceDiscountConditionFacts`, combination fact, `InitialOutreachCheckoutOfferSet` and `WooRestoreOutreachOfferV1` export. No other producer/consumer shape is amended.

## Dependencies

- ARCH-052-SHARED-013.

## Enables

- ARCH-052-MCP-002.
- ARCH-052-BACKGROUND-010 (through MCP-002; publication remains explicit prerequisite).

## Acceptance Criteria

- [x] Accepted SHARED-013 code is published unchanged in a new immutable registry version.
- [x] Exact published package fields and old approved exports are inspected; implementation source is unchanged by this publication.
- [x] Only release metadata and necessary package-build artifacts are produced, with no duplicate tests/typecheck/lint runs.

## Validation

- [x] Pre-publication accepted task status and SHA check.
- [x] Exact new version and registry content verification.
- [x] Release metadata `git diff --check` and package artifact integrity inspection; no implementation validation rerun.

## Stop Condition

Complete the publication Completion Report and set `status: review` for `moda_architect`; STOP. Do not perform dependent MCP or Background implementation.

## Implementation Notes

Use the owning Shared repo's existing publication command and launcher-resolved task worktree. Never include credentials or raw customer/provider data in logs or metadata. Do not edit `_index.md`.

## Completion Report

### Status

Complete — accepted by the architect on Attempt 1. ARCH-052-SHARED-013 was Complete with an Accepted review before publication; version `3.0.0` is published and its registry tarball has been inspected.

### Files Changed

`moda-interact-shared/package.json` and `moda-interact-shared/package-lock.json` only. Both contain the release version `3.0.0`; no source, test, export-map or dependency changes were made.

### Work Completed

Published `@modainteract/moda-interact-shared@3.0.0` to the public npm registry using `npm publish --json --registry=https://registry.npmjs.org`. The repository's `prepack` invoked `npm run build` to generate the required ESM and declaration artifacts; this was packaging, not an implementation-validation rerun. The version is a major bump because this release adds a required field to the public strict contract. The registry did not expose the version on the first immediate lookup; after npm's stated processing delay it became available, and no retry of publication was made.

Pre-publication gate: remote task `ARCH-052-SHARED-013` was `status: complete` with `Accepted — Complete (2026-10-31)`. Accepted implementation SHA: `0b13687d4584801b2aaef3bd625d5b2d6f693648`; the publication worktree HEAD `a582ca9e66d86a1d1ff64099df24520f56adb46a` contains that commit. Package version `3.0.0` was absent from the registry before publication; existing `2.8.1` was not changed.

Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-014` on `task/ARCH-052-SHARED-014`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-014` on `task/ARCH-052-SHARED-014`. Parent claim commit: `dcf282a2d4c023b65aea7fe4742a3974283e80c5`; prepared parent head: `5362773f36eec15e7e095764b040da6c5ce19680`; prepared implementation head: `a582ca9e66d86a1d1ff64099df24520f56adb46a`. Both task branches required no remote fast-forward and already incorporated `origin/main`. Recursive `git submodule sync --recursive` and `git submodule update --init --recursive` passed; no submodule entries were present. The shared workspace checkout and shared implementation checkout were not switched or mutated; no other task worktree was reused.

Registry artifact: `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-3.0.0.tgz`. Integrity: `sha512-CvixJpQEL0nOQv+zoDUAveF0JA1G9PFrT2FN+ubYu94tEgjiLRMtHZGLyxfE5FUHroDt6ZajY/36j3EvyJyFuw==`; SHA-1: `690daf0aa4684a545cc1c39a941ab2267f93b856`. `npm view` metadata and `npm pack @modainteract/moda-interact-shared@3.0.0 --pack-destination /tmp --json` reported matching integrity, size `272590` bytes, and the same SHA-1.

Inspection of the exact downloaded tarball confirmed `CommerceDiscountConditionFactsSchema` has required `subtotalRequirementCurrency: z.ZodNullable<z.ZodString>`, and its Commerce declaration exports `CommerceDiscountCombinationFacts` and its schema. The Commerce entrypoint retains `InitialOutreachCheckoutOfferSet` and its schema; the WooCommerce entrypoint retains `WooRestoreOutreachOfferV1` and its schema. Package metadata includes the `./commerce`, `./commerce/runner` and `./woocommerce` export paths. The implementation source and tests were unchanged by publication.

### Validation Results

Passed: pre-publication accepted-status/SHA check; registry version availability check; `npm ci` from the checked-in lockfile; `npm pack --dry-run --json` (including the package-required `prepack` build); `npm publish --json --registry=https://registry.npmjs.org`; `npm view` registry metadata; `npm pack` of the exact registry version; declaration/export inspection from that tarball; and `git diff --check`.

`npm ci` reported 3 dependency advisories (1 low, 2 high); dependencies were not changed because remediation is outside scope. No tests, typecheck or lint were rerun, as required by this publication task.

### Deviations

The first immediate lookup after publishing returned E404 while the registry was processing the package; the version became available on a later lookup and the published tarball was verified. No publication retry was performed.

### Assumptions

Pre-production wire update; no rolling-compatibility adapter required after coordinated consumer pin changes. SHARED-013 remains the source of the accepted implementation; SHARED-014 changed release metadata only.

### Unresolved Issues

No unresolved publication issue. The published artifact is available at the recorded registry URL.

### Architectural Concerns

The immutable `3.0.0` artifact is published with the accepted SHARED-013 implementation. Consumer implementation remains outside this task.

## Architect Review

### Attempt 1 Architect Review

#### Review Status

Accepted — Complete (2026-10-31).

#### Review Notes

The publication task satisfies its release gate. SHARED-013 was already Complete with an Accepted architect review, and the publication branch contains that accepted source. The implementation diff is limited to the version fields in `package.json` and `package-lock.json`; no source, tests, export map or dependencies changed. Version `3.0.0` is a major release, appropriate for the newly required strict-contract field, and leaves immutable `2.8.1` untouched.

The Completion Report records inspection of the exact registry tarball and its declarations/exports: required nullable `subtotalRequirementCurrency`, combination facts, checkout offer-set exports, Woo offer exports, and Commerce/Woo entrypoints. Its reported tarball integrity is `sha512-CvixJpQEL0nOQv+zoDUAveF0JA1G9PFrT2FN+ubYu94tEgjiLRMtHZGLyxfE5FUHroDt6ZajY/36j3EvyJyFuw==`, with SHA-1 `690daf0aa4684a545cc1c39a941ab2267f93b856`; the report states registry metadata and the downloaded tarball matched. The initial registry propagation delay was resolved and no duplicate publish was made.

#### Reviewed Files

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- This task definition and Completion Report.
- Accepted SHARED-013 implementation commit `0b13687d4584801b2aaef3bd625d5b2d6f693648` as release provenance.

#### Validation Reviewed

Reviewed the recorded SHARED-013 acceptance gate, release metadata diff, `prepack` build, npm publication, registry metadata, exact downloaded tarball integrity and export inspection, and `git diff --check`. Tests, typecheck and lint were not rerun, as required by this publication task. Dependency advisories reported during `npm ci` are documented and outside this task's scope. These validations were reviewed from the report and were not rerun during architect review.

#### Architecture Conformance

Accepted. The exact accepted contract is available as immutable `@modainteract/moda-interact-shared@3.0.0`; the release is metadata-only in Git and follows the task's publication boundary. No unresolved publication or architecture issue remains.

#### Follow-up

SHARED-014 is Complete. MCP-002 and BACKGROUND-010 remain Pending because they still have other unsatisfied dependencies; publication clears only their SHARED-014 dependency. Do not begin their work through this review.
