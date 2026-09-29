---
id: ARCH-021-COMMERCE-103
architecture_id: ARCH-021
title: Add Previous/Next traversal to persisted Tool authoring
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
  - ARCH-021-COMMERCE-095
  - ARCH-021-COMMERCE-099
enables:
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-29
updated: 2026-09-29
---

# Add Previous/Next traversal to persisted Tool authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add deterministic `Previous`/`Next` traversal to **persisted DRAFT Tool authoring** for `EXTERNAL_HTTP`, `SHOPIFY_ADMIN_GRAPHQL` and `POLICY_OPERATION`, reusing the accepted six-step Tool order and shared navigation presentation while preserving the existing rule that every persisted authoring tab is always directly clickable and navigation never performs validation, persistence or provider execution.

## Context

COMMERCE-095 established the canonical six-step Tool authoring order and shared `ToolAuthoringStepNavigation`, but deliberately excluded persisted-DRAFT traversal. Its accepted regression currently asserts that persisted External Tool authoring has no `Previous` or `Next` controls.

The current persisted surfaces are:

```text
ToolEditor / EXTERNAL_HTTP
ToolEditor / SHOPIFY_ADMIN_GRAPHQL
PolicyOperationEditor / POLICY_OPERATION
```

All three already render the same six tabs:

```text
Tool Definition
Request
Response
Result Template
Test
Review
```

and all persisted tabs are intentionally directly clickable even when the current candidate is dirty, invalid, stale or not yet tested. The missing behaviour is only sequential navigation parity.

This task therefore adds a shell-level navigation footer to persisted DRAFT authoring. It does **not** import the progressive first-unlock semantics from new Tool creation.

Hard invariant:

```text
Persisted DRAFT
  direct tab click = free navigation
  Previous/Next    = the same free navigation expressed sequentially

Validation/Test/Save readiness remain independent concerns.
```

COMMERCE-099 is an explicit dependency because it owns the canonical persisted `POLICY_OPERATION` DRAFT authoring/Test/CAS-save surface that this task must include. COMMERCE-102 is independent: its selected-shop and single-flight correction must not be coupled to this navigation implementation.

## Scope

Primary implementation areas:

```text
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-navigation.ts
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-step-navigation.tsx
moda-interact-commerce/src/studio/tools/authoring/tool-authoring-tabs.tsx
moda-interact-commerce/src/studio/tools/tool-editor.tsx
moda-interact-commerce/src/studio/tools/policy-operation-editor.tsx
```

Focused tests:

```text
moda-interact-commerce/tests/external-tools-ui.test.tsx
moda-interact-commerce/tests/shopify-admin-tools-ui.test.tsx
```

`tests/tool-authoring-screen.test.tsx` may be changed only if a shared canonical navigation helper/presentation regression genuinely belongs there. Do not create a new duplicate test harness when the existing persisted provider suites can prove the behaviour.

## Out of Scope

- Changing COMMERCE-095 progressive new-Tool unlocking or `navigation.enabledThrough` semantics.
- Adding an unlock frontier to persisted Tools.
- Disabling persisted tabs because Request/Response/Result Template/Test is invalid or stale.
- Performing validation automatically from `Previous` or `Next`.
- Changing Request, Response, Result Template or Test validation semantics.
- Changing Save, Cancel, Publish, CAS, operation-ID or reconciliation semantics.
- Changing COMMERCE-102 selected-shop execution targeting or single-flight action admission.
- Changing Shopify offline-session resolution, provider execution or credential handling.
- Adding a new authoring-session field for persisted navigation.
- Changing the existing persisted active-section restore contract in `ToolAuthoringSession.editor.section`.
- Feature/Capability authoring or COMMERCE-088..092 navigation.
- Database, Shared, Background, Gateway or system-test implementation.
- Refactoring Tool and Feature/Capability flows into a generic wizard framework.

## Requirements

### R1 — one canonical six-step order; do not create a second persisted order

The persisted DRAFT flow uses exactly this order:

```text
1. tool-definition  -> Tool Definition
2. request          -> Request
3. response         -> Response
4. result-template  -> Result Template
5. test             -> Test
6. review           -> Review
```

Reuse the canonical order/labels already established by COMMERCE-095 in:

```text
src/studio/tools/authoring/tool-authoring-navigation.ts
```

Do **not** add another independently maintained six-element array for persisted navigation.

The current `ToolAuthoringTabs` has a separate `persistedToolTabs` literal containing the same six entries. Remove that duplication or mechanically derive persisted tabs from the canonical six-step source.

A provider-neutral alias/type may be introduced if needed to avoid using a misleading `NewTool...` name in persisted code, but it must be an alias/derivation of the same canonical literals, not a second source of truth. Existing COMMERCE-095 imports/behaviour must remain compatible.

The legacy `agent` tab must not reappear in rendered Tool authoring.

### R2 — persisted tabs remain permanently unlocked

For a persisted DRAFT of any supported kind:

```text
EXTERNAL_HTTP
SHOPIFY_ADMIN_GRAPHQL
POLICY_OPERATION
```

all six tabs remain enabled and directly clickable exactly as today.

Do not pass or derive a progressive `enabledThrough` frontier for persisted mode.

Do not disable a persisted tab because any of the following is true:

```text
Tool Definition invalid
Request invalid or not validated
Response stale or invalid
Result Template invalid
Test NOT_RUN
Test RUNNING
Test FAILED
Test STALE
candidate dirty
Save disabled
Publish disabled
```

This task must not make direct tab navigation more restrictive than the current persisted editor.

### R3 — exact `Previous` semantics for persisted DRAFTs

Use one visible button labelled exactly:

```text
Previous
```

with this mapping:

```text
Tool Definition: no Previous button
Request:         Previous -> Tool Definition
Response:        Previous -> Request
Result Template: Previous -> Response
Test:            Previous -> Result Template
Review:          Previous -> Test
```

On activation, `Previous` performs exactly one authoring-shell section transition to the immediate predecessor.

It must not:

```text
validate a section
invoke a Server Action
perform provider I/O
change dirty state merely because navigation occurred
change persisted authoring revisions
change Test status/result
save/update/publish a Tool
change editVersion
change operationId/reconciliation state
```

### R4 — exact `Next` semantics for persisted DRAFTs

Use one visible button labelled exactly:

```text
Next
```

with this mapping:

```text
Tool Definition: Next -> Request
Request:         Next -> Response
Response:        Next -> Result Template
Result Template: Next -> Test
Test:            Next -> Review
Review:          no Next button
```

Every displayed `Next` is enabled whenever the equivalent destination tab is enabled. Because all persisted tabs are directly navigable, persisted `Next` must not depend on current validation/Test freshness.

On activation, `Next` performs exactly one authoring-shell section transition to the immediate successor and nothing else.

### R5 — `Previous`/`Next` must be behaviourally equivalent to direct tab navigation

For persisted DRAFT authoring, direct tab click and sequential navigation differ only in how the destination is selected.

Required example:

```text
Request was edited into an invalid/stale state
Response tab remains clickable
Next from Request remains enabled
click Next -> Response
zero validation calls
zero persistence calls
```

Required Review example:

```text
Review is open
candidate becomes unsaveable because Test is stale/failed
Previous still returns to Test
Review remains directly clickable
Save remains governed by the existing Save gate
```

Do not add a `canNavigate`, `canAdvance`, validation checkpoint or Test gate for persisted navigation.

### R6 — reuse the shared navigation presentation exactly once per active persisted step

Reuse:

```text
src/studio/tools/authoring/tool-authoring-step-navigation.tsx
ToolAuthoringStepNavigation
```

Do not add provider-specific `Previous`/`Next` copies inside:

```text
ExternalHttpEditor
ShopifyAdminEditor
ShopifyAdminResponseEditor
ShopifyAdminTestTab
PolicyOperationTestTab
ResultTemplateTab
ReviewTab
```

Render exactly one `ToolAuthoringStepNavigation` footer for the active persisted step.

Placement is deterministic:

```text
ToolAuthoringTabs
active step content
ToolAuthoringStepNavigation
```

For Review:

```text
ReviewTab content/actions
ToolAuthoringStepNavigation containing Previous only
```

Existing Review Save/Cancel/Validate/Publish controls remain inside `ReviewTab`; navigation does not move or replace them.

### R7 — integrate at the owning persisted shells

#### External HTTP and Shopify Admin

`ToolEditor` remains the owner of the persisted active section (`externalSection`).

The navigation footer must derive `previousStep` and `nextStep` from that same current section and update it through the same `setExternalSection` path used by direct tab clicks.

Do not introduce a second active-step state.

#### Policy Operation

`ToolEditor` continues to own the active section and passes:

```text
section={externalSection}
setSection={setExternalSection}
```

to `PolicyOperationEditor`.

`PolicyOperationEditor` must derive its footer from those props and call the supplied `setSection`. It must not create an independent section state or navigation frontier.

### R8 — preserve existing authoring-session section restore and Explore Shopify round trip

Persisted existing-Tool session restoration already uses:

```text
ToolAuthoringSession.editor.section
```

and `ToolEditor` initializes `externalSection` from that value when it is one of the canonical six steps.

Preserve that mechanism unchanged.

Do not add `enabledThrough` or another persisted navigation field.

When an existing Shopify Admin Request opens Explore Shopify, the existing handoff already records:

```text
editor.section: externalSection
```

`Previous`/`Next` must update `externalSection`, so any subsequent Explore handoff naturally records the current section. Do not add special Explore synchronization beyond that existing source of truth.

### R9 — navigation remains available under the same conditions as direct persisted tabs

Do not make `Previous` or `Next` more restrictive than direct persisted tab selection.

In particular, do not newly disable sequential navigation merely because:

```text
pending === true
locked === true
```

unless this task also changes direct persisted tab navigation to the same rule, which is **not authorised**.

The purpose is parity with the current directly clickable persisted tabs, not a new interaction lock model. COMMERCE-102 separately owns consequential action admission.

### R10 — persisted tablist accessible name is provider-neutral

The current persisted tablist uses:

```text
aria-label="External tool authoring steps"
```

even for Shopify Admin and Policy Operation Tools.

Change the persisted tablist label to exactly:

```text
Tool authoring steps
```

New Tool creation already uses that provider-neutral label. After this task, the same label is used for all Tool-authoring provider kinds.

Do not vary the label by provider.

### R11 — navigation is local-only and zero-write

The following operations must perform zero durable writes and zero provider calls:

```text
click Previous
click Next
click any persisted authoring tab
```

At minimum, navigation must not invoke:

```text
createToolWithInitialDraft
createToolDraft
updateToolDraft
publishToolRevision
validateExternalRequestAction
validateExternalResponseAction
validateExternalToolDefinitionAction
validateShopifyAdminRequestAction / persisted Shopify validation action
getPolicyOperationAuthoringDescriptorAction beyond its existing mount/read lifecycle
testExternalHttpCandidateAction
testShopifyAdminCandidateAction
testPolicyOperationCandidateAction
```

A descriptor read that already occurs because `PolicyOperationEditor` mounts is not caused by Previous/Next and must not be duplicated by navigation.

### R12 — preserve candidate, validation, Test and dirty state across navigation

A pure section transition must not reset or recompute current authoring state.

For each provider, author a transient value/state, navigate away with Previous/Next, then navigate back and prove the transient state is retained exactly as the existing direct-tab path retains it.

At minimum preserve:

```text
External HTTP: invalid/unsaved Request edit
Shopify Admin: stale/unsaved Request or Result-path edit
Policy Operation: unsaved mapping/input edit
```

The existing Test freshness ledger may change only when its owning candidate/input/shop mutation changes it, never because navigation occurred.

### R13 — do not alter new-Tool progressive behaviour

All COMMERCE-095 behaviours remain unchanged:

```text
fresh new Tool shows all six steps
future new-Tool steps are progressively unlocked
first-time Next may be gated by existing readiness signals
already-unlocked new-Tool steps remain navigable
provider replacement may reset the new-Tool frontier
```

