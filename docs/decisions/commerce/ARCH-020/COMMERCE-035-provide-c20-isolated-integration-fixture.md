---
id: ARCH-020-COMMERCE-035
architecture_id: ARCH-020
title: Provide the C20 isolated integration fixture boundary
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 130
executor: copilot
claimed_at: 2026-09-22T00:26:47Z
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-013
enables:
  - ARCH-020-COMMERCE-018
  - ARCH-020-COMMERCE-019
created: 2026-09-21
updated: 2026-09-22
---

# Provide the C20 isolated integration fixture boundary

## Architecture

Architecture ID: ARCH-020.

Architecture document:
`docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md`.

Binding contract:
`docs/architecture/ARCH-020-implementation-contracts.md#c20-integration-task-ownership-and-parallel-execution`.

Coordinator: `moda_architect`.

This is a bounded post-acceptance producer-correction task. It does **not** reopen,
replace or redesign the accepted COMMERCE-013 production backend. It supplies only
the C20 test fixture boundary that C20 assigned to the backend producer and that
COMMERCE-018 Attempt 3 proved absent from the accepted source.

## Objective

Provide one deterministic, test-only C20 seed/reset boundary that lets
COMMERCE-018 and COMMERCE-019 run their required real PostgreSQL/Redis integration
paths without mocking Moda application services or weakening ARCH-020 database
invariants.

## Context

COMMERCE-018 Attempt 3 verified that accepted COMMERCE-013 exports the production
backend and `createFixtureExecution`, but does not export the isolated C20
seed/reset helper promised by the architecture. COMMERCE-018 correctly stopped
rather than creating a competing backend fixture. COMMERCE-019 consumes the same
C20 fixture and is therefore gated by this producer correction as well.

Published ARCH-020 revisions, release members and audit rows are deliberately
immutable. Therefore PostgreSQL reset **must not** be implemented as row-by-row
DELETEs or by disabling triggers. The PostgreSQL isolation boundary for this fixture
is a dedicated disposable test database. Redis isolation is a task-owned key prefix.

## Scope

Create the missing test-only fixture module and deterministic reset/rehearsal
entrypoint in `moda-interact-commerce`.

Authorized implementation files are:

- `src/commerce/integration/backend/c20-test-fixture.ts` — new test-only fixture API;
- `tests/c20-integration-fixture.test.ts` — new focused real PostgreSQL/Redis proof;
- `scripts/reset-c20-integration-fixture.mjs` — new guarded disposable-target reset;
- `package.json` — add only the named fixture validation/reset scripts;
- `docs/commerce-backend-integration.md` — document the exported fixture API,
  target guards and consumer contract.

If compilation requires a type-only import adjustment in an existing backend file,
record it explicitly in the Completion Report. Do **not** add this helper to a
production runtime barrel or application startup path.

## Out of Scope

- No changes to `getCommerceBackend()` production semantics.
- No changes to MCP routes, Studio pages/actions, preview runtime or C21 external API work.
- No Prisma schema or migration changes.
- No new Shared contract or npm publication.
- No live Shopify, Meta, WhatsApp or paid-model call.
- No `FLUSHALL`, `FLUSHDB`, production database reset, trigger disabling or
  `session_replication_role` bypass.
- No fixture registration reachable from a production request.
- Do not implement COMMERCE-018 or COMMERCE-019 acceptance flows in this task.

## Requirements

### R1. Exact module boundary

Create exactly:

`src/commerce/integration/backend/c20-test-fixture.ts`

It must export these names:

```ts
export type C20IntegrationFixture
export type C20IntegrationFixtureInput
export function assertC20IntegrationFixtureTarget(...): void
export async function seedC20IntegrationFixture(...): Promise<C20IntegrationFixture>
```

The module may export narrow supporting types used by those signatures, but must
not export or register a process-global fixture/backend singleton.

`C20IntegrationFixtureInput` must carry explicit caller-owned dependencies rather
than reading production credentials implicitly. At minimum it must contain:

```ts
{
  prisma: PrismaClient;
  databaseUrl: string;
  redisUrl: string;
  redisNamespace: string;
  environment: 'TEST';
  now?: Date;
}
```

