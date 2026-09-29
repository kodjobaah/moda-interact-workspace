---
id: ARCH-021-COMMERCE-087
architecture_id: ARCH-021
title: Make generated Nunjucks templates safe for optional result fields
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 74
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-084
enables:
  - ARCH-021-COMMERCE-083
created: 2026-09-29
updated: 2026-09-29
---

# Make generated Nunjucks templates safe for optional result fields

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Guarantee that a deterministic Nunjucks template generated from a valid Commerce Result contract renders safely for every runtime result value permitted by that contract, including omission of optional fields, without weakening C084's strict renderer or changing C085 editor ownership.

## Context

Manual External live Test exposed this valid sequence:

```text
Request construction   Passed
Connection resolution  Passed
Provider request        Passed
Response processing     Passed
Result validation       Passed
Result rendering        Failed
```

The generated template directly interpolated fields such as:

```nunjucks
Image: {{ item.image }}
Department: {{ item.department }}
Description: {{ item.description }}
```

while the Response contract marked those projected fields optional (`omit if missing`).

The result validator correctly accepts omission of an optional property. The C084 renderer correctly uses strict undefined handling. The mismatch is therefore in the generated-template/runtime-context contract: generated source must not assume that an optional path exists.

This is a C084 generator/renderer correction, not a C085 editor correction.

## Scope

Primary implementation areas:

```text
src/commerce/tool-authoring/result-template-generator.ts
src/commerce/execution/renderer.ts
src/commerce/tool-definition/result-schema.ts          # inspect/reuse only unless a bounded helper belongs here
tests/result-template-generator.test.ts
tests/result-template-renderer.test.ts
tests/external-http-live-test-action.test.ts           # bounded regression where useful
tests/shopify-admin-live-test-action.test.ts           # bounded regression where useful
```

A small pure Commerce-local helper for producing a template-safe render context from a validated result/schema is allowed when it keeps generator/runtime semantics explicit and testable.

## Out of Scope

- C085 CodeMirror/editor UX changes.
- Changing the persisted `nunjucks.v1` template shape.
- Reintroducing Text/Items templates.
- Weakening `throwOnUndefined`.
- Provider Request/Response execution changes.
- Changing C079/C081 authoring lifecycle/Test freshness.
- Shopify Admin Test UI integration; COMMERCE-083.
- Database schema/migration changes.
- Fabricating provider/business values for missing optional fields.
- Broadening C084 grammar except where strictly necessary to implement this optional-field safety contract; return any such grammar change to `moda_architect` before implementation.

## Requirements

### R1 — generated-template runtime-safety invariant

For every canonical `CommerceResultSchema` accepted by the C084 generator:

```text
schema
  -> generateDefaultResultTemplate(schema)
  -> any runtime value accepted by that schema
  -> renderDefinitionResult(...)
```

must not fail merely because a schema-optional property is absent.

Static template validation alone is not sufficient.

### R2 — preserve strict rendering

Keep the C084 renderer's strict undefined protection.

Do not solve this task by globally making undefined values silently stringify.

The render context presented to Nunjucks must have deterministic semantics derived from the already-validated Commerce Result schema/value.

### R3 — missing optional values become template-safe, not fabricated business data

After result-contract validation and before Nunjucks evaluation, normalize only schema-permitted **omitted optional properties** to deterministic template-safe structure.

The normalization:

```text
must not mutate the original processed/provider result
must not change result-contract validity
must preserve every present valid value exactly
must not invent a non-null business value
must be deterministic for the same schema/value
must recurse through nested objects/arrays as required for safe template access
```

A suitable implementation may represent an absent optional scalar as `null`, an absent optional collection as an empty/safe collection context, and an absent optional object using a schema-shaped template-only representation whose descendants remain omission-safe. The exact representation is an implementation detail provided no invalid result is made valid and no non-null business value is fabricated.

### R4 — generator respects effective optionality recursively

Generated source must distinguish required paths from paths that may be absent because:

```text
the property itself is optional
or
any ancestor object/path is optional
```

Required scalar paths may remain direct interpolations.

Optional/effectively-optional scalar output must be guarded so the generated template does not emit a missing value.

Optional/effectively-optional object and collection structures must be emitted in a way that is safe when the structure is absent, including nested optional structures.

