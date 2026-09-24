---
id: ARCH-021-COMMERCE-034
architecture_id: ARCH-021
title: Generate Storefront GraphQL from dynamic schema selections
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-033
enables:
  - ARCH-021-COMMERCE-035
created: 2026-09-24
updated: 2026-09-25
---

# Generate Storefront GraphQL from dynamic schema selections

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Compile the COMMERCE-033 schema-driven selection tree and real introspected field arguments into a deterministic Storefront GraphQL query that validates against the same pinned schema artifact before it can be applied to a Tool draft.

## Context

COMMERCE-032 makes the real pinned Storefront introspection artifact authoritative.

COMMERCE-033 makes recursive parent/child traversal and a nested selection tree authoritative.

The existing Explore builder currently extends GraphQL using:

```text
string path -> split(".") -> addPath(...)
```

which cannot truthfully model schema argument requirements and was coupled to the invalid synthetic `field.path` contract.

This task replaces that path-string query construction with schema-backed GraphQL AST generation/merge.

It must reuse the existing accepted Storefront compiler/validation boundary. It must not create a second GraphQL validator.

## Scope

Primary files:

```text
src/studio/discovery/storefront-query-builder.ts          # pure AST generator/merge logic
src/studio/discovery/storefront-schema-browser.tsx         # preserve C033 navigation/selection behavior
src/studio/discovery/storefront-argument-bindings.tsx      # new required selected-argument editor
src/studio/discovery/selection-tree.ts
components/studio-workspace.tsx                           # compose selection + argument bindings + validation
lib/discovery/storefront-input-compatibility.ts            # new client-safe shared compatibility helper
lib/discovery/compiler.ts                                  # reuse the same compatibility helper
tests/storefront-query-builder.test.ts
tests/storefront-argument-bindings.test.tsx                # new required
tests/storefront-schema-browser.test.tsx
tests/studio-workspace.test.tsx
tests/discovery.test.ts
package.json
```

Additional directly affected Tool-definition files may be changed only when required to consume the existing accepted `SHOPIFY_STOREFRONT_QUERY` contract.

## Out of Scope

- New Storefront execution semantics.
- Live Shopify calls.
- Store-specific schema introspection.
- Shopify Admin GraphQL.
- Fragments/directives.
- Mutations/subscriptions.
- Database changes.
- Shared/Background/Gateway changes.
- Replacing the accepted Storefront compiler.
- Changing publication rules.
- Removing historical Storefront Tool support.

## Requirements

### R1 — AST generation, not string concatenation

Generate/merge GraphQL using `graphql` AST utilities.

Do not construct the final query with string concatenation or dot-path splitting.

The generated document must remain:

```text
exactly one named query operation
no mutation
no subscription
no fragments
no directives
```

matching the accepted compiler contract.

### R2 — selection tree is authoritative for new selections

The builder consumes the COMMERCE-033 nested selection tree.

Every new generated selection must correspond to:

```text
real parent type
real field name
real return type
real schema argument metadata
```

from COMMERCE-032.

Do not accept arbitrary client-supplied field names that are absent from the normalized graph.

### R3 — dynamic argument bindings

For each selected field, render argument controls from that field's normalized schema metadata.

Support exactly these authoring binding kinds:

```text
INPUT_PROPERTY
LITERAL
```

`INPUT_PROPERTY`:

- selects one current top-level property from the Tool's persisted `inputSchema`;
- generates/reuses a GraphQL variable definition with the **exact schema argument type**;
- adds/updates `execution.variables` so the generated variable maps to that top-level input property;
- must fail visibly when the current inputSchema property is not compatible with the schema argument type under the accepted compiler.

`LITERAL`:

- is converted to a GraphQL AST value using the actual schema argument input type;
- scalar and enum literals must be type checked before candidate validation;
- unsupported literal input-object construction must be rejected explicitly rather than serialized heuristically.

Do not persist invocation values; `inputSchema` remains the CommerceAgent argument contract.

### R4 — required arguments fail closed

A selected field with an unresolved non-null schema argument must make the candidate invalid before `Use in tool`.

Display the exact missing argument name/type.

Do not invent a default value.

### R5 — bounded connection pagination

