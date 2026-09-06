---
id: ARCH-005-SHARED-006
architecture_id: ARCH-005
title: Publish shared ICU internationalisation runtime
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 28
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-005-SHARED-005
enables:
  - ARCH-005-SHOPIFY-002
  - ARCH-005-ADMIN-001
created: 2026-09-06
updated: 2026-09-06
---

# Publish shared ICU internationalisation runtime

## Objective

Publish the architect-accepted SHARED-005 runtime as the next compatible
`@modainteract/moda-interact-shared` release and verify the exact revision that
Shopify and Admin must consume.

## Context

Current accepted published ARCH-005 Shared release before this task:

```text
@modainteract/moda-interact-shared@0.6.2
```

SHARED-005 changes runtime implementation/API under the established
internationalisation boundary. Consumer tasks remain blocked/pending until an
exact published revision exists.

## Requirements

Follow the Shared publication protocol:

- verify SHARED-005 is Complete and architect-accepted;
- apply only required release/version/lock metadata;
- publish the intended compatible package version;
- verify the exact version from the intended registry;
- verify the published package contains the ICU runtime and declarations;
- perform a clean temporary install/import of the internationalisation entrypoint;
- record version and integrity evidence;
- do not modify Shopify or Admin from this task.

## Acceptance criteria

- [x] SHARED-005 is accepted before publication.
- [x] exact package version is published and registry-verified.
- [x] ICU runtime is present through the published internationalisation entrypoint.
- [x] declarations/types are present.
- [x] clean install/import succeeds.
- [x] version/integrity evidence is recorded.
- [x] no consumer repository changes are made.

## Enables

Only after architect acceptance of this publication task may:

```text
ARCH-005-SHOPIFY-002 -> Ready
ARCH-005-ADMIN-001   -> Ready
```

The exact published version must be recorded in those consumer Completion
Reports when they adopt it.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`

The existing implementation/test changes in the shared worktree were produced
by the accepted SHARED-005 task and were not modified by this publication task.

### Work Completed

- Verified `ARCH-005-SHARED-005` was complete and architect-accepted before
  publication.
- Bumped the compatible shared package release from `0.6.2` to `0.6.3`.
- Published `@modainteract/moda-interact-shared@0.6.3` to npm with the latest
  tag and public access.
- Published tarball contains the ICU runtime JavaScript entrypoint and
  `dist/internationalization.d.ts`; npm reported 42 package files.
- No Shopify, Admin, or other consumer repository was modified.

### Validation Results

- `npm publish --access public`: passed; prepack build and declaration build
  passed, published `0.6.3`.
- `npm view @modainteract/moda-interact-shared@0.6.3 version dist.integrity
  --json --registry=https://registry.npmjs.org`: passed.
- Registry integrity:
  `sha512-QdGfpV+hX5ut/vmR+RD3fQ/Tyy978A1J58hVf9+Ro2f6jq+f09jB4Jf5fPFxzgsAIsXx0/ftO+FChpa+w1cAAg==`.
- Clean temporary install of `@modainteract/moda-interact-shared@0.6.3`: passed;
  verified `dist/internationalization.d.ts` and imported/used
  `@modainteract/moda-interact-shared/internationalization`.

### Deviations

None.

### Assumptions

- `0.6.3` is the next compatible patch release after the published `0.6.2`.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Git / VCS

Release metadata is ready for developer commit/push. The repository agent did
not commit or push.

## Architect Review

### Review Status

Accepted.


### Review Notes

Accepted. Publication metadata is limited to the compatible 0.6.3 version bump. The recorded registry verification, integrity evidence and clean public-subpath install satisfy the publication contract. Consumer repositories were not modified by this task.

### Published Revision

```text
@modainteract/moda-interact-shared@0.6.3
```

Registry integrity recorded by the publication task:

```text
sha512-QdGfpV+hX5ut/vmR+RD3fQ/Tyy978A1J58hVf9+Ro2f6jq+f09jB4Jf5fPFxzgsAIsXx0/ftO+FChpa+w1cAAg==
```

### Dependency Result

```text
ARCH-005-SHOPIFY-002 -> Ready (next claim Attempt 5)
ARCH-005-ADMIN-001   -> Ready (first claim Attempt 1)
```
