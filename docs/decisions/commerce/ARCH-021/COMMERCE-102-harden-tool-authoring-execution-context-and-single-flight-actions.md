---
id: ARCH-021-COMMERCE-102
architecture_id: ARCH-021
title: Harden Tool authoring execution context and single-flight actions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 73
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-083
  - ARCH-021-COMMERCE-095
enables:
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-29
updated: 2026-09-30
---
# Harden Tool authoring execution context and single-flight actions

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the validated Studio shop selection the only browser execution target for Shopify Admin Tool testing and ensure every consequential Tool-authoring action admits at most one in-flight operation for the same action/candidate, including same-tick repeated clicks/submits, without weakening the existing server-side authorization, idempotency or unknown-outcome reconciliation boundaries.

## Context

Manual validation exposed two related Tool-authoring interaction-safety gaps.

First, `ProductionStudioPage` resolves `resolveStudioShopSelection(shopId)` and the shell correctly renders `shopSelection.selectedShop`, but the normal Tools path still passes the raw URL `shopId` into `StudioWorkspace`. A stale/invalid URL shop can therefore reach Tool authoring even while the shell displays `No shop selected`. C082 remains server-authoritative and will reject an invalid shop or a shop without an offline session, but the browser must not present or dispatch Shopify Admin Test as if an execution target exists.

Second, several Tool-authoring actions use React `pending` state as their only re-entry barrier. React state is presentation state, not a synchronous admission lock: two activations in the same tick can enter the handler before the pending render commits. `components/pending-action-form.tsx` already demonstrates the required synchronous `useRef` admission pattern. This task applies equivalent semantics to the active Tool-authoring surface; it does not replace durable operation IDs, CAS, backend authorization or reconciliation.

## Scope

Primary implementation areas include the existing Tool-authoring composition and the active action owners, including as required:

```text
components/production-studio-page.tsx
components/studio-workspace.tsx
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/shopify-admin-editor.tsx
src/studio/tools/shopify-admin-response-editor.tsx
src/studio/tools/authoring/shopify-admin-test-tab.tsx
src/studio/tools/authoring/result-template-tab.tsx
src/studio/tools/authoring/tool-definition-tab.tsx
src/studio/external-http/request-tab.tsx
src/studio/external-http/response-tab.tsx
focused Tool-authoring / selected-shop tests
```

A small Commerce-local reusable synchronous action-gate helper may be introduced under `src/studio/tools/authoring/` if it reduces duplication. Do not replace unrelated forms or create a platform-wide interaction framework.

## Out of Scope

- Changing the C082 Shopify Admin live-Test server contract or provider executor.
- Moving Shopify offline-session tokens or credentials into browser props.
- Automatically choosing the first/last/only shop when no explicit authoring shop is selected.
- Database/schema changes.
- New Tool types or new Tool-authoring phases.
- Reworking Policy Operation lifecycle work owned by COMMERCE-099/100; any new buttons introduced by those tasks must consume the common interaction-safety rule rather than being implemented here speculatively.
- Debouncing with timers or arbitrary delays.
- Gating ordinary repeatable local controls such as tabs, Previous/Next, text insertion, mapping Add/Remove, or normal field edits merely because they are buttons.

## Requirements

### R1 — validated selected shop is authoritative

After `resolveStudioShopSelection(shopId)` returns, only `shopSelection.selectedShop` may be propagated as Tool-authoring execution context.

For the Tools path:

```text
raw URL shopId
    -> resolveStudioShopSelection
    -> selectedShop: ShopExecutionContext | null
    -> StudioWorkspace / ToolAuthoringScreen
```

The raw unresolved `shopId` must not be forwarded into Tool authoring after selection resolution.

Pass enough non-secret selected-shop context for the Shopify Admin Test UI to render the target explicitly:

```text
id
domain
shopifyOfflineSessionAvailable
```

The existing `ShopExecutionContext` is the canonical shape. Do not copy or expose tokens/session payloads.

An invalid/stale URL shop must result in:

```text
shell selected shop = null
Tool authoring selected shop = null
```