The seed helper may construct a short-lived Redis client from `redisUrl`; it must
close it before returning. It must not overwrite `DATABASE_URL`/`REDIS_URL` or mutate
process-global backend state.

### R2. Destructive-target guards

`assertC20IntegrationFixtureTarget` is mandatory and must run before any seed/reset
write.

It must fail closed unless all of the following are true:

1. `environment === 'TEST'`;
2. `DEPLOYMENT_ENVIRONMENT_NAME`, when present, is exactly `test` case-insensitively;
3. the PostgreSQL URL parses successfully and its database name matches
   `^arch020_c20_[a-z0-9_]+$`;
4. `redisNamespace` matches `^arch020:c20:[a-z0-9_-]+$`;
5. neither URL is empty; when `COMMERCE_TEST_DATABASE_URL` /
   `COMMERCE_TEST_REDIS_URL` are present, the supplied URLs must equal those exact
   test variables rather than `DATABASE_URL` / `REDIS_URL`.

Use stable error codes/messages in the focused test:

- `C20_FIXTURE_UNSAFE_ENVIRONMENT`
- `C20_FIXTURE_UNSAFE_DATABASE_TARGET`
- `C20_FIXTURE_UNSAFE_REDIS_NAMESPACE`

Do not silently downgrade a guard failure into a skipped test.

### R3. PostgreSQL reset semantics

Because ARCH-020 published rows are immutable, the reset implementation must use a
**dedicated disposable database** whose name passed R2. It must not delete immutable
publication rows one by one.

Create exactly:

`scripts/reset-c20-integration-fixture.mjs`

The script must:

1. require `COMMERCE_TEST_DATABASE_URL`, `COMMERCE_TEST_REDIS_URL` and
   `COMMERCE_C20_REDIS_NAMESPACE`;
2. run the same R2 target guards before any destructive action;
3. invoke Prisma against **only** `COMMERCE_TEST_DATABASE_URL` to reset/reapply the
   existing migrations for `database/prisma/schema.prisma`;
4. connect to **only** `COMMERCE_TEST_REDIS_URL` and delete keys matching exactly
   `${COMMERCE_C20_REDIS_NAMESPACE}:*` using bounded SCAN batches;
5. never call `FLUSHALL` or `FLUSHDB`;
6. exit non-zero on any failed guard, migration reset or Redis cleanup;
7. print no credentials or full connection URLs.

Add this exact package script name:

```json
"c20-fixture:reset": "node scripts/reset-c20-integration-fixture.mjs"
```

### R4. Seed graph — exact minimum durable fixture

`seedC20IntegrationFixture` must create one committed graph in the supplied fresh
C20 database and return every identifier; consumers must never infer identity from
names or parse IDs.

Seed exactly these logical records:

**Staff**
- one active `ADMIN` PlatformAdmin;
- one active `SUPER_ADMIN` PlatformAdmin.

**Merchants/conversations**
- shop A: ACTIVE Shop -> DETECTED CheckoutRecovery -> RECOVERY Conversation;
- shop B: ACTIVE Shop -> DETECTED CheckoutRecovery -> RECOVERY Conversation;
- each recovery uses its own unique checkout token;
- each conversation has `inboundVersion >= 1` and is recovery-linked, never standalone.

**Feature/plan selection**
- one active Feature with `activationMode = MERCHANT_OPT_IN`;
- one active BillingPlan;
- one enabled BillingPlanFeature linking that plan to the Feature;
- ACTIVE Subscriptions for both shops to that plan;
- shop A feature preference enabled;
- shop B feature preference disabled.

This gives consumers one authoritative eligible feature shop and one authoritative
preference-excluded shop without inventing feature IDs.

Use these exact non-ID fixture values so consumers do not invent their own variants:

```text
ADMIN email:                 c20-admin@example.test
SUPER_ADMIN email:           c20-super-admin@example.test
eligible shop domain:        c20-eligible.example.test
excluded shop domain:        c20-excluded.example.test
eligible checkout token:     c20-checkout-eligible
excluded checkout token:     c20-checkout-excluded
Feature.key:                 c20_fixture_feature
Feature.activationMode:      MERCHANT_OPT_IN
BillingPlan.shopifyPlanHandle: c20_fixture_plan
BillingPlan.name:            C20 Fixture Plan
BillingPlan.kind:            PAID_METERED
CommerceTool.name:           c20_fixture_lookup
definitionVersion:           1.0.0
BASE capability key:         conversation_core
FEATURE capability key:      fixture_feature
contractVersion:             commerce.v1
runnerCompatibility:         ^1.0.0
pointer environment:         TEST
operation reason:            ARCH-020 C20 integration fixture
```

The tool definition must be the following current-schema value, parsed through
`CommerceToolDefinitionSchema` before publication:

```ts
{
  name: 'c20_fixture_lookup',
  definitionVersion: '1.0.0',
  description: 'C20 fixture product lookup.',
  inputSchema: {
    type: 'object',
    properties: { query: { type: 'string', maxLength: 128 } },
    required: ['query'],
    additionalProperties: false,
  },
  execution: {
    kind: 'POLICY_OPERATION',
    operation: 'shopify.searchProducts',
    operationVersion: '1.0.0',
    arguments: { query: { input: 'query' } },
  },
  responseTemplate: {
    kind: 'text',
    text: '{{result.value}}',
    unavailable: 'Fixture product data is unavailable.',
  },
}
```

The response contract for both seeded releases is exactly:

```ts
{
  version: 'response.v1',
  instructions: 'Answer only from C20 fixture facts.',
  detailsSchema: { type: 'object', properties: {}, additionalProperties: false },
}
```

Use these exact published capability drafts:

```text
conversation_core prompt: Use the C20 fixture lookup for core conversation facts.
fixture_feature prompt:   Use the C20 fixture lookup when the fixture feature is eligible.
configuration:            {}
toolBindings:             the exact published c20_fixture_lookup toolId/toolRevisionId
```

Release 1 contains `conversation_core` only and is returned as `releases.inactive`.
Release 2 contains `conversation_core` at position 0 and `fixture_feature` at position
1 and is activated in TEST as `releases.active`. The original shop-A grant is pinned
to Release 2 and selects exactly:

```json
["conversation_core", "fixture_feature"]
```

Its `grantedTools` contains exactly one tool entry derived from the persisted release
union. With the fixed keys above the `capabilityKeys` array is exactly:

```json
["conversation_core", "fixture_feature"]
```

Do not hard-code generated IDs into that grant; read the persisted IDs/names/version
and build the exact trigger-required value from them.

Use these exact lifecycle operation IDs on a freshly reset target and return them in
`operationIds`:

```text
c20-fixture:create-tool
c20-fixture:create-tool-draft
c20-fixture:publish-tool
c20-fixture:create-base-capability
c20-fixture:create-base-draft
c20-fixture:publish-base
c20-fixture:create-feature-capability
c20-fixture:create-feature-draft
c20-fixture:publish-feature
c20-fixture:create-release-1
c20-fixture:create-release-2
c20-fixture:activate-release-2
```

**Published Commerce data**
- one enabled CommerceTool;
- one exact PUBLISHED CommerceToolRevision with a valid
  `CommerceToolDefinitionSchema` definition;
- one BASE capability whose key is exactly `conversation_core`;
- one FEATURE capability linked to the seeded Feature;
- one PUBLISHED revision for each capability;
- both capability revisions bind the exact published tool revision when a tool
  binding is required by the consumer fixture;
- two non-empty CommerceRelease rows with valid `response.v1` contracts;
- one TEST CommerceReleasePointer pointing at the designated active release;
- one original CommerceConversationGrant for shop A's conversation, with
  `initialInboundVersion <= conversation.inboundVersion`, selected keys containing
  `conversation_core`, and `grantedTools` equal to the database-enforced complete
  tool union for those selected release capabilities.

Use the accepted `CommerceLifecycle` + real `PrismaPublicationStorage` for
publication-owned tool/capability/revision/release/pointer writes. Do not hand-insert
published revisions, hashes, release members or audit rows and do not disable their
relational guards. Direct Prisma writes are allowed for fixture-only staff/shop/
billing/recovery/conversation rows and the original conversation grant after its
release graph exists.

