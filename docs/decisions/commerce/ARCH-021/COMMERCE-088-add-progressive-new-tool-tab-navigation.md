---
id: ARCH-021-COMMERCE-088
architecture_id: ARCH-021
title: Add progressive Previous/Next traversal to new Tool authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 77
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-078
  - ARCH-021-COMMERCE-083
enables:
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-29
updated: 2026-09-29
---

# Add progressive Previous/Next traversal to new Tool authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add deterministic progressive traversal to **new Tool creation only** so the six canonical authoring tabs are visible from session start, `Previous`/`Next` controls first-time forward progression, and any tab remains freely clickable after it has once been enabled for the current provider authoring path.

## Context

The accepted new-Tool flow is:

```text
Tool Definition -> Request -> Response -> Result Template -> Test -> Review
```

The current snapshot renders only Tool Definition until a provider is selected and then makes the entire remaining tab set freely clickable. C078 deliberately deferred general Next/Previous traversal. The current code already has the provider-specific readiness signals needed for deterministic progression:

```text
Tool Definition:
  validateNewToolDefinition(...) + selected/loaded provider draft

External Request:
  ExternalHttpRequestTab current request validation

Shopify Request:
  adminMappingValid + adminValidated

External Response:
  externalResponseValid

Shopify Response:
  adminResultContractFresh

Result Template:
  resultTemplateValid

Test:
  isCurrentTestPassed(authoringState)
```

This task adds navigation state and presentation only. It must reuse those accepted validation/Test boundaries rather than inventing a second validation system.

The user's navigation rule is a hard invariant:

> Validation may gate the **first unlock** of the next step, but once a tab has been enabled it remains directly clickable even if an earlier/current section is later edited, becomes dirty, invalid, stale or untested. Persistence readiness remains independently enforced by the existing Review/Save gate.

## Scope

Primary implementation areas:

```text
moda-interact-commerce/src/studio/tools/new-tool-authoring-state.ts
moda-interact-commerce/src/studio/tools/new-tool-editor.tsx
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-tabs.tsx
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-navigation.ts       # new pure step/order helpers
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-step-navigation.tsx # new Previous/Next presentation
moda-interact-commerce/src/studio/tools/authoring-session.ts
moda-interact-commerce/src/studio/external-http/editor.tsx                          # expose existing Request validation only if required
```

Focused tests:

```text
moda-interact-commerce/tests/tool-authoring-screen.test.tsx
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/shopify-admin-tools-ui.test.tsx
moda-interact-commerce/tests/authoring-session.test.ts
```

Use the actual current filenames if a focused session test is named differently; do not create a duplicate test harness merely to satisfy this list.

## Out of Scope

- Persisted-DRAFT (`ToolEditor`) tab gating or Previous/Next controls.
- Changing the canonical six-step order or labels.
- Changing Request, Response, Result Template or Test validation semantics.
- Adding automatic validation when `Next` is pressed.
- Reimplementing External or Shopify live Test.
- Changing C081/C083 Test result contracts.
- Changing C084/C087 Nunjucks runtime/generator semantics.
- Changing the C085 Result Template editor.
- Changing C086 user-guide packaging/link behaviour.
- Changing Create/Save/Cancel persistence semantics.
- Database, Shared, Background, Gateway or system-test implementation.
- Turning the flow into a modal wizard that prevents revisiting already-enabled tabs.

## Requirements

### R1 — one canonical new-Tool step order

Create one pure Commerce Studio navigation module containing the exact new-Tool order:

```ts
export const NEW_TOOL_AUTHORING_STEPS = [
  "tool-definition",
  "request",
  "response",
  "result-template",
  "test",
  "review",
] as const;

export type NewToolAuthoringStepId =
  (typeof NEW_TOOL_AUTHORING_STEPS)[number];
```

`ToolAuthoringTabs` and the Previous/Next logic must consume this same order. Do not maintain a second independently ordered six-step array for new Tool navigation.

The existing persisted Tool tab order may continue to use its current representation; this task must not alter persisted-DRAFT behaviour.