not a shell/tool mismatch.

### R2 — Shopify Admin Test exposes and gates the execution target

Keep the Test tab navigable. Do not hide the tab simply because no shop is selected.

The Shopify Admin Test surface must show the current execution target before the Run action.

When a valid selected shop with an offline session is available, show at minimum:

```text
Target shop: <selectedShop.domain>
Shopify offline session: Available
```

When no selected shop is available, show a persistent instruction equivalent to:

```text
Select an Authoring shop before running this Shopify Admin Tool.
```

and disable `Run Test`.

When a selected shop exists but `shopifyOfflineSessionAvailable === false`, show the selected shop domain plus an unavailable-session message and disable `Run Test`.

`Run Test` is enabled only when all existing authoring prerequisites are satisfied **and**:

```text
selectedShop != null
selectedShop.shopifyOfflineSessionAvailable === true
```

Do not rely on a click-time local error as the normal no-shop UX.

C082 remains authoritative at execution time. The client availability flag is a UX gate only; the Server Action must continue resolving the supplied shop ID and validating the current offline session server-side.

The live-Test request remains exactly the existing narrow shape:

```text
definition
arguments
shopId
```

Do not send domain, session availability, tokens or credentials to the action as trusted execution data.

Changing the selected shop must retain the existing C083 Test-staleness semantics and must never allow a previous target's result to become current again.

### R3 — persistence mutations use a synchronous admission gate

`ToolAuthoringScreen` is the common admission boundary for Tool lifecycle writes. Harden its mutation path so the first activation synchronously acquires the gate **before** a new operation ID is generated or any asynchronous work is dispatched.

The rule is:

```text
first activation
  -> synchronously acquire mutation gate
  -> allocate exactly one operationId
  -> dispatch exactly one mutation
  -> known success / known failure: release gate
  -> unknown outcome: keep original operation admitted and locked
```

While one mutation is admitted, repeated Save/Create/Publish/Edit-as-new-draft/Create-draft submissions must not create another operation ID or invoke another mutation.

The existing rendered `pending`/disabled state remains required for feedback but is not the correctness barrier.

Unknown outcomes must preserve the exact admitted operation ID. `Check original operation` must synchronously reject repeated reconciliation activation while one reconciliation call is in flight and must never replay the original mutation.

### R4 — async authoring actions are single-flight for the submitted action identity

Audit every active Tool-authoring button that dispatches provider I/O, a Server Action, an async validator, or a one-shot authoring hand-off. Add a synchronous admission gate where one is not already present.

The current audit must include at least:

```text
Shopify Admin Request: Validate
Shopify Admin Response: Derive result contract
Shopify Admin Test: Run Test
External Request: Validate request
External Request: Preview request
External Response: Validate response
External Response: Generate from live response
External Test: Run live test
Result Template: Validate Result Template
persisted Review validation actions
new/persisted provider selection requiring Admin metadata
Reset and change Tool type when it starts Admin metadata loading
Explore Shopify authoring-session hand-off
Check original operation
all Tool lifecycle Save/Create/Publish actions routed through runCommand/mutate
```

For candidate-keyed actions, the gate may be keyed by the canonical submitted identity so an obsolete in-flight request can be ignored and a genuinely changed candidate can be treated according to the component's existing stale-result model. The same current identity must never dispatch twice concurrently.

Preserve existing stronger guards such as `ShopifyAdminTestTab.activeRuns`; do not replace a correct monotonic stale-result mechanism with a weaker global boolean.

If the candidate changes while an old action is in flight, the old completion must not overwrite or resurrect current state.

### R5 — Explore Shopify is a one-shot authoring hand-off

`Explore Shopify` currently creates a new authoring-session ID, persists a browser-local session and navigates. Repeated same-tick activation must create at most one new authoring session and one navigation hand-off.

Do not create multiple orphaned local sessions from a double click.

The gate may clear only when the hand-off fails synchronously and the user can safely retry; successful navigation/unmount naturally ends the source surface.

### R6 — provider reset cannot duplicate metadata requests

