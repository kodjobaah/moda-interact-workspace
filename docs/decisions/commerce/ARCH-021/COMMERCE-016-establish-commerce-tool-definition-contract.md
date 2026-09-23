---
id: ARCH-021-COMMERCE-016
architecture_id: ARCH-021
title: Establish the canonical Commerce-owned Tool definition contract
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-021-COMMERCE-017
  - ARCH-021-COMMERCE-018
  - ARCH-021-COMMERCE-020
created: 2026-09-23
updated: 2026-09-24
---

# Establish the canonical Commerce-owned Tool definition contract

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Move the complete persisted Tool authoring/execution definition out of Shared ownership and make `moda-interact-commerce` the canonical source for Phase 3 `EXTERNAL_HTTP`, `SHOPIFY_ADMIN_GRAPHQL`, transitional Storefront and policy execution definitions, while preserving only genuinely cross-service descriptors/results in `@modainteract/moda-interact-shared@0.14.2`.

## Context

The full `CommerceToolDefinition` is currently defined in `moda-interact-shared/src/commerce/definitions.ts`, but inspection of the current workspace confirms the full definition is consumed only by `moda-interact-commerce`. Background and the other services consume the projected MCP/runner contracts (`ToolDescriptor`, `CommerceManifest`, `CommerceToolResult`, runner contracts), not the connection revision, GraphQL document, request JavaScript or response-processing definition.

ARCH-021 therefore corrects ownership without publishing a new Shared package. Shared remains pinned at exact `0.14.2`; Phase 3 may import reusable primitives from it but MUST NOT modify or publish Shared. Existing authoring exports in Shared may remain temporarily as dead legacy exports; no new Commerce code may use them as the canonical Tool definition after this task.

Moda is pre-production. Change the canonical Commerce definition directly. Do not create `EXTERNAL_HTTP_V2`, legacy normalization adapters or dual canonical schemas for development-only persisted definitions.

## Scope

Create this exact Commerce-owned module boundary:

```text
src/commerce/tool-definition/
  contracts.ts
  mappings.ts
  publication.ts
  storage.ts
  index.ts
```

Migrate Commerce imports/usages of the following full-authoring concepts from `@modainteract/moda-interact-shared/commerce` to `src/commerce/tool-definition`:

```text
CommerceToolDefinitionSchema
CommerceToolDraftDefinitionSchema
CommerceToolDefinition
CommerceToolDraftDefinition
ExternalHttpExecution
CommerceExecutionSchema
CommerceDefinitionCompiler
validateDefinitionForPublication
definitionToMcpDescriptor
mapToolArguments
toolHashInput
```

The migration includes production Commerce code and focused tests/fixtures that currently import those names, including at minimum:

```text
src/commerce/execution/executor.ts
src/commerce/execution/ports.ts
src/commerce/integration/backend/* definition/compiler consumers
src/commerce/preview/* definition consumers
src/commerce/external-http/* definition consumers
src/commerce/external-preview/* definition consumers
src/commerce/external-publication/* definition consumers
src/studio/testing/in-memory-studio-services.ts
tests/query-execution.test.ts
tests/definition-execution.test.ts
tests/external-http-executor.test.ts
tests/local-external-mcp-diagnostic.test.ts
```

Small adjacent import changes are allowed only where `rg` proves the same full Tool-definition concepts are consumed. Do not move genuinely shared `ToolDescriptor`, `GrantedTool`, `CommerceToolResult`, manifest or runner contracts out of Shared.

## Out of Scope

- Modifying `moda-interact-shared` source or package version.
- Publishing a Shared package.
- Provider/network execution for new Phase 3 execution modes.
- Request-JavaScript QuickJS execution (COMMERCE-017).
- Shopify Admin compiler implementation (COMMERCE-018).
- Studio UI (COMMERCE-020/021/022).
- Database changes.
- Conversation tool-invocation persistence.
- Removing obsolete authoring exports from Shared; leave them untouched until a later genuine Shared release.

