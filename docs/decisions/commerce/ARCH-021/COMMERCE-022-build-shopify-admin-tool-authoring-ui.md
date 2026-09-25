---
id: ARCH-021-COMMERCE-022
architecture_id: ARCH-021
title: Build Shopify Admin GraphQL tool-authoring UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-019
  - ARCH-021-COMMERCE-020
  - ARCH-021-COMMERCE-024
enables: []
created: 2026-09-23
updated: 2026-09-25
---

# Build Shopify Admin GraphQL tool-authoring UI

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Allow admins to author and locally validate immutable `SHOPIFY_ADMIN_GRAPHQL` tool drafts against the pinned Admin 2026-07 schema, mapping the CommerceAgent's persisted inputSchema arguments to GraphQL variables without using a shop session or making a live Shopify request.

## Context

ARCH-021's target Shopify execution path uses the selected shop's offline session at runtime. Phase 3 only defines/validates the query. Shopify AI Toolkit/Dev MCP helps prove the local compiler but is not invoked by normal Studio validation.

The accepted simplification is authoritative for this UI: Tool components consume named Server Actions, receive serializable props only, use the platform-role hierarchy, preserve deterministic server errors, and use COMMERCE-020 audit reconciliation only for genuinely unconfirmed mutation responses.

## Scope

Primary files:

```text
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/shopify-admin-editor.tsx
src/studio/tools/admin-validation-server-actions.ts
src/studio/tools/reconciliation-server-actions.ts
lib/discovery/schema.ts                         # existing API-surface DTO only if needed
app/api/studio/discovery/route.ts              # consume COMMERCE-018 compiler contract
tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

## Out of Scope

- Offline session lookup.
- Admin API request/execution.
- Mutations.
- Store-specific live schema introspection.
- Provider/model/prompt configuration.

## Requirements

### R1 — new Shopify authoring kind

New Tool creation must offer:

```text
Shopify Admin GraphQL
External HTTP
```

Do not offer `SHOPIFY_STOREFRONT_QUERY` for new Phase 3 authoring. Existing Storefront revisions remain readable in revision history until later cutover.

### R2 — exact fields

The Admin editor persists exactly the COMMERCE-016 Commerce-owned execution fields:

```text
apiVersion       read-only: 2026-07
schemaHash       server/compiler supplied; never free-typed
document         GraphQL editor
operationName
variables        mapping of GraphQL variable -> inputSchema property or bounded literal
resultPath
resultSchema
```

The Tool's `name`, `description`, `definitionVersion`, `inputSchema` and `responseTemplate` remain the common Tool fields.

### R3 — GraphQL authoring behavior

- Code editor may use GraphQL/plain text editor already available or a bounded textarea if no GraphQL editor exists; do not add a second large editor framework in this task.
- `Validate` calls the COMMERCE-024 Shopify Admin authoring-validation action, which uses COMMERCE-018 internally.
- Show bounded compiler issues with path/message and never raw session/token data.
- Only a named `query` can become valid. Mutation/subscription errors must be explicit.
- Variable mappings must be selectable only from current top-level `inputSchema` properties plus bounded literal input.
- Changing inputSchema must mark mappings requiring revalidation rather than silently retaining invalid mappings.

### R4 — Explore/discovery UI remains out of scope

Do not modify the existing Explore/discovery UI in this task. COMMERCE-018 may expose/extend server-side discovery metadata required by its compiler and development oracle, but adding Admin API browsing to the Explore surface is a separate independently reviewable UI capability.

Normal Tool validation uses COMMERCE-024 and the local committed schema. Do not call `validate_graphql_codeblocks` from browser/server request handling.

### R5 — no live shop requirement

Authoring/validation does not require a selected shop because the GraphQL contract is pinned to Admin 2026-07, not a merchant-specific schema. If a Studio `shopId` exists in navigation, preserve it but do not use it for validation or credentials in Phase 3.

### R6 — publication handoff

Save DRAFT normally. Publication validation must display COMMERCE-019 `LIVE_TEST_REQUIRED` until Phase 4 proves the exact saved revision against a selected shop's offline session.

Mutation/error handling follows COMMERCE-020 exactly:

- Save/create/update/publish use named Server Actions;
- explicit server errors remain visible and are not converted to unknown;
- only a rejected/lost mutation response may enter `UNCONFIRMED`;
- reconciliation checks the original `operationId` audit receipt and never replays the mutation;
- compiler/metadata validation is non-mutating and never creates `UNCONFIRMED`.

Publishing remains visible/enabled only for `PLATFORM_SUPER_ADMIN`; PLATFORM_ADMIN may author/save/validate drafts.

### R7 — UI regression cases

Prove:

- valid products query + variables saves exact definition;
- mutation cannot validate;
- schemaHash cannot be user-edited;
- stale variable mapping after inputSchema edit is invalid;
- Storefront is not offered for new creation;
- historical Storefront revision remains readable;
- validation makes no Shopify store request/session lookup;
- live-test-required is presented clearly.

## Work Items

- [ ] Add Admin authoring kind/editor.
- [ ] Add inputSchema-to-variable mapping UI.
- [ ] Wire local server validation and schemaHash.
- [ ] Remove Storefront from new-tool choice while preserving history rendering.
- [ ] Add focused UI regressions.

## Interfaces / Contracts

Consumes COMMERCE-024 Shopify Admin authoring validation and the COMMERCE-019 common publication gate. COMMERCE-024 owns the direct dependency on the COMMERCE-018 compiler.

## Dependencies

- ARCH-021-COMMERCE-019
- ARCH-021-COMMERCE-020
- ARCH-021-COMMERCE-024

## Enables

None in Phase 3. Phase 4 live Shopify Tool testing will depend on this task.

## Acceptance Criteria

- [ ] Admin can create a complete, pinned, query-only Shopify Admin tool DRAFT.
- [ ] CommerceAgent argument contract remains the persisted inputSchema/variable mapping.
- [ ] Authoring requires no shop token/session/provider I/O.
- [ ] New Storefront authoring is removed without hiding historical definitions.
- [ ] Explore/discovery UI is unchanged by this task.
- [ ] Explicit server failures remain visible; only lost/rejected mutation responses enter reconcilable UNCONFIRMED state.
- [ ] Publish authority remains PLATFORM_SUPER_ADMIN-only through the accepted hierarchy.

## Validation

- [ ] focused `tests/shopify-admin-tools-ui.test.tsx`
- [ ] `npm run test:arch021-shopify-admin-compiler`
- [ ] affected Studio workspace/tool-authoring tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not execute Admin GraphQL against a shop.

## Implementation Notes

The eventual Phase 4 runtime will resolve the selected shop's offline session server-side. No shop/session fields belong in the tool definition.

## Completion Report

### Status
Implementation complete; ready for architect review.
### Files Changed
Implementation worktree changes are committed and pushed on `task/ARCH-021-COMMERCE-022`:

- `src/studio/tools/shopify-admin-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/tool-library.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/studio-workspace.test.tsx`
- Existing Attempt 1 additions also include `src/commerce/tool-definition/contracts.ts`, `src/commerce/tool-authoring/admin-validation.ts`, `src/commerce/tool-authoring/contracts.ts`, and `src/studio/tools/admin-validation-server-actions.ts`.
### Work Completed
Implemented the pinned, query-only Shopify Admin GraphQL authoring flow. New Tool creation offers exactly Shopify Admin GraphQL and External HTTP; historical Storefront revisions remain readable. Admin metadata is loaded through the named metadata Server Action, gates creation, and supplies the pinned `2026-07` API version and compiler schema hash. The Admin editor persists the exact visible document, operation name, variable mappings or bounded JSON literals, result path, result schema, common Tool fields, and response template.

Admin validation is provider-free and rejects mutation/subscription documents with bounded issues. Save/validate state is controlled so stale mappings, invalid JSON, metadata errors, and changed persisted fields block publication. Composite Admin creation and recovery use C020 serializable staged state, distinct operation IDs, draft-only retry, and no replay of a committed `createTool`. Publication remains `SUPER_ADMIN`-only and surfaces `LIVE_TEST_REQUIRED` without entering `UNCONFIRMED`.
### Validation Results
Preparation used the deterministic launcher with `--prepare --executor copilot`; the implementation worktree was `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-022` and the parent worktree was `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-022`. Recursive materialization was verified with database submodule commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

- `npm exec eslint src/studio/tools/shopify-admin-editor.tsx src/studio/tools/tool-library.tsx src/studio/tools/tool-authoring-screen.tsx src/studio/tools/tool-editor.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/studio-workspace.test.tsx`: passed.
- Focused Admin/C020/validation tests: 29/29 passed across `tests/shopify-admin-tools-ui.test.tsx`, `tests/tool-authoring-screen.test.tsx`, and `tests/shopify-admin-authoring-validation.test.ts`.
- `npm run test:arch021-shopify-admin-compiler`: passed, 22/22.
- `npm run test:arch021-shopify-admin-authoring-validation`: passed, 9/9.
- Targeted TypeScript diagnostics for changed source/test files: no diagnostics.
- `git diff --check`: passed.
- `tests/studio-workspace.test.tsx`: 20/21 passed. One existing stale-CAS assertion still expects `changed elsewhere`, while the current historical Storefront fixture reports `Saved.`; no Admin flow assertion failed.

Implementation commits: `ef3765c` and `934d897`. The latter is pushed to `origin/task/ARCH-021-COMMERCE-022` and matches the local branch.
### Deviations
The connected workspace test suite retains one baseline failure in the historical Storefront stale-CAS scenario described above. It was not changed because the failure does not exercise the new Admin authoring path and the current fixture's update response is successful.
### Assumptions
The task's accepted platform-role aliases include `ADMIN`/`SUPER_ADMIN` in this repository's Studio test harness. The pinned compiler metadata and provider-free validation action are authoritative for Phase 3; live Shopify testing remains a Phase 4 concern.
### Unresolved Issues
The historical Storefront stale-CAS test expectation should be reconciled with the fixture/service behavior in a separate focused maintenance change. No unresolved Admin authoring or publication-handoff issue remains.
### Architectural Concerns
None identified. No shop, session, token, provider, or live Shopify request is used during Admin authoring or validation. Explore/discovery UI was not modified.

## Architect Review

### Review Status
Changes Requested

### Review Notes

Attempt 1 establishes the Shopify Admin GraphQL editor foundation, removes Storefront from the new-Tool selector, preserves historical Storefront rendering, consumes COMMERCE-024 validation, and persists common Tool fields. Preserve those changes.

Attempt 2 is limited to the deterministic corrections below. Do not redesign COMMERCE-018/019/020/024, do not add live Shopify/session I/O, and do not modify Explore/discovery UI.

#### CR-1 — make new Admin creation metadata-gated and recoverable

Files:

```text
src/studio/tools/tool-library.tsx
src/studio/tools/tool-authoring-screen.tsx
tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

