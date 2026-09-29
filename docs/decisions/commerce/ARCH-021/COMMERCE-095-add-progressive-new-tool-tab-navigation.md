---
id: ARCH-021-COMMERCE-095
architecture_id: ARCH-021
title: Add progressive Previous/Next traversal to new Tool authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 76
executor: null
claimed_at: null
attempt: 2
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
moda-interact-commerce/src/studio/tools/tool-authoring-screen.tsx
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-tabs.tsx
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-navigation.ts       # new pure step/order helpers
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-step-navigation.tsx # new Previous/Next presentation
moda-interact-commerce/src/studio/tools/authoring-session.ts
moda-interact-commerce/src/studio/external-http/editor.tsx                          # expose the existing Request checkpoint upward
```

Focused tests:

```text
moda-interact-commerce/tests/tool-authoring-screen.test.tsx
moda-interact-commerce/tests/new-tool-authoring-state.test.ts
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/shopify-admin-tools-ui.test.tsx
moda-interact-commerce/tests/tool-authoring-session.test.ts
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
- Feature/Capability authoring work in COMMERCE-088..092, including COMMERCE-091 `Capability -> Tool -> Review` traversal.
- Refactoring Tool and Feature/Capability navigation into a new cross-domain generic wizard framework.
- Changing Create/Save/Cancel persistence semantics.
- Database, Shared, Background, Gateway or system-test implementation.
- Turning the flow into a modal wizard that prevents revisiting already-enabled tabs.

## Requirements

### R1 — one canonical new-Tool step order

Create one pure Commerce Studio navigation module containing the exact new-Tool order:

```ts
export const NEW_TOOL_AUTHORING_STEPS = [
Ready for Review after Attempt 2.
  "request",
  "response",
  "result-template",
Attempt 1 implementation commit `96ffdeca8f1e1cc420df9d2c1878fc459f82b530` added the progressive navigation implementation and baseline regression matrix. Attempt 2 correction commit `fb0c5fe00c816c7e599de7611049f4f89e6e4b32` updates `src/studio/tools/authoring/tool-authoring-tabs.tsx`, `src/studio/tools/new-tool-editor.tsx`, and `tests/tool-authoring-screen.test.tsx`. Both commits are pushed to `origin/task/ARCH-021-COMMERCE-095`.
  "review",
] as const;

export type NewToolAuthoringStepId =
  (typeof NEW_TOOL_AUTHORING_STEPS)[number];
```

- A1-R1: while provider replacement confirmation is unresolved, the new-Tool tab list disables navigation away from the active Tool Definition step, and Next/Previous/tab handlers reject navigation. Cancel clears only the pending choice and restores the prior frontier; successful replacement still resets it. Covered in `tool-authoring-screen.test.tsx`.
- A1-R2: replaced the pre-provider text with accurate guidance to complete Tool Definition and use Next to unlock each step; the screen regression asserts the exact guidance.
- A1-R3: added the prepared worktree, branch synchronization, claim and recursive submodule evidence below. The Architect Review section was not modified.
`ToolAuthoringTabs` and the Previous/Next logic must consume this same order. Do not maintain a second independently ordered six-step array for new Tool navigation.

The existing persisted Tool tab order may continue to use its current representation; this task must not alter persisted-DRAFT behaviour.

- Focused provider-confirmation regression — 1 test passed; asserts navigation is frozen during the decision, cancellation restores the enabled Request step, and confirmation starts the new provider at Tool Definition before Next.
- Targeted ESLint across all 13 changed source/test paths passed in Attempt 1; Attempt 2 ESLint on all three corrected files passed with no warnings. Changed-file TypeScript diagnostics report no errors.
- `git diff --check` — passed after Attempt 2.
- Repository `pnpm run typecheck` from Attempt 1 reported 146 TypeScript errors across 17 unchanged files; none referenced C095-changed files. Attempt 2 changed-file diagnostics remain clean.

