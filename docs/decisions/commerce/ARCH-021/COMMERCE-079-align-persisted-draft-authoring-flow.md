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
status: review
priority: 76
executor: copilot
claimed_at: 2026-09-28T17:46:51Z
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

\n### R7 — persisted DRAFTs own the same provider-neutral Test freshness checkpoint semantics\n\nCOMMERCE-081 and COMMERCE-083 consume C079 as the persisted-DRAFT authoring-session/persistence boundary. C079 must therefore establish the persisted equivalent of the C078 provider-neutral Test freshness checkpoint before either downstream Test-integration task executes.\n\nDo not add provider execution in C079. C080 and C082 remain the canonical External HTTP and Shopify Admin Test backends.\n\nFor persisted `EXTERNAL_HTTP` and `SHOPIFY_ADMIN_GRAPHQL` DRAFT authoring, maintain one common checkpoint state with semantics equivalent to the accepted C078 contract:\n\n```ts\ntype AuthoringTestStatus =\n  | "NOT_RUN"\n  | "RUNNING"\n  | "PASSED"\n  | "FAILED"\n  | "STALE";\n\ntype AuthoringTestSnapshot = {\n  toolDefinitionRevision: number;\n  requestRevision: number;\n  responseRevision: number;\n  resultTemplateRevision: number;\n};\n\ntype AuthoringTestState = {\n  status: AuthoringTestStatus;\n  testedSnapshot: AuthoringTestSnapshot | null;\n};\n```\n\nThe persisted authoring model must expose semantic operations equivalent to:\n\n```text\ncurrentAuthoringSnapshot(...)\nisCurrentTestPassed(...)\nmark Test RUNNING for an exact submitted snapshot\nmark Test PASSED for that submitted snapshot\nmark Test FAILED for that submitted snapshot\nmark Test STALE and clear testedSnapshot\n```\n\nReuse/extract the accepted C078 provider-neutral helpers where practical; do not create a competing Test-result authority.\n\nPersisted authoring must keep **persistence dirtiness** distinct from **Test freshness**:\n\n- changing Tool Definition, Request, Response or Result Template is a persisted authoring mutation, advances the corresponding freshness revision and sets persistence-dirty;\n- changing only the selected tab must not change persistence dirtiness or Test freshness;\n- provider-specific Test arguments, selected shop, Test output or diagnostic state are transient and must not become persisted Tool definition state or persistence-dirty;\n- C081/C083 may stale the common checkpoint for Test-only argument/shop changes without making the persisted DRAFT dirty;\n- Cancel unsaved changes restores the saved candidate, clears transient Test/validation state and returns the common Test checkpoint to `NOT_RUN` / `testedSnapshot: null`;\n- a stale in-flight completion must never mark the current persisted candidate PASSED.\n\nC079 establishes this common persisted-session state only. C081/C083 remain responsible for invoking C080/C082 and for provider-specific safe Test diagnostics/presentation.\n

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

Changes Requested

### Review Notes

Attempt 1 is not accepted.

Manual validation confirms that the persisted Shopify DRAFT **does** expose the required six tabs:

```text
Tool Definition -> Request -> Response -> Result Template -> Test -> Review
```

The earlier concern that C079 removed the tabs was based on the Tool Library screen and is withdrawn. The six-tab persisted composition itself is correct.

Three task/architecture corrections remain.

#### 1. Remove the unreachable duplicate External persisted-DRAFT implementation

`tool-editor.tsx` contains two consecutive branches with the same condition:

```ts
if (
  selected?.status === "DRAFT" &&
  definition.execution.kind === "EXTERNAL_HTTP"
) {
  // new C079 six-step persisted editor
  return ...
}

if (
  selected?.status === "DRAFT" &&
  definition.execution.kind === "EXTERNAL_HTTP"
) {
  // old pre-C079 persisted editor
  return ...
}
```

The second branch is unreachable, but it still contains the pre-C079 ownership model: inline Definition fields, inline Input JSON Schema, inline Response template, inline review facts and its own Save/Validate/Publish controls.

C079 exists specifically to replace that regressed persisted ownership model. Do not leave the old editor dormant behind an unreachable duplicate condition.

Attempt 2 must remove the obsolete External persisted-DRAFT branch and its now-unused code paths/imports while preserving the accepted six-step C079 branch.

Add a focused regression/source-level guard sufficient to prevent both persisted External authoring implementations from coexisting again.

#### 2. Shopify durable actions must be Review-owned only

The Shopify C079 path correctly renders `ReviewTab` with:

```text
Cancel unsaved changes
Save draft
Validate
Publish tool version
```

but it also renders another `Save draft` / `Publish tool version` button row whenever:

```ts
externalSection !== "review"
```

The submitted manual screenshot demonstrates this directly on the **Result Template** tab.

That violates C079 R4's Review ownership model and creates two persistence surfaces for the same candidate.

Attempt 2 must:

- remove the non-Review Shopify Save/Publish controls;
- keep persisted Save, Validate, Cancel and publication controls in Review;
- preserve the existing one-call CAS `updateToolDraft` implementation and authorization/publication gates;
- preserve navigation among all six tabs while the candidate is dirty.

Add regressions proving Request, Response, Result Template and Test expose no durable Save/Publish mutation controls, while Review exposes the correct role-authorized actions.

#### 3. Establish the persisted common Test freshness/session model required by C081/C083

C078 is already Complete and owns the provider-neutral new-Tool Test checkpoint over:

```text
Tool Definition revision
Request revision
Response revision
Result Template revision
```

