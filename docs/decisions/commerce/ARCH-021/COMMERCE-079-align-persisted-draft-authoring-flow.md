---
id: ARCH-021-COMMERCE-079
architecture_id: ARCH-021
title: Align persisted DRAFT authoring with the Tool creation ownership model
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 76
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-078
enables:
  - ARCH-021-COMMERCE-081
  - ARCH-021-COMMERCE-083
  - ARCH-021-SYSTEM-TEST-002
created: 2026-09-28
updated: 2026-09-28
---

# Align persisted DRAFT authoring with the Tool creation ownership model

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Apply the same Tool Definition/Request/Response/Result Template/Test/Review ownership model to persisted External HTTP and Shopify Admin DRAFTs while preserving explicit CAS Save/Validate/Publish semantics.

## Context

COMMERCE-078 changes the new Tool creation flow. The current `ToolEditor` independently retains the regressed Agent Contract/template composition and has provider-specific layout divergence. Leaving that state would mean a Tool changes ownership models immediately after first Save.

This task is separate because persisted DRAFTs have different failure/persistence semantics: immutable Tool identity already exists, Save uses revision `editVersion` CAS, validation/publication operate on a saved revision, and Cancel must revert local edits rather than deleting a not-yet-created Tool.

## Scope

Primary implementation:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/tool-authoring-tabs.tsx           # consume shared registry/composition
src/studio/tools/authoring/tool-definition-tab.tsx           # consume persisted mode
src/studio/tools/authoring/result-template-tab.tsx           # consume
src/studio/tools/authoring/review-tab.tsx
```

Focused tests:

```text
tests/external-tools-ui.test.tsx
tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```


## Out of Scope

- Changing revision lifecycle, CAS rules or publication proof.
- Making immutable MCP name or provider kind mutable after Tool creation.
- Updating Tool-level display name/metadata through a draft save unless an already-existing explicit metadata action is intentionally invoked outside this task.
- External/Shopify new live-Test backend behaviour (C080/C082).
- Database changes.
- Non-External/non-Shopify legacy Tool editor cleanup unrelated to the supported authoring flow.

## Requirements

### R1 — persisted supported DRAFTs use the same six-step sequence

For `EXTERNAL_HTTP` and `SHOPIFY_ADMIN_GRAPHQL` DRAFTs, expose exactly:

```text
Tool Definition
Request
Response
Result Template
Test
Review
```

No Agent Contract tab is exposed.

### R2 — persisted Tool Definition has explicit mutability

Show in Tool Definition:

```text
MCP name          read-only
Display name      read-only summary of Tool metadata
Tool type         read-only
Description       editable definition.description
Definition version editable definition.definitionVersion
```

Do not introduce a provider-kind migration. Do not mutate Tool-level display name from draft Save.

### R3 — Request and Result Template ownership matches new Tools

External and Shopify input schema is edited only in Request. `responseTemplate` is edited only in Result Template. Result Template bindings use the same production-envelope result contract rules as C078.

### R4 — persisted Review derives Agent Contract and preserves revision operations

Review shows the same separate read-only cards as C078, including derived Agent Contract (`definitionVersion`, `description`, `inputSchema`) and Result Template.

Persisted Review retains the existing supported actions/authorization:

```text
Cancel unsaved changes
Save draft
Validate (where currently supported)
Publish controls for SUPER_ADMIN where currently supported
```

`Cancel unsaved changes` must restore the current selected revision's last saved definition and editor buffers, clear transient validation/Test state, set dirty false, and stay on the same revision route. It must not create another revision and must not call a mutation Server Action.

### R5 — Save remains one CAS update

`Save draft` must assemble the complete current candidate and call the existing `updateToolDraft` exactly once with the selected revision id and current `expectedEditVersion`. Successful Save replaces local buffers with the canonical returned revision and current editVersion. A CAS conflict remains visible and must not silently overwrite.

### R6 — Explore Shopify remains exact-session safe

For persisted Shopify DRAFTs, Request -> Explore -> Use in tool -> Request must preserve `toolId`, `toolRevisionId`, tab/editor buffers and the existing sessionStorage identity checks. Returning from Explore must not auto-save.


### R7 — persisted DRAFTs own the same provider-neutral Test freshness checkpoint semantics

COMMERCE-081 and COMMERCE-083 consume C079 as the persisted-DRAFT authoring-session/persistence boundary. C079 must therefore establish the persisted equivalent of the C078 provider-neutral Test freshness checkpoint before either downstream Test-integration task executes.

Do not add provider execution in C079. C080 and C082 remain the canonical External HTTP and Shopify Admin Test backends.

For persisted `EXTERNAL_HTTP` and `SHOPIFY_ADMIN_GRAPHQL` DRAFT authoring, maintain one common checkpoint state with semantics equivalent to the accepted C078 contract:

```ts
type AuthoringTestStatus =
  | "NOT_RUN"
  | "RUNNING"
  | "PASSED"
  | "FAILED"
  | "STALE";