Persisted DRAFT traversal must not read or mutate `NewToolAuthoringState.navigation.enabledThrough`.

## Work Items

- [ ] Reuse/derive persisted tab order from the COMMERCE-095 canonical six-step source; remove the independent persisted six-step literal.
- [ ] Make the persisted tablist provider-neutral with `aria-label="Tool authoring steps"`.
- [ ] Reuse the existing previous/next step helpers or a provider-neutral alias derived from the same canonical order.
- [ ] Reuse `ToolAuthoringStepNavigation`; do not create provider-specific navigation button copies.
- [ ] Add one navigation footer to persisted External HTTP authoring in `ToolEditor`.
- [ ] Add one navigation footer to persisted Shopify Admin authoring in `ToolEditor`.
- [ ] Add one navigation footer to persisted Policy Operation authoring in `PolicyOperationEditor` using the parent-owned `section`/`setSection` props.
- [ ] Preserve existing `ToolAuthoringSession.editor.section` restore and Explore Shopify handoff semantics without a new session field.
- [ ] Preserve all direct persisted tabs as always enabled/clickable.
- [ ] Prove Previous/Next perform zero validation, provider/Test or Tool lifecycle calls.
- [ ] Prove invalid/stale persisted state does not block Previous/Next.
- [ ] Prove navigation preserves transient edits, validation/Test state and dirty semantics.
- [ ] Prove COMMERCE-095 new-Tool progressive traversal is unchanged.
- [ ] Add/adjust focused regressions exactly as defined below.

## Interfaces / Contracts

Consumes existing Commerce-local contracts only:

```text
COMMERCE-095 canonical six-step Tool authoring order/helpers
ToolAuthoringTabs
ToolAuthoringStepNavigation
ToolAuthoringSession.editor.section
ToolEditor externalSection/setExternalSection
PolicyOperationEditor section/setSection
```

No database, Shared, cross-service or provider runtime contract is introduced or changed.

## Dependencies

- ARCH-021-COMMERCE-095
- ARCH-021-COMMERCE-099

Both dependencies are architect-accepted Complete, so this task is `Ready`.

COMMERCE-102 is intentionally not a dependency. C102 and C103 may be implemented independently, but terminal `ARCH-021-SYSTEM-TEST-002` must wait for both.

## Enables

- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Persisted `EXTERNAL_HTTP`, `SHOPIFY_ADMIN_GRAPHQL` and `POLICY_OPERATION` DRAFTs each show exactly six tabs in the canonical order.
- [ ] The persisted tablist accessible name is exactly `Tool authoring steps` for all three provider kinds.
- [ ] All six persisted tabs remain enabled and directly clickable regardless of current validation/Test freshness.
- [ ] Tool Definition has no Previous and has Next -> Request.
- [ ] Request has Previous -> Tool Definition and Next -> Response.
- [ ] Response has Previous -> Request and Next -> Result Template.
- [ ] Result Template has Previous -> Response and Next -> Test.
- [ ] Test has Previous -> Result Template and Next -> Review.
- [ ] Review has Previous -> Test and no Next.
- [ ] Previous/Next navigate exactly one step and never auto-validate the current/destination step.
- [ ] Invalid/stale Request/Response/Result Template/Test state does not disable navigation to an already directly clickable persisted step.
- [ ] Review Save/Cancel/Validate/Publish gates remain unchanged and independent from navigation.
- [ ] External transient edits survive sequential navigation exactly as they survive direct tab navigation.
- [ ] Shopify Admin transient edits/Test freshness survive sequential navigation exactly as they survive direct tab navigation.
- [ ] Policy Operation transient edits/Test freshness survive sequential navigation exactly as they survive direct tab navigation.
- [ ] Existing authoring-session section restore and Shopify Explore return context remain correct without a new persisted navigation field.
- [ ] Previous/Next/direct tab navigation invoke zero Tool create/update/publish mutations and zero live-Test/provider actions.
- [ ] Policy descriptor metadata is not re-requested merely because Previous/Next is clicked.
- [ ] New Tool progressive unlocking and its existing C095 regressions remain unchanged.