Use `CommerceToolDefinitionSchema.parse(...)` for the fixture definition and
`CommerceResponseContractSchema.parse(...)` for the release response contract.
Do not copy stale JSON that bypasses current schemas.

### R5. Returned typed object

`C20IntegrationFixture` must be a readonly object that returns, at minimum:

```ts
{
  environment: 'TEST';
  admins: {
    admin: { id: string; role: 'ADMIN'; email: string };
    superAdmin: { id: string; role: 'SUPER_ADMIN'; email: string };
  };
  shops: {
    eligible: { shopId: string; recoveryId: string; conversationId: string };
    excluded: { shopId: string; recoveryId: string; conversationId: string };
  };
  billing: {
    featureId: string;
    featureKey: string;
    planId: string;
  };
  tool: {
    toolId: string;
    toolRevisionId: string;
    name: string;
    definitionVersion: string;
  };
  capabilities: {
    base: { capabilityId: string; revisionId: string; key: 'conversation_core' };
    feature: { capabilityId: string; revisionId: string; key: string; featureId: string };
  };
  releases: {
    active: { releaseId: string };
    inactive: { releaseId: string };
  };
  activePointer: {
    environment: 'TEST';
    releaseId: string;
    editVersion: number;
  };
  originalGrant: {
    grantId: string;
    shopId: string;
    conversationId: string;
    releaseId: string;
  };
  operationIds: Readonly<Record<string, string>>;
}
```

Additional fields are allowed only when they are actual persisted identifiers needed
by both consumer suites. Do not return secret/token material.

Every publication mutation used by the seed must have an explicit unique operation ID
and non-empty reason. Return those IDs under `operationIds`; do not derive them later
from business IDs.

### R6. Redis namespace

The seed helper must establish only the task-owned Redis namespace needed by
consumer integration. Redis keys created by this helper or the focused proof must be
under:

`${redisNamespace}:*`

No generic `commerce:*` cleanup is permitted. Reset must demonstrate that a sentinel
key outside this prefix survives.

### R7. Consumer contract

Update `docs/commerce-backend-integration.md` with a section titled exactly:

`## C20 isolated integration fixture`

Document:

- the module path and four required exports from R1;
- the disposable PostgreSQL naming rule;
- the Redis namespace rule;
- the exact reset command;
- the fixture graph from R4;
- which identifiers are returned;
- that COMMERCE-018 and COMMERCE-019 must use this helper rather than local copies;
- that only external query/policy/model transports may be substituted in their tests;
- that application services (`CommerceLifecycle`, Prisma storage, saved/inspection
  reads, Studio/Preview adapters) must remain real.

## Work Items

- [ ] Add `src/commerce/integration/backend/c20-test-fixture.ts` with the exact R1 exports.
- [ ] Implement R2 fail-closed target guards before any write.
- [ ] Add guarded disposable PostgreSQL + prefix-scoped Redis reset script from R3.
- [ ] Seed the exact R4 graph using real publication lifecycle/storage for published Commerce rows.
- [ ] Return the typed R5 identifiers and explicit operation IDs.
- [ ] Prove R6 prefix isolation with an outside-prefix sentinel.
- [ ] Add `tests/c20-integration-fixture.test.ts`.
- [ ] Add the exact `c20-fixture:reset` and `test:arch020-c20-integration-fixture` package scripts.
- [ ] Document the R7 consumer contract in `docs/commerce-backend-integration.md`.

## Interfaces / Contracts

Consumes accepted COMMERCE-013 production building blocks only:

- `src/commerce/integration/backend.ts:createCommerceBackend` / accepted backend types;
- `src/commerce/integration/backend/publication-storage.ts:PrismaPublicationStorage`;
- `src/commerce/publication/lifecycle.ts:CommerceLifecycle`;
- accepted Commerce schemas/hash/validation functions already used by the lifecycle;
- canonical Prisma models through the nested `database/` submodule.

