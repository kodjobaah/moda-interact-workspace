---
id: ARCH-023-COMMERCE-001
architecture_id: ARCH-023
title: Implement Merchant Knowledge lookup policy operation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 60
executor: copilot
claimed_at: 2026-09-30T12:56:59Z
attempt: 2
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
  - ARCH-021-COMMERCE-096
enables:
  - ARCH-023-COMMERCE-002
created: 2026-09-29
updated: 2026-09-30
---

# Implement Merchant Knowledge lookup policy operation

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement and register the Commerce-owned:

```text
merchantKnowledge.lookup@1.0.0
```

policy operation using the canonical ARCH-021 Policy Operation registry/descriptor contract.

The operation must independently enforce the authenticated shop's current Merchant Knowledge commercial entitlement, embed the bounded semantic query with the same configured multilingual embedding provenance used by Background, perform exact tenant-scoped pgvector cosine ranking, and return the exact ARCH-023 C5 envelope.

This task does not create or publish the `merchant_knowledge_lookup` Commerce Tool identity. COMMERCE-002 owns bootstrap/publication.

## Context

ARCH-021-COMMERCE-096 makes each Policy Operation registration the single owner of:

```text
operation + version
input validator
output validator
Studio authoring descriptor
runtime adapter
```

Do not restore executor-local `POLICY_SCHEMAS` ownership or create an ARCH-023-only registry.

Merchant Knowledge Tool association and Merchant Knowledge commercial entitlement are separate facts.

A Tool revision may later be bound to more than one Capability revision. Therefore `merchantKnowledge.lookup` itself MUST fail closed unless the current shop has a valid current `merchant_knowledge` BillingPlanFeature entitlement.

## Scope

Primary authorized implementation surface:

```text
database                         # gitlink update only
package.json
package-lock.json

lib/server/config.ts

src/commerce/merchant-knowledge/contracts.ts
src/commerce/merchant-knowledge/embedding.ts
src/commerce/merchant-knowledge/entitlement.ts
src/commerce/merchant-knowledge/retrieval.ts
src/commerce/merchant-knowledge/operation.ts

src/commerce/integration/backend.ts
src/commerce/tool-definition/contracts.ts       # only canonical PolicyOperation identifier extension if still required after C096
src/commerce/execution/renderer.ts              # only bounded item-limit integration if still operation-specific after C096

tests/merchant-knowledge-contract.test.ts
tests/merchant-knowledge-entitlement.test.ts
tests/merchant-knowledge-embedding.test.ts
tests/merchant-knowledge-retrieval.test.ts
tests/merchant-knowledge-policy.test.ts
tests/merchant-knowledge-policy-postgres.test.ts
```

Use the accepted C096 registry files/names if they differ after implementation. Do not recreate the pre-C096 registry shape.

## Out of Scope

- Commerce Tool/Capability/release bootstrap.
- Commerce Studio generic `POLICY_OPERATION` UI.
- Merchant Knowledge ingestion.
- R2.
- source CRUD.
- plan authoring/materialisation.
- Platform/Shop prompt composition.
- Redis vector search.
- ANN/HNSW/IVFFlat.
- new public/private HTTP endpoint.

## Requirements

### R1 — adopt accepted dependencies

Before implementation:

1. advance `database` gitlink to accepted/merged `ARCH-023-DATABASE-001`;
2. do not edit schema/migrations inside the Commerce database submodule;
3. adopt exactly `@modainteract/moda-interact-shared@1.0.1`, the Architect-Accepted revision published by `ARCH-023-SHARED-002`; do not substitute a range, `latest`, workspace link or later release without architect reconciliation;
4. work on the accepted implementation of `ARCH-021-COMMERCE-096`;
5. regenerate Prisma Client.

If C096 is not Complete/accepted, STOP.

### R2 — canonical operation identity

Register exactly:

```text
operation        = merchantKnowledge.lookup
operationVersion = 1.0.0
displayName      = Merchant Knowledge Lookup
description      = Search the current shop's entitled Merchant Knowledge for factual reference passages.
```

If the accepted C096 base still requires a closed `PolicyOperation` identifier union, add `merchantKnowledge.lookup` exactly once to that canonical identifier source.

Do not add another allow-list under Merchant Knowledge code.

### R3 — exact runtime input validator

The mapped policy-operation argument object is:

```ts
{
  query: string;
  purposes?: MerchantKnowledgePurposeKey[];
}
```

Validate:

```text
query:
  trim for validation
  1..1000 Unicode code points
  runtime value passed to embedding = trimmed query

purposes:
  optional
  array
  max 7
  unique
  every item one Shared MerchantKnowledgePurposeKey
```

Reject unknown fields.

Do not accept:

```text
shopId
shopDomain
languageTag
planId
feature configuration
embedding model/version
limit/topK
R2 information
```

from mapped Tool input.

### R4 — exact authoring arguments schema

C096 `authoring.argumentsSchema` must describe the mapped operation arguments:

```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "minLength": 1,
      "maxLength": 1000
    },
    "purposes": {
      "type": "array",
      "maxItems": 7,
      "items": {
        "type": "string",
        "enum": [
          "COMPANY_INFORMATION",
          "CUSTOMER_SUPPORT",
          "POLICIES",
          "FAQ",
          "PRODUCT_INFORMATION",
          "SHIPPING_AND_DELIVERY",
          "PRICING"
        ]
      }
    }
  },
  "required": ["query"],
  "additionalProperties": false
}
```

If the Shared `SubsetSchema` cannot represent JSON Schema `uniqueItems`, runtime R3 remains authoritative for uniqueness; do not weaken R3.

### R5 — exact successful result validator

Successful `CommerceToolResult.data` must be exactly:

```ts
{
  trust: "UNTRUSTED_REFERENCE";
  matches: Array<{
    sourceId: string;
    sourceRevisionId: string;
    sourceName: string;
    purpose: MerchantKnowledgePurposeKey;
    dataFormat: MerchantKnowledgeDataFormatKey;
    languageTag: ModaSupportedLanguageTag;
    sourceUrl?: string;
    chunkOrdinal: number;
    content: string;
  }>;
}
```

Validation:

```text
trust exact literal UNTRUSTED_REFERENCE
matches max 5
all ids/names non-empty bounded strings
sourceName max 160
sourceUrl max 2048 and present only for WEB_PAGE
chunkOrdinal non-negative integer
content non-empty max 4800 code units after persisted chunk read
```

No additional properties.

The operation output validator is the C096 registration `outputValidator`.

### R6 — exact C096 authoring result schema

The browser-safe `authoring.resultSchema` must describe the same successful data shape within the existing CommerceResultSchema expressiveness:

```text
object:
  trust       string maxLength 32
  matches     array maxItems 5
    object:
      sourceId           string maxLength 128
      sourceRevisionId   string maxLength 128
      sourceName         string maxLength 160
      purpose            string maxLength 64
      dataFormat         string maxLength 32
      languageTag        string maxLength 16
      sourceUrl          string maxLength 2048   # optional
      chunkOrdinal       integer
      content            string maxLength 4800
```

Required match fields are every field except `sourceUrl`.

The runtime Zod validator, not this lossy authoring schema, enforces enum/literal semantics.

### R7 — embedding environment contract

Extend server configuration with exactly:

```text
EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
EMBEDDING_INDEX_VERSION
EMBEDDING_API_KEY
```

For ARCH-023 v1:

```text
EMBEDDING_PROVIDER = openai
```

Any other provider rejects configuration as:

```text
UNSUPPORTED_EMBEDDING_PROVIDER
```

Validation:

```text
EMBEDDING_MODEL trimmed non-empty <= 255
EMBEDDING_DIMENSIONS positive safe integer
EMBEDDING_INDEX_VERSION trimmed non-empty <= 64
EMBEDDING_API_KEY trimmed non-empty and never logged
```

Commerce and Background intentionally use the same variable names/provenance.

### R8 — OpenAI query embedding adapter

Use server-side `fetch` to:

```text
POST https://api.openai.com/v1/embeddings
```

Request:

```json
{
  "model": "<EMBEDDING_MODEL>",
  "input": "<trimmed query>",
  "dimensions": <EMBEDDING_DIMENSIONS>
}
```

Headers:

```text
Authorization: Bearer <EMBEDDING_API_KEY>
Content-Type: application/json
```

Deadline:

```text
10 seconds
```

No retry inside the adapter; the normal Tool/runner retry boundary remains authoritative.

Require response:

```text
HTTP 200
exactly one data item
embedding array length == EMBEDDING_DIMENSIONS
every value finite
```

Map:

```text
429 / 500 / 502 / 503 / 504 / timeout -> UNAVAILABLE retryable=true
other non-200 / malformed response      -> UNAVAILABLE retryable=false
```

Never log query text, API key or vector.

