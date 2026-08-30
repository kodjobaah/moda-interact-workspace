---
id: ARCH-002-BACKGROUND-004
architecture_id: ARCH-002
title: Use published shared package in background service
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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

# Use Published Shared Package in Background Service

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Change the committed deployable dependency boundary in
`moda-interact-background` so the canonical cross-service package resolves from
the published npm artifact:

```text
@modainteract/moda-interact-shared
```

rather than:

```text
file:../moda-interact-shared
```

The result must support all three ARCH-002 worker entrypoints in both test and
production.

## Context

The original `file:` dependency required the sibling shared repository to exist
inside the build context.

ARCH-002 now uses a versioned published npm artifact as the deployed
cross-service dependency boundary.

A public version is known to exist, but this task must verify the artifact
against the **current** background imports, queue/event contracts and runtime
exports before selecting it.

## Scope

Within `moda-interact-background`:

- inspect current shared-package imports/usage;
- inspect available published package metadata/contents;
- select an exact compatible published version;
- replace the committed `file:` dependency with that exact npm version;
- update `package-lock.json`;
- verify registry resolution;
- verify all three worker entrypoints/build targets compile against the artifact;
- run clean install/tests/typecheck/build;
- verify the sibling shared checkout is not required for deployed builds.

## Out of Scope

- publishing/modifying `moda-interact-shared`;
- changing shared queue/event contracts;
- changing recovery/order/messaging business semantics;
- changing worker topology;
- changing Render infrastructure;
- changing `moda-interact`;
- adding npm credentials for a public artifact;
- using a floating version range.

## Requirements

Use an exact version:

```json
"@modainteract/moda-interact-shared": "<exact-version>"
```

The lockfile must resolve the artifact from npm rather than a local path.

The selected package must expose all schemas, queue/job constants, types and
helpers consumed by the current background implementation.

The same committed dependency model must work for:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

and for both deployed environments.

If no currently published artifact satisfies the accepted consumer code, return
this task **Blocked** with evidence. Do not:

- copy/recreate shared contracts locally;
- change contract semantics merely to install a package;
- silently fall back to `file:`;
- publish a new package version from this task.

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
- [ ] verify all three worker entrypoints compile/start as applicable;
- [ ] prove the sibling shared repository is not required.

## Interfaces / Contracts

Package:

```text
@modainteract/moda-interact-shared
```

Enables:

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
- [ ] all required current background exports resolve;
- [ ] all three worker deployment units compile against the package;
- [ ] clean `npm ci` succeeds without the sibling shared checkout;
- [ ] relevant tests pass;
- [ ] typecheck passes or unrelated pre-existing failure is explicitly recorded;
- [ ] production build succeeds;
- [ ] no npm credential is committed;
- [ ] background/shared contract semantics are unchanged;
- [ ] the same committed dependency model supports test and production.

## Validation

- [ ] package metadata/artifact inspection;
- [ ] dependency/lockfile inspection;
- [ ] clean `npm ci`;
- [ ] focused tests;
- [ ] typecheck;
- [ ] production build;
- [ ] worker-entrypoint compile/start verification where practical;
- [ ] no-sibling-checkout verification.

## Implementation Notes

GATEWAY-005 performs the cross-consumer infrastructure validation after this task
and SHOPIFY-004 are architect-accepted.

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
