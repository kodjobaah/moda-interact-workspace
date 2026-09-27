---
id: ARCH-021-COMMERCE-062
architecture_id: ARCH-021
title: Derive Shopify Admin result contracts
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 72
executor: copilot
claimed_at: 2026-09-27T14:19:22Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-018
enables:
  - ARCH-021-COMMERCE-065
  - ARCH-021-COMMERCE-070
created: 2026-09-27
updated: 2026-09-27
---

# Derive Shopify Admin result contracts

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add a pure/non-provider Shopify Admin compiler capability that derives the canonical Commerce `resultSchema` and normalization semantics from a validated Admin GraphQL document plus `resultPath`, so Shopify authors no longer duplicate the selected response schema manually and later UI/runtime tasks consume the same deterministic contract.

## Context

The existing Admin compiler proves that `resultPath` points into the selected GraphQL shape and checks a separately authored `resultSchema` for compatibility. The New Tool UI therefore asks the author to duplicate information already known by the pinned Admin schema and the GraphQL selection.

A direct GraphQL-to-Commerce mapping is not trivial because the current Commerce result schema deliberately has no general `null` union. Shopify GraphQL fields may be nullable. This task defines the canonical derivation/normalization rules as pure compiler-domain behavior without changing provider execution.

The agreed rule is:

```text
GraphQL non-null object field      -> required Commerce property
GraphQL nullable object field      -> optional Commerce property
nullable object field returns null -> omit that optional property during normalization
selected root null                 -> NOT_FOUND at execution integration
required/non-null field is null    -> invalid provider data at execution integration
unrepresentable nullable/list/scalar shape -> deterministic derivation rejection
```

## Scope

Expected implementation areas include:

```text
lib/discovery/admin-compiler.ts
src/commerce/tool-definition/result-schema.ts
src/commerce/tool-authoring/admin-validation.ts
focused pure Admin result-contract/normalization module if useful
Admin authoring Server Action/service for non-mutating derivation if that boundary belongs here

tests/admin-graphql-compiler.test.ts
tests/shopify-admin-authoring-validation.test.ts
new focused Admin result-contract tests
```

## Out of Scope

- Shopify provider/network execution; COMMERCE-060 owns Admin execution and COMMERCE-070 owns integration with this derived contract.
- React Request/Response UI changes; COMMERCE-065 owns them.
- Explore Shopify UI.
- External HTTP result-schema behavior.
- Result Template UI.
- Adding a separately persisted `ToolResultContract`.
- General-purpose nullable JSON Schema support across all Commerce result processing unless strictly required by the pure Admin derivation helper.
- Shopify mutations.

## Requirements

### R1 — derive from the validated Admin query

Add one canonical derivation boundary that consumes the accepted Admin schema identity/document/operation and `resultPath` and produces the Commerce-owned `CommerceResultSchema` that will be persisted as `execution.resultSchema`.

The derivation API performs no provider I/O and no durable writes.

Do not require callers to author a second independent response schema.

### R2 — preserve aliases and exact selected shape

Derivation must follow the actual selected GraphQL response keys, including aliases, and must not expose unselected fields.

`resultPath` resolves against response keys exactly as runtime selection does.

### R3 — deterministic scalar mapping

Maintain one explicit Admin GraphQL output-scalar mapping whose JSON representation matches Shopify's actual GraphQL serialization and the Commerce result schema.

Do not infer primitive types merely from scalar names. Unsupported/unrepresentable scalars produce actionable derivation issues.

Bounded strings receive a canonical maximum length; no unbounded Commerce strings are generated.

### R4 — deterministic nullability mapping

For object properties:

```text
GraphQL NonNull(T) -> property appears in Commerce required[]
GraphQL nullable T -> property exists in properties but not required[]
```

Expose/reuse a pure normalization helper or equivalent compiler-owned semantics so later runtime integration can omit `null` optional object properties before Commerce result-schema validation.

The helper must reject `null` for a required/non-null property rather than silently dropping it.

Do not represent GraphQL nullable values as a made-up Commerce primitive type.

### R5 — arrays must remain truthful and bounded

Derive an array only when the selected GraphQL field has a truthful Commerce representation and a bounded maximum item count can be established from the accepted query/compiler contract.

Do not fabricate `maxItems` from a global constant when the query does not establish that bound.

Nullable list elements or nested list shapes that the current Commerce result grammar cannot represent safely must fail derivation deterministically.

### R6 — selected root must be representable as canonical values

The selected `resultPath` must derive a canonical result schema suitable for the Tool's `data.values` boundary. Unsupported root shapes return bounded authoring/compiler issues rather than a guessed schema.

### R7 — canonical equality is available for later runtime enforcement

Expose a deterministic/canonical representation suitable for COMMERCE-070 to prove that the persisted `execution.resultSchema` exactly matches the schema derived from the immutable GraphQL definition and `resultPath`.

Do not persist a second hidden result contract.

### R8 — non-mutating authoring use

Any server/service action exposed for UI consumption returns the derived result contract/issues only. It must not save the Tool, create a ToolRevision, mutate a DRAFT or perform Shopify provider I/O.

## Work Items

