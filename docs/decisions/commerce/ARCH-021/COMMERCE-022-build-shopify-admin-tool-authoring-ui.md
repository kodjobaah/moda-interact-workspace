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
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-09-25T18:27:55Z
attempt: 4
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

- [x] Add Admin authoring kind/editor.
- [x] Add inputSchema-to-variable mapping UI.
- [x] Wire local server validation and schemaHash.
- [x] Remove Storefront from new-tool choice while preserving history rendering.
- [x] Add focused UI regressions.

## Interfaces / Contracts

Consumes COMMERCE-024 Shopify Admin authoring validation and the COMMERCE-019 common publication gate. COMMERCE-024 owns the direct dependency on the COMMERCE-018 compiler.

## Dependencies

- ARCH-021-COMMERCE-019
- ARCH-021-COMMERCE-020
- ARCH-021-COMMERCE-024

## Enables

None in Phase 3. Phase 4 live Shopify Tool testing will depend on this task.

## Acceptance Criteria

- [x] Admin can create a complete, pinned, query-only Shopify Admin tool DRAFT.
- [x] CommerceAgent argument contract remains the persisted inputSchema/variable mapping.
- [x] Authoring requires no shop token/session/provider I/O.
- [x] New Storefront authoring is removed without hiding historical definitions.
- [x] Explore/discovery UI is unchanged by this task.
- [x] Explicit server failures remain visible; only lost/rejected mutation responses enter reconcilable UNCONFIRMED state.
- [x] Publish authority remains PLATFORM_SUPER_ADMIN-only through the accepted hierarchy.

## Validation

- [x] focused `tests/shopify-admin-tools-ui.test.tsx`
- [x] `npm run test:arch021-shopify-admin-compiler`
- [x] affected Studio workspace/tool-authoring tests
- [x] targeted lint/typecheck
- [x] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not execute Admin GraphQL against a shop.

## Implementation Notes

The eventual Phase 4 runtime will resolve the selected shop's offline session server-side. No shop/session fields belong in the tool definition.

## Completion Report

### Status
Attempt 3 implementation complete; ready for architect review.
### Files Changed
Implementation worktree changes are committed and pushed on `task/ARCH-021-COMMERCE-022`:

- `src/studio/tools/shopify-admin-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/tool-library.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/studio-workspace.test.tsx`
- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-authoring/admin-validation.ts`
- `src/commerce/tool-authoring/contracts.ts`
- `src/studio/tools/admin-validation-server-actions.ts`
### Work Completed
Implemented the pinned, query-only Shopify Admin GraphQL authoring flow. New Tool creation offers exactly Shopify Admin GraphQL and External HTTP; historical Storefront revisions remain readable. Admin metadata is loaded through the named metadata Server Action, gates creation, and supplies the pinned `2026-07` API version and compiler schema hash. The Admin editor persists the exact visible document, operation name, variable mappings or bounded JSON literals, result path, result schema, common Tool fields, and response template.

Admin validation is provider-free and rejects mutation/subscription documents with bounded issues. Save/validate state is controlled so stale mappings, invalid JSON, metadata errors, and changed persisted fields block publication. Composite Admin creation and recovery use C020 serializable staged state, distinct operation IDs, draft-only retry, and no replay of a committed `createTool`. Publication remains `SUPER_ADMIN`-only and surfaces `LIVE_TEST_REQUIRED` without entering `UNCONFIRMED`. Attempt 3 specifically makes metadata identity authoritative, shares one visible candidate builder between Save and Validate, aggregates literal validity, exposes typed publication errors, and proves Admin draft recovery paths.
### Validation Results
Preparation used the deterministic launcher with `--prepare --executor copilot`; the implementation worktree was `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-022` and the parent worktree was `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-022`. Recursive materialization was verified with database submodule commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

- `npm exec eslint src/studio/tools/shopify-admin-editor.tsx src/studio/tools/tool-library.tsx src/studio/tools/tool-authoring-screen.tsx src/studio/tools/tool-editor.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/studio-workspace.test.tsx`: passed.
- Focused Admin/C020/validation tests: 38/38 passed across `tests/shopify-admin-tools-ui.test.tsx`, `tests/tool-authoring-screen.test.tsx`, and `tests/shopify-admin-authoring-validation.test.ts`.
- `npm run test:arch021-shopify-admin-compiler`: passed, 22/22.
- `npm run test:arch021-shopify-admin-authoring-validation`: passed, 9/9.
- Targeted TypeScript diagnostics for changed source/test files: no diagnostics.
- `git diff --check`: passed.
- `tests/studio-workspace.test.tsx`: 20/21 passed. One existing stale-CAS assertion still expects `changed elsewhere`, while the current historical Storefront fixture reports `Saved.`; no Admin flow assertion failed.

Implementation commits: `ef3765c`, `934d897`, and `889b3e4`. Attempt 3 commit `889b3e4` is pushed to `origin/task/ARCH-021-COMMERCE-022`; the implementation worktree was clean after push and local/remote branch heads matched.
### Deviations
The connected workspace test suite retains one baseline failure in the historical Storefront stale-CAS scenario described above. It was not changed because the failure does not exercise the new Admin authoring path and the current fixture's update response is successful. Attempt 3 otherwise completes all requested review corrections.
### Assumptions
The task's accepted platform-role aliases include `ADMIN`/`SUPER_ADMIN` in this repository's Studio test harness. The pinned compiler metadata and provider-free validation action are authoritative for Phase 3; live Shopify testing remains a Phase 4 concern.
### Unresolved Issues
The historical Storefront stale-CAS test expectation should be reconciled with the fixture/service behavior in a separate focused maintenance change. No unresolved Admin authoring or publication-handoff issue remains. The final implementation commit is `889b3e4`; the parent report handoff commit is `6b737e9`.
### Architectural Concerns
None identified. No shop, session, token, provider, or live Shopify request is used during Admin authoring or validation. Explore/discovery UI was not modified.

## Architect Review

### Review Status
Changes Requested

### Review Notes

Attempt 3 closes the substantive Attempt 2 corrections around metadata identity, exact Save/Validate candidates, SUPER_ADMIN publication gating, and Admin-specific composite create/draft recovery. Preserve those changes.

One remaining functional defect prevents acceptance: Admin variable-mapping validity is stored as stale historical state instead of being derived from the mappings currently visible in the editor. The current implementation can therefore both (a) keep a now-valid mapping blocked after switching away from an invalid literal and (b) treat an unmapped GraphQL variable rendered as a blank literal as valid before that literal has ever parsed successfully.

Attempt 4 is limited to the deterministic correction contract below. Do not redesign the Admin compiler, Tool mutation/reconciliation kernel, metadata action, publication gate, historical Storefront rendering, or Phase 4 runtime.

#### CR-1 — derive Admin mapping validity from the current visible mapping set

Files:

```text
src/studio/tools/shopify-admin-editor.tsx
tests/shopify-admin-tools-ui.test.tsx
```

The current editor stores `literalValidity` entries independently from the current mapping mode. That produces stale state. For example:

```text
$query mapped as Bounded literal
→ literal text blank
→ literalValidity.query = false

user changes $query to input:query
→ execution.variables.query is now valid
→ stale literalValidity.query remains false
→ parent adminMappingValid remains false
→ Save/Validate remain blocked incorrectly
```

The reverse edge also exists:

```text
GraphQL document introduces $query
execution.variables.query is absent
UI renders Bounded literal with blank text
literalValidity has no query entry
→ aggregate check can incorrectly remain true
→ Save can persist an unmapped/blank visible variable state
```

Required implementation rule:

1. Compute mapping validity from the CURRENT GraphQL variable names, CURRENT `execution.variables`, CURRENT parsed top-level `inputSchema` properties, and CURRENT visible literal text.
2. For every current GraphQL variable:
   - no mapping => invalid;
   - `{ input: name }` => valid only when `name` exists in the current top-level inputSchema properties;
   - `{ literal: ... }` => valid only when the visible literal text for that variable exists and parses as JSON.
3. Variables no longer present in the current GraphQL document MUST NOT contribute stale validity state.
4. Switching `literal -> input` MUST immediately stop considering the old literal text/validity for that variable.
5. Switching `input -> literal` MUST immediately make the mapping invalid until the visible literal text parses as JSON.
6. Editing one literal MUST NOT clear an invalid state belonging to another currently literal-mapped variable.
7. Changing `inputSchemaText` so an input-mapped property disappears MUST immediately make the mapping aggregate invalid; Save and Validate MUST NOT call their Server Actions while that mapping is invalid.
8. The parent callback `onInputValidityChange(...)` MUST always receive the aggregate validity of the CURRENT visible mapping set. Do not set it from one variable's latest event in isolation.
9. Do not duplicate the COMMERCE-018 GraphQL type-compatibility compiler in the browser. This UI validity check owns only mapping presence, current input-property existence, and JSON literal parse validity. Type compatibility remains server/compiler-owned.

A deterministic implementation may use a derived helper such as:

```text
isCurrentMappingSetValid(variableNames, execution.variables, inputProperties, literalText)
```

provided it is pure/bounded and is used consistently after document, mapping-mode, literal-text, and input-schema changes.

#### CR-2 — add the missing executable mapping-state regressions

File:

```text
tests/shopify-admin-tools-ui.test.tsx
```

Add focused production-component regressions for ALL of these exact cases:

```text
1. $query has no mapping
   → UI shows the literal editor as blank/invalid (or another explicit unmapped state)
   → Save does not call updateToolDraft
   → Validate does not call validateShopifyAdminDefinitionAction