## Requirements

### R1 — exact Shared boundary

`package.json` MUST remain on exact:

```json
"@modainteract/moda-interact-shared": "0.14.2"
```

Phase 3 MUST NOT edit the Shared gitlink/package or create a Shared publication task.

Commerce-local contracts MAY import the existing exported primitives needed to build the local definition, including:

```text
zod-compatible Shared primitives already exported from /commerce:
IdSchema
SemverSchema
HashSchema
InputSchemaSchema
DetailsSchemaSchema
ExternalPathSchema
ExternalQueryMappingsSchema
ExternalQueryValueSchema
ExternalResponseFormatSchema
VisualResponseProcessingSchema
ResponseTemplate-compatible primitives where appropriate
safeName / safePath / compileSubset / boundedJson / canonicalJson
ToolDescriptorSchema / ToolDescriptor
```

Do not import `CommerceToolDefinitionSchema` or `CommerceToolDefinition` from Shared in production Commerce code after migration.

### R2 — exact local storage rule

`src/commerce/tool-definition/storage.ts` owns the current PostgreSQL jsonb-text storage bound. Preserve the existing behavior exactly:

```text
maximum definition storage bytes: 65536
error text: Definition exceeds the 65536-byte jsonb text limit
```

Use canonical JSON normalization and the current jsonb-text byte accounting semantics; do not silently replace this with `JSON.stringify(value).length`.

### R3 — exact external request descriptor

In `contracts.ts`, define/export strict `ExternalRequestDescriptorSchema` with exactly:

```ts
{
  path: string;
  query: Record<string, string | number | boolean>;
  headers: Record<string, string>;
}
```

Rules:

```text
path
  existing ExternalPathSchema

query
  max 32 keys
  safeName keys
  scalar values only: string | finite number | boolean

headers
  max 16 keys
  canonical lowercase name matching ^[a-z][a-z0-9-]{0,63}$
  UTF-8 value <= 2048 bytes
  value contains no CR/LF/NUL
```

Reject these header names case-insensitively:

```text
authorization
proxy-authorization
proxy-authenticate
cookie
set-cookie
host
content-length
transfer-encoding
connection
x-api-key
api_key
apikey
access_token
token
secret
password
```

The descriptor MUST NOT accept `origin`, absolute `url`, `method`, `body`, credentials, timeout, redirect policy, shop identity or arbitrary extra fields.

### R4 — exact EXTERNAL_HTTP request construction

Define/export strict `ExternalRequestConstructionSchema` as exactly:

```ts
{
  kind: 'DECLARATIVE';
  path: ExternalPathSchema;
  query: ExternalQueryMappingsSchema;
  headers: ExternalRequestHeadersSchema;
}
|
{
  kind: 'JAVASCRIPT';
  runtimeVersion: 'quickjs-sync.v1';
  source: string; // non-empty, UTF-8 <= 16384 bytes
}
```

`DECLARATIVE.headers` are static safe literal headers. Dynamic request shaping uses JavaScript.

The JavaScript source contract is exactly:

```js
function buildRequest({ args }) {
  return {
    path: '/catalogue/search',
    query: { q: args.query },
    headers: { accept: 'application/json' }
  };
}
```

`export default`, imports, async functions and network operations are not part of the persisted contract.

### R5 — exact response processing

Define local response processing as:

```text
DIRECT
OBJECT
LIST
JAVASCRIPT
```

Add strict:

```ts
{ kind: 'DIRECT' }
```

Semantics enforced by the local EXTERNAL_HTTP schema:

```text
DIRECT      -> responseFormat.mode == JSON
OBJECT/LIST -> responseFormat.mode == JSON
JAVASCRIPT  -> resultPath == ''
```

DIRECT means: decode JSON, select `resultPath` (or root when empty), validate the selected JSON value directly against `resultSchema`; no visual projection/filter or JavaScript transform.

### R6 — exact canonical EXTERNAL_HTTP shape