```ts
type NewToolAuthoringNavigationState = {
  enabledThrough: NewToolAuthoringStepId;
No implementation scope deviations. The persisted editor retains its pre-existing tablist accessible name; only new-Tool creation uses the provider-neutral label. The enabled `ARCH-021-SYSTEM-TEST-002` task was not started.
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

The tablist accessibility label must be provider-neutral (for example `Tool authoring steps`), not the current `External tool authoring steps`, because this shell is shared by External HTTP and Shopify Admin.

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

The current implementation already owns these two facts inside `ExternalHttpEditor` as:

```text
requestState.valid
requestValidated
```

Expose them upward without duplicating validation by adding one provider-neutral reporting callback on `ExternalHttpEditor`, semantically:

```ts
onRequestCheckpointChange?(checkpoint: {
  structurallyValid: boolean;
  validated: boolean;
}): void;
```

`ExternalHttpEditor` must report the current pair whenever either value changes. `NewToolWorkspace` consumes that callback and the first-unlock predicate is exactly:

```ts
checkpoint.structurallyValid && checkpoint.validated
```

Do not invoke `validateExternalRequestAction` from navigation code and do not create another Request validator.

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

The current restore owner is `ToolAuthoringScreen`: after `restoreNewToolAuthoringState(...)`, apply the restored frontier to the returned `NewToolAuthoringState` before calling `setLocalSession(...)`. `NewToolEditor` may continue to restore the active `section` from `authoringSession.editor.section`; it must not maintain a second independent unlock frontier.

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

### R15 — keep Tool traversal independent from the new Feature/Capability workstream

COMMERCE-088..092 now own the separate Phase-5 Feature/Capability simplification. They do not change the Tool creation flow and they are not dependencies of this task.

In particular, COMMERCE-091 may implement a similar `Capability -> Tool -> Review` Previous/Next experience. Do not:

```text
make C093 depend on C091
make C091 depend on C093
move Tool authoring state into the Feature domain
move Feature/Capability state into the Tool domain
create a speculative cross-domain wizard framework merely to share these buttons
```

Reuse an already-existing genuinely generic primitive only if it requires no behaviour change to either domain. Otherwise keep this task bounded to `src/studio/tools/**`.

## Work Items

- [x] Add the pure canonical new-Tool step order/helpers.
- [x] Add `navigation.enabledThrough` to `NewToolAuthoringState` with `tool-definition` initial state.
- [x] Render all six new-Tool tabs from session start and disable only steps beyond the frontier.
- [x] Make enabled tab clicks depend only on the frontier, not current validation freshness.
- [x] Add the shared Previous/Next presentation component.
- [x] Implement exact Case A / Case B Next behaviour from R7.
- [x] Wire the exact R8 first-unlock predicates for both providers without adding validation calls.
- [x] Expose the exact current External `requestState.valid` + `requestValidated` checkpoint upward through one callback; do not duplicate validation.
- [x] Reset the frontier only on a confirmed successful provider-kind replacement.
- [x] Preserve frontier + active step through new-Tool Explore Shopify sessionStorage handoff, restoring the frontier into `NewToolAuthoringState` in `ToolAuthoringScreen`.
- [x] Keep Review Save/Cancel readiness/persistence semantics unchanged.
- [x] Prove persisted-DRAFT tabs/navigation are unchanged.
- [x] Add the full deterministic regression matrix below.

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

C083 is an explicit dependency because `Test -> Review` must use the same current successful Test checkpoint for both External HTTP and Shopify Admin. C086 is unrelated and is not a dependency. C087 is already Complete and is reached transitively through C083.

COMMERCE-088..092 are now occupied by the independent Feature/Capability simplification workstream. They are deliberately not dependencies of C093.

## Enables

- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [x] New Tool creation always shows exactly six tabs in canonical order with a provider-neutral tablist label.
- [x] A fresh session enables only Tool Definition; the other five tabs are visible and disabled.
- [x] A disabled future tab cannot be selected.
- [x] First-time forward unlock happens one step at a time through `Next` only.
- [x] `Next` never invokes validation itself.
- [x] Tool Definition first unlock uses exactly the R8 Tool Definition predicate.
- [x] External and Shopify Request first unlocks use their existing current validation signals exactly as specified in R8.
- [x] External and Shopify Response first unlocks use their existing current validity/freshness signals exactly as specified in R8.
- [x] Result Template first unlock requires current canonical template validation.
- [x] Review first unlock requires `isCurrentTestPassed(authoringState)`.
- [x] Once a step is enabled, direct tab click remains allowed even after upstream/current authoring becomes dirty, invalid or stale.
- [x] Once a next step is already enabled, `Next` navigates to it without revalidating the current step.
- [x] `Previous` always navigates to the immediate previous step without validation or frontier mutation.
- [x] Review remains clickable after it has been enabled even when later edits stale Test; the existing Save gate remains disabled until current readiness is restored.
- [x] Initial provider selection does not automatically unlock Request.
- [x] Cancelled provider change preserves active step and frontier exactly.
- [x] Confirmed provider replacement resets active step/frontier to Tool Definition only.
- [x] New-Tool Explore Shopify round trip restores active step and enabled frontier without unlocking later steps.
- [x] Navigation performs zero durable Tool writes.
- [x] Persisted-DRAFT tabs remain fully clickable and receive no Previous/Next footer.
- [x] Feature/Capability authoring (COMMERCE-088..092) is untouched and has no dependency on this Tool-navigation state.

## Validation

Run the focused current repository commands declared by the task/repository. At minimum:

- [x] `pnpm exec vitest run tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-session.test.ts tests/new-tool-authoring-state.test.ts --reporter=dot` — 5 files passed, 181 tests passed.
- [x] Authoring-session focused tests cover `editor.enabledThrough` round trip and backwards-compatible absence.
- [x] Targeted ESLint for every changed source/test file — passed with no warnings.
- [x] Repository typecheck run and reconciled: 146 existing errors across 17 untouched files; no diagnostics in changed C095 files.
- [x] `git diff --check` — passed.

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

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled task, reopen C083/C087, or modify COMMERCE-088..092 Capability work beyond consuming unrelated shared UI primitives that already exist.

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

Ready for Review after Attempt 2.

### Files Changed

Attempt 1 implementation commit `96ffdeca8f1e1cc420df9d2c1878fc459f82b530` added progressive navigation and its baseline regression matrix. Attempt 2 correction commit `fb0c5fe00c816c7e599de7611049f4f89e6e4b32` changes `src/studio/tools/authoring/tool-authoring-tabs.tsx`, `src/studio/tools/new-tool-editor.tsx`, and `tests/tool-authoring-screen.test.tsx`. Both commits are pushed to `origin/task/ARCH-021-COMMERCE-095`.

### Work Completed

- Added the canonical six-step navigation helpers, monotonic session-local frontier, shared Previous/Next footer, progressive tabs, and exact first-unlock predicates using existing provider validation/Test signals.
- Exposed External Request structural-validity/current-validation state without adding another validator; persisted the optional frontier in v1 Explore sessions and restored active step/frontier compatibly.
- Preserved persisted-DRAFT navigation, provider confirmation semantics, and independent Review/Save readiness; no durable schema or non-Commerce repository changes.
- Extended UI/state/session regressions for disabled steps, successful/failed/stale checkpoints, backwards/monotonic navigation, provider reset, Explore restore, zero writes, and persisted editor behavior.
- A1-R1: while provider replacement confirmation is unresolved, the tab list disables navigation away from the active Tool Definition step, and Next/Previous/tab handlers reject navigation. Cancel clears only the pending choice and restores the prior frontier; confirmation still resets the new provider to Tool Definition. The confirmation regression verifies both cases.
- A1-R2: replaced the stale pre-provider instruction with guidance to complete Tool Definition and use Next to unlock each step; the fresh-session screen test asserts the updated text.
- A1-R3: recorded the launcher-resolved worktree, synchronization, claim and recursive submodule evidence below. Architect Review was not edited.

### Validation Results

- Attempt 2: `pnpm exec vitest run tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-session.test.ts tests/new-tool-authoring-state.test.ts --reporter=dot` — 5 files passed, 181 tests passed.
- Provider-confirmation regression — 1 test passed; verifies navigation remains at Tool Definition while pending, cancellation restores the prior enabled tab, and confirmation resets the frontier before Next progresses.
- Targeted ESLint across all 13 changed source/test paths passed in Attempt 1; Attempt 2 rerun on the three corrected files passed with no warnings. Changed-file TypeScript diagnostics report no errors.
- `git diff --check` — passed after Attempt 2.
- Repository `pnpm run typecheck` in Attempt 1 reported 146 TypeScript errors across 17 unchanged files; none of the diagnostics reference C095-changed files. Attempt 2 changed-file diagnostics remain clean.
- Prisma Client was generated locally in the isolated worktree to enable the UI regression suites; no Prisma schema or gitlink was changed.

### Deviations

No implementation scope deviations. The persisted editor retains its pre-existing tablist accessible name; only new-Tool creation uses the provider-neutral label. `ARCH-021-SYSTEM-TEST-002` was not started.

### Assumptions

The v1 authoring-session contract remains unchanged; `editor.enabledThrough` is optional and older sessions fall back to their valid active section.

### Unresolved Issues

The repository-wide typecheck remains blocked by the 146 diagnostics in 17 untouched files noted above; focused C095 tests, corrected-file diagnostics and lint are clean.

### Architectural Concerns

None.

### Attempt 2 Prepared Execution Evidence

Launcher claim: Attempt 2, executor `copilot`, claimed at `2026-09-29T16:29:46Z`; claim commit `92607cab5c3e92426247c3dd72386456edb37cbe` was committed and pushed.

Physical worktree isolation:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-095`, `task/ARCH-021-COMMERCE-095`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-095`, `task/ARCH-021-COMMERCE-095`.
- Shared workspace checkout switched or mutated for task work: no. Shared implementation checkout switched or mutated for task work: no. Another task worktree reused: no.

Start-of-attempt synchronization:
- Parent remote task branch fast-forwarded: not needed; parent branch started at launcher head `6f053ed4045801cb34886136de354f86c4bcfbcb`.
- Parent `origin/main` incorporated: yes.
- Implementation remote task branch fast-forwarded: not needed; implementation branch started at launcher head `8227555e071494c4bc5aedbfe7a218aeb0e34902`.
- Implementation `origin/main` incorporated: yes.

Recursive implementation submodules:
- `git submodule sync --recursive`: passed.
- `git submodule update --init --recursive`: passed.
- Recorded initialized submodule: `database` at `e9fb60221f1532205650154dfff2aadb6270b14c`.

Attempt 2 implementation correction commit `fb0c5fe00c816c7e599de7611049f4f89e6e4b32` is pushed. This report is being published on the mirrored parent task branch with the review transition; task metadata is set to `status: review`, `executor: null` and `claimed_at: null`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is accepted in substance for the canonical six-step order, monotonic
session-local frontier, exact existing validation/Test checkpoints, shared
Previous/Next presentation, Explore-session restoration and persisted-DRAFT
isolation. The implementation remains within Commerce ownership and the focused
regression packet is broad.

Two implementation corrections and one durable execution-evidence correction are
required before acceptance:

1. **A1-R1 — provider-reset confirmation does not actually preserve the active
   step.** R9 requires the current provider, active step and frontier to remain
   unchanged until the destructive provider replacement is confirmed or
   cancelled. `pendingProvider` correctly blocks a first-time Tool Definition
   unlock, but an already-enabled Request/Response/etc. tab remains clickable and
   Case-A `Next` remains enabled. Because the confirmation is rendered inside the
   Tool Definition panel rather than as a browser-modal primitive, the user can
   navigate away while the confirmation is still pending. The hidden
   `pendingProvider` state then survives on another step. Navigation must be
   frozen at Tool Definition while the provider-reset decision is unresolved;
   cancel must restore normal traversal without changing the frontier, and a
   successful replacement must continue to reset the frontier to Tool Definition.

2. **A1-R2 — the pre-provider instruction now contradicts progressive unlock
   semantics.** The screen still says that Request, Response, Result Template,
   Test and Review "become available after a Tool type is selected", while R9 and
   the accepted implementation intentionally keep Request locked after initial
   provider selection until Tool Definition satisfies its checkpoint and later
   steps unlock one at a time. Replace the message with wording that accurately
   describes progressive `Next`-based unlock; do not change the actual predicates.

3. **A1-R3 — the Completion Report does not durably record the required prepared
   worktree evidence.** The report identifies the implementation commit and says
   the work ran in an isolated worktree, but it does not record the
   launcher-resolved dedicated parent and Commerce worktree evidence,
   start-of-attempt synchronization evidence, or recursive submodule preparation
   evidence required by the task execution policy. This is report/evidence work;
   do not create code churn merely to manufacture a new implementation commit.

The supplied archive contains no Git metadata or installed `node_modules`, so the
architect inspected the submitted source/tests/task record directly but could not
independently verify the pushed refs or rerun the 181-test/lint/typecheck packet.

### Reviewed Files

- `moda-interact-commerce/src/studio/tools/authoring/tool-authoring-navigation.ts`
- `moda-interact-commerce/src/studio/tools/authoring/tool-authoring-step-navigation.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/tool-authoring-tabs.tsx`
- `moda-interact-commerce/src/studio/tools/new-tool-authoring-state.ts`
- `moda-interact-commerce/src/studio/tools/new-tool-editor.tsx`
- `moda-interact-commerce/src/studio/tools/tool-authoring-screen.tsx`
- `moda-interact-commerce/src/studio/tools/authoring-session.ts`
- `moda-interact-commerce/src/studio/external-http/editor.tsx`
- the five focused C095 test files listed by the task
- the C095 Completion Report and dependency task records

### Validation Reviewed

- Submitted focused packet: 5 suites / 181 tests passed.
- Submitted targeted ESLint: passed.
- Submitted `git diff --check`: passed.
- Submitted repository typecheck: 146 diagnostics across 17 unchanged files, with
  no C095 changed-file diagnostics.
- Static architect inspection confirmed the provider-confirmation navigation gap
  described in A1-R1 and the contradictory instruction described in A1-R2.

### Architecture Conformance

Changes Requested. The progressive-navigation architecture is otherwise
conformant, but R9 is not fully enforced while provider replacement confirmation
is pending. The durable execution record also requires the missing prepared
worktree/synchronization/submodule evidence before acceptance.

### Follow-up

Attempt 2 must:

1. make a pending provider-reset confirmation preserve the active Tool Definition
   step even when later tabs were already enabled; clicking those tabs or `Next`
   while the decision is unresolved must not navigate or mutate the frontier;
2. prove cancel preserves the prior frontier and re-enables normal traversal, and
   prove successful replacement still resets active step/frontier to Tool
   Definition;
3. replace the stale "steps become available after Tool type selection" text with
   progressive-unlock guidance;
4. add focused regressions for the pending-confirmation navigation case and the
   corrected guidance; and
5. amend the Completion Report with the prepared launcher packet's dedicated
   parent/implementation worktree, start synchronization and recursive submodule
   evidence.

Return the same task to review after the focused validation required by the task.
Do not start `ARCH-021-SYSTEM-TEST-002`.
