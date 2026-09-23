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
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-09-23T23:17:56Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-021-COMMERCE-017
  - ARCH-021-COMMERCE-018
  - ARCH-021-COMMERCE-020
created: 2026-09-23
updated: 2026-09-23
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

- [ ] Create the exact `src/commerce/tool-definition/*` module boundary.
- [ ] Define the canonical local Tool schemas/types/helpers above.
- [ ] Migrate Commerce production imports from Shared full Tool-definition ownership.
- [ ] Migrate development fixtures/tests to the canonical EXTERNAL_HTTP request shape.
- [ ] Keep cross-service ToolDescriptor/result/manifest/runner contracts in Shared.
- [ ] Make new Phase 3 execution branches fail closed before provider I/O.
- [ ] Add focused contract/migration regression.

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

- [ ] Full persisted Tool authoring definition is Commerce-owned.
- [ ] Shared remains exact 0.14.2 and is not modified/published.
- [ ] There is one canonical EXTERNAL_HTTP shape and no compatibility parser.
- [ ] `SHOPIFY_ADMIN_GRAPHQL` is structurally authorable but not live-executable.
- [ ] Request JavaScript can describe only a bounded relative GET request.
- [ ] DIRECT/Visual/JavaScript response semantics are deterministic.
- [ ] Existing policy and transitional Storefront behavior remains readable/executable.
- [ ] Cross-service descriptor/result contracts remain Shared and unchanged.

## Validation

- [ ] `npm run test:arch021-commerce-tool-contract`
- [ ] `npm run test:arch020-external-http`
- [ ] `npm run test:arch020-backend-integration`
- [ ] targeted lint/typecheck for changed files
- [ ] `git diff --check`

## Stop Condition

After the exact contract, migration and focused validation pass, complete the Completion Report, set the task to `review`, return control to `moda_architect` and STOP. Do not implement request JavaScript execution, Admin compiler or UI in this task.

## Implementation Notes

This task may update/reseed development fixtures. It MUST NOT perform production-data compatibility work. Existing dead authoring exports in Shared are intentionally left untouched until a future genuine Shared release.

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
None
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
None