Initial Shopify Admin Tool-type selection and confirmed `Reset and change Tool type` may require `getShopifyAdminAuthoringMetadataAction()`.

Repeated activation for the same requested provider while the selection is in flight must issue one metadata request. Preserve the existing generation/stale-completion protection when the requested provider genuinely changes.

The confirmation dialog must remain frozen until Cancel or the admitted provider replacement settles, preserving COMMERCE-095 traversal rules.

### R7 — button audit is explicit and bounded

The implementing agent must inspect every rendered `<button>` in the active Tool-authoring flow and classify it in the Completion Report as one of:

```text
CONSEQUENTIAL_ASYNC
ONE_SHOT_HANDOFF
LOCAL_REPEATABLE
```

Every `CONSEQUENTIAL_ASYNC` and `ONE_SHOT_HANDOFF` action must identify its synchronous admission mechanism and focused regression coverage.

`LOCAL_REPEATABLE` controls must not gain arbitrary debounce/locking. Examples normally include tabs, Previous/Next, insertion helpers and local Add/Remove controls.

Dead/unmounted legacy components do not need churn solely to satisfy the audit; record that they are not reachable from the current Tool-authoring composition.

### R8 — no security or lifecycle weakening

This is UI admission hardening, not a substitute for server correctness.

Preserve:

```text
server-side Studio authorization
server-side selected-shop resolution
Shopify offline-session/token lookup
operation IDs and durable idempotency
CAS editVersion checks
unknown-outcome reconciliation
zero-write live Test boundaries
C083 Test freshness/staleness
C095 progressive navigation
```

No browser-side gate may be treated as an authorization, credential or durable deduplication mechanism.

## Work Items

- [x] Make `shopSelection.selectedShop` the only Tool-authoring shop context after server resolution.
- [x] Propagate the non-secret selected `ShopExecutionContext` to Shopify Admin Test.
- [x] Render target shop/offline-session status and disable Run Test when the target is not executable.
- [x] Add a synchronous gate to the common Tool mutation/reconciliation boundary.
- [x] Add/preserve candidate-keyed single-flight guards for all active async Tool-authoring actions in R4.
- [x] Make Explore Shopify a one-shot local-session/navigation hand-off.
- [x] Prevent duplicate Shopify Admin metadata loads for the same provider selection/reset.
- [x] Add same-tick repeated-activation regressions and selected-shop execution-context regressions.
- [x] Record the complete Tool-authoring button classification/gate inventory in the Completion Report.

## Interfaces / Contracts

Consumes:

- `StudioShopSelection` / `ShopExecutionContext` from the existing selected-shop boundary;
- COMMERCE-082 server-authoritative Shopify Admin candidate Test;
- COMMERCE-083 common Shopify Admin Test freshness/result behavior;
- COMMERCE-095 progressive authoring navigation;
- existing Tool mutation operation-ID/CAS/reconciliation contracts.

The synchronous UI-gate semantics may follow `components/pending-action-form.tsx` as the already-proven local pattern, but this task must not route unrelated Tool authoring through that form component merely for reuse.

Produces no new cross-repository contract.

## Dependencies

- `ARCH-021-COMMERCE-083`
- `ARCH-021-COMMERCE-095`

## Enables

