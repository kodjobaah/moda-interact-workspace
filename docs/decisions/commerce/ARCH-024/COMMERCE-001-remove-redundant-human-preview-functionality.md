---
id: ARCH-024-COMMERCE-001
architecture_id: ARCH-024
title: Remove redundant human-facing Preview functionality
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-10-01T15:18:07Z
attempt: 1
depends_on: []
enables:
  - ARCH-024-COMMERCE-004
created: 2026-09-30
updated: 2026-10-01
---

# Remove redundant human-facing Preview functionality

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Remove the obsolete human-facing synthetic Preview composition workflow from `moda-interact-commerce` and leave a deliberately minimal, selected-shop-aware **Test Conversations shell** on `/preview`, while preserving the backend run/reconciliation seams that are still required by accepted Tool Authoring/Code Response functionality or by later ARCH-024 Test Conversation tasks.

This is the first ARCH-024 Commerce task. It is intentionally subtractive. It MUST NOT implement Feature composition, effective model resolution, selected-shop Tool execution or OpenRouter execution.

## Context

The current integrated Commerce baseline still exposes the pre-ARCH-024 Preview design.

`app/preview/page.tsx` currently:

```text
requires Studio Admin
resolves the selected Studio shop
loads every saved Tool
loads every saved Release
maps both into Preview sources
renders title "Synthetic preview"
passes Tool/Release sources into PreviewScreen
```

`src/studio/preview/preview-screen.tsx` currently combines two separate human workflows:

```text
Tool test
Conversation test
```

and exposes/maintains state for:

```text
Tool source
Release source
Saved selection
RELEASE / DRAFT selection
Fixture scenario
FIXTURE / MODEL mode
Release-derived Capability composition
Tool-test argument authoring
Tool-test polling/reconciliation
synthetic conversation execution
```

Release authoring also contains a Preview handoff:

```text
Release composer
    -> Test conversation
    -> composer.setRelease(...)
    -> /preview?source=release-composer
```

`StudioComposerContext` carries Preview-only Tool handoff state and bypasses the normal dirty-navigation guard when navigation targets `/preview` with a Tool/Release handoff.

ARCH-024 deliberately does **not** evolve that human workflow in place. The replacement Test Conversation experience is intentionally **not** one serial Commerce chain. This task establishes the clean human-UI/runtime seam required by COMMERCE-004, while database-backed model resolution proceeds independently through DATABASE-001 + SHARED-002:

```text
ARCH-024-COMMERCE-001   remove obsolete human Preview composition
        |
        v
ARCH-024-COMMERCE-004   compose Test Conversations from selected Features
        |
        +--------------------------+
                                   |
DATABASE-001 + SHARED-002          |
        |                          |
        v                          |
ARCH-024-COMMERCE-002              |
resolve effective available +      |
SHOP -> PRICING_PLAN -> PLATFORM    |
        |                          |
        +--> ARCH-024-COMMERCE-003 |
             Studio selection-only |
             (after ADMIN-002)     |
                                   |
ARCH-023-COMMERCE-003 -------------+
                                   v
ARCH-024-COMMERCE-005   build Test Conversations UI + complete authored snapshot
        |
        v
ARCH-024-COMMERCE-006   execute Tools against selected real shop
        |
        v
ARCH-024-COMMERCE-007   execute snapshot model through OpenRouter
```

The cleanup must nevertheless preserve reusable backend infrastructure. In particular, the current Code Response production path directly uses:

```text
POST /api/studio/preview/tool-tests
GET  /api/studio/preview/tool-tests/:runId
POST /api/studio/preview/tool-tests/:runId/cancel
```

through `src/studio/code-response/production-port.ts`. Deleting those routes or their required service/store semantics would regress accepted Tool Authoring functionality and is forbidden by this task.

The current conversation run/store/service infrastructure may be temporarily unused by a human UI after this task, but ARCH-024-COMMERCE-004..007 are expected to reuse or deliberately replace it. Do not perform speculative backend rewrites in this cleanup task.

ARCH-021-COMMERCE-105..109 remain unstarted and are being superseded by ARCH-024. This repository task MUST NOT edit their task files or architecture coordination state; `moda_architect` owns that reconciliation.