- [x] Add canonical Admin GraphQL-selection -> `CommerceResultSchema` derivation.
- [x] Map aliases, object fields, scalars and bounded arrays deterministically.
- [x] Encode GraphQL nullability through required/optional Commerce properties.
- [x] Add pure nullable-output normalization semantics/helper for later runtime integration.
- [x] Add deterministic canonical equality/fingerprint behavior for a derived schema.
- [x] Expose a non-mutating authoring derivation boundary through an authenticated Server Action.
- [x] Add focused derivation, alias, nullability, list-bound and unsupported-scalar tests.

## Interfaces / Contracts

Consumes:

```text
SHOPIFY_ADMIN_GRAPHQL contract from COMMERCE-018
pinned Admin 2026-07 schema + schema hash
createAdminCommerceCompiler
CommerceResultSchema
```

Produces a repository-local pure capability conceptually equivalent to:

```text
deriveAdminResultContract({ document, operationName, resultPath, schemaIdentity })
  -> { resultSchema, normalization semantics } | bounded issues
```

No new cross-repository contract is introduced.

## Dependencies

- `ARCH-021-COMMERCE-018`

## Enables

- `ARCH-021-COMMERCE-065`
- `ARCH-021-COMMERCE-070`

## Acceptance Criteria

- [x] A valid Admin query/resultPath deterministically derives one canonical Commerce result schema without provider I/O.
- [x] GraphQL response aliases become the canonical result keys.
- [x] Unselected Shopify fields never appear in the result contract.
- [x] Non-null object fields are required Commerce properties.
- [x] Nullable object fields are optional Commerce properties.
- [x] Pure normalization semantics omit `null` optional object fields and reject `null` required fields.
- [x] Selected list shapes are emitted only when a truthful finite `maxItems` is established.
- [x] Unrepresentable nullable/list/scalar shapes return actionable derivation issues rather than guessed schemas.
- [x] Generated strings are bounded.
- [x] Canonical equality/fingerprint behavior is deterministic across equivalent derivations.
- [x] Authoring derivation creates no Tool/ToolRevision and performs no Shopify provider request.
- [x] Existing Admin compiler validation remains green.

## Validation

- [x] focused Admin result-contract derivation tests
- [x] Admin compiler regression tests
- [x] Admin authoring-validation regression tests where affected
- [x] targeted lint/type diagnostics for changed files
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Keep provider execution out of this task. The purpose is to create a deterministic compiler-owned capability that UI and runtime can independently consume.

Do not broaden `CommerceResultSchema` to arbitrary JSON Schema unless the accepted Admin selection genuinely cannot be represented without a narrowly justified grammar change.

## Completion Report

### Status

Implemented; submitted for Architect Review.

### Files Changed

- `moda-interact-commerce/lib/discovery/admin-compiler.ts`
- `moda-interact-commerce/src/commerce/tool-definition/result-schema.ts`
- `moda-interact-commerce/src/commerce/tool-authoring/admin-validation.ts`
- `moda-interact-commerce/src/studio/tools/admin-validation-server-actions.ts`
- `moda-interact-commerce/tests/admin-result-contract.test.ts`
- `moda-interact-commerce/tests/shopify-admin-authoring-validation.test.ts`

### Work Completed

- Added `deriveAdminResultContract`, which reuses the pinned Admin schema/document validation and follows response aliases and `resultPath` without provider I/O.
- Added explicit JSON-serialized Admin scalar mappings using the pinned 2026-07 artifact descriptions. Strings are bounded to 4096 characters; unsupported JSON/unknown output scalars fail with bounded actionable issues.
- Derived object required/optional properties from GraphQL non-null wrappers. Bounded connection `nodes`/`edges` arrays use the query's literal `first` argument; unrelated, unbounded lists and nullable/nested-list elements are rejected.
- Added nullable-output normalization that omits null optional object properties and reports null required properties, plus deterministic canonical schema serialization with sorted object keys and required lists.
- Exposed an input-bounded authoring derivation service and authenticated platform-admin Server Action. The action returns only the derived contract/issues and performs no durable writes or provider calls.
- Corrected existing Admin compiler type-kind detection so valid pinned-schema scalars such as `UnsignedInt64` are not mistaken for object types during query validation.

### Validation Results

- `npx vitest run tests/admin-result-contract.test.ts tests/admin-graphql-compiler.test.ts tests/discovery-route.test.ts tests/shopify-admin-authoring-validation.test.ts`: passed, 39 tests.
- Targeted ESLint across all six changed files: passed with no output/errors.
- `git diff --check`: passed.
- `npx tsc --noEmit --pretty false`: repository-wide check remains blocked by 252 diagnostics in unrelated files (including missing preview module imports and Prisma client types); no diagnostics referenced C062-changed files.

### Deviations

None. No provider execution, persistence changes, cross-repository contracts, or UI changes were added.

### Assumptions

- The pinned Admin 2026-07 introspection descriptions are authoritative for scalar JSON serialization; unsupported JSON scalar output remains rejected because the Commerce result grammar has no general JSON value node.

### Unresolved Issues

- Repository-wide TypeScript validation remains red on the unrelated diagnostics noted above; the changed files had no reported TypeScript diagnostics.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