- `ARCH-021-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] An invalid/stale URL `shopId` cannot reach Tool authoring after `resolveStudioShopSelection` resolves no selected shop.
- [x] Shopify Admin Test visibly identifies the selected shop domain when one exists.
- [x] With no selected shop, Run Test is disabled and C082 is not called.
- [x] With a selected shop whose offline session is unavailable, Run Test is disabled and C082 is not called.
- [x] With a selected shop whose offline session is available, existing Test prerequisites and C082 execution continue to work without exposing credentials.
- [x] Changing shop context stales/clears the previous Shopify Test result exactly as the existing freshness contract requires.
- [x] Two or more same-tick activations of one Tool lifecycle write dispatch exactly one mutation and allocate exactly one operation ID.
- [x] An unknown mutation outcome remains locked to its original operation ID; repeated reconciliation activation dispatches one reconciliation call and never replays the mutation.
- [x] Every active consequential async action listed in R4 has a synchronous re-entry guard; same-identity repeated activation dispatches exactly once.
- [x] Explore Shopify repeated same-tick activation creates one authoring-session hand-off/navigation.
- [x] Shopify Admin provider selection/reset repeated activation issues one metadata request for the admitted selection.
- [x] Stale async completions cannot overwrite current candidate state.
- [x] Local repeatable controls remain responsive and are not globally debounced.
- [x] Completion Report contains the full rendered Tool-authoring button classification and guard/test mapping.

## Validation

- [x] Focused selected-shop route/composition tests prove validated `selectedShop` authority, including invalid/stale URL input.
- [x] Focused Shopify Admin Tool UI tests cover no shop, no offline session, visible target domain, executable target and shop-change staleness.
- [x] Same-tick `fireEvent` regression for common Tool lifecycle mutation admission proves one invocation/one operation ID.
- [x] Same-tick reconciliation regression proves one check of the original operation and zero mutation replay.
- [x] Same-tick regressions cover each active R4 action directly or through a shared gate unit test plus explicit integration wiring assertions for every action owner.
- [x] Existing Shopify Admin and External live-Test stale-result/concurrency suites remain passing.
- [x] Targeted ESLint for changed files.
- [x] Targeted TypeScript diagnostics for changed files, plus the package-declared task-relevant typecheck when available under the repository baseline.
- [x] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin SYSTEM-TEST-002 or any Policy Operation follow-on task.

## Implementation Notes

Prefer a synchronous `useRef` admission token/gate, acquired before `setState`, `newOperationId()`, Server Action invocation, provider invocation, local session creation or navigation. React `disabled={pending}` remains presentation/feedback only.

Do not use time-based debounce/throttle as the correctness mechanism.

For a mutation with an unknown outcome, do not clear the admitted operation merely because the HTTP promise rejected; the original ID remains authoritative until reconciliation proves committed or not committed.

## Completion Report

### Status

Complete; ready for architecture review. Attempt remains 1. This report is now ready for publication.

### Files Changed

Commerce implementation:

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/external-http/request-tab.tsx`
- `src/studio/external-http/response-tab.tsx`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `src/studio/tools/authoring/review-tab.tsx`
- `src/studio/tools/authoring/shopify-admin-test-tab.tsx`
- `src/studio/tools/authoring/tool-definition-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/shopify-admin-editor.tsx`
- `src/studio/tools/shopify-admin-response-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`

Focused tests:

- `tests/external-tools-ui.test.tsx`
- `tests/feature-configuration-page.test.tsx`
- `tests/result-template-tab.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/selected-shop-route.test.tsx`
- `tests/selected-shop-navigation.test.tsx`

### Work Completed

Validated `shopSelection.selectedShop` is now the sole selected-shop context passed through the Tools route. Shopify Admin Test displays the selected domain and session availability, disables execution without an executable selected shop, and continues sending only `{ definition, arguments, shopId }` to the server action. Server-side authorization/session resolution and C083 freshness remain authoritative.

Added synchronous admission and stale-completion protection at the active action owners. Lifecycle writes acquire the common mutation gate before allocating an operation ID; unknown outcomes retain the operation lock and reconciliation has its own in-flight gate. Candidate-keyed validation/preview/derivation and test-run gates preserve current identity/generation checks. Provider selection deduplicates metadata loads; Explore Shopify admits one local-session/navigation hand-off. Existing progressive navigation, CAS, idempotency and zero-write Test behavior are preserved.

Corrected External Request Validate and Preview completion freshness by synchronizing authoritative current-action-key refs in layout effects and checking those refs for parse, action-result, and thrown-error completion paths. Added deferred A/B tests that complete B before A for both actions; retained same-tick admission tests.

Provider reset now has a separate synchronous admitted-reset lock and pending presentation state. While Shopify metadata is unresolved, traversal, provider selection, repeated Reset and Cancel remain locked. Success installs the replacement and closes confirmation; known failure clears busy state but keeps confirmation available for Retry or Cancel. A deferred-success test checks the in-flight behavior and a known-failure test checks recovery. Initial provider selection generation/supersession behavior remains unchanged.

