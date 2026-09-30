---
id: ARCH-023-DATABASE-004
architecture_id: ARCH-023
title: Allow successor releases to preserve historical Feature snapshots
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 62
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-DATABASE-003
  - ARCH-023-DATABASE-001
enables:
  - ARCH-023-COMMERCE-002
created: 2026-09-30
updated: 2026-09-30
---

# Allow successor releases to preserve historical Feature snapshots

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Correct the accepted ARCH-021 `CommerceReleaseFeature` insert guard with one forward-only database migration so a new release may preserve an exact immutable historical Feature Behaviour snapshot after the current `CommerceFeatureConfiguration.behaviourPrompt` has advanced.

The database must continue to reject arbitrary stale/never-published prompt text. The allowed insert values for one Feature become exactly:

```text
current CommerceFeatureConfiguration.behaviourPrompt
OR
an exact behaviourPrompt already persisted in an immutable CommerceReleaseFeature
for the same featureId
```

This task exists because `ARCH-023-COMMERCE-002` Attempt 3 proved that the current guard rejects the architecture-required successor-release operation when it copies the base release's frozen Feature snapshot after unrelated Feature authoring has changed.

## Context

ARCH-021 deliberately models release Feature Behaviour as an immutable per-release snapshot:

```text
CommerceFeatureConfiguration
    current authoring value

CommerceReleaseFeature
    immutable value used by one release
```

The accepted `20260929120000_arch021_feature_capability_simplification` migration currently installs:

```text
commerce.arch021_release_feature_guard
```

and requires every new `CommerceReleaseFeature.behaviourPrompt` to equal the **current** Feature configuration. That correctly protects ordinary fresh release composition, but it is too strict for an immutable successor release.

The required successor operation is:

```text
base release
    Feature F snapshot = "v1"

Feature F current authoring later becomes "v2"

successor release copies the base release
    Feature F snapshot MUST remain exactly "v1"
```

Mutating the base release, rewriting the copied snapshot to `v2`, bypassing the database trigger from Commerce, or restoring retired Capability-revision concepts would all violate accepted architecture.

The database therefore needs one narrowly scoped historical-snapshot admission rule while retaining all existing release-row immutability and Feature/Tool release integrity.

## Scope

Modify only `moda-interact-database` files required for this guard correction and its focused validation.

Required primary files:

```text
prisma/migrations/20260930200000_arch023_release_feature_snapshot_history/migration.sql
scripts/validate-arch023-release-feature-snapshot-history.mjs
scripts/test-arch023-release-feature-snapshot-history-postgres.mjs
package.json
```

`prisma/schema.prisma` MUST remain unchanged unless `prisma format` produces no semantic schema change; this task adds no model, column, enum, key, index or relation.

The migration directory name above is fixed.

## Out of Scope

- Commerce application/lifecycle/storage changes.
- Changing `CommerceRelease`, `CommerceReleaseFeature` or `CommerceReleaseCapability` Prisma models.
- Adding `parentReleaseId`, release ancestry tables or a successor-release database model.
- Session variables, trigger-disable flags, privileged bypass functions or task-specific SQL escape hatches.
- Mutating or deleting historical release Feature snapshots.
- Weakening `arch021_release_feature_immutable`.
- Weakening exact PUBLISHED Tool-revision release membership.
- Restoring `CommerceCapabilityRevision`, `selectionBinding`, `toolBindings[]` or another retired Capability revision/binding model.
- Merchant Knowledge schema changes.
- Reworking ordinary release composition semantics in Commerce.

## Requirements

### R1 — forward-only guard correction

Create exactly:

```text
prisma/migrations/20260930200000_arch023_release_feature_snapshot_history/migration.sql
```

The migration MUST use `CREATE OR REPLACE FUNCTION` to replace only:

```text
commerce.arch021_release_feature_guard()
```

Do not drop/recreate `commerce."CommerceReleaseFeature"` and do not disable its triggers.

The existing trigger name MUST remain:

```text
arch021_release_feature_guard
```

The existing immutable trigger MUST remain installed and unchanged:

```text
arch021_release_feature_immutable
```

### R2 — exact current-or-historical admission rule

For `NEW."featureId"`, the corrected guard MUST retain the existing Feature-row share lock and current-prompt lookup semantics.

It MUST admit the insert when either condition is true:

```text
A. NEW.behaviourPrompt exactly equals the current
   CommerceFeatureConfiguration.behaviourPrompt for NEW.featureId

OR

B. an already-persisted CommerceReleaseFeature row exists where:
     prior.featureId       = NEW.featureId
     prior.behaviourPrompt = NEW.behaviourPrompt
```

If no `CommerceFeatureConfiguration` exists for the Feature, retain the existing current-prompt fallback of the empty string.

The historical alternative MUST be scoped to the **same `featureId`** and the **exact prompt text**. A prompt historically published for another Feature does not authorize it for this Feature.

If neither A nor B holds, reject with SQLSTATE `23514`. Preserve the existing error text unless a more precise replacement is needed by the focused validator; do not downgrade rejection to a warning.

### R3 — historical means already immutable and persisted

The historical branch may consult only already-persisted `commerce."CommerceReleaseFeature"` rows.

Do not add a mutable history table or copy current configuration into a helper table.

The correction relies on the already-accepted invariant that `CommerceReleaseFeature` rows cannot be updated or deleted. It MUST NOT weaken that invariant.

No release-ancestry claim is added at the database layer. `ARCH-023-COMMERCE-002` remains responsible for proving that its successor lifecycle copies the **selected base release** exactly. This task only makes that valid immutable copy representable in PostgreSQL.

### R4 — preserve concurrency protection

Retain:

```text
PERFORM ... FROM billing."Feature" ... FOR SHARE
```

before evaluating current Feature configuration.

The final guard must continue to serialize correctly with `commerce.arch021_feature_configuration_guard`, which locks the same Feature row `FOR UPDATE` while Feature Behaviour is edited.

Do not add advisory locks or a second locking protocol.

### R5 — static validator

Add:

```text
scripts/validate-arch023-release-feature-snapshot-history.mjs
```

and package command:

```text
test:arch023-release-feature-snapshot-history
```

The validator MUST fail unless the fixed migration:

1. `CREATE OR REPLACE`s `commerce.arch021_release_feature_guard`;
2. retains the billing Feature `FOR SHARE` lock;
3. retains the current `CommerceFeatureConfiguration.behaviourPrompt` path and empty-string fallback;
4. admits an exact already-persisted `CommerceReleaseFeature` snapshot only when both `featureId` and `behaviourPrompt` match;
5. retains SQLSTATE `23514` rejection when neither allowed source matches;
6. does not drop/disable `arch021_release_feature_immutable`;
7. does not add a session/bypass flag or modify the Prisma schema.

The validator must inspect semantics tightly enough that removing either the `featureId` match or the exact `behaviourPrompt` match causes it to fail.

### R6 — executable PostgreSQL regression proof

Add:

```text
scripts/test-arch023-release-feature-snapshot-history-postgres.mjs
```

and package command:

```text
test:arch023-release-feature-snapshot-history:postgres
```

Use one invocation-owned disposable `pgvector/pgvector:pg17` PostgreSQL instance. Do not consume an ambient/user database URL. The runner must clean up its owned container on success and failure.

The proof MUST exercise the real accepted migration chain and establish all of the following:

#### Upgrade-before/after proof

1. apply the migration chain through `20260929160000_arch023_merchant_knowledge_schema`, excluding this new migration;
2. create Feature `F` with current Behaviour `v1`;
3. create a release and persist Feature `F` snapshot `v1` successfully;
4. update current Feature Behaviour to `v2` using the accepted edit-version path;
5. prove the predecessor ARCH-021 guard rejects inserting a different release snapshot `v1` with SQLSTATE `23514`;
6. apply `20260930200000_arch023_release_feature_snapshot_history`;
7. prove the same historical `v1` snapshot is now admitted for a new release;
8. prove current `v2` is still admitted for a new release.