type AuthoringTestSnapshot = {
  toolDefinitionRevision: number;
  requestRevision: number;
  responseRevision: number;
  resultTemplateRevision: number;
};

type AuthoringTestState = {
  status: AuthoringTestStatus;
  testedSnapshot: AuthoringTestSnapshot | null;
};
```

The persisted authoring model must expose semantic operations equivalent to:

```text
currentAuthoringSnapshot(...)
isCurrentTestPassed(...)
mark Test RUNNING for an exact submitted snapshot
mark Test PASSED for that submitted snapshot
mark Test FAILED for that submitted snapshot
mark Test STALE and clear testedSnapshot
```

Reuse/extract the accepted C078 provider-neutral helpers where practical; do not create a competing Test-result authority.

Persisted authoring must keep **persistence dirtiness** distinct from **Test freshness**:

- changing Tool Definition, Request, Response or Result Template is a persisted authoring mutation, advances the corresponding freshness revision and sets persistence-dirty;
- changing only the selected tab must not change persistence dirtiness or Test freshness;
- provider-specific Test arguments, selected shop, Test output or diagnostic state are transient and must not become persisted Tool definition state or persistence-dirty;
- C081/C083 may stale the common checkpoint for Test-only argument/shop changes without making the persisted DRAFT dirty;
- Cancel unsaved changes restores the saved candidate, clears transient Test/validation state and returns the common Test checkpoint to `NOT_RUN` / `testedSnapshot: null`;
- a stale in-flight completion must never mark the current persisted candidate PASSED.

C079 establishes this common persisted-session state only. C081/C083 remain responsible for invoking C080/C082 and for provider-specific safe Test diagnostics/presentation.


## Work Items

- [x] Apply the six-step shared flow to persisted External HTTP DRAFTs.
- [x] Apply the six-step shared flow to persisted Shopify Admin DRAFTs.
- [x] Add persisted Tool Definition read-only/editable field split.
- [x] Move External persisted input schema to Request.
- [x] Integrate persisted ResultTemplateTab with production-envelope contracts.
- [x] Remove persisted Agent Contract authoring tab/use.
- [x] Derive read-only Agent Contract in Review.
- [x] Add `Cancel unsaved changes` reset semantics.
- [x] Preserve one-CAS Save and canonical refresh/editVersion update.
- [x] Preserve persisted Shopify Explore handoff without auto-save.
- [x] Add persisted-provider regression coverage.
- [x] Remove the unreachable legacy External persisted-DRAFT authoring branch after the six-step C079 branch.
- [x] Keep all persisted Shopify Save/Validate/Publish/Cancel actions owned by Review; remove duplicate Save/Publish controls from non-Review tabs.
- [x] Add the persisted provider-neutral validation/Test freshness checkpoint required by C081/C083, separate from persistence dirtiness.

## Interfaces / Contracts

Consumes C078's shared UI ownership model and existing persisted lifecycle actions:

```text
updateToolDraft
publishToolRevision
validateExternalToolDefinitionAction
ToolAuthoringSession(mode="existing")
```

No new database or cross-repository contract.

## Dependencies

- ARCH-021-COMMERCE-078

## Enables

- ARCH-021-COMMERCE-081
- ARCH-021-COMMERCE-083
- ARCH-021-SYSTEM-TEST-002

## Acceptance Criteria

- [x] Persisted External and Shopify DRAFTs expose the same six-step sequence as new Tools.
- [x] MCP name/provider kind are visibly read-only in Tool Definition.
- [x] Input schema is owned by Request; Result Template owns `responseTemplate`.
- [x] Agent Contract is review-only and contains no Result Template content.
- [x] Cancel restores the exact saved revision locally with zero mutation call.
- [x] Save performs exactly one `updateToolDraft` CAS write using current editVersion.
- [x] CAS conflicts remain visible and do not overwrite newer state.
- [x] Save/Publish authorization and current publication gates are unchanged.
- [x] Persisted Shopify Explore return remains session-isolated and non-durable until Save.
- [x] Persisted External and Shopify have exactly one active authoring implementation path each; no unreachable legacy External DRAFT editor remains.
- [x] Persisted Shopify durable Save/Validate/Publish/Cancel controls appear only in Review.
- [x] Persisted DRAFT authoring exposes the common four-revision Test freshness checkpoint required by C081/C083.
- [x] Authored-section mutations stale/advance the common checkpoint and set persistence-dirty; Test-only transient state never sets persistence-dirty.
- [x] Cancel restores the saved candidate and resets common Test state to `NOT_RUN` with `testedSnapshot: null`.

## Validation

- [x] `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx`
- [x] focused CAS Save and Cancel-zero-write regressions
- [x] focused persisted Explore round-trip regression
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [x] `git diff --check`
- [x] focused regression proving no duplicate legacy External persisted editor path remains
- [x] focused regression proving Shopify durable Save/Publish/Cancel controls are Review-owned only, while non-mutating Request validation remains available
- [x] focused persisted common-Test-state regressions covering initial state, four authored revisions, stale mismatch and Cancel reset without provider execution

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Do not merge Tool-level metadata updates into revision Save. The task is about authoring ownership parity, not redefining the Tool/ToolRevision data model.

## Completion Report

### Status

Completed for Architect Review (Attempt 1)

### Files Changed

`src/studio/tools/authoring/review-tab.tsx`
`src/studio/tools/authoring/tool-authoring-tabs.tsx`
`src/studio/tools/authoring/tool-definition-tab.tsx`
`src/studio/tools/tool-editor.tsx`
`tests/external-tools-ui.test.tsx`
`tests/shopify-admin-tools-ui.test.tsx`

### Work Completed

Aligned persisted External HTTP and Shopify Admin DRAFT authoring with the six-step Tool Definition, Request, Response, Result Template, Test and Review flow. Identity and provider fields remain read-only; description/version edits, input-schema ownership, production-envelope Result Template contracts and separate review cards now follow C078 ownership. Cancel restores the selected saved revision and local buffers without a mutation. Save remains a single revision-scoped CAS update, uses the current edit version, and adopts the canonical returned revision; conflicts retain the local candidate. Shopify Explore preserves the existing revision/session identity and editor buffers without auto-saving.

### Validation Results

`npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx`: passed, 3 test files and 136 tests.
Targeted ESLint over the six changed files: passed.
Changed-file editor diagnostics: no errors.
`git diff --check`: passed.
Regression coverage includes six-tab order/field ownership, zero-write Cancel, one-call CAS Save with canonical refresh, visible CAS conflicts, and Shopify Explore buffer round-trip without mutation.

### Deviations

No implementation deviations. A repeat Vitest invocation through `pnpm exec` attempted dependency setup and was blocked by pnpm's ignored-build-script policy (`ERR_PNPM_IGNORED_BUILDS`); the focused suites had already passed using the successful `npx vitest` invocation above.

### Assumptions

Validation used the focused UI suites and changed-file diagnostics; a full repository typecheck was not run. Shopify Explore return behavior is covered with the existing persisted-session fixture and verifies the relevant identity, buffers and absence of writes.

### Unresolved Issues

No unresolved implementation issues identified. Full repository typecheck remains unrun.

### Architectural Concerns

None identified; Architect Review remains pending.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is accepted.

All three Attempt 1 correction items are satisfied.

1. **One persisted External DRAFT implementation path**
   - The duplicate/unreachable pre-C079 `EXTERNAL_HTTP` DRAFT branch is removed.
   - `tool-editor.tsx` now contains one supported External persisted-DRAFT branch.
   - The remaining generic fallback editor applies only outside the supported External/Shopify C079 flow and remains within the task's explicit non-goal boundary.
   - The focused source-level regression asserts that only one `EXTERNAL_HTTP` DRAFT branch exists.

2. **Shopify durable actions are Review-owned**
   - Tool Definition, Request, Response, Result Template and Test expose no persisted Save/Publish/Cancel actions.
   - Review owns `Cancel unsaved changes`, `Save draft`, Validate and the existing role-authorized publication action.
   - Request retains its non-mutating GraphQL validation action, which is not a persistence operation.
   - The submitted SUPER_ADMIN regression verifies publication controls appear only in Review.

3. **Persisted common Test freshness/checkpoint state**
   - Persisted External and Shopify DRAFTs reuse the accepted C078 provider-neutral authoring Test model rather than defining a competing provider-specific checkpoint.
   - The state carries the four Tool Definition/Request/Response/Result Template revisions plus `NOT_RUN | RUNNING | PASSED | FAILED | STALE`.
   - Authored-section changes advance/stale the relevant checkpoint independently of the existing persistence-dirty flag.
   - Changing only the selected tab or External Test arguments does not advance authored revisions.
   - Cancel restores the selected saved revision and resets the common checkpoint to `NOT_RUN` with all four revisions at zero.
   - Successful CAS Save adopts the canonical returned revision and restores the checkpoint from that saved definition.
   - No C080/C082 backend, provider transport or additional Test result contract was implemented by C079.

The persisted six-tab composition remains:

```text
Tool Definition -> Request -> Response -> Result Template -> Test -> Review
```

MCP name, display name and provider kind remain read-only in persisted Tool Definition; description and definition version remain revision-owned edits. External/Shopify input schema remains Request-owned, Result Template remains separately owned, Agent Contract remains derived/read-only in Review, CAS Save remains one revision-scoped update, and Shopify Explore remains exact-session/non-durable until Save.

The submitted task metadata still carries `executor: copilot` and a non-null `claimed_at` despite the review handoff reporting a cleared claim. This acceptance overlay normalizes both fields to `null`; it is not an implementation defect.

### Reviewed Files

- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/new-tool-authoring-state.ts`
- `src/studio/tools/authoring/review-tab.tsx`
- `src/studio/tools/authoring/tool-authoring-tabs.tsx`
- `src/studio/tools/authoring/tool-definition-tab.tsx`
- `tests/external-tools-ui.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/new-tool-authoring-state.test.ts`
- C079 Completion Report — Attempt 2
- C081/C083 downstream task contracts

