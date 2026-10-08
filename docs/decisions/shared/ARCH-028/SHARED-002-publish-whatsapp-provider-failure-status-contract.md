---
id: ARCH-028-SHARED-002
architecture_id: ARCH-028
title: Publish WhatsApp provider-failure status contract
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
attempt: 2
depends_on:
  - ARCH-028-SHARED-001
enables:
  - ARCH-028-BACKGROUND-001
  - ARCH-028-MESSAGING-001
  - ARCH-028-SHARED-003
created: 2026-10-03
updated: 2026-10-08
---

# Publish WhatsApp provider-failure status contract

## Architecture

Architecture ID:

`ARCH-028`

Architecture document:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator:

`moda_architect`

## Objective

Publish exactly one compatible patch release of `@modainteract/moda-interact-shared` containing the architect-accepted `ARCH-028-SHARED-001` dual-version WhatsApp provider-status contract, verify the exact registry revision and clean consumer imports, record release evidence, and stop without changing implementation source or consumer repositories.

## Context

`ARCH-028-SHARED-001` owns the v2/v3 runtime-contract implementation and all implementation validation.

ARCH-028 Messaging and Background adoption must consume one exact published Shared revision. They must not depend on unpublished task-branch source, local workspace linking, copied schemas, or independently recreated provider-failure envelopes.

This is a publication/release gate only.

## Scope

Only release-specific work is authorised:

```text
verify SHARED-001 is Complete and architect-accepted
establish the checked-in package version against the public npm registry
bump exactly one compatible patch version
update release metadata only
publish @modainteract/moda-interact-shared
verify exact published version + integrity + tarball
verify the published billing subpath contains the accepted ARCH-028 exports
clean-install the exact published version outside the repository
verify runtime imports from the clean installation
record publication evidence
```

Expected normal changed files in `moda-interact-shared`:

```text
package.json
package-lock.json
```

No implementation source should change.

## Out of Scope

- Changing `src/billing.ts`, tests, validation scripts or implementation code.
- Correcting defects discovered in SHARED-001 inside this task.
- Rerunning SHARED-001 unit tests, typecheck or build merely to revalidate accepted implementation.
- Changing the v2/v3 schema design, bounds or compatibility contract.
- Database work.
- Messaging producer integration.
- Background consumer integration.
- Updating consumer package versions/lockfiles.
- Defining downstream Messaging/Background tasks.
- Publishing a minor or major version.
- Publishing more than once to work around an implementation defect.
- Modifying `docs/architecture/_index.md`.

## Requirements

### R1 — Prerequisite acceptance is mandatory

Before changing package metadata, verify from the durable task record:

```text
ARCH-028-SHARED-001.status = complete
ARCH-028-SHARED-001 Architect Review = Accepted
```

Record the accepted SHARED-001 implementation commit SHA in this task's Completion Report.

If SHARED-001 is not Complete and architect-accepted, STOP without publishing.

### R2 — Establish the registry/version baseline deterministically

Read the checked-in version from:

```text
moda-interact-shared/package.json
```

and query the public npm registry:

```bash
npm view @modainteract/moda-interact-shared version \
  --registry=https://registry.npmjs.org
```

The checked-in package version MUST equal the currently published registry version before this task performs its bump.

If they differ:

```text
STOP
record the baseline conflict
return to moda_architect
do not guess which version wins
do not publish
```

### R3 — Bump exactly one patch version

Use semantic patch versioning only:

```text
X.Y.Z -> X.Y.(Z+1)
```

Update only release/version metadata required by the repository's normal npm release process.

Normal expected changes:

```text
package.json
package-lock.json
```

Do not choose a minor or major release.

### R4 — Publish using the repository's existing npm convention

Publish from `moda-interact-shared` using:

```bash
npm publish --access public
```

The package's existing `prepack` build is part of the publication mechanism and is allowed.

Do not manually rerun implementation tests, typecheck or build as a second validation pass.

If publication reveals a defect requiring source/test changes:

```text
STOP
do not edit implementation source in SHARED-002
return the defect to moda_architect
```

### R5 — Verify the exact published registry revision

After publication, query exactly the new version:

```bash
npm view @modainteract/moda-interact-shared@<NEW_VERSION> \
  version dist.integrity dist.tarball \
  --json \
  --registry=https://registry.npmjs.org
```

Record all three values in the Completion Report.

