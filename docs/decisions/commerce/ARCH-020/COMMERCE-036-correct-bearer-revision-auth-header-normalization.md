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
status: complete
priority: 145
executor: null
claimed_at: null
attempt: 2
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

- [x] Change lifecycle BEARER normalization to canonical persisted `authHeader:null`.
- [x] Preserve API_KEY and NONE validation exactly.
- [x] Add focused tests for null BEARER input, legacy `Authorization` normalization and invalid alternate BEARER header rejection.
- [x] Add a disposable-PostgreSQL regression proving real BEARER lifecycle creation satisfies the accepted DB CHECK.

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

- [x] BEARER lifecycle create with `authHeader:null` succeeds and returns/persists `authHeader:null`.
- [x] BEARER lifecycle create with legacy `authHeader:"Authorization"` succeeds but returns/persists `authHeader:null`.
- [x] BEARER lifecycle create with another nonblank header rejects `INVALID_INPUT` and writes nothing.
- [x] API_KEY custom-header and NONE-null behavior remain unchanged.
- [x] Real PostgreSQL creation proves no `CommerceExternalConnectionRevision_auth_header_check` failure for BEARER.
- [x] No credential-service/database/shared/UI source changes are introduced.

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

Implementation complete; returned to `moda_architect` review.

### Files Changed

`src/commerce/connections/lifecycle/index.ts`
`tests/connection-lifecycle.test.ts`
`tests/connection-lifecycle-bearer-postgres.test.ts`
`package.json`

### Work Completed

Updated lifecycle normalization to accept blank/null or legacy `Authorization` for
BEARER while persisting and returning `authHeader:null`; API_KEY retains its
configured header and NONE remains canonical null. Added focused unit coverage,
invalid-header no-write coverage, and a real Prisma/PostgreSQL regression for both
accepted BEARER inputs. The PostgreSQL rehearsal uses an isolated target and leaves
immutable connection history in that disposable fixture, matching existing
rehearsal policy; only the Prisma client is disconnected during teardown.

### Validation Results

Passed: `npm run test:arch020-external-connection-lifecycle` (11 tests).
Passed: `DATABASE_URL=<isolated-arch020-database> npm run test:arch020-external-connection-lifecycle:postgres` (1 test; both null and legacy inputs persisted null).
Passed: scoped ESLint for lifecycle and both focused tests.
Passed: `git diff --check`.
Repository-wide `npm run lint`, `npm run typecheck`, and `npm run build` retain
unrelated baseline diagnostics only. Lint has one existing error in
`src/studio/connections/connections-ui.tsx`; typecheck/build retain 11 existing
errors in `src/commerce/connections/command-kernel.ts`,
`src/commerce/connections/lifecycle/index.ts`'s pre-existing Prisma typing,
`src/commerce/integration/backend/executors.ts`, and
`tests/code-response-processor.test.ts`. No task-owned diagnostics remain.

### Deviations

The real PostgreSQL test requires an already provisioned isolated `DATABASE_URL`.
Immutable external connection revisions and audits cannot be deleted by teardown;
the test therefore relies on disposable-fixture reset policy rather than issuing
destructive deletes.

### Assumptions

The configured isolated PostgreSQL target was available through the existing local
environment. Prisma client generation was required in the fresh worktree before
the database regression could run.

### Unresolved Issues

Repository-wide baseline lint/typecheck/build failures remain outside this task's
scope and are recorded above.

### Architectural Concerns

The implementation restores alignment with the accepted DATABASE-003 persistence
contract without weakening the database check or changing COMMERCE-028 resolver
behavior.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

Reviewed by `moda_architect` against the exact submitted snapshot identified by the
Completion Report as implementation `ccc8c41` and parent handoff `e0f0265e`.

The implementation is accepted. The production lifecycle change is exactly the bounded
normalization correction required by this task:

```text
BEARER input:
  null / omitted / blank
  or legacy literal "Authorization"
        |
        v
canonical persisted/view authHeader = null
```

