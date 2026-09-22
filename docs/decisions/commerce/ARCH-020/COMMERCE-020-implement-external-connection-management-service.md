---
id: ARCH-020-COMMERCE-020
architecture_id: ARCH-020
title: Implement external connection lifecycle and command kernel
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 150
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-DATABASE-003
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
  - ARCH-020-COMMERCE-028
created: 2026-09-21
updated: 2026-09-22
---

# Implement external connection lifecycle and command kernel

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/connections/lifecycle/** and src/commerce/connections/command-kernel.ts only. Implement metadata/revision/enabled lifecycle and reusable transaction/auth/replay kernel. No credential encryption/storage commands/resolver, network, UI or final factories.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/connections/lifecycle/** and src/commerce/connections/command-kernel.ts only. Implement metadata/revision/enabled lifecycle and reusable transaction/auth/replay kernel. No credential encryption/storage commands/resolver, network, UI or final factories.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [ ] Implement createConnectionLifecycle with list/get/create/updateMetadata/createRevision/setEnabled, strict section4 DTOs, immutable revision allocation and locked metadata CAS.
- [ ] Implement section9 command kernel with authorization-before-replay, canonical keyed digest, transaction mutation/audit atomicity and unique-race reconciliation.028 imports it; no generic application framework.
- [ ] Provide metadata-only U15/U16 read models; do not claim credential status is implemented. Return exact new revision IDs without migrating published tool references.
- [ ] Produce actual lifecycle create/revise/disable success and contentious update/replay/rollback scenarios early.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-DATABASE-003
- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-002

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003
- ARCH-020-COMMERCE-028

## Acceptance Criteria

- [ ] CL01: valid create->metadata update->new immutable revision->disable/enable path through actual service preserves prior revision and returns exact IDs.
- [ ] CL02: two clients contend on same CAS or operation: one effect/audit; same replay returns original; altered replay/stale CAS produce no write; failure after actual write rolls back.
- [ ] CL03: ADMIN/revoked staff mutation denied before replay; connection origin/auth schema errors rejected; no credentials or HTTP in owned implementation.

## Validation

Provide `test:arch020-external-connection-lifecycle` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Implementation complete; submitted for Architect Review.

### Files Changed

- `src/commerce/connections/command-kernel.ts`
- `src/commerce/connections/lifecycle/index.ts`
- `src/commerce/connections/lifecycle/types.ts`
- `tests/connection-lifecycle.test.ts`

### Work Completed

- Consumed the exact Shared `0.14.2` commerce connection schemas/types and returned strict Shared result envelopes without invented error messages.
- Implemented the reusable C21 command kernel with authorization-before-replay, canonical keyed digests, all six accepted actions including credential actions, same-connection parameterized PostgreSQL `FOR UPDATE`, transaction-scoped mutation/audit, and unique-race reconciliation.
- Implemented metadata-only list/get/create/updateMetadata/createRevision/setEnabled lifecycle operations with strict bounded DTOs, canonical HTTPS origins, immutable revision numbering, and edit-version CAS.
- Preserved the accepted development-admin helper call inside the command transaction before replay and FK-backed mutation/audit writes.
- Added CL01/CL02/CL03 and A1-R2 focused acceptance coverage for lifecycle success, replay/conflict/stale-CAS/rollback, strict result parsing, credential-action locking, and bounded input rejection.

### Validation Results

- `npm run test:arch020-external-connection-lifecycle`: passed, 1 file and 9 tests.
- `npx eslint src/commerce/connections/command-kernel.ts src/commerce/connections/lifecycle/index.ts src/commerce/connections/lifecycle/types.ts tests/connection-lifecycle.test.ts`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: non-zero only on existing unrelated `src/commerce/integration/**` diagnostics; no diagnostics were reported for the task-owned connection files.
- `npm run build`: non-zero at the same existing unrelated integration TypeScript diagnostics; the task-owned connection files were not implicated.
- PostgreSQL/container checks were not run; no live credentials or external HTTP calls were used.

### Deviations

No design deviations. Implementation remains within the task-owned connection lifecycle/kernel paths; credential storage, OAuth, network execution, UI, publication, preview, and final factories remain out of scope.

### Unresolved Issues

Repository-wide typecheck/build debt remains outside the task-owned files. PostgreSQL/container validation remains developer-owned and unrun.

### Architectural Concerns

Architect review should confirm the accepted C21 field/error contracts and the baseline integration typecheck/build debt noted above.

### Git / VCS

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-020`
  parent branch: `task/ARCH-020-COMMERCE-020`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-020`
  implementation branch: `task/ARCH-020-COMMERCE-020`
  shared workspace checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  recorded submodule commit: `database` at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`

Logical agent: `moda_commerce`; canonical executor: `copilot`; attempt: 2.
Dependencies accepted before execution: DATABASE-003, SHARED-002, COMMERCE-002.
Implementation commit/push: `d2b7154` on `task/ARCH-020-COMMERCE-020`.
Parent claim commit/push: `bb2d70a` from launcher; claim cleared for review handoff.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.

### Attempt 1 — Review Status

Changes Requested.

### Attempt 1 — Review Notes

Reviewed implementation `5229b033` and parent report `29a6ffb1` against the exact
submitted snapshot and C21 sections 4 and 9.2. The lifecycle/CAS structure, immutable
revision creation, HMAC replay direction, transaction-wrapped business mutation/audit,
API-key/BEARER/PER_SHOP rejection direction and no-network/no-secret scope are useful
and must be preserved.

Attempt 1 is not accepted because the production service does not yet implement the
accepted C21 cross-service contract or the reusable command-kernel boundary that
`COMMERCE-028` must consume. The corrections below are functional contract fixes;
they are not a request for an exhaustive test matrix.

#### A1-R1 — consume the accepted Shared 0.14.2 connection contract exactly

**Source/dependency change required.**

Files permitted/expected:

```text
moda-interact-commerce/package.json
moda-interact-commerce/package-lock.json
moda-interact-commerce/src/commerce/connections/lifecycle/types.ts
moda-interact-commerce/src/commerce/connections/lifecycle/index.ts
moda-interact-commerce/src/commerce/connections/command-kernel.ts
moda-interact-commerce/tests/connection-lifecycle.test.ts
```

Current defect:

```text
package.json / package-lock.json -> @modainteract/moda-interact-shared 0.13.1
SHARED-002 accepted/public package -> @modainteract/moda-interact-shared 0.14.2
```

`lifecycle/types.ts` also redefines C21's Shared-owned `ConnectionCommandSchema`,
`RevisionInputSchema`, `ConnectionRevisionView`, `ConnectionView` and
`ConnectionResult`. This is prohibited by the accepted Shared boundary and has already
caused a material wire mismatch: the local result union adds `message` to
`not-found`, `forbidden`, `unavailable` and `conflict`, while the published 0.14.2
`ConnectionResultSchema` is strict and does not contain those fields.

Required implementation:

1. Pin exactly:

   ```json
   "@modainteract/moda-interact-shared": "0.14.2"
   ```

   in `package.json`; reconcile `package-lock.json` so the root dependency and
   `node_modules/@modainteract/moda-interact-shared` resolve exactly `0.14.2`.
   Do not use a range and do not republish Shared.
2. Consume/re-export the canonical connection exports from exactly:

   ```ts
   @modainteract/moda-interact-shared/commerce
   ```

   including, where used:

   ```text
   IdSchema
   ConnectionCommandSchema / ConnectionCommand
   RevisionInputSchema / RevisionInput
   ConnectionRevisionViewSchema / ConnectionRevisionView
   ConnectionViewSchema / ConnectionView
   ConnectionResultSchema / ConnectionResult
   ```

3. Delete the local Zod/type copies of those Shared-owned contracts. A local
   service-only request schema is allowed only for fields that C21 did not publish as a
   standalone Shared request DTO (for example create/update command composition); it
   must build from the canonical Shared schemas/primitives rather than redefining them.
4. Return the 0.14.2 result envelope exactly:

   ```text
   success:      {kind:'ok', value: ...}
   not found:    {kind:'not-found'}
   forbidden:    {kind:'forbidden'}
   unavailable:  {kind:'unavailable'}
   invalid:      {kind:'invalid', issues:[...]}
   conflict:     {kind:'conflict', code:'STALE_CAS'|'CONFLICTING_REPLAY'}
   ```

   Do not expose an internal exception message by adding a `message` field to a strict
   Shared result variant. Invalid issues remain bounded by the Shared schema.
5. Internal `LifecycleError` messages may remain server-internal for control flow; they
   must not change the Shared response shape.

Required focused proof:

- Import the connection schemas/types from the real 0.14.2 package in the focused test.
- Parse at least one successful `ConnectionView`, one `invalid`, one `forbidden`, one
  `not-found` and one `conflict` service result through the appropriate
  `ConnectionResultSchema(...)`/Shared value schema and prove strict parsing succeeds.
- Assert the non-success strict variants contain no invented `message` property.

#### A1-R2 — make `createConnectionCommandKernel` match C21 9.2 and serialize the connection row

**Source change required.**

File:

```text
moda-interact-commerce/src/commerce/connections/command-kernel.ts
```

and update lifecycle callers/tests accordingly.

Required public kernel contract:

```text
createConnectionCommandKernel({prisma,clock,commandHmacKey})
  .execute({principal,action,input,connectionId,mutate})
```

The property is `input`, not `command`.

The accepted action set is exactly the database/C21 action set:

```text
CREATE_CONNECTION
UPDATE_METADATA
CREATE_REVISION
SET_ENABLED
SET_CREDENTIAL
REMOVE_CREDENTIAL
```

`COMMERCE-020` does not implement credential mutations, but its reusable kernel MUST
accept the two credential actions so `COMMERCE-028` can consume it without duplicating
ledger/auth/transaction behavior.

Required mutation return shape:

```ts
{
  value: Record<string, unknown>;
  connectionId: string;
  connectionRevisionId: string | null;
  shopId: string | null;
}
```

Those nullable fields are required, not optional. Lifecycle callbacks return explicit
`null` where not applicable.

Required execution order inside the same READ COMMITTED transaction:

```text
1. repeat/establish current staff authorization;
2. require SUPER_ADMIN for mutation;
3. lookup (actorAdminId, operationId) replay;
4. if same digest -> return stored value without mutate;
5. if different digest -> CONFLICTING_REPLAY without mutate;
6. on replay miss and connectionId != null -> acquire an actual PostgreSQL row lock
   on commerce."CommerceExternalConnection" for that exact id using SELECT ... FOR UPDATE;
7. if the locked row does not exist -> NOT_FOUND; do not call mutate and do not append audit;
8. call mutate with the same Prisma TransactionClient and actor id;
9. append the audit in that same transaction;
10. commit once.
```

For step 6, a normal Prisma `findUnique`/`findUniqueOrThrow` is NOT a row lock. Use the
transaction client's parameterized raw-query facility (`Prisma.sql` / `$queryRaw`) or
another actual PostgreSQL `FOR UPDATE` mechanism. Do not interpolate the ID into raw
SQL text. `connectionId` is `null` only for `CREATE_CONNECTION`; reject an invalid
kernel call shape rather than silently running an unlocked non-create mutation.

Keep the existing unique-audit-race reconciliation after transaction failure: same
digest returns the committed winner; different digest returns `CONFLICTING_REPLAY`;
no winner returns bounded unavailable. Do not move business writes outside the
transaction.

Required focused proof:

- Directly exercise the kernel with `action: 'SET_CREDENTIAL'` and a non-null
  `connectionId`; prove the action is accepted, the connection lock occurs before
  `mutate`, `mutate` runs once, and the audit records `SET_CREDENTIAL`.
- Make the fake transaction's lock operation observable. The test must fail if the
  implementation substitutes `findUnique` for the real lock seam.
- Missing connection on a non-create action returns canonical `{kind:'not-found'}` at
  the lifecycle/result boundary, with zero mutate/audit effect.

#### A1-R3 — materialize and verify the development SUPER_ADMIN before FK-backed writes

**Source change required.**

File:

```text
moda-interact-commerce/src/commerce/connections/command-kernel.ts
```

C7.1 requires a server-resolved development-bypass principal to have the reserved
`PlatformAdmin` backing row established and verified **inside the same transaction**
before FK-backed writes. Attempt 1 currently treats `developmentBypass` as an in-memory
staff row and then writes revision/audit FKs using that id; a clean development database
can therefore fail instead of exercising the supported development principal.

Required implementation:

1. Reuse, do not copy, the accepted COMMERCE-002 helper:

   ```ts
   ensureDevelopmentStudioAdmin(transaction, principal)
   ```

   from the existing server-only auth module.
2. For `principal.developmentBypass === true`, call that helper inside the command
   transaction before replay lookup and before any revision/audit FK write. Let the
   helper enforce the development environment and exact reserved identity.
3. For a hosted/non-bypass principal, retain the in-transaction `PlatformAdmin` reload
   and require `active === true` plus exact role match.
4. In both paths, only `SUPER_ADMIN` may continue to replay/mutation.
5. Do not create/update an auth row at service construction, list/get, process startup,
   or outside the transaction. Do not silently promote a real staff record.

Required focused proof:

- Execute one mutation using the canonical development principal in a development
  environment against a fake transaction exposing the auth helper's raw SQL seam;
  prove backing-identity establishment occurs before replay/business/audit.
- Preserve a hosted inactive/ADMIN case where audit replay is pre-seeded with an old
  success; the call must return canonical `forbidden` **before replay is read** and
  `mutate` must not run. A replay lookup trap/counter is sufficient proof.

#### A1-R4 — validate the complete lifecycle inputs and canonicalize origin exactly

**Source change required.**

File:

```text
moda-interact-commerce/src/commerce/connections/lifecycle/index.ts
```

with focused regressions in:

```text
moda-interact-commerce/tests/connection-lifecycle.test.ts
```

Attempt 1 validates only the base command and revision. It passes key/display-name/
description/CAS/id fields directly to Prisma, clamps invalid list limits, and preserves
an authored explicit `:443`. C21 requires strict section-4 inputs and canonical origin
storage.

Required input behavior before any database effect:

```text
connection key:
  ^[a-z][a-z0-9_]{0,127}$

displayName:
  string <= 255 characters and btrim/display trim must not be empty

description:
  string <= 4096 characters

connectionId / cursor / operationId:
  canonical Shared IdSchema where applicable

expectedEditVersion:
  positive integer

limit:
  absent -> 25
  present -> integer 1..100
  0, negative, fractional or >100 -> invalid (DO NOT clamp)

revision:
  canonical Shared RevisionInputSchema, then the C21 service semantic checks
```

Use strict local action schemas composed from the Shared schemas/primitives so unknown
request fields are rejected. Invalid request data returns canonical
`{kind:'invalid',issues:[...]}` and causes zero business/audit writes.

Origin normalization must produce exactly the canonical origin. In particular:

```text
input:   HTTPS://API.EXAMPLE.COM:443/
stored:  https://api.example.com
```

Do not store a trailing slash or explicit default port. Continue rejecting userinfo,
non-443 ports, IP literals, query, fragment, non-root paths, single-label/local hosts,
`PER_SHOP + NONE`, forbidden API-key header names and invalid HTTP token names.

Required focused proof:

Add bounded cases proving all of the following through the real lifecycle service:

```text
- create with key "Bad-Key" -> invalid, zero connection/audit write;
- create/update with blank displayName -> invalid;
- description length 4097 -> invalid;
- expectedEditVersion 0 -> invalid (not STALE_CAS);
- list limit 0 and 101 -> invalid (not clamped);
- HTTPS://API.EXAMPLE.COM:443/ stores/returns https://api.example.com;
- existing valid CL01 create -> metadata -> revision -> disable -> enable still succeeds.
```

Do not add credential storage, credential status, HTTP execution, OAuth, browser UI or
final factory work to satisfy this correction.

### Attempt 1 — Validation Reviewed

Submitted supporting evidence:

```text
npm run test:arch020-external-connection-lifecycle     PASS (5 focused tests)
focused ESLint                                        PASS
git diff --check                                      PASS
repository typecheck                                  non-zero outside task-owned files
```

The five focused tests support the implementation direction but do not cover the
contract mismatches above. The fake rollback test also proves only that no success audit
is appended; the fake map transaction does not itself model PostgreSQL rollback. The
production source correctly keeps mutation and audit inside one Prisma transaction, so
this review does not require an unrelated PostgreSQL/container matrix merely to restate
that structure.

Attempt 2 validation is deliberately bounded. Run:

```text
npm run test:arch020-external-connection-lifecycle
npx eslint src/commerce/connections/command-kernel.ts \
  src/commerce/connections/lifecycle/index.ts \
  src/commerce/connections/lifecycle/types.ts \
  tests/connection-lifecycle.test.ts
npm run typecheck
git diff --check
```

Also run `npm run build` because the task's existing Validation contract requires the
repository build where defined. If repository-wide typecheck/build remains non-zero
only in files untouched by this task, record the exact command/failure and prove the
Attempt 2 changed files introduce no diagnostics; do not modify unrelated files merely
to manufacture a green global command.

### Attempt 1 — Architecture Conformance

Not yet conformant. The central lifecycle mechanics are within the correct repository
and ownership boundary, but the implementation currently bypasses the accepted Shared
contract, does not expose a credential-capable reusable kernel, does not provide the
required same-connection row lock, does not materialize the supported development
principal before FK writes, and does not strictly validate all section-4 inputs.

Preserve from Attempt 1:

```text
- no credential encryption/storage/resolution;
- no outbound HTTP/network behavior;
- immutable revision creation rather than mutation;
- explicit desired enabled value rather than toggle semantics;
- HMAC-SHA256 canonical request digest direction;
- authorization-before-replay ordering for hosted principals;
- transaction-scoped business mutation plus audit append;
- same-digest replay / altered-digest conflict direction;
- API-key forbidden-header and PER_SHOP+NONE rejection direction.
```

### Attempt 1 — Follow-up / Stop Condition

Return this same task to `ready`, retain `attempt: 1`, and keep `executor: null` and
`claimed_at: null`.

On the next authorized `/moda-task ARCH-020-COMMERCE-020` claim, increment to
**Attempt 2 exactly once**. Implement only A1-R1 through A1-R4. Do not begin
`ARCH-020-COMMERCE-028`, `ARCH-020-COMMERCE-024`, `ARCH-020-GATEWAY-003`,
`ARCH-020-COMMERCE-012` or any system-test task.

Before returning, update Work Items / Acceptance Criteria / Validation checkboxes only
for behavior actually satisfied, update the Completion Report with exact changed files,
exact Shared package version and command results, set the task back to `review`, clear
`executor`/`claimed_at`, push both mirrored task branches, return control to
`moda_architect`, and **STOP**.

## Architect Review — Attempt 2 — 2026-09-22

### Review Status

Accepted

### Review Notes

Reviewed the submitted implementation identified by the Completion Report as
`d2b7154` and parent report `a6d09e32` against the exact Attempt-1 A1-R1..A1-R4
correction contract and C21 sections 4 and 9.2.

Attempt 2 resolves the functional contract gaps from Attempt 1:

- Commerce consumes exact `@modainteract/moda-interact-shared@0.14.2`;
- Shared owns/re-exports the canonical connection command/revision/view/result
  schemas and types; the local duplicate wire contracts are removed;
- lifecycle results use the strict Shared envelopes without invented public
  `message` fields;
- the reusable command kernel exposes the exact six accepted actions, including
  `SET_CREDENTIAL` and `REMOVE_CREDENTIAL`, and uses the required
  `.execute({principal,action,input,connectionId,mutate})` shape;
- non-create commands acquire an actual parameterized PostgreSQL
  `SELECT ... FOR UPDATE` lock on the exact connection before mutation;
- development bypass calls the accepted `ensureDevelopmentStudioAdmin(...)`
  helper inside the same transaction before replay/FK-backed writes;
- hosted authorization is repeated inside the transaction before replay;
- lifecycle create/update/revision/enabled inputs are strict and bounded;
- invalid list limits reject instead of clamp;
- default HTTPS port canonicalization stores/returns
  `https://api.example.com` without trailing slash or explicit `:443`;
- revision allocation remains behind the same-connection lock and published
  references are not migrated;
- credential storage/resolution, HTTP execution, OAuth, UI and final-factory work
  remain outside COMMERCE-020 ownership.

The implementation therefore satisfies the bounded connection lifecycle and reusable
command-kernel producer contract required by COMMERCE-028.

### Reviewed Files

- `moda-interact-commerce/package.json`
- `moda-interact-commerce/package-lock.json`
- `moda-interact-commerce/src/commerce/connections/command-kernel.ts`
- `moda-interact-commerce/src/commerce/connections/lifecycle/index.ts`
- `moda-interact-commerce/src/commerce/connections/lifecycle/types.ts`
- `moda-interact-commerce/tests/connection-lifecycle.test.ts`
- `moda-interact-commerce/lib/auth/development-platform-admin.ts`
- `moda-interact-commerce/database/prisma/schema.prisma`

### Validation Reviewed

Submitted evidence:

```text
npm run test:arch020-external-connection-lifecycle    PASS (9/9)
focused ESLint                                        PASS
git diff --check                                      PASS
npm run typecheck                                     non-zero only in unrelated
                                                      src/commerce/integration/**
npm run build                                         same unrelated baseline
```

Architect source inspection confirmed no remaining A1-R1..A1-R4 functional defect in
the task-owned implementation. The uploaded review archive does not include installed
`node_modules`, so the architect did not manufacture another dependency-backed run.

Real PostgreSQL/container validation was not claimed and is not required to accept
this bounded producer task; later credential/integration/system-test work owns the
assembled database scenarios. This acceptance does not convert the in-memory focused
test into evidence of PostgreSQL rollback semantics beyond the production transaction
structure actually inspected.

### Architecture Conformance

Conformant for COMMERCE-020.

Accepted invariants include:

```text
Shared 0.14.2 canonical contract
SUPER_ADMIN mutation authorization before replay
development principal materialization before FK-backed writes
HMAC-SHA256 canonical {action,input} replay digest
same-operation replay / changed-input conflict
READ COMMITTED transaction
same-connection FOR UPDATE lock
business mutation + audit in one transaction
immutable connection revisions
strict lifecycle request bounds
canonical HTTPS origins
no credentials or outbound HTTP in COMMERCE-020
```

### Follow-up

`ARCH-020-COMMERCE-020` is Complete at Attempt 2.

`ARCH-020-COMMERCE-028` is promoted from Pending to Ready because its other declared
dependencies (`DATABASE-003` and `SHARED-002`) are already Complete.

Do not automatically launch COMMERCE-028. `COMMERCE-024`, `GATEWAY-003`,
`COMMERCE-012` and later system-test work remain gated by their other declared
dependencies.