### R2 — session-scoped unlock frontier

Extend `NewToolAuthoringState` with exactly one navigation frontier:

```ts
type NewToolAuthoringNavigationState = {
  enabledThrough: NewToolAuthoringStepId;
};
```

Initial new Tool state is exactly:

```ts
navigation: {
  enabledThrough: "tool-definition"
}
```

Meaning:

```text
Tool Definition   enabled
Request           disabled
Response          disabled
Result Template   disabled
Test              disabled
Review            disabled
```

This is browser/session state only. It must not be persisted to Tool, ToolRevision, audit, operation receipt or another durable record.

### R3 — all six tabs are always visible during new Tool creation

Remove the current new-Tool `definitionOnly` behaviour that hides later steps before provider selection.

From the moment `Create Tool` enters the local authoring session, render all six tabs in canonical order.

For a step after `navigation.enabledThrough`, render its tab button with the native `disabled` attribute and `aria-disabled="true"`.

For every step at or before `navigation.enabledThrough`, the tab is enabled and directly clickable.

Do not hide locked steps. The user must be able to see the complete authoring flow.

### R4 — enabled tabs never re-lock because authoring becomes dirty/stale/invalid

Within one provider authoring path, `enabledThrough` is monotonic: it may move forward but MUST NOT move backward because:

```text
Tool Definition is edited
Request is edited
Request validation becomes stale/invalid
Response is edited/stale/invalid
Result Template is edited/stale/invalid
Test becomes FAILED or STALE
Test arguments change
selected shop changes
user navigates backward
user clicks any already-enabled tab
```

Those conditions continue to affect validation/Test/Save readiness through their existing owners, but they must not remove direct access to an already-enabled tab.

The only normal flow allowed to reset `enabledThrough` is the confirmed destructive provider/type change defined by R9.

### R5 — direct tab clicks obey only the unlock frontier

When the user clicks a tab whose step index is less than or equal to `enabledThrough`, navigate to that tab immediately.

Do NOT re-check the clicked tab's predecessor validation at click time.

Therefore this is required behaviour:

```text
Request was once valid
Response was unlocked
user returns to Request
user edits Request so it is now stale/invalid
Response remains enabled
clicking Response still navigates to Response
```

Save/Create may remain disabled because current authoring state is no longer save-ready. Navigation access and persistence readiness are separate concerns.

Clicks on disabled future tabs must not change the active step or unlock state.

### R6 — exact `Previous` semantics

Add one shared new-Tool step-navigation component with button label exactly:

```text
Previous
```

Rules:

```text
Tool Definition: no Previous button
Request:         Previous -> Tool Definition
Response:        Previous -> Request
Result Template: Previous -> Response
Test:            Previous -> Result Template
Review:          Previous -> Test
```

`Previous`:

- never performs validation;
- never changes `enabledThrough`;
- never changes Tool data;
- never changes dirty state merely because it was clicked;
- never performs a durable write;
- remains usable regardless of current step validity because its destination is already enabled.

### R7 — exact `Next` semantics

Add one shared button labelled exactly:

```text
Next
```

There is no `Next` button on Review.

For every other step, calculate `nextStep` from `NEW_TOOL_AUTHORING_STEPS`.

There are two distinct cases.

#### Case A — the next step is already enabled

If `nextStep` is already at or before `navigation.enabledThrough`:

```text
Next is enabled.
Clicking Next navigates to nextStep.
Do not revalidate the current step.
Do not re-lock/re-unlock anything.
```

This rule is mandatory so `Next` does not become more restrictive than directly clicking an already-enabled tab.

#### Case B — the next step has never been enabled

If `nextStep` is beyond `navigation.enabledThrough`:

```text
Next is enabled only when the current step satisfies the exact first-unlock predicate in R8.
```

On click, in one local transition:

```text
1. advance enabledThrough to nextStep;
2. set active step to nextStep.
```

Do not unlock more than one step at a time.