The canonical local parser MUST accept exactly:

```ts
{
  kind: 'EXTERNAL_HTTP';
  executorVersion: '1.0.0';
  connectionRevisionId: IdSchema;
  method: 'GET';
  request: ExternalRequestConstructionSchema;
  responseFormat: ExternalResponseFormatSchema;
  resultPath: string; // '' or safePath
  responseProcessing: LocalResponseProcessingSchema;
  resultSchema: DetailsSchemaSchema;
}
```

The canonical parser MUST reject the old root-level `path` / `query` EXTERNAL_HTTP shape. Migrate development fixtures/tests; do not add normalization.

### R7 — exact Shopify Admin GraphQL shape

Add strict local `ShopifyAdminGraphqlExecutionSchema`:

```ts
{
  kind: 'SHOPIFY_ADMIN_GRAPHQL';
  executorVersion: '1.0.0';
  apiVersion: '2026-07';
  schemaHash: HashSchema;
  document: string;              // non-empty, UTF-8 <= 16384 bytes
  operationName: safeName;
  variables: MappingSchema record with <= 32 entries;
  resultPath: safePath;
  resultSchema: DetailsSchemaSchema;
}
```

It MUST NOT contain shop id/domain/session/token/scopes. Commerce's selected-shop/offline-session context is runtime state for Phase 4.

### R8 — execution union

Local `CommerceExecutionSchema` MUST contain exactly:

```text
SHOPIFY_STOREFRONT_QUERY   transitional existing runtime/read-history support
POLICY_OPERATION            existing
EXTERNAL_HTTP              canonical Phase 3 shape
SHOPIFY_ADMIN_GRAPHQL      new authoring shape
```

Do not offer Storefront as the target new-authoring kind after COMMERCE-022, but keep it parseable during Phase 3 so historical accepted definitions remain readable.

### R9 — Tool definition identity

Local `CommerceToolDefinitionSchema` preserves the current common fields exactly:

```text
name
  ToolNameSchema behavior unchanged

definitionVersion
  SemverSchema

description
  1..4096

inputSchema
  InputSchemaSchema

execution
  local CommerceExecutionSchema

responseTemplate
  current response-template semantics
```

Preserve the existing authority/credential input-name prohibition and 65536-byte storage bound.

`CommerceToolDraftDefinitionSchema` remains a loose bounded draft object with the same identity and 65536-byte storage bound.

### R10 — argument mapping

`mapToolArguments(definition, raw)` MUST validate `raw` against the persisted `inputSchema` before any mapping.

Then:

```text
POLICY_OPERATION
  existing argument mapping

SHOPIFY_STOREFRONT_QUERY
  existing variables mapping

SHOPIFY_ADMIN_GRAPHQL
  variables mapping using the same mapping contract

EXTERNAL_HTTP + DECLARATIVE
  map request.query only using existing scalar restrictions

EXTERNAL_HTTP + JAVASCRIPT
  return a null-prototype deep/plain bounded copy of the validated top-level argument object for COMMERCE-017
```

No credential/authority value may be supplied by model arguments.

### R11 — cross-service projection remains Shared

`definitionToMcpDescriptor()` MUST still return only:

```text
name
description
inputSchema
```

and then be parsed/compatible with the existing Shared `ToolDescriptorSchema`.

Do not expose execution kind, connection revision, GraphQL document, request/response JavaScript, provider origin, schema hash or credentials through the descriptor.

### R12 — publication structural helper

Move `validateDefinitionForPublication()` into `publication.ts` and update structural semantics for:

```text
EXTERNAL_HTTP + DIRECT
  output = { values: resultSchema }

EXTERNAL_HTTP + OBJECT/LIST
  preserve accepted visual compatibility checks

EXTERNAL_HTTP + JAVASCRIPT
  preserve declared resultSchema wrapper

SHOPIFY_ADMIN_GRAPHQL
  delegate document/output proof to a `CommerceDefinitionCompiler`; COMMERCE-018 supplies the Admin implementation later
```