Do not introduce a second client-side generator; C085 continues to consume the canonical generator/helper.

### R5 — preserve accepted C084 grammar semantics

Do not reopen the accepted scalar-only equality/comparison rules merely as a shortcut.

If optional object/array safety cannot be expressed with the currently accepted grammar plus a template-safe normalized context, stop and return the grammar gap to `moda_architect` rather than silently broadening `nunjucks.v1`.

### R6 — no valid omission may produce `RESULT_RENDERING_FAILED`

Add runtime regressions proving a generated template renders successfully when optional fields are omitted in every materially distinct supported location:

```text
optional scalar property
multiple optional sibling scalars
optional scalar under a required object
required scalar under an optional object
optional scalar under an optional object
optional object omitted entirely
optional array omitted entirely
optional scalar inside object-list items
nested optional object/list combinations
```

The rendered result may omit corresponding human-readable lines/sections or use the generator's deterministic empty-list fallback, but must not expose `undefined`, `Infinity`, `NaN`, an engine-dependent error, or `RESULT_RENDERING_FAILED`.

### R7 — required fields remain strict

Do not mask an invalid runtime result.

If a required field is absent, result-contract validation must continue to fail before template rendering according to the accepted execution pipeline.

The template-safe normalization is only for omissions already permitted by the canonical result schema.

### R8 — Test and production share the correction

The correction must live at the canonical C084 generator/renderer boundary so:

```text
External live Test
Shopify Admin live Test
production Tool execution
```

all receive identical optional-field safety.

Do not patch only one Test Server Action or one provider.

## Work Items

- [ ] Add a pure deterministic template-safe normalization step for schema-permitted omitted optional properties, or an equivalent bounded renderer-side mechanism satisfying R2/R3.
- [ ] Make the canonical generator propagate effective optionality recursively.
- [ ] Keep required paths direct/strict and optional paths safe.
- [ ] Add nested optional object/list generator fixtures.
- [ ] Add render regressions across all materially distinct omission cases in R6.
- [ ] Add at least one External/Shopify execution-boundary regression proving a valid optional-field omission does not become `RESULT_RENDERING_FAILED`.
- [ ] Confirm no C085 UI/state file is changed.

## Interfaces / Contracts

Consumes:

```text
CommerceResultSchema
validate/normalize result contract from COMMERCE-063/C084
generateDefaultResultTemplate from COMMERCE-084
renderDefinitionResult from COMMERCE-084
```

Produces no new persistent, database or cross-repository contract.

Any new normalization/helper API remains Commerce-local.

## Dependencies

- ARCH-021-COMMERCE-084

## Enables

- ARCH-021-COMMERCE-083

## Acceptance Criteria

- [ ] A generated template renders every schema-valid fixture in the optional-omission matrix without `RESULT_RENDERING_FAILED`.
- [ ] Missing optional scalars never reach Nunjucks as unguarded undefined interpolation.
- [ ] Nested optional objects/arrays are safe recursively.
- [ ] Present valid values are rendered unchanged.
- [ ] Required-field omission still fails result-contract validation before render.
- [ ] Original processed/provider result objects are not mutated by template-safety normalization.
- [ ] No non-null business value is fabricated for an omitted optional property.
- [ ] External Test, Shopify Admin Test and production continue to share one canonical renderer behavior.
- [ ] C084 grammar/runtimeVersion/persisted template shape is unchanged.
- [ ] No C085 UI/state implementation is modified.

## Validation

- [ ] focused generator tests for required vs optional/effective-optional source
- [ ] focused renderer tests for the complete optional-omission matrix
- [ ] focused result-validation regression proving required omissions remain invalid
- [ ] focused External or Shopify live-Test execution regression for optional omission
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-083.

## Implementation Notes

Prefer solving optionality at the canonical generator/render-context boundary rather than weakening Nunjucks or duplicating provider-specific behavior.

The runtime result has already passed the canonical Result contract before rendering. The template-safety transformation may therefore rely on that fact but must remain pure and non-mutating.

## Completion Report

### Status

Ready for Rework

### Attempt 1 Evidence Reconciled from Duplicate Task Record

The repository agent executed Attempt 1 against a non-canonical duplicate C087 task file:
`docs/decisions/commerce/ARCH-021/COMMERCE-087-make-generated-nunjucks-optional-safe.md`.

