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
status: in_progress
priority: 35
executor: copilot
claimed_at: 2026-09-25T12:40:52Z
attempt: 4
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-020-COMMERCE-011
enables:
  - ARCH-021-COMMERCE-024
created: 2026-09-23
updated: 2026-09-25
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

The 2026-09-24 simplification checkpoint is implementation-complete. Its terminal system test remains Ready by developer choice and is not an implementation dependency. This task is restored to Ready because its source dependencies are Complete and its technical contract is unaffected by the simplification.

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
every declared variable is used
every non-null variable without a GraphQL default has a mapping
all mapping.input names exist as top-level inputSchema properties
mapped input/literal types are compatible with the GraphQL variable type
resultPath exists in the selected query response shape
selected resultPath resolves to object/array/object-derived data compatible with declared resultSchema
```

Unknown or ambiguous output shape fails closed; do not use `z.unknown()` as proof.

### R3 — bounded query structure

Reuse the accepted Storefront compiler's structural admission limits for Admin queries rather than inventing a new unbounded GraphQL policy. In addition to R2:

```text
fragments and inline fragments are rejected
operation directives and field directives are rejected
selected field count <= 100
maximum selection depth <= 8, counting the root selection as depth 1
estimated query cost <= 500 using the existing multiplier rule
schema-backed connections require a literal `first` from 1 through 20
`last` pagination is rejected
unbounded list traversal is rejected
```

The cost algorithm MUST match the existing Storefront compiler convention: each selected field contributes the current multiplier; descending through a schema-backed connection multiplies descendant cost by that connection's literal `first` value. Do not substitute a materially different scoring model inside this task.

These are structural safety limits only. Storefront-specific token-required-field and forbidden-root rules do not apply to the Admin schema unless separately required by this task.

### R4 — query-only read contract

The compiler MUST reject `mutation` and `subscription`, regardless of Shopify scope. This is the authoring safety gate that permits later offline-session execution without exposing write-capable authored tools.

### R5 — discovery route contract

Extend the existing discovery validation input with an explicit API surface:

```text
storefront-graphql
admin-graphql
```

For `admin-graphql`, version is fixed to `2026-07`; the server invokes the local Admin compiler. Browser input cannot select a schema path/package version/hash.

Existing Storefront discovery behavior remains unchanged.

### R6 — Shopify Dev MCP conformance oracle

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

### R7 — no telemetry leakage

Continue spawning Shopify Dev MCP with `SHOPIFY_DEV_MCP_TELEMETRY=0`. The committed/runtime local compiler has no telemetry/network dependency.

### R8 — exact validation commands

Add:

```text
npm run test:arch021-shopify-admin-compiler
npm run validate:arch021-shopify-admin-oracle
```

The first is normal deterministic/offline validation. The second is explicit developer/toolkit conformance validation and must be reported separately if unavailable.

## Work Items

- [x] Commit deterministic Admin 2026-07 artifact + provenance.
- [x] Implement query-only Admin compiler.
- [x] Extend discovery validation API surface.
- [x] Add Dev MCP conformance script using validate_graphql_codeblocks.
- [x] Add focused offline compiler tests.

## Interfaces / Contracts

Consumes the COMMERCE-016 Commerce-owned `SHOPIFY_ADMIN_GRAPHQL` execution contract.

Produces a local compiler/validation port for COMMERCE-024.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-020-COMMERCE-011

## Enables

- ARCH-021-COMMERCE-024

## Acceptance Criteria

- [x] Admin tool drafts are validated locally against pinned Admin 2026-07 schema.
- [x] Only named GraphQL queries are accepted.
- [x] Admin queries enforce the existing bounded GraphQL structure: no fragments/directives, <=100 selected fields, depth <=8, estimated cost <=500 and literal `first` pagination <=20.
- [x] No shop credential/session is required for authoring validation.
- [x] Dev MCP acts only as explicit development conformance evidence.
- [x] Existing Storefront discovery remains functional.

## Validation

- [x] `npm run test:arch021-shopify-admin-compiler`
- [x] focused regressions reject fragments, directives, >100 selections, depth >8, cost >500, `last`, non-literal/unbounded pagination and `first > 20`
- [x] `npm run test` for affected discovery/compiler suites
- [x] `npm run validate:arch021-shopify-admin-oracle` when developer environment supports pinned Dev MCP
- [x] targeted lint/typecheck
- [x] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not implement Admin API execution or Tool UI.

## Implementation Notes

The Shopify Toolkit helps prove the compiler; it is not a runtime dependency for merchant requests.

## Completion Report

### Status
Ready for Review
### Files Changed
Implementation commits `db18555446f0c8f3a9601397941451bdb20b3714`, synchronization merge `ed0b0e9e2226d5d133d25de73fb2b9e13b57278e`, and merge repair `bcb61f6` on `task/ARCH-021-COMMERCE-018`:

- `app/api/studio/discovery/route.ts`
- `lib/discovery/admin-compiler.ts`
- `lib/discovery/artifacts/admin-2026-07.json`
- `lib/discovery/artifacts/admin-2026-07.provenance.json`
- `lib/discovery/schema.ts`
- `lib/discovery/service.ts`
- `package.json`
- `scripts/sync-shopify-admin-schema.mjs`
- `scripts/validate-shopify-admin-oracle.mjs`
- `scripts/validate-shopify-admin-local.ts`
- `tests/admin-graphql-compiler.test.ts`
- `tests/discovery-route.test.ts`
### Work Completed
- Added deterministic Admin 2026-07 introspection artifact and exact provenance for `@shopify/dev-mcp@1.15.4`, including SHA-256 `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`.
- Added offline query-only Admin compiler with schema validation, named-operation enforcement, variable/input compatibility, bounded selection/depth/cost/pagination rules, and closed result-path/schema compatibility checks.
- Added explicit `storefront-graphql`/`admin-graphql` discovery validation dispatch without changing Storefront behavior.
- Added the explicit Dev MCP oracle using `learn_shopify_api` and `validate_graphql_codeblocks`; normal request validation remains local and artifact-backed.
- Prepared launcher evidence: parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-018`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-018`; implementation submodule `database` at recorded `98fdf715e54fe6df92ac6951facd104e410068f2`.
### Validation Results
- `npm run test:arch021-shopify-admin-compiler`: PASS, 2 files and 17 tests.
- `npm run validate:arch021-shopify-admin-oracle`: PASS; valid products query matched valid, unknown field/argument and wrong variable type matched invalid, and mutation was locally rejected while upstream schema accepted it.
- Focused ESLint over all changed source/scripts/tests: PASS with no warnings or errors.
- `git diff --check`: PASS.
- Filtered `npm run typecheck`: no diagnostics in the touched Admin compiler, discovery schema/service, route, or Admin tests. Full typecheck remains non-zero on existing unrelated diagnostics, including missing preview modules in `app/api/studio/code-response/validate/route.ts`, existing Studio/agent-configuration strictness errors, and generated/fixture type errors in unrelated tests.
- `npm run build`: BLOCKED by existing unrelated missing modules: `lib/preview/http`, `lib/preview/runtime`, and `src/commerce/preview/types` imported by `app/api/studio/code-response/validate/route.ts`.
- Implementation branch local/remote parity: PASS at `db18555446f0c8f3a9601397941451bdb20b3714`.
- Attempt 2 launcher evidence: parent worktree reused at `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-018`, implementation worktree reused at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-018`, dependencies passed, and recursive submodule initialization completed with `database` at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Attempt 2 synchronization incorporated current `origin/main` in merge `ed0b0e9`; the Storefront artifact discovery refactor was retained while Admin validation dispatch was preserved. The resulting conflict-marker repair is committed and pushed as `bcb61f6`.
- Attempt 2 focused validation: `npm run test:arch021-shopify-admin-compiler` passed 2 files and 17 tests; `npm run validate:arch021-shopify-admin-oracle` passed the valid, invalid, mutation, and wrong-variable fixtures; targeted ESLint passed; `git diff --check` passed.
- Attempt 3 implementation commit `48d6ab0` tightened mapped Admin input/literal compatibility fail-closed for non-null, list, union, enum, scalar and object cases; added the required CR-2 regressions; and added a bounded `vite-node` bridge so every oracle local verdict executes the production Admin compiler.
- Attempt 3 focused validation: `npm run test:arch021-shopify-admin-compiler` passed 2 files and 20 tests; `npm run validate:arch021-shopify-admin-oracle` passed all five fixture comparisons with local verdicts from the production compiler; the exact architect-requested ESLint command passed; and `git diff --check` passed.
- Attempt 3 implementation branch local/remote parity: PASS at `48d6ab0`; accepted Storefront/discovery files and Admin artifact/provenance were unchanged.
- Attempt 2 typecheck: full `npm run typecheck` remains non-zero on unrelated repository diagnostics; filtered output contains no diagnostics in the touched Admin compiler, discovery schema/service/route, scripts, or tests.
- Attempt 2 implementation branch local/remote parity: PASS at `bcb61f6`.
### Deviations
- Full repository typecheck and production build are reported as baseline failures because their diagnostics are outside the task files and were present independently of this compiler change.
### Assumptions
- `@shopify/dev-mcp@1.15.4` is the available pinned developer validation environment; the oracle is not part of runtime request handling.
### Unresolved Issues
- Existing repository-wide typecheck/build baseline remains for the owning tasks; no Admin compiler or discovery-slice diagnostics remain.
### Architectural Concerns
None