#### R7 Button Audit

Classification applies to rendered buttons in the active Tool-authoring composition. Repeated controls are grouped by owner and behavior; local edits/navigation are not artificially locked.

| Classification | Rendered action(s) | Synchronous admission and focused regression coverage |
| --- | --- | --- |
| `CONSEQUENTIAL_ASYNC` | New Tool Save; persisted Save draft, Publish, Create draft and Edit as new draft | Common `ToolAuthoringScreen.mutate` ref gate is acquired before operation-ID creation and dispatch. `tests/tool-authoring-screen.test.tsx`: exact returned identities after confirmed creation; lost final create reconciliation without mutation replay. Persisted writes in `tests/shopify-admin-tools-ui.test.tsx` and `tests/external-tools-ui.test.tsx`. |
| `CONSEQUENTIAL_ASYNC` | Check original operation | `reconciliationInFlight` ref gate; keeps the original operation ID and never replays the write. `tests/tool-authoring-screen.test.tsx`: `reconciles a lost final create without replaying the mutation` repeats the check in one tick and asserts one reconcile call. |
| `CONSEQUENTIAL_ASYNC` | Shopify Admin Request Validate | Canonical candidate key plus monotonic generation and `validationInFlight` set; obsolete completions are ignored. `tests/shopify-admin-tools-ui.test.tsx`: `does not accept an old Shopify Request validation after A-to-B-to-A` also double-activates the initial identity in the same tick. |
| `CONSEQUENTIAL_ASYNC` | Shopify Admin Response Derive result contract | Canonical action key plus monotonic identity and `derivationsInFlight` set. `tests/shopify-admin-tools-ui.test.tsx`: `does not apply an old Shopify Response derivation after A-to-B-to-A` also verifies same-tick duplicate admission. |
| `CONSEQUENTIAL_ASYNC` | Shopify Admin Run Test and Policy Operation Run Test | Candidate/shop/arguments identity, synchronous `activeRuns` set, sequence and latest-identity checks. Coverage: Shopify shop-and-arguments A-to-B-to-A test double-activates its first run; the `runPolicyOperationTest` helper double-activates Run Test in one tick, alongside Policy Test transient-arguments/shop A-to-B-to-A coverage in `tests/shopify-admin-tools-ui.test.tsx`; C083 zero-write, target and staleness cases are in the same file. Policy lifecycle remains owned by COMMERCE-099/100. |
| `CONSEQUENTIAL_ASYNC` | External Request Validate request and Preview request | Separate canonical-identity `validationInFlight` and `previewInFlight` sets. `tests/external-tools-ui.test.tsx`: same-tick Validate/Preview tests plus `keeps the newer External Request validation when an older validation completes last` and the equivalent Preview regression verify stale A-after-B completions. |
| `CONSEQUENTIAL_ASYNC` | External Response Validate response | Validation-generation keyed `responseValidationsInFlight` set; completion applies only while its generation is current. `tests/external-tools-ui.test.tsx`: `ignores late Response validation results after the authored path changes` double-activates the current action in one tick; `validates only Response fields and invalidates stale validation after an edit` covers contract behavior. |
| `CONSEQUENTIAL_ASYNC` | External Response Generate from live response | Context/generation-keyed `automaticRunsInFlight` set; stale observations cannot apply candidates. `tests/external-tools-ui.test.tsx`: `does not apply an old live-response generation after Request context A-to-B-to-A` also double-activates the first generation. |
| `CONSEQUENTIAL_ASYNC` | External Run live test | Candidate identity and synchronous `activeRuns` set, with sequence/latest-identity checks. `tests/external-tools-ui.test.tsx`: `prevents duplicate submissions and discards an older out-of-order result`. |
| `CONSEQUENTIAL_ASYNC` | Result Template Validate Result Template | Candidate key and synchronous `validationInFlight` set. `tests/result-template-tab.test.tsx`: `coalesces same-tick Result Template validation dispatches`. |
| `CONSEQUENTIAL_ASYNC` | Persisted Shopify Admin and External Review Validate | Candidate-keyed `reviewValidationInFlight` sets and current-action-key checks; pending state is presentation only. Coverage: Shopify Review A-to-B-to-A test double-activates the first candidate in the same tick; External Review A-to-B-to-A test does likewise in `tests/shopify-admin-tools-ui.test.tsx` and `tests/external-tools-ui.test.tsx`. |
| `CONSEQUENTIAL_ASYNC` | Initial/new/reset Shopify Admin provider selection when metadata is required | `providerSelectionsInFlight` keyed by requested provider, plus provider generation checks. `tests/tool-authoring-screen.test.tsx`: `admits only one same-tick Shopify provider metadata load`, Shopify-to-External stale-completion, deferred provider-reset lock, and known-failure recovery tests. The persisted Shopify Admin metadata read runs once per editor mount and is not a rendered-button action. |
| `ONE_SHOT_HANDOFF` | Explore Shopify (new and persisted authoring) | `exploreHandoffInFlight` is acquired before session ID creation, browser-local persistence and navigation; it clears only on synchronous failure. The new-session round-trip regression in `tests/tool-authoring-screen.test.tsx` double-activates Explore in one tick and asserts one history hand-off; persisted identity coverage is in `tests/shopify-admin-tools-ui.test.tsx`. |
| `LOCAL_REPEATABLE` | Tool library Create Tool; Return to Tools; Back/discard navigation and confirmation; Review Cancel / Cancel unsaved changes; provider-reset Cancel | Local session, navigation or dialog state only; no provider/server dispatch. |
| `LOCAL_REPEATABLE` | Tool authoring tabs; Previous/Next; ordinary field edits and mode selection; local request/result mapping Add/Remove; visual field/filter Add/Remove; insertion and local response/result-template helpers | Synchronous local state transformations. Intentionally no debounce or async admission lock. |
| `LOCAL_REPEATABLE` | Policy Operation Validate Tool Definition and Validate Request | Synchronous local validation; no provider or server-action dispatch. |

