---
id: ARCH-005-SHARED-004
architecture_id: ARCH-005
title: Publish Shopify international-context event contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 26
executor: copilot
claimed_at: 2026-09-05T22:30:29Z
attempt: 1
depends_on:
  - ARCH-005-SHARED-003
enables:
  - ARCH-005-BACKGROUND-001
created: 2026-09-05
updated: 2026-09-05T22:35:42Z
---

# Publish Shopify international-context event contract

## Architecture

This is the release gate for the architect-accepted SHARED-003 queue-contract
extension. It is intentionally separate from implementation.

## Objective

Publish the next compatible `@modainteract/moda-interact-shared` version that
contains the accepted optional Shopify V2 `internationalContext` event field.

## Context

Current published ARCH-005 base release:

```text
@modainteract/moda-interact-shared@0.6.1
```

The exact next version must be selected by the repository release mechanism and
recorded in the Completion Report.

## Scope

Release metadata and publication mechanics only.

## Out of Scope

- Runtime implementation changes.
- Consumer repository changes.
- Shopify producer changes.
- Re-running implementation tests/lint/typecheck/build already accepted under SHARED-003.
- Database changes.

## Requirements

Follow the architect publication-task protocol:

- verify SHARED-003 is Complete and architect-accepted;
- apply only release-specific version/lock metadata required by publication;
- publish the intended package version;
- verify the exact version is available from the intended registry;
- record package version/integrity evidence;
- do not continue into Background or Shopify adoption.

## Work Items

- [x] Confirm SHARED-003 is Complete and accepted.
- [x] Apply approved release version metadata.
- [x] Publish package.
- [x] Verify exact published package/version.
- [x] Record registry/integrity evidence.
- [x] Confirm no implementation source changed beyond release metadata.

## Interfaces / Contracts

Published contract:

```text
ShopifyRecoveryEventV2.internationalContext?: InternationalContext
```

## Dependencies

- ARCH-005-SHARED-003.

## Enables

- ARCH-005-BACKGROUND-001.

## Acceptance Criteria

- [x] SHARED-003 was architect-accepted before publication.
- [x] intended package version is published successfully.
- [x] exact registry version is verified.
- [x] release/integrity evidence is recorded.
- [x] no consumer repository is modified.
- [x] no unrelated implementation change is introduced.

## Validation

Publication mechanics only. Do not rerun the implementation validation suite
that belongs to SHARED-003.

## Implementation Notes

Consumer-first rollout is mandatory because older strict V2 parsers do not know
the new field. Background adopts this published version before Shopify emits
`internationalContext`.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`

### Work Completed

- Confirmed architect acceptance and completion of `ARCH-005-SHARED-003`
  before publication.
- Bumped the additive shared contract release from `0.6.1` to `0.6.2`.
- Published `@modainteract/moda-interact-shared@0.6.2` to the public npm
  registry with the `latest` tag.
- Preserved the existing package exports, including `./shopify` and
  `./internationalization`.
- Did not modify any consumer repository or implementation source beyond the
  release metadata.

### Validation Results

- `npm pack --dry-run --json`: passed; verified 42 package files, including
  `dist/shopify/index.d.ts`, `dist/shopify/index.js`,
  `dist/internationalization.d.ts`, and `dist/internationalization.js`.
- Package build during `prepack`: passed, including declaration generation.
- `npm publish --access public`: passed; published version `0.6.2`.
- `npm view @modainteract/moda-interact-shared@0.6.2 version dist.integrity
  --json`: passed; registry integrity:
  `sha512-/dDwRQqzWiZ1cO9sfCVZpg2ZVusztfca8PFJs9/zjIqCiVwdhWPISbSkeHEpM7PnhepMmmWy1KN9joB27vx75g==`.
- Clean temporary install of `@modainteract/moda-interact-shared@0.6.2`:
  passed; imported both Shopify recovery and internationalization entrypoints.

### Deviations

None.

### Assumptions

- `0.6.2` is the next compatible release after the published `0.6.1`.

### Unresolved Issues

None.

### Git / VCS

Release metadata is ready for developer commit/push. The repository agent did
not commit or push.

## Architect Review

### Review Status

Accepted

### Review Notes

The architect reviewed the supplied `moda-interact-shared` release workspace and
compared it with the previously accepted SHARED-003 workspace, not only the
Completion Report.

The publication task is correctly bounded to release metadata:

- `package.json` changes only the package version from `0.6.1` to `0.6.2`;
- `package-lock.json` changes only the corresponding root package version
  metadata;
- no runtime/shared-contract source changed between the accepted SHARED-003
  workspace and this publication workspace;
- the source being released still contains the accepted optional
  `ShopifyRecoveryEventV2.internationalContext` contract and the canonical
  internationalisation exports;
- the Completion Report records a successful package dry-run, prepack build,
  npm publication, registry version/integrity lookup, and clean temporary
  consumer installation;
- no consumer repository, commit, or push was performed by the repository
  agent.

Published release:

```text
@modainteract/moda-interact-shared@0.6.2
```

Recorded registry integrity:

```text
sha512-/dDwRQqzWiZ1cO9sfCVZpg2ZVusztfca8PFJs9/zjIqCiVwdhWPISbSkeHEpM7PnhepMmmWy1KN9joB27vx75g==
```

### Architectural Dependency Result

`ARCH-005-SHARED-004` is **Complete**.

All dependencies of `ARCH-005-BACKGROUND-001` are now Complete:

```text
ARCH-005-SHARED-004     Complete
ARCH-005-DATABASE-001   Complete
```

Therefore:

```text
ARCH-005-BACKGROUND-001   Ready
```

The rollout gate remains consumer-first. `ARCH-005-SHOPIFY-003` stays Pending
until BACKGROUND-001 is implemented and architect accepted. `MESSAGING-001` also
stays Pending because it depends on BACKGROUND-001.

The developer should commit/push the accepted shared implementation and release
metadata so repository source history matches the package already published to
the registry. This publication task itself is nevertheless complete because
publication and registry verification have already occurred.
