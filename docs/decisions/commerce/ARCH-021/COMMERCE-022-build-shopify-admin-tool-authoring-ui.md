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
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-018
  - ARCH-021-COMMERCE-019
  - ARCH-021-COMMERCE-020
  - ARCH-020-COMMERCE-011
enables: []
created: 2026-09-23
updated: 2026-09-23
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

## Scope

Primary files:

```text
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/shopify-admin-editor.tsx
src/studio/tools/validation-server-actions.ts
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
- `Validate` calls COMMERCE-019/018 server validation.
- Show bounded compiler issues with path/message and never raw session/token data.
- Only a named `query` can become valid. Mutation/subscription errors must be explicit.
- Variable mappings must be selectable only from current top-level `inputSchema` properties plus bounded literal input.
- Changing inputSchema must mark mappings requiring revalidation rather than silently retaining invalid mappings.

### R4 — Shopify developer discovery assistance

The existing Explore/discovery UI may expose `admin-graphql` as an API surface for docs/schema browsing using COMMERCE-018's pinned metadata. Normal validation uses the local committed schema. Do not call `validate_graphql_codeblocks` from browser/server request handling.

### R5 — no live shop requirement

Authoring/validation does not require a selected shop because the GraphQL contract is pinned to Admin 2026-07, not a merchant-specific schema. If a Studio `shopId` exists in navigation, preserve it but do not use it for validation or credentials in Phase 3.

### R6 — publication handoff

Save DRAFT normally. Publication validation must display COMMERCE-019 `LIVE_TEST_REQUIRED` until Phase 4 proves the exact saved revision against a selected shop's offline session.

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
- [ ] Extend discovery surface to Admin docs/schema where applicable.
- [ ] Remove Storefront from new-tool choice while preserving history rendering.
- [ ] Add focused UI regressions.

## Interfaces / Contracts

Consumes COMMERCE-018 compiler and COMMERCE-019 authoring validator.

## Dependencies

- ARCH-021-COMMERCE-018
- ARCH-021-COMMERCE-019
- ARCH-021-COMMERCE-020
- ARCH-020-COMMERCE-011

## Enables

None in Phase 3. Phase 4 live Shopify Tool testing will depend on this task.

## Acceptance Criteria

- [ ] Admin can create a complete, pinned, query-only Shopify Admin tool DRAFT.
- [ ] CommerceAgent argument contract remains the persisted inputSchema/variable mapping.
- [ ] Authoring requires no shop token/session/provider I/O.
- [ ] New Storefront authoring is removed without hiding historical definitions.

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
