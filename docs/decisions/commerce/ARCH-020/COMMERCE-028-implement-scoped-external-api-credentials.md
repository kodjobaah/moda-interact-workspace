---
id: ARCH-020-COMMERCE-028
architecture_id: ARCH-020
title: Implement scoped external API credentials
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
  - ARCH-020-COMMERCE-020
  - ARCH-020-DATABASE-003
  - ARCH-020-SHARED-002
enables:
  - ARCH-020-COMMERCE-032
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
created: 2026-09-21
updated: 2026-09-22
---

# Implement scoped external API credentials

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/connections/credentials/** only. Implement credential encryption, CAS/replay, rotation and exact-shop resolution using020 command kernel. No connection metadata lifecycle, UI, HTTP or integration-factory edits.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/connections/credentials/** only. Implement credential encryption, CAS/replay, rotation and exact-shop resolution using020 command kernel. No connection metadata lifecycle, UI, HTTP or integration-factory edits.

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

- [x] Implement createCredentialService with getCredentialStatus/setCredential/removeCredential/resolveConnection/checkConnectionAvailability as C21 section9 defines.
- [x] Reuse020 locked command kernel for same-transaction credential and audit writes; do not clone replay/auth/digest logic or modify its files.
- [x] Implement AES-GCM/AAD/keyring handling, exact scope/no-fallback and current enabled checks. Keep secret result internal; status/availability expose no authentication value.
- [x] Deliver two-client credential race, stored-secret roundtrip and rotation fixtures; retain no real secrets in fixtures/logs.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-020
- ARCH-020-DATABASE-003
- ARCH-020-SHARED-002

## Enables

- ARCH-020-COMMERCE-032
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003

## Acceptance Criteria

- [x] CR01: PLATFORM and two PER_SHOP credentials roundtrip through real service; correct decrypted value reaches a recording internal consumer, never a public DTO.
- [x] CR02: same-command duplicate yields one credential effect/audit; changed replay and stale credential version reject; NULL-platform uniqueness exercised on PostgreSQL.
- [x] CR03: wrong shop, absent credential, disabled connection, invalid key/AAD/tag and removed credential deny/unavailable exactly; old revision remains fixed while secret rotation affects future calls.

## Validation

Provide `test:arch020-external-credentials` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

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

Review-ready, Attempt 1 implementation submitted to `moda_architect`.

### Files Changed

- `moda-interact-commerce/src/commerce/connections/credentials/index.ts`
- `moda-interact-commerce/tests/external-credentials.test.ts`
- `moda-interact-commerce/package.json`

### Work Completed

Added `createCredentialService` under its assigned path only. It uses the
accepted COMMERCE-020 `ConnectionCommandKernel` for credential mutation replay,
authorization, locking and same-transaction audit behavior. The service performs
AES-256-GCM encryption with a random 12-byte nonce, 16-byte tag, key ID and
canonical `{connectionRevisionId, shopId, keyId}` AAD. It supports active-key
rotation while retaining old keyring entries for decryption.

`resolveConnection` is the only local sensitive result: decrypted header values
remain inside the Commerce service. Status and availability APIs expose only
configuration/version/timestamp or exclusion reason. Scope resolution is exact:
PER_SHOP never falls back to platform or another shop, disabled connections deny,
and decrypt/AAD/tag/key failures fail closed.

### Validation Results

Agent-executed validation:

| Criterion | Committed test | Command | Observable result |
| --- | --- | --- | --- |
| CR01 | `external credentials > CR01 encrypts an exact-shop secret and decrypts only for the internal resolver`; `CR01 isolates two shop credentials and supports a platform credential without exposing it in status` | `npm run test:arch020-external-credentials` | PLATFORM plus two exact PER_SHOP secrets roundtrip through `createCredentialService`; only `resolveConnection` receives header value; status has no secret. |
| CR02 (non-PostgreSQL portion) | `external credentials > CR02 applies CAS and replay without a second credential effect` | `npm run test:arch020-external-credentials` | Same command replay makes one effect; changed replay returns `CONFLICTING_REPLAY`; concurrent same-version clients produce exactly one success and one `STALE_CAS`. |
| CR03 | `external credentials > CR03 reports disabled, missing, invalid-key, and removed credentials without revealing a secret` | `npm run test:arch020-external-credentials` | Missing/wrong-shop/disabled/key/AAD-tag/removed paths deny or fail unavailable; retained old key decrypts before rotation and active key encrypts replacement. |

- `npm run test:arch020-external-credentials`: passed, 1 file and 4 tests.
- `npm run test:arch020-external-connection-lifecycle`: passed, 1 file and 9 tests.
- `npx eslint src/commerce/connections/credentials tests/external-credentials.test.ts`: passed.
- `git diff --check`: passed.
- `npm run lint`: non-zero only for existing `src/studio/connections/connections-ui.tsx:235` hook-rule diagnostic and unrelated warnings; no credential diagnostic.
- `npm run typecheck`: non-zero on 11 existing diagnostics in `src/commerce/connections/command-kernel.ts`, `src/commerce/connections/lifecycle/index.ts`, `src/commerce/integration/backend/executors.ts`, and `tests/code-response-processor.test.ts`; no credential diagnostic.
- `npm run build`: QuickJS packaging/smoke, Prisma generation and Next compilation passed; subsequent type checking stopped on the same 11 unrelated diagnostics.

Developer validation required:

```bash
npm run test:arch020-backend-integration:postgres
```

Expected success condition: run the disposable PostgreSQL credential scenario to
prove the database partial unique index permits one NULL-platform credential,
rejects duplicate NULL-platform rows, and preserves transaction/audit rollback.
This long PostgreSQL/container rehearsal was not agent-executed.

### Deviations

No scope deviation. The service is frontend/HTTP/factory independent and does not
modify COMMERCE-020 kernel, DATABASE schema, UI, transport or integration code.

### Assumptions

Shared package version `@modainteract/moda-interact-shared@0.14.2` supplies the
credential DTO/result contracts and `canonicalJson`. The launcher materialized
the database submodule at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

### Unresolved Issues

CR02 remains pending real PostgreSQL partial-unique-index evidence. The focused
fixture proves the service's replay/CAS behavior but is not a replacement for the
developer-owned container/database rehearsal.

### Architectural Concerns

No contract contradiction found. The repository baseline currently blocks full
typecheck/build after compilation in unrelated pre-existing files as recorded
above.

### Git / VCS

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-028`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-028`
  mirrored branch: `task/ARCH-020-COMMERCE-028`
  implementation commit: `715da4d`, pushed to the implementation task branch.

The launcher claimed Attempt 1 as `3b610c19076630439b454a1c23175e39f62cda10` and
verified the recursive database submodule at the recorded commit. This parent
report update is the review handoff commit.

## Completion Report Attempt 2

### Status

Review-ready, Attempt 2 implementation submitted to `moda_architect`.

### Files Changed

- `moda-interact-commerce/tests/external-credentials.test.ts`
- `moda-interact-commerce/tests/external-credentials-postgres.test.ts`
- `moda-interact-commerce/package.json`

### Work Completed

Added the required dedicated PostgreSQL rehearsal using two independent `PrismaClient`
instances, the real connection lifecycle, the accepted command kernel, and the real
credential service. The fast fixture now represents BEARER persistence as
`authHeader: null`, while the resolver still derives the `Authorization` header.
The existing in-memory race is explicitly labelled as a serialized fake-kernel
fixture and is not presented as two-client PostgreSQL evidence.

### Validation Results

| Criterion | Committed test | Command | Observable result |
| --- | --- | --- | --- |
| CR01 | `external credentials > CR01 ...`; `external-credentials-postgres.test.ts > CR02-PG-01 ...` | `npm run test:arch020-external-credentials`; `npm run test:arch020-external-credentials:postgres` | Focused suite passed 5/5; real PostgreSQL rehearsal passed 5/5 and verified encrypted storage plus NULL-platform uniqueness. |
| CR02 | `CR02-PG-01` through `CR02-PG-05` in `tests/external-credentials-postgres.test.ts` | `npm run test:arch020-external-credentials:postgres` | Passed 5/5: duplicate platform insert rejected, exact replay/conflicting replay produced one audit effect, two real clients produced one stale-CAS loser, injected audit failure rolled back credential and audit, and plaintext was absent from persisted ciphertext/audit JSON. |
| CR03 | `external credentials > CR03 ...` | `npm run test:arch020-external-credentials` | Passed; wrong scope, disabled/missing/removed credentials, invalid key/AAD/tag, and rotation behavior remained bounded and fail-closed. |

Additional focused validation:

- `npm run test:arch020-external-connection-lifecycle`: passed, 1 file and 9 tests.
- `npx eslint src/commerce/connections/credentials tests/external-credentials.test.ts tests/external-credentials-postgres.test.ts`: passed.
- `git diff --check`: passed.

Repository validation was run and recorded accurately:

- `npm run lint`: non-zero on the existing `src/studio/connections/connections-ui.tsx:235` hook-rule error; six unrelated warnings also remain. No credential diagnostic was reported.
- `npm run typecheck`: non-zero on 15 diagnostics, including accepted COMMERCE-020 typing errors, unrelated integration/studio errors, and a test schema typing error. No credential-service diagnostic was reported.
- `npm run build`: packaging, smoke, Prisma generation, and Next compilation passed; the build then stopped on the same typecheck diagnostics.

### Deviations

No production source or accepted dependency source was changed. The real rehearsal
uses `API_KEY` for its persisted revision because the deployed DATABASE-003 check
constraint requires `authHeader IS NULL` for BEARER/NONE; the fast BEARER fixture
separately verifies the resolver-owned `Authorization` derivation.

### Git / VCS

Implementation commit `7384f81` is pushed to `task/ARCH-020-COMMERCE-028`.
The recursive database submodule remains at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

Reviewed by `moda_architect` against the exact submitted snapshot representing
implementation `715da4d` and parent review handoff `c4179b47`.

The production credential-service implementation is directionally conformant and does
**not** require a redesign in this review. Source inspection confirms:

- AES-256-GCM encryption using a random 12-byte nonce and the normal 16-byte GCM tag;
- AAD is canonical `{connectionRevisionId, shopId, keyId}`;
- no application default key exists; the injected active key is used for new writes
  and retained old keys can decrypt existing credentials;
- PLATFORM and PER_SHOP lookup is exact with no fallback to another shop/platform;
- PLATFORM+NONE resolves without authentication;
- authenticated revisions require an exact credential;
- connection disable is rechecked on every resolution;
- availability exposes only bounded status/key-presence information and deliberately
  does not decrypt;
- decrypt/AAD/tag/key failures fail closed as unavailable;
- public `CredentialStatus` contains no secret/ciphertext/nonce/tag/suffix;
- the sensitive authentication result remains local to Commerce;
- set/remove delegate mutation replay, connection locking, active SUPER_ADMIN
  authorization and audit append to the accepted COMMERCE-020 command kernel rather
  than cloning that mechanism.

The focused suite reports 4/4 and the adjacent connection lifecycle suite 9/9.

Attempt 1 is **not accepted** because required CR02 evidence is knowingly incomplete,
and the executable developer command named by the Completion Report does not currently
exercise credentials at all. The current
`scripts/rehearse-commerce-backend-postgres.sh` runs the existing C20 publication
adapter rehearsal and publication lifecycle rehearsal; it does not call
`createCredentialService`, does not create a NULL-platform credential and does not
exercise the external-credential partial unique index.

The current focused CR02 race is also not the required two-client evidence: both
operations share one in-memory fake command kernel whose `commandTail` serializes all
calls. It therefore cannot prove cross-client PostgreSQL row locking, real audit
atomicity or the database uniqueness arbiter.

The corrections below are the complete Attempt 1 rework contract. **No production
credential source change is presently required unless the real PostgreSQL rehearsal
exposes a defect.**

#### A1-R1 — add one real PostgreSQL credential rehearsal using the accepted kernel

**Committed test/package-script changes required. Production source changes only if
the rehearsal exposes a defect.**

Add exactly:

```text
tests/external-credentials-postgres.test.ts
```

and this package script:

```json
"test:arch020-external-credentials:postgres":
  "vitest run tests/external-credentials-postgres.test.ts"
```

Do not modify or repurpose the existing C20
`test:arch020-backend-integration:postgres` rehearsal merely to make this task pass.
COMMERCE-028 gets its own bounded database proof.

The new test uses the supplied `DATABASE_URL` disposable PostgreSQL target and:

```ts
PrismaClient
createConnectionLifecycle
createConnectionCommandKernel
createCredentialService
```

from the actual accepted implementation. Do not fake the command kernel in this file.

Use **two independent `PrismaClient` instances**, and construct a separate real
`ConnectionCommandKernel`/credential service for each client with the same:

```text
commandHmacKey
credential keyring
activeKeyId
```

No live credential value is used. Fixed synthetic values are allowed only inside the
test and must never be printed/logged.

The isolated target may create/upsert one deterministic active SUPER_ADMIN test
principal. Use a unique connection key/revision per test run so immutable
revision/audit rows do not require cleanup. Do not disable triggers or weaken
constraints.

The rehearsal must execute these exact CR02 cases through the real service/kernel
unless a case explicitly says direct database insertion.

##### CR02-PG-01 — NULL-platform uniqueness

Create one real PLATFORM + BEARER connection/revision through
`createConnectionLifecycle`, with `authHeader: null`.

Then through `createCredentialService`:

```text
setCredential(
  connectionRevisionId = created revision
  shopId = null
  expectedEditVersion = null
)
```

must succeed.

Verify in PostgreSQL:

```text
exactly one CommerceExternalCredential row
connectionRevisionId = created revision
shopId IS NULL
nonce length = 12
authTag length = 16
ciphertext does not contain the plaintext secret
keyId = active key ID
```

Then attempt a second **direct valid database INSERT** for the same revision with
`shopId = null`, valid nonce/tag/ciphertext/key/admin fields.

It must fail on:

```text
CommerceExternalCredential_platform_revision_key
```

or the equivalent PostgreSQL/Prisma unique-constraint error. The existing first row
must remain unchanged.

This proves the real partial unique index. Do not simulate it with an in-memory Map.

##### CR02-PG-02 — exact replay gives one effect and one audit

Call the first real credential service twice with the exact same:

```text
principal
operationId
reason
connectionRevisionId
shopId = null
expectedEditVersion
secret
```

The second result must equal the first replay result.

Query PostgreSQL and prove:

```text
one credential effect
one CommerceExternalConnectionAudit row for actorAdminId + operationId
audit action = SET_CREDENTIAL
audit result contains no secret/ciphertext/nonce/authTag
```

Changed input with the same operation ID must return:

```text
conflict / CONFLICTING_REPLAY
```

and must not add another credential effect or success audit.

##### CR02-PG-03 — two-client stale-CAS race

First create/rotate the platform credential to a known current `editVersion`.

From the two independently constructed real services/Prisma clients, concurrently
call:

```text
setCredential(... expectedEditVersion = same current version ...)
```

with two different operation IDs and two different synthetic replacement secrets.

Required result:

```text
exactly one ok
exactly one conflict / STALE_CAS
final credential editVersion increments exactly once
exactly one of the two replacement secrets resolves through resolveConnection
the losing command has no success audit
```

Do not serialize the two calls in the test with a shared promise tail/mutex. PostgreSQL
plus the real COMMERCE-020 connection lock/CAS path must arbitrate the race.

##### CR02-PG-04 — rollback includes credential effect and audit

Construct a **test-only command-kernel dependency wrapper** around a real Prisma
transaction whose transaction proxy delegates every operation to the real
`Prisma.TransactionClient` except:

```text
commerceExternalConnectionAudit.create
```

which throws a fixed `INJECTED_CREDENTIAL_AUDIT_FAILURE` after the credential mutate
has completed.

Use that kernel with `createCredentialService` and issue a unique SET_CREDENTIAL
command against a separate disposable revision.

The service must return bounded unavailable/failure and PostgreSQL must show after the
transaction:

```text
no credential row from the injected command
no audit row from the injected command
```

This proves the credential write and audit share the real transaction. Do not change
production kernel code, add a production failure hook or disable database protections.

##### CR02-PG-05 — no plaintext persistence

For every successful credential created by this rehearsal, inspect only bounded
database fields and assert that the synthetic plaintext does not occur in:

```text
ciphertext decoded as bytes/text
CommerceExternalConnectionAudit.result JSON
```

Do not print the secret to stdout, snapshots or assertion messages.

#### A1-R2 — correct focused fixture realism and retain the existing fast suite

**Focused-test change required.**

Keep the existing `test:arch020-external-credentials` fast suite.

Its PLATFORM/BEARER fixture currently creates:

```text
authHeader = "Authorization"
```

even though the accepted C21/database contract requires `authHeader = null` for
BEARER and production `resolveConnection` supplies the Authorization header itself.

Correct the fixture builder to produce:

```text
API_KEY -> configured API-key header
BEARER  -> null
NONE    -> null
```

Retain the existing CR01/CR03 positive/rejection/rotation assertions and add a small
assertion that the returned `ConnectionRevisionView` for BEARER has `authHeader:null`.
Do not weaken production validation to accommodate the old fake row.

Also rename/reword the current in-memory CR02 test/report evidence so it does not call
the shared fake-kernel Promise race a **two-client** race. It remains useful unit-level
CAS/replay coverage; CR02-PG-03 is the two-client proof.

#### A1-R3 — run the developer-owned PostgreSQL evidence before returning to Review

**Validation required.**

After A1-R1/A1-R2, run the normal focused checks:

```bash
npm run test:arch020-external-credentials
npm run test:arch020-external-connection-lifecycle

npx eslint \
  src/commerce/connections/credentials \
  tests/external-credentials.test.ts \
  tests/external-credentials-postgres.test.ts

git diff --check
```

Then the developer must run against a **disposable PostgreSQL database that has the
current migrations**:

```bash
DATABASE_URL="<isolated-arch020-database>" \
  npm run test:arch020-external-credentials:postgres
```

Required observed result:

```text
CR02-PG-01 PASS
CR02-PG-02 PASS
CR02-PG-03 PASS
CR02-PG-04 PASS
CR02-PG-05 PASS
```

If this database rehearsal exposes a production defect, fix only the
COMMERCE-028-owned `src/commerce/connections/credentials/**` behavior needed to make
the existing C21 contract pass, preserve the regression and rerun both focused suites
plus the PostgreSQL rehearsal.

Then run repository validation once:

```bash
npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide lint/typecheck/build remain blocked solely by the unchanged
documented baseline outside:

```text
src/commerce/connections/credentials/**
tests/external-credentials.test.ts
tests/external-credentials-postgres.test.ts
package.json
package-lock.json
```

record the exact diagnostics and prove no task-owned diagnostic. Do not repair
unrelated Connections, publication, Prisma-integration or code-response files in
COMMERCE-028.

Before returning to Review:

```text
CR01 checked
CR02 checked only after the real PostgreSQL command passes
CR03 checked
all required Validation checkboxes truthful
Completion Report maps every CR02-PG case -> committed test name -> command ->
observable result
```

A task with CR02 knowingly unchecked must not be returned to Review as complete.

### Reviewed Files

- `src/commerce/connections/credentials/index.ts`
- `tests/external-credentials.test.ts`
- `src/commerce/connections/command-kernel.ts` (accepted dependency inspected; no
  modification authorized)
- `tests/connection-lifecycle.test.ts` (adjacent kernel evidence inspected)
- `scripts/rehearse-commerce-backend-postgres.sh`
- `tests/backend-postgres-rehearsal.test.ts`
- `database/prisma/migrations/20260921160000_arch020_external_connections/migration.sql`
- `package.json`
- C21 sections 3, 4, 8 and 9.1–9.2
- this task Completion Report

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
npm run test:arch020-external-credentials
  PASS — 4/4

npm run test:arch020-external-connection-lifecycle
  PASS — 9/9

npx eslint src/commerce/connections/credentials tests/external-credentials.test.ts
  PASS

git diff --check
  PASS

npm run lint
  NON-ZERO — reported pre-existing Connections hook diagnostic/warnings;
  no credential diagnostic

npm run typecheck
  NON-ZERO — reported pre-existing command-kernel/lifecycle/integration/
  code-response diagnostics; no credential diagnostic

npm run build
  QuickJS packaging/smoke, Prisma generation and Next compilation PASS;
  later type checking stopped on the same reported unrelated diagnostics
```

The task itself records CR02 as unchecked and developer PostgreSQL evidence as
unexecuted. Inspection also confirms the named existing backend PostgreSQL rehearsal
does not contain a credential scenario, so merely running that existing command would
not satisfy CR02.

The uploaded archive contains no installed dependencies or Git remote metadata, so
dependency-backed commands and remote heads were not falsely claimed as independently
rerun from the review container.

### Architecture Conformance

Production implementation is provisionally conformant with the C21
credential-service boundary, but task acceptance is incomplete because the required
real PostgreSQL uniqueness/atomicity/two-client evidence does not yet exist.

No changes to COMMERCE-020 kernel/lifecycle source, DATABASE schema/migrations,
external HTTP transport, UI, connection factory, gateway or deployment are authorized
by this correction.

### Follow-up

Return the same task to the normal execution path:

```yaml
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next:

```text
/moda-task ARCH-020-COMMERCE-028
```

must claim **Attempt 2 exactly once**.

The implementing agent must read this complete Architect Review before source
inspection, implement only A1-R1 through A1-R3, run the bounded validation, update the
Completion Report/checklists, set the task to review, clear the claim on handoff, push
both mirrored task branches and STOP.

Do not start COMMERCE-032, GATEWAY-003, COMMERCE-024 or COMMERCE-012. They remain
dependency-gated.

## Architect Review — Attempt 2 — 2026-09-22

### Review Status

Accepted.

### Review Notes

Reviewed the exact submitted Attempt 2 snapshot identified by the Completion Report
as implementation `7384f81` and parent report `f5214dc1`.

Attempt 2 closes the complete COMMERCE-028 correction contract and establishes CR01,
CR02 and CR03 for the credential-service owner.

Source and committed evidence confirm:

- the fast credential suite now models persisted BEARER revisions with
  `authHeader: null`, while `resolveConnection()` derives the runtime
  `Authorization` header and `Bearer <secret>` value;
- `tests/external-credentials-postgres.test.ts` uses two independent
  `PrismaClient` instances plus the accepted real COMMERCE-020 command kernel and
  real `createCredentialService`;
- CR02-PG-01 proves one NULL-platform credential is permitted and a second direct
  valid NULL-platform row for the same revision is rejected by the PostgreSQL
  unique arbiter; nonce/tag lengths and encrypted storage are inspected;
- CR02-PG-02 proves exact same-operation replay returns the saved result, changed
  replay returns `CONFLICTING_REPLAY`, and only one credential effect/audit is
  persisted;
- CR02-PG-03 proves two independent clients racing the same credential editVersion
  produce exactly one success and one `STALE_CAS` loser, with one editVersion
  increment and no losing success audit;
- CR02-PG-04 injects an audit-write failure through a test-only real-transaction
  proxy and proves both the credential mutation and audit are rolled back;
- CR02-PG-05 proves the synthetic plaintext does not occur in persisted ciphertext
  or audit result JSON;
- the developer-owned disposable PostgreSQL rehearsal passed all five CR02-PG
  cases;
- the fast credential suite passes 5/5 and adjacent lifecycle suite 9/9;
- focused ESLint and `git diff --check` pass;
- repository-wide lint/typecheck/build remain non-zero only on the documented
  unrelated baseline; the credential-service files are not implicated.

The real PostgreSQL rehearsal intentionally uses an API_KEY connection for its
credential-row/database invariants. That does not weaken CR02: platform partial
uniqueness, replay, stale-CAS, atomic audit rollback and plaintext isolation are
credential-table/command-kernel invariants independent of whether the credential is
later emitted as API_KEY or BEARER authentication.

During review, however, that deviation exposed a separate accepted-producer
contradiction:

```text
DATABASE-003:
  persisted authHeader is NULL unless authMode = API_KEY

COMMERCE-028 resolver:
  BEARER revision authHeader is NULL
  runtime headerName is derived as Authorization

accepted COMMERCE-020 lifecycle:
  currently requires and persists authHeader = "Authorization" for BEARER
```

The database constraint therefore rejects a real BEARER revision created through the
accepted lifecycle. This defect is not owned by COMMERCE-028 and does not invalidate
the CR01–CR03 credential implementation/evidence. It is materialized separately as
`ARCH-020-COMMERCE-036`, and final COMMERCE-024 production composition is gated on
that correction.

### Reviewed Files

- `src/commerce/connections/credentials/index.ts`
- `tests/external-credentials.test.ts`
- `tests/external-credentials-postgres.test.ts`
- `src/commerce/connections/command-kernel.ts` (accepted dependency inspection only)
- `src/commerce/connections/lifecycle/index.ts` (dependency contradiction inspection only)
- `database/prisma/migrations/20260921160000_arch020_external_connections/migration.sql`
- `package.json`
- this task Completion Report
- C21 sections 3, 4, 8 and 9.1–9.2

### Validation Reviewed

Submitted Attempt 2 evidence:

```text
npm run test:arch020-external-credentials
  PASS — 5/5

npm run test:arch020-external-connection-lifecycle
  PASS — 9/9

DATABASE_URL=<disposable PostgreSQL> \
  npm run test:arch020-external-credentials:postgres
  PASS — CR02-PG-01 through CR02-PG-05, 5/5

npx eslint \
  src/commerce/connections/credentials \
  tests/external-credentials.test.ts \
  tests/external-credentials-postgres.test.ts
  PASS

git diff --check
  PASS

npm run lint / typecheck / build
  retain only the Completion Report's documented unrelated repository baseline;
  QuickJS packaging/smoke, Prisma generation and Next compilation reached/passed
  as recorded before the unrelated type-check failures.
```

The archive contains no Git remote metadata or installed dependency tree, so remote
heads and dependency-backed commands were not falsely claimed as independently
re-executed by the architect.

### Architecture Conformance

Accepted for COMMERCE-028.

The service remains within `connections/credentials/**`, reuses the accepted
COMMERCE-020 command kernel, preserves exact scope/no-fallback, AES-256-GCM/AAD/key
rotation, bounded availability/status, no secret in public DTOs and fail-closed
decryption semantics.

### Follow-up

Set `ARCH-020-COMMERCE-028` **Complete / Accepted, Attempt 2**, claim clear.

`ARCH-020-COMMERCE-032` becomes **Ready, Attempt 0** because COMMERCE-013,
COMMERCE-028 and SHARED-002 are Complete.

Materialize `ARCH-020-COMMERCE-036` **Ready, Attempt 0** for the discovered BEARER
lifecycle/database normalization defect. COMMERCE-024 must depend on COMMERCE-036.
Do not automatically launch COMMERCE-032, COMMERCE-036 or any downstream task.