## Architect Review

### Review Status
Changes Requested

### Review Notes
Attempt 3 satisfies the complete Attempt 2 correction contract. The production Admin compiler is now executed by the Dev MCP oracle through the bounded `vite-node` bridge, mapped enum/scalar/object/list compatibility is fail-closed for the requested cases, the Storefront synchronization result remains intact, `lib/discovery/schema.ts` is conflict-marker clean, and the committed Admin artifact still hashes exactly to the recorded provenance. These corrections are accepted and MUST NOT be reworked.

One remaining R2 contract defect was identified during Attempt 3 review: `validateMappedArguments()` still requires a mapping for every used GraphQL variable. R2 only requires a mapping for a **non-null variable that has no GraphQL default**. A nullable variable or a variable with a GraphQL default is allowed to be omitted from `execution.variables`. The current compiler discards variable-default metadata and therefore rejects valid definitions that rely on GraphQL optional/default semantics. The same compatibility boundary also rejects a nullable input-schema branch (`type: ['string', 'null']`) for a nullable GraphQL variable. Attempt 4 is limited to the deterministic corrections below.

#### CR-1 — preserve mapping-required metadata from the GraphQL variable definition

Files:
- `lib/discovery/admin-compiler.ts`
- `tests/admin-graphql-compiler.test.ts`