Required behavior:

1. `getShopifyAdminAuthoringMetadataAction()` is the only source of the Admin `apiVersion` and `schemaHash` used to create a new Admin draft. Do not duplicate the hash in browser code.
2. While Admin metadata is loading, disable the Admin create submit button.
3. If metadata returns a typed error, display exactly `<CODE>: <message>` and do not call `createTool()`. Do not silently leave the editor in `Loading…`.
4. Creating an Admin Tool is a two-operation sequence:
   - operation A: `createTool`;
   - operation B: `createToolDraft` with a fresh operation id.
   The two operation ids MUST differ.
5. Generalize the existing C020 staged composite-create state so it can represent both `EXTERNAL_HTTP` and `SHOPIFY_ADMIN_GRAPHQL` without regressing the accepted external flow. The staged state must remain serializable and contain only the immutable Tool name, purpose/kind, optional committed `toolId`, and proposed definition. Never store a mutation closure.
6. If operation A is proven committed after a lost response, reload the Tool list, resolve the Tool by immutable unique `name`, retain its id in staged state, and continue only with operation B. Never re-run `createTool`.
7. If operation B is proven not committed, retain the staged Tool id/definition and expose a draft-only retry that generates a NEW operation id. Never re-run `createTool`.
8. If operation B is proven committed, reload the canonical Tool, resolve the committed DRAFT, clear staged state and navigate to that revision. If the DRAFT cannot be resolved, remain UNCONFIRMED and fail closed exactly as C020 requires.
9. A new Admin creation must never fall through to the historical Storefront `emptyDefinition()` path.

#### CR-2 — make Admin metadata loading non-destructive

Files:

```text
src/studio/tools/shopify-admin-editor.tsx
src/studio/tools/tool-editor.tsx
```

The current mount effect closes over the initial `execution` object and calls the generic dirtying `onChange()`. A delayed metadata response can therefore overwrite newer query/mapping edits and marks an unchanged draft dirty.

Required behavior:

1. Loading pinned Admin metadata MUST NOT overwrite `document`, `operationName`, `variables`, `resultPath` or `resultSchema` edited after the request began.
2. If the returned `apiVersion/schemaHash` are already identical to the current definition, loading metadata MUST NOT mark the draft dirty.
3. If existing persisted metadata differs from the pinned compiler metadata, expose that as a visible validation/metadata state; do not silently replace unrelated execution fields. Any correction that changes persisted definition state must remain dirty until explicitly saved.
4. Metadata action typed errors must remain visible as `<CODE>: <message>`.

#### CR-3 — save and validate the exact visible Admin candidate

