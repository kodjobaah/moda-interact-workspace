---
id: ARCH-004-SHARED-002
architecture_id: ARCH-004
title: Publish cart activity shared contract release
task_kind: release
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-05T14:16:26Z
attempt: 1
depends_on:
  - ARCH-004-SHARED-001
enables:
  - ARCH-004-SHOPIFY-001
  - ARCH-004-BACKGROUND-001
created: 2026-09-05
updated: 2026-09-05
---

# Publish cart activity shared contract release

## Objective

Publish the architect-accepted `cart.activity` contract so Shopify and
Background can adopt the same canonical package version.

## Requirements

- publish the next compatible `@modainteract/moda-interact-shared` version
  containing accepted ARCH-004-SHARED-001;
- preserve existing package exports;
- verify the package contains the Shopify v2 schema/type/queue-contract changes;
- verify `npm pack`/package contents before publication;
- do not publish an unreviewed SHARED-001 implementation;
- record the exact published package version and integrity evidence in the task
  report.

## Out of scope

Consumer dependency bumps belong to their repository tasks.

## Acceptance criteria

 [x] accepted contract is packaged.
 [x] package exports remain valid.
 [x] package tests/build/typecheck pass.
 [x] published version is recorded.
 [x] registry package can be installed/resolved.
 [x] no consumer source is modified by this task.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- `docs/decisions/shared/ARCH-004/SHARED-002-publish-cart-activity-contract.md`

### Work Completed

- Bumped the accepted additive shared contract release from `0.5.0` to
  `0.6.0`.
- Verified the package contains the Shopify v2 cart activity schema/type,
  union exports, type guard, ordering helper, and queue contract in the built
  Shopify entrypoint.
- Published `@modainteract/moda-interact-shared@0.6.0` to the configured public
  npm registry with the `latest` tag.

### Validation Results

- `npm run typecheck`: passed.
- `npm test`: 66 passed, 1 skipped because `TEST_REDIS_URL` is not configured
  for the live BullMQ propagation test.
- `npm run build`: passed.
- `npm pack --dry-run --json`: passed; 37 files, package size 48.5 kB,
  shasum `571669c11d6cab5af3cae77a09e685f3f6029eb1`, integrity
  `sha512-zXfRUxPaEtCfxTzvH8H6d3igwL7jcPk66b370YuElZUWrtjiNrpehLbzeZkyg+ARJkCPkXyt1ojdjt3NCJitsw==`.
- Temporary npm install and scoped import of `@modainteract/moda-interact-shared@0.6.0`:
  passed; resolved `cart.activity` and `cart-activity` exports.
- `npm view @modainteract/moda-interact-shared@0.6.0 version dist.integrity dist.shasum`:
  confirmed version and integrity metadata.
- `git diff --check`: pending final check after this report update.

### Deviations

None.

### Assumptions

The accepted additive v2 contract uses `0.6.0` as the next compatible minor
release from the currently published `0.5.0`.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Git / VCS

Package publication completed as required. Repository agent did not commit or
push; source and release metadata remain ready for developer commit.

## Architect Review

### Review Status

Accepted

### Review Notes

Architect reviewed the supplied release workspace directly.

Accepted release:

```text
@modainteract/moda-interact-shared@0.6.0
```

The uploaded package metadata and lockfile both identify version `0.6.0`. The
release report records successful packaging, registry publication, temporary
registry installation and scoped import of the accepted `cart.activity` and
`cart-activity` exports.

Reviewed publication evidence:

```text
package version: 0.6.0
package files:   37
shasum:          571669c11d6cab5af3cae77a09e685f3f6029eb1
integrity:       sha512-zXfRUxPaEtCfxTzvH8H6d3igwL7jcPk66b370YuElZUWrtjiNrpehLbzeZkyg+ARJkCPkXyt1ojdjt3NCJitsw==
```

Validation evidence records:

- 66 tests passed;
- 1 Redis-dependent test skipped because `TEST_REDIS_URL` was unset;
- typecheck passed;
- build passed;
- dry-run package inspection passed;
- registry install/import passed;
- final `git diff --check` passed.

No consumer repository was modified by this release task, and no commit or push
was performed by the agent.

### Architecture Conformance

Conforms. The accepted cart activity contract is now available to consumer
repositories through shared package version `0.6.0`.

### Result

`ARCH-004-SHARED-002` is Complete.

The following tasks may advance in parallel:

```text
ARCH-004-SHOPIFY-001
ARCH-004-BACKGROUND-001
```