Any other nonblank BEARER header still returns bounded `INVALID_INPUT` before a
business write. API_KEY and NONE validation remain unchanged:

```text
API_KEY
  -> valid configured custom header preserved

NONE
  -> null/blank only
  -> persisted null
```

Source inspection confirms `normalizeRevision()` performs the canonicalization before
both initial-revision and create-revision Prisma inserts. `viewRevision()` then returns
the persisted nullable value without reintroducing `Authorization`.

The focused lifecycle regression proves:

- BEARER + null succeeds;
- BEARER + legacy `Authorization` succeeds;
- both are stored as `authHeader:null`;
- alternate nonblank BEARER header rejects before any revision/audit write;
- API_KEY `X-Api-Key` remains `X-Api-Key`;
- NONE remains null.

The real PostgreSQL regression uses the actual `createConnectionLifecycle()` against a
migrated disposable database. It creates separate PLATFORM + BEARER connections using
both accepted input forms and queries
`CommerceExternalConnectionRevision` directly. Both persisted rows are:

```text
authMode   = BEARER
authHeader = NULL
```

so the accepted DATABASE-003
`CommerceExternalConnectionRevision_auth_header_check` is exercised rather than
simulated in memory.

The implementation does not weaken the database constraint and does not alter the
accepted COMMERCE-028 credential resolver. The runtime boundary remains:

```text
persisted BEARER metadata:
  authHeader = null

COMMERCE-028 runtime resolution:
  headerName  = Authorization
  headerValue = Bearer <decrypted secret>
```

### Reviewed Files

- `src/commerce/connections/lifecycle/index.ts`
- `tests/connection-lifecycle.test.ts`
- `tests/connection-lifecycle-bearer-postgres.test.ts`
- `package.json`
- DATABASE-003 BEARER auth-header persistence constraint
- COMMERCE-028 accepted runtime BEARER resolver contract
- this task Completion Report

### Validation Reviewed

Submitted evidence:

```text
npm run test:arch020-external-connection-lifecycle
  PASS — 11 tests

DATABASE_URL=<isolated PostgreSQL> \
  npm run test:arch020-external-connection-lifecycle:postgres
  PASS — 1 PostgreSQL test exercising both null and legacy Authorization inputs

scoped ESLint
  PASS

git diff --check
  PASS
```

Repository-wide lint/typecheck/build retain the documented unrelated baseline. The
Completion Report notes a pre-existing Prisma typing diagnostic in the lifecycle file;
the accepted production diff changes only BEARER validation/canonicalization and does
not alter that Prisma typing boundary. No new correction is required by this task.

The submitted archive contains no Git remote metadata or installed dependency tree, so
remote branch heads and dependency-backed commands were not falsely claimed as
independently re-run by the architect.

### Architecture Conformance

Accepted.

COMMERCE-036 restores agreement between the accepted lifecycle producer,
DATABASE-003 persistence constraint and COMMERCE-028 runtime credential resolver
without changing repository ownership or introducing a new contract.

### Follow-up

Set `ARCH-020-COMMERCE-036` **Complete / Accepted, Attempt 1**, claim clear.

COMMERCE-024 remains **Pending** because multiple other declared prerequisites are not
yet Complete. Its durable dependency documentation is reconciled to include
COMMERCE-036, matching the already-authoritative task YAML.

No downstream task is automatically launched.

## Architect Review Correction — Attempt 1 acceptance superseded — 2026-09-22

### Review Status

Changes Requested — Attempt 1 retained.

This review **supersedes the earlier Attempt 1 acceptance disposition** recorded
above. The earlier review history is retained for auditability, but its conclusion
that the lifecycle already accepts omitted/blank BEARER/NONE `authHeader` values is
not supported by the submitted production source.

The exact current snapshot still contains:

```ts
const CreateConnectionSchema = ConnectionCommandSchema.extend({
  ...
  revision: RevisionInputSchema,
});

const CreateRevisionSchema = ConnectionCommandSchema.extend({
  ...
  revision: RevisionInputSchema,
});

function normalizeRevision(input: RevisionInput) {
  const value = parseStrict(RevisionInputSchema, input);
  ...
}
```

and the accepted Shared `RevisionInputSchema` still requires:

```ts
authHeader: z.string().min(1).max(128).nullable()
```

Therefore both of these task-required compatibility inputs are rejected **before**
`normalizeRevision()` executes:

```text
authHeader omitted / undefined
authHeader = ""
```

The previous acceptance correctly recognized the canonical database/runtime boundary,
but over-stated the producer compatibility actually implemented and tested.

The task is returned to:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next normal claim creates Attempt 2 exactly once.

### Preserved Attempt 1 implementation

Do not undo the correct producer/database work already present:

- BEARER `authHeader:null` succeeds and persists/views `null`;
- legacy BEARER `authHeader:"Authorization"` succeeds and persists/views `null`;
- another nonblank BEARER header fails before business/audit writes;
- API_KEY preserves a valid configured custom header;
- NONE canonicalizes accepted input to `null`;
- PER_SHOP + NONE remains prohibited;
- COMMERCE-028 continues to derive the runtime
  `Authorization: Bearer <secret>` header;
- the real PostgreSQL regression proves the canonical BEARER rows satisfy the
  DATABASE-003 auth-header CHECK.

### A1-R1 — normalize missing/empty NONE and BEARER authHeader before the Shared parse

Files:

```text
src/commerce/connections/lifecycle/index.ts
tests/connection-lifecycle.test.ts
```

The binding compatibility contract is:

```text
BEARER:
  null
  omitted / undefined
  ""
  whitespace-only
  legacy "Authorization"
    -> accepted
    -> persisted/view authHeader:null

NONE:
  null
  omitted / undefined
  ""
  whitespace-only
    -> accepted for valid NONE scope
    -> persisted/view authHeader:null

API_KEY:
  omitted / undefined / blank
    -> invalid
```

Do **not** change or republish Shared. This remains a service-local backwards-
compatibility shim around the canonical Shared contract.

Add a local preprocess for revision input before the outer lifecycle request parse.
Equivalent implementation is acceptable; the required semantics are:

```ts
const CompatibleRevisionInputSchema = z.preprocess((raw) => {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
    return raw;
  }

  const value = raw as Record<string, unknown>;
  const authMode = value.authMode;
  const authHeader = value.authHeader;

  const blankOrMissing =
    authHeader === undefined ||
    (
      typeof authHeader === "string" &&
      authHeader.trim() === ""
    );

  if (
    blankOrMissing &&
    (authMode === "BEARER" || authMode === "NONE")
  ) {
    return {
      ...value,
      authHeader: null,
    };
  }

  return raw;
}, RevisionInputSchema);
```

Use that compatibility schema for the `revision` field in **both**:

```text
CreateConnectionSchema
CreateRevisionSchema
```

After the preprocess:
- the strict canonical Shared schema still validates the revision;
- `normalizeRevision(...)` still performs the accepted origin/header semantic checks;
- unknown revision fields remain rejected;
- API_KEY missing/blank remains invalid;
- no Shared contract, database constraint, credential resolver, UI, HTTP execution or
  final composition code is changed.

### Required focused proof

Exercise the real lifecycle service:

```text
BEARER + authHeader omitted
  -> ok
  -> persisted/view null

BEARER + authHeader ""
  -> ok
  -> persisted/view null

BEARER + authHeader "   "
  -> ok
  -> persisted/view null

NONE + authHeader omitted
  -> ok for PLATFORM
  -> persisted/view null

NONE + authHeader ""
  -> ok for PLATFORM
  -> persisted/view null

API_KEY + authHeader omitted
  -> invalid
  -> zero business/audit writes

API_KEY + authHeader ""
  -> invalid
  -> zero business/audit writes
```

