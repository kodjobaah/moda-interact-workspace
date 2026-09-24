---
id: ARCH-021-COMMERCE-028
architecture_id: ARCH-021
title: Simplify Agent Configuration UI and make failures reconcilable
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-09-24T16:00:53Z
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-025
  - ARCH-021-COMMERCE-026
  - ARCH-021-COMMERCE-027
  - ARCH-021-COMMERCE-011
  - ARCH-021-COMMERCE-012
  - ARCH-021-COMMERCE-013
  - ARCH-021-COMMERCE-014
enables:
  - ARCH-021-COMMERCE-029
created: 2026-09-24
updated: 2026-09-24
---

# Simplify Agent Configuration UI and make failures reconcilable

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`


## Objective

Remove Phase-2 action-bundle/replay/unknown-state UI machinery from Agent Configuration, consume named Server Actions directly, and provide explicit user-visible error plus read-only reconciliation for requests whose response is genuinely unconfirmed.

## Context

Current Agent Configuration components generate operation IDs, retain executable operation closures, interpret `kind:'unknown'`, and offer "Check original operation" because domain services stored replay results in audit metadata. The new service contract retains operationId only as an atomic audit receipt and exposes a read-only reconciliation action.

## Scope

Primary files:

```text
app/agent-configuration/page.tsx
components/production-studio-page.tsx
components/studio-workspace.tsx
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-model-configuration.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
src/studio/agent-configuration/prompt-template-library.tsx
src/studio/agent-configuration/*-server-actions.ts
src/studio/agent-configuration/reconciliation-server-actions.ts
tests/*agent-configuration*.test.tsx
```

## Out of Scope

- General Tools/Connections/Features/Release port removal (COMMERCE-029).
- Merchant-facing Agent Configuration UI. The auth boundary exists, but platform/shop configuration UI remains platform-admin controlled in this checkpoint.
- MCP changes.

## Requirements

### R1. No function-valued Agent Configuration action props

Remove production props/types equivalent to:

```text
agentConfigurationActions
agentConfigurationTemplateActions
agentConfigurationPromptActions
ModelConfigurationActions
TemplateConfigurationActions
PromptConfigurationActions
```

Client Agent Configuration components import named Server Actions directly from their `*-server-actions.ts` modules.

Server Components may pass serializable initial DTOs only.

### R2. No generic unknown result UI

Remove service-result handling for:

```text
kind:'unknown'
CONFLICTING_REPLAY
Check original operation
stored invoke() closure
```

Known Server Action results display their exact `code` and bounded `message`.

### R3. Preserve genuine unconfirmed transport state

When a Server Action Promise rejects before the client receives a typed result:

1. do not silently ignore the exception;
2. keep the generated `operationId` plus action label in serializable local state;
3. display a visible `UNCONFIRMED` notice containing a bounded error message;
4. offer `Reconcile`;
5. disable automatic retry until reconciliation completes or the user explicitly abandons the unconfirmed attempt.

Do not store a function/closure in reconciliation state.

### R4. Reconcile behavior

`Reconcile` calls `reconcileAgentConfigurationOperation({operationId})`.

- `committed`: reload canonical DTOs and show "Committed; state refreshed".
- `not-committed`: show "Not committed" and permit retry with a new operationId.
- explicit error: display the returned error and retain reconciliation control where appropriate.
- DB unavailable: keep state unconfirmed; do not falsely classify committed/not committed.

### R5. Explicit database failures

If Server Action returns `DATABASE_UNAVAILABLE`, render that code/message directly. Do not relabel it "outcome unknown".

### R6. Simplified configuration UX

Model and prompt overrides read/write the single `CommerceAgentConfiguration` DTO:

```text
modelId / modelEditVersion
activePromptRevisionId / promptEditVersion
```

Clearing override visibly returns to platform inheritance without deleting/recreating a configuration row.

### R7. Simplified template UX

Consume COMMERCE-026 current-template API. Remove template revision history/draft/publish controls while retaining categories and current promptText editing.

### R8. Existing correctness guards stay

Preserve:

```text
dirty prompt edit guards
stale shop-load isolation
navigation blocking
prompt publish immutability
CAS conflict display
server-validated selected shop
```

## Work Items

- [ ] Remove Agent Configuration action-object props.
- [ ] Import named actions directly in Agent Configuration domain components.
- [ ] Replace replay/unknown UI with explicit errors + R3/R4 reconciliation.
- [ ] Update UI to reduced config/template DTOs.
- [ ] Preserve existing dirty/stale/CAS protections.
- [ ] Update focused UI tests.

## Interfaces / Contracts

Consumes COMMERCE-025/026 mutation/reconciliation contracts and COMMERCE-027 platform authorization helpers.

## Dependencies

- ARCH-021-COMMERCE-025
- ARCH-021-COMMERCE-026
- ARCH-021-COMMERCE-027
- ARCH-021-COMMERCE-011
- ARCH-021-COMMERCE-012
- ARCH-021-COMMERCE-013
- ARCH-021-COMMERCE-014

## Enables

- ARCH-021-COMMERCE-029

## Acceptance Criteria

- [ ] No production Agent Configuration function bundle crosses Server -> Client.
- [ ] Known errors are visible with their real codes.
- [ ] Transport-level uncertainty is visible and reconcilable.
- [ ] Reconciliation never replays stored mutation results.
- [ ] A database outage is not mislabeled as a committed/unknown operation.
- [ ] Existing dirty/stale/CAS protections remain.

## Validation

- [ ] model UI focused tests
- [ ] prompt UI focused tests
- [ ] template UI focused tests
- [ ] rejected-Promise -> UNCONFIRMED -> reconcile committed test
- [ ] reconcile not-committed -> retry-enabled test
- [ ] DB unavailable visible error test
- [ ] targeted ESLint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

"Reconcilable" does not mean "swallow every error into unknown". Typed server errors remain errors. Reconciliation exists for the narrow case where the client did not receive a trustworthy typed outcome.

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

Changes Requested

### Review Notes

Attempt 1 is **not accepted**. The direct named-Server-Action / serializable `UNCONFIRMED` refactor is directionally correct and must be preserved, but the submitted implementation is incomplete against R1-R8 and is not ready to enable COMMERCE-029.

The next claim is Attempt 2. Implement **only** the correction contract below. Do not redesign COMMERCE-025/026/027 services, restore function-valued action bundles, restore `kind:'unknown'`, store mutation closures, or begin COMMERCE-029.

#### CR-1 — Restore the reduced selected-shop Agent Configuration surface

Files:

```text
components/production-studio-page.tsx
components/studio-workspace.tsx
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx   # restore/create
```

Required behavior:

1. In the `page === 'agent-configuration'` branch of `ProductionStudioPage`, derive exactly:

   ```ts
   const validatedShopId = shopSelection.selectedShop?.id;
   ```

2. Pass `validatedShopId` to `StudioWorkspace` as `shopId`. **Do not pass the raw query-string `shopId`** into Agent Configuration.
3. `StudioWorkspace` passes that validated `shopId` to `AgentConfigurationScreen`.
4. `AgentConfigurationScreen` renders the platform surfaces plus a reduced `ShopAgentConfiguration` when `shopId` is present. When it is absent, render a bounded "Select a shop to configure shop overrides" state and do not fabricate a shop id.
5. `ShopAgentConfiguration` imports named Server Actions directly. It must not receive function-valued action bundles.
6. The shop surface consumes the reduced DATABASE-002 contract only:

   ```text
   modelId / modelEditVersion
   activePromptRevisionId / promptEditVersion
   ```

   It must not reintroduce `generationId`, selection/pointer-table DTOs, stored-result replay, or `kind:'unknown'`.
7. Clearing a shop model/prompt override must visibly return to platform inheritance while preserving the retained configuration-row CAS token returned by the service.

#### CR-2 — Aggregate dirty state; one clean surface must never clear another dirty surface

Files:

```text
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/prompt-template-library.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx
components/studio-workspace.tsx
```

`AgentConfigurationScreen` must own independent dirty flags at minimum:

```text
templateDirty
platformPromptDirty
shopPromptDirty
```

and derive:

```ts
const agentConfigurationDirty =
  templateDirty || platformPromptDirty || shopPromptDirty;
```

A child reporting `false` must update only its own flag. It must **not** directly call the shared Studio dirty setter in a way that can clear another child's dirty state.

Report only the derived `agentConfigurationDirty` to `StudioWorkspace`.

#### CR-3 — UNCONFIRMED must lock Studio navigation, not only mutation buttons

Files:

```text
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-model-configuration.tsx
src/studio/agent-configuration/prompt-template-library.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx
components/studio-workspace.tsx
```

Each Agent Configuration surface that can mutate must report whether it currently owns an `UNCONFIRMED` operation. `AgentConfigurationScreen` aggregates those flags and reports one boolean to `StudioWorkspace`.

`StudioWorkspace` navigation blocking must satisfy:

```text
blocked = existingDirty || agentConfigurationDirty || existingUnknown || agentConfigurationUnconfirmed
locked  = existingUnknown || agentConfigurationUnconfirmed
```

Consequences:

- dirty state may be explicitly discarded by the existing Composer flow;
- `UNCONFIRMED` is locked and cannot be discarded through ordinary navigation;
- reconciliation to `committed` / `not-committed`, or explicit **Abandon**, clears the owning component's unconfirmed flag and therefore unlocks navigation;
- navigation state contains booleans only; never store a mutation closure in it.

#### CR-4 — Make reconciliation deterministic and transport-safe in every Agent Configuration mutating component

Files:

```text
src/studio/agent-configuration/platform-model-configuration.tsx
src/studio/agent-configuration/prompt-template-library.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx
```

Every `reconcile()` implementation must use this state machine:

```text
no UNCONFIRMED -> return
set pending=true
call reconcileAgentConfigurationOperation({ original operationId })

committed:
  reload canonical DTOs
  clear UNCONFIRMED
  set final message exactly: "Committed; state refreshed"

not-committed:
  clear UNCONFIRMED
  set final message exactly: "Not committed"
  next explicit mutation retry generates a NEW operationId

error / DATABASE_UNAVAILABLE / FORBIDDEN / INTERNAL_ERROR:
  retain original UNCONFIRMED operationId
  render returned `code` + bounded `message`
  keep mutation retry disabled
  Reconcile remains available
  Abandon remains available

reconciliation Promise rejects:
  retain original UNCONFIRMED operationId
  set bounded message exactly: "Reconciliation unavailable; try reconciliation again"
  keep mutation retry disabled
  Reconcile remains available
  Abandon remains available

always:
  pending=false in `finally`
```

For the committed path, call/reload canonical state **before** assigning the final `"Committed; state refreshed"` message so a loader that clears status text cannot erase the required final message.

A typed mutation result `DATABASE_UNAVAILABLE` is **not** `UNCONFIRMED`; display its real code/message directly. Only a rejected mutation Promise creates `UNCONFIRMED`.

#### CR-5 — Preserve operation identity and explicit retry semantics

For every mutating Agent Configuration component:

```text
mutation starts -> generate operationId once
Promise rejects -> retain exactly that operationId in serializable UNCONFIRMED state
Reconcile -> use exactly that operationId
Reconcile not-committed -> clear it
next mutation retry -> generate a different/new operationId
```

Do not retain the original mutation function/closure and do not replay the original mutation during reconciliation.

#### CR-6 — Migrate the stale UI tests to the direct-action / UNCONFIRMED architecture

Files that must be migrated and active:

```text
tests/agent-configuration-model-ui.test.tsx
tests/agent-configuration-platform-prompt-ui.test.tsx
tests/agent-configuration-template-ui.test.tsx
```

Create:

```text
tests/agent-configuration-shop-ui.test.tsx
tests/agent-configuration-screen-state.test.tsx
```

The tests must **not** import or construct:

```text
ModelConfigurationActions
TemplateConfigurationActions
PromptConfigurationActions
actions={...}
promptActions={...}
templateActions={...}
kind:'unknown'
Check original operation
stored/replayed invoke closures
```

Instead, use `vi.mock(...)` on the named modules used by production code:

```text
src/studio/agent-configuration/model-server-actions.ts
src/studio/agent-configuration/prompt-server-actions.ts
src/studio/agent-configuration/template-server-actions.ts
src/studio/agent-configuration/effective-server-actions.ts
src/studio/agent-configuration/reconciliation-server-actions.ts
```

Required focused proofs:

1. rejected mutation Promise -> visible `UNCONFIRMED` + exact operationId retained + mutation controls disabled;
2. reconcile `committed` -> canonical reload -> `Committed; state refreshed` -> writes enabled;
3. reconcile `not-committed` -> `Not committed` -> retry enabled -> retry uses a new operationId;
4. reconcile Promise rejection -> original operation remains UNCONFIRMED, `pending` returns false, Reconcile remains available;
5. typed `DATABASE_UNAVAILABLE` mutation result -> exact code/message rendered, no UNCONFIRMED state;
6. one dirty child + another clean child -> Studio remains dirty;
7. any UNCONFIRMED child -> Studio navigation blocker is `locked`; Abandon/reconciled outcome unlocks;
8. shop UI uses only the supplied validated shop id and reduced CAS DTOs.

#### CR-7 — Tighten production composition tests around selected-shop validation

File:

```text
tests/agent-configuration-production.test.tsx
```

For a resolver result containing `selectedShop.id === 'shop-01'`, assert:

```ts
expect(state.workspaceProps).toMatchObject({
  page: 'agent-configuration',
  agentConfigurationEnvironment: 'STAGING',
  shopId: 'shop-01',
});
```

Add a negative case:

```text
raw query shopId = "attacker-or-missing-shop"
resolveStudioShopSelection(...) returns selectedShop = null/undefined
StudioWorkspace shopId is undefined
raw query value is never forwarded to AgentConfigurationScreen
```

Continue asserting that production Agent Configuration props contain none of:

```text
agentConfigurationActions
agentConfigurationTemplateActions
agentConfigurationPromptActions
```

#### CR-8 — Reconcile task/report state before resubmission

The supplied parent task snapshot still contains `Completion Report -> Status: Not Started` and unchecked task/validation boxes despite implementation changes. Attempt 2 must update all executor-owned task state honestly:

- Work Items: check only actually completed items;
- Acceptance Criteria: check every satisfied criterion;
- Validation: record exact commands/results;
- Completion Report Status: `Ready for Review`;
- Files Changed: complete list;
- Validation Results: include focused tests, ESLint, typecheck result/baseline and `git diff --check`;
- Deviations / Assumptions / Unresolved Issues / Architectural Concerns: explicit values;
- physical parent + implementation worktree paths, start-of-attempt synchronization and recursive submodule evidence;
- final implementation commit, final parent report commit, push parity and clean-worktree evidence.

### Reviewed Files

```text
components/production-studio-page.tsx
components/studio-workspace.tsx
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-model-configuration.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
src/studio/agent-configuration/prompt-template-library.tsx
src/studio/agent-configuration/model-server-actions.ts
src/studio/agent-configuration/prompt-server-actions.ts
src/studio/agent-configuration/template-server-actions.ts
src/studio/agent-configuration/reconciliation-server-actions.ts
tests/agent-configuration-production.test.tsx
tests/agent-configuration-model-ui.test.tsx
tests/agent-configuration-platform-prompt-ui.test.tsx
tests/agent-configuration-template-ui.test.tsx
```

### Validation Reviewed

The partial implementation reports targeted production/template validation, ESLint and `git diff --check`, but the legacy model/prompt suites still encode removed action-bundle / `kind:'unknown'` contracts and the required shop/navigation reconciliation cases are missing. This is insufficient for acceptance.

Attempt 2 must execute exactly:

```bash
npm exec vitest run \
  tests/agent-configuration-model-ui.test.tsx \
  tests/agent-configuration-platform-prompt-ui.test.tsx \
  tests/agent-configuration-template-ui.test.tsx \
  tests/agent-configuration-shop-ui.test.tsx \
  tests/agent-configuration-screen-state.test.tsx \
  tests/agent-configuration-production.test.tsx
```

All six files must pass with **zero skipped tests**.

Then run targeted ESLint:

```bash
npm exec eslint \
  components/production-studio-page.tsx \
  components/studio-workspace.tsx \
  src/studio/agent-configuration/agent-configuration-screen.tsx \
  src/studio/agent-configuration/platform-model-configuration.tsx \
  src/studio/agent-configuration/platform-prompt-configuration.tsx \
  src/studio/agent-configuration/prompt-template-library.tsx \
  src/studio/agent-configuration/shop-agent-configuration.tsx \
  tests/agent-configuration-model-ui.test.tsx \
  tests/agent-configuration-platform-prompt-ui.test.tsx \
  tests/agent-configuration-template-ui.test.tsx \
  tests/agent-configuration-shop-ui.test.tsx \
  tests/agent-configuration-screen-state.test.tsx \
  tests/agent-configuration-production.test.tsx
```

Required result: **0 errors**.

Run typecheck and retain the complete diagnostic output:

```bash
npm run typecheck > /tmp/arch021-c028-typecheck.log 2>&1 || true
```

There must be **no diagnostics** in the following task-owned paths:

```text
components/production-studio-page.tsx
components/studio-workspace.tsx
src/studio/agent-configuration/
tests/agent-configuration-*.test.tsx
```

Finally:

```bash
git diff --check
```

### Architecture Conformance

Changes Requested. The direct-action and serializable UNCONFIRMED direction conforms to the simplification checkpoint, but the submitted state currently removes the shop configuration surface, does not lock Studio navigation on UNCONFIRMED operations, allows dirty-state overwrite between independent surfaces, and leaves stale bundle/replay tests. Those gaps violate R3, R4, R6 and R8.

### Follow-up

Return the **same** task through `/moda-task ARCH-021-COMMERCE-028`. The next authorized claim increments `attempt: 1` to Attempt 2. Do not start COMMERCE-029.