Preserve the accepted compiler policy for schema-backed connections.

When a selected field exposes connection pagination:

```text
first
last
```

the builder supports only a literal `first` value from `1` through `20` for this checkpoint.

Do not generate `last`.

Do not silently add a pagination value without showing it in the builder state/UI.

### R6 — merge with existing authored query safely

The Explore builder may extend an existing Storefront Tool query.

Use these exact merge rules:

1. parse the current `execution.document`;
2. require exactly one named query operation;
3. preserve unrelated existing selections, aliases and arguments;
4. for each builder-selected field:
   - if exactly one compatible existing field selection is present at that parent, merge descendants into it;
   - preserve its existing alias/arguments;
   - if no compatible selection exists, add the new field using builder argument bindings;
   - if more than one candidate for the same underlying field makes the parent ambiguous, return a bounded ambiguity error and do not mutate the document;
5. do not duplicate the same selected field merely because it is already present;
6. do not silently rewrite an existing argument binding.

The existing alias-preservation regression must remain supported.

### R7 — variable definition/mapping determinism

For an `INPUT_PROPERTY` binding:

- derive a GraphQL-safe variable name deterministically;
- identical input property + identical GraphQL type may reuse one variable;
- conflicting reuse with different GraphQL types must fail visibly;
- generated variable definitions must be ordered deterministically;
- generated `execution.variables` entries must be ordered/stable under existing serialization conventions;
- preserve unrelated existing variable definitions/mappings still used by preserved query selections.

No unused generated variable may remain.

### R8 — schema identity

The candidate Tool definition MUST use:

```text
apiVersion = COMMERCE-032 apiVersion
schemaHash = COMMERCE-032 schemaHash
```

Do not accept browser-supplied arbitrary schema hashes.

If the currently edited Tool references another schema identity, the builder must show a visible incompatibility and require rebuilding/revalidation against the pinned artifact.

### R9 — existing compiler is the final authority

After AST generation/merge:

1. construct the candidate `ToolDefinition`;
2. invoke the existing named `validateToolDefinition` Server Action;
3. enable `Use in tool` only after that exact candidate validates successfully;
4. any selection/argument/inputSchema/document change invalidates the previous validation token;
5. `Use in tool` applies the exact validated candidate and nothing else.

Do not duplicate `lib/discovery/compiler.ts` validation logic in React.

### R10 — resultPath safety

Preserve an existing valid `execution.resultPath`.

If the current resultPath no longer resolves in the generated document, validation must fail visibly; do not silently rewrite it.

When there is no existing resultPath and the generated query has exactly one unaliased root field, the builder may propose that response key but must display the value before application.

Do not guess across multiple roots.

### R11 — deterministic integrated regression

Using the **real pinned artifact/normalizer**, prove this traversal and generation:

```text
QueryRoot.product
  -> Product.priceRange
    -> ProductPriceRange.minVariantPrice
      -> MoneyV2.amount
```

with `product.handle` explicitly bound to a top-level Tool input property.

The C032 artifact shows `QueryRoot.product(handle: String, id: ID)` as optional arguments, so this binding proves dynamic input-property mapping but MUST NOT be treated as a required Shopify argument.

Separately use the real required root:

```text
QueryRoot.productByHandle(handle: String!)
```

to prove that an unresolved required argument blocks the candidate/application path.

The resulting nested `product` candidate must contain a valid named query and pass the existing Storefront compiler.

Also prove:

```text
selecting amount does not select sibling fields
missing required root argument blocks application
wrong inputSchema type blocks application
restricted customer root cannot be selected
connection first=1..20 validates
connection first outside 1..20 is rejected
existing aliased product selection is merged without a duplicate product root
ambiguous duplicate existing roots are rejected explicitly
schema hash comes from the pinned artifact
```

### R12 — remove legacy path-string builder

Remove the obsolete path-string query construction from `components/studio-workspace.tsx`, including the old:

```text
addPath(...)
buildQueryDefinition(... selectedPaths: string[])
```

or equivalent path-splitting implementation.

No production Storefront query generation may depend on `path.split(".")`.

## Work Items

