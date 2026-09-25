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
status: ready
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

Attempt 2 completes most of the C022 foundation and preserves the accepted C018/C019/C020/C024 boundaries. Preserve the current direct named Server Actions, pinned local compiler metadata, historical Storefront read-only rendering, serializable staged composite-create state, C020 audit-only reconciliation, and zero shop/session/provider I/O.

Attempt 3 is limited to the deterministic corrections below. Do not redesign the Admin compiler, publication gate, Tool mutation/reconciliation kernel, Explore UI or Phase 4 runtime.

#### CR-1 — use the metadata action as the only source of both Admin API identity fields

Files:

```text
src/studio/tools/tool-library.tsx
tests/shopify-admin-tools-ui.test.tsx
```

The submitted new-Tool flow stores only `schemaHash` from `getShopifyAdminAuthoringMetadataAction()` and still hard-codes:

```text
apiVersion = 2026-07
```

inside `adminDefinition()`.

Required behavior:

1. Store the successful metadata result as one bounded value containing BOTH:

```text
apiVersion
schemaHash
```

2. `adminDefinition()` MUST use exactly that returned `apiVersion` and `schemaHash`. Do not duplicate either value in browser code.
3. While metadata is loading, Admin creation remains disabled.
4. A typed metadata action error remains visible as exactly `<CODE>: <message>` and `createTool()` MUST NOT run.
5. If the metadata action Promise itself rejects, Admin creation remains disabled and show exactly:

```text
Admin authoring metadata is unavailable.
```

This non-mutating metadata failure MUST NOT create Tool `UNCONFIRMED` state.

Focused regression:

```text
metadata action returns apiVersion="2099-01", schemaHash="b...b"
→ created Admin proposedDefinition contains exactly apiVersion="2099-01"
→ schemaHash exactly equals returned hash
```

The test uses a deliberately non-default API version to prove there is no browser hard-code.

#### CR-2 — Save and Validate must build the same exact visible candidate

Files:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/shopify-admin-editor.tsx
tests/shopify-admin-tools-ui.test.tsx
```

The submitted Save path parses visible `responseTemplateText`, but the Admin `Validate` path currently validates `definition.responseTemplate`, which may be the previously persisted value. This violates CR-3 from Attempt 1.

Create one deterministic Admin candidate-building boundary. Save and Validate MUST consume the same candidate composed from the current visible values:

```text
definitionVersion
description
inputSchemaText
Admin execution.document
Admin execution.operationName
Admin execution.variables
Admin execution.resultPath
adminResultSchemaText
responseTemplateText
```

Required behavior:

1. Parse `inputSchemaText`, `adminResultSchemaText` and `responseTemplateText` for BOTH Save and Validate.
2. Invalid JSON in any of those three editors remains visible and blocks both Save and Validate from calling their Server Action.
3. `validateShopifyAdminDefinitionAction()` receives exactly the same `CommerceToolDefinition` that `updateToolDraft()` would persist at that instant.
4. Successful Validate of an unchanged saved candidate MUST NOT mark the editor dirty.
5. Successful Save sets `adminValidated=false` because validation evidence is stale after persistence.
6. Save followed by Validate with no later edit MUST end in exactly:

```text
dirty = false
adminValidated = true
```

7. Any later persisted-field edit sets `adminValidated=false`.

Required regression:

```text
edit visible response template
→ Validate
→ validation action receives the edited response template, not the old persisted template