The returned version must exactly equal the version written to `package.json`.

### R6 — Verify the published billing entrypoint exists

Use the publication output and/or:

```bash
npm pack --dry-run
```

to verify the published package contains at least:

```text
dist/billing.js
dist/billing.d.ts
```

Do not accept publication if the billing runtime/declaration entrypoint is absent.

### R7 — Clean-install the exact published version

Create a temporary empty consumer directory outside the repository worktree.

Install exactly:

```text
@modainteract/moda-interact-shared@<NEW_VERSION>
```

from `https://registry.npmjs.org`.

The clean consumer must not resolve the local Shared repository through a workspace/symlink/file dependency.

### R8 — Verify the ARCH-028 billing exports from the clean install

From the clean consumer, import:

```text
@modainteract/moda-interact-shared/billing
```

and verify the accepted SHARED-001 runtime surface is available, including:

```text
WHATSAPP_PROVIDER_STATUS_V2_SCHEMA_VERSION === 2
WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION === 3
WhatsAppProviderFailureEvidenceSchema
NormalizedWhatsAppStatusV2Schema
NormalizedWhatsAppStatusV3Schema
NormalizedWhatsAppStatusSchema
parseNormalizedWhatsAppStatus
safeParseNormalizedWhatsAppStatus
```

Also perform a bounded runtime smoke proving the installed canonical parser accepts:

1. one valid legacy v2 provider-status payload; and
2. one valid v3 `FAILED` payload carrying `failure.providerCode`.

This is package-consumption verification, not a rerun of SHARED-001's implementation test suite.

### R9 — Do not start consumer integration

After the package is published and verified, STOP.

Do not update:

```text
moda-interact-messaging/package.json
moda-interact-background/package.json
consumer lockfiles
consumer source
```

Consumer adoption remains separate architecture work.

## Work Items

- [x] Verify ARCH-028-SHARED-001 is Complete and architect-accepted.
- [x] Record the accepted SHARED-001 implementation commit SHA.
- [x] Verify checked-in Shared version equals the currently published npm version.
- [ ] Bump exactly one patch version in release metadata only.
- [ ] Publish with the existing public npm convention.
- [ ] Verify exact published version, integrity and tarball metadata.
- [ ] Verify the billing runtime/declaration entrypoint is present in the published package.
- [ ] Clean-install the exact published version outside the repository worktree.
- [ ] Verify the accepted ARCH-028 runtime exports and v2/v3 parser smoke from the clean install.
- [ ] Confirm no implementation source or consumer repository was modified.
- [ ] Complete the publication Completion Report and return to `moda_architect` at `status: review`.

## Interfaces / Contracts

Published package:

`@modainteract/moda-interact-shared@<NEW_VERSION>`

Published subpath:

`@modainteract/moda-interact-shared/billing`

Implementation owner:

`ARCH-028-SHARED-001`

Publication owner:

`ARCH-028-SHARED-002`

Future consumers:

- `moda-interact-background` must adopt the exact published dual-version parser before v3 producer rollout.
- `moda-interact-messaging` must use the same exact published package before emitting v3 failure evidence.

No consumer may copy or locally redefine the ARCH-028 provider-status contract.

## Dependencies

- `ARCH-028-SHARED-001`

## Enables

- `ARCH-028-BACKGROUND-001`

BACKGROUND-001 also depends on `ARCH-028-DATABASE-001`. After both prerequisites are Complete, Background adopts the exact published dual-version parser before Messaging begins producing v3.

## Acceptance Criteria

- [x] SHARED-001 was Complete and architect-accepted before release metadata changed.
- [x] The pre-release checked-in version exactly matched the public registry version.
- [ ] Exactly one patch version was published.
- [ ] Only release metadata changed in the Shared repository.
- [ ] `npm publish --access public` succeeded once for the intended revision.
- [ ] The exact new version is visible on the public npm registry.
- [ ] `dist.integrity` and `dist.tarball` are recorded.
- [ ] Published package contains `dist/billing.js` and `dist/billing.d.ts`.
- [ ] A clean external consumer installs the exact new version without local workspace resolution.
- [ ] The clean install exposes all accepted ARCH-028 billing runtime symbols.
- [ ] The clean installed canonical parser accepts both the representative v2 event and v3 FAILED event with bounded failure evidence.
- [ ] No Shared implementation source/test change was made in this task.
- [ ] No Messaging/Background consumer change was made in this task.
- [ ] No implementation tests/typecheck/build were manually rerun merely to revalidate accepted source.