## Validation

Use the repository-declared commands and current Node bootstrap policy. At minimum run:

- [ ] `pnpm exec vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx --reporter=dot`
- [ ] targeted ESLint for every changed source/test file
- [ ] `npm run typecheck` (or record the exact known baseline ID if the observed failure is an unchanged documented baseline and no changed-file diagnostics exist)
- [ ] `git diff --check`

Required executable regressions:

1. Persisted External DRAFT: from Tool Definition, Next traverses Request -> Response -> Result Template -> Test -> Review; Previous traverses back one step each time; boundary buttons are absent exactly at first/last step.
2. Persisted Shopify Admin DRAFT: same exact six-step Previous/Next traversal.
3. Persisted Policy Operation DRAFT: same exact six-step Previous/Next traversal.
4. Persisted External invalid Request: after making Request invalid without validating, Next still opens Response; `validateExternalRequestAction`, Tool mutations and live Test are not called by navigation.
5. Persisted Shopify Admin stale/invalid authoring state: Next/Previous still traverse; Shopify validation/Test/mutation actions are not called by navigation.
6. Persisted Policy Operation invalid/stale mapping or validation state: Next/Previous still traverse; Policy Test/Save are not called by navigation and no extra descriptor read is triggered solely by the button click.
7. Review: Save remains disabled/enabled only by existing readiness; Previous always returns to Test; there is no Next.
8. Direct tab click remains enabled for every persisted step after the navigation footer is introduced.
9. Existing `authoringSession.editor.section` restore selects the saved persisted step and the footer computes the correct immediate neighbours from that restored step.
10. Existing Shopify Explore round trip records/restores the current `externalSection`; no `enabledThrough` field is added for persisted mode.
11. Navigation preserves transient External/Shopify/Policy edits and does not mutate current Test checkpoint merely because the section changes.
12. Existing new-Tool C095 traversal tests continue to pass unchanged in behaviour.
13. Replace the current persisted External assertion that `Previous`/`Next` are absent with positive traversal/parity assertions; do not leave a contradictory regression expectation.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not start `ARCH-021-SYSTEM-TEST-002`, COMMERCE-102 or another follow-on task.

## Implementation Notes

This task is intentionally simpler than COMMERCE-095.

For persisted DRAFTs there is no unlock history and no first-unlock predicate. The navigation algorithm is only:

```text
current canonical step
    |
    +-- Previous -> immediate predecessor if one exists
    |
    +-- Next -----> immediate successor if one exists
```

The active section remains the single source of truth already owned by `ToolEditor`.

Do not derive navigation permission from candidate validity. If an implementation introduces validation-based persisted navigation gating, it does not conform to this task even if Save/Test validation still works.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

`moda-interact-commerce/src/studio/tools/authoring/tool-authoring-navigation.ts`
`moda-interact-commerce/src/studio/tools/authoring/tool-authoring-step-navigation.tsx`
`moda-interact-commerce/src/studio/tools/authoring/tool-authoring-tabs.tsx`
`moda-interact-commerce/src/studio/tools/tool-editor.tsx`
`moda-interact-commerce/src/studio/tools/policy-operation-editor.tsx`
`moda-interact-commerce/tests/external-tools-ui.test.tsx`
`moda-interact-commerce/tests/shopify-admin-tools-ui.test.tsx`

### Work Completed

- Derived persisted tabs from the COMMERCE-095 canonical six-step order and introduced provider-neutral step type/helper aliases without changing new-Tool progression.
- Set the persisted tablist accessible name to `Tool authoring steps`; all six tabs remain directly enabled.
- Added one shared, readiness-independent Previous/Next footer to persisted External HTTP, Shopify Admin GraphQL and Policy Operation shells, using their existing section state/setter paths.
- Added regressions for forward/backward boundaries, invalid/stale navigation, transient edit retention, zero action calls, Policy descriptor-read stability, and Shopify Explore section restore. Preserved the existing Review save gate and new-Tool progressive behavior.