#### Negative cases

9. reject prompt text for Feature `F` that is neither current nor historically persisted for `F`;
10. create another Feature `G` and prove a prompt historical only for Feature `F` does **not** become valid for `G`;
11. retain rejection of UPDATE and DELETE against an existing `CommerceReleaseFeature` row.

#### Preservation

12. prove the migration does not alter existing `CommerceReleaseFeature` rows, release rows, release capability rows, current Feature configuration or unrelated ARCH-023 data;
13. prove the final database still contains exactly one active `arch021_release_feature_guard` trigger and the unchanged `arch021_release_feature_immutable` trigger on `CommerceReleaseFeature`.

### R7 — no Commerce workaround

This Database task must not patch `moda-interact-commerce` to bypass the guard.

The intended sequence is:

```text
DATABASE-004 migration accepted
        ↓
ARCH-023-COMMERCE-002 returns from Blocked to Ready
        ↓
next Commerce attempt reruns its existing real PostgreSQL successor-preservation proof
```

## Work Items

- [x] Add the fixed forward migration.
- [x] Replace only `commerce.arch021_release_feature_guard()` with current-or-historical exact admission.
- [x] Preserve all release Feature immutability and other ARCH-021 release guards.
- [x] Add the exact static validator.
- [x] Add the disposable pgvector/PostgreSQL before/after upgrade rehearsal.
- [x] Add package scripts for both validators.
- [x] Run Prisma validation/generation only as required to prove no schema regression.
- [x] Record canonical parent/implementation worktree preparation, synchronization and recursive-submodule evidence.
- [x] Update the Completion Report and return to architect review.

## Acceptance Criteria

- [x] No Prisma model/schema semantic change is introduced.
- [x] Existing current Feature Behaviour snapshots remain valid.
- [x] An exact historical immutable snapshot for the same Feature becomes valid in a later release after current authoring advances.
- [x] Arbitrary never-published stale prompt text remains invalid.
- [x] A historical prompt from a different Feature remains invalid.
- [x] Existing `CommerceReleaseFeature` rows remain immutable.
- [x] Existing Tool-revision/member release guards remain unchanged.
- [x] The disposable PostgreSQL upgrade proof demonstrates the predecessor failure and corrected post-migration success.
- [x] The migration preserves existing release/configuration data.
- [x] No Commerce implementation workaround or retired Capability model is introduced.
- [x] All required validation passes and the task-owned container is removed.

## Validation

Required repository validation:

```text
npm run prisma:validate
npm run prisma:generate
npm run test:arch023-release-feature-snapshot-history
npm run test:arch023-release-feature-snapshot-history:postgres
git diff --check
```

Also run the repository's existing ARCH-021 Feature/Capability migration/schema validators if they are still declared in `package.json`. If an ARCH-021 static validator encodes the superseded **current-only** guard assertion, update that validator narrowly so it proves the new current-or-historical invariant rather than deleting release-snapshot validation.

Changed-file diagnostics must be clean.

## Dependencies

Depends on:

- `ARCH-021-DATABASE-003` — owns the direct Feature/Capability/release snapshot model and predecessor guard.
- `ARCH-023-DATABASE-001` — current latest accepted database migration baseline consumed by ARCH-023.

Enables:

- resumption of blocked `ARCH-023-COMMERCE-002`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, clear the active claim, return the Completion Report to `moda_architect` and STOP.

Do not start or modify `ARCH-023-COMMERCE-002` from this task.

## Completion Report

### Status

Attempt 1 complete; returned to Architect Review with `status: review`, `attempt: 1`, `executor: null`, and `claimed_at: null`.

### Files Changed

Implementation files:
- `prisma/migrations/20260930200000_arch023_release_feature_snapshot_history/migration.sql`
- `scripts/validate-arch023-release-feature-snapshot-history.mjs`
- `scripts/test-arch023-release-feature-snapshot-history-postgres.mjs`
- `package.json`

The Prisma schema, package lockfile, other repositories, and all out-of-scope models/guards were unchanged.