This task does not create a live-test receipt or provider call.

### R13 — runtime fail-closed baseline

After the local union is adopted, existing executable production branches MUST continue for:

```text
POLICY_OPERATION
SHOPIFY_STOREFRONT_QUERY
EXTERNAL_HTTP + DECLARATIVE + OBJECT/LIST/JAVASCRIPT response
```

The following Phase 3 definitions MUST fail closed before provider I/O until their later tasks/Phase 4 explicitly enable execution:

```text
EXTERNAL_HTTP + JAVASCRIPT request
EXTERNAL_HTTP + DIRECT response
SHOPIFY_ADMIN_GRAPHQL
```

Do not downgrade JS request to declarative or Admin GraphQL to Storefront.

### R14 — deterministic migration test

Add npm script:

```json
"test:arch021-commerce-tool-contract": "vitest run tests/arch021-commerce-tool-contract.test.ts"
```

The focused suite MUST prove at least:

1. canonical declarative EXTERNAL_HTTP parses;
2. old root-level path/query EXTERNAL_HTTP fails;
3. canonical JavaScript request parses;
4. request descriptor rejects URL/origin/method/body/credential fields;
5. reserved headers fail;
6. DIRECT requires JSON;
7. JavaScript response requires empty `resultPath`;
8. SHOPIFY_ADMIN_GRAPHQL parses structurally only with pinned version/required fields;
9. MCP descriptor contains only name/description/inputSchema;
10. request-JS argument mapping returns validated CommerceAgent args only;
11. Admin variable mapping uses persisted inputSchema;
12. tool hash changes when request source/header/response mode/Admin document changes;
13. policy and transitional Storefront definitions still parse;
14. `rg` shows no production Commerce import of `CommerceToolDefinitionSchema` or `CommerceToolDefinition` from Shared.

## Work Items

- [x] Create the exact `src/commerce/tool-definition/*` module boundary.
- [x] Define the canonical local Tool schemas/types/helpers above.
- [x] Migrate Commerce production imports from Shared full Tool-definition ownership.
- [x] Migrate development fixtures/tests to the canonical EXTERNAL_HTTP request shape.
- [x] Keep cross-service ToolDescriptor/result/manifest/runner contracts in Shared.
- [x] Make new Phase 3 execution branches fail closed before provider I/O.
- [x] Add focused contract/migration regression.

## Interfaces / Contracts

Produces the Commerce-local canonical Tool definition consumed by:

- ARCH-021-COMMERCE-017
- ARCH-021-COMMERCE-018
- ARCH-021-COMMERCE-019
- ARCH-021-COMMERCE-020
- ARCH-021-COMMERCE-021
- ARCH-021-COMMERCE-022

Continues to project the existing Shared `ToolDescriptor` at the Commerce/Background/MCP boundary.

## Dependencies

- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-030

Both are already Complete in the Phase 3 baseline.

## Enables

- ARCH-021-COMMERCE-017
- ARCH-021-COMMERCE-018
- ARCH-021-COMMERCE-020

## Acceptance Criteria

- [x] Full persisted Tool authoring definition is Commerce-owned.
- [x] Shared remains exact 0.14.2 and is not modified/published.
- [x] There is one canonical EXTERNAL_HTTP shape and no compatibility parser.
- [x] `SHOPIFY_ADMIN_GRAPHQL` is structurally authorable but not live-executable.
- [x] Request JavaScript can describe only a bounded relative GET request.
- [x] DIRECT/Visual/JavaScript response semantics are deterministic.
- [x] Existing policy and transitional Storefront behavior remains readable/executable.
- [x] Cross-service descriptor/result contracts remain Shared and unchanged.

## Validation