The downstream accepted task contracts explicitly require C079 to provide the persisted-DRAFT equivalent:

- C081: “COMMERCE-079 applies the same session/persistence model to persisted DRAFT authoring.”
- C083: “Persisted-DRAFT Test freshness remains governed by the persisted authoring state model introduced by C079.”

The submitted C079 implementation still relies on provider-local booleans such as `externalValidated`, `adminValidated` and `adminResultContractFresh`; it does not establish one persisted provider-neutral `AuthoringTestState`/four-revision freshness checkpoint that C081/C083 can consume.

Attempt 2 must implement R7 added by this review:

- one persisted common four-revision freshness ledger;
- common `NOT_RUN/RUNNING/PASSED/FAILED/STALE` Test checkpoint semantics equivalent to C078;
- authored-section edits advance/stale the corresponding checkpoint and remain persistence-dirty;
- Test-only transient arguments/shop/result changes remain non-durable and must not create persistence dirtiness;
- Cancel restores the saved candidate and resets transient Test state to `NOT_RUN` / `testedSnapshot: null`;
- no C080/C082 provider Test execution is added here.

Reuse/extract the accepted C078 provider-neutral checkpoint helpers rather than creating a second incompatible Test authority.

### Reviewed Files

- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/authoring/tool-authoring-tabs.tsx`
- `src/studio/tools/authoring/tool-definition-tab.tsx`
- `src/studio/tools/authoring/review-tab.tsx`
- `src/studio/tools/authoring-session.ts`
- `src/studio/tools/new-tool-authoring-state.ts`
- `tests/external-tools-ui.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `docs/decisions/commerce/ARCH-021/COMMERCE-081-show-rendered-template-in-external-test.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-083-integrate-shopify-admin-test-tab.md`
- submitted manual screenshot of the persisted Shopify DRAFT Result Template tab

### Validation Reviewed

- Submitted C079 focused packet: 3 files, 136 tests passed.
- Submitted targeted ESLint: passed.
- Submitted changed-file diagnostics: clean.
- Submitted `git diff --check`: passed.
- Manual validation confirms the six-tab persisted Shopify flow.
- Source inspection confirms the unreachable duplicate External DRAFT branch and duplicate non-Review Shopify Save/Publish controls.
- Source/contract inspection confirms the persisted common Test checkpoint required by C081/C083 is not present.

### Architecture Conformance

Partial.

The six-step persisted External/Shopify ownership split, immutable/read-only Tool identity, Result Template ownership, CAS Save implementation, Cancel reset and Shopify Explore handoff are aligned.

Acceptance is blocked by:
1. retained duplicate legacy External persisted authoring code;
2. Shopify persistence actions outside Review; and
3. the missing persisted common Test freshness/session model required by downstream C081/C083.

### Follow-up

Return the same task as Attempt 2.

## Completion Report — Attempt 2

### Status

Ready for Architect Review. Task lifecycle status is `review`; Attempt 1's Changes Requested review is preserved above.

### Files Changed

- `moda-interact-commerce/src/studio/tools/new-tool-authoring-state.ts`
- `moda-interact-commerce/src/studio/tools/tool-editor.tsx`
- `moda-interact-commerce/tests/external-tools-ui.test.tsx`
- `moda-interact-commerce/tests/new-tool-authoring-state.test.ts`
- `moda-interact-commerce/tests/shopify-admin-tools-ui.test.tsx`

### Work Completed

- Removed the unreachable legacy External persisted-DRAFT editor and added a source-level regression asserting there is exactly one such branch.
- Kept Shopify durable Save, Cancel, Validate and Publish controls in Review. Request's existing non-mutating GraphQL validation remains available; Request, Response, Result Template, Test and Tool Definition expose no duplicate durable actions.
- Reused the C078 authoring state for the persisted four-revision Test checkpoint. Authored changes advance relevant revisions and stale/clear the checkpoint without conflating it with the existing persistence-dirty flag. Test-only arguments remain transient. Cancel and successful CAS Save restore checkpoint state from the canonical saved revision.
- Added regressions for each independent revision, stale/in-flight Test behavior, no provider execution, External Cancel/transient inputs, Shopify action ownership, and checkpoint reset.
- No C080/C082 provider Test execution or database changes were added.

### Validation Results

- `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts`: passed, 4 files and 160 tests.
- Final Shopify-focused rerun after extending Review-ownership coverage: passed, 1 file and 25 tests.
- Targeted ESLint over all five changed files: passed.
- `git diff --check`: passed.
- `npm run typecheck`: repository check remains blocked by existing TypeScript failures (261 diagnostics across 27 files). Two diagnostics point at the persisted `ResultTemplateTab` props in `tool-editor.tsx`; the same `definition.responseTemplate` typing existed at the corresponding two Result Template call sites in the task branch base. The new state tests introduce no remaining TypeScript diagnostics.

### Deviations and Remaining Validation

The full repository typecheck is not clean and was not repaired because its failures are outside this task; the pre-existing Result Template typing diagnostics are retained for architect review. No implementation acceptance item remains open.

### VCS and Worktree

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-079`, branch `task/ARCH-021-COMMERCE-079`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-079`, branch `task/ARCH-021-COMMERCE-079`.
- Both changesets are to be committed and pushed on their mirrored task branches. No `main` branch or submodule pointer is changed by this task.

Correct only the three items above, preserve the accepted C079 behavior, rerun the focused persisted authoring packet plus the new regressions, and STOP.

COMMERCE-081 and COMMERCE-083 remain dependency-gated until C079 is architect-accepted Complete.
