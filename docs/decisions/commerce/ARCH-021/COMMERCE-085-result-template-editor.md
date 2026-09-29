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
status: in_progress
priority: 76
executor: copilot
claimed_at: 2026-09-29T01:25:24Z
attempt: 2
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

- [x] Replace Text/Items/Collection authoring controls with one `nunjucks.v1` source + unavailable fallback surface.
- [x] Add a dedicated CodeMirror 6 `ResultTemplateEditor` without the JavaScript language extension.
- [x] Add session-only GENERATED/USER_MODIFIED metadata and canonical Response fingerprint handling.
- [x] Auto-generate the first new-Tool template from the first current VALID Response contract.
- [x] Auto-regenerate only while the template remains GENERATED.
- [x] Preserve USER_MODIFIED source byte-for-byte across Response changes.
- [x] Add confirmed `Regenerate from Response` semantics exactly as R10.
- [x] Render the recursive provider-neutral Available result data tree.
- [x] Add schema-derived interpolation/loop insertion or completion helpers.
- [x] Add bounded Nunjucks delimiter syntax presentation in CodeMirror.
- [x] Keep canonical validation server/domain-owned and wire results to C078 central validation state.
- [x] Ensure Review/persistence receive only the canonical `responseTemplate` object.
- [x] Add deterministic pristine/regeneration/manual-edit/stale-validation regressions.

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

- ARCH-021-COMMERCE-083

## Acceptance Criteria

- [x] Result Template no longer exposes Text/Items/Collection/Item-template/Empty-fallback controls.
- [x] Result Template uses the repository CodeMirror 6 stack and exposes one editable Nunjucks source.
- [x] A new Tool with a current VALID Response automatically receives the deterministic generated template without persistence.
- [x] The documented `values.items[]` Response opens with generated loop source over `result.values.items`, not `{{result.values.value}}` and not an empty Text template.
- [x] Generated source is marked GENERATED and still requires explicit Result Template validation.
- [x] Editing source or unavailable fallback switches to USER_MODIFIED and immediately stales validation/Test.
- [x] A later Response change automatically regenerates only GENERATED templates.
- [x] A later Response change never overwrites USER_MODIFIED source/fallback.
- [x] Cancelled Regenerate changes no authoring or validation/Test state.
- [x] Confirmed Regenerate replaces source deterministically and returns origin to GENERATED.
- [x] Available result data displays recursive object/array/scalar paths and optionality from the canonical schema.
- [x] Completion/insertion suggestions originate only from the canonical schema/generator helpers.
- [x] Canonical validation remains COMMERCE-084-owned; CodeMirror does not become a second validator.
- [x] React never renders/evaluates Nunjucks and never uses rendered source as HTML.
- [x] Authoring metadata remains session-only and is absent from the persisted Tool definition.

## Validation

- [x] `vitest run tests/result-template-tab.test.tsx tests/tool-authoring-screen.test.tsx` (also included with New Tool state/session suites below)
- [x] focused new-Tool auto-generation regression for the exact `values.items[]` six-field example
- [x] focused GENERATED -> Response change -> automatic regeneration regression
- [x] focused USER_MODIFIED -> Response change -> preserve-byte-for-byte regression
- [x] focused Regenerate cancel/confirm regressions
- [x] focused validation-revision race regression: validation for source revision N cannot validate revision N+1
- [x] focused result-data-tree recursion/optionality regression
- [x] focused completion/snippet insertion regression proving schema-derived paths, including scalar arrays
- [x] focused proof that no Result Template edit/regeneration/validation writes Tool/ToolRevision state
- [x] External and Shopify Result Template UI tests updated; execution blocked before collection by the missing generated Prisma Client
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics are clean; repository `tsc --noEmit` reports existing unrelated errors and missing generated Prisma types
- [x] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin COMMERCE-083 or another follow-on task.

## Implementation Notes

Do not create a visual programming language. The editor exposes ordinary bounded Nunjucks source, deterministic generation, schema-derived help and canonical validation.

