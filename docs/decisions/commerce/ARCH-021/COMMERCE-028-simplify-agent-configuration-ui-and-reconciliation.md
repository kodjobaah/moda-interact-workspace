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
status: review
priority: 20
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-025
  - ARCH-021-COMMERCE-026
  - ARCH-021-COMMERCE-027
  - ARCH-021-COMMERCE-011
  - ARCH-021-COMMERCE-012
  - ARCH-021-COMMERCE-013
  - ARCH-021-COMMERCE-014
  - ARCH-021-COMMERCE-031
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

- [x] Remove Agent Configuration action-object props.
- [x] Import named actions directly in Agent Configuration domain components.
- [x] Replace replay/unknown UI with explicit errors + R3/R4 reconciliation.
- [x] Update UI to reduced config/template DTOs.
- [x] Preserve existing dirty/stale/CAS protections.
- [x] Update focused UI tests.

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
- ARCH-021-COMMERCE-031

## Enables

- ARCH-021-COMMERCE-029

## Acceptance Criteria

- [x] No production Agent Configuration function bundle crosses Server -> Client.
- [x] Known errors are visible with their real codes.
- [x] Transport-level uncertainty is visible and reconcilable.
- [x] Reconciliation never replays stored mutation results.
- [x] A database outage is not mislabeled as a committed/unknown operation.
- [x] Existing dirty/stale/CAS protections remain.

## Validation

- [x] model UI focused tests
- [x] prompt UI focused tests
- [x] template UI focused tests
- [x] rejected-Promise -> UNCONFIRMED -> reconcile committed test
- [x] reconcile not-committed -> retry-enabled test
- [x] DB unavailable visible error test
- [x] targeted ESLint/typecheck (targeted ESLint passed; repository typecheck remains blocked by pre-existing unrelated errors)
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.


## Implementation Notes

"Reconcilable" does not mean "swallow every error into unknown". Typed server errors remain errors. Reconciliation exists for the narrow case where the client did not receive a trustworthy typed outcome.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation commit `354c06b` on `task/ARCH-021-COMMERCE-028`:

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/platform-model-configuration.tsx`
- `src/studio/agent-configuration/platform-prompt-configuration.tsx`
- `src/studio/agent-configuration/prompt-template-library.tsx`
- `src/studio/agent-configuration/shop-agent-configuration.tsx`
- `tests/agent-configuration-model-ui.test.tsx`
- `tests/agent-configuration-platform-prompt-ui.test.tsx`
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-template-ui.test.tsx`
- `tests/agent-configuration-screen-state.test.tsx`
- `tests/agent-configuration-shop-ui.test.tsx`

### Work Completed

- Direct named Server Actions are used by Agent Configuration client surfaces; function-valued action bundles, replay/unknown-result UI, and stored mutation closures are absent.
- Platform and selected-shop surfaces use reduced model/prompt configuration DTOs, preserve configuration-row CAS tokens when clearing overrides, validate selected-shop forwarding, and show the bounded no-shop state.
- Agent Configuration owns independent dirty and unconfirmed flags, reports aggregate state to StudioWorkspace, and locks navigation while an operation is unconfirmed.
- Reconciliation uses the original operation receipt, reloads canonical state before the committed message, enables retry only after not-committed, retains reconciliation control on errors, and supports explicit abandonment.
- Focused tests cover model, prompt, template, shop, production selected-shop validation, reconciliation state transitions, database errors, dirty aggregation, and navigation locking.

### Validation Results

- Exact `npm exec vitest run tests/agent-configuration-model-ui.test.tsx tests/agent-configuration-platform-prompt-ui.test.tsx tests/agent-configuration-template-ui.test.tsx tests/agent-configuration-shop-ui.test.tsx tests/agent-configuration-screen-state.test.tsx tests/agent-configuration-production.test.tsx`: passed, 6 files / 18 tests, zero skipped.
- Targeted `npm exec eslint --` over all three Attempt 3 changed TS/TSX files and the six focused tests: passed.
- `git diff --check`: passed before commit.
- `npm run typecheck`: exit non-zero with 18 existing errors in 9 unrelated preview, integration, and older test files; no changed Agent Configuration file was reported.
- `npm run build`: blocked before compilation because `@jitl/quickjs-wasmfile-release-sync/package.json` is missing from the worktree dependency state.

### Deviations

