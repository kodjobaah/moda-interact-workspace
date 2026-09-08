---
id: ARCH-007-SHARED-004
architecture_id: ARCH-007
title: Publish corrected provider-status v2 Shared release 0.7.4
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 63
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-SHARED-003
enables:
  - ARCH-007-MESSAGING-001
created: 2026-09-07
updated: 2026-09-07T22:28:42+01:00
---

# ARCH-007-SHARED-004: Publish corrected provider-status v2 Shared release 0.7.4

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Publish the architect-accepted SHARED-003 provider-status v2 correction as the
exact npm release `@modainteract/moda-interact-shared@0.7.4`, then prove a clean
consumer can load the corrected contract.

## Scope

Shared package version/lock metadata, build/package validation, npm publication,
clean-consumer exact-version smoke validation, task record.

## Out of Scope

- Any provider-status source/schema change beyond architect-accepted SHARED-003.
- Consumer repository edits.
- MESSAGING-001 rework.

## Requirements

- Begin only after SHARED-003 is architect-accepted Complete.
- Verify the runtime/provider-status source is exactly the accepted SHARED-003
  implementation before versioning.
- Bump `package.json` and `package-lock.json` consistently to exactly `0.7.4`.
- Build/test before publication.
- Publish exactly `@modainteract/moda-interact-shared@0.7.4`.
- From a clean temporary consumer install exact `0.7.4` and verify:
  - package import succeeds;
  - provider-status schema version is `2`;
  - valid event requires `providerAccountId`, `providerPhoneNumberId`,
    `providerMessageId`;
  - normalized provider-status schema does not require/accept `shopId`;
  - existing billing exports used by ARCH-007 remain importable.
- Record publication evidence without secrets/tokens.
- Do not modify Messaging/Background consumers in this task.

## Work Items

- [x] Verify SHARED-003 accepted source.
- [x] Bump package + lock metadata to 0.7.4.
- [x] Typecheck/build/test/package validation.
- [x] Publish 0.7.4 once.
- [x] Perform clean-consumer exact-version smoke validation.
- [x] Return only SHARED-004 to `review` and STOP.

## Interfaces / Contracts

Published artifact:

```text
@modainteract/moda-interact-shared@0.7.4
```

Provider-status contract: schema v2 from SHARED-003.

## Dependencies

SHARED-003 must be architect-accepted Complete.

## Enables

- ARCH-007-MESSAGING-001

## Acceptance Criteria

- [x] npm 0.7.4 contains exactly the accepted provider-status v2 contract.
- [x] package/lock metadata both equal 0.7.4.
- [x] clean exact-version consumer smoke test passes.
- [x] no consumer repository is modified.
- [x] publication evidence is recorded safely.

## Validation

Use the repository's declared typecheck/build/test/package verification plus a
clean exact-version consumer install and `git diff --check`.

## Implementation Notes

Do not republish 0.7.3. Do not skip directly to consumer implementation.

Luna deterministic-execution guardrails:

- Publication only after SHARED-003 architect acceptance.
- Do not change accepted source while publishing.
- Do not modify another repository.
- Do not run git commit/push unless the developer explicitly authorizes it.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- `docs/decisions/shared/ARCH-007/SHARED-004-publish-provider-status-v2-release.md`

### Work Completed

- Verified SHARED-003 is architect-accepted Complete and the owned source/test changes match the accepted v2 contract exactly.
- Bumped package and lock metadata consistently from `0.7.3` to `0.7.4` without changing provider-status source.
- Built and published exactly `@modainteract/moda-interact-shared@0.7.4` with public access.
- Verified a clean temporary consumer can import the package root and billing entrypoint, parse schema v2 with the three required provider identities, reject missing identities and reject `shopId`, while retaining billing helper exports.

### Validation Results

- `npm run typecheck` — passed.
- `npm test` — 104 passed, 1 skipped because `TEST_REDIS_URL` is not configured.
- `npm run build` — passed with ESM and declaration output.
- `npm pack --dry-run` — passed; exact package `@modainteract/moda-interact-shared@0.7.4`, 58 files.
- `npm publish --access public` — published exactly `@modainteract/moda-interact-shared@0.7.4`; no secret/token output recorded.
- Clean temporary consumer install of exact `@modainteract/moda-interact-shared@0.7.4` — passed schema/import smoke validation.
- `git diff --check` — passed.

### Deviations

None. The package source remains the architect-accepted SHARED-003 implementation; only release metadata and the task report changed.

### Assumptions

The published npm registry artifact is the source of truth for the clean-consumer smoke test; no consumer repository was edited.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
