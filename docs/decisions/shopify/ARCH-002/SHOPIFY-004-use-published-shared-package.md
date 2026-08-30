---
id: ARCH-002-SHOPIFY-004
architecture_id: ARCH-002
title: Use published shared package in Shopify application
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-001
enables:
  - ARCH-002-GATEWAY-005
created: 2026-08-29
updated: 2026-08-29
---

# Use Published Shared Package in Shopify Application

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Change the committed deployable dependency boundary in `moda-interact` so the
canonical cross-service package resolves from the published npm artifact:

```text
@modainteract/moda-interact-shared
```

rather than:

```text
file:../moda-interact-shared
```

The result must be deployable identically in both ARCH-002 test and production.

## Context

The original `file:` dependency required the sibling shared repository to exist
inside the build context.

ARCH-002 now uses a versioned published npm artifact as the deployed
cross-service dependency boundary.

A public package version is already known to exist, but this task must verify the
artifact against the consumer's **current** imports/contracts before selecting
it.

Do not assume an older published version is compatible merely because it can be
installed.

## Scope

Within `moda-interact`:

- inspect current shared-package imports/usage;
- inspect available published package metadata/contents;
- select an exact published version that satisfies current accepted consumer
  requirements;
- replace the committed `file:` dependency with that exact npm version;
- update `package-lock.json`;
- verify registry resolution;
- run clean install/tests/typecheck/build;
- verify the sibling shared checkout is not needed for the deployed build.

## Out of Scope

- publishing/modifying `moda-interact-shared`;
- changing shared contract semantics;
- changing Shopify webhook/recovery business behaviour;
- changing Render topology;
- changing `moda-interact-background`;
- adding npm credentials for a public artifact;
- using a floating version range.

## Requirements

Use an exact version:

```json
"@modainteract/moda-interact-shared": "<exact-version>"
```

Do not use `^`, `~`, `latest` or another floating production range.

The committed lockfile must resolve the package from npm rather than a local
filesystem source.

The selected artifact must contain the runtime JavaScript, typings and exports
required by the current Shopify application.

A clean service-local build must not require `../moda-interact-shared`.

The same committed dependency model is used by test and production.

Local development tooling may use workspace conveniences only if that does not
change the committed deployed dependency boundary.

If no currently published version satisfies the accepted application imports,
return this task **Blocked** with evidence. Do not:

- copy shared schemas into the app;
- change contract semantics merely to make installation succeed;
- silently fall back to `file:`;
- publish a new shared version from this task.

## Work Items

- [ ] inspect current shared imports/usage;
- [ ] inspect published package metadata/contents;
- [ ] select a compatible exact published version;
- [ ] replace the `file:` dependency in `package.json`;
- [ ] update `package-lock.json`;
- [ ] verify registry lockfile resolution;
- [ ] run clean `npm ci`;
- [ ] run relevant tests;
- [ ] run typecheck;
- [ ] run production build;
- [ ] prove the sibling shared repository is not required.

## Interfaces / Contracts

Package:

```text
@modainteract/moda-interact-shared
```

Enables infrastructure validation:

```text
ARCH-002-GATEWAY-005
```

This task changes package distribution/resolution only.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-005`

## Acceptance Criteria

- [ ] a current-compatible exact published version is selected;
- [ ] `package.json` no longer uses `file:../moda-interact-shared`;
- [ ] lockfile resolves the package from npm;
- [ ] all required current imports/exports resolve;
- [ ] clean `npm ci` succeeds without the sibling shared checkout;
- [ ] relevant tests pass;
- [ ] typecheck passes or unrelated pre-existing failure is explicitly recorded;
- [ ] production build succeeds;
- [ ] no npm credential is committed;
- [ ] Shopify/shared contract semantics are unchanged;
- [ ] the same committed dependency model supports test and production.

## Validation

- [ ] package metadata/artifact inspection;
- [ ] dependency/lockfile inspection;
- [ ] clean `npm ci`;
- [ ] focused tests;
- [ ] typecheck;
- [ ] production build;
- [ ] no-sibling-checkout verification.

## Implementation Notes

GATEWAY-005 performs the cross-consumer infrastructure validation after this task
and BACKGROUND-004 are architect-accepted.

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

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