Required implementation:

1. Replace the current `Map<string, SchemaType>` variable metadata with a bounded structure that records, for each **used** variable:
   - the schema-backed expected `SchemaType`; and
   - `mappingRequired: boolean`.
2. Compute `mappingRequired` from the GraphQL variable definition itself, not from the argument type:

```text
mappingRequired =
  variableDefinition.type.kind === 'NonNullType'
  AND variableDefinition.defaultValue === undefined
```

3. Preserve the existing rules that every declared variable is used and every used variable is declared/type-compatible with the pinned Admin schema.
4. In `validateMappedArguments(candidate)`:
   - if a known variable has no mapping and `mappingRequired === true`, return `false`;
   - if a known variable has no mapping and `mappingRequired === false`, continue without failure;
   - if a mapping is present, validate it exactly through the existing input/literal compatibility rules;
   - reject every mapping key that is not one of the compiled operation variables.
5. Do not synthesize a mapping or mutate the GraphQL document. Missing optional/defaulted variables are intentionally left absent so GraphQL can apply null/default semantics at execution time.

Required focused regressions:

```text
query Products($query: String) { ... query: $query ... }
execution.variables = {}
-> validateMappedArguments = true

query Products($query: String! = "tag:summer") { ... query: $query ... }
execution.variables = {}
-> validateMappedArguments = true

query Products($query: String!) { ... query: $query ... }
execution.variables = {}
-> validateMappedArguments = false
```

#### CR-2 — permit `null` only when the GraphQL variable type is nullable

Files:
- `lib/discovery/admin-compiler.ts`
- `tests/admin-graphql-compiler.test.ts`

Required `sameInputType()` semantics:

1. If `expected.kind === 'NON_NULL'`, any input schema that admits `null` MUST return `false`; otherwise recurse into `expected.ofType`.
2. If the input schema type is a union/array, **every admitted branch** must be compatible.
3. A branch whose schema type is exactly `null` is compatible only when the current GraphQL `expected` type is nullable (`expected.kind !== 'NON_NULL'`).
4. Preserve all Attempt 3 enum/scalar/list/input-object checks unchanged for the non-null branches.