That duplicate used the same task ID but a different contract and is removed by this architect reconciliation. The implementation/report evidence below is preserved verbatim in substance so the next attempt does not lose its execution history.


### Status

Attempt 1 implementation complete; submitted for Architect Review.

### Files Changed

`moda-interact-commerce/src/commerce/execution/renderer.ts`
`moda-interact-commerce/src/commerce/tool-authoring/nunjucks-template.ts`
`moda-interact-commerce/src/commerce/tool-authoring/result-template-generator.ts`
`moda-interact-commerce/tests/definition-execution.test.ts`
`moda-interact-commerce/tests/external-http-live-test.test.ts`
`moda-interact-commerce/tests/result-template-authoring.test.ts`
`moda-interact-commerce/tests/result-template-optionality.test.ts`
`moda-interact-commerce/tests/result-template-renderer.test.ts`

### Work Completed

- Reproduced the C084 boundary mismatch: canonical normalization accepts omitted optional properties, while a direct strict Nunjucks lookup fails on the absent value. The External live-Test regression now proves `resultValidation: Passed` and `resultRendering: Passed` for that same permitted omission.
- Generated templates use canonical `required` membership at root and nested object boundaries. Optional scalar/object paths are guarded with `is defined`; absent optional arrays use the deterministic unavailable-for-collection message, including when present-empty; required scalar paths remain direct.
- The canonical validator recognizes only the bounded `is defined` AST test, tracks positive-branch presence without leaking scope, validates optional loop sources, and reports `unguarded_optional_result_path` for unsafe accesses.
- Registered the `defined` test in the existing strict renderer without changing `throwOnUndefined`. A local intersection type describes the runtime `addTest` API omitted from the installed Nunjucks declaration.
- Added the exact six-optional-field item fixture, empty-item rendering, nested optionality matrix, falsy-present values, top-level optionality, required-field rejection, unsafe-authored-template cases, External live-Test coverage and a Shopify Admin canonical execution regression.
- The C087 implementation commit changes no C085 UI/state files, provider-specific validators, persisted template shape, publication-proof writes or durable Test writes. C085 files visible in the task branch are unchanged files brought in by the required `origin/main` merge.

### Validation Results

- Final focused C087 packet after merging current `origin/main`: 11 files passed, 132 tests passed. It covers generator, canonical validator, renderer, Admin definition execution, External live Test, publication/preflight and commerce lifecycle boundaries.
- External omitted-optional-field Test asserts `resultValidation: passed`, `resultRendering: passed`, and returned rendered text. Missing required data remains rejected before rendering. Shopify Admin coverage uses a compiler-supported nullable selected field, canonical omission normalization and the production definition executor; no Admin Test UI is introduced by this task.
- Targeted ESLint on all eight changed files passed. VS Code changed-file diagnostics reported no errors. Project-wide `tsc --noEmit` remains nonzero on unrelated C085 Result Template tab test diagnostics (`tests/result-template-tab.test.tsx`); filtered diagnostics contain no C087-changed file. C084 Attempt 2 also records a broad pre-existing repository typecheck baseline.
- `git diff --check` passed before commit and after mainline synchronization.
- A 12-file supplemental run passed 152/154 tests. Its two failures are existing QuickJS request-preview cases in `tests/external-tool-authoring-validation.test.ts`: the packaged runtime reports `MODULE_NOT_FOUND`, producing `RUNTIME_UNAVAILABLE`. C084 Attempt 1 documents the same QuickJS preview baseline; the C087-focused 11-file packet passes when those unrelated cases are excluded.

### Deviations

- The repository has no Shopify Admin live-Test action/test integration yet; that UI integration is explicitly owned by C083 and is out of scope here. The Admin production-execution regression covers the same canonical optional-result and strict-rendering path.
- Whole-project typecheck and the two QuickJS-dependent external-authoring tests remain limited by the documented repository/runtime baseline; no C087-changed file is implicated.

### Assumptions

The C082/C083 Admin live-Test surface will consume the same canonical renderer; C087 does not add a second provider-specific presence implementation.

### Unresolved Issues