## Validation

Publication validation only:

- [x] prerequisite acceptance check
- [x] checked-in version vs public-registry baseline check
- [ ] `npm publish --access public`
- [ ] exact-version `npm view ... version dist.integrity dist.tarball --json`
- [ ] package-content verification for `dist/billing.js` and `dist/billing.d.ts`
- [ ] clean external install of the exact published revision
- [ ] clean-install import/runtime smoke for the accepted ARCH-028 billing exports and representative v2/v3 events
- [ ] `git diff --check`

Do **not** list or rerun SHARED-001's implementation tests, typecheck or build here. The publication `prepack` build is allowed because it is part of npm publication mechanics.

## Stop Condition

After the defined Work Items, Acceptance Criteria and publication Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin Background or Messaging consumer integration.

## Implementation Notes

- Treat `package.json` and `package-lock.json` as the normal release-metadata surface.
- If the checked-in version and public registry baseline differ, do not attempt to reconcile them inside this task.
- If `npm publish` reports the target version already exists, STOP and reconcile with `moda_architect`; do not select another version opportunistically.
- Never print/persist npm credentials or registry authentication material in the task report.
- Use a temporary clean consumer directory outside the Shared worktree for import verification.

## Completion Report

### Status

Blocked during Attempt 2 before release metadata changes or publication. Shared
main contains the accepted SHARED-001 commit, but the parent workspace gitlink
still points to an older Shared commit that does not contain it.

### Files Changed

Only this task report in the parent worktree. No Shared package files changed.

### Work Completed

- Verified the durable `ARCH-028-SHARED-001` record is `complete` with
  `Accepted — Attempt 1 (2026-10-08)`.
- Accepted implementation commit:
  `1875bf434c4185f365e64c96c26ff3dffbde28db`.
- Shared `origin/main` is `92d71fd35b360872ea237677aa89d64e6556d704`; the
  accepted implementation commit is its ancestor.
- The parent workspace `origin/main`, the current task branch, and the SHARED-002
  implementation worktree's parent gitlink all pin Shared at
  `a6ebfb3daf75bbd9265b42c138898b53dfba087f` (ARCH-020-SHARED-002). This commit
  is an ancestor of Shared main but does not contain accepted commit
  `1875bf434c4185f365e64c96c26ff3dffbde28db`.
- Checked-in package version is `1.3.0`; public npm registry version is `1.3.0`.
- On 2026-10-08 the developer explicitly requested `reopen`, noting SHARED-001
  is complete and merged and that its evidence is in the codebase. This override
  reopens lifecycle state only; it does not assert registry/version checks or
  publication have passed.
- No package version, lockfile, registry release, or consumer repository was
  changed. No publish was attempted.

### Validation Results

- Prerequisite acceptance check: passed; SHARED-001 is complete and architect-
  accepted.
- Accepted SHARED-001 implementation commit `1875bf434c4185f365e64c96c26ff3dffbde28db`
  is integrated in Shared `origin/main` at `92d71fd35b360872ea237677aa89d64e6556d704`.
- Release baseline check passed: checked-in version `1.3.0` equals npm registry
  version `1.3.0`.
- Parent integration gate remains unmet: parent main/task gitlink
  `a6ebfb3daf75bbd9265b42c138898b53dfba087f` does not contain the accepted
  implementation commit. SHARED-001 Architect Review Follow-up requires the
  parent gitlink to reference the merged implementation-main commit before
  publication.
- Registry version comparison, patch bump, publication, registry integrity /
  tarball verification, package-content verification and clean external
  consumer install remain outstanding because the parent integration gate is
  unmet. No package metadata or registry side effect occurred.
- Direct dependents `ARCH-028-MESSAGING-001`, `ARCH-028-SHARED-003`, and
  `ARCH-028-BACKGROUND-001` are all `pending` and unclaimed; their states are
  unchanged. Reopening this task does not make them eligible because this task
  is not Complete.
- `git diff --check`: passed for the reopen update.

### Deviations

Attempt 2 stopped before package metadata changes and publication because the
accepted Shared main commit is not yet represented by the parent workspace
gitlink. The durable developer reopen was honored; this agent did not change
that developer-owned integration surface.

### Assumptions

