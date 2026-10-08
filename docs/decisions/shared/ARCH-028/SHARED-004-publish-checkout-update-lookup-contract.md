---
id: ARCH-028-SHARED-004
architecture_id: ARCH-028
title: Publish compatible Shopify checkout-update lookup-context contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 29
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-SHARED-003
enables:
  - ARCH-028-BACKGROUND-012
  - ARCH-028-SHOPIFY-001
created: 2026-10-08
updated: 2026-10-08
---

# Publish compatible Shopify checkout-update lookup-context contract

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Publish one exact registry version containing the accepted SHARED-003 Shopify checkout-update v2/v3 parser and contract, without modifying runtime implementation or consumer repositories.

## Context

SHARED-003 must be Complete and architect-accepted before this publication task executes. SHARED-002 already published the separate WhatsApp provider-status contract. This task follows that release rather than racing it, then makes the separately reviewed Shopify contract available to Background and Shopify consumer/producer tasks.

## Scope

- Verify SHARED-003 is Complete and architect-accepted, recording its implementation commit.
- Establish checked-in package version and actual public npm registry baseline, stopping if they disagree.
- Select exactly one approved compatible patch version, change only release metadata (normally `package.json` and lockfile) and publish using the repository's normal process.
- Verify exact package version, registry integrity, tarball and clean-install runtime imports of the accepted Shopify subpath contract.
- Record registry/published-version evidence for BACKGROUND-012 and SHOPIFY-001.

## Out of Scope

- Modifying Shared `src` or tests; fixing implementation defects in the publication branch.
- Rerunning unit tests, lint, typecheck or builds already accepted in SHARED-003.
- Changing WhatsApp schema, rolling back SHARED-002, changing consumer/producer repositories.
- Performing Background or Shopify implementation work.

## Requirements

- [ ] SHARED-003 must have status Complete and Architect Review Accepted.
- [ ] Checked-in and registry version baseline must agree before patch bump.
- [ ] Release is one compatible patch and contains accepted SHARED-003 Shopify exports.
- [ ] No implementation source is modified, and no implementation validation is rerun.
- [ ] Exact published version and clean-install imports are proven.

## Work Items

- [ ] Record accepted SHARED-003 implementation SHA and package baseline.
- [ ] Apply allowed release metadata patch bump and publish once.
- [ ] Validate npm registry version/integrity and the clean-install Shopify exports.
- [ ] Record publication evidence in Completion Report.

## Interfaces / Contracts

Publishes `@modainteract/moda-interact-shared/shopify` containing accepted SHARED-003 v2/v3 checkout-update contracts. BACKGROUND-012 consumes first; SHOPIFY-001 emits new v3 events only after Background acceptance. The separate SHARED-002 WhatsApp contract remains intact.

## Dependencies

- `ARCH-028-SHARED-003`

## Enables

- `ARCH-028-BACKGROUND-012`
- `ARCH-028-SHOPIFY-001`

## Acceptance Criteria

- [ ] Accepted prerequisite implementation is verified.
- [ ] A single exact patch release is available from target npm registry.
- [ ] Clean install resolves the version and runtime exports; package integrity is recorded.
- [ ] No unauthorized source change or code-validation run occurs in publication task.

## Validation

Release mechanics only: version baseline, patch metadata, npm publish, registry/integrity/tarball lookup, clean installation/import of the exact published artifact and `git diff --check`. Do not rerun SHARED-003 tests, typecheck or build.

## Stop Condition

Complete the publication report, set status `review`, return to `moda_architect`, and STOP. Never continue into consumer integration.

## Implementation Notes

If publication reveals an implementation defect or version-baseline disagreement, stop and return to architect for same-task correction; do not modify implementation source here. Credentials are supplied securely outside source control.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

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

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