### R9 — current Merchant Knowledge entitlement is operation-level authority

Resolve `shopId` only from:

```text
AuthorizedToolCall.context.turn.shopId
```

Never from agent input.

For that shop require:

1. current `Subscription`;
2. `status IN (ACTIVE, TRIALING)`;
3. current `planId`/`plan`;
4. enabled `BillingPlanFeature`;
5. related `Feature.key = merchant_knowledge`;
6. related `Feature.active = true`;
7. parse `BillingPlanFeature.configuration` with Shared C2.

Ignore:

```text
pendingPlanId
pendingShopifyPlanHandle
pendingEffectiveAt
ShopFeaturePreference
capability key that happened to grant this Tool
```

Outcomes:

```text
no current merchant_knowledge entitlement -> Commerce Tool ERROR code DENIED, retryable=false
malformed current C2 configuration         -> ERROR code UNAVAILABLE, retryable=false
```

This rule applies even if another eligible Capability revision grants the same Tool revision.

### R10 — determine currently entitled source ids before vector ranking

Load source rows for the trusted shop including:

```text
Purpose.key/active
DataFormat.key/active/inputKind
composite MerchantKnowledgePurposeDataFormat existence
position
id
```

Candidate pair is globally supported only when:

```text
Purpose.active = true
DataFormat.active = true
composite pair exists
```

Then:

1. filter to exact pairs in current C2 `allowedSourceTypes`;
2. order:
   ```text
   position ASC, id ASC
   ```
3. take first:
   ```text
   maxKnowledgeSources
   ```
4. if optional `purposes` supplied, filter that already-entitled set to those Purpose keys.

Source language is NOT a filter.

If candidate source set is empty:

```ts
return OK {
  trust: "UNTRUSTED_REFERENCE",
  matches: []
}
```

without calling embedding provider.

### R11 — exact pgvector query boundary

After embedding, execute one parameterized PostgreSQL query over only R10 source ids.

Join:

```text
MerchantKnowledgeChunk
-> MerchantKnowledgeSourceRevision
-> MerchantKnowledgeSource
-> MerchantKnowledgePurpose
-> MerchantKnowledgeDataFormat
```

Require:

```text
source.shopId = trusted shopId
source.id IN currently entitled source ids
revision.status = ACTIVE
chunk.embeddingProvider = EMBEDDING_PROVIDER
chunk.embeddingModel = EMBEDDING_MODEL
chunk.embeddingDimensions = EMBEDDING_DIMENSIONS
chunk.embeddingIndexVersion = EMBEDDING_INDEX_VERSION
```

Rank by exact cosine distance:

```text
chunk.embedding <=> queryEmbedding::vector ASC
source.position ASC
source.id ASC
chunk.ordinal ASC
```

Limit:

```text
5
```

Use parameterized Prisma raw SQL / `Prisma.sql` / `Prisma.join` according to repository conventions.

Never concatenate:

```text
shopId
source ids
purpose keys
query vector values
```

into an unparameterized SQL statement.

There is no ANN index.

### R12 — result shaping

For each row return:

```text
sourceId
sourceRevisionId
sourceName
purpose = Purpose.key
dataFormat = DataFormat.key
languageTag = source.languageTag
chunkOrdinal
content
```

For `WEB_PAGE` only:

```text
sourceUrl = activeRevision.resolvedUrl ?? activeRevision.requestedUrl
```

If neither URL exists for a WEB_PAGE active revision, omit the row as inconsistent and emit bounded diagnostic.

For CSV/XLSX:

```text
sourceUrl absent
```

Never return:

```text
distance
embedding
objectKey
uploadedAssetId
signed URL
plan limits
shopId
```

### R13 — Tool result envelope

Success uses normal Commerce result wrapper:

```ts
{
  contractVersion: "commerce.v1",
  status: "OK",
  data: {
    trust: "UNTRUSTED_REFERENCE",
    matches: [...]
  }
}
```

Do not use the trust marker as authorization.

### R14 — registration is canonical

Register through the accepted C096 registration object:

```text
operation
operationVersion
inputValidator
outputValidator
authoring descriptor
adapter
```

`createProductionPolicyRegistrations(...)` must include exactly one Merchant Knowledge registration.

Do not modify `DefinitionExecutor` to special-case Merchant Knowledge.

If the accepted C096 executor/renderer retains an operation-specific item-limit switch, add exactly:

```text
merchantKnowledge.lookup -> 5
```

and nothing broader.

### R15 — no capability-dependent authorization inside the adapter