Required focused regressions:

```text
$query: String
inputSchema.query.type = ['string', 'null']
with variables.query.input = 'query'
-> true

$query: String!
inputSchema.query.type = ['string', 'null']
with variables.query.input = 'query'
-> false
```

#### CR-3 — preserve all accepted Attempt 3 boundaries

Do not modify these accepted areas except for imports/types mechanically required by CR-1/CR-2:
- `scripts/validate-shopify-admin-oracle.mjs`;
- `scripts/validate-shopify-admin-local.ts`;
- Storefront compiler/artifact behavior;
- explicit `storefront-graphql` / `admin-graphql` discovery dispatch;
- Admin artifact/provenance bytes/hash;
- query-only, field/depth/cost/pagination/result-path/result-schema admission rules.

### Reviewed Files
- `lib/discovery/admin-compiler.ts`
- `scripts/validate-shopify-admin-oracle.mjs`
- `scripts/validate-shopify-admin-local.ts`
- `tests/admin-graphql-compiler.test.ts`
- `tests/discovery-route.test.ts`
- `lib/discovery/schema.ts`
- `lib/discovery/artifacts/admin-2026-07.provenance.json`
- `docs/decisions/commerce/ARCH-021/COMMERCE-018-implement-shopify-admin-graphql-compiler.md`

### Validation Reviewed
Accepted from Attempt 3:
- `npm run test:arch021-shopify-admin-compiler`: 2 files / 20 tests passed;
- `npm run validate:arch021-shopify-admin-oracle`: all five bounded fixtures passed with local verdicts obtained from the production compiler via `vite-node`;
- exact targeted ESLint command: passed;
- `git diff --check`: passed;
- implementation branch pushed at `48d6ab0`; parent report pushed at `6f943702`; worktrees reported clean/synchronized.

The review archive does not contain installed runtime dependencies, so the focused commands could not be independently rerun inside this review environment. Source inspection confirms the submitted Attempt 3 corrections and provenance hash.

Attempt 4 MUST run exactly:

```bash
npm run test:arch021-shopify-admin-compiler
npm run validate:arch021-shopify-admin-oracle
npm exec eslint \
  lib/discovery/admin-compiler.ts \
  lib/discovery/schema.ts \
  lib/discovery/service.ts \
  app/api/studio/discovery/route.ts \
  scripts/sync-shopify-admin-schema.mjs \
  scripts/validate-shopify-admin-oracle.mjs \
  scripts/validate-shopify-admin-local.ts \
  tests/admin-graphql-compiler.test.ts \
  tests/discovery-route.test.ts
git diff --check
```

The focused Admin compiler suite MUST include all CR-1/CR-2 regressions above. The Dev MCP oracle fixtures and production-compiler bridge must remain passing and unchanged unless a mechanical import/type update is required.

### Architecture Conformance
Partial. Attempt 3 satisfies the prior oracle and fail-closed enum/scalar compatibility corrections and preserves R1, R3-R8. R2 remains incomplete only for GraphQL variables whose mapping is optional because the variable is nullable or has a GraphQL default, and for nullable input-schema union compatibility.

### Follow-up
Return the SAME task through `/moda-task ARCH-021-COMMERCE-018`. Preserve `attempt: 3`; the next authorized claim becomes Attempt 4. Implement only CR-1 and CR-2, run the exact validation commands above, update the Completion Report with final implementation/report commits and worktree synchronization evidence, set the task to `review`, and STOP. Do not begin COMMERCE-024.

## Developer Override

### Reopen Decision

This task was explicitly reopened by the developer on 2026-09-25. The prior
review remains historical; the task is returned to `ready` for a new execution
attempt without incrementing `attempt`.

### Previous Accepted Attempt

The prior implementation attempt was attempt 1, recorded as `review` with
implementation commit `db18555446f0c8f3a9601397941451bdb20b3714`.

### Lifecycle Transition

- `status: ready`
- `executor: null`
- `claimed_at: null`
- `attempt: 1`

### Downstream Eligibility

`ARCH-021-COMMERCE-024` remains `pending` because this task is no longer in a
complete state. No downstream status transition was required.