### Validation Results

- `./node_modules/.bin/vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx --reporter=dot` — passed, 3 files and 163 tests.
- Targeted ESLint over all changed implementation and test files — passed.
- `git diff --check` — passed.
- VS Code diagnostics for all changed files — no errors.
- `npm run typecheck` — passed. The task worktree initially lacked the lockfile-pinned Vite package; the exact installed Vite 6.4.3 package was temporarily linked from the canonical Commerce checkout inside ignored `node_modules` and the link was removed after the check. No project manifest was changed.
- Initial `pnpm exec vitest` did not reach tests because pnpm rejected ignored dependency build scripts (`ERR_PNPM_IGNORED_BUILDS`). The local Vitest binary was used after generating the task worktree's Prisma client; bootstrap-generated untracked pnpm files were removed.

### Deviations

The required Vitest suites were run via the installed local binary because `pnpm exec` attempted dependency installation and stopped at the ignored-build-script policy. Typecheck used the lockfile-pinned Vite package from the already-installed canonical environment without changing project files.

### Assumptions

Persisted tabs are canonical six-step IDs; the existing new-Tool names remain compatibility aliases for the same literals/helpers.

### Unresolved Issues

None.

### Architectural Concerns

None identified.

## Architect Review

### Review Status

Changes Requested

### Review Notes

COMMERCE-103 Attempt 1 is **accepted in implementation substance**. No product/source correction is requested at this stage.

The inspected implementation conforms to the persisted-DRAFT navigation contract:

- `EXTERNAL_HTTP`, `SHOPIFY_ADMIN_GRAPHQL` and `POLICY_OPERATION` reuse the canonical six-step order;
- persisted tabs remain directly clickable and do not gain a progressive unlock frontier;
- `Previous` / `Next` use the shared `ToolAuthoringStepNavigation` presentation and the canonical previous/next helpers;
- External and Shopify Admin update the existing parent-owned `externalSection`;
- Policy Operation uses the existing parent-supplied `section` / `setSection`;
- sequential navigation is independent of validation, Test freshness, Save readiness, `pending` and `locked`, matching direct persisted tab behaviour required by this task;
- the persisted tablist label is provider-neutral (`Tool authoring steps`);
- navigation does not create another authoring-session navigation field;
- the existing Shopify Explore `editor.section` restore/handoff remains the section source of truth;
- the Policy descriptor is not re-requested merely because Previous/Next changes the active section;
- the inspected regressions cover External, Shopify Admin and Policy Operation traversal, transient edits, zero lifecycle/Test/validation side effects, boundaries and Explore restoration;
- new-Tool progressive navigation remains on the existing COMMERCE-095 path.

The implementation therefore does **not** need code churn merely for this review.

Attempt 1 cannot be accepted Complete yet because the durable task record is not protocol-complete:

1. Every Work Item remains unchecked even though the Completion Report says the work was implemented.
2. Every Acceptance Criterion remains unchecked.
3. Every Validation checklist item remains unchecked.
4. The Completion Report does not record the mandatory launcher-resolved physical-isolation/start-of-attempt synchronization evidence for the dedicated parent and implementation worktrees, including recursive submodule preparation.

The architect protocol requires this evidence for every repository task. A clean pushed branch and passing tests do not substitute for the prepared-worktree evidence.

#### Attempt 2 correction contract — evidence/report reconciliation only

Do **not** redesign or refactor the C103 implementation.

Run the normal:

```text
/moda-task ARCH-021-COMMERCE-103
```

preparation path for Attempt 2.

The launcher must establish/reuse the canonical dedicated parent and implementation worktrees, incorporate current `origin/main` as required, initialize/verify recursive submodules and claim Attempt 2.

If the already-pushed implementation commit is valid, check out/use that implementation in the canonical C103 implementation worktree. Do not manufacture source churn solely to create another implementation commit.

From the launcher-prepared canonical implementation worktree:

1. rerun the required C103 focused validation;
2. reconcile every completed Work Item to `[x]`;
3. reconcile every satisfied Acceptance Criterion to `[x]`;
4. reconcile every completed Validation item to `[x]`;
5. preserve the exact Attempt 1 implementation and Completion Report history;
6. add Attempt 2 preparation/validation evidence to the Completion Report;
7. return the same task to `review`;
8. STOP — do not start SYSTEM-TEST-002, COMMERCE-102 or another follow-on task.

The Attempt 2 Completion Report MUST record the exact launcher packet facts, not inferred values:

```text
canonical workspace_root

parent_worktree_path
parent task branch
parent remote task-branch synchronization result
parent origin/main incorporation result
parent synchronized HEAD

implementation_worktree_path
implementation task branch
implementation remote task-branch synchronization result
implementation origin/main incorporation result
implementation synchronized HEAD

recursive submodule sync/update result
recursive submodule status
database (or other implementation submodule) recorded commit, where applicable

claim executor
claimed_at
Attempt 2 claim commit
```

If the launcher reports that execution cannot be prepared in the canonical isolated worktrees, return the task Blocked rather than validating from a shared/default checkout.

#### Validation reconciliation

The task-required focused suites are:

```text
tests/external-tools-ui.test.tsx
tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

Attempt 1 reports 163 tests passed and the reviewed test source is consistent with the required C103 regression matrix.

For Attempt 2:

- rerun the same focused three-suite packet from the canonical implementation worktree;
- rerun targeted ESLint for every C103-changed source/test file;
- rerun `npm run typecheck`;
- rerun `git diff --check`.

The Attempt 1 `pnpm exec vitest` deviation is documented. If the repository's prepared dependency environment still makes `pnpm exec` stop before executing tests because of the same ignored-build policy, using the already-installed lockfile-pinned local Vitest binary for the exact same files is acceptable **only if** the Completion Report records the command and confirms no project manifest/lockfile change and no dependency installation is smuggled into task scope.

Do not rely on a temporary cross-checkout Vite symlink as the final Attempt 2 typecheck proof. Run typecheck against the canonical prepared task environment. If the required lockfile-pinned dependency is unavailable there, report the environment/dependency gap instead of modifying manifests or borrowing runtime dependencies from another checkout.

### Reviewed Files

- `docs/decisions/commerce/ARCH-021/COMMERCE-103-add-persisted-tool-previous-next-navigation.md`
- `moda-interact-commerce/src/studio/tools/authoring/tool-authoring-navigation.ts`
- `moda-interact-commerce/src/studio/tools/authoring/tool-authoring-step-navigation.tsx`
- `moda-interact-commerce/src/studio/tools/authoring/tool-authoring-tabs.tsx`
- `moda-interact-commerce/src/studio/tools/tool-editor.tsx`
- `moda-interact-commerce/src/studio/tools/policy-operation-editor.tsx`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/shopify-admin-tools-ui.test.tsx`
- `moda-interact-commerce/tests/tool-authoring-screen.test.tsx`

### Validation Reviewed

Attempt 1 submitted evidence:

- focused UI packet: **3 files / 163 tests passed**;
- targeted ESLint: passed;
- changed-file diagnostics: clean;
- `npm run typecheck`: reported passed, with the dependency-environment deviation documented above;
- `git diff --check`: passed.

The submitted archive does not contain installed `node_modules`, so these commands were not independently rerun in this review environment.

The implementation/test source was inspected directly and no C103 behavioural defect was identified.

### Architecture Conformance

Implementation: **Conforms**.

Task execution/report protocol: **Changes Requested** pending checklist reconciliation and mandatory launcher/worktree/start-of-attempt evidence.

### Follow-up

Return the SAME `ARCH-021-COMMERCE-103` task through `/moda-task` for Attempt 2.

Task state for rework:

```text
status: ready
executor: null
claimed_at: null
attempt: 1
```

The next authorized launcher claim increments to Attempt 2.

No implementation source change is required unless the canonical rerun exposes a real defect.

ARCH-021-SYSTEM-TEST-002 remains dependency-gated until C103 is architect-accepted Complete.