The existing MCP grant/Tool authorization occurs before operation execution.

The operation may inspect trusted shop/current billing entitlement but MUST NOT require:

```text
eligibleCapabilityKeys contains merchant_knowledge
```

because the same published Tool revision may legitimately be bound to another Capability.

### R16 — exact operation tests

Tests must prove:

```text
query >1000 Unicode code points rejected
duplicate purposes rejected
shopId cannot be supplied through input
no current entitlement -> DENIED
pending future plan ignored
malformed C2 -> UNAVAILABLE
source-type filter occurs before maxKnowledgeSources
optional purposes narrows only already-entitled sources
source language never filters
empty candidates skip embedding and return []
cross-shop chunk never returned
non-ACTIVE revision never returned
embedding provenance mismatch excluded
distance ties deterministic
at most 5 matches
CSV/XLSX never expose sourceUrl/objectKey/asset id
WEB_PAGE uses resolvedUrl before requestedUrl
registration descriptor matches runtime operation
Tool granted through non-merchant_knowledge capability still rechecks commercial entitlement
```

PostgreSQL integration must use real pgvector on a disposable database and prove a known nearest-neighbour ordering.

## Work Items

- [x] Adopt Database/Shared/C096 accepted revisions.
- [x] Add exact embedding server configuration.
- [x] Implement C5 input/output contracts.
- [x] Implement current-plan entitlement resolver.
- [x] Implement query embedding adapter.
- [x] Implement exact pgvector retrieval.
- [x] Implement result shaping.
- [x] Register operation through canonical C096 registry.
- [x] Add unit + disposable PostgreSQL/pgvector tests.
- [x] Confirm no capability/Tool/release objects are created.

## Interfaces / Contracts

Consumes:

```text
ARCH-023-DATABASE-001
@modainteract/moda-interact-shared/merchant-knowledge
ARCH-021-COMMERCE-096 PolicyOperationRegistration
```

Produces Commerce-local:

```text
merchantKnowledge.lookup@1.0.0
```

