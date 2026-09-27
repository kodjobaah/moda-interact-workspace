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
status: complete
priority: 72
executor: null
claimed_at: null
attempt: 2
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

GraphQL field-merging semantics are part of the exact selected response shape. A
validated query may repeat the same response key when GraphQL considers those field
selections merge-compatible (same underlying field/arguments with compatible
sub-selections). Derivation must recursively merge those compatible selections
rather than rejecting them merely because each occurrence contributes a different
subset of child fields.

Do not use last-write-wins and do not merge semantically conflicting response
keys. `compileDocument()` already runs GraphQL semantic validation; incompatible
field merges must continue to fail through that validation boundary.

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
- [x] Merge compatible repeated GraphQL response-key selections recursively instead of rejecting complementary selected shapes.
- [x] Add direct regressions for GraphQL field merging and real pinned-schema nullable-list rejection.

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
- [x] A valid repeated response-key selection derives the same canonical result schema as the equivalent single merged GraphQL selection.
- [x] A real pinned Admin list with nullable elements fails derivation with `UNREPRESENTABLE_NULLABLE_LIST`.

## Validation

- [x] `npx vitest run tests/admin-result-contract.test.ts tests/admin-graphql-compiler.test.ts tests/discovery-route.test.ts tests/shopify-admin-authoring-validation.test.ts --reporter=verbose`
- [x] targeted ESLint for every Attempt 2 changed source/test file
- [x] `npm run typecheck` (unrelated repository diagnostics remain; zero C062-owned diagnostics)
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to review, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Keep provider execution out of this task. The purpose is to create a deterministic compiler-owned capability that UI and runtime can independently consume.

Do not broaden `CommerceResultSchema` to arbitrary JSON Schema unless the accepted Admin selection genuinely cannot be represented without a narrowly justified grammar change.

## Completion Report

### Status

Attempt 1: submitted for Architect Review. Attempt 2: Ready for Review.

### Files Changed

- `moda-interact-commerce/lib/discovery/admin-compiler.ts`
- `moda-interact-commerce/src/commerce/tool-definition/result-schema.ts`
- `moda-interact-commerce/src/commerce/tool-authoring/admin-validation.ts`
- `moda-interact-commerce/src/studio/tools/admin-validation-server-actions.ts`
- `moda-interact-commerce/tests/admin-result-contract.test.ts`
- `moda-interact-commerce/tests/shopify-admin-authoring-validation.test.ts`

Additional Attempt 2 files:

- `moda-interact-commerce/lib/discovery/admin-compiler.ts`
- `moda-interact-commerce/tests/admin-result-contract.test.ts`

### Work Completed

- Added `deriveAdminResultContract`, which reuses the pinned Admin schema/document validation and follows response aliases and `resultPath` without provider I/O.
- Added explicit JSON-serialized Admin scalar mappings using the pinned 2026-07 artifact descriptions. Strings are bounded to 4096 characters; unsupported JSON/unknown output scalars fail with bounded actionable issues.
- Derived object required/optional properties from GraphQL non-null wrappers. Bounded connection `nodes`/`edges` arrays use the query's literal `first` argument; unrelated, unbounded lists and nullable/nested-list elements are rejected.
- Added nullable-output normalization that omits null optional object properties and reports null required properties, plus deterministic canonical schema serialization with sorted object keys and required lists.
- Exposed an input-bounded authoring derivation service and authenticated platform-admin Server Action. The action returns only the derived contract/issues and performs no durable writes or provider calls.
- Corrected existing Admin compiler type-kind detection so valid pinned-schema scalars such as `UnsignedInt64` are not mistaken for object types during query validation.

Attempt 2 — Architect Review corrections:

- Implemented Finding 1 in `lib/discovery/admin-compiler.ts` and `tests/admin-result-contract.test.ts`: after `compileDocument()` performs GraphQL semantic validation, recursively merge repeated response-key selection sets before generating output shapes. Complementary object fields and nested selections are unioned, arrays retain the same proven bound and recursively merged item schema, and required child keys are combined. Repeated scalar selections collapse to one property. Distinct underlying fields and conflicting selected shapes are not unioned; semantic conflicts continue to return `GRAPHQL_VALIDATION`.
- Added the exact aliased repeated-`nodes` regression and proved its canonical schema equals the equivalent single merged selection. Exact schema assertion verifies only `id` and `title` are present and both are required; alias `items` is retained in the query path.
- Implemented Finding 2 in `lib/discovery/admin-compiler.ts` and `tests/admin-result-contract.test.ts`: a literal `QueryRoot.nodes(ids: [...])` query establishes its truthful maximum result count when the list contains 1–20 IDs, allowing the pinned `[Node]!` output to reach the existing nullable-list guard. The test uses the real pinned `QueryRoot.nodes` and `Node.id`, and asserts `UNREPRESENTABLE_NULLABLE_LIST`.
- Attempt 2 implementation commit `622add6` is pushed to `task/ARCH-021-COMMERCE-062`.

### Validation Results

- `npx vitest run tests/admin-result-contract.test.ts tests/admin-graphql-compiler.test.ts tests/discovery-route.test.ts tests/shopify-admin-authoring-validation.test.ts`: passed, 39 tests.
- Targeted ESLint across all six changed files: passed with no output/errors.
- `git diff --check`: passed.
- `npx tsc --noEmit --pretty false`: repository-wide check remains blocked by 252 diagnostics in unrelated files (including missing preview module imports and Prisma client types); no diagnostics referenced C062-changed files.

Attempt 2:

- `npx vitest run tests/admin-result-contract.test.ts tests/admin-graphql-compiler.test.ts tests/discovery-route.test.ts tests/shopify-admin-authoring-validation.test.ts --reporter=verbose` — 4 files, 42 tests passed.
- Targeted ESLint on `lib/discovery/admin-compiler.ts` and `tests/admin-result-contract.test.ts` passed.
- `npm run typecheck` completed with the existing repository-wide failures: 260 diagnostics in 28 files. Neither Attempt 2 changed file appears in the diagnostics; changed-file editor TypeScript diagnostics report no errors for either file.
- `git diff --check` passed.

### Deviations

None. No provider execution, persistence changes, cross-repository contracts, or UI changes were added.

### Assumptions

- The pinned Admin 2026-07 introspection descriptions are authoritative for scalar JSON serialization; unsupported JSON scalar output remains rejected because the Commerce result grammar has no general JSON value node.

### Unresolved Issues

- Repository-wide TypeScript validation remains red on the unrelated diagnostics noted above; the changed files had no reported TypeScript diagnostics.

### Architectural Concerns

None.

### Attempt 2 Launcher Evidence

Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-062` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-062`, both on `task/ARCH-021-COMMERCE-062`. Shared workspace checkout switched/mutated for task work: no. Shared implementation checkout switched/mutated for task work: no. Another task worktree reused: no.

Start synchronization from the successful preparation packet: parent remote task branch fast-forwarded `not-needed`; parent `origin/main` incorporated `already-current`; implementation remote task branch fast-forwarded `not-needed`; implementation `origin/main` incorporated `already-current`. Parent start HEAD `a481e3e757a5c0539b6608e665880db482b718fd`; implementation start HEAD `368de55c3b05e5d5fa3cb98e3f3bfae5dbe38e0d`.

Recursive implementation submodules: sync passed; update/init passed; `database` initialized at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`. Attempt 2 launcher claim commit `d6e3b4c3b6d9939defcfc24a2ecba09ada2414d9`.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 satisfies both Attempt 1 correction items and is accepted.

The derivation path now preserves GraphQL field-merging semantics after the existing semantic-validation boundary. Compatible repeated response keys are recursively merged without last-write-wins behavior: repeated scalar selections collapse to one property, object child selections are unioned recursively with required keys combined, and repeated arrays preserve the same proven bound while recursively merging their item schemas. Incompatible field/argument selections continue to fail through GraphQL semantic validation rather than being unioned by Commerce.

The exact repeated aliased `nodes` regression proves that two complementary `items: nodes` selections derive the same canonical Commerce result schema as the equivalent single merged selection, preserving alias `items`, including only the selected `id` and `title` fields, and retaining the query-proven `maxItems: 2` bound.

The second correction is also complete. A literal `QueryRoot.nodes(ids: [...])` selection now derives a truthful finite maximum from the 1-20 literal IDs supplied to the real pinned Admin `2026-07` field, allowing its actual `[Node]!` nullable-element type to reach the existing representability guard. The focused regression therefore returns `UNREPRESENTABLE_NULLABLE_LIST` without altering the pinned schema artifact or relaxing the Commerce result grammar.

The rest of the C062 architecture remains conformant: derivation is pure/non-provider; aliases and exact selected shape remain authoritative; scalar serialization is explicit and bounded; GraphQL nullability maps to required/optional Commerce properties; nullable-output normalization remains pure; unbounded or otherwise unrepresentable list/scalar shapes fail deterministically; canonical schema equality remains deterministic; and the authenticated authoring boundary performs no Tool persistence or Shopify provider I/O.

COMMERCE-060 is already Complete. With COMMERCE-062 now accepted Complete, both dependencies of COMMERCE-070 are satisfied, so COMMERCE-070 is promoted from Pending to Ready. COMMERCE-065 remains Pending because its other dependency, COMMERCE-064, is Ready but not Complete.

### Reviewed Files

- `moda-interact-commerce/lib/discovery/admin-compiler.ts`
- `moda-interact-commerce/tests/admin-result-contract.test.ts`
- C062 Completion Report and prior Architect Review
- `docs/decisions/commerce/ARCH-021/COMMERCE-070-enforce-shopify-admin-result-contract-runtime.md`
- Commerce ARCH-021 task index
- ARCH-021 parent architecture execution tables/change history

### Validation Reviewed

Submitted/recorded Attempt 2 validation:

- required four-file regression packet: 42/42 tests passed;
- targeted ESLint on the two Attempt 2 changed files: passed;
- `npm run typecheck`: repository-wide check remains red with 260 diagnostics across 28 unrelated files, with zero diagnostics in the two C062 Attempt 2 changed files;
- changed-file editor TypeScript diagnostics: clean;
- `git diff --check`: passed.

Source inspection confirms the required repeated-field merge and real pinned nullable-list regressions exercise the correction contract. The submitted archive contains no installed dependencies, so the Vitest/ESLint commands were not independently rerun in this review environment; the validation results and clean pushed worktree state are recorded from the Completion Report/submission.

### Architecture Conformance

Conformant.

- GraphQL semantic validation remains authoritative for conflicting response keys/arguments.
- Compatible repeated response keys derive one exact canonical Commerce output shape.
- Real pinned Admin list nullability is preserved rather than guessed away.
- No provider execution, React/UI change, persistence change, cross-repository contract, or schema-artifact mutation was introduced.

### Follow-up

None for COMMERCE-062.

Task is architect-accepted Complete at Attempt 2. ARCH-021-COMMERCE-070 is promoted to Ready because ARCH-021-COMMERCE-060 and ARCH-021-COMMERCE-062 are both Complete. ARCH-021-COMMERCE-065 remains Pending on ARCH-021-COMMERCE-064.