`Next` MUST NOT automatically invoke a validation Server Action. The user completes the existing validation/Test action in the owning tab; `Next` only consumes its current accepted readiness signal.

### R8 — exact first-unlock predicates

Use these predicates and no substitute validation implementation.

#### Tool Definition -> Request

First unlock is allowed only when all are true:

```text
state.tool.kind is SHOPIFY_ADMIN_GRAPHQL or EXTERNAL_HTTP
state.providerDraft is non-null
validateNewToolDefinition(state.tool) returns no field errors
state.tool.description.trim().length > 0
there is no unconfirmed provider-switch dialog awaiting user choice
provider metadata/draft selection has completed successfully
```

Do not require Request validation here.

#### Request -> Response

External HTTP:

```text
current External Request candidate is structurally valid
AND
its current canonical Request validation has succeeded
```

Consume the existing `ExternalHttpRequestTab`/`ExternalHttpEditor` current-validation signal. If that signal is currently private to `ExternalHttpEditor`, expose it upward with one callback. Do not call `validateExternalRequestAction` a second time from navigation code.

Shopify Admin:

```text
adminMappingValid === true
AND
adminValidated === true
```

Consume the existing current values from `NewToolWorkspace`.

#### Response -> Result Template

External HTTP:

```text
externalResponseValid === true
```

Shopify Admin:

```text
adminResultContractFresh === true
```

Do not derive another Response-valid flag.

#### Result Template -> Test

Both providers:

```text
resultTemplateValid === true
```

Use the C085/C084 canonical Result Template validation result already exposed to `NewToolWorkspace`.

#### Test -> Review

Both providers, after C083:

```text
isCurrentTestPassed(authoringState) === true
```

Do not infer Test success from rendered text, provider HTTP success, a local provider result object, or the presence of diagnostics.

### R9 — provider/type changes reset the navigation path only after confirmation

Existing provider-change confirmation semantics remain authoritative.

When changing from one already-selected provider kind to the other:

```text
SHOPIFY_ADMIN_GRAPHQL <-> EXTERNAL_HTTP
```

before confirmation:

```text
keep current provider
keep active step
keep enabledThrough
```

If the user presses the existing Cancel action:

```text
no provider change
no navigation change
```

If the user confirms the destructive provider reset and the new provider draft is successfully established:

```text
active step = "tool-definition"
navigation.enabledThrough = "tool-definition"
```

Request/Response/Result Template/Test reset continues to follow the existing provider-reset implementation.

Selecting the initial provider from `kind === null` does NOT automatically enable Request. After successful initial provider selection, the user remains on Tool Definition and presses `Next` when R8's Tool Definition predicate is satisfied.

Re-selecting the same provider kind must not reset navigation.

### R10 — Explore Shopify round trip preserves unlock state

The new Tool Shopify Explore flow leaves `/tools` temporarily and restores the browser authoring session from `sessionStorage`. Preserve the navigation frontier through that round trip.

Extend the existing strict `ToolAuthoringSession.editor` contract with the optional field:

```ts
enabledThrough?: NewToolAuthoringStepId;
```

Do not bump `TOOL_AUTHORING_SESSION_VERSION`; this is an optional backwards-compatible field.

When opening Explore Shopify from a new Tool Request, write the current `navigation.enabledThrough` into `editor.enabledThrough`.

On restore for `mode === "new"`:

```text
if editor.enabledThrough is present and valid:
    restore it
else:
    use editor.section when it is one of the six new-Tool steps
    otherwise use "tool-definition"
```

After computing the restored frontier, ensure the restored active `editor.section` itself is enabled by taking the later of:

```text
restored enabledThrough
restored section
```

Do not unlock any step after the restored active section merely because the Explore round trip occurred.

The normal confirmed provider-reset rule in R9 may subsequently reset this restored frontier.

### R11 — one shared navigation presentation; no provider-specific button copies

Create one reusable presentation component, mechanically equivalent to:

```tsx
<ToolAuthoringStepNavigation
  step={activeStep}
  previousStep={...}
  nextStep={...}
  nextEnabled={...}
  onPrevious={...}
  onNext={...}
/>
```