No C087-owned issue remains. The existing QuickJS `MODULE_NOT_FOUND` preview condition and unrelated C085/repository type diagnostics are recorded above for Architect review.

### Architectural Concerns

None. Strict undefined rendering, the persisted `nunjucks.v1` shape, canonical schema ownership and C085 UI ownership are preserved.

### Git / VCS

Task branch: `task/ARCH-021-COMMERCE-087`

Physical worktree isolation:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-087`
- parent branch: `task/ARCH-021-COMMERCE-087`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-087`
- implementation branch: `task/ARCH-021-COMMERCE-087`
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Start-of-attempt synchronization:
- parent remote task branch fast-forwarded: yes (launcher-prepared; verified current before report update)
- parent `origin/main` incorporated: yes
- implementation remote task branch fast-forwarded: not-needed (no remote task ref existed before publication)
- implementation `origin/main` incorporated: yes

Implementation repository:
- repository: `moda-interact-commerce`
- implementation commit: `8905d9b` (C087 implementation `dfefb3f`; mainline merge `8905d9b`)
- remote branch: `origin/task/ARCH-021-COMMERCE-087`
- pushed: yes

Parent workspace:
- task file: `docs/decisions/commerce/ARCH-021/COMMERCE-087-make-generated-nunjucks-optional-safe.md`
- commit: `072447753bd85d7fd7fa91c7c93d5e69c036444c` (completion report)
- remote branch: `origin/task/ARCH-021-COMMERCE-087`
- pushed: yes
- submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is not accepted.

The implementation correctly reproduces the original live-Test failure and demonstrates that schema-permitted omission is the cause. It also proves that guarding optional paths can prevent `RESULT_RENDERING_FAILED` while preserving required-field validation, and the focused External/Admin execution coverage is useful.

However, the submitted implementation does **not** conform to the canonical C087 contract that is indexed by the Commerce architecture.

There are two required corrections.

#### 1. Do not broaden accepted `nunjucks.v1` with `is defined`

The canonical C087 task explicitly states:

```text
R5 — preserve accepted C084 grammar semantics

Do not reopen the accepted scalar-only equality/comparison rules merely as a shortcut.

If optional object/array safety cannot be expressed with the currently accepted grammar plus a template-safe normalized context, stop and return the grammar gap to moda_architect rather than silently broadening nunjucks.v1.
```

Attempt 1 instead changes the canonical language/validator/runtime by adding:

```nunjucks
{% if path is defined %}
```

and then requires manually authored optional paths to use that new construct through `unguarded_optional_result_path`.

That is a semantic grammar expansion outside the authoritative task contract.

The accepted C084 grammar already has the pieces needed for this correction without adding a Nunjucks test:

```text
if / elif / else
scalar/null equality and inequality
property-only paths
for loops
```

Attempt 2 must therefore restore the accepted C084 grammar and implement optional safety at the canonical render-context + generator boundary.

Required semantics:

1. Add a pure, deterministic, non-mutating **template-safe normalization** of the already contract-valid runtime result before Nunjucks evaluation.
2. For schema-permitted omitted optional values, normalize only the template context:
   - omitted optional scalar -> `null`;
   - omitted optional array -> an empty array;
   - omitted optional object -> a schema-shaped template-only object whose missing descendants are recursively represented safely (`null`, empty array, or nested template-only object as appropriate).
3. Preserve every present valid runtime value exactly.
4. Never fabricate a non-null business value.
5. Never mutate the processed/provider result.
6. Keep required-field omission invalid in canonical result validation before render.
7. Remove C087's `is defined` grammar/test registration and the corresponding canonical-validator language expansion.
8. Remove the requirement that manually authored templates must use `is defined`; return the validator to the accepted C084 expression grammar.

The generator must propagate **effective optionality** recursively.

For a scalar that is optional itself, or sits beneath any optional ancestor, emit a guard using the existing C084 scalar/null grammar, for example:

```nunjucks
{% if item.image != null %}
  Image: {{ item.image }}
{% endif %}
```

Required scalars whose entire ancestor chain is required remain direct:

```nunjucks
Name: {{ item.name }}
```

Optional/effectively-optional arrays can be looped safely because the template-only normalized context supplies an empty array when absent. The current deterministic `{% else %} No ... available. {% endfor %}` behavior may remain.

