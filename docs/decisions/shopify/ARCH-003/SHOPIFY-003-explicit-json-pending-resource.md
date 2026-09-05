---
id: ARCH-003-SHOPIFY-003
architecture_id: ARCH-003
title: Make pending-recovery resource an explicit JSON response
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-05T12:58:09Z
attempt: 1
depends_on:
  - ARCH-003-SHOPIFY-002
enables:
  - ARCH-003-SYSTEM-TEST-002
created: 2026-09-05
updated: 2026-09-05
---

# Make pending-recovery resource an explicit JSON response

## Architecture

Architecture ID:

```text
ARCH-003
```

Architecture document:

```text
docs/architecture/ARCH-003-admin-operational-ui.md
```

Coordinator:

```text
moda_architect
```

## Objective

Make the authenticated `/app/pending-recoveries` resource route return an
explicit JSON HTTP response so both React Router `useFetcher` and the live
system-test HTTP collector consume the same stable response contract.

## Context

`ARCH-003-SHOPIFY-002` is Complete and its merchant UI works through
React Router's `useFetcher`.

During `ARCH-003-SYSTEM-TEST-002` live evidence collection, an authenticated
CDP-attached Chrome session successfully reached the embedded merchant app.

A direct same-origin fetch of:

```text
/app/pending-recoveries?pendingPage=1
```

returned React Router's framework/Turbo Stream representation because the
resource loader currently returns a raw object:

```js
return {
  pendingRecoveries,
  refreshedAt: ...
};
```

The Python evidence collector therefore received an array-like encoded payload
rather than a plain JSON object and failed with:

```text
'list' object has no attribute 'get'
```

This is a response-encoding contract issue at the resource-route boundary.

React Router resource routes intended for ordinary HTTP consumption should make
the response encoding explicit.

## Scope

Repository:

```text
moda-interact
```

Primary route:

```text
app/routes/app.pending-recoveries.jsx
```

Focused tests for the resource response contract are in scope.

## Out of Scope

- changing the pending-recovery reader;
- Redis/BullMQ behavior;
- tenant-selection behavior;
- merchant UI redesign;
- pagination semantics;
- automatic polling;
- database changes;
- system-test validator changes;
- decoding Turbo Stream in Python.

## Requirements

The resource loader must preserve all existing authentication and tenant
resolution behavior.

It must return an explicit JSON HTTP response containing:

```json
{
  "pendingRecoveries": {},
  "refreshedAt": "..."
}
```

Conceptually:

```js
return Response.json({
  pendingRecoveries,
  refreshedAt: pendingRecoveries.available
    ? new Date().toISOString()
    : null,
});
```

Exact implementation may use the repository/framework equivalent if required.

Required response header:

```text
Content-Type: application/json
```

The body must be consumable with an ordinary browser:

```js
const result = await fetch("/app/pending-recoveries?pendingPage=1");
const data = await result.json();

data.pendingRecoveries
data.refreshedAt
```

without React Router/Turbo Stream decoding.

Existing `useFetcher().load(...)` behavior in `PendingRecoveries.jsx` must
continue to receive:

```text
fetcher.data.pendingRecoveries
fetcher.data.refreshedAt
```

with no merchant behavior regression.

## Work Items

- [x] Change the resource loader to an explicit JSON HTTP response.
- [x] Preserve authenticated Shopify shop resolution.
- [x] Preserve `pendingPage` parsing and reader invocation.
- [x] Preserve unavailable-state `refreshedAt: null`.
- [x] Add focused test proving ordinary HTTP JSON body/Content-Type.
- [x] Preserve existing fetcher-facing data shape.
- [x] Run focused/full validation.

## Interfaces / Contracts

HTTP resource:

```text
GET /app/pending-recoveries?pendingPage=<n>
```

Response:

```text
Content-Type: application/json
```

JSON body:

```text
pendingRecoveries
refreshedAt
```

No shop identity is accepted from browser query parameters.

## Dependencies

- `ARCH-003-SHOPIFY-002`

## Enables