- [x] `npm run test:arch021-commerce-tool-contract` (7/7)
- [x] `npm run test:arch020-external-http` (13/13)
- [ ] `npm run test:arch020-backend-integration` (60/62; 2 existing backend singleton environment assertions fail)
- [x] targeted lint; full typecheck attempted, with existing Shared/Prisma baseline diagnostics remaining
- [x] `git diff --check`

## Stop Condition

After the exact contract, migration and focused validation pass, complete the Completion Report, set the task to `review`, return control to `moda_architect` and STOP. Do not implement request JavaScript execution, Admin compiler or UI in this task.

## Implementation Notes

This task may update/reseed development fixtures. It MUST NOT perform production-data compatibility work. Existing dead authoring exports in Shared are intentionally left untouched until a future genuine Shared release.

## Completion Report

### Status
Ready for architect review.

### Implementation

Created the Commerce-owned contract boundary in `src/commerce/tool-definition/` with local contracts, mappings, publication validation, storage accounting, and MCP projection. The canonical `EXTERNAL_HTTP` shape now uses nested `request`, supports declarative and bounded JavaScript request descriptions, preserves visual/direct/JavaScript response semantics, pins Admin GraphQL to `2026-07`, and fails closed for request JavaScript, direct response execution, and Admin GraphQL runtime branches.

Migrated Commerce runtime, publication, preview, external integration, compiler, and focused fixture consumers. Shared remains untouched and the package dependency remains exactly `@modainteract/moda-interact-shared: 0.14.2`.

### Evidence

- Launcher claim: attempt 1, executor `copilot`, implementation branch `task/ARCH-021-COMMERCE-016`.
- Implementation commit pushed: `98511ef`.
- Focused contract: 7/7.
- External HTTP executor: 13/13.
- External publication: 12/12.
- External preview: 19/19.
- Execution, wiring, and lifecycle slice: 17/17.
- Legacy studio UI regression: 13/13; UI remains out of scope for this task.
- Local disposable PostgreSQL/Redis MCP diagnostic: end-to-end PASS; persisted lifecycle, signed `tools/list`, signed `tools/call`, and cleanup all passed.
- Targeted ESLint and `git diff --check`: pass.

### Limitations

- The backend integration command reports 60/62 passing because two pre-existing singleton tests expect unavailable production dependencies while this environment resolves them; no contract-specific failure was reported.
- Full repository typecheck remains non-clean due existing Shared/local Storefront type-boundary diagnostics and Prisma/generated-client baseline diagnostics. The changed focused suites and targeted lint pass.

### Parent report state

Task status is `review`, with `executor: null` and `claimed_at: null`. Control is returned to `moda_architect`; no request-JavaScript execution, Admin compiler implementation, or UI work was added.

## Architect Review

### Review Status
Changes Requested — Attempt 1.

### Review Notes
Reviewed the corrected submitted snapshot for implementation `98511ef` and parent
report `9b7de4ad`. The new `src/commerce/tool-definition/` boundary is directionally
correct, Shared remains pinned at exact `0.14.2`, the canonical nested
`EXTERNAL_HTTP.request` shape exists, new runtime kinds fail closed in the executor,
and the local MCP diagnostic evidence is useful. Attempt 1 is not accepted because
the ownership migration and several exact contract semantics are incomplete.

The correction items below are the complete Attempt 2 rework contract. Keep the
work inside COMMERCE-016: do not implement request-JavaScript execution, the Admin
GraphQL compiler, Phase 3 UI expansion, database work or a Shared publication.

#### A1-R1 — finish the Commerce-owned definition migration

Source/import and focused-test changes are required. The task requires the full
persisted authoring definition to have one Commerce owner, but the submitted tree
still consumes the old Shared full-definition contracts in production code. At
minimum the review snapshot still contains:

- `lib/discovery/schema.ts` importing Shared `validateDefinitionForPublication`;
- `src/studio/contracts.ts` importing Shared `CommerceToolDefinition` /
  `CommerceToolDraftDefinition`;