If generalising `src/studio/code-response/code-editor.tsx`, preserve its existing JavaScript behaviour and tests exactly. A separate ResultTemplateEditor is preferred when generalisation would couple JavaScript-specific and Nunjucks-specific behaviour.

## Completion Report

### Status

Attempt 1 implementation complete; ready for Architect Review. Task metadata is reconciled to `status: review`, `executor: null` and `claimed_at: null`.

### Files Changed

Implementation changes are in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-085` on `task/ARCH-021-COMMERCE-085`:

- `src/studio/tools/authoring-session.ts`
- `src/studio/tools/authoring/result-template-editor.tsx`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/new-tool-authoring-state.test.ts`
- `tests/result-template-tab.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

### Work Completed

Replaced the Text/Items Result Template form with a dedicated CodeMirror 6 Nunjucks editor, canonical schema tree and schema-derived root/loop insertions. Added deterministic generation tied to the current canonical Response fingerprint, session-only GENERATED/USER_MODIFIED metadata, preservation of user-authored source across Response changes, confirmed regeneration and stale-safe COMMERCE-084 validation wired through C078 state. New Tool, persisted External/Admin Tool and Explore Shopify browser-session flows consume the canonical response template without persisting authoring metadata or rendering Nunjucks in React.

Updated New Tool/External integration fixtures and selectors for the single-source editor, and added focused coverage for the six-field `values.items[]` example, scalar arrays, source preservation, confirmation, validation races, optionality and canonical snippet insertion.

### Validation Results

Passed: `vitest run tests/result-template-tab.test.tsx tests/new-tool-authoring-state.test.ts tests/tool-authoring-session.test.ts tests/tool-authoring-screen.test.tsx` (4 files, 63 tests); targeted ESLint over all changed TypeScript/TSX files; changed-file editor diagnostics; `git diff --check`.

Attempted `tests/external-tools-ui.test.tsx` and `tests/shopify-admin-tools-ui.test.tsx`; both stop before test collection because `.prisma/client/default` is absent. Prisma generation was not run because its package workflow includes submodule/build setup that was not approved for this attempt. The repository-wide `tsc --noEmit` remains nonzero with errors outside the changed C085 files and missing generated Prisma types; the changed-file diagnostic check is clean.

### Deviations

Prisma-backed External and Shopify UI suites could not execute in this worktree. Their tests were migrated, but they need a rerun after the generated Prisma Client is made available through the approved setup workflow.

### Assumptions

COMMERCE-084 remains the sole source of Nunjucks grammar, canonical validation and server rendering; COMMERCE-078 remains the owner of local revision/checkpoint and Test freshness behavior.

### Unresolved Issues

The External and Shopify Admin UI integration suites remain unexecuted due to the missing generated Prisma Client. Architect review is pending.

### Architectural Concerns

None identified during implementation; architect review remains pending.

### VCS and Worktree

- Implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-085`, branch `task/ARCH-021-COMMERCE-085`, implementation commit `297123e` (`Implement generated Result Template authoring`), pushed.
- Parent task report: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-085`, branch `task/ARCH-021-COMMERCE-085`.
- The launcher prepared and claimed Attempt 1 in these dedicated task worktrees. The implementation baseline recorded in the handoff was `b78681d`; the initialized database submodule was at `4da3139`.
- The shared coordinator checkout and shared implementation checkout were not switched or modified for task implementation. The coordinator checkout's unrelated existing changes were left untouched. No submodule gitlink change was staged.
- The parent task report is committed and pushed separately on the matching task branch; Architect Review remains unchanged and pending.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is not accepted.

The broad C085 direction is correct and several important boundaries are already satisfied:

- the bespoke Text/Items/Collection form is replaced by one canonical `nunjucks.v1` source plus unavailable fallback;
- CodeMirror 6 is used without the JavaScript language extension;
- GENERATED / USER_MODIFIED origin and canonical result-contract fingerprint metadata are browser/session-only;
- existing persisted Tools restore as USER_MODIFIED;
- canonical Result Template validation remains COMMERCE-084-owned;
- validation response identity is guarded so a late result for source revision N cannot validate revision N+1;
- parent candidates persist only the canonical `responseTemplate`;
- React does not render Nunjucks; and
- new/persisted Tool integration is wired through the accepted C078/C079 state boundaries.

Four implementation corrections and one validation-record correction remain.

#### 1. Programmatic CodeMirror synchronisation is currently reported as a user edit

`ResultTemplateEditor` synchronises a new controlled `source` prop with:

```ts
if (current !== source) {
  view.dispatch({
    changes: { from: 0, to: current.length, insert: source },
  });
}
```

The same editor also registers:

```ts
EditorView.updateListener.of((update) => {
  if (update.docChanged) {
    emitChange(update.state.doc.toString());
  }
})
```

CodeMirror does not distinguish that controlled-prop dispatch from keyboard/user editing. Therefore a programmatic automatic generation or confirmed regeneration changes the document, fires `onChange`, and `ResultTemplateTab.authorEdit(...)` immediately executes:

```text
origin = USER_MODIFIED
validation = stale
parent onChange(...)
```

That violates R6/R7/R8/R10. A generated template must remain `GENERATED` until the user actually edits source or unavailable fallback.

This also breaks the core tracking rule: after the first automatic generation, a later valid Response change may no longer auto-regenerate because the session has been spuriously converted to USER_MODIFIED.

Attempt 2 must make controlled prop synchronisation silent with respect to the public `onChange` callback. Use a transaction annotation/effect, a bounded synchronisation guard or another CodeMirror-native mechanism that distinguishes parent synchronisation from user-originated edits.

Add integration regressions proving:

```text
A. automatic initial generation
   -> editor receives generated source
   -> no user-edit callback is emitted by prop synchronisation
   -> origin remains GENERATED