No new Shared contract.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`
- `ARCH-021-COMMERCE-096`

## Enables

- `ARCH-023-COMMERCE-002`

## Acceptance Criteria

- [x] One canonical C096 registration owns operation runtime/authoring metadata.
- [x] Trusted shop identity never comes from the model.
- [x] Commercial entitlement is rechecked inside the operation.
- [x] Tool reuse by another Capability cannot bypass Merchant Knowledge plan entitlement.
- [x] Exact pgvector retrieval is tenant/source/provenance bounded.
- [x] No language filter prevents cross-language retrieval.
- [x] C5 result is bounded and contains no storage/security secrets.
- [x] No bootstrap/Studio generic UI implementation is introduced.

## Validation

- [x] focused C5/entitlement/embedding/operation tests
- [x] real disposable PostgreSQL + pgvector production retrieval proof
- [x] existing DefinitionExecutor/policy-operation regressions
- [x] `npm run typecheck`
- [x] `npm run lint` (warnings only; changed-file ESLint clean)
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not start COMMERCE-002.

## Completion Report

### Status
Attempt 2 review correction and required PostgreSQL/pgvector proof complete; submitted for architecture review. Attempt 1 Architect Review remains unchanged.
### Files Changed
- `moda-interact-commerce/.env.example`
- `moda-interact-commerce/lib/preview/runtime.ts`
- `moda-interact-commerce/lib/server/config.ts`
- `moda-interact-commerce/lib/server/connections.ts`
- `moda-interact-commerce/package.json`
- `moda-interact-commerce/package-lock.json`
- `moda-interact-commerce/src/commerce/execution/policy-operation-authoring.ts`
- `moda-interact-commerce/src/commerce/execution/renderer.ts`
- `moda-interact-commerce/src/commerce/integration/backend.ts`
- `moda-interact-commerce/src/commerce/merchant-knowledge/contracts.ts`
- `moda-interact-commerce/src/commerce/merchant-knowledge/embedding.ts`
- `moda-interact-commerce/src/commerce/merchant-knowledge/entitlement.ts`
- `moda-interact-commerce/src/commerce/merchant-knowledge/operation.ts`
- `moda-interact-commerce/src/commerce/merchant-knowledge/retrieval.ts`
- `moda-interact-commerce/src/commerce/tool-definition/contracts.ts`
- `moda-interact-commerce/tests/arch021-commerce-tool-contract.test.ts`
- `moda-interact-commerce/tests/database-contract.test.ts`
- `moda-interact-commerce/tests/health.test.ts`
- `moda-interact-commerce/tests/merchant-knowledge-contract.test.ts`
- `moda-interact-commerce/tests/merchant-knowledge-embedding.test.ts`
- `moda-interact-commerce/tests/merchant-knowledge-entitlement.test.ts`
- `moda-interact-commerce/tests/merchant-knowledge-policy-postgres.test.ts`
- `moda-interact-commerce/tests/merchant-knowledge-policy.test.ts`
- `moda-interact-commerce/tests/merchant-knowledge-retrieval.test.ts`
- `moda-interact-commerce/tests/policy-operation-registry.test.ts`
- `moda-interact-commerce/tests/preview-model-provider.test.ts`
### Work Completed
- Adopted the prepared Database gitlink revision and the exact `@modainteract/moda-interact-shared@1.0.1` dependency; no database schema/migration changes or gitlink changes were introduced.
- Added strict C5 input/output runtime validators, OpenAI embedding configuration and adapter, current-plan Merchant Knowledge entitlement enforcement, tenant/source/provenance-bounded exact pgvector retrieval, and canonical `merchantKnowledge.lookup@1.0.0` registration.
- Added the exact bounded authoring arguments/result descriptors and the five-match renderer item limit. Runtime Zod validation remains authoritative for enum and literal semantics.
- Added focused contract, entitlement, embedding, retrieval, registration, rendering, and conditional pgvector tests. No Tool/Capability/release bootstrap or Studio UI was introduced.
- Corrected the connection-check helper types affected by expanding server configuration.
- Attempt 2 A1-R1: replaced the unrelated temporary-vector-table smoke test with a disposable PostgreSQL test that invokes production `retrieveMerchantKnowledge` against the migrated ARCH-023 tables. Deterministic fixtures prove cosine ordering and exclude closer cross-shop, superseded-revision, and embedding-model-mismatched chunks.
### Validation Results
- Attempt 1 focused C5/entitlement/embedding/retrieval/operation/registry/DefinitionExecutor/database-contract packet: 8 files passed, 47 tests passed, 1 test skipped. Attempt 2 replaced that skipped smoke test with the live proof below.
- Attempt 2 live proof: `tests/merchant-knowledge-policy-postgres.test.ts` passed (1/1) against `pgvector/pgvector:pg17`. All 21 migrations from the pinned `database/prisma/schema.prisma` were deployed to a newly created `commerce_arch023_test` database bound only to `127.0.0.1` on a dynamically assigned port; the production retrieval call returned the two expected nearest eligible facts and excluded all three closer ineligible fixtures. The disposable container was removed after the test. `COMMERCE_TEST_DATABASE_URL` rejects non-loopback/non-test targets, URL overrides, and the configured `DATABASE_URL`; no remote database was used.
- `npm run typecheck`: passed.
- `npm run lint`: passed with warnings only. Targeted ESLint over changed implementation and test files passed without warnings. Remaining full-repository warnings are in untouched files.
- `npm run build`: passed; existing Nunjucks dynamic dependency warning was emitted during compilation.
- Changed-file diagnostics: no errors. `git diff --check`: passed.
- Startup evidence from the deterministic prepare packet: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-COMMERCE-001` on `task/ARCH-023-COMMERCE-001`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-COMMERCE-001` on the same task branch. Both worktrees were newly created, no other task worktree or shared checkout was reused or switched. Parent and implementation task branches required no remote fast-forward; `origin/main` was already current in both.
- Recursive implementation submodule sync/init passed. The `database` submodule was initialized at `2eb17ee910491e8f9df82736fc0a843844415947`.
### Deviations
None. The live proof used an ephemeral local pgvector container rather than the configured remote database.
### Assumptions
- The launcher-prepared database gitlink at `2eb17ee910491e8f9df82736fc0a843844415947` is the accepted ARCH-023-DATABASE-001 revision, as established by the deterministic dependency gate and initialized submodule packet.
### Unresolved Issues
None.
### Architectural Concerns
- None identified. `## Architect Review` below remains unchanged.

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes

The production implementation is otherwise architecture-conformant on the reviewed
paths: the exact C5 validators and authoring descriptors are registered through the
accepted C096 registry; trusted shop identity comes from the authorized turn; current
commercial entitlement is rechecked independently of capability association; source
eligibility is resolved before the source cap; the raw query is tenant/source/provenance
bounded and parameterized; result shaping is bounded; and no Tool/Capability/release
bootstrap was introduced.