Produces only the test fixture module described in R1 and the reset command described
in R3. This is **not** a Shared cross-service runtime contract and is not published as
an npm package.

## Dependencies

- ARCH-020-COMMERCE-013 — Complete / architect accepted.

No other dependency may be added without returning to `moda_architect`.

## Enables

- ARCH-020-COMMERCE-018
- ARCH-020-COMMERCE-019

Neither consumer becomes Ready merely because source code exists; this task must be
architect-accepted Complete first.

## Acceptance Criteria

- [ ] F01: unsafe environment, database-name and Redis-prefix inputs fail before any destructive operation.
- [ ] F02: `c20-fixture:reset` resets only the dedicated C20 PostgreSQL database and the exact Redis prefix; an outside-prefix Redis sentinel survives.
- [ ] F03: one seed produces exactly two active admins, two active recovery-linked shops/conversations, one plan/Feature selection with eligible/excluded preferences, published tool/capability/release state, one TEST active pointer and one original valid grant.
- [ ] F04: all returned IDs point to the exact persisted rows; no consumer-relevant identity is derived from fixture names or parsed IDs.
- [ ] F05: tool/capability/release publication is performed through real `CommerceLifecycle`/`PrismaPublicationStorage`; existing hashes, immutability triggers and grant relational guards remain enabled.
- [ ] F06: reset -> seed -> inspect -> reset -> seed succeeds twice against the same disposable targets without duplicate-key leakage or stale Redis state.
- [ ] F07: no production source/application route imports `c20-test-fixture.ts`; no application startup seed or global fixture registry is introduced.
- [ ] F08: the documented consumer API is sufficient for 018/019 to import directly without copying fixture construction.

## Validation

Add exactly:

```json
"test:arch020-c20-integration-fixture": "vitest run tests/c20-integration-fixture.test.ts"
```

The focused test must use **real PostgreSQL and real Redis**. It must fail, not skip,
when either required test URL is absent.

Required execution sequence for the repository agent:

```bash
# 1. The developer/test harness supplies disposable targets.
export COMMERCE_TEST_DATABASE_URL='postgresql://.../arch020_c20_<unique_name>'
export COMMERCE_TEST_REDIS_URL='redis://...'
export COMMERCE_C20_REDIS_NAMESPACE='arch020:c20:<unique_name>'
export DEPLOYMENT_ENVIRONMENT_NAME='test'

# 2. Reset only those targets.
npm run c20-fixture:reset

# 3. Run the real fixture proof.
npm run test:arch020-c20-integration-fixture

# 4. Repository checks.
npm run typecheck
npm run lint -- --quiet
npm run build
git diff --check
```

The focused test must prove F01-F08 with actual database reads and Redis reads. Do not
mock `PrismaClient`, `PrismaPublicationStorage`, `CommerceLifecycle` or Redis. External
query/policy/model transports may be deterministic in-process fixtures because C20
explicitly permits substitution of external providers, not Moda application services.

If disposable PostgreSQL or Redis is unavailable, record the exact command and failure
and return the task `blocked`; do not mark F02/F03/F05/F06 or the focused validation
complete.

## Stop Condition

After F01-F08 and every required validation command above passes, update only this
task's execution metadata, Work Items, Acceptance Criteria, Validation and Completion
Report; set status to `review`; clear the claim according to the normal workflow;
push both mirrored task branches; return control to `moda_architect`; **STOP**.

Do not start COMMERCE-018 or COMMERCE-019. Do not modify their task files, indexes,
architecture status or dependency frontier from the repository-agent execution.

## Implementation Notes

Use the prepared launcher packet and dedicated mirrored worktrees. The fixture module
is test-only even though it lives under the backend integration directory. Keep its
imports out of production entrypoints. Prefer existing accepted schema validators and
publication commands over copied JSON or raw publication-table inserts.

No migration is authorized. If the existing schema makes the exact R4 graph impossible
without a migration or production semantic change, stop and report the precise
constraint to `moda_architect`.

## Completion Report

### Status

Blocked: implementation is present, but the required disposable PostgreSQL and
Redis targets were not supplied in this execution environment.

### Files Changed