Use it for the new Tool flow regardless of provider.

Do not put separate hard-coded Previous/Next buttons inside:

```text
ExternalHttpRequestTab
ExternalHttpResponseTab
ExternalHttpTestTab
ShopifyAdminEditor
ShopifyAdminResponseEditor
ShopifyAdminTestTab
ResultTemplateTab
ReviewTab
```

The navigation controls are authoring-shell concerns, not provider-tab concerns.

Render exactly one visible navigation footer for the active new-Tool step, visually after that step's authoring content.

Review keeps its existing Cancel/Save controls. Its navigation footer contains Previous only.

### R12 — preserve Save/Create readiness independently

Do not weaken or replace the existing Review/Create gate.

Unlocking or clicking Review does NOT imply the Tool is saveable.

If Review was previously enabled and the user later makes any required section stale/invalid or makes the current Test stale/failed:

```text
Review remains enabled/clickable
Save remains disabled by the existing current validation/Test gate
```

Do not create a second `canSave` calculation in navigation code.

### R13 — persisted DRAFT behaviour is unchanged

This task applies only when:

```text
ToolAuthoringTabs mode === "new-tool"
```

For persisted Tool editing:

```text
all existing tabs remain directly clickable as today
no progressive enablement is added
no Previous/Next navigation footer is added
ToolEditor is not refactored for this task
```

Any future persisted-DRAFT traversal design requires a separate task.

### R14 — navigation is non-durable and side-effect free

The following operations perform zero Tool/ToolRevision/audit/operation-receipt writes:

```text
unlock next step
Previous
Next
click already-enabled tab
click disabled tab
restore enabledThrough from sessionStorage
```

Navigation state must not be included in `CommerceToolDefinition`, provider execution definitions, Result Template, Agent Contract or saved Tool metadata.

## Work Items

- [ ] Add the pure canonical new-Tool step order/helpers.
- [ ] Add `navigation.enabledThrough` to `NewToolAuthoringState` with `tool-definition` initial state.
- [ ] Render all six new-Tool tabs from session start and disable only steps beyond the frontier.
- [ ] Make enabled tab clicks depend only on the frontier, not current validation freshness.
- [ ] Add the shared Previous/Next presentation component.
- [ ] Implement exact Case A / Case B Next behaviour from R7.
- [ ] Wire the exact R8 first-unlock predicates for both providers without adding validation calls.
- [ ] Expose current External Request validation upward if necessary; do not duplicate validation.
- [ ] Reset the frontier only on a confirmed successful provider-kind replacement.
- [ ] Preserve frontier + active step through new-Tool Explore Shopify sessionStorage handoff.
- [ ] Keep Review Save/Cancel readiness/persistence semantics unchanged.
- [ ] Prove persisted-DRAFT tabs/navigation are unchanged.
- [ ] Add the full deterministic regression matrix below.

## Interfaces / Contracts

Consumes existing Commerce-owned behaviour only:

```text
C078 canonical six-step new-Tool composition and browser-local session
C081 common External Test checkpoint integration
C083 common Shopify Test checkpoint integration
validateNewToolDefinition
External Request current validation signal
adminMappingValid
adminValidated
externalResponseValid
adminResultContractFresh
resultTemplateValid
isCurrentTestPassed(authoringState)
ToolAuthoringSession sessionStorage handoff
```

New UI-local contract:

```ts
type NewToolAuthoringNavigationState = {
  enabledThrough: NewToolAuthoringStepId;
};
```

No database or cross-repository runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-078
- ARCH-021-COMMERCE-083

C083 is an explicit dependency because `Test -> Review` must use the same current successful Test checkpoint for both External HTTP and Shopify Admin. C086 is unrelated and is not a dependency. C087 is reached transitively through C083.

## Enables

- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] New Tool creation always shows exactly six tabs in canonical order.
- [ ] A fresh session enables only Tool Definition; the other five tabs are visible and disabled.
- [ ] A disabled future tab cannot be selected.
- [ ] First-time forward unlock happens one step at a time through `Next` only.
- [ ] `Next` never invokes validation itself.
- [ ] Tool Definition first unlock uses exactly the R8 Tool Definition predicate.
- [ ] External and Shopify Request first unlocks use their existing current validation signals exactly as specified in R8.
- [ ] External and Shopify Response first unlocks use their existing current validity/freshness signals exactly as specified in R8.
- [ ] Result Template first unlock requires current canonical template validation.
- [ ] Review first unlock requires `isCurrentTestPassed(authoringState)`.
- [ ] Once a step is enabled, direct tab click remains allowed even after upstream/current authoring becomes dirty, invalid or stale.
- [ ] Once a next step is already enabled, `Next` navigates to it without revalidating the current step.
- [ ] `Previous` always navigates to the immediate previous step without validation or frontier mutation.
- [ ] Review remains clickable after it has been enabled even when later edits stale Test; the existing Save gate remains disabled until current readiness is restored.
- [ ] Initial provider selection does not automatically unlock Request.
- [ ] Cancelled provider change preserves active step and frontier exactly.
- [ ] Confirmed provider replacement resets active step/frontier to Tool Definition only.
- [ ] New-Tool Explore Shopify round trip restores active step and enabled frontier without unlocking later steps.
- [ ] Navigation performs zero durable Tool writes.
- [ ] Persisted-DRAFT tabs remain fully clickable and receive no Previous/Next footer.

## Validation

Run the focused current repository commands declared by the task/repository. At minimum:

- [ ] `npx vitest run tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx`
- [ ] authoring-session focused tests covering `editor.enabledThrough` round trip/backwards-compatible absence
- [ ] targeted ESLint for every changed source/test file
- [ ] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [ ] `git diff --check`

Required executable regressions:

1. Fresh Create Tool session renders all six tabs; only Tool Definition is enabled; Previous absent; Next disabled until Tool Definition is advance-ready.
2. Valid Tool Definition + loaded provider enables Next; click unlocks/navigates Request only; Response remains disabled.
3. Clicking disabled Response before Request first unlock does nothing.
4. External Request: current successful request validation enables first Next to Response; stale/invalid current validation does not.
5. Shopify Request: `adminMappingValid && adminValidated` enables first Next to Response; either false blocks first unlock.
6. External Response requires `externalResponseValid`; Shopify Response requires `adminResultContractFresh` before first unlock of Result Template.
7. Result Template requires `resultTemplateValid` before first unlock of Test.
8. Test FAILED/STALE/NOT_RUN cannot first-unlock Review; exact-current PASSED can.
9. After Response has been unlocked, return to Request and invalidate Request. Response stays enabled and direct click still opens it.
10. In the same state as test 9, Next from Request remains enabled because Response is already unlocked and navigates there without running validation.
11. After Review has been unlocked, change Result Template so Test becomes STALE. Review remains enabled/clickable; existing Save remains disabled.
12. Previous from every non-first step navigates exactly one step backward and does not change `enabledThrough`.
13. Initial provider selection leaves `enabledThrough=tool-definition`; confirmed provider replacement resets it to Tool Definition; cancelled replacement preserves it.
14. Explore Shopify from Request with later steps already unlocked returns to the same active step/frontier and does not unlock an additional step.
15. Tab/Previous/Next interactions invoke zero create/update Tool mutation actions.
16. Persisted Tool editor still exposes its current direct-click tabs and has no new progressive traversal controls.

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled task or alter C086/C087/C083 beyond consuming their accepted contracts.

## Implementation Notes

The navigation frontier is intentionally a **history of which steps the user has already reached**, not a live projection of current validity. Do not derive `enabledThrough` on every render from validation booleans. Doing that would violate the core requirement that previously enabled tabs remain clickable after edits.

The first-unlock predicate answers only:

```text
"May the user progress to this never-before-enabled next step now?"
```

It does not answer:

```text
"May the user visit a step they already reached?"
```

Keep those two concerns separate.

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