- [x] Add pure Storefront AST query builder.
- [x] Add schema-driven argument-binding state/controls.
- [x] Add inputSchema-property variable mapping.
- [x] Add bounded literal argument generation.
- [x] Add connection-first handling.
- [x] Merge selections safely into existing query AST.
- [x] Preserve aliases/unrelated existing selections.
- [x] Make pinned schema identity authoritative.
- [x] Wire exact candidate through existing `validateToolDefinition`.
- [x] Remove old dot-path query-generation code.
- [x] Add real-artifact integrated regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-032 normalized Storefront schema contract
ARCH-021-COMMERCE-033 Storefront selection tree
existing Commerce ToolDefinition / SHOPIFY_STOREFRONT_QUERY contract
existing Storefront compiler
```

Produces no new cross-service contract.

## Dependencies

- ARCH-021-COMMERCE-033

## Enables

- ARCH-021-COMMERCE-035

## Acceptance Criteria

- [x] GraphQL is generated/merged from real schema metadata and selection tree.
- [x] Required schema arguments cannot be bypassed.
- [x] Input-property variable mappings remain the Tool's persisted argument contract.
- [x] Connection pagination obeys existing bounded compiler policy.
- [x] Existing aliases/unrelated selections survive deterministic merge.
- [x] No dot-path split builder remains.
- [x] Candidate uses the pinned API version/schema hash.
- [x] `Use in tool` can apply only the exact candidate that passed existing server validation.
- [x] Real-artifact nested product regression passes.
- [x] No provider/network request occurs during schema authoring/validation.

## Validation

- [x] `npx vitest run tests/storefront-query-builder.test.ts tests/storefront-argument-bindings.test.tsx tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts --reporter=verbose`
- [x] Existing Storefront compiler/definition tests directly affected by generated queries pass.
- [x] Targeted ESLint for every changed source/test file.
- [x] `npm run typecheck` (unchanged unrelated baseline recorded; zero task-owned diagnostics).
- [x] Legacy path-string source audit:
  ```text
  rg -n "buildQueryDefinition|path\.split\("\\\."\)|selectedPaths" components src/studio
  ```
  expected: no legacy Storefront path-string builder matches.
- [x] Client artifact-boundary audit:
  ```text
  rg -n "storefrontSchemaHash|storefrontArtifact|storefrontSchema"     src/studio/discovery components
  ```
  expected: no runtime Storefront artifact/schema value import in client query-builder/UI code.
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP.

Do not start SYSTEM-TEST-001.

## Implementation Notes

Reuse the accepted Storefront compiler as the validation authority. This task builds authoring state/document AST; it does not create another compiler.

Do not add a live schema network dependency. Both generation and validation are pinned to the same committed real introspection artifact.

Do not broaden Storefront access or compiler limits merely to make a generated query validate.

## Completion Report

### Status

Ready for Review

### Files Changed

- `components/studio-workspace.tsx`
- `lib/discovery/compiler.ts`
- `lib/discovery/storefront-input-compatibility.ts`
- `src/studio/discovery/selection-tree.ts`
- `src/studio/discovery/storefront-argument-bindings.tsx`
- `src/studio/discovery/storefront-query-builder.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/storefront-argument-bindings.test.tsx`
- `tests/storefront-query-builder.test.ts`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-services.test.ts`
- `tests/studio-workspace.test.tsx`
- Attempt 2 implementation commit: `9e180cc2956d50f064825f3e13a2cc72115b7782`
- Attempt 3 implementation commit: `cf3c75b19760329914cfeff41c7056a9e068d18c`

### Work Completed

Attempt 1 established the AST/merge foundation. Attempt 2 added production schema-driven argument-binding state and controls; shared client-safe inputSchema compatibility with the accepted compiler; typed scalar/enum literal generation with explicit unsupported input-object/list rejection; bounded connection `first` handling; authoritative C032 API-version/schema-hash identity; generated-variable collision protection; real compiler-backed validation regressions; and result-path/alias/selection merge safety. Attempt 3 corrected LIST wrapper detection and the first-only/last connection UI policy, removed the task-owned TS2367, and added the required exact-candidate and connected Studio regressions. The legacy dot-path builder remains removed.

### Validation Results