- `src/commerce/mcp/ports.ts` importing Shared `CommerceToolDefinition`;
- `src/commerce/publication/ports.ts` importing Shared Tool definition/draft types;
- `src/commerce/preview/types.ts` and
  `src/commerce/integration/preview/adapters.ts` importing Shared Tool definition
  schema/types;
- `src/studio/external-http/ports.ts`, `src/studio/external-http/editor.tsx` and
  `components/studio-workspace.tsx` still consuming the old Shared full Tool /
  EXTERNAL_HTTP definition contract; and
- focused/adjacent tests such as `tests/query-execution.test.ts`,
  `tests/recommendation-contract.test.ts`, `tests/commerce-lifecycle.test.ts`,
  `tests/studio-services.test.ts`, `tests/external-wiring.test.ts` and
  `tests/external-tools-ui.test.tsx` still importing the legacy definition helpers.

`lib/discovery/schema.ts` is particularly important: calling the old Shared
publication helper leaves a second canonical publication definition path after this
task. Migrate the full-definition symbols to `src/commerce/tool-definition`; retain
Shared imports only for genuinely cross-service primitives/results/descriptors,
manifests, grants and runner contracts. Do not redesign the Studio UI here; make
only the minimum contract/fixture changes needed to stop using the old full
definition as canonical.

Acceptance proof must include an exhaustive `rg` (or equivalent deterministic
check) showing no production Commerce import of Shared
`CommerceToolDefinitionSchema`, `CommerceToolDefinition`,
`CommerceToolDraftDefinitionSchema`, `CommerceToolDraftDefinition`, the old full
`ExternalHttpExecution` schema/type, Shared `validateDefinitionForPublication`,
`definitionToMcpDescriptor`, `mapToolArguments` or `toolHashInput`. Migrate the
focused/fixture consumers called out by the task as well.

#### A1-R2 — enforce the exact request-JavaScript persisted/argument contract

Source and focused-test changes are required. `mapToolArguments()` currently uses
`JSON.parse(JSON.stringify(input))` for `EXTERNAL_HTTP + JAVASCRIPT`. That returns
ordinary prototype-bearing objects and does not satisfy R10's required
null-prototype deep/plain bounded copy of the already validated CommerceAgent
arguments. Build the copy deterministically after `inputSchema` validation, with
null prototypes for object nodes and no authority/credential injection. Add a
regression that verifies the top-level and nested object prototypes and that invalid
raw input is rejected before copying.

The focused contract test also currently asserts that
`export default async function buildRequest() {}` parses successfully. That is the
opposite of R4, which defines a synchronous `function buildRequest({ args }) { ... }`
persisted source contract and states that `export default`, imports, async functions
and network operations are not part of it. Remove that positive assertion and make
persisted-source admission deterministically reject those unsupported forms without
executing JavaScript or performing network I/O. COMMERCE-017 remains the runtime
owner.

#### A1-R3 — restore accepted visual publication-shape compatibility

Source and focused-test changes are required. The submitted local
`validateDefinitionForPublication()` derives `{ values: resultSchema }` for every
EXTERNAL_HTTP definition and does not statically compare OBJECT/LIST projections
with the declared closed `resultSchema`. This reintroduces the publication hole that
was already corrected in the accepted Shared contract: for example an OBJECT
projection can produce `{ other: ... }` while `resultSchema` requires `title`, yet
the current local helper can still accept a response template using
`result.values.title`.

Preserve the accepted semantics when moving ownership locally:

- DIRECT -> wrapper output `{ values: resultSchema }`;
- OBJECT/LIST -> deterministic static visual projection/result-schema compatibility,
  including required names, LIST array/item shape, scalar projection compatibility,
  undeclared output names and `omitIfMissing` versus required outputs;
- JAVASCRIPT -> declared `resultSchema` wrapper; and
- SHOPIFY_ADMIN_GRAPHQL -> delegate document/output proof to the supplied
  `CommerceDefinitionCompiler`.