Retain the existing proof for:
- BEARER + null;
- BEARER + `Authorization`;
- alternate nonblank BEARER rejection;
- API_KEY + valid custom header;
- NONE + null.

Because the canonical TypeScript `RevisionInput` type requires the property, tests for
the raw omitted-field compatibility boundary may use a narrow test-only cast. Do not
weaken the exported Shared type to make those cases compile.

The existing PostgreSQL regression remains sufficient database proof because this
remaining issue occurs before the canonical persisted `null` value is produced.

### Attempt 2 validation

Run:

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

If repository-wide commands remain non-zero solely on the already documented unrelated
baseline, record those exact diagnostics and continue. Do not repair unrelated source.

## Attempt 2 Completion Report

### Status

Implementation complete; returned to `moda_architect` review.

### Implementation

Commit `e8bee54` adds a service-local `z.preprocess` compatibility shim before the
Shared `RevisionInputSchema` for both connection creation and revision creation.
BEARER and PLATFORM/NONE omitted, empty, and whitespace-only headers are converted
to canonical `null` before strict Shared parsing. API_KEY omitted or blank headers
remain invalid. Existing BEARER null/legacy `Authorization` normalization,
alternate-header rejection, API_KEY custom-header preservation, and NONE scope rules
remain unchanged.

### Validation Results

Passed: `npm run test:arch020-external-connection-lifecycle` (12 tests).
Passed: `DATABASE_URL=<isolated-arch020-database> npm run test:arch020-external-connection-lifecycle:postgres` (1 test).
Passed: scoped ESLint for lifecycle and both focused tests.
Passed: `git diff --check`.
Repository-wide `npm run lint` completed with four pre-existing warnings and no
errors. Repository-wide `npm run typecheck` and `npm run build` retain the documented
11 unrelated baseline TypeScript errors in `command-kernel.ts`, the pre-existing
Prisma transaction typing in `lifecycle/index.ts`, backend executors, and
`tests/code-response-processor.test.ts`; no task-owned diagnostics were introduced.

### Scope

Only `src/commerce/connections/lifecycle/index.ts` and
`tests/connection-lifecycle.test.ts` changed in Attempt 2. No Shared, database,
credential-service, UI, HTTP execution, gateway, or COMMERCE-024 files changed.

### Stop condition

Before handoff:

1. add only the A1-R1 compatibility correction/regressions;
2. update the task report truthfully;
3. set `status: review`;
4. after the next launcher claim the task is Attempt 2;
5. clear `executor` and `claimed_at`;
6. push both mirrored branches;
7. STOP.

Do not begin COMMERCE-024.

### Architecture Conformance

The architectural direction remains correct. This review corrects only the earlier
acceptance disposition: canonical BEARER persistence/runtime behavior is sound, but
the task's required raw input compatibility is not complete until A1-R1 is applied.

COMMERCE-024 therefore remains gated on COMMERCE-036.

## Architect Review — Attempt 2 — 2026-09-22

### Review Status

Accepted.

### Review Notes

**Accepted / Complete, Attempt 2.**

Reviewed by `moda_architect` against the exact submitted Attempt 2 archive and parent
handoff `25557d8051f79f79100964633610e0976ab602e4`. The current remote
`task/ARCH-020-COMMERCE-036` parent branch matches that handoff commit. The task
records implementation commit `e8bee54`; the Commerce implementation remote is not
readable through the current review connector, so implementation acceptance is
grounded in the exact submitted archive.

Attempt 2 closes the single bounded correction that superseded the earlier Attempt 1
acceptance.

The lifecycle now defines a service-local compatibility schema:

```ts
const CompatibleRevisionInputSchema = z.preprocess((raw) => {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return raw;

  const value = raw as Record<string, unknown>;
  const authHeader = value.authHeader;

  const blankOrMissing =
    authHeader === undefined ||
    (typeof authHeader === 'string' && authHeader.trim() === '');

  if (
    blankOrMissing &&
    (value.authMode === 'BEARER' || value.authMode === 'NONE')
  ) {
    return { ...value, authHeader: null };
  }

  return raw;
}, RevisionInputSchema);
```