- Full repository typecheck and production build could not complete because of the unrelated baseline/dependency blockers listed above.

### Assumptions

- The prepared launcher evidence remains authoritative: parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-028`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-028`, mirrored branch `task/ARCH-021-COMMERCE-028`.
- The implementation repository has its recorded nested submodule state from launcher preparation; no submodule pin was changed by this task.

### Unresolved Issues

- Repository-wide typecheck remains blocked by the 18 unrelated errors reported above.
- Production build remains blocked by the missing `@jitl/quickjs-wasmfile-release-sync` package metadata before Next.js compilation.

### Architectural Concerns

- None identified within the bounded Attempt 2 correction contract.

### Attempt 3 Completion Evidence

- A3-R1: `ShopAgentConfiguration` now consumes named `getShopAgentConfiguration(shopId)` and uses only `modelId`, `activePromptRevisionId`, `modelEditVersion`, and `promptEditVersion`; retained versions survive clear/reload. The shop UI test proves model and prompt set/version2, clear/null/version3, set/version3 sequences and cross-field version independence.
- A3-R2: the shop UI now consumes named `getShopPrompt(shopId)` for exact-shop durable lineage when the active pointer is null; it does not use platform lineage, Prisma, or a second client shop store.
- A3-R3: focused tests prove exact `Not committed`, retry with a different operation ID, reconciliation rejection with the original operation ID and exact `Reconciliation unavailable; try reconciliation again`, pending/retry lock, retained Reconcile/Abandon controls, and StudioWorkspace navigation lock/unlock composition.
- A3-R4: Attempt 2 behavior remains preserved, including validated shop forwarding, direct named actions, typed `DATABASE_UNAVAILABLE`, original reconciliation receipt, committed reload ordering, independent dirty flags, ADMIN read-only behavior, and no live provider/model execution.
- A3-R5: exact six-file packet passed with 6 files / 18 tests; targeted ESLint passed; full typecheck retained 18 unrelated baseline diagnostics with none in changed files; `git diff --check` passed.
- A3-R6: implementation commit `268eaa8` is pushed. Parent report commit and parity verification follow this edit.

### Attempt 3 Launcher and Publication Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-028`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-028`.
- Matching branches: `task/ARCH-021-COMMERCE-028` in both repositories.
- Start-of-attempt parent synchronization: `3501b0ed3f3101f569940d982e42f01764cf7f82`.
- Start-of-attempt implementation synchronization/head: `99f5dd2876920145115286de752eb0002c170704`.
- Attempt 3 claim: prepared launcher evidence recorded `execution_state: claimed`, executor `copilot`, attempt `3`, with parent claim committed/pushed before execution.
- Recursive submodule sync/update passed; database submodule commit: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation branch publication: `268eaa8` pushed to `origin/task/ARCH-021-COMMERCE-028`.
- Parent report publication: pending this report commit/push.
- No token, secret, database schema, or follow-on task was touched.

## Architect Review

### Review Status

Changes Requested — Attempt 2 (dependency resolved)

### Review Notes

#### Dependency resolution — 2026-09-24

`ARCH-021-COMMERCE-031` is architect-accepted Complete at Attempt 2. The retained
configuration read contract now exposes nullable override state together with the
real persisted `modelEditVersion` / `promptEditVersion`, and exact-shop durable prompt
lineage can be rediscovered independently of an active pointer.

The blocking prerequisite identified below is resolved. This same task returns to
`ready` with `attempt: 2`; the next authorized claim becomes Attempt 3.

The existing **Attempt 3 correction contract after COMMERCE-031 completes** below is
now authoritative. Execute A3-R1 through A3-R6 exactly; do not infer a reduced scope.

#### Historical Attempt 2 block

#### Attempt 2 review — 2026-09-24

Reviewed implementation `354c06b` and parent report `7f18953b` against the
Attempt 1 correction contract.

Attempt 2 correctly restores the server-validated selected-shop handoff, direct named
Server Actions, independent dirty/unconfirmed aggregation, Studio navigation locking,
and the transport-safe reconciliation state machine. Those changes must be preserved.

The task cannot be accepted or returned directly for UI-only rework because review
identified a missing prerequisite read contract in the already-completed
COMMERCE-025 boundary.

##### B1 — retained shop configuration CAS state is not readable after clear

`ShopAgentConfiguration.load()` currently derives CAS state from:

```text
getShopModelSelection(shopId)
getShopPromptPointer(shopId)
```

and then does:

```text
modelVersion  = selection?.editVersion ?? 1
promptVersion = pointer?.editVersion ?? 1
```

The accepted DATABASE-002 model deliberately retains one `CommerceAgentConfiguration`
row and clears nullable override fields instead of deleting/recreating the row.

The current service reads return `null` when the nullable override is absent:

```text
modelId == null                -> getShopModelSelection(...) returns null
activePromptRevisionId == null -> getShopPromptPointer(...) returns null
```

while clear mutations increment the retained row's corresponding CAS version.

Concrete failure:

```text
existing shop model row modelEditVersion = 2
clear with expectedEditVersion = 2
database row remains, modelId = null, modelEditVersion = 3
ShopAgentConfiguration reloads
getShopModelSelection(...) returns null
UI resets modelVersion to 1
next set sends expectedEditVersion = 1
service correctly returns CAS_CONFLICT
```

The same defect exists for `promptEditVersion`.

This violates R6 and Attempt 1 CR-1 step 7: clearing an override must return visibly
to platform inheritance **while preserving the retained configuration-row CAS
token**.

COMMERCE-028 must not read Prisma directly or reconstruct an edit version locally.
The missing canonical read belongs to the COMMERCE-025 service boundary.

##### B2 — durable shop prompt lineage cannot be rediscovered while inherited

The simplified shop UI obtains prompt choices only after
`getShopPromptPointer(shopId)` returns an active pointer. When the shop inherits the
platform prompt, that pointer is `null`, so the component has no prompt id from which
to load the shop's durable lineage. The selector therefore has no published
shop-specific revisions to select after a clear/reload even if a durable shop prompt
lineage exists.

COMMERCE-025 originally specified a `getShopPrompt` read. The current reduced service
snapshot exposes `getPrompt({promptId})`, `getPlatformPrompt()` and pointer reads but
does not expose a durable `getShopPrompt(shopId)` lookup.

The UI task must not query `CommerceAgentPrompt` directly to repair this.

##### Blocking dependency

Create and complete:

```text
ARCH-021-COMMERCE-031
Complete retained Agent Configuration read contract
```

COMMERCE-031 owns only the missing read capability. It does not change mutation,
audit, CAS, reconciliation, schema or UI semantics.

After COMMERCE-031 is architect-accepted Complete, return this same task to `ready`.
The next authorized claim will be Attempt 3.

#### Attempt 3 correction contract after COMMERCE-031 completes

Attempt 3 remains a COMMERCE-028 UI task. Implement only the following:

##### A3-R1 — consume the retained configuration DTO as the CAS source of truth

`ShopAgentConfiguration` must call the COMMERCE-031 named
`getShopAgentConfiguration(shopId)` read and use exactly:

```text
modelId
activePromptRevisionId
modelEditVersion
promptEditVersion
```

as its persisted override/CAS state.

Rules:

1. `modelId === null` means inherit the platform model; it does **not** mean
   `modelEditVersion = 1`.
2. `activePromptRevisionId === null` means inherit the platform prompt; it does
   **not** mean `promptEditVersion = 1`.
3. A missing configuration row may use the deterministic first-write baseline
   defined by COMMERCE-025.
4. After every successful set/clear and after reconciliation `committed`, reload the
   retained configuration DTO before enabling another mutation.
5. Do not synthesize, decrement or reset an existing row's CAS version in browser
   state.

Add exact regression:

```text
initial retained model version = 1
set model expected=1 -> reload version=2
clear model expected=2 -> reload modelId=null, version=3
set model again expected=3
```

and the equivalent independent prompt sequence.

Also prove clearing model leaves `promptEditVersion` unchanged and clearing prompt
leaves `modelEditVersion` unchanged.

##### A3-R2 — rediscover durable shop prompt lineage independently of active pointer

Use the COMMERCE-031 `getShopPrompt(shopId)` read when loading the selected shop.

- The durable shop prompt lineage must remain discoverable when
  `activePromptRevisionId` is null.
- Published revisions from that exact shop lineage may populate the shop prompt
  override control.
- Never use a platform prompt lineage as a shop override candidate.
- Shop id remains the validated id supplied by `ProductionStudioPage`.
- Do not add Prisma access or a second shop-selection store in the client.

##### A3-R3 — complete the missing mandatory Attempt 1 reconciliation proofs