### Work Completed

Added a forward-only `CREATE OR REPLACE FUNCTION` migration that replaces only `commerce.arch021_release_feature_guard()`. It retains the Feature-row `FOR SHARE` lock, current prompt lookup, and empty-string fallback; it admits a historical prompt only when an already-persisted `CommerceReleaseFeature` row has both the same `featureId` and exact `behaviourPrompt`. Otherwise it continues to reject with SQLSTATE `23514`. Existing trigger identities and immutability remain intact.

Added a static validator that requires the fixed replacement function and checks the lock, current fallback, exact two-column historical match, rejection code, absence of bypass/trigger/schema changes, and one-function-only migration. Added a disposable `pgvector/pgvector:pg17` migration-chain rehearsal that proves predecessor rejection, corrected same-Feature historical acceptance, current-value acceptance, never-published and cross-Feature rejection, UPDATE/DELETE immutability, data preservation, and unchanged trigger topology. The runner uses one invocation-owned container on `--network none` and removes it in `finally`.

### Validation Results

`npm run prisma:validate`: passed. `npm run prisma:generate`: passed.

`npm run test:arch023-release-feature-snapshot-history`: passed.

`npm run test:arch023-release-feature-snapshot-history:postgres`: passed; full accepted migration chain through `20260929160000_arch023_merchant_knowledge_schema` applied, all predecessor/upgrade and negative cases passed, and invocation-owned container removed.

`npm run test:arch021-feature-capability-schema`: passed. `npm run test:arch021-feature-capability-migration`: passed (structural mode).

Changed-file diagnostics: no errors found for the migration, both new scripts, and `package.json`. `git diff --check`: passed. The initial Prisma validation attempt could not find Prisma because the prepared worktree had no `node_modules`; `npm ci` installed the existing lockfile dependencies without changing package manifests, after which validation and generation passed. The task-runner output noted 3 high-severity npm audit findings; no audit remediation or dependency changes were in scope.

### Deviations

The existing ARCH-021 validators required no edits: their schema validator inspects the accepted predecessor migration, and their migration validator's stale prompt is never-persisted text, so it remains correctly rejected under the new contract. The supplied launcher skill notation accepts `--definition` at the workflow level, but this installed launcher rejected that option; after its normal `--prepare` reported the task missing, the documented route-only exception was followed and the portable definition was materialized unchanged before preparing again.

### Assumptions

None beyond the accepted ARCH-021/ARCH-023 prerequisites above.

### Unresolved Issues

None at definition time.

### Architectural Concerns

None identified. No Commerce workaround, Prisma schema change, trigger bypass, release ancestry model, or retired Capability model was introduced.