edit visible result schema + response template
→ Save
→ updateToolDraft receives those exact visible values
```

#### CR-3 — literal validity is aggregate state; blank/invalid visible literals may never be silently persisted

Files:

```text
src/studio/tools/shopify-admin-editor.tsx
src/studio/tools/tool-editor.tsx
tests/shopify-admin-tools-ui.test.tsx
```

The submitted editor currently sets `{ literal: "" }` when `Bounded literal` is selected while leaving the parent validity flag potentially `true`. With multiple literal mappings, editing one valid literal can also set the shared boolean `true` while another literal remains invalid.

Required behavior:

1. Selecting `Bounded literal` creates visible literal text but the mapping is INVALID until that text parses as JSON.
2. Empty text is invalid JSON and MUST block Save and Validate.
3. Track validity across ALL currently visible literal mappings. Parent `adminMappingValid` is true only when every literal-mode mapping has valid JSON.
4. Editing one valid literal MUST NOT clear an invalid state from another literal mapping.
5. Invalid literal text remains visible; do not replace it with the last valid literal.
6. Save and Validate MUST NOT call their Server Actions while any literal is invalid.
7. Once all literals are valid, the exact parsed JSON values are included in the candidate.

Required regressions:

```text
select Bounded literal and leave blank
→ Save blocked
→ Validate blocked

$query literal = "TITLE"
$first literal = 10
→ both mappings persisted exactly

$query invalid
$first valid
→ overall mapping state remains invalid
```

#### CR-4 — make the required SUPER_ADMIN publication handoff executable

Files:

```text
src/studio/tools/tool-editor.tsx
tests/shopify-admin-tools-ui.test.tsx
```

The Attempt 2 tests only render the explanatory live-test paragraph. They do not prove the actual C019 publication handoff.

Required executable cases:

```text
ADMIN + saved/validated Admin draft
→ no enabled Publish action

SUPER_ADMIN + dirty=false + adminValidated=true
→ Publish enabled
→ click Publish
→ publishToolRevision returns LIVE_TEST_REQUIRED
→ UI shows exactly:
   LIVE_TEST_REQUIRED: Run a successful live tool test for the current saved revision before publishing.
→ Tool UNCONFIRMED is NOT created
→ draft definition/validation baseline remains unchanged
```

The test MUST reach `dirty=false/adminValidated=true` through the real Save -> Validate sequence, not by manually injecting validation state.

#### CR-5 — add Admin-specific composite create/recovery proof

Files:

```text
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-library.tsx
tests/tool-authoring-screen.test.tsx
tests/shopify-admin-tools-ui.test.tsx
```

The production staged state is correctly generalized to Admin/External, but the submitted tests mainly prove C020's generic/external recovery. Add explicit Admin cases.

Required cases:

```text
successful Admin create
→ createTool operationId A
→ createToolDraft operationId B
→ A != B
→ draft definition contains the exact metadata/candidate staged before createTool

Admin createTool(A) response lost
→ reconciliation committed
→ canonical Tool resolved by immutable name
→ createTool is never called again
→ only createToolDraft(B) may proceed

Admin createToolDraft(B) response lost
→ reconciliation not-committed
→ Retry draft remains staged
→ retry generates NEW operationId C
→ createTool call count remains exactly 1