Focused validation passed: `npx vitest run tests/storefront-query-builder.test.ts tests/storefront-argument-bindings.test.tsx tests/storefront-schema-browser.test.tsx tests/studio-workspace.test.tsx tests/discovery.test.ts tests/studio-services.test.ts --reporter=verbose` completed with 6 test files and 70 tests passing. This includes the exact generated nested product candidate through the real compiler, connection `first=1` and `first=20` through the real compiler, LIST/first-only/last UI behavior, fail-closed required/wrong-input workflows, exact schema-identity application, and invalid result-path behavior. The directly affected Storefront definition/compiler tests passed; no provider or network request was used. Targeted ESLint over the five Attempt 3-owned files passed with zero errors/warnings.

The legacy path-string source audit passed: no `buildQueryDefinition`, `path.split(".")`, or `selectedPaths` matches remain in `components` or `src/studio`. The client artifact-boundary audit passed: no runtime Storefront artifact/schema value import remains in the client query-builder/UI surface. `git diff --check` passed.

`npm run typecheck` exits non-zero with the unchanged documented repository baseline, including missing preview modules, Prisma generated-type drift, and existing implicit-any/strictness diagnostics outside the C034-owned files. No diagnostics remain in `components/studio-workspace.tsx`, `src/studio/discovery/storefront-argument-bindings.tsx`, `src/studio/discovery/storefront-query-builder.ts`, or the changed C034 tests; the Attempt 2-owned TS2367 is absent.

Launcher topology evidence: implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-034` and parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-034` both use `task/ARCH-021-COMMERCE-034`. The implementation worktree is clean and `HEAD` equals `origin/task/ARCH-021-COMMERCE-034` at `cf3c75b6a8c5dc003164e9d3aaf1e54b4ecf2c58`. Recursive submodule evidence: `database` at `0a8d3b9feade69690b6c1e33aeda051ea588bd45` (`heads/main`). No ARCH-021-COMMERCE-035 worktree, branch, or implementation was started.

### Deviations

The full repository typecheck remains non-zero only because of unchanged documented baseline diagnostics. Focused tests, targeted ESLint, both source audits, and `git diff --check` passed. No live provider/network request was added or used.

### Assumptions

The accepted Storefront compiler and COMMERCE-032 pinned artifact remain the validation authority. The implementation commit is pushed to `origin/task/ARCH-021-COMMERCE-034`.

### Unresolved Issues

Repository-wide typecheck remains non-zero on unrelated baseline diagnostics; zero task-owned diagnostics are present.

### Architectural Concerns

None identified within the bounded task scope.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 completes most of the substantive C034 authoring architecture.

Accepted in substance:

- production Studio now owns real `StorefrontArgumentBindings` state;
- a dedicated `storefront-argument-bindings.tsx` component renders selected schema arguments;
- candidate construction consumes current Tool definition + C033 selection tree + bindings + C032 schema identity;
- `INPUT_PROPERTY` mappings use the shared client-safe compatibility helper also used by the accepted compiler;
- query generation remains AST-based;
- required arguments fail before a candidate can be validated;
- schema identity now comes from the C032 `SchemaPage`;
- runtime client code no longer imports the pinned schema/hash artifact value;
- deterministic variable collisions are rejected rather than silently rewriting existing mappings;
- the in-memory Studio validator now delegates to the real Commerce compiler;
- connection candidate generation enforces literal `first` 1..20 and rejects `last`;
- exact validation-token/hash handling remains in place before `Use in tool`.

Attempt 2 is not acceptable yet for two source-code reasons and several explicit
regression-evidence gaps.

#### Finding 1 — task-owned `TS2367` is a required validation failure and reveals a real LIST-argument UI bug

The task contract explicitly permits a non-zero repository typecheck only when:

```text
all diagnostics are unchanged unrelated baseline
zero task-owned diagnostics
```

The Attempt 2 Completion Report records one task-owned error:

```text
src/studio/discovery/storefront-argument-bindings.tsx:62
TS2367
```

The relevant code is:

```ts
const named = namedType(argument.typeRef);
const literalUnsupported =
  named.kind === "INPUT_OBJECT" ||
  named.kind === "LIST";
```

`namedType()` recursively unwraps both `NON_NULL` and `LIST`, so `named.kind` can
never be `"LIST"`. TypeScript is correct to flag the comparison.

