---
id: ARCH-021-COMMERCE-018
architecture_id: ARCH-021
title: Implement pinned Shopify Admin GraphQL authoring compiler
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-020-COMMERCE-011
enables:
  - ARCH-021-COMMERCE-019
  - ARCH-021-COMMERCE-022
created: 2026-09-23
updated: 2026-09-23
---

# Implement pinned Shopify Admin GraphQL authoring compiler

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Add a server-side, offline Shopify Admin GraphQL 2026-07 compiler for `SHOPIFY_ADMIN_GRAPHQL` tool drafts, using the pinned `@shopify/dev-mcp@1.15.4` Admin schema and its `validate_graphql_codeblocks` capability as development conformance evidence, without requiring a shop session or making an Admin API request.

## Context

Commerce already pins `@shopify/dev-mcp@1.15.4`, starts `shopify-dev-mcp` with telemetry disabled, and contains a Storefront compiler plus tests that directly load `dist/data/admin_2026-07.json.gz`. Phase 3 promotes the Admin schema into an explicit authored-tool validator. Shopify Dev MCP remains a development/schema oracle, not the deployed execution path.

## Scope

Primary files:

```text
lib/discovery/artifacts/admin-2026-07.json
lib/discovery/artifacts/admin-2026-07.provenance.json
lib/discovery/admin-compiler.ts
lib/discovery/admin-schema.ts
lib/discovery/schema.ts
lib/discovery/service.ts
lib/discovery/upstream.ts
app/api/studio/discovery/route.ts
scripts/sync-shopify-admin-schema.mjs
scripts/validate-shopify-admin-oracle.mjs
tests/admin-graphql-compiler.test.ts
tests/discovery-route.test.ts
package.json
```

Do not replace the existing Storefront artifact/compiler in this task.

## Out of Scope

- Shopify session/token lookup.
- Calling `https://*.myshopify.com/admin/api/...`.
- Mutations/subscriptions.
- Studio Tool editor UI.
- Runtime executor.
- Auto-updating the pinned API version.

## Requirements

### R1 — pinned source and provenance

The committed Admin artifact MUST be deterministically generated from:

```text
@shopify/dev-mcp@1.15.4
dist/data/admin_2026-07.json.gz
```

`scripts/sync-shopify-admin-schema.mjs` MUST:

1. verify installed `@shopify/dev-mcp` is exactly `1.15.4`;
2. gunzip/parse the source introspection document;
3. write canonical JSON to `lib/discovery/artifacts/admin-2026-07.json`;
4. compute SHA-256 over the exact committed canonical JSON bytes;
5. write `admin-2026-07.provenance.json` containing exactly API surface, API version, package/version, source relative path and SHA-256;
6. fail rather than silently changing API/package versions.

Production validation MUST use the committed artifact, not read `node_modules` at request time.

### R2 — exact compiler input

The compiler accepts `Extract<CommerceToolDefinition['execution'], {kind:'SHOPIFY_ADMIN_GRAPHQL'}>` plus the tool `inputSchema`.

It MUST reject unless all are true:

```text
apiVersion == 2026-07
schemaHash == committed Admin artifact SHA-256
UTF-8 document <= 16384 bytes
GraphQL parses
exactly one OperationDefinition exists
operation is query
operation has a non-empty name equal to execution.operationName
no mutation or subscription exists
GraphQL validate(adminSchema, document) returns zero errors
every variable used by the operation is defined
every non-null variable without a GraphQL default has a mapping
all mapping.input names exist as top-level inputSchema properties
mapped input/literal types are compatible with the GraphQL variable type
resultPath exists in the selected query response shape
selected resultPath resolves to object/array/object-derived data compatible with declared resultSchema
```

Unknown or ambiguous output shape fails closed; do not use `z.unknown()` as proof.

### R3 — query-only read contract

The compiler MUST reject `mutation` and `subscription`, regardless of Shopify scope. This is the authoring safety gate that permits later offline-session execution without exposing write-capable authored tools.

### R4 — discovery route contract

Extend the existing discovery validation input with an explicit API surface:

```text
storefront-graphql
admin-graphql
```

For `admin-graphql`, version is fixed to `2026-07`; the server invokes the local Admin compiler. Browser input cannot select a schema path/package version/hash.

Existing Storefront discovery behavior remains unchanged.

### R5 — Shopify Dev MCP conformance oracle

Extend the pinned upstream only as needed for a developer validation script to call the already allowlisted:

```text
learn_shopify_api
validate_graphql_codeblocks
```

for `admin-graphql` / `2026-07`.

`validate-shopify-admin-oracle.mjs` MUST compare a bounded fixture set against the local compiler:

```text
valid products query                both valid
unknown field                       both invalid
unknown argument                    both invalid
mutation                            local invalid regardless of schema validity
wrong variable type                 both invalid/local type guard
```

This oracle is development validation only. Normal Studio requests MUST NOT spawn Dev MCP to validate a draft and MUST NOT transmit merchant-authored GraphQL to Shopify tooling.

### R6 — no telemetry leakage

Continue spawning Shopify Dev MCP with `SHOPIFY_DEV_MCP_TELEMETRY=0`. The committed/runtime local compiler has no telemetry/network dependency.

### R7 — exact validation commands

Add:

```text
npm run test:arch021-shopify-admin-compiler
npm run validate:arch021-shopify-admin-oracle
```

The first is normal deterministic/offline validation. The second is explicit developer/toolkit conformance validation and must be reported separately if unavailable.

## Work Items

- [ ] Commit deterministic Admin 2026-07 artifact + provenance.
- [ ] Implement query-only Admin compiler.
- [ ] Extend discovery validation API surface.
- [ ] Add Dev MCP conformance script using validate_graphql_codeblocks.
- [ ] Add focused offline compiler tests.

## Interfaces / Contracts

Consumes the COMMERCE-016 Commerce-owned `SHOPIFY_ADMIN_GRAPHQL` execution contract.

Produces a local compiler/validation port for COMMERCE-019 and COMMERCE-022.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-020-COMMERCE-011

## Enables

- ARCH-021-COMMERCE-019
- ARCH-021-COMMERCE-022

## Acceptance Criteria

- [ ] Admin tool drafts are validated locally against pinned Admin 2026-07 schema.
- [ ] Only named GraphQL queries are accepted.
- [ ] No shop credential/session is required for authoring validation.
- [ ] Dev MCP acts only as explicit development conformance evidence.
- [ ] Existing Storefront discovery remains functional.

## Validation

- [ ] `npm run test:arch021-shopify-admin-compiler`
- [ ] `npm run test` for affected discovery/compiler suites
- [ ] `npm run validate:arch021-shopify-admin-oracle` when developer environment supports pinned Dev MCP
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not implement Admin API execution or Tool UI.

## Implementation Notes

The Shopify Toolkit helps prove the compiler; it is not a runtime dependency for merchant requests.

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