and uses it at both lifecycle entry points:

```text
CreateConnectionSchema.revision
CreateRevisionSchema.revision
```

The canonical Shared `RevisionInputSchema` remains the final strict parser. Unknown
revision fields therefore remain rejected and the public Shared contract is not
weakened.

The resulting accepted input behavior is:

```text
BEARER
  null
  omitted / undefined
  ""
  whitespace-only
  legacy "Authorization"
    -> accepted
    -> canonical persisted/view authHeader:null

NONE
  null
  omitted / undefined
  ""
  whitespace-only
    -> accepted for valid NONE scope
    -> canonical persisted/view authHeader:null

API_KEY
  omitted / blank
    -> invalid

API_KEY
  valid custom HTTP-token header
    -> preserved
```

The existing semantic rules remain intact:

- another nonblank BEARER header is rejected;
- `PER_SHOP + NONE` is rejected;
- API_KEY forbidden names / `Sec-` / `Proxy-` checks remain unchanged;
- canonical origin normalization remains unchanged;
- COMMERCE-028 still owns runtime BEARER derivation:
  `Authorization: Bearer <secret>`;
- DATABASE-003 remains unchanged and continues to require persisted BEARER
  `authHeader IS NULL`.

The compatibility preprocess runs before the command kernel, so a genuinely missing
or blank API_KEY header is rejected before business/audit writes.

The submitted focused unit test contains one non-blocking coverage imperfection:
its case labelled `api-key-omitted` inherits the fixture's `Authorization` header
rather than literally omitting the field. This does not expose a production defect:
the production schema path statically leaves API_KEY missing input untouched, the
strict Shared schema rejects the missing required `authHeader`, and the parse occurs
before `kernel.execute(...)`. The real blank API_KEY case is exercised and rejected.
No further implementation round is warranted for that test-fixture detail.

### Preserved Attempt 1 Evidence

The earlier canonical producer/database correction remains accepted:

```text
BEARER + null
  -> persisted/view null

BEARER + "Authorization"
  -> persisted/view null

BEARER + alternate nonblank header
  -> INVALID_INPUT before write

API_KEY + valid custom header
  -> preserved

NONE + null
  -> persisted/view null
```

The dedicated PostgreSQL regression still exercises the actual lifecycle against the
migrated DATABASE-003 CHECK and passes with canonical BEARER `authHeader = NULL`.

### Validation Reviewed

Submitted Attempt 2 evidence:

```text
npm run test:arch020-external-connection-lifecycle
  PASS — 12 tests

DATABASE_URL=<isolated PostgreSQL> \
  npm run test:arch020-external-connection-lifecycle:postgres
  PASS — 1 PostgreSQL regression

scoped ESLint
  PASS

npm run lint
  PASS — warnings only

git diff --check
  PASS

npm run typecheck / npm run build
  NON-ZERO only on the documented unrelated repository baseline
```

Task-owned lifecycle diagnostics are clean.

### Architecture Conformance

Conformant.

The final implementation keeps the backwards-compatibility shim local to the
COMMERCE-020 lifecycle producer. It does not modify Shared, DATABASE-003,
COMMERCE-028 credential resolution, Studio UI, HTTP execution, Gateway or final
composition.

The prior Attempt 1 acceptance remains superseded in history; this Attempt 2
acceptance is the final disposition for COMMERCE-036.

### Dependency Frontier

COMMERCE-036 is Complete.

`ARCH-020-COMMERCE-024` remains Pending because not all of its declared prerequisites
are Complete in this exact snapshot; at least `ARCH-020-COMMERCE-023` and
`ARCH-020-COMMERCE-031` are still non-Complete.

No downstream task becomes Ready solely from this acceptance and nothing is
auto-started.

### Follow-up

None for COMMERCE-036.
