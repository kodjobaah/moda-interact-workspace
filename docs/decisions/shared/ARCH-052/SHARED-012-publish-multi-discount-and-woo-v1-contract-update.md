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
status: ready
priority: 22
executor: null
claimed_at: null
attempt: 0
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

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Architect coordination task; **portable definition, not materialised**. No branch or runtime implementation has been created by this artifact.

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

- [ ] Verify prerequisite Architect Reviews are Accepted and status Complete.
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
- [ ] No implementation source changes, tests or builds performed during release.

## Validation

- [ ] Publication permission and registry visibility.
- [ ] Exact published version and source tree diff inspection.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Ready — both implementation prerequisites are architect-accepted Complete. This publication task remains defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No production compatibility is required; all required source provenance remains available for implementing agents to verify.

### Unresolved Issues

None at definition time.

### Architectural Concerns

Any source contract/deployment gap must be escalated rather than patched locally.

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