This is not merely a typing nuisance. It means a real argument such as:

```text
QueryRoot.predictiveSearch(types: [PredictiveSearchType!])
```

is not recognized by the argument editor as a LIST literal. The UI can therefore
offer a scalar-looking literal editor for a binding type that C034 explicitly
requires to be rejected as unsupported literal authoring.

Attempt 3 must distinguish wrapper shape from named type.

A conformant implementation may add a small client-safe pure helper such as:

```ts
function isListType(type: StorefrontTypeRef): boolean {
  return type.kind === "LIST" ||
    (type.kind === "NON_NULL" && isListType(type.ofType));
}
```

and then use:

```ts
const literalUnsupported =
  isListType(argument.typeRef) ||
  named.kind === "INPUT_OBJECT";
```

Do not import runtime helpers from `storefront-artifact.ts` into this Client
Component, because that module owns the complete pinned JSON/provenance runtime
values. A type-only import remains acceptable.

The final UI must show the bounded existing guidance rather than a scalar editor:

```text
Use a Tool input property for <actual GraphQL type>.
```

for LIST and INPUT_OBJECT literal selection.

#### Finding 2 — `first`-only schema fields are incorrectly offered INPUT_PROPERTY authoring

The current argument editor decides that `first` is the special connection bound
only when the same field also exposes `last`:

```ts
const isFirst =
  argument.name === "first" &&
  node.arguments.some((candidate) => candidate.name === "last");
```

That does not match the accepted compiler policy.

The compiler treats a field as paginated whenever its schema exposes either:

```text
first
last
```

The real pinned C032 Storefront 2026-07 artifact contains five `first`-only
fields, including:

```text
Fulfillment.trackingInfo(first: Int)
Order.successfulFulfillments(first: Int)
Product.options(first: Int)
QueryRoot.productTags(first: Int!)
QueryRoot.productTypes(first: Int!)
```

Therefore the current UI incorrectly offers `Tool input` for those `first`
arguments, while candidate generation/compiler policy later rejects that binding.

Attempt 3 must make authoring parity exact.

For every selected argument named:

```text
first
```

the editor must use the fixed connection-bound behavior:

```text
source: Literal only
numeric control
min=1
max=20
no INPUT_PROPERTY option
```

Do not require a sibling `last` argument before applying that rule.

For an argument named:

```text
last
```

the normal authoring source selector must not permit creating a new binding.
Render a bounded read-only explanation such as:

```text
Only a literal first connection bound is supported.
```

The query builder must retain its current defensive rejection of a stale/manual
`last` binding.

#### Finding 3 — the required nested-product regression still does not validate the exact generated candidate

The current test:

```text
generates the real nested product price traversal ...
```

builds the required candidate with:

```text
product.handle -> INPUT_PROPERTY(handle)
```

but stops after inspecting the document/mapping.

A separate test validates a hand-authored nested query through
`InMemoryStudioServices`.

The Attempt 2 correction contract explicitly required the **exact generated
candidate** to pass the real accepted compiler.

Attempt 3 must change/add the regression so this exact value:

```ts
const generated =
  buildStorefrontQueryDefinition(...).definition;
```

is passed unchanged to:

```text
InMemoryStudioServices.validateToolDefinition()
```

(or the equivalent real `validateDefinition` path), and returns:

```text
valid: true
errors: []
```

Do not satisfy this with a separately hand-written query.

#### Finding 4 — `first = 20` is not currently proved through the real compiler

Attempt 2 validates the `first = 1` generated connection candidate through the
real compiler.

For:

```text
first = 20
```

the current test only proves the builder returns a Storefront execution kind.

The correction contract explicitly required both boundary values to validate via
the real compiler.

Attempt 3 must pass the exact generated `first = 20` candidate through the same
real compiler path and prove it is valid.

#### Finding 5 — required-argument / wrong-input fail-closed UI evidence is still missing

Builder-unit tests correctly prove:

```text
missing productByHandle.handle -> build error
wrong inputSchema type -> build error
```

but the explicit Attempt 2 regression contract also required the connected Studio
behavior:

```text
unbuildable candidate
  -> Validate does not invoke validateToolDefinition
  -> Use in tool cannot become enabled
```