- `src/commerce/integration/backend/c20-test-fixture.ts`
- `scripts/reset-c20-integration-fixture.mjs`
- `tests/c20-integration-fixture.test.ts`
- `package.json`
- `docs/commerce-backend-integration.md`

### Work Completed

Implemented the guarded C20 fixture API, lifecycle-backed publication graph,
prefix-scoped Redis seed/reset boundary, focused real-client proof, package
scripts, and consumer documentation. No production route or startup registration
was added.

### Validation Results

- `npm ci` passed.
- `npm run prisma:generate` passed.
- `npm run typecheck` passed.
- `npm run lint -- --quiet` passed.
- `npm run build` passed.
- `node --check scripts/reset-c20-integration-fixture.mjs` passed.
- `git diff --check` passed.
- `npm run c20-fixture:reset` failed closed with `C20_FIXTURE_UNSAFE_ENVIRONMENT:
  C20 test targets are required` because no disposable URLs were supplied.
- `npm run test:arch020-c20-integration-fixture` failed before tests with
  `C20_FIXTURE_UNSAFE_ENVIRONMENT: disposable PostgreSQL, Redis, and namespace
  variables are required` for the same reason.

### Deviations

F02, F03, F05, and F06 remain unverified because the required real PostgreSQL and
Redis targets were unavailable. The task is intentionally blocked rather than
claiming integration evidence.

### Assumptions

The developer/test harness will provide a fresh PostgreSQL database named
`arch020_c20_<unique_name>`, a Redis URL, the matching C20 namespace, and
`DEPLOYMENT_ENVIRONMENT_NAME=test` for the remaining validation.

### Unresolved Issues

Run the reset twice and execute the focused proof against supplied disposable
targets, then review persisted graph, immutability, grant, and Redis sentinel
evidence.

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Reviewed implementation `f928cffea3b059bf0f4b74958062fe3f92e9d126` and parent
report `a39f7f713a060857f141e2d486e7401c25ce9db0` against the canonical C20
contract. The bounded file scope, exact exports, fail-closed target guards,
dedicated PostgreSQL reset command, prefix-scoped Redis scan, lifecycle-backed
publication calls, package scripts, and consumer documentation are aligned with
the task. The supplied static checks passed, and the required real-client
commands correctly failed closed when their target variables were absent.

The implementation is not yet conformant for acceptance:

- `src/commerce/integration/backend/c20-test-fixture.ts` constructs
  `selectedCapabilityKeys` and `grantedTools` with hardcoded values instead of
  deriving the grant's complete tool union and capability keys from the
  persisted Release 2 graph as required by R4/F03/F05.
- `tests/c20-integration-fixture.test.ts` does not prove the required C20
  contract. It omits subscription and preference assertions, release member
  ordering/response-contract assertions, persisted grant tool-union and
  lifecycle-audit/immutability assertions, and the second reset/seed cycle.
- The focused test writes an outside-prefix sentinel but never runs the reset
  command afterward, so it cannot establish F02 or the required sentinel
  survival evidence.

The missing disposable targets explain why F02, F03, F05 and F06 could not be
executed, but they do not explain the source-level deficiencies above. The task
therefore returns to `ready` with its claim cleared; it is not accepted or
eligible to unblock COMMERCE-018 or COMMERCE-019.

### Reviewed Files

- `src/commerce/integration/backend/c20-test-fixture.ts`
- `scripts/reset-c20-integration-fixture.mjs`
- `tests/c20-integration-fixture.test.ts`
- `package.json`
- `docs/commerce-backend-integration.md`
- `docs/architecture/ARCH-020-implementation-contracts.md`
- `docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md`

### Validation Reviewed

- Reviewed the submitted `prisma:generate`, `typecheck`, `lint -- --quiet`,
  `build`, `node --check`, and `git diff --check` results.
- Confirmed both required real-client commands failed closed with the documented
  missing-target guard.
- Confirmed dedicated parent and implementation task worktrees are clean,
  isolated, on matching `task/ARCH-020-COMMERCE-035` branches, and match the
  supplied remote commits.

### Architecture Conformance

