---
id: ARCH-005-SHARED-002
architecture_id: ARCH-005
title: Publish internationalisation shared contract release
task_kind: release
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-05T19:07:34Z
attempt: 1
depends_on:
  - ARCH-005-SHARED-001
enables:
  - ARCH-005-SHOPIFY-001
  - ARCH-005-BACKGROUND-001
  - ARCH-005-MESSAGING-001
  - ARCH-005-SHOPIFY-002
created: 2026-09-05
updated: 2026-09-05T19:15:00Z
---

# Publish internationalisation shared contract release

## Objective

Publish the architect-accepted international-context primitives for adoption by
Shopify, Background and Messaging.

## Requirements

- publish the next compatible `@modainteract/moda-interact-shared` version;
- include only architect-accepted SHARED-001 changes;
- verify package exports and `npm pack` contents;
- record exact package version/integrity evidence;
- confirm the published package can be installed and imported;
- preserve existing exports.

## Acceptance criteria

- [x] SHARED-001 is architect-accepted before publication.
- [x] package tests/build/typecheck pass.
- [x] package contents contain the intended exports.
- [x] registry publication succeeds.
- [x] published version is recorded.
- [x] consumer repositories are not modified by this task.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`

### Work Completed

- Bumped the additive shared contract release from `0.6.0` to `0.6.1`.
- Published `@modainteract/moda-interact-shared@0.6.1` to the public npm
  registry with the `latest` tag.
- Preserved the existing root and subpath exports, including
  `./internationalization`.
- Did not modify any consumer repository.

### Validation Results

- Full `npm test`: 72 passed, 1 skipped because `TEST_REDIS_URL` is not
  configured for the existing BullMQ integration test.
- `npm run typecheck`: passed.
- `npm run build`: passed, including declaration generation.
- `npm pack --dry-run --json`: verified 42 intended package files, including
  `dist/internationalization.js` and `dist/internationalization.d.ts`.
- Published package integrity:
  `sha512-nU6mf4bVEJezkJ5g4KtJj8Rh38IMfJlYMEPvW9Hmr4n02wHPhQxq2CbsqJEezSv2R4ZlxStKtMkTNU9LFATRvA==`.
- Temporary consumer install of `@modainteract/moda-interact-shared@0.6.1`
  succeeded, and the internationalization subpath import was verified.

### Deviations

None.

### Assumptions

- `0.6.1` is the next compatible additive release after the published `0.6.0`.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

The architect reviewed the supplied `moda-interact-shared` release workspace
directly and compared it with the previously accepted SHARED-001 workspace.

The release is appropriately narrow.

Between the accepted SHARED-001 workspace and this release workspace:

```text
package.json
  version: 0.6.0 -> 0.6.1

package-lock.json
  root version: 0.6.0 -> 0.6.1

src/internationalization.ts
  no change

src/internationalization.test.ts
  no change
```

No additional internationalisation contract behavior was introduced after
SHARED-001 architect acceptance.

### Package Surface Review

The published package metadata retains the existing root and subpath exports:

```text
.
./internationalization
./shopify
./shopify/node
./logging
./logging/node
./observability
./observability/node
./observability/bullmq
./observability/genai
```

`tsup.config.ts` continues to build the matching entry points, including:

```text
internationalization -> src/internationalization.ts
```

The package remains `dist`-only for publication.

### Release Evidence Reviewed

The Completion Report records successful publication of:

```text
@modainteract/moda-interact-shared@0.6.1
```

with registry integrity:

```text
sha512-nU6mf4bVEJezkJ5g4KtJj8Rh38IMfJlYMEPvW9Hmr4n02wHPhQxq2CbsqJEezSv2R4ZlxStKtMkTNU9LFATRvA==
```

and reports:

```text
72 tests passed
1 existing Redis-dependent test skipped because TEST_REDIS_URL is absent
typecheck passed
build/declarations passed
npm pack dry-run verified 42 intended files
temporary consumer install succeeded
internationalization subpath import succeeded
consumer repositories were not modified
```

The supplied workspace itself confirms the release version is `0.6.1`, the
lockfile agrees, and the architect-accepted SHARED-001 implementation is
unchanged.

### Architecture Conformance

Accepted.

This task owns publication only. It does not modify Shopify, Background,
Messaging, Database, Admin or other consumer repositories.

The accepted release is now available for later ARCH-005 consumer-adoption
tasks.

### Result

`ARCH-005-SHARED-002` is **Complete**.

There is no remaining Shared implementation task for ARCH-005.

The next currently executable ARCH-005 task remains:

```text
ARCH-005-DATABASE-001
```

`SHOPIFY-001` remains dependency-gated by `DATABASE-001`, so publication alone
does not make it executable.

No commit or push was performed by the task.
