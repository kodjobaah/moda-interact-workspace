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
status: review
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

- [x] Inspect the existing Admin platform-configuration read, save and
  authorization paths.
- [x] Add the typed `shopBrand.publicMedia` contract and defaults.
- [x] Implement non-persisting default resolution on read.
- [x] Implement validated explicit SUPER_ADMIN save using existing persistence.
- [x] Add focused tests for defaults, no-write-on-read, save round-trip,
  validation, authorization and unchanged private R2 configuration.
- [x] Record worktree and synchronization evidence, changed files and validation
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

- [x] An absent setting reads as the exact agreed defaults and does not write
  persistent state.
- [x] A valid explicit SUPER_ADMIN save persists both values and subsequent
  reads return them.
- [x] Unauthorized saves and invalid values fail without changing stored values.
- [x] `merchant.knowledge.r2` behavior and values are unchanged.
- [x] No database schema, migration, credential, media-processing, or delivery
  changes are made.
- [x] Existing persistence supports the additional key without schema changes;
  no database workaround was needed.

## Validation

- [x] Run the relevant checks declared by `moda-interact-admin` for the changed
  surface; do not invent replacement validation commands.
- [x] Focused tests cover read defaults without writes, explicit save and
  read-back, invalid values, authorization, and private R2 non-regression.
- [x] `git diff --check`.

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

Ready for Review

### Files Changed

- `moda-interact-admin/src/lib/admin/platform-configuration/contracts.ts`
- `moda-interact-admin/src/lib/admin/platform-configuration/repository.ts`
- `moda-interact-admin/tests/unit/arch043-platform-configuration-contracts.test.ts`
- `moda-interact-admin/tests/unit/arch049-public-media-configuration.test.ts`

### Work Completed

- Added `shopBrand.publicMedia` as a distinct SUPER_ADMIN policy with the agreed
  public origin and bucket defaults. The origin is required, HTTPS-only, and
  restricted to an origin without a path; bucket input uses the existing
  bounded bucket validator.
- Missing-row reads return defaults in memory and do not write. Explicit saves
  use the existing validated, versioned, audited platform-configuration writer.
- The contract is not resettable, so defaults are not persisted through an
  implicit reset action. `merchant.knowledge.r2` remains unchanged.
- No schema, migration, credential, deployment, or media-pipeline changes were
  made. The agreed values are code defaults only; they have not been explicitly
  persisted to a live environment and no live write was attempted.

### Validation Results

- `npm run test:arch043-admin-config:unit`: passed, 10 tests.
- `npm run test:arch043-admin-config:components`: passed, 2 tests.
- `npm exec -- tsx --test tests/unit/arch049-public-media-configuration.test.ts`:
  passed, 4 tests covering defaults/no-write, save/read-back, invalid values,
  SUPER_ADMIN authorization, and private R2 isolation.
- `npm run lint -- src/lib/admin/platform-configuration/contracts.ts src/lib/admin/platform-configuration/repository.ts`:
  passed with no warnings on changed production files.
- `npm exec -- tsc --noEmit`: passed.
- `npm exec -- prettier --check tests/unit/arch049-public-media-configuration.test.ts`:
  passed. Existing compactly styled modules and tests were already flagged at
  `HEAD`; no unrelated formatting churn was introduced.
- `git diff --check`: passed.
- Persistence round-trip was tested with an injected test database only; no live
  database or environment configuration was written.

### Worktree and Synchronization Evidence

- Implementation worktree:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-049-ADMIN-001`
- Parent worktree:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-049-ADMIN-001`
- Both were clean before implementation and on `task/ARCH-049-ADMIN-001`;
  both already contained `origin/main`, so no mainline merge was required.
- Implementation commit `7cbe5b0` was pushed to
  `origin/task/ARCH-049-ADMIN-001`.

### Deviations

None

### Assumptions

The existing platform-configuration table supports another environment/key
record. The generic environment/key lookup and audited transactional
create/update path were verified; no schema change was needed.

### Unresolved Issues

None.

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
