---
id: ARCH-021-COMMERCE-085
architecture_id: ARCH-021
title: Build generated CodeMirror Result Template authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 76
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-084
enables:
  - ARCH-021-COMMERCE-083
created: 2026-09-28
updated: 2026-09-29
---

# Build generated CodeMirror Result Template authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the current Text/Items Result Template controls with one CodeMirror 6 Nunjucks source editor that automatically seeds a deterministic template from the current validated Response contract, preserves user-authored source on later Response changes, exposes schema-derived insertion/completion help, and participates in COMMERCE-078's central dirty/validation state without performing persistence or rendering in React.

## Context

COMMERCE-084 replaces the persisted/runtime Result Template grammar with bounded `nunjucks.v1` and provides:

```text
generateDefaultResultTemplate(outputSchema)
validateResponseTemplateAuthoring(template, outputSchema)
renderDefinitionResult(...)
```

The current Result Template UI still contains bespoke controls for:

```text
Template type: Text | Items
Collection
Text template / Item template
Empty fallback
Unavailable fallback
```

Those controls duplicate structural information already present in the Response contract. The new Result Template authoring model is:

```text
validated Response contract
        |
        +--> deterministic generated Nunjucks source
        |
        v
CodeMirror Result Template editor
        |
        +--> explicit Validate Result Template
        |
        v
canonical responseTemplate
```

The editor is an authoring aid only. It does not own template grammar, canonical validation or runtime rendering.

COMMERCE-079 and COMMERCE-081 are already architect-accepted Complete. C085 must preserve their persisted-DRAFT and External Test behavior while replacing the Result Template authoring surface; they are not downstream tasks to be re-executed.

COMMERCE-083 has not started and is dependency-gated on C085 so Shopify Admin Test UI integration consumes the final Nunjucks editor contract rather than the obsolete Text/Items surface.

## Scope

Primary implementation areas:

```text
src/studio/tools/authoring/result-template-tab.tsx
src/studio/tools/authoring/result-template-editor.tsx       # new, or exact bounded equivalent
src/studio/tools/authoring/result-template-bindings.tsx      # optional bounded presentation extraction
src/studio/code-response/code-editor.tsx                     # generalise only if required; preserve JavaScript editor behaviour
src/studio/tools/new-tool-editor.tsx                         # consume C078 session state only where required
src/studio/tools/tool-editor.tsx                             # consume shared component only where required
app/styles.css                                               # bounded editor/result-tree styles
```

Tests:

```text
tests/result-template-tab.test.tsx
tests/tool-authoring-screen.test.tsx
tests/external-tools-ui.test.tsx
tests/shopify-admin-tools-ui.test.tsx
```

## Out of Scope

- Nunjucks runtime grammar, renderer, validator or generator semantics; COMMERCE-084 owns them.
- Provider execution.
- React-side template rendering.
- Persisted-DRAFT save/CAS parity beyond consuming the reusable editor; COMMERCE-079.
- External live-Test presentation/gating; COMMERCE-081.
- Shopify live-Test presentation/gating; COMMERCE-083.
- A visual/WYSIWYG template designer.
- Drag/drop programming blocks.
- HTML preview or `dangerouslySetInnerHTML`.
- A second client-side template validator.
- Automatically rewriting a user-modified Result Template when Response changes.

## Requirements

### R1 — remove the bespoke Text/Items authoring UI

The Result Template tab must no longer render:

```text
Template type
Text template
Collection
Item template
Empty fallback
```

There is one persisted template source:

```text
responseTemplate.source
```

and one plain fallback:

```text
responseTemplate.unavailable
```

The visible Result Template tab consists of these conceptual areas in this order:

```text
1. Result Template heading/status
2. Generated-from-Response explanation + Regenerate action
3. CodeMirror Result Template source editor
4. Available result data / insertion helpers
5. Unavailable fallback
6. Validate Result Template action + diagnostics
```

### R2 — use the repository's existing CodeMirror 6 stack

Build a dedicated `ResultTemplateEditor` over the CodeMirror 6 packages already used by the Commerce JavaScript editor.

Required editor behaviour:

```text
multiline editing
line numbers
normal cursor/selection behaviour
source controlled by React props
read-only support if reused in Review later
onChange(source) callback
aria-label = "Result template source"
data-language = "nunjucks"
```