Add a connected `StudioWorkspace` regression using the same named Server Action
boundary production imports.

Required case A:

```text
select productByHandle.title
leave handle unconfigured
click Validate
```

Prove:

```text
exact missing argument name/type is visible
services.validateToolDefinition is not invoked
Use in tool remains disabled
```

Required case B:

```text
current inputSchema.handle = integer
bind productByHandle.handle -> Tool input "handle"
click Validate
```

Prove:

```text
incompatibility is visible
services.validateToolDefinition is not invoked
Use in tool remains disabled
```

Do not add a test-only production port or callback.

#### Finding 6 — schema-identity exact-candidate application evidence is incomplete

The builder unit test proves:

```text
schemaIdentityChanged === true
candidate apiVersion/hash == C032 SchemaPage
```

and production UI contains the visible identity-change note.

The explicit correction contract also required proving that, in the connected
Studio flow:

```text
the exact rebuilt candidate is sent to validateToolDefinition
Use in tool remains disabled before that validation succeeds
Use in tool applies the exact validated candidate
```

Add a `StudioWorkspace` regression starting from a Tool whose Storefront
`schemaHash` is a different valid-looking 64-character hash.

Spy on the same fixture-backed named `validateToolDefinition` action.

Prove:

1. the identity-change note is visible;
2. before validation, `Use in tool` is disabled;
3. the validation call receives the rebuilt candidate with exactly:
   ```text
   execution.apiVersion = schema.apiVersion
   execution.schemaHash = schema.schemaHash
   ```
4. after success, `Use in tool` applies the same candidate definition that was
   validated.

Do not compare only the query string; compare the complete candidate definition
or a stable structural clone/hash of it.

#### Finding 7 — invalid `resultPath` connected behavior is not covered

The final builder correctly preserves the current `resultPath` and the real
compiler rejects an invalid path.

However, the explicit Attempt 2 regression:

```text
invalid current resultPath cannot enable Use in tool
```

is absent.

Add a connected Studio regression:

1. start with a valid Storefront Tool except for a current `resultPath` that does
   not resolve after the candidate query is built;
2. select a valid real schema field;
3. click Validate;
4. prove the real server/compiler validation error is visible;
5. prove `Use in tool` remains disabled.

Do not make the builder silently rewrite the invalid resultPath.

### Attempt 3 deterministic correction

Reclaim the same task as Attempt 3.

This is a bounded correction. Preserve the accepted AST merge, schema identity,
variable-collision and real-compiler architecture.

#### Source corrections

1. Fix the task-owned `TS2367`.
2. Correct LIST-vs-named-type detection in the argument editor.
3. Apply literal-only `first` UI behavior to all real `first` arguments,
   including first-only fields.
4. Prevent normal UI authoring of `last` while retaining builder-side stale/manual
   rejection.

No other production redesign is authorized unless the stronger regressions expose
a real defect.

#### Required focused regressions

Add/extend tests using the real C032 browse contract/artifact:

**LIST literal editor**

Use a real argument such as:

```text
QueryRoot.predictiveSearch.types: [PredictiveSearchType!]
```

Prove choosing Literal does not render a scalar literal input and displays the
bounded Tool-input guidance.

**First-only pagination UI**

Use:

```text
QueryRoot.productTags(first: Int!)
```

Prove:

```text
first source is fixed to Literal
no Tool input option exists
numeric input has min=1
numeric input has max=20
```

**Last UI**

Using a real field that exposes `last`, prove the editor does not offer a normal
binding source for `last` and displays the bounded first-only policy.

**Generated nested candidate**

Pass the exact generated:

```text
product(handle: $input_handle)
  -> priceRange
  -> minVariantPrice
  -> amount
```

candidate through the real compiler and prove valid.

**Connection boundary**

Pass exact generated candidates for both:

```text
first=1
first=20
```

through the real compiler and prove valid.

Retain the existing builder rejections for:

```text
0
21
INPUT_PROPERTY first
last
missing first
```

**Connected required/wrong-input behavior**

Prove unbuildable candidates never invoke `validateToolDefinition` and never
enable `Use in tool`.

**Connected schema identity**