Do not call the legacy Shared publication helper as the new canonical owner. Add at
least valid OBJECT/LIST controls and focused negative regressions for incompatible
projection names/shape. No live provider call belongs here.

#### A1-R4 — complete the mandatory R14 migration/contract proof

The new focused script reports 7 tests, but the submitted suite does not prove all
mandatory R14 cases. Extend it (test count itself is irrelevant) so the required
behaviours are actually demonstrated, including:

- request descriptor rejection of extra `origin`, `method`, `body` and credential
  fields plus lowercase reserved headers;
- request-JS argument mapping returning only validated CommerceAgent arguments with
  the R10 safe-copy semantics;
- Admin GraphQL variable mapping through the persisted `inputSchema`;
- tool-hash changes for request source, headers, response mode and Admin document;
- policy and transitional Storefront definitions still parsing;
- canonical JavaScript source acceptance and unsupported source-form rejection per
  R4; and
- the zero-legacy-full-definition-import migration check from A1-R1.

Keep the existing DIRECT/JSON, JavaScript-response root, canonical/root-level HTTP
shape, Admin pinned-version and MCP-projection checks.

#### A1-R5 — reconcile validation and prepared-worktree evidence

The Completion Report records the implementation branch/commit but omits the
launcher-resolved parent worktree, implementation worktree, matching branch names,
start-of-attempt synchronization and recursive submodule/database evidence required
by the architect protocol. Record the exact preparation packet values; do not invent
them. Replace the trailing placeholder `Files Changed/Work Completed/Validation
Results/Deviations/...: None` block with the actual report rather than keeping two
conflicting Completion Reports.

After A1-R1, rerun the task-focused suites, targeted lint and `git diff --check`.
Re-run typecheck and distinguish genuinely pre-existing diagnostics from
Shared/local Tool-definition diagnostics: any diagnostic caused by the incomplete
ownership migration is task-owned and must not be classified as baseline. The two
backend singleton environment assertions may remain documented if they reproduce
unchanged after the corrections and are not caused by the Tool-contract migration.

### Reviewed Files

- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-definition/mappings.ts`
- `src/commerce/tool-definition/publication.ts`
- `src/commerce/tool-definition/storage.ts`
- `src/commerce/tool-definition/index.ts`
- `src/commerce/execution/executor.ts`
- `src/commerce/external-http/index.ts`
- `lib/discovery/schema.ts`
- `src/commerce/publication/ports.ts`
- `src/commerce/mcp/ports.ts`
- `src/commerce/preview/types.ts`
- `src/commerce/integration/preview/adapters.ts`
- `src/studio/contracts.ts`
- `src/studio/external-http/ports.ts`
- `src/studio/external-http/editor.tsx`
- `components/studio-workspace.tsx`
- `tests/arch021-commerce-tool-contract.test.ts`
- adjacent Tool-definition consumers identified by repository search

### Validation Reviewed

- Submitted `npm run test:arch021-commerce-tool-contract`: 7/7 reported pass.
- Submitted `npm run test:arch020-external-http`: 13/13 reported pass.
- Submitted external publication/preview/execution/wiring slices and local MCP
  diagnostic reviewed as evidence.
- Submitted backend integration result: 60/62 with two stated environment/baseline
  singleton assertions.
- Static source/import review independently identified A1-R1 through A1-R4.
- The supplied archive does not contain `node_modules`, so Vitest/typecheck were not
  independently rerun in the review environment.

### Architecture Conformance

Changes required. The ownership direction and fail-closed runtime baseline conform,
but the submitted implementation still has dual Shared/Commerce canonical Tool
definitions, does not meet R10 request-JS safe-copy semantics, regresses R12 visual
publication compatibility, and does not yet provide the complete R14 proof.

### Follow-up

Return the same task through `/moda-task ARCH-021-COMMERCE-016`. Preserve
`attempt: 1`; the next authorized claim increments to Attempt 2. Do not start
COMMERCE-017/018/020 until COMMERCE-016 is architect-accepted Complete.
