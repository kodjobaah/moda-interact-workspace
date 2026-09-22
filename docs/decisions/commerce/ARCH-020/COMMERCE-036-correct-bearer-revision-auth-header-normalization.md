---
id: ARCH-020-COMMERCE-036
architecture_id: ARCH-020
title: Correct BEARER revision auth-header normalization
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 145
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-020
  - ARCH-020-DATABASE-003
  - ARCH-020-SHARED-002
enables:
  - ARCH-020-COMMERCE-024
created: 2026-09-22
updated: 2026-09-22
---

# Correct BEARER revision auth-header normalization

## Architecture

ARCH-020 C21 sections 3, 4 and 9.2. This bounded correction was discovered while
reviewing COMMERCE-028 Attempt 2. The accepted database contract and credential
resolver already agree that BEARER does not persist an auth-header name; the accepted
COMMERCE-020 lifecycle currently persists `Authorization`, which violates the
database CHECK and makes real BEARER revision creation fail.

## Objective

Make COMMERCE-020 lifecycle input normalization compatible with the accepted
DATABASE-003 persistence contract while preserving the accepted COMMERCE-028 runtime
BEARER resolver.

## Context

Authoritative accepted behavior now is:

```text
API_KEY:
  persisted revision.authHeader = configured custom header
  resolver uses that persisted header

BEARER:
  persisted revision.authHeader = null
  resolver derives headerName = Authorization
  resolver derives headerValue = Bearer <secret>

NONE:
  persisted revision.authHeader = null
  resolver returns null authentication
```

The current lifecycle instead requires `authHeader === "Authorization"` for BEARER
and returns/persists that value. PostgreSQL rejects that row because
`CommerceExternalConnectionRevision_auth_header_check` permits non-null authHeader
only for API_KEY.

## Scope

Only:

- `src/commerce/connections/lifecycle/index.ts`;
- the existing focused lifecycle test file;
- one dedicated disposable-PostgreSQL lifecycle regression;
- `package.json` only for the focused PostgreSQL test script if required.

Do not modify credential-service source, DATABASE schema/migration, Shared contracts,
Studio UI, HTTP execution, gateway configuration or final composition.

## Out of Scope

No new auth mode, no migration, no credential encryption change, no resolver rewrite,
no HTTP/provider work, no UI redesign, no COMMERCE-024 composition and no deployment.

## Requirements

Implement these exact normalization rules.

### API_KEY

Input:

```text
authHeader must be nonblank HTTP-token syntax
must retain existing forbidden-name/Sec-/Proxy- checks
```

Persistence/view:

```text
authHeader = normalized configured header
```

### NONE

Input:

```text
authHeader must be null/undefined/blank only
```

Persistence/view:

```text
authHeader = null
```

### BEARER

For compatibility with already-authored callers, accept either:

```text
authHeader = null/undefined/blank
```

or exactly:

```text
authHeader = "Authorization"
```

Reject every other nonblank BEARER header.

Canonical persistence/view is always:

```text
authHeader = null
```

The lifecycle must therefore normalize an accepted legacy `"Authorization"` input to
`null` **before the Prisma insert**.

Do not weaken the database CHECK and do not change COMMERCE-028. Its accepted
`resolveConnection()` already derives:

```text
headerName = "Authorization"
headerValue = "Bearer <decrypted secret>"
```

from `authMode === "BEARER"`.

The PER_SHOP/NONE prohibition remains unchanged.

## Work Items

- [ ] Change lifecycle BEARER normalization to canonical persisted `authHeader:null`.
- [ ] Preserve API_KEY and NONE validation exactly.
- [ ] Add focused tests for null BEARER input, legacy `Authorization` normalization and invalid alternate BEARER header rejection.
- [ ] Add a disposable-PostgreSQL regression proving real BEARER lifecycle creation satisfies the accepted DB CHECK.

## Interfaces / Contracts

No new interface.

Consumes:

- accepted `RevisionInput` / `ConnectionRevisionView`;
- accepted DATABASE-003 `CommerceExternalConnectionRevision_auth_header_check`;
- accepted COMMERCE-028 runtime BEARER derivation.

The public `ConnectionRevisionView` for a persisted BEARER revision must expose
`authHeader:null`.

## Dependencies

- ARCH-020-COMMERCE-020
- ARCH-020-DATABASE-003
- ARCH-020-SHARED-002

## Enables

- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [ ] BEARER lifecycle create with `authHeader:null` succeeds and returns/persists `authHeader:null`.
- [ ] BEARER lifecycle create with legacy `authHeader:"Authorization"` succeeds but returns/persists `authHeader:null`.
- [ ] BEARER lifecycle create with another nonblank header rejects `INVALID_INPUT` and writes nothing.
- [ ] API_KEY custom-header and NONE-null behavior remain unchanged.
- [ ] Real PostgreSQL creation proves no `CommerceExternalConnectionRevision_auth_header_check` failure for BEARER.
- [ ] No credential-service/database/shared/UI source changes are introduced.

## Validation

Add:

```text
tests/connection-lifecycle-bearer-postgres.test.ts
```

and, if no suitable existing script exists:

```json
"test:arch020-external-connection-lifecycle:postgres":
  "vitest run tests/connection-lifecycle-bearer-postgres.test.ts"
```

Focused unit proof must cover:

```text
BEARER + null
  -> normalized null

BEARER + Authorization
  -> normalized null

BEARER + X-Other
  -> INVALID_INPUT

API_KEY + X-Api-Key
  -> preserved

NONE + null
  -> preserved
```

The PostgreSQL regression must use the actual `createConnectionLifecycle` against a
disposable migrated database:

```text
create PLATFORM + BEARER revision
input authHeader = null
-> lifecycle returns ok
-> persisted authMode = BEARER
-> persisted authHeader IS NULL
```

Then repeat with legacy input `"Authorization"` on a separate connection and prove the
persisted row is still NULL.

Run exactly:

```bash
npm run test:arch020-external-connection-lifecycle

DATABASE_URL="<isolated-arch020-database>" \
  npm run test:arch020-external-connection-lifecycle:postgres

npx eslint \
  src/commerce/connections/lifecycle \
  tests/connection-lifecycle.test.ts \
  tests/connection-lifecycle-bearer-postgres.test.ts

npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide lint/typecheck/build retain only the known unrelated baseline,
record exact diagnostics and prove no task-owned diagnostic. Do not repair unrelated
files.

## Stop Condition

After the defined source change, focused tests and real PostgreSQL regression pass:

```text
update Work Items / Acceptance Criteria / Validation truthfully
update Completion Report
set status: review
clear executor / claimed_at
push implementation + parent task branches
return to moda_architect
STOP
```

Do not begin COMMERCE-024 or another enabled task.

## Implementation Notes

This task is a normalization correction, not an authentication redesign.

The canonical rule is:

```text
BEARER header name is runtime behavior, not persisted connection metadata.
```

Do not change the accepted DATABASE-003 constraint merely to accommodate the old
lifecycle value.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the binding contract above.

### Unresolved Issues

None known.

### Architectural Concerns

None beyond the defect this task resolves.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Execute only after an authorized `/moda-task ARCH-020-COMMERCE-036` claim.
