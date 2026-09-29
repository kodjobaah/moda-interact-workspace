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
status: ready
priority: 73
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-083
  - ARCH-021-COMMERCE-095
enables:
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-29
updated: 2026-09-29
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

- [ ] Make `shopSelection.selectedShop` the only Tool-authoring shop context after server resolution.
- [ ] Propagate the non-secret selected `ShopExecutionContext` to Shopify Admin Test.
- [ ] Render target shop/offline-session status and disable Run Test when the target is not executable.
- [ ] Add a synchronous gate to the common Tool mutation/reconciliation boundary.
- [ ] Add/preserve candidate-keyed single-flight guards for all active async Tool-authoring actions in R4.
- [ ] Make Explore Shopify a one-shot local-session/navigation hand-off.
- [ ] Prevent duplicate Shopify Admin metadata loads for the same provider selection/reset.
- [ ] Add same-tick repeated-activation regressions and selected-shop execution-context regressions.
- [ ] Record the complete Tool-authoring button classification/gate inventory in the Completion Report.

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

- [ ] An invalid/stale URL `shopId` cannot reach Tool authoring after `resolveStudioShopSelection` resolves no selected shop.
- [ ] Shopify Admin Test visibly identifies the selected shop domain when one exists.
- [ ] With no selected shop, Run Test is disabled and C082 is not called.
- [ ] With a selected shop whose offline session is unavailable, Run Test is disabled and C082 is not called.
- [ ] With a selected shop whose offline session is available, existing Test prerequisites and C082 execution continue to work without exposing credentials.
- [ ] Changing shop context stales/clears the previous Shopify Test result exactly as the existing freshness contract requires.
- [ ] Two or more same-tick activations of one Tool lifecycle write dispatch exactly one mutation and allocate exactly one operation ID.
- [ ] An unknown mutation outcome remains locked to its original operation ID; repeated reconciliation activation dispatches one reconciliation call and never replays the mutation.
- [ ] Every active consequential async action listed in R4 has a synchronous re-entry guard; same-identity repeated activation dispatches exactly once.
- [ ] Explore Shopify repeated same-tick activation creates one authoring-session hand-off/navigation.
- [ ] Shopify Admin provider selection/reset repeated activation issues one metadata request for the admitted selection.
- [ ] Stale async completions cannot overwrite current candidate state.
- [ ] Local repeatable controls remain responsive and are not globally debounced.
- [ ] Completion Report contains the full rendered Tool-authoring button classification and guard/test mapping.

## Validation

- [ ] Focused selected-shop route/composition tests prove validated `selectedShop` authority, including invalid/stale URL input.
- [ ] Focused Shopify Admin Tool UI tests cover no shop, no offline session, visible target domain, executable target and shop-change staleness.
- [ ] Same-tick `fireEvent` regression for common Tool lifecycle mutation admission proves one invocation/one operation ID.
- [ ] Same-tick reconciliation regression proves one check of the original operation and zero mutation replay.
- [ ] Same-tick regressions cover each active R4 action directly or through a shared gate unit test plus explicit integration wiring assertions for every action owner.
- [ ] Existing Shopify Admin and External live-Test stale-result/concurrency suites remain passing.
- [ ] Targeted ESLint for changed files.
- [ ] Targeted TypeScript diagnostics for changed files, plus the package-declared task-relevant typecheck when available under the repository baseline.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin SYSTEM-TEST-002 or any Policy Operation follow-on task.

## Implementation Notes

Prefer a synchronous `useRef` admission token/gate, acquired before `setState`, `newOperationId()`, Server Action invocation, provider invocation, local session creation or navigation. React `disabled={pending}` remains presentation/feedback only.

Do not use time-based debounce/throttle as the correctness mechanism.

For a mutation with an unknown outcome, do not clear the admitted operation merely because the HTTP promise rejected; the original ID remains authoritative until reconciliation proves committed or not committed.

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