### Physical Worktree and Launcher Evidence

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-DATABASE-004
parent branch: task/ARCH-023-DATABASE-004
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-DATABASE-004
implementation branch: task/ARCH-023-DATABASE-004
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
parent remote task branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
implementation remote task branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
git submodule sync --recursive: passed
git submodule update --init --recursive: passed
recursive submodule entries: none
dependency gate: passed (ARCH-021-DATABASE-003 and ARCH-023-DATABASE-001 complete)
```

### Commit Identities

Implementation commit: `0cdea8b` (`fix(database): allow immutable historical release feature snapshots`).

Parent definition-materialization commit: `5950ba78e428610e800e88e5ee7b86688f7ba4da`.

Parent launcher claim commit: `9c4d7dad1cb0f326a39f65cb3000dbe6536f58e7`.

Parent Completion Report commit: `4d0d5f1b` (`docs(database): submit DATABASE-004 attempt 1 for review`).

After push/fetch, implementation `HEAD` and `origin/task/ARCH-023-DATABASE-004` matched at `0cdea8b0a7f1ce61df67bcc80b6325e16d82e12f`; parent `HEAD` and `origin/task/ARCH-023-DATABASE-004` matched at `4d0d5f1b`. Both worktrees were clean after publication.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

DATABASE-004 satisfies the narrow correction contract authorised from COMMERCE-002 Attempt 3. The forward migration replaces only `commerce.arch021_release_feature_guard()` and preserves the predecessor `billing."Feature" ... FOR SHARE` lock, current `CommerceFeatureConfiguration.behaviourPrompt` lookup, missing-configuration empty-string fallback and SQLSTATE `23514` rejection.

Historical admission is bounded to an exact `CommerceReleaseFeature.behaviourPrompt` already persisted for the same `featureId`. The accepted rule therefore permits immutable successor-release preservation after current Feature authoring advances without making arbitrary stale text or another Feature's history valid.

The migration does not drop/recreate `CommerceReleaseFeature`, disable/recreate its triggers, add a bypass/session flag, alter the Prisma schema, or weaken `arch021_release_feature_immutable`. No release ancestry model or Commerce-side workaround is introduced.

The disposable PostgreSQL upgrade proof exercises the real accepted migration chain through `20260929160000_arch023_merchant_knowledge_schema`, demonstrates the predecessor `23514` rejection, applies DATABASE-004, then proves same-Feature historical acceptance, current-value acceptance, never-published/cross-Feature rejection, UPDATE/DELETE immutability, row preservation and unchanged trigger topology.

The submitted implementation identity is `0cdea8b0a7f1ce61df67bcc80b6325e16d82e12f`. The developer-supplied final parent-report identity is `b4305941d6287c6a60b8e85e21a0f74862b2c2ca`; the Completion Report's earlier `4d0d5f1b` entry is retained as historical pre-final-evidence publication.

### Reviewed Files

- `prisma/migrations/20260930200000_arch023_release_feature_snapshot_history/migration.sql`
- `scripts/validate-arch023-release-feature-snapshot-history.mjs`
- `scripts/test-arch023-release-feature-snapshot-history-postgres.mjs`
- `package.json`
- predecessor `prisma/migrations/20260929120000_arch021_feature_capability_simplification/migration.sql`
- `prisma/schema.prisma` and `package-lock.json` for no-change verification
- DATABASE-004 Completion Report and physical-worktree evidence

### Validation Reviewed

Submitted validation accepted:

- `npm run prisma:validate` — passed.
- `npm run prisma:generate` — passed.
- `npm run test:arch023-release-feature-snapshot-history` — passed.
- `npm run test:arch023-release-feature-snapshot-history:postgres` — passed with owned `pgvector/pgvector:pg17` cleanup.
- existing ARCH-021 Feature/Capability schema and migration validators — passed.
- changed-file diagnostics and `git diff --check` — passed.

Architect-side review additionally:

- confirmed `prisma/schema.prisma` and `package-lock.json` are unchanged from the pre-DATABASE-004 ARCH-023 baseline available in the review workspace;
- executed the static validator successfully against the submitted migration;
- mutation-probed removal of the historical same-`featureId` match, exact `behaviourPrompt` match and Feature `FOR SHARE` lock; each mutation was rejected by the validator;
- ran Node syntax checks for both new validation scripts.

The review environment did not provide a Docker daemon, so the PostgreSQL container proof was not independently rerun; the test implementation and recorded canonical-worktree result were inspected instead.

### Architecture Conformance

Conformant. DATABASE-004 changes only the database invariant that prevented an otherwise valid immutable successor snapshot. It preserves repository ownership, release immutability, current Feature-authoring protection, exact Tool-revision/member release guards and the direct ARCH-021 Feature/Capability model.

### Follow-up

Mark `ARCH-023-DATABASE-004` Complete / Accepted Attempt 1. The external database blocker on `ARCH-023-COMMERCE-002` is now satisfied.

The authoritative COMMERCE-002 Attempt 3 record lives on its own task branch, so it must be reconciled there from `blocked -> ready` with `attempt: 3` retained. Its next normal `/moda-task` claim becomes Attempt 4. Attempt 4 should preserve the existing Commerce implementation unless the accepted migration exposes a new defect, update the database submodule to the accepted DATABASE-004 revision, rerun the complete disposable PostgreSQL successor-preservation proof and final validation set, then return to review.
