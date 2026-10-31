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
status: ready
priority: 24
executor: null
claimed_at: null
attempt: 0
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

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised.**

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

- [ ] Check accepted SHARED-013 review and final SHA.
- [ ] Select a new available package version strictly later than `2.8.1` and update release-only metadata.
- [ ] Publish via the established npm release mechanism and verify the actual tarball/export declarations.
- [ ] Record version, integrity, commands and evidence, then STOP before MCP or Background consumer work.

## Interfaces / Contracts

`@modainteract/moda-interact-shared/commerce`: required nullable `CommerceDiscountConditionFactsSchema.subtotalRequirementCurrency`; retain every existing `CommerceDiscountConditionFacts`, combination fact, `InitialOutreachCheckoutOfferSet` and `WooRestoreOutreachOfferV1` export. No other producer/consumer shape is amended.

## Dependencies

- ARCH-052-SHARED-013.

## Enables

- ARCH-052-MCP-002.
- ARCH-052-BACKGROUND-010 (through MCP-002; publication remains explicit prerequisite).

## Acceptance Criteria

- [ ] Accepted SHARED-013 code is published unchanged in a new immutable registry version.
- [ ] Exact published package fields and old approved exports are inspected; implementation source is unchanged by this publication.
- [ ] Only release metadata and necessary package-build artifacts are produced, with no duplicate tests/typecheck/lint runs.

## Validation

- [ ] Pre-publication accepted task status and SHA check.
- [ ] Exact new version and registry content verification.
- [ ] Release metadata `git diff --check` and package artifact integrity inspection; no implementation validation rerun.

## Stop Condition

Complete the publication Completion Report and set `status: review` for `moda_architect`; STOP. Do not perform dependent MCP or Background implementation.

## Implementation Notes

Use the owning Shared repo's existing publication command and launcher-resolved task worktree. Never include credentials or raw customer/provider data in logs or metadata. Do not edit `_index.md`.

## Completion Report

### Status

Ready — ARCH-052-SHARED-013 is Complete with an Accepted architect review. Publication may proceed under this task's release gate.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Pre-production wire update; no rolling-compatibility adapter required after coordinated consumer pin changes.

### Unresolved Issues

None at definition.

### Architectural Concerns

Return package/contract bugs to moda_architect, not a local publishing fix.

## Architect Review

### Review Status

Pending.

### Review Notes

No publication reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None.
