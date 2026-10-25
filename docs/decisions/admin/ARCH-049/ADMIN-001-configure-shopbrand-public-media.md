---
id: ARCH-049-ADMIN-001
architecture_id: ARCH-049
title: Configure ShopBrand public-media settings
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-10-25T14:25:42Z
attempt: 1
depends_on: []
enables: []
created: 2026-10-25
updated: 2026-10-25
---

# Configure ShopBrand public-media settings

## Architecture

Architecture ID: ARCH-049

Architecture document:
`docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`

Coordinator: moda_architect

## Objective

Expose and persist the agreed non-secret `shopBrand.publicMedia` settings for
SUPER_ADMIN through the existing Admin platform-configuration facility.

## Context

The settings establish configuration values only. They do not implement or
authorize the separate ShopBrand media pipeline.

## Scope

- Add the `shopBrand.publicMedia` contract with defaults:
  - `publicOrigin`: `https://shop-brands.modainteract.com`
  - `bucketName`: `moda-interact-shop-brands`
- Resolve defaults on read without persisting them.
- Persist validated values only after an explicit SUPER_ADMIN save.
- Use the existing platform-configuration persistence mechanism.
- Preserve the private `merchant.knowledge.r2` configuration unchanged.

## Out of Scope

- Database schemas, migrations, or database access changes.
- Media ingestion, fetching, processing, uploading, delivery, or retention.
- Credentials, secrets, or a READY-media contract.
- Changes to private merchant knowledge R2 behavior.

## Requirements

- Reads return saved values when present, otherwise the agreed defaults.
- A read with missing configuration does not create or update persisted state.
- Only an explicit, authorized SUPER_ADMIN save persists values.
- Validate `publicOrigin` as an HTTPS origin and `bucketName` as a valid,
  bounded bucket-name value; reject invalid input without mutation.
- Enforce SUPER_ADMIN authorization server-side.
- Do not treat these settings as proof that public media exists or is accessible.
- Do not alter, alias, or migrate `merchant.knowledge.r2`.
- If the existing platform-config mechanism cannot persist this shape without
  schema changes, stop and return the blocker to moda_architect. Do not change
  the database or invent another persistence mechanism.

## Work Items

- [ ] Inspect the existing Admin platform-configuration read, save and
  authorization paths.
- [ ] Add the typed `shopBrand.publicMedia` contract and defaults.
- [ ] Implement non-persisting default resolution on read.
- [ ] Implement validated explicit SUPER_ADMIN save using existing persistence.
- [ ] Add focused tests for defaults, no-write-on-read, save round-trip,
  validation, authorization and unchanged private R2 configuration.
- [ ] Record worktree and synchronization evidence, changed files and validation
  results in the Completion Report.

## Interfaces / Contracts

Consumes the agreed configuration shape and defaults in:
`docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`.

No shared-package contract, database contract, or media-pipeline contract is
introduced.

## Dependencies

None.

## Enables

None.

## Acceptance Criteria

- [ ] An absent setting reads as the exact agreed defaults and does not write
  persistent state.
- [ ] A valid explicit SUPER_ADMIN save persists both values and subsequent
  reads return them.
- [ ] Unauthorized saves and invalid values fail without changing stored values.
- [ ] `merchant.knowledge.r2` behavior and values are unchanged.
- [ ] No database schema, migration, credential, media-processing, or delivery
  changes are made.
- [ ] If the existing persistence mechanism is insufficient, the task is
  returned blocked without a database workaround.

## Validation

- [ ] Run the relevant checks declared by `moda-interact-admin` for the changed
  surface; do not invent replacement validation commands.
- [ ] Focused tests cover read defaults without writes, explicit save and
  read-back, invalid values, authorization, and private R2 non-regression.
- [ ] `git diff --check`.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are complete,
submit the Completion Report for review and stop. Do not implement or begin any
media-pipeline work.

## Implementation Notes

Inspect the repository's existing platform-configuration persistence and
authorization abstractions first. Keep this task within the Admin repository.
A need for schema changes or cross-repository work is an architectural blocker,
not permission to expand scope.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviations

None

### Assumptions

The existing Admin platform-configuration facility can persist the new
namespace without a database schema change.

### Unresolved Issues

None. If the assumption above is false, return the task blocked to
moda_architect.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not Reviewed

### Follow-up

None