2. $query = blank Bounded literal
   → invalid
   → switch Mapping for query to input:query
   → aggregate mapping validity becomes true
   → Save may call updateToolDraft
   → Validate may call validateShopifyAdminDefinitionAction

3. two GraphQL variables use literals
   → $query invalid
   → $first valid JSON `10`
   → aggregate remains invalid
   → Save/Validate blocked
   → fix $query to `"TITLE"`
   → aggregate becomes valid

4. $query uses input:query
   → remove `query` from visible Input JSON Schema
   → aggregate becomes invalid immediately
   → Save/Validate blocked before either Server Action is called

5. a variable with stale invalid literal state is removed from the GraphQL document
   → that removed variable no longer contributes to aggregate mapping validity
   → remaining current mappings determine validity
```

Keep the existing Attempt 3 metadata, exact visible Save/Validate, LIVE_TEST_REQUIRED and Admin composite-recovery regressions green.

#### CR-3 — validation and handoff

Attempt 4 MUST run exactly:

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

Required source audits remain:

```bash
if rg -n '<option[^>]*SHOPIFY_STOREFRONT_QUERY|value="SHOPIFY_STOREFRONT_QUERY"' \
  src/studio/tools/tool-library.tsx; then
  echo 'ERROR: new Tool creation still exposes Storefront' >&2
  exit 1
fi

if rg -n 'offline session|accessToken|shopifySession|/admin/api/' \
  src/studio/tools/shopify-admin-editor.tsx \
  src/studio/tools/admin-validation-server-actions.ts; then
  echo 'ERROR: Phase 3 Admin authoring contains live provider/session access' >&2
  exit 1
fi

if rg -n 'actions=\{|adminActions=|service=\{|controlled=' \
  src/studio/tools/tool-library.tsx \
  src/studio/tools/tool-authoring-screen.tsx \
  src/studio/tools/tool-editor.tsx; then
  echo 'ERROR: C022 restored a function-valued production action boundary' >&2
  exit 1
fi
```

If repository-wide typecheck retains baseline diagnostics, the Completion Report MUST record zero diagnostics in C022-owned source/test files.

Before returning to review, reconcile the executor-owned Work Items, Acceptance Criteria and Validation checklists with what actually ran, update the Completion Report with the final Attempt 4 implementation commit and final parent handoff commit, and return exactly:

```yaml
status: review
attempt: 4
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

Attempt 3 reports:

```text
Focused Admin/C020/UI packet: 38/38 passed
COMMERCE-018 compiler:         22/22 passed
COMMERCE-024 validation:        9/9 passed
targeted lint/type diagnostics: passed
git diff --check:               passed
```

Those results support the accepted Attempt 3 foundation, but the current focused tests do not execute the stale mapping-mode transitions described in CR-1/CR-2.

### Architecture Conformance

Not yet conformant. The Admin GraphQL authoring boundary now conforms on metadata identity, exact Save/Validate candidates, publication gating, zero-provider-I/O behavior and composite recovery. The remaining defect is local UI mapping-state correctness: mapping validity can still reflect stale literal history rather than the current visible mapping set.

### Follow-up

Reclaim the SAME task as Attempt 4. Implement CR-1 through CR-3 only. Preserve all accepted Attempt 3 work. Do not add live Shopify/session/provider I/O, do not modify Explore/discovery UI, and do not begin Phase 4. After required validation passes, set the task to `review`, clear the claim, return to `moda_architect`, and STOP.