Partial. Repository ownership and the bounded C20 fixture boundary conform, but
the grant derivation and focused real-client proof do not yet satisfy the
ARCH-020 C20 acceptance contract. No production route, startup seed, migration,
or cross-service contract change was introduced.

### Follow-up

On the same task branch and attempt, correct grant construction to derive the
persisted Release 2 member/tool union, expand the focused proof to cover the
omitted F03/F05 assertions, and execute the required reset -> seed/inspect ->
reset -> seed cycle with a sentinel outside the deleted prefix. Once disposable
targets are supplied, run `npm run c20-fixture:reset`, then
`npm run test:arch020-c20-integration-fixture`, then the repository checks in the
Validation section. Return the task to review only after the source corrections
and F01-F08 evidence pass. Do not start COMMERCE-018 or COMMERCE-019.

## Architect Review — Attempt 1 follow-up — 2026-09-22

### Review Status

Changes Requested

### Review Notes

Reviewed the latest submitted source after implementation commits `f928cff` and
`5ae2695` against the existing Attempt 1 rework contract.

The production fixture implementation is now accepted in substance for the
previous source-level defects:

- `selectedCapabilityKeys` is derived from the persisted Release 2 member graph;
- `grantedTools` is derived from the persisted tool bindings/tool revisions rather
  than hard-coded generated identifiers;
- subscription and merchant preference rows are asserted;
- active Release 2 member positions are asserted;
- the reset script is invoked inside the focused proof;
- an outside-prefix Redis sentinel is asserted after reset;
- the second seed is executed after that reset.

Do not redesign those working paths.

Two proof-source corrections from the existing Architect Review remain unresolved.
They are not new scope and they are not a request for exhaustive testing.

#### A1-R1 — prove the exact persisted release graph and response contract

File requiring correction:

`tests/c20-integration-fixture.test.ts`

During the first seed/inspect phase, load both fixture releases from PostgreSQL with
their `CommerceReleaseCapability` rows ordered by `position`.

Assert the inactive release is exactly:

```text
releaseId: fixture.releases.inactive.releaseId
runnerCompatibility: ^1.0.0
contractVersion: commerce.v1
responseContract:
  version: response.v1
  instructions: Answer only from C20 fixture facts.
  detailsSchema:
    type: object
    properties: {}
    additionalProperties: false
members:
  position 0:
    capabilityId:         fixture.capabilities.base.capabilityId
    capabilityRevisionId: fixture.capabilities.base.revisionId
```

Assert the active release is exactly:

```text
releaseId: fixture.releases.active.releaseId
runnerCompatibility: ^1.0.0
contractVersion: commerce.v1
responseContract:
  version: response.v1
  instructions: Answer only from C20 fixture facts.
  detailsSchema:
    type: object
    properties: {}
    additionalProperties: false
members:
  position 0:
    capabilityId:         fixture.capabilities.base.capabilityId
    capabilityRevisionId: fixture.capabilities.base.revisionId

  position 1:
    capabilityId:         fixture.capabilities.feature.capabilityId
    capabilityRevisionId: fixture.capabilities.feature.revisionId
```

Do not prove only `[0, 1]`; prove the exact persisted member identities and order.

Also assert that both persisted releases have a non-empty
`responseContractHash`, and that the published tool/capability revisions inspected
by the test have non-empty `contentHash` values. Do not reimplement the hash
algorithm in this test.

#### A1-R2 — prove lifecycle audit, immutable published state and the grant relational guard

File requiring correction:

`tests/c20-integration-fixture.test.ts`

After the first seed succeeds, compute:

```ts
const expectedOperationIds = Object.values(fixture.operationIds).sort();
```

Read `CommerceAuditEvent` rows whose IDs are in that set and assert:

```text
audit row IDs, sorted == expectedOperationIds
audit row count          == expectedOperationIds.length
every reason             == "ARCH-020 C20 integration fixture"
every actorAdminId       is one of:
  fixture.admins.admin.id
  fixture.admins.superAdmin.id
```

This proves each fixture publication command went through the real lifecycle/audit
boundary exactly once.