Do not instantiate Monaco and do not introduce another editor framework.

If autocomplete requires CodeMirror packages currently present only transitively, add them as direct dependencies rather than relying on transitive imports.

Do not apply the JavaScript language extension to Result Template source.

### R3 — CodeMirror is not the grammar authority

The CodeMirror component may provide highlighting, completion and insertion conveniences, but it must not decide whether a template is valid.

Canonical validation remains:

```text
COMMERCE-084 validateResponseTemplateAuthoring
```

and is invoked through the existing Result Template validation action/boundary accepted by C078.

Do not duplicate Nunjucks parsing/path validation in React.

### R4 — authoring metadata is session-only

Extend the C078 browser-local Result Template authoring slice with session metadata semantically equivalent to:

```ts
type ResultTemplateOrigin = "GENERATED" | "USER_MODIFIED";

type ResultTemplateAuthoringMeta = {
  origin: ResultTemplateOrigin;
  generatedFromContractFingerprint: string | null;
};
```

This metadata is **not persisted** in `CommerceToolDefinition.responseTemplate` and requires no database field.

For a new Tool before the first generated template exists:

```text
origin = GENERATED
generatedFromContractFingerprint = null
```

For an existing persisted Tool loaded later by COMMERCE-079:

```text
origin = USER_MODIFIED
```

regardless of whether its source text happens to equal the current generator output. Never assume a persisted author intended automatic regeneration.

### R5 — canonical Response fingerprint

The Result Template tab receives the current canonical output schema used by COMMERCE-084 validation.

Use the canonical Commerce result-schema serialisation as the session fingerprint:

```text
canonicalizeCommerceResultSchema(outputSchema)
```

Do not fingerprint provider-specific Request/Response UI objects and do not use `JSON.stringify` over uncontrolled object insertion order when a canonical schema serializer already exists.

### R6 — automatic generation for a pristine new template

For a **new Tool only**, when all of the following become true:

```text
Response is current + VALID under C078
current canonical output schema is available
Result Template has never been user-modified
current generatedFromContractFingerprint != current Response fingerprint
```

call exactly:

```ts
generateDefaultResultTemplate(currentOutputSchema, currentUnavailable)
```

and replace the local Result Template with the returned `nunjucks.v1` template.

After automatic generation:

```text
origin = GENERATED
generatedFromContractFingerprint = current fingerprint
Result Template validation = STALE/UNVALIDATED according to C078
Test = STALE according to C078
```

Generation does **not** count as validation and must not enable Save by itself.

Do not wait for the user to select Text/Items/Collection; those concepts no longer exist.

### R7 — generated template tracks Response only while pristine/generated

If Response changes and later becomes current + VALID again:

```text
IF origin == GENERATED
  AND the author has not edited source/unavailable since the last generation
THEN
  regenerate from the new canonical Response schema automatically
  update generatedFromContractFingerprint
  mark Result Template validation stale
  stale Test
```

Do not perform automatic regeneration while Response is invalid/stale because there is no authoritative current contract to generate from.

### R8 — any author edit makes the template user-modified

Any user-originated change to either:

```text
responseTemplate.source
responseTemplate.unavailable
```

must synchronously set:

```text
origin = USER_MODIFIED
```

and follow C078's existing edit transition:

```text
Result Template validation -> STALE
Test -> STALE
Save -> disabled until current validation/Test requirements are restored
```

Programmatic automatic generation must **not** mark the source USER_MODIFIED.

### R9 — Response changes never overwrite USER_MODIFIED source

When:

```text
origin == USER_MODIFIED
```

and Response changes:

```text
preserve source byte-for-byte
preserve unavailable byte-for-byte
recompute available result data from the new contract when it becomes valid
mark Result Template validation STALE
stale Test
```

Do not silently replace invalid/obsolete paths. The explicit Validate action tells the user what no longer matches.

### R10 — explicit Regenerate from Response

Render one action labelled exactly:

```text
Regenerate from Response
```

It is disabled when no current VALID Response/output schema exists.

If the current template is USER_MODIFIED, clicking it must ask for confirmation using the repository's accepted browser-confirm pattern with this exact message:

```text
Regenerate Result Template? This will replace your current template with one generated from the current Response contract.
```

If the user cancels:

```text
no source change
no fallback change
no origin change
no validation revision change
no Test-state change
```

If confirmed, or if the current template is still GENERATED:

```text
replace source with COMMERCE-084 generated source
preserve the current unavailable fallback as the generator input
origin = GENERATED
generatedFromContractFingerprint = current fingerprint
mark Result Template validation STALE
stale Test
```

Do not persist as part of Regenerate.

### R11 — result-data tree is derived from the canonical contract

Below the editor, render a provider-neutral read-only tree headed exactly:

```text
Available result data
```

The root label is:

```text
result
```

Recursively show the current canonical output schema using these representations:

```text
object property: name
array property:  name[]
scalar leaf:     name <type>
```

For the manual-review example, the visible structure must communicate:

```text
result
└── values
    └── items[]
        ├── department string
        ├── description string
        ├── id integer
        ├── image string
        ├── name string
        └── price string
```

Optional properties must be visibly marked `optional`; required properties must not be labelled optional.

The tree consumes only the canonical `CommerceResultSchema`; it must not infer provider-specific paths.

### R12 — insertion/completion helpers are generated from the schema, not guessed

Provide CodeMirror completion/insertion assistance for schema-known paths.

At minimum expose these completion/snippet categories:

```text
ROOT SCALAR
  inserts: {{ result.path.to.scalar }}

COLLECTION
  inserts a complete supported for/else/endfor skeleton using the deterministic
  alias and field structure supplied by the COMMERCE-084 generator/helper.

SCALAR ARRAY
  inserts a complete loop using {{ itemN }}.
```

Do not invent a client-only grammar or completion path absent from the canonical schema.

It is acceptable for v1 completion to offer complete root expressions/loop snippets rather than implementing a full IDE-quality scope resolver for arbitrary hand-authored loop aliases. If alias-aware completions are implemented, they must consume a shared COMMERCE-084 analysis helper rather than a second regex parser in React.

Clicking/inserting a suggestion modifies source exactly as a normal author edit and therefore sets `origin = USER_MODIFIED` and stales Result Template validation/Test.

### R13 — minimal Nunjucks syntax presentation

The editor must visually distinguish at least:

```text
{{ ... }} interpolation regions
{% ... %} statement regions
plain literal text
```

Use CodeMirror decorations/language support without implementing a second Nunjucks validity parser.

Syntax colouring is presentation only; canonical validation errors come from COMMERCE-084.

### R14 — canonical validation UX

Keep one action labelled exactly:

```text
Validate Result Template
```

It submits the current canonical object:

```ts
{
  kind: "nunjucks",
  runtimeVersion: "nunjucks.v1",
  source,
  unavailable,
}
```

against the current canonical output schema.

Successful validation updates C078's central Result Template validation checkpoint for the exact current section revision. Failed validation updates the same checkpoint to current INVALID with bounded issues. Stale asynchronous responses must not validate a newer source revision.

Show validation diagnostics in the Result Template surface. If COMMERCE-084 supplies line/column information, display it; do not derive different line/column positions in the browser.

### R15 — Review and persistence use only the canonical source object

The parent candidate/Review receives exactly the current `responseTemplate` object produced by this tab.

Do not persist:

```text
origin
generatedFromContractFingerprint
CodeMirror state
completion state
validation diagnostics
```

Review may display Nunjucks source read-only, but editing remains owned by Result Template.

Save/Cancel persistence semantics remain those defined by C078/C079.

### R16 — no browser rendering

The editor must never execute Nunjucks and must never attempt to produce the agent-facing result.

Only Test/production server code renders through:

```text
renderDefinitionResult
```

The Test tab continues to display the server-returned `renderedText` exactly; C081/C083 own that presentation.

## Work Items