### Validation Reviewed

- Submitted focused Attempt 2 packet: 4 files, 160 tests passed.
- Submitted final Shopify-focused rerun: 25/25 passed.
- Submitted targeted ESLint: passed.
- Submitted `git diff --check`: passed.
- Repository typecheck remains non-green with 261 diagnostics across 27 files. The two diagnostics in `tool-editor.tsx` are the pre-existing Result Template prop diagnostics recorded by the implementing agent and are not introduced by the Attempt 2 correction set.
- Review snapshot has no installed `node_modules`, so the submitted Vitest/ESLint commands were inspected rather than independently rerun.
- Direct source inspection confirms the duplicate External branch is removed, Shopify persistence actions are Review-owned, and the common checkpoint module contains no provider request/Test Server Action dependency.

### Architecture Conformance

Conforms.

C079 now provides persisted-DRAFT parity with the C078 ownership model while preserving persisted lifecycle semantics: immutable Tool identity/provider kind, one CAS Save, explicit Cancel reset, existing validation/publication gates, exact-session Shopify Explore, and one provider-neutral Test freshness checkpoint separate from persistence dirtiness.

### Follow-up

C079 is Complete / Accepted — Attempt 2.

COMMERCE-081 becomes Ready because C078, C079 and C080 are Complete.

COMMERCE-083 remains Pending because COMMERCE-081 is still incomplete, even though C078, C079 and C082 are Complete.

ARCH-021-SYSTEM-TEST-002 remains Pending until C079, C081 and C083 are all Complete.