Then, against the same real PostgreSQL target, prove the existing database guards
remain active. All of the following operations must reject and leave the persisted
fixture unchanged:

1. update the active `CommerceRelease.description`;
   expected database error contains `ARCH020 immutable CommerceRelease`;

2. update the published feature `CommerceCapabilityRevision.promptTemplate`;
   expected database error contains `ARCH020 published revision immutable`;

3. update the audit row whose ID is
   `fixture.operationIds.createRelease2`;
   expected database error contains `ARCH020 immutable CommerceAuditEvent`;

4. attempt to create a grant for
   `fixture.shops.excluded.conversationId` / `fixture.shops.excluded.shopId`
   on the active release using:

```text
initialInboundVersion: 1
selectedCapabilityKeys: ["conversation_core"]
grantedTools: []
runnerVersion: "1.0.0"
```

   expected database error contains
   `ARCH020 grant must equal complete tool union`.

After the rejected mutations assert:

```text
CommerceConversationGrant count == 1
the original grant still has the exact selectedCapabilityKeys/grantedTools already asserted
the lifecycle audit ID set is unchanged
```

Do not disable triggers, alter transaction isolation, mock Prisma, or replace these
checks with source-regex assertions.

#### A1-R3 — infrastructure outcome is deterministic

The real PostgreSQL/Redis validation remains mandatory and is separate from A1-R1
and A1-R2.

After implementing only A1-R1/A1-R2, execute exactly:

```bash
npm run c20-fixture:reset
npm run test:arch020-c20-integration-fixture
npm run typecheck
npm run lint -- --quiet
npm run build
git diff --check
```

with all four required environment values present:

```text
COMMERCE_TEST_DATABASE_URL=postgresql://.../arch020_c20_<unique_name>
COMMERCE_TEST_REDIS_URL=redis://...
COMMERCE_C20_REDIS_NAMESPACE=arch020:c20:<unique_name>
DEPLOYMENT_ENVIRONMENT_NAME=test
```

If the disposable PostgreSQL/Redis values are still unavailable, do **not** return
the task to `review` and do **not** leave it `ready`. After committing the proof-source
corrections, set:

```yaml
status: blocked
executor: null
claimed_at: null
attempt: <current claimed attempt>
```

and record the exact missing environment values/failed commands in the Completion
Report. This follows the task's existing Validation contract.

When the targets are later supplied, `moda_architect` will return the blocked task
to `ready` for validation-only execution.

### Reviewed Files

- `src/commerce/integration/backend/c20-test-fixture.ts`
- `tests/c20-integration-fixture.test.ts`
- `scripts/reset-c20-integration-fixture.mjs`
- `docs/commerce-backend-integration.md`
- `docs/architecture/ARCH-020-implementation-contracts.md`
- `database/prisma/migrations/20260920182429_arch020_commerce_capability_releases/migration.sql`

### Validation Reviewed

Submitted evidence records successful Prisma generation, typecheck, lint, build,
reset-script syntax and diff checks. The required live reset/fixture commands remain
unexecuted because the disposable target variables were not supplied.

The review environment archive does not contain installed repository dependencies,
so the architect did not manufacture a second dependency-backed run. Static
inspection confirms the latest fixture source contains the persisted grant derivation
and reset/sentinel corrections described above.

### Architecture Conformance

Partial.

The fixture production boundary now conforms in substance, but the focused proof still
does not establish all previously requested C20 persisted-release and F05
audit/immutability/relational-guard evidence. Real PostgreSQL/Redis execution also
remains mandatory before acceptance.

`ARCH-020-COMMERCE-035` is therefore not Complete and does not yet satisfy its
producer gate for COMMERCE-018/019 C20 integration acceptance.

### Follow-up

On the next authorized claim, change only
`tests/c20-integration-fixture.test.ts` for A1-R1/A1-R2 unless an actual failing real
integration run proves another task-owned correction is necessary.

Do not modify the production fixture implementation merely to manufacture test
evidence. Do not start COMMERCE-018 or COMMERCE-019 from this task.

If A1-R1/A1-R2 are committed but disposable targets are unavailable, return this same
task `blocked` exactly as A1-R3 specifies and STOP.