No additional assumption beyond the task's stated registry and acceptance
requirements.

### Unresolved Issues

The developer must update/integrate the parent workspace gitlink to the accepted
Shared main revision, then `moda_architect` must re-gate and return this task to
`ready`. Publication must not proceed before then.

## Developer Override - Reopen

- Date: 2026-10-08.
- Previous state: `blocked`, Attempt 1, executor `copilot`, claimed at
  `2026-10-08T13:06:34Z`.
- Developer instruction: reopen the task, noting SHARED-001 is marked Complete
  and its implementation/evidence is merged into main in the codebase.
- Transition: `status: ready`, `executor: null`, `claimed_at: null`; attempt
  remains `1`. This is not a claim; the next normal `/moda-task` preparation
  will claim Attempt 2 if its gate passes.
- Previous review/report and integration evidence are preserved. No package
  metadata, implementation source, consumer repository, or registry state was
  changed by this override.

## Attempt 2 Execution Record

- Launcher claim: Attempt 2, executor `copilot`, claimed
  `2026-10-08T13:44:56Z`; claim commit
  `13d4ca4e22bd99ce5e9703f847fe201c39dd4ac8` was pushed.
- Prepared parent worktree head: `54f8b98b9e937a06abb579e806b61b2e4b489eb7`;
  prepared implementation worktree head:
  `92d71fd35b360872ea237677aa89d64e6556d704`.
- Parent and implementation worktrees were reused at the launcher-supplied
  canonical paths; recursive submodule sync/update passed, with no nested
  submodule entries.
- This agent cleared the active claim and set `status: blocked`, preserving
  `attempt: 2`. No package release action occurred.

### Architectural Concerns

No new architectural concern is introduced by the lifecycle reopen.

## Architect Review

### Review Status

Pending

### Review Notes

- **Conditional integration re-gate following blocked Attempt 2.** The developer must first merge the accepted parent `task/ARCH-028-SHARED-001` into parent `main`, push the result, and verify parent `origin/main` records Shared gitlink `92d71fd35b360872ea237677aa89d64e6556d704`. Do not apply this lifecycle change while parent `origin/main` still records `a6ebfb3daf75bbd9265b42c138898b53dfba087f`.
- Accepted Shared implementation `1875bf434c4185f365e64c96c26ff3dffbde28db` is already present in Shared `origin/main` at `92d71fd35b360872ea237677aa89d64e6556d704`. The accepted SHARED-001 parent task branch records that same gitlink. The missing integration is parent-main Git history, not another Shared source change.
- Attempt 2 stopped before any package metadata change or npm publication; its Completion Report remains intact as historical evidence. Checked-in and public-registry versions were both `1.3.0` at that stop point. This re-gate is not acceptance of publication and does not establish that any release occurred.
- After the verified parent-main integration and synchronization of this parent task branch, restore `status: ready`, preserve `attempt: 2`, and keep `executor` and `claimed_at` null. The deterministic launcher must claim Attempt 3 itself.

### Reviewed Files

- `docs/decisions/shared/ARCH-028/SHARED-002-publish-whatsapp-provider-failure-status-contract.md` (Attempt 2 report and lifecycle).
- Parent `moda-interact-shared` gitlink references on `main`, `task/ARCH-028-SHARED-001` and `task/ARCH-028-SHARED-002` (remote Git tree evidence).

### Validation Reviewed

- Shared accepted commit ancestry and parent gitlink differences inspected; publication remains unperformed.
- Parent `origin/main` gitlink verification must pass before applying this conditional decision. No publication test, version bump or registry validation is represented as passing here.

### Architecture Conformance

- Publication-only boundary retained. No implementation code, npm package metadata, downstream task, or `_index.md` change is authorised by this reconciliation.

### Follow-up

- Once the parent-main gitlink integration is verified, merge parent `origin/main` into `task/ARCH-028-SHARED-002`, apply this patch, commit and push the task-only lifecycle change, then invoke `/moda-task ARCH-028-SHARED-002` to claim Attempt 3.
- Execute only the task's publication-specific validation and release steps. Do not rerun accepted SHARED-001 implementation tests or perform Background/Messaging consumer integration under this task.
- Keep `ARCH-028-SHARED-003`, `ARCH-028-BACKGROUND-001`, `ARCH-028-MESSAGING-001` and terminal system testing gated until SHARED-002 is architect-accepted Complete.