One acceptance-blocking validation defect remains:

**A1-R1 — the required disposable PostgreSQL/pgvector retrieval proof is both unexecuted
and currently too shallow.** `tests/merchant-knowledge-policy-postgres.test.ts` creates an
unrelated temporary vector table and exercises the pgvector `<=>` operator directly. It
does not invoke `retrieveMerchantKnowledge`, the Merchant Knowledge policy adapter, or
the production R11 SQL. Running that test successfully would therefore prove pgvector is
available, but would not prove that COMMERCE-001's real tenant/source/provenance-bounded
retrieval query executes correctly against the ARCH-023 schema.

Attempt 2 is a bounded validation correction. Strengthen the disposable PostgreSQL test
so it executes the production Merchant Knowledge retrieval path against a local disposable
test database with the accepted ARCH-023 schema and pgvector enabled. Seed deterministic
fixtures that prove, through the production query, a known cosine nearest-neighbour
ordering. The proof must also demonstrate that a closer row is excluded when it belongs
to another shop, a non-ACTIVE revision, or mismatched embedding provenance. Keep the test
strictly disposable/local and continue refusing the configured remote database.

No production implementation change is requested unless the strengthened live proof
exposes an actual defect.

### Reviewed Files

- `src/commerce/merchant-knowledge/contracts.ts`
- `src/commerce/merchant-knowledge/embedding.ts`
- `src/commerce/merchant-knowledge/entitlement.ts`
- `src/commerce/merchant-knowledge/retrieval.ts`
- `src/commerce/merchant-knowledge/operation.ts`
- `src/commerce/execution/policy-operation-authoring.ts`
- `src/commerce/execution/renderer.ts`
- `src/commerce/integration/backend.ts`
- `src/commerce/tool-definition/contracts.ts`
- `lib/server/config.ts`
- `lib/server/connections.ts`
- `lib/preview/runtime.ts`
- `tests/merchant-knowledge-contract.test.ts`
- `tests/merchant-knowledge-embedding.test.ts`
- `tests/merchant-knowledge-entitlement.test.ts`
- `tests/merchant-knowledge-retrieval.test.ts`
- `tests/merchant-knowledge-policy.test.ts`
- `tests/merchant-knowledge-policy-postgres.test.ts`
- `tests/policy-operation-registry.test.ts`
- `package.json`
- `package-lock.json`
- `docs/decisions/commerce/ARCH-023/COMMERCE-001-implement-merchant-knowledge-policy-operation.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`

### Validation Reviewed

- Reviewed the recorded focused result: 47 tests passed and the single live pgvector test
  was skipped.
- Reviewed the recorded passing TypeScript check and production build.
- Reviewed the recorded full lint result (warnings only), changed-file ESLint pass,
  changed-file diagnostics pass and `git diff --check` pass.
- Confirmed the task's required `real disposable PostgreSQL + pgvector retrieval proof`
  remains unchecked in the authoritative Validation section.
- Inspected the skipped PostgreSQL test and confirmed it validates pgvector operator
  behavior only; it does not execute the production Merchant Knowledge retrieval SQL.
- Reviewed the launcher-resolved dedicated parent/implementation worktree evidence,
  synchronization evidence and recursive database-submodule initialization recorded in
  the Completion Report.

### Architecture Conformance

The implementation code is consistent with the ARCH-023/C096 ownership boundaries and no
production-code correction is presently identified. Acceptance is withheld because R16
and the explicit Validation contract require a real disposable PostgreSQL/pgvector proof
of the production retrieval path. Mocked Prisma/query-shape tests plus a standalone
pgvector smoke query are not equivalent to that integration boundary.

### Follow-up

`ARCH-023-COMMERCE-001` returns to **Ready** for Attempt 2 with `attempt: 1` preserved and
no active executor/claim. The next normal claim increments it to Attempt 2.

Attempt 2 must:

1. strengthen `tests/merchant-knowledge-policy-postgres.test.ts` as described in A1-R1;
2. run that test against a local disposable PostgreSQL database with pgvector and the
   accepted ARCH-023 schema;
3. record the exact command/database safety evidence and passing result;
4. mark the live PostgreSQL/pgvector Validation item complete only after the proof passes;
5. rerun only the focused checks materially affected by the test correction; and
6. return the same task to Architect Review and STOP.

`ARCH-023-COMMERCE-002` remains **Pending** and must not be started until COMMERCE-001 is
Accepted/Complete.
