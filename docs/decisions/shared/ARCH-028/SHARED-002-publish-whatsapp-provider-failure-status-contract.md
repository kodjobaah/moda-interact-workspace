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
status: pending
priority: 21
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-SHARED-001
enables:
  - ARCH-028-BACKGROUND-001
  - ARCH-028-MESSAGING-001
created: 2026-10-03
updated: 2026-10-03
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

- [ ] Verify ARCH-028-SHARED-001 is Complete and architect-accepted.
- [ ] Record the accepted SHARED-001 implementation commit SHA.
- [ ] Verify checked-in Shared version equals the currently published npm version.
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

- [ ] SHARED-001 was Complete and architect-accepted before release metadata changed.
- [ ] The pre-release checked-in version exactly matched the public registry version.
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

- [ ] prerequisite acceptance check
- [ ] checked-in version vs public-registry baseline check
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

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

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

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