`src/studio/tools/authoring/agent-contract-tab.tsx` is a legacy, unmounted component: no imports or mount sites exist in the active composition, and the persisted-tab regression asserts that Agent Contract is absent. It is excluded from this rendered-button audit.

### Validation Results

Passed the final focused packet after all corrections and direct same-tick coverage: 7 files, 195 tests. The Shopify Admin and Policy Test owner suite passed at 41 tests after the final Policy Test duplicate-activation assertion.

Targeted ESLint across the complete C102-changed implementation/test set passed without warnings or errors. `npm run typecheck` passed (`next typegen && tsc --noEmit`) after regenerating the local Prisma Client with `npx prisma generate --schema database/prisma/schema.prisma`; no schema or migration changes were made. Changed-file diagnostics reported no TypeScript issues in the C102-changed file set, and `git diff --check` passed.

#### Broader Suite Baseline Comparison

The seven `tests/studio-workspace.test.tsx` failures reproduce before C102 changes. Ran the suite in a detached clean worktree at pre-C102 commit `8fb5ebdffb2491803a3918bfb98aa5a51ce56c3a` (created with `git worktree add --detach /tmp/ARCH-021-COMMERCE-102-baseline 8fb5ebdffb2491803a3918bfb98aa5a51ce56c3a`, installed that checkout's lockfile dependencies with `npm ci`, then ran `npm run test -- --run tests/studio-workspace.test.tsx`): **7 failed, 5 passed (12)**. The C102-modified worktree run produced the same **7 failed, 5 passed (12)** and the same observed failures: both Shopify Admin draft workflow assertions look for `Save draft` and fail at test lines 191 and 225. This is baseline evidence, not an inference that the suite is unrelated based only on the task-focused packet. The detached baseline worktree was removed after evidence capture.

### Deviations

The package-manager `pnpm test` invocation was blocked before running tests by pnpm's ignored-build-script approval gate. The same focused tests were run successfully with the repository's npm script. The failed pnpm setup generated untracked `pnpm-lock.yaml` and `pnpm-workspace.yaml` files in the implementation worktree; only those command-generated files were removed. No existing user changes were reverted. A separate detached baseline worktree and npm dependency installation were used only for the required pre-C102 failure comparison.

### Assumptions

`ShopExecutionContext` is the sole browser-safe execution context; its shop ID is submitted as the existing C082 action input, while domain/session-availability are display-only and no credentials cross the browser boundary. Policy Operation lifecycle changes remain outside this task's scope.

### Unresolved Issues

The 7 `tests/studio-workspace.test.tsx` failures remain, but exact pre-C102 baseline evidence above demonstrates they reproduce without C102 changes. No C102-specific validation, lint or typecheck failures remain.

### Architectural Concerns

None. Client-side admission remains a UX/concurrency guard only; durable idempotency, CAS, authorization, offline-session lookup and reconciliation remain server-authoritative.

## Architect Review

### Review Status

Accepted

### Review Notes

ARCH-021-COMMERCE-102 is **Complete / Accepted, Attempt 1**.

The selected-shop execution boundary is corrected end to end: only the server-resolved `shopSelection.selectedShop` reaches Tool authoring, Shopify Admin Test visibly identifies the selected target/session availability, and Run Test remains disabled unless that target is executable. No credentials are exposed to the browser; C082 remains the server-authoritative authorization/session boundary.

Consequential Tool-authoring actions now use synchronous admission before operation-ID allocation, Server Action/provider dispatch, local session creation or navigation. Candidate/context identity plus monotonic generation prevents stale async completions from becoming current again, including A -> B -> A reversion. Unknown mutation outcomes retain the original operation ID for reconciliation and never replay the mutation.

The final bounded corrections are accepted: External Request Validate/Preview completion checks use authoritative current-action-key refs after `await`, and confirmed Shopify provider reset stays frozen while metadata resolution is in flight, with deterministic success/failure release behavior.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/external-http/request-tab.tsx`
- `src/studio/external-http/response-tab.tsx`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `src/studio/tools/authoring/review-tab.tsx`
- `src/studio/tools/authoring/shopify-admin-test-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/shopify-admin-editor.tsx`
- `src/studio/tools/shopify-admin-response-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`
- focused C102 route/navigation/Tool-authoring regression files listed in the Completion Report.

Implementation commit reviewed: `b295545`.

Parent review handoff: `2c5904bb`; parent branch was subsequently synchronized with current `origin/main` at `d58cc6538ee1dd24f4c86b291d8e4494afa10a4c` before acceptance coordination.

### Validation Reviewed

- Final focused packet: **7 files, 195 tests passed**.
- Targeted ESLint: passed with no warnings/errors.
- `npm run typecheck` (`next typegen && tsc --noEmit`): passed after local Prisma Client generation; no schema/migration change was made.
- Changed-file diagnostics: no C102 TypeScript errors.
- `git diff --check`: passed.
- Broad `tests/studio-workspace.test.tsx` baseline comparison: pre-C102 and C102 both produced the same **7 failed / 5 passed** result and the same observed `Save draft` failures, so those failures are not introduced by C102.
- Temporary detached baseline worktree was removed after evidence capture.
- Final parent and implementation task refs were reported clean and remote-aligned before the parent synchronization merge.

### Architecture Conformance

Accepted.

C102 preserves the existing Tool-authoring architecture rather than adding a second execution or persistence model. Client admission is a UX/concurrency correctness guard only; durable authorization, CAS/idempotency, offline-session resolution and reconciliation remain server-authoritative. Existing C082/C083/C095/C099/C100 ownership boundaries are preserved, local repeatable controls are not globally debounced, and Policy Operation lifecycle semantics are not reopened.

### Follow-up

Mark ARCH-021-COMMERCE-102 Complete.

COMMERCE-103 is already Complete, so every declared dependency of `ARCH-021-SYSTEM-TEST-002` is now Complete. Promote SYSTEM-TEST-002 to **Ready** as terminal integrated Tool-authoring validation. Do not start it automatically from this acceptance.
