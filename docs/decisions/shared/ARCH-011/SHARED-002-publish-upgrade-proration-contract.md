---
id: ARCH-011-SHARED-002
architecture_id: ARCH-011
title: Publish the accepted ARCH-011 upgrade and proration Shared contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: automatic
status: pending
priority: 12
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-SHARED-001
enables:
- ARCH-011-BACKGROUND-002
- ARCH-011-SHOPIFY-001
- ARCH-011-ADMIN-001
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-011-SHARED-002: Publish the accepted ARCH-011 upgrade and proration Shared contract

## Objective

Publish the architect-accepted `ARCH-011-SHARED-001` package exactly once using the repository's next valid semantic version. This is a publication-only task.

## Preconditions

Before changing package metadata:

1. `ARCH-011-SHARED-001` is architect-accepted Complete;
2. determine current local package version and npm `latest`;
3. choose the next **minor** version because ARCH-011 adds public billing primitives without intentionally removing the accepted ARCH-010 API;
4. prove the target version does not already exist in npm.

Do not hard-code a version from this task document if intervening releases changed `latest`. If local main, package metadata and npm registry disagree, STOP and return evidence to `moda_architect`; do not guess the next version.

## Publication steps

Use the accepted ARCH-010 publication pattern:

```text
1. update package.json + package-lock.json only for version metadata;
2. npm pack --dry-run --json;
3. inspect built runtime/declarations for all ARCH-011 exports;
4. prove retained ARCH-010 exports still exist;
5. npm publish exactly once;
6. wait only for normal registry propagation checks in this execution;
7. verify version, latest, tarball and dist.shasum;
8. verify registry shasum equals pre-publication packed artifact;
9. commit/push final package metadata according to repository workflow;
10. return exact evidence.
```

Required ARCH-011 artifact exports include the accepted names/types for:

```text
canonical topology validation
plan direction classification
target billing-period entitlement calculation
additional included-credit grant calculation
```

Use the exact names implemented/accepted in SHARED-001; do not rename during publication.

## Forbidden changes

Do not:

- refactor SHARED-001 semantics;
- change tests to repair an implementation issue;
- modify consumer repositories;
- publish a second corrective version in the same task;
- remove accepted ARCH-010 exports.

If the packed artifact is wrong, STOP before publication and return to architect/implementation correction.

## Validation / evidence

Record at minimum:

```text
pre-publication npm view target-version => absent
local old -> new version
npm pack --dry-run artifact name/version/shasum
required export scan
retained ARCH-010 export scan
npm publish result
post-publication version
post-publication latest
post-publication dist.tarball
post-publication dist.shasum
shasum equality
final Git commit
```

## Completion Report

### Status
Not started.

### Architect Review
Pending.