Optional objects must be safe recursively through the template-only schema-shaped context. A required child under an omitted optional object is **effectively optional for rendering** and must not be directly emitted as though the parent existed in the provider value.

Do not change the persisted template shape, `runtimeVersion`, provider execution, C085 UI/state, or strict `throwOnUndefined`.

Add focused regressions proving:

```text
- generated optional scalar source uses existing `!= null` semantics, not `is defined`;
- `is defined` remains unsupported by the canonical C084 grammar;
- optional scalar omitted -> normalized null -> guarded line omitted;
- optional array omitted -> normalized [] -> deterministic empty-list fallback;
- optional object omitted -> nested required/optional descendants render safely without fabricated business values;
- nested optional object/list combinations remain total;
- 0 / false / "" remain present and render normally;
- present runtime values are byte/value-preserved by normalization;
- the original runtime result object is not mutated;
- missing required fields still fail result validation before render;
- External live Test and Shopify Admin production execution both use the same canonical correction.
```

#### 2. Reconcile the duplicate C087 task record

The submitted snapshot contains two files with the same task ID:

Canonical/indexed task:

```text
docs/decisions/commerce/ARCH-021/COMMERCE-087-make-generated-nunjucks-safe-for-optional-fields.md
```

Non-canonical duplicate used for Attempt 1:

```text
docs/decisions/commerce/ARCH-021/COMMERCE-087-make-generated-nunjucks-optional-safe.md
```

The Commerce `_index.md` and parent architecture point to the first file. The duplicate contains a materially different R3/R4/R5 contract and cannot remain as a second source of truth.

This architect patch:

- keeps the indexed architect-created file as canonical;
- records the real first attempt as `attempt: 1`;
- preserves the submitted Attempt 1 Completion Report evidence in the canonical task; and
- removes the duplicate task file.

Attempt 2 must claim and update **only** the canonical task file.

Do not recreate or rename another C087 task definition.

### Reviewed Files

- `src/commerce/tool-authoring/result-template-generator.ts`
- `src/commerce/tool-authoring/nunjucks-template.ts`
- `src/commerce/execution/renderer.ts`
- `tests/result-template-optionality.test.ts`
- `tests/result-template-generator.test.ts`
- `tests/result-template-renderer.test.ts`
- `tests/external-http-live-test.test.ts`
- Admin production-execution optional-result regression
- canonical C087 task file
- duplicate C087 task/report file
- Commerce `_index.md`
- parent ARCH-021 architecture task graph

### Validation Reviewed

Submitted Attempt 1 evidence preserved from the implementation report:

- focused packet: **11 files, 132 tests passed**;
- supplemental packet: 152/154, with the two failures attributed to the previously documented QuickJS `MODULE_NOT_FOUND` preview baseline;
- targeted ESLint: passed;
- changed-file diagnostics: clean;
- `git diff --check`: passed;
- repository-wide TypeScript remains non-green on unrelated C085/baseline diagnostics, with no C087 changed-file diagnostics.

Those results establish that the implemented `is defined` approach works mechanically. They do not make the grammar expansion architecture-conformant.

Source inspection additionally confirms:

- no renderer normalization/template-safe schema shaping was implemented;
- the strict renderer remains strict;
- the generator emits `is defined` guards for optional scalar/object/array paths;
- the canonical validator now admits the `Is` AST node and enforces `unguarded_optional_result_path`; and
- the renderer registers a `defined` Nunjucks test.

### Architecture Conformance

Partial.

The runtime-totality goal, required-field strictness, provider-neutral correction location and focused execution coverage are aligned.

Acceptance is blocked because Attempt 1 changed the canonical `nunjucks.v1` grammar contrary to C087 R5 and executed under a duplicate, non-canonical task definition.

### Follow-up

Return the canonical C087 task as Attempt 2.

Replace the `is defined` grammar expansion with template-safe schema-derived context normalization plus generator guards expressed in the already-accepted C084 grammar. Remove the duplicate-task-derived validator/runtime grammar additions, add the focused normalization/generator/execution regressions above, rerun the focused C087 packet and required changed-file checks, update the canonical Completion Report, and STOP.

Do not modify C085 UI/state.

COMMERCE-083 remains Pending until canonical C087 is accepted Complete.