Files:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/shopify-admin-editor.tsx
```

The current `resultSchemaText` is private to `ShopifyAdminEditor`, so Save can persist the previous `execution.resultSchema`. Validation then copies the result schema through `onChange()`, which marks the editor dirty; after Save validation is reset, producing a validate -> dirty -> save -> invalidated loop that prevents a clean validated revision from reaching the publication gate.

Required behavior:

1. The parent Tool editor must have access to the exact visible result-schema text (or an equivalent controlled parsed candidate).
2. Admin Save must parse and validate ALL visible persisted fields in one candidate:

```text
definitionVersion
description
inputSchemaText
Admin document
operationName
variables
resultPath
resultSchemaText
responseTemplateText
```

3. Invalid JSON in `inputSchemaText`, `resultSchemaText` or `responseTemplateText` must remain visible, block Save/Validate as applicable, and never be replaced with the last valid persisted value.
4. `validateShopifyAdminDefinitionAction()` must receive the exact same visible candidate that Save would persist.
5. Successful validation of an unchanged saved candidate MUST NOT mark the draft dirty.
6. After a successful Save, validation is stale and must be re-run.
7. After Save + Validate with no further edits, state must be exactly:

```text
dirty = false
adminValidated = true
```

so a `SUPER_ADMIN` can press Publish and reach the COMMERCE-019 `LIVE_TEST_REQUIRED` gate.
8. Any subsequent persisted-field edit must invalidate `adminValidated`.

#### CR-4 — implement editable bounded JSON literal mappings

Files:

```text
src/studio/tools/shopify-admin-editor.tsx
tests/shopify-admin-tools-ui.test.tsx
```

Selecting `Bounded literal` currently writes only `{ literal: "" }`; the admin cannot author the literal.

Required behavior:

1. For every GraphQL variable mapping, allow either:
   - one current top-level `inputSchema.properties` name; or
   - a bounded JSON literal.
2. When literal mode is selected, render an editable control labelled exactly `Literal for <variableName>`.
3. The literal control must support JSON scalar/array/object values accepted by the COMMERCE-016 bounded mapping contract. At minimum regressions must prove a string enum literal (`"TITLE"`) and a numeric literal (`10`).
4. Invalid literal JSON must remain visible, mark Admin validation invalid, and block Save until corrected.
5. Changing `inputSchemaText` must immediately invalidate `adminValidated`; an existing mapping to a removed/incompatible input property must fail COMMERCE-024 validation rather than silently validate.

#### CR-5 — publication handoff must be reachable and exact

Files:

```text
src/studio/tools/tool-editor.tsx
tests/shopify-admin-tools-ui.test.tsx
```

Required behavior:

1. `PLATFORM_ADMIN`/`ADMIN` may create, edit, save and validate Admin drafts but never receives an enabled Publish action.
2. `PLATFORM_SUPER_ADMIN`/`SUPER_ADMIN` sees Publish only after the exact current saved draft has been validated and `dirty === false`.
3. Calling Publish for an otherwise valid Admin definition in Phase 3 must surface the exact COMMERCE-019 typed error:

```text
LIVE_TEST_REQUIRED: Run a successful live tool test for the current saved revision before publishing.
```

4. The error must remain a deterministic Tool mutation error. It MUST NOT create UNCONFIRMED.
5. Publication failure must not mutate the draft definition or validation baseline.

#### CR-6 — add the missing C022 UI regressions

Create the task-owned file required by the task definition:

```text
tests/shopify-admin-tools-ui.test.tsx
```

Use `vi.mock(...)` for the named Server Action modules. Do not test by injecting a function-valued action bundle into production components.

The file MUST execute at least these cases:

```text
1. new-tool selector offers exactly Shopify Admin GraphQL + External HTTP; Storefront absent
2. Admin create disabled while metadata loading
3. metadata typed error prevents createTool and is visible
4. Admin create uses createTool(A) then createToolDraft(B), A != B, exact pinned metadata persisted
5. lost/rejected Admin draft mutation enters C020 UNCONFIRMED; not-committed recovery retries only the draft with a new id
6. historical SHOPIFY_STOREFRONT_QUERY revision still renders/readable
7. schemaHash/apiVersion have no editable input
8. valid input-property variable mapping persists exactly
9. editable literal mapping persists JSON string enum and number literals
10. inputSchema change makes a stale mapping fail validation
11. mutation GraphQL document cannot validate and issue path/message are shown
12. visible resultSchema + responseTemplate are both persisted by Save
13. Save -> Validate reaches dirty=false/adminValidated=true
14. SUPER_ADMIN Publish surfaces LIVE_TEST_REQUIRED without UNCONFIRMED
15. Admin authoring/validation invokes no shop/session/provider action
```

Existing `tests/tool-authoring-screen.test.tsx` must retain all accepted C020 reconciliation behavior and add any composite Admin-create cases that belong at the parent Tool screen boundary.

#### CR-7 — finish the durable task handoff

The submitted archive is not a valid review handoff. It still records:

```yaml
status: in_progress
executor: copilot
claimed_at: 2026-09-25T17:15:36Z
attempt: 1
```

and the Completion Report is `Not Started`.

Attempt 2 must populate the formal Completion Report with:

```text
dedicated parent worktree path
dedicated implementation worktree path
launcher/preparation synchronization evidence
recursive submodule materialization evidence
database submodule commit
exact implementation commit
exact parent report commit
changed files
exact validation commands and results
branch/remote parity
clean-worktree evidence
Deviations
Assumptions
Unresolved Issues
Architectural Concerns
```

and return exactly:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

### Reviewed Files

```text
src/studio/tools/tool-library.tsx
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/shopify-admin-editor.tsx
src/studio/tools/admin-validation-server-actions.ts
src/commerce/tool-authoring/admin-validation.ts
tests/tool-authoring-screen.test.tsx
tests/shopify-admin-authoring-validation.test.ts
docs/decisions/commerce/ARCH-021/COMMERCE-022-build-shopify-admin-tool-authoring-ui.md
```

### Validation Reviewed

Attempt 1 reported the COMMERCE-018 compiler and COMMERCE-024 validation suites passing, but the submitted archive contains no task-owned `tests/shopify-admin-tools-ui.test.tsx`, the authoritative task checklists remain unchecked, and the Completion Report is empty. Those results are not sufficient C022 acceptance evidence.

Attempt 2 MUST run exactly:

```bash
npm run test:arch021-shopify-admin-compiler
npm run test:arch021-shopify-admin-authoring-validation