The current 14-test packet does not prove all mandatory CR-6 cases. Add active
focused regressions for:

```text
1. reconcile not-committed:
   - original UNCONFIRMED clears
   - exact "Not committed" message
   - retry controls re-enable
   - next mutation uses a DIFFERENT operationId

2. reconciliation Promise rejection:
   - original operationId remains visible/unchanged
   - exact "Reconciliation unavailable; try reconciliation again" message
   - pending returns false
   - mutation retry remains disabled
   - Reconcile and Abandon remain available

3. Studio navigation lock:
   - any Agent Configuration child UNCONFIRMED => Composer blocker locked=true
   - ordinary discard cannot bypass that lock
   - Abandon OR committed/not-committed reconciliation clears the aggregate
     unconfirmed state and unlocks navigation
```

Do not satisfy these only by testing the child aggregate callback; prove the
`StudioWorkspace` navigation-blocker composition for the lock/unlock case.

##### A3-R4 — preserve all accepted Attempt 2 behavior

Do not regress:

```text
server-validated selected shop only
direct named Server Actions
no function-valued action bundles
no kind:'unknown'
typed DATABASE_UNAVAILABLE stays a typed error
exact original operationId used for Reconcile
committed reload occurs before "Committed; state refreshed"
independent template/platform/shop dirty flags
ADMIN read-only behavior
no live provider/model execution
```

##### A3-R5 — deterministic validation

Run exactly:

```bash
npm exec vitest run \
  tests/agent-configuration-model-ui.test.tsx \
  tests/agent-configuration-platform-prompt-ui.test.tsx \
  tests/agent-configuration-template-ui.test.tsx \
  tests/agent-configuration-shop-ui.test.tsx \
  tests/agent-configuration-screen-state.test.tsx \
  tests/agent-configuration-production.test.tsx
```

All six files must pass with zero skipped tests.

Run targeted ESLint over every COMMERCE-028 changed TypeScript/TSX file and the six
focused tests. Run `npm run typecheck` and retain the full diagnostics. No diagnostic
caused by the retained configuration DTO, shop-prompt read, CAS version flow or
Agent Configuration files changed by Attempt 3 may be classified as baseline.

Finally run:

```bash
git diff --check
```

##### A3-R6 — execution/report evidence

The Attempt 3 Completion Report must record exact launcher-provided:

```text
parent worktree path
implementation worktree path
matching task branches
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 3 claim evidence
recursive submodule materialization
database submodule commit
implementation commit
parent report commit
push parity
clean-worktree evidence
```

Do not reuse or infer values from Attempt 2.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/platform-model-configuration.tsx`
- `src/studio/agent-configuration/platform-prompt-configuration.tsx`
- `src/studio/agent-configuration/prompt-template-library.tsx`
- `src/studio/agent-configuration/shop-agent-configuration.tsx`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `src/commerce/agent-configuration/model-service.ts`
- `src/commerce/agent-configuration/prompt-service.ts`
- the six COMMERCE-028 focused UI/production tests
- COMMERCE-025 accepted task contract and review

### Validation Reviewed

Submitted Attempt 2 evidence:

```text
focused packet: 6 files / 14 tests PASS
targeted ESLint: PASS
git diff --check: PASS
typecheck: non-zero with reported sibling/baseline diagnostics
build: blocked before compilation by missing QuickJS package metadata
```

Static review confirms the focused packet does not currently contain the mandatory
not-committed/new-operation-id proof, reconciliation-rejection proof, or actual
Studio navigation blocker lock/unlock proof required by Attempt 1 CR-6.

### Architecture Conformance

Blocked. The direct named-Server-Action and serializable `UNCONFIRMED` direction
conforms, but COMMERCE-028 cannot correctly round-trip the reduced retained-row CAS
contract using the currently exposed COMMERCE-025 reads. Fixing that inside the UI
would cross the accepted service ownership boundary. COMMERCE-031 is therefore a
required bounded prerequisite.

### Follow-up

- `ARCH-021-COMMERCE-031` is Complete / Accepted, Attempt 2.
- `ARCH-021-COMMERCE-028` is Ready at `attempt: 2`; the next authorized claim is
  Attempt 3 using A3-R1 through A3-R6 above.
- `ARCH-021-COMMERCE-029` remains Pending.
- Do not start COMMERCE-029.
