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
status: complete
priority: 35
executor: null
claimed_at: null
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

### Attempt 4 Completion Addendum

#### Status
Ready for Review

#### Correction Checklist
- CR-1 implemented in `lib/discovery/admin-compiler.ts`: compiled variable metadata now preserves the schema-backed expected type and whether the GraphQL variable is non-null without a default. Optional/defaulted variables may omit mappings; required variables still fail closed; unknown mapping keys remain rejected.
- CR-1 regressions added in `tests/admin-graphql-compiler.test.ts` for omitted nullable, omitted non-null-with-default, and omitted required non-null variables.
- CR-2 implemented in `lib/discovery/admin-compiler.ts`: nullable input-schema branches are accepted only for nullable GraphQL variables, while non-null variables reject any schema that admits `null`; all non-null branch compatibility checks remain unchanged.
- CR-2 regressions added in `tests/admin-graphql-compiler.test.ts` for nullable and non-null GraphQL variables mapped from `['string', 'null']`.
- CR-3 accepted Attempt 3 boundaries preserved: no changes to the oracle bridge/scripts, Storefront compiler or artifact, discovery dispatch, Admin artifact/provenance, or query safety limits.

#### Implementation Evidence
- Implementation commit: `a6df0f193606bd14d31d3a46989ad284a81a6b3c`.
- Implementation branch: `task/ARCH-021-COMMERCE-018`, local/remote parity at the implementation commit.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-018`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-018`.
- Launcher preparation evidence: claim commit `b73d2c1ea3915a8e52e1377cdf3a142d03e2ca95`; parent origin-main already current; implementation origin-main already current; task-branch fast-forward not needed; recursive submodule sync/update passed; database submodule at exact recorded commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Artifact integrity preserved: `admin-2026-07.json` SHA-256 remains `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`, matching `admin-2026-07.provenance.json`.

#### Attempt 4 Validation
- `npm run test:arch021-shopify-admin-compiler`: PASS, 2 files and 22 tests.
- `npm run validate:arch021-shopify-admin-oracle`: PASS; valid products, unknown field, unknown argument, mutation safety divergence, and wrong variable type all matched the expected local/upstream outcomes; local verdicts used the production compiler bridge.
- Exact architect-requested `npm exec eslint` command over all compiler/discovery/scripts/tests: PASS with no warnings or errors.
- `git diff --check`: PASS.
- Relevant `npm run test:arch021-commerce-tool-contract`: PASS, 1 file and 12 tests.
- Source audit: no network calls, credentials, authorization headers, or telemetry dependencies in the touched compiler/tests.
- `npm run typecheck`: repository baseline failure, 242 diagnostics across 19 unrelated files; no diagnostics were reported for the touched Admin compiler, discovery, route, scripts, or focused tests.
- Implementation worktree was clean after commit and push; no live Shopify request, credential execution, mutation, or out-of-scope UI/publication work was performed.

#### Attempt 4 Report State
The task is ready for Architect Review. No downstream task was started.

## Architect Review

### Review Status
Accepted

### Review Notes
Attempt 4 satisfies the complete remaining R2 correction contract. The compiler now preserves per-variable `mappingRequired` metadata from the GraphQL variable definition, permits omitted mappings for nullable variables and non-null variables with GraphQL defaults, still requires mappings for non-null variables without defaults, rejects unknown mapping keys, and preserves the accepted mapped input/literal compatibility rules. Nullable input-schema unions are accepted only for nullable GraphQL variables; non-null variables still reject any schema that admits `null`.

The previously accepted Attempt 2/3 boundaries remain intact: the Dev MCP oracle gets every local verdict from the production Admin compiler through the bounded `vite-node` bridge; mapped enum/scalar/object/list compatibility remains fail-closed; Storefront behavior and explicit `storefront-graphql` / `admin-graphql` discovery dispatch are unchanged; `lib/discovery/schema.ts` is conflict-marker clean; and the committed Admin 2026-07 artifact still matches its recorded SHA-256 provenance exactly.

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
- `npm run test:arch021-shopify-admin-compiler`: PASS, 2 files / 22 tests.
- Attempt 4 regressions prove omitted nullable variables are accepted, omitted non-null variables with GraphQL defaults are accepted, omitted required non-null variables are rejected, nullable input schemas are accepted for nullable GraphQL variables, and the same nullable schemas are rejected for non-null variables.
- `npm run validate:arch021-shopify-admin-oracle`: PASS, all five bounded fixtures; local verdicts use the production compiler bridge.
- `npm run test:arch021-commerce-tool-contract`: PASS, 1 file / 12 tests.
- Exact targeted ESLint command: PASS.
- Admin artifact/provenance SHA-256 verification: PASS.
- `git diff --check`: PASS.
- `npm run typecheck`: repository baseline remains non-zero with 242 unrelated diagnostics; zero task-owned diagnostics were reported.
- Implementation commit: `a6df0f193606bd14d31d3a46989ad284a81a6b3c`; parent report commit: `8d74e8b8`; implementation and parent worktrees reported clean and synchronized with their remotes.

### Architecture Conformance
Conformant. R1-R8 are satisfied for the bounded Shopify Admin GraphQL authoring compiler. Validation is local/artifact-backed at runtime, query-only safety is preserved, optional/defaulted GraphQL variables follow GraphQL semantics without weakening required-variable checks, and the Dev MCP remains development conformance evidence only.

### Follow-up
Mark `ARCH-021-COMMERCE-018` Complete. `ARCH-021-COMMERCE-024` remains Pending because `ARCH-021-COMMERCE-019` is still Ready rather than Complete. Do not start COMMERCE-024 from this acceptance.

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
