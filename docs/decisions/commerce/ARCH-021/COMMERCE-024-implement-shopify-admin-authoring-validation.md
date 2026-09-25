---
id: ARCH-021-COMMERCE-024
architecture_id: ARCH-021
title: Implement Shopify Admin GraphQL authoring validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-018
  - ARCH-021-COMMERCE-019
enables:
  - ARCH-021-COMMERCE-022
created: 2026-09-24
updated: 2026-09-25
---

# Implement Shopify Admin GraphQL authoring validation

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Implement the authoritative zero-provider-I/O validation boundary for canonical `SHOPIFY_ADMIN_GRAPHQL` Tool definitions using the pinned COMMERCE-018 compiler, independently of External HTTP request-JavaScript work.

## Context

COMMERCE-018 owns the pinned Admin 2026-07 compiler and schema provenance. COMMERCE-019 owns the common validation result/auth/publication gate. This task composes those boundaries for the Shopify Admin authoring UI without resolving a shop session or calling Shopify.

## Scope

Primary files:

```text
src/commerce/tool-authoring/admin-validation.ts
src/studio/tools/admin-validation-server-actions.ts
tests/shopify-admin-authoring-validation.test.ts
package.json
```

## Out of Scope

- External HTTP/request JavaScript validation.
- Shopify offline-session/token lookup.
- Admin API execution.
- Dev MCP invocation from normal Studio requests.
- Live-test receipts.
- Tool editor UI.

## Requirements

### R1 — full Admin definition validation

For a candidate full definition:

1. parse through COMMERCE-016 `CommerceToolDefinitionSchema`;
2. require `execution.kind === 'SHOPIFY_ADMIN_GRAPHQL'`;
3. invoke the COMMERCE-018 local compiler with the exact Tool `inputSchema`;
4. require the compiler's pinned `schemaHash` to equal `definition.execution.schemaHash`;
5. validate responseTemplate against the declared/proved resultSchema;
6. return COMMERCE-019 `ToolAuthoringValidation`.

The normal validation path performs no Dev MCP call, shop/session lookup or Admin API request.

### R2 — schema metadata for authoring UI

Expose the pinned authoring metadata needed by COMMERCE-022 through the named Server Action `src/studio/tools/admin-validation-server-actions.ts`. Every action in that module MUST call `requireStudioPlatformRole('ADMIN')`; do not create a duplicate auth helper or function-valued production port. Return metadata through COMMERCE-019 `ToolAuthoringActionResult`.

The metadata is:

```text
apiVersion = 2026-07
schemaHash = exact committed COMMERCE-018 artifact SHA-256
```

The browser cannot choose a schema path, package version or arbitrary hash.

### R3 — explicit errors and deterministic diagnostics

Compiler syntax/schema/operation/variable/result-shape failures are translated into the common bounded issue form with deterministic paths under `/execution/...`. No raw session/token/provider payload may appear in diagnostics.

Validation/metadata actions are non-mutating. `FORBIDDEN`, `INVALID_INPUT`, `NOT_FOUND`, `DATABASE_UNAVAILABLE` and `INTERNAL_ERROR` remain explicit COMMERCE-019 action results; they MUST NOT become `unknown`/`UNCONFIRMED`. Unexpected errors are logged server-side through the approved shared structured logger.

### R4 — publication relationship

This task proves authoring validity only. It MUST NOT create a live-test receipt. After successful validation, publication remains blocked by COMMERCE-019 `LIVE_TEST_REQUIRED`.

### R5 — focused validation

Add `test:arch021-shopify-admin-authoring-validation` proving:

- valid named Admin query is accepted locally;
- mutation/subscription is rejected;
- wrong schema hash is rejected;
- bounded-query failures from COMMERCE-018 propagate deterministically;
- stale/invalid inputSchema variable mapping is rejected;
- schemaHash metadata is server supplied;
- no Dev MCP/shop session/Admin transport is called;
- common issue/auth contract comes from COMMERCE-019.

## Work Items

- [ ] Add Shopify Admin full-definition validation boundary.
- [ ] Expose pinned API version/schemaHash metadata for authoring UI.
- [ ] Translate compiler diagnostics to the common validation result.
- [ ] Use COMMERCE-019 explicit action results and COMMERCE-027 `requireStudioPlatformRole('ADMIN')`.
- [ ] Add focused zero-provider-I/O tests.

## Interfaces / Contracts

Consumes COMMERCE-016 Tool contracts, COMMERCE-018 compiler and COMMERCE-019 common validation/auth contract.

Produces the authoritative Shopify Admin authoring-validation boundary consumed by COMMERCE-022.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-018
- ARCH-021-COMMERCE-019

## Enables

- ARCH-021-COMMERCE-022

## Acceptance Criteria