- [ ] Replace Text/Items/Collection authoring controls with one `nunjucks.v1` source + unavailable fallback surface.
- [ ] Add a dedicated CodeMirror 6 `ResultTemplateEditor` without the JavaScript language extension.
- [ ] Add session-only GENERATED/USER_MODIFIED metadata and canonical Response fingerprint handling.
- [ ] Auto-generate the first new-Tool template from the first current VALID Response contract.
- [ ] Auto-regenerate only while the template remains GENERATED.
- [ ] Preserve USER_MODIFIED source byte-for-byte across Response changes.
- [ ] Add confirmed `Regenerate from Response` semantics exactly as R10.
- [ ] Render the recursive provider-neutral Available result data tree.
- [ ] Add schema-derived interpolation/loop insertion or completion helpers.
- [ ] Add bounded Nunjucks delimiter syntax presentation in CodeMirror.
- [ ] Keep canonical validation server/domain-owned and wire results to C078 central validation state.
- [ ] Ensure Review/persistence receive only the canonical `responseTemplate` object.
- [ ] Add deterministic pristine/regeneration/manual-edit/stale-validation regressions.

## Interfaces / Contracts

Consumes from COMMERCE-084:

```text
ResponseTemplate `nunjucks.v1` shape
generateDefaultResultTemplate
validateResponseTemplateAuthoring
canonical CommerceResultSchema
```

Consumes from COMMERCE-078:

```text
browser-local Tool authoring session
Result Template section revision/validation state
Test freshness state
final candidate assembly
```

Produces UI-only/session-only authoring metadata:

```text
origin: GENERATED | USER_MODIFIED
generatedFromContractFingerprint
```

No database/cross-service contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-078
- ARCH-021-COMMERCE-084

## Enables

- ARCH-021-COMMERCE-079
- ARCH-021-COMMERCE-081
- ARCH-021-COMMERCE-083

## Acceptance Criteria

- [ ] Result Template no longer exposes Text/Items/Collection/Item-template/Empty-fallback controls.
- [ ] Result Template uses the repository CodeMirror 6 stack and exposes one editable Nunjucks source.
- [ ] A new Tool with a current VALID Response automatically receives the deterministic generated template without persistence.
- [ ] The documented `values.items[]` Response opens with generated loop source over `result.values.items`, not `{{result.values.value}}` and not an empty Text template.
- [ ] Generated source is marked GENERATED and still requires explicit Result Template validation.
- [ ] Editing source or unavailable fallback switches to USER_MODIFIED and immediately stales validation/Test.
- [ ] A later Response change automatically regenerates only GENERATED templates.
- [ ] A later Response change never overwrites USER_MODIFIED source/fallback.
- [ ] Cancelled Regenerate changes no authoring or validation/Test state.
- [ ] Confirmed Regenerate replaces source deterministically and returns origin to GENERATED.
- [ ] Available result data displays recursive object/array/scalar paths and optionality from the canonical schema.
- [ ] Completion/insertion suggestions originate only from the canonical schema/generator helpers.
- [ ] Canonical validation remains COMMERCE-084-owned; CodeMirror does not become a second validator.
- [ ] React never renders/evaluates Nunjucks and never uses rendered source as HTML.
- [ ] Authoring metadata remains session-only and is absent from the persisted Tool definition.

## Validation

- [ ] `npx vitest run tests/result-template-tab.test.tsx tests/tool-authoring-screen.test.tsx`
- [ ] focused new-Tool auto-generation regression for the exact `values.items[]` six-field example
- [ ] focused GENERATED -> Response change -> automatic regeneration regression
- [ ] focused USER_MODIFIED -> Response change -> preserve-byte-for-byte regression
- [ ] focused Regenerate cancel/confirm regressions
- [ ] focused validation-revision race regression: validation for source revision N cannot validate revision N+1
- [ ] focused result-data-tree recursion/optionality regression
- [ ] focused completion/snippet insertion regression proving schema-derived paths
- [ ] focused proof that no Result Template edit/regeneration/validation writes Tool/ToolRevision state
- [ ] existing External and Shopify Result Template integration UI tests updated for the one-source editor
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin COMMERCE-079, COMMERCE-081, COMMERCE-083 or another follow-on task.

## Implementation Notes

Do not create a visual programming language. The editor exposes ordinary bounded Nunjucks source, deterministic generation, schema-derived help and canonical validation.

If generalising `src/studio/code-response/code-editor.tsx`, preserve its existing JavaScript behaviour and tests exactly. A separate ResultTemplateEditor is preferred when generalisation would couple JavaScript-specific and Nunjucks-specific behaviour.

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