B. GENERATED template + valid Response A
   -> automatic generation A
   -> valid Response changes to B without any user edit
   -> automatic generation B occurs
   -> origin remains GENERATED

C. confirmed Regenerate from Response
   -> generated source is synchronised into CodeMirror
   -> origin remains GENERATED after the editor update

D. actual keyboard/source insertion edit
   -> onChange fires
   -> origin becomes USER_MODIFIED
```

Do not suppress real CodeMirror user edits.

#### 2. COLLECTION insertion logic duplicates the C084 generator in React

`result-template-tab.tsx` contains its own:

```text
aliases = ["item", "item2", "item3", "item4"]
humanize(...)
templateLines(...)
```

and recursively manufactures Nunjucks loop source.

That is a second client-side template-generation implementation. R12 explicitly requires COLLECTION snippets to use the deterministic alias/field structure supplied by the COMMERCE-084 generator/helper rather than recreating the grammar in React.

Attempt 2 must remove the duplicated React generation logic.

If C084 does not yet export a sufficiently narrow snippet helper, extract/export a pure provider-neutral helper from the existing C084 generator implementation and have both default generation and C085 insertion consume the same underlying node/alias generation semantics. This is a non-semantic reuse extraction: do not change the accepted `nunjucks.v1` grammar or default-generator output.

Add a regression proving the inserted COLLECTION / SCALAR ARRAY snippet is byte-for-byte the canonical helper output for the same schema/path and is accepted by `validateResponseTemplateAuthoring`.

#### 3. The result-data tree adds a synthetic `item` node that R11 does not specify

For an array, `ResultTreeNode` currently renders:

```text
items[]
  item
    department string
    description string
    ...
