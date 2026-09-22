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
status: ready
priority: 130
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-013
enables:
  - ARCH-020-COMMERCE-018
  - ARCH-020-COMMERCE-019
created: 2026-09-21
updated: 2026-09-21
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

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