## Scope

The implementation is restricted to removing obsolete **human-facing** Preview composition and the handoff state used only to reach it.

### Mandatory source targets

Inspect and, where specified below, modify/delete these files:

```text
moda-interact-commerce/app/preview/page.tsx
moda-interact-commerce/src/studio/preview/preview-screen.tsx
moda-interact-commerce/src/studio/preview/client.ts
moda-interact-commerce/components/studio-workspace.tsx
moda-interact-commerce/components/studio-composer-context.tsx
moda-interact-commerce/components/preview-handoff.tsx
moda-interact-commerce/tests/preview-screen.test.tsx
moda-interact-commerce/tests/preview-client.test.ts
moda-interact-commerce/tests/studio-workspace.test.tsx
```

Create the replacement minimal shell at exactly:

```text
moda-interact-commerce/src/studio/test-conversations/test-conversations-screen.tsx
moda-interact-commerce/tests/test-conversations-screen.test.tsx
```

Additional Commerce files may be changed only when the mandatory reference audit in R1 proves they belong exclusively to the removed human flow or are required to keep retained consumers compiling. Every additional file MUST be named and justified in the Completion Report.

### Explicitly retained boundaries

This task MUST preserve these backend/publication boundaries unless the reference audit reveals that a narrower internal refactor is required solely to keep the same behaviour:

```text
app/api/studio/preview/conversations/**
src/commerce/preview/**
lib/preview/**

app/api/studio/preview/tool-tests/**
src/commerce/external-preview/**
src/studio/code-response/**

src/commerce/integration/preview/model-provider.ts
lib/server/config.ts Preview provider/model/key configuration
COMMERCE_PREVIEW_ENABLED
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

The static Preview model/provider/key configuration is intentionally retained for now. ARCH-024-COMMERCE-007 plus the later Gateway cutover own replacing/removing that runtime dependency.

## Out of Scope

- Implementing Feature selection or Feature -> Capability composition.
- Implementing the new Test Conversation API contract.
- Resolving Model Availability or the one effective active model.
- Changing Commerce Studio Agent Configuration model selection.
- Adding LangChain, OpenRouter or `CommerceModelClient` dependencies.
- Reading ARCH-024 database/shared model contracts in Commerce.
- Executing Shopify/External/Policy Tools against the selected real shop.
- Changing production Background CommerceAgent execution.
- Removing `COMMERCE_PREVIEW_PROVIDER`, `COMMERCE_PREVIEW_MODEL`, `COMMERCE_PREVIEW_API_KEY` or their model-provider implementation.
- Gateway/Render edits.
- Database changes.
- Editing ARCH-021-COMMERCE-105..109 task files or statuses.
- Deleting retained Preview backend infrastructure merely because the human UI no longer calls it during this intermediate task.

## Requirements

### R1 — Mandatory reference audit before deletion

Before changing source, run from `moda-interact-commerce`:

```bash
rg -n --hidden \
  --glob '!node_modules/**' \
  --glob '!tsconfig.tsbuildinfo' \
  'PreviewScreen|PreviewHandoff|source=release-composer|Test conversation|Tool source|Release source|Saved selection|Fixture scenario|Model mode|selectedToolRevisionId|selectedReleaseId|selectionKey|modelMode|composer\.tool|setTool\(|toolRef|runToolTest|getToolTest|/api/studio/preview/tool-tests|/api/studio/preview/fixtures|COMMERCE_PREVIEW_PROVIDER|COMMERCE_PREVIEW_MODEL|COMMERCE_PREVIEW_API_KEY' \
  app components src lib tests
```

Record a table in the Completion Report with these columns:

```text
Symbol / route
Current path(s)
Current supported consumer
Disposition: REMOVE | RETAIN | DEFER
Reason
```

Classification rules are deterministic:

```text
REMOVE
    only human-facing old /preview UI or its Preview handoff

RETAIN
    currently required by accepted Tool Authoring/Code Response functionality
    OR explicitly retained backend conversation infrastructure listed in Scope

DEFER
    runtime/config/backend seam deliberately replaced by a later ARCH-024 task