```

because it recursively renders the array item object with `name="item"`.

R11's required provider-neutral representation for an object collection is:

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

The array node represents the item scope already. Object-item properties must appear directly beneath `items[]`; do not insert a synthetic object label that is not in the canonical result path.

For scalar arrays it is reasonable to render a scalar `item <type>` child because there is no object-property path to display.

Add a DOM-structure regression, not merely a text-presence assertion, proving the six-field example has the fields directly beneath `items[]`.

#### 4. The accessible name is attached to the wrapper, not the actual CodeMirror editing surface

R2 requires:

```text
aria-label = "Result template source"
```

The implementation currently puts that label on the outer host `<div>`, while CodeMirror creates the actual `contenteditable`/textbox descendant.

The editable surface itself must expose the accessible name. Configure the CodeMirror content DOM (for example via CodeMirror content attributes or the equivalent supported API) so assistive technology sees:

```text
role/textbox + accessible name "Result template source"
```

The wrapper may keep presentation/data attributes, but it must not be the only labelled element.

Add a regression that locates the actual editable CodeMirror textbox by role and accessible name.

#### 5. The required External/Shopify integration validation was not executed and must not be recorded as passed

The task Validation section currently checks:

```text
External and Shopify Result Template UI tests updated; execution blocked before collection by the missing generated Prisma Client
```

The Completion Report confirms that neither suite collected tests because `.prisma/client/default` is absent.

Under the repository task protocol, required validation that did not execute must remain unchecked and be explained; "tests were updated" is not equivalent to the required integration suite passing.

These suites are especially relevant to C085 because the task must preserve the already-accepted C079 persisted-DRAFT and C081 External Test integrations while replacing their Result Template UI.

Attempt 2 must:

- reconcile that Validation item back to unchecked before execution;
- obtain the generated Prisma Client through the approved repository/setup path without modifying schema or performing an unrelated migration;
- run the required External and Shopify Admin UI suites;
- check the item only when the suites actually collect and pass;
- if the approved environment still cannot provide the generated client, return the task `blocked` with the exact environment gap rather than representing the validation as complete.

The repository-wide unrelated TypeScript baseline does not need to be fixed by C085. Continue to require clean changed-file diagnostics.

### Reviewed Files

- `src/studio/tools/authoring/result-template-editor.tsx`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/authoring-session.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/commerce/tool-authoring/result-template-generator.ts`
- `tests/result-template-tab.test.tsx`
- `tests/new-tool-authoring-state.test.ts`
- `tests/tool-authoring-screen.test.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- C085 Completion Report

### Validation Reviewed

Submitted Attempt 1 evidence:

- focused editor/state/session/screen packet: **63/63 tests passed**;
- targeted ESLint: passed;
- changed-file diagnostics: clean;
- `git diff --check`: passed;
- repository typecheck remains non-green on unrelated existing/generated-Prisma diagnostics;
- External and Shopify Admin UI suites did **not** collect because `.prisma/client/default` was missing.

The review archive contains no installed `node_modules`, so the submitted focused commands were inspected rather than independently rerun.

Source inspection additionally established:

- controlled CodeMirror prop synchronisation currently emits the same callback as a user edit;
- COLLECTION insertion maintains a React-local copy of C084's alias/loop generation semantics;
- object-array result-tree rendering introduces a synthetic `item` node; and
- the actual CodeMirror editable surface is not the element carrying the required accessible name.

### Architecture Conformance

Partial.

C085 conforms to the one canonical Nunjucks source/fallback model, C084 validation ownership, C078/C079 session metadata/persistence boundary and no-browser-rendering invariant.

Acceptance is blocked by:
1. programmatic source synchronisation being misclassified as a user modification;
2. duplicated client-side collection-generation semantics instead of C084 helper reuse;
3. incorrect object-array tree structure;
4. incomplete CodeMirror accessibility naming; and
5. required External/Shopify integration suites not having executed.

### Follow-up

Return the same task as Attempt 2.

Correct only the four bounded implementation issues above, reconcile/run the missing integration validation through the approved setup path, rerun the focused C085 packet plus changed-file lint/diagnostics and `git diff --check`, and STOP.

Do not change the accepted C084 grammar/runtime semantics, and do not reimplement C079/C081 lifecycle/Test behavior.

COMMERCE-083 remains Pending on C085.