- `ARCH-003-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] ordinary authenticated `fetch()` + `response.json()` returns an object;
- [x] response contains `pendingRecoveries`;
- [x] response contains `refreshedAt`;
- [x] `Content-Type` is JSON;
- [x] `useFetcher` refresh behavior remains functional;
- [x] authenticated shop remains server-derived;
- [x] pending page behavior remains unchanged;
- [x] unavailable response remains safe;
- [x] no sensitive data exposure regression;
- [x] no UI redesign or polling behavior change.

## Validation

- [x] focused resource-route tests;
- [x] existing Pending recoveries tests;
- [x] full test suite subject to documented baseline;
- [x] build;
- [x] changed-file lint;
- [x] `git diff --check`.

## Implementation Notes

The live system-test should not implement its own decoder for React Router's
internal streaming representation.

The HTTP boundary should be explicit because it is now intentionally consumed
both by:

```text
React Router useFetcher
```

and:

```text
authenticated live system-test fetch
```

## Completion Report

### Status

Ready for Review.

### Files Changed

- `app/routes/app.pending-recoveries.jsx`
- `tests/unit/pending-recoveries-route.test.ts`

### Work Completed

Changed the authenticated pending-recoveries loader to return `Response.json`
while preserving server-derived shop resolution, page parsing, reader inputs,
unavailable-state handling, and the existing `{ pendingRecoveries, refreshedAt }`
fetcher data shape. Added response-header/body assertions for available and
unavailable responses.

### Validation Results

- Focused route, display-state, and reader tests: 7 passed.
- Full test suite: 89 passed, 1 skipped.
- Changed-file ESLint: passed; emitted the repository's existing warning that
  TypeScript 5.9.3 is outside the installed `@typescript-eslint` supported
  range.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: failed on pre-existing unrelated errors in
  `PendingRecoveries.jsx`, `db.server.js`, `_index/route.jsx`, and unresolved
  aliases/modules in `app._index.jsx`; no changed route/test file was reported.

### Deviations

None.

### Assumptions

`Response.json` is the React Router/runtime-supported explicit response API and
React Router `useFetcher` continues to expose its parsed JSON body as the
existing `fetcher.data` shape.

### Unresolved Issues

The repository-wide typecheck baseline remains failing for unrelated existing
errors documented above.

### Architectural Concerns

None.

### Git / VCS

Implementation ready for developer commit/push. Repository agent did not commit
or push.

## Architect Review

### Review Status

Accepted

### Review Notes

Architect reviewed the supplied Shopify implementation archive directly.

The resource route now returns:

```js
Response.json({
  pendingRecoveries,
  refreshedAt: pendingRecoveries.available
    ? new Date().toISOString()
    : null,
});
```

This preserves the existing authenticated server-side shop resolution and
`pendingPage` parsing while making the HTTP encoding explicit for ordinary
browser `fetch()` consumers.

Focused route tests verify both:

```text
available response
unavailable response
```

including:

```text
Content-Type: application/json
response.json()
pendingRecoveries
refreshedAt
```

The implementation does not accept browser-supplied shop identity and does not
change the pending-recovery reader, Redis/BullMQ behavior, pagination
semantics, polling behavior, or merchant UI.

React Router resource-route semantics support returning explicit `Response`
instances for externally consumed resource routes, while fetcher consumers
continue to receive the parsed route data.

### Validation Reviewed

Implementing-agent evidence:

- focused tests: 7 passed;
- full suite: 89 passed, 1 skipped;
- production build: passed;
- changed-file lint: passed;
- `git diff --check`: passed;
- repository typecheck remains blocked by documented pre-existing unrelated
  diagnostics.

The supplied review archive does not contain `node_modules`, so the architect
did not rerun Vitest from the archive. The changed route and focused test
sources were inspected directly.

### Architecture Conformance

Conforms.

### Result

`ARCH-003-SHOPIFY-003` is Complete.

The source-level resource encoding blocker for
`ARCH-003-SYSTEM-TEST-002` is cleared.

`ARCH-003-SYSTEM-TEST-002` remains Blocked only on developer-owned deployed
live evidence. After this Shopify change is deployed, rerun the existing CDP
collector against the authenticated merchant app.