Admin createToolDraft(B) response lost
→ reconciliation committed
→ canonical DRAFT resolved
→ staged state cleared
→ navigate to canonical revision
→ createToolDraft call count remains exactly 1
```

No staged state may contain a function/mutation closure.

#### CR-6 — complete the C022-owned UI regression contract

File:

```text
tests/shopify-admin-tools-ui.test.tsx
```

The file exists in Attempt 2, but only six tests are present. Expand it so the required C022 behavior is explicitly executable rather than inferred from other suites.

At minimum the final file MUST prove all of these observable cases:

```text
1. selector offers Admin GraphQL + External HTTP; Storefront absent
2. Admin create disabled while metadata loads
3. metadata typed error prevents createTool
4. metadata apiVersion + schemaHash are the exact create-definition values
5. historical Storefront revision remains readable
6. apiVersion/schemaHash have no editable input
7. input-property mapping persists exactly
8. string and numeric JSON literals persist exactly
9. blank/invalid literal blocks Save/Validate
10. inputSchema change causes stale mapping validation failure
11. mutation GraphQL cannot validate and bounded issue is visible
12. visible resultSchema + responseTemplate are both used by Save
13. visible responseTemplate is also used by Validate
14. Save -> Validate yields clean validated publication state
15. ADMIN cannot publish
16. SUPER_ADMIN Publish returns LIVE_TEST_REQUIRED without UNCONFIRMED
17. normal authoring/validation performs no shop/session/provider operation
```

Cases may share setup, but each assertion must execute the production component path with named Server Action mocks. Do not restore function-valued action bundles.

#### CR-7 — reconcile executor-owned task state before review

The Completion Report is populated, but the Work Items, Acceptance Criteria and Validation checklists at the top of the task are still unchecked. Those sections belong to the implementing agent.

Before returning Attempt 3 to Architect Review:

1. Check every Work Item actually completed.
2. Check every Acceptance Criterion actually satisfied.
3. Check every required Validation item actually run.
4. Update the Completion Report with the final Attempt 3 implementation commit and final parent report commit.
5. Record exact focused test counts, exact lint/typecheck outcome, branch/remote parity and clean worktree evidence.
6. Return exactly:

```yaml
status: review
attempt: 3
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
tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
tests/studio-workspace.test.tsx
docs/decisions/commerce/ARCH-021/COMMERCE-022-build-shopify-admin-tool-authoring-ui.md
```

### Validation Reviewed

Attempt 2 reports and the submitted snapshot support:

```text
Admin/C020/validation focused packet: 29/29 passed
COMMERCE-018 compiler:                22/22 passed
COMMERCE-024 authoring validation:     9/9 passed
targeted lint/diff checks:             passed
```

Those results support the retained foundation, but they do not prove CR-1 through CR-6 above. The current C022-owned UI file contains only six tests and does not execute the required Save->Validate->Publish handoff or exact visible-candidate validation contract.

Attempt 3 MUST run exactly:

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

If repository-wide typecheck retains baseline diagnostics, the Completion Report MUST prove zero diagnostics in these C022-owned source/test files.

Required source audits:

```bash
# New creation selector must not expose Storefront.
if rg -n '<option[^>]*SHOPIFY_STOREFRONT_QUERY|value="SHOPIFY_STOREFRONT_QUERY"' \
  src/studio/tools/tool-library.tsx; then
  echo 'ERROR: new Tool creation still exposes Storefront' >&2
  exit 1
fi

# Normal Admin authoring/validation must not introduce live shop/session/provider access.
if rg -n 'offline session|accessToken|shopifySession|/admin/api/' \
  src/studio/tools/shopify-admin-editor.tsx \
  src/studio/tools/admin-validation-server-actions.ts; then
  echo 'ERROR: Phase 3 Admin authoring contains live provider/session access' >&2
  exit 1
fi

# C022 must not restore function-valued production action bundles.
if rg -n 'actions=\{|adminActions=|service=\{|controlled=' \
  src/studio/tools/tool-library.tsx \
  src/studio/tools/tool-authoring-screen.tsx \
  src/studio/tools/tool-editor.tsx; then
  echo 'ERROR: C022 restored a function-valued production action boundary' >&2
  exit 1
fi
```

### Architecture Conformance

Not yet conformant. Attempt 2 establishes the correct Admin authoring foundation and preserves C018/C019/C020/C024 boundaries, but the browser still duplicates the pinned `apiVersion`, Validate does not yet use the exact visible response-template candidate, literal validity is not aggregated fail-closed, and the required publication/composite-recovery behavior is not yet executable in the C022 regression suite.

### Follow-up

Reclaim the SAME task as Attempt 3. Implement CR-1 through CR-7 only. Preserve all accepted Attempt 2 foundation work. Do not add live Shopify/session/provider I/O, do not modify Explore/discovery UI, and do not begin Phase 4. After all required validation passes, complete the executor-owned checklists and Completion Report, set the task to `review`, clear the claim, return to `moda_architect`, and STOP.