Prove the rebuilt exact candidate is what is validated and subsequently applied.

**Connected invalid resultPath**

Prove compiler rejection leaves `Use in tool` disabled.

#### Validation

Run:

```bash
npx vitest run \
  tests/storefront-query-builder.test.ts \
  tests/storefront-argument-bindings.test.tsx \
  tests/storefront-schema-browser.test.tsx \
  tests/studio-workspace.test.tsx \
  tests/discovery.test.ts \
  tests/studio-services.test.ts \
  --reporter=verbose
```

Run targeted ESLint for every Attempt 3-owned source/test file.

Run:

```bash
npm run typecheck
```

Acceptance rule remains:

```text
unchanged documented unrelated baseline diagnostics are permitted
zero diagnostics in C034-owned files are required
```

The previous task-owned:

```text
src/studio/discovery/storefront-argument-bindings.tsx TS2367
```

must be absent.

Run both audits:

```bash
rg -n "buildQueryDefinition|path\.split\(\"\\\.\"\)|selectedPaths" \
  components src/studio

rg -n "storefrontSchemaHash|storefrontArtifact|storefrontSchema" \
  src/studio/discovery components
```

Expected: no prohibited production matches.

Then run:

```bash
git diff --check
```

#### Task/report reconciliation

The task Validation checkbox for `npm run typecheck` must remain unchecked until
the Attempt 3 run proves zero task-owned diagnostics.

Mark the re-opened Work Items / Acceptance Criteria complete only after the
corrections and required regressions pass.

Update the Completion Report to distinguish:

```text
Attempt 1:
  AST/merge foundation

Attempt 2:
  production argument binding + schema identity + compiler integration

Attempt 3:
  LIST/connection UI parity
  task-owned typecheck cleanup
  exact connected regression evidence
```

Record:

```text
Attempt 3 implementation commit
final parent report commit
focused test file/count
ESLint
typecheck baseline and zero task-owned diagnostics
both source audits
git diff --check
branch/worktree synchronization
database submodule synchronization
```

Return:

```yaml
status: review
executor: null
claimed_at: null
attempt: 3
```

and STOP.

Do not start `ARCH-021-COMMERCE-035`.

### Reviewed Files

- `components/studio-workspace.tsx`
- `lib/discovery/compiler.ts`
- `lib/discovery/storefront-input-compatibility.ts`
- `src/studio/discovery/selection-tree.ts`
- `src/studio/discovery/storefront-argument-bindings.tsx`
- `src/studio/discovery/storefront-query-builder.ts`
- `src/studio/testing/in-memory-studio-services.ts`
- `tests/storefront-argument-bindings.test.tsx`
- `tests/storefront-query-builder.test.ts`
- `tests/storefront-schema-browser.test.tsx`
- `tests/studio-workspace.test.tsx`
- `tests/discovery.test.ts`
- `tests/studio-services.test.ts`
- task Completion Report

### Validation Reviewed

Submitted Attempt 2 evidence:

```text
focused tests: 6 files / 62 passed
targeted ESLint: PASS
legacy path-string audit: PASS
client artifact-boundary audit: PASS
git diff --check: PASS
typecheck: non-zero
  - unchanged unrelated repository baseline
  - one task-owned TS2367 in storefront-argument-bindings.tsx
```

Architect static review independently confirmed:

- no legacy dot-path Storefront builder source remains;
- no runtime `storefrontSchemaHash` / `storefrontArtifact` / `storefrontSchema`
  value import exists in the client authoring surface;
- the pinned artifact contains real first-only pagination arguments, so the
  current `isFirst` UI test is not compiler-parity complete.

The supplied review archive has no installed dependency tree suitable for
independently rerunning the full Vitest/ESLint/typecheck packet.

### Architecture Conformance

Partial.

The core C034 AST, binding-state, schema-identity and real-compiler architecture
now conforms.

Acceptance is blocked by:

```text
one task-owned TypeScript/source defect
LIST literal UI parity
first-only pagination UI parity
explicit connected regression evidence required by the prior correction contract
```

### Follow-up

Reclaim the same task as Attempt 3.

`ARCH-021-COMMERCE-035` remains Pending until C034 is architect-accepted
Complete.