```

Tests alone are not a production consumer. A production route whose only consumers are the deleted UI and tests may be deleted, and the obsolete tests must then be removed/reworked.

### R2 — `/preview` becomes a minimal selected-shop-aware Test Conversations shell

Rewrite `app/preview/page.tsx` so that it performs **only**:

```text
requireStudioAdminPage()
await searchParams
resolveStudioShopSelection(query.shopId)
render StudioScreen
render TestConversationsScreen
```

It MUST NOT import or call:

```text
listTools
listReleases
CommerceToolDefinitionSchema
PreviewScreen
```

It MUST NOT construct Tool/Release Preview source props or source notices.

Use these StudioScreen values exactly:

```text
path    = "preview"
eyebrow = "TEST CONVERSATIONS"
title   = "Test conversations"
```

Continue passing the result of `resolveStudioShopSelection(query.shopId)` to `StudioScreen.shopSelection`. The selected-shop control remains visible because the replacement experience will be shop-scoped.

`searchParams` for this task supports only:

```ts
{ shopId?: string }
```

Do not preserve or parse `source=release-composer`.

### R3 — create one minimal replacement shell

Create:

```text
src/studio/test-conversations/test-conversations-screen.tsx
```

with a zero-prop exported component:

```ts
export function TestConversationsScreen(): JSX.Element
```

The component is presentation-only and MUST NOT:

```text
create a Preview client
read StudioComposerContext
load fixtures
load Tools
load Releases
start conversations
run Tools
poll runs
accept a model/fixture/source prop
```

Its rendered DOM MUST contain:

```text
<section aria-labelledby="test-conversations-heading">
<h2 id="test-conversations-heading">Test conversations</h2>
<p>The Feature-composed Test Conversation experience will be configured by ARCH-024.</p>
</section>
```

The exact text above is the temporary development shell. Later ARCH-024 tasks replace it.

The canonical replacement human UI module is now:

```text
src/studio/test-conversations/**
```

ARCH-024-COMMERCE-005 MUST continue from this module. It MUST NOT recreate the deleted `src/studio/preview/preview-screen.tsx` or `src/studio/preview/client.ts` browser implementation. The `/preview` route name remains only the URL/server route boundary; it does not make `src/studio/preview/**` the owner of the new human UI.

### R4 — delete the old human Preview screen and browser Preview client

Delete:

```text
src/studio/preview/preview-screen.tsx
src/studio/preview/client.ts
tests/preview-screen.test.tsx
tests/preview-client.test.ts
```

This deletion is mandatory because repository reference inspection shows that the browser `PreviewClient` is consumed only by the obsolete `PreviewScreen` and its tests in the current baseline.

Do **not** reuse the old client as the starting point for later ARCH-024 work. ARCH-024-COMMERCE-004 defines the server-side Feature composition boundary and ARCH-024-COMMERCE-005 MUST define the replacement browser contract/client under `src/studio/test-conversations/**`.

### R5 — remove Release -> Preview handoff, preserve Release cloning

In `components/studio-workspace.tsx`, remove only the Release Composer action whose accessible name is:

```text
Test conversation
```

Delete its complete handler, including:

```text
composer.setRelease({ ...preview handoff... })
navigate("/preview?source=release-composer")
```

Do not change:

```text
Create immutable release
Validate
Edit as new release
/release clone/edit-as-new behaviour
composer.setRelease used for Release cloning
```

`ReleaseDetail` must continue to use `composer.setRelease(...)` for `Edit as new release` and navigate to the Release authoring/clone flow, not Preview.

### R6 — simplify StudioComposerContext deterministically

In `components/studio-composer-context.tsx`:

1. delete `ToolComposerState`;
2. delete `tool` from `ComposerContextValue`;
3. delete `setTool` from `ComposerContextValue`;
4. delete `tool` state;
5. delete `toolRef`;
6. delete the Preview handoff condition:

```ts
nextDestination.startsWith('/preview') && Boolean(...)
```

7. restore the normal navigation-blocker rule for `/preview` exactly like any other destination;
8. keep `ReleaseComposerState`, `release`, and `setRelease` because Release cloning/edit-as-new still uses them;
9. remove `releaseRef` if, after deleting the Preview bypass, it has no remaining reference;
10. remove the `ToolDefinition` type import if it becomes unused.

The resulting `requestNavigation` rule must be equivalent to:

```ts
if (!preserveDraft && blocker.current?.blocked) {
  // existing pending-navigation behaviour
  return;
}

beforeNavigate?.();
navigate(nextDestination);
```

Do not weaken dirty-navigation or locked-operation protections.

### R7 — delete PreviewHandoff

Delete:

```text
components/preview-handoff.tsx
```

and remove every import/reference to it.

There must be no supported path that displays:

```text
Fixture preview only
Release candidate ready
Back to release composer
```

as Preview-handoff UI.

### R8 — production Code Response Tool-test routes are retained

The following route family MUST remain:

```text
POST /api/studio/preview/tool-tests
GET  /api/studio/preview/tool-tests/:runId
POST /api/studio/preview/tool-tests/:runId/cancel
```

because `src/studio/code-response/production-port.ts` currently calls those routes directly.

Preserve the underlying service/store contracts necessary for:

```text
External Code Response sample execution
read/reconcile sample run
cancel sample run
UNKNOWN outcome semantics
```

At minimum these existing focused tests must remain green:

```text
tests/code-editor.test.tsx
tests/code-response-processor.test.ts
tests/external-preview.test.ts
tests/external-wiring.test.ts
tests/preview-service.test.ts
tests/preview-store.test.ts
```

Do not rename the retained route in this task.

### R9 — fixture catalogue route is reference-driven

After R4, re-run:

```bash
rg -n --hidden \
  --glob '!node_modules/**' \
  --glob '!tsconfig.tsbuildinfo' \
  '/api/studio/preview/fixtures|listFixtures\(' \
  app components src lib tests
```

If `app/api/studio/preview/fixtures/route.ts` has no non-test production consumer after deletion of the old browser Preview client, delete the HTTP route and delete route/client tests that exist only for that production endpoint.

Do **not** delete fixture definitions or `PreviewService.listFixtures()` solely because this route becomes unused if retained backend/unit tests or deferred Preview internals still use them. This task removes the obsolete HTTP/UI surface, not every fixture implementation detail.

Record the result in the Completion Report.

### R10 — conversation backend remains available for later ARCH-024 work

Do not delete or redesign:

```text
app/api/studio/preview/conversations/**
src/commerce/preview/service.ts
src/commerce/preview/store.ts
src/commerce/preview/redis-store.ts
src/commerce/preview/types.ts
lib/preview/runtime.ts
lib/preview/http.ts
```

solely because the temporary Test Conversations shell does not invoke them.

Later ARCH-024 tasks own changing the conversation creation/composition contract and selected-shop runtime semantics.

Any compilation-only edit to these files requires an explicit explanation in the Completion Report and MUST NOT change their behaviour.

### R11 — static Preview model configuration is deferred, not deleted

This task MUST NOT remove or rename:

```text
COMMERCE_PREVIEW_ENABLED
COMMERCE_PREVIEW_PROVIDER
COMMERCE_PREVIEW_MODEL
COMMERCE_PREVIEW_API_KEY
```

or the existing Preview model-provider implementation/tests.

They are intentionally DEFERRED until ARCH-024-COMMERCE-007 and the Gateway cutover can replace model execution atomically.

### R12 — tests must prove subtraction and retained behaviour

Create:

```text
tests/test-conversations-screen.test.tsx
```

It MUST render `TestConversationsScreen` and assert:

```text
heading "Test conversations" exists
ARCH-024 temporary explanatory copy exists
```

and assert the DOM does **not** contain any of:

```text
Tool source
Release source
Tool test
Saved selection
Draft revisions
Fixture scenario
Model mode
Run tool test
```

Update `tests/studio-workspace.test.tsx` so that:

1. it no longer imports `PreviewHandoff`;
2. it no longer expects the Release Composer `Test conversation` button;
3. Release creation still validates and creates an immutable release;
4. Release edit-as-new/clone composer state remains supported by existing/replacement coverage;
5. dirty-navigation tests remain unchanged unless compilation requires a bounded update.

Add a focused source/reference regression at:

```text
tests/arch024-preview-cleanup.test.ts
```

This test may read repository source files and MUST assert absence of these strings from the human UI/handoff files:

```text
source=release-composer
Test conversation
PreviewHandoff
composer.tool
Tool source
Saved selection
Fixture scenario
Model mode
```

Scope that source guard to the human-facing files changed by this task; do not globally reject terms that are legitimately retained in backend fixture/model tests.

### R13 — no compatibility flags or hidden old controls

The removed human functionality MUST be deleted, not hidden behind:

```text
feature flags
query parameters
CSS
disabled controls
development-only branches
alternate tabs
```

After this task there is exactly one human `/preview` surface: the temporary ARCH-024 Test Conversations shell.

## Work Items

- [ ] Run and record the mandatory R1 reference audit before editing source.
- [ ] Rewrite `app/preview/page.tsx` to the exact minimal selected-shop-aware shell contract in R2.
- [ ] Create `src/studio/test-conversations/test-conversations-screen.tsx` exactly as specified in R3.
- [ ] Delete the old `PreviewScreen`, browser `PreviewClient`, and their obsolete tests per R4.
- [ ] Remove Release Composer `Test conversation` -> `/preview?source=release-composer` handoff while preserving Release cloning.
- [ ] Remove Preview-only Tool composer state and the `/preview` dirty-navigation bypass from `StudioComposerContext`.
- [ ] Delete `components/preview-handoff.tsx` and all references.
- [ ] Preserve Code Response Tool-test production routes/service behaviour and prove the required focused suites remain green.
- [ ] Re-audit `/api/studio/preview/fixtures`; delete the HTTP route only if no non-test production consumer remains.
- [ ] Leave conversation backend and static Preview model configuration deferred and behaviourally unchanged.
- [ ] Add the replacement shell test and bounded ARCH-024 source/absence guard.
- [ ] Run the required focused and repository validation.
- [ ] Record every retained legacy-looking Preview seam and its concrete consumer/deferred owner in the Completion Report.

## Interfaces / Contracts

This cleanup task introduces **no new cross-service runtime contract**.

It preserves these current internal interfaces for subsequent ARCH-024 work:

```text
Preview conversation run/store/service infrastructure
Tool-test routes required by Code Response
selected Studio shop resolution on /preview
```

The temporary human shell has no API/client contract.

Downstream contract ownership:

```text
ARCH-024-COMMERCE-004
    defines Feature-composed conversation creation/composition

ARCH-024-COMMERCE-005
    extends `src/studio/test-conversations/**` with the replacement human Test Conversations contracts/client/UI

ARCH-024-COMMERCE-006
    defines selected-shop Tool execution

ARCH-024-COMMERCE-007
    defines OpenRouter model execution/cutover
```

## Dependencies

None.

This task may be implemented before ARCH-024 database/shared model work because it is a subtractive UI/handoff cleanup and explicitly leaves model runtime configuration untouched.

## Enables

- `ARCH-024-COMMERCE-004`

## Acceptance Criteria

- [ ] `/preview` authenticates, resolves the selected Studio shop and renders only the minimal ARCH-024 Test Conversations shell.
- [ ] `/preview` does not call `listTools()` or `listReleases()` and does not parse Tool definitions for Preview sources.
- [ ] `src/studio/preview/preview-screen.tsx` is deleted.
- [ ] `src/studio/preview/client.ts` is deleted.
- [ ] The canonical replacement human UI module is `src/studio/test-conversations/**`; later ARCH-024 tasks must not recreate the deleted Preview screen/client.
- [ ] The old Preview screen/client tests are deleted rather than rewritten to preserve old behaviour.
- [ ] The Release Composer no longer exposes a `Test conversation` button or navigates to `source=release-composer`.
- [ ] Release `Edit as new release`/clone behaviour remains intact.
- [ ] `StudioComposerContext` contains no Preview-only Tool handoff state and no special `/preview` dirty-navigation bypass.
- [ ] `components/preview-handoff.tsx` is deleted and unreferenced.
- [ ] Normal `/preview` DOM contains none of the old Tool/Release/Fixture/Model-mode controls.
- [ ] Code Response sample execution can still POST/read/cancel `/api/studio/preview/tool-tests` with its existing semantics.
- [ ] Conversation backend infrastructure remains available and behaviourally unchanged for later ARCH-024 tasks.
- [ ] Static Preview model/provider/API-key configuration remains available and behaviourally unchanged for the later atomic model-runtime cutover.
- [ ] `/api/studio/preview/fixtures` is either deleted because no non-test consumer remains or explicitly retained with a named production consumer; tests alone are not sufficient reason to retain the HTTP route.
- [ ] No removed human functionality is hidden behind compatibility flags or alternate UI branches.
- [ ] Completion Report contains the required REMOVE/RETAIN/DEFER reference-audit table.

## Validation

Run from `moda-interact-commerce` after first inspecting `package.json` as required by repository policy.

### Focused UI/navigation cleanup

```bash
npx vitest run \
  tests/test-conversations-screen.test.tsx \
  tests/arch024-preview-cleanup.test.ts \
  tests/studio-workspace.test.tsx
```

### Retained Code Response / Tool-test boundary

```bash
npx vitest run \
  tests/code-editor.test.tsx \
  tests/code-response-processor.test.ts \
  tests/external-preview.test.ts \
  tests/external-wiring.test.ts \
  tests/preview-service.test.ts \
  tests/preview-store.test.ts
```

If the reference-driven R9 decision retains/deletes the fixtures HTTP route, run the corresponding affected Preview route tests and record exactly which assertions were removed or preserved:

```bash
npx vitest run tests/preview-routes.test.ts
```

### Static reference audit after changes

```bash
rg -n --hidden \
  --glob '!node_modules/**' \
  --glob '!tsconfig.tsbuildinfo' \
  'source=release-composer|PreviewHandoff|composer\.tool|Tool source|Release source|Saved selection|Fixture scenario|Model mode' \
  app components src tests
```

Expected result: no matches in human Preview/Release/Composer UI paths. Any remaining match MUST be a deliberately retained backend/test fixture and documented in the Completion Report.

Also prove Code Response still owns the Tool-test route:

```bash
rg -n "/api/studio/preview/tool-tests" src/studio/code-response app/api/studio/preview/tool-tests tests
```

### Repository validation

```bash
npm run typecheck
npm run lint -- \
  app/preview/page.tsx \
  components/studio-workspace.tsx \
  components/studio-composer-context.tsx \
  src/studio/test-conversations/test-conversations-screen.tsx \
  tests/test-conversations-screen.test.tsx \
  tests/arch024-preview-cleanup.test.ts \
  tests/studio-workspace.test.tsx
npm run build
git diff --check
```

If targeted `npm run lint -- <files>` is not accepted by the repository script/runtime, run the repository's declared `npm run lint` instead and record that exact command/result. Do not invent a different lint contract.

All required validation items must pass or be left unchecked with the exact blocker recorded in the Completion Report.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. update only this task's execution metadata, Work Items, Acceptance Criteria, Validation and Completion Report;
2. set Completion Report status to `Ready for Review`;
3. set task status to `review`;
4. return control to `moda_architect`;
5. STOP.

Do not begin `ARCH-024-COMMERCE-004` or any other ARCH-024 task. COMMERCE-002 is independently gated by Database + Shared publication and may execute in parallel once those dependencies are Complete.

## Implementation Notes

This task is intentionally a **clean-sheet preparation task**, not the new Test Conversation implementation.

Prefer deletion over compatibility code. The target intermediate state is allowed to have a minimal Test Conversations page while later ARCH-024 tasks are pending because Moda is still in development.

Do not interpret "clean sheet" as permission to remove reusable backend correctness machinery. In particular, Tool-test run reconciliation used by Code Response and the conversation run/store semantics reserved for later ARCH-024 work remain valid infrastructure until an owning later task replaces them deliberately.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Reference Audit

Not Run

Required final table:

| Symbol / route | Current path(s) | Current supported consumer | Disposition | Reason |
|---|---|---|---|---|

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