- [ ] Shopify Admin authoring validation is server authoritative and zero-provider-I/O.
- [ ] Only compiler-proved pinned Admin 2026-07 query definitions can validate.
- [ ] API version/schemaHash metadata is server owned and not user-selectable.
- [ ] Validation creates no evidence that can satisfy the Phase 3 publication gate.
- [ ] PLATFORM_ADMIN and PLATFORM_SUPER_ADMIN are admitted through hierarchy; merchant roles are denied.
- [ ] Validation/metadata failures remain explicit and never become mutation UNCONFIRMED state.

## Validation

- [ ] `npm run test:arch021-shopify-admin-authoring-validation`
- [ ] `npm run test:arch021-shopify-admin-compiler`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not build Tool UI or execute Admin GraphQL against a shop.

## Implementation Notes

Shopify Dev MCP remains an explicit developer oracle owned by COMMERCE-018; it is not part of this runtime validation path.

## Completion Report

### Status
Ready for Review — Attempt 2
### Files Changed
- `src/commerce/tool-authoring/admin-validation.ts`
- `src/studio/tools/admin-validation-server-actions.ts`
- `tests/shopify-admin-authoring-validation.test.ts`
### Work Completed
- Normalized compiler-origin Admin GraphQL diagnostics to the canonical slash-delimited `/execution/...` path contract.
- Preserved the zero-provider-I/O local compiler boundary, server-owned API version/schema hash metadata, explicit COMMERCE-019 action results, and ADMIN platform-role authorization.
- Added exact operation, schema-hash, connection-bound, and variable compiler-path regression assertions.
### Validation Results
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-024`; launcher synchronized `task/ARCH-021-COMMERCE-024`, remote parity was `not-needed`, and parent head before report work was `2fd3e0f1c406f8069a124fe2e32b407c283e8289`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-024`; launcher synchronized `task/ARCH-021-COMMERCE-024`, remote parity was `not-needed`, and implementation head before correction was `c98cd0b27e07d441a0561552888d5d96f7501cfa`.
- Launcher claim: `--prepare --executor copilot --json` succeeded; dependency gate passed; Attempt 2 claimed; parent claim commit `2fd3e0f1c406f8069a124fe2e32b407c283e8289` was committed and pushed.
- Recursive submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; status `ready`; database submodule commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commit: `eb1c658c0cb9b77b38f3e1df82c9e89d3328f3cd`; implementation branch pushed to `origin/task/ARCH-021-COMMERCE-024` and matched its remote tip after push.
- Parent report commit: `23bf78bfbd8bccfb4c71efe56b1df654bc832c3a`.
- `npm run test:arch021-shopify-admin-authoring-validation`: 1 file passed, 9 tests passed.
- `npm run test:arch021-shopify-admin-compiler`: 2 files passed, 22 tests passed.
- `npm exec eslint src/commerce/tool-authoring/admin-validation.ts src/studio/tools/admin-validation-server-actions.ts tests/shopify-admin-authoring-validation.test.ts`: passed.
- `npm run typecheck`: blocked by 267 pre-existing diagnostics across 34 unrelated files; zero diagnostics were reported in the three C024 task-owned files.
- `git diff --check`: passed.
- Final implementation worktree was clean after commit/push; parent worktree was clean before this report update. Branch/remote parity was verified with `git rev-parse HEAD` and `git rev-parse @{u}`.
### Deviations
- Full typecheck remains non-blocking only because diagnostics are outside the C024 task-owned files and include existing generated-Prisma/module baseline failures.
### Assumptions
- COMMERCE-019 remains authoritative for publication gating and `LIVE_TEST_REQUIRED`; this task creates no live-test receipt or publication evidence.
### Unresolved Issues
- None within C024 scope.
### Architectural Concerns
None

## Architect Review

### Review Status
Changes Requested

### Review Notes

Attempt 1 establishes the intended zero-provider-I/O Shopify Admin authoring-validation boundary and is otherwise directionally correct. Preserve the production design in `src/commerce/tool-authoring/admin-validation.ts` and `src/studio/tools/admin-validation-server-actions.ts`: local COMMERCE-018 compiler only, pinned server-owned API version/schema hash, COMMERCE-019 `ToolAuthoringValidation` / `ToolAuthoringActionResult`, and `requireStudioPlatformRole('ADMIN')`. Do not add Shopify session/token lookup, Admin API execution, Dev MCP calls, live-test receipts, browser-selectable schema metadata, another auth helper, or a function-valued production port.

Attempt 2 is limited to the following deterministic corrections.

#### CR-1 — normalize compiler diagnostic paths to the canonical slash path contract

Modify exactly:

```text
src/commerce/tool-authoring/admin-validation.ts
tests/shopify-admin-authoring-validation.test.ts
```

COMMERCE-018 compiler errors use internal dotted paths such as:

```text
execution.operationName
execution.schemaHash
execution.document.products.first
execution.variables.query
```

C024 R3 requires the authoring boundary to expose bounded paths under `/execution/...`. The current adapter prepends `/` without converting dot separators, producing invalid public paths such as `/execution.schemaHash`.

Implement one local path-normalization helper with these exact rules:

```text
input already begins with '/'
  -> preserve it unchanged

otherwise
  -> split on '.'
  -> discard empty segments
  -> join segments with '/'
  -> prefix one leading '/'

missing/non-string compiler path
  -> '/execution'
```

Required examples:

```text
execution.operationName
  -> /execution/operationName

execution.schemaHash
  -> /execution/schemaHash

execution.document.products.first
  -> /execution/document/products/first

execution.variables.query
  -> /execution/variables/query
```

Do not change COMMERCE-018 compiler error codes/messages and do not modify `lib/discovery/admin-compiler.ts` merely to satisfy this adapter contract. `parsedIssue()` paths created from Zod issue arrays remain slash-delimited as they are today.

Update the focused tests so they assert the exact slash paths above. At minimum the existing mutation/subscription, wrong-schema-hash and invalid-connection-bound assertions MUST use slash paths. Add one variable-mapping/compiler-path regression asserting `/execution/variables/...` when the compiler provides a variable-specific path.

#### CR-2 — preserve zero-provider-I/O and explicit action-result behavior

Do not broaden Attempt 2. The final implementation MUST still satisfy all of the following:

```text
validateShopifyAdminDefinition()
  -> no auth lookup
  -> no shop/session lookup
  -> no Shopify Admin transport
  -> no Dev MCP invocation

validateShopifyAdminDefinitionAction()
getShopifyAdminAuthoringMetadataAction()
  -> call requireStudioPlatformRole('ADMIN')
  -> return ToolAuthoringActionResult
  -> never return kind:'unknown' / UNCONFIRMED

metadata
  apiVersion = 2026-07
  schemaHash = committed COMMERCE-018 adminSchemaHash
```

Do not create publication evidence or a live-test receipt. C019 continues to own `LIVE_TEST_REQUIRED`.

#### CR-3 — reconcile the task execution record before review handoff

The supplied parent snapshot is not a valid review handoff: YAML is `in_progress` with an active claim and the formal Completion Report is still `Not Started`. Attempt 2 MUST complete the existing task protocol rather than placing execution evidence in chat only.

Before returning to Architect Review, update the executor-owned task fields/checklists and Completion Report so the task file records all of the following:

```text
status: review
executor: null
claimed_at: null
attempt: 2
```

Completion Report MUST include:

```text
- dedicated parent worktree path
- dedicated implementation worktree path
- launcher/start-of-attempt synchronization evidence for both worktrees
- recursive submodule materialization evidence
- database submodule commit
- exact implementation commit SHA
- exact parent report commit SHA
- changed-file list
- exact validation commands/results
- branch/remote parity and clean-worktree evidence
- Deviations / Assumptions / Unresolved Issues / Architectural Concerns
```

Do not mark the task Complete.

### Reviewed Files

```text
src/commerce/tool-authoring/admin-validation.ts
src/studio/tools/admin-validation-server-actions.ts
src/commerce/tool-authoring/contracts.ts
src/commerce/tool-definition/publication.ts
lib/discovery/admin-compiler.ts
tests/shopify-admin-authoring-validation.test.ts
package.json
docs/decisions/commerce/ARCH-021/COMMERCE-024-implement-shopify-admin-authoring-validation.md
```

### Validation Reviewed

Submitted Attempt 1 evidence:

```text
focused C024 tests: 9/9 reported passing
COMMERCE-018 compiler suite: 22/22 reported passing
new-file lint: reported passing
git diff --check: reported passing
full typecheck: unrelated baseline failures reported
```

The attached parent snapshot does not contain a completed Completion Report, so this evidence is not yet durably reconciled into the task record. The linked GitHub connector available to this review session did not expose `kodjobaah/moda-interact-commerce`, so remote commit/branch state could not be independently fetched; the Attempt 2 Completion Report must therefore carry the required Git/worktree/push evidence.

Attempt 2 MUST run exactly:

```bash
npm run test:arch021-shopify-admin-authoring-validation
npm run test:arch021-shopify-admin-compiler

npm exec eslint \
  src/commerce/tool-authoring/admin-validation.ts \
  src/studio/tools/admin-validation-server-actions.ts \
  tests/shopify-admin-authoring-validation.test.ts

npm run typecheck
git diff --check
```

For `npm run typecheck`, documented unrelated baseline diagnostics remain non-blocking only if there are zero diagnostics in the C024 task-owned files above. Record that distinction explicitly in the Completion Report.

### Architecture Conformance

Changes Requested. The zero-I/O validation architecture, pinned metadata ownership, COMMERCE-019 action envelope and COMMERCE-027 authorization boundary conform. Public compiler diagnostic paths currently violate C024 R3, and the durable task handoff is incomplete.

### Follow-up

1. Apply CR-1 through CR-3 only.
2. Preserve all already-correct Attempt 1 behavior.
3. After the defined corrections and required validation are complete, set the task to `review`, clear the claim, finish the Completion Report and STOP.
4. Do not begin ARCH-021-COMMERCE-022 or any adjacent Tool UI/provider-execution work.