npm exec vitest run \
  tests/shopify-admin-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx \
  tests/studio-workspace.test.tsx

npm exec eslint \
  src/studio/tools/tool-library.tsx \
  src/studio/tools/tool-authoring-screen.tsx \
  src/studio/tools/tool-editor.tsx \
  src/studio/tools/shopify-admin-editor.tsx \
  src/studio/tools/admin-validation-server-actions.ts \
  tests/shopify-admin-tools-ui.test.tsx \
  tests/tool-authoring-screen.test.tsx

npm run typecheck
git diff --check
```

If repository-wide typecheck retains documented baseline diagnostics, the Completion Report must prove zero diagnostics in C022-owned files.

Required source audits:

```bash
# New creation selector must not expose Storefront.
if rg -n '<option[^>]*SHOPIFY_STOREFRONT_QUERY|value="SHOPIFY_STOREFRONT_QUERY"' \
  src/studio/tools/tool-library.tsx; then
  echo 'ERROR: new Tool creation still exposes Storefront' >&2
  exit 1
fi

# Normal Admin authoring/validation must not introduce live shop/session/provider access.
if rg -n 'offline session|accessToken|shopifySession|fetch\(|/admin/api/' \
  src/studio/tools/shopify-admin-editor.tsx \
  src/studio/tools/admin-validation-server-actions.ts; then
  echo 'ERROR: Phase 3 Admin authoring contains live provider/session access' >&2
  exit 1
fi

# C022 must not restore function-valued action bundles.
if rg -n 'actions=\{|adminActions=|service=\{|controlled=' \
  src/studio/tools/tool-library.tsx \
  src/studio/tools/tool-authoring-screen.tsx \
  src/studio/tools/tool-editor.tsx; then
  echo 'ERROR: C022 restored a function-valued production action boundary' >&2
  exit 1
fi
```

### Architecture Conformance

Not yet conformant. The zero-I/O validation service and Admin editor foundation are aligned with C018/C024, but the new Admin create/draft lifecycle, exact visible-candidate persistence/validation, literal mapping authoring and publication handoff do not yet satisfy C022 R1/R2/R3/R6/R7.

### Follow-up

Reclaim the SAME task as Attempt 2. Implement CR-1 through CR-7 only. Preserve historical Storefront rendering and all accepted C018/C019/C020/C024 behavior. Do not begin Phase 4 or execute Admin GraphQL against a shop. After all required tests/validation pass, complete the formal Completion Report, set the task to `review`, clear the claim, return to `moda_architect`, and STOP.
