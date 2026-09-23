---
id: ARCH-021-COMMERCE-003
architecture_id: ARCH-021
title: Expose a server-validated Studio shop execution context
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-018
enables:
  - ARCH-021-COMMERCE-004
created: 2026-09-23
updated: 2026-09-23
---

# Expose a server-validated Studio shop execution context

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Define and expose the authenticated server-side shop context that later Studio authoring and preview phases will use, including whether the selected shop has an offline Shopify session available, without exposing the offline access token.

## Context

Commerce already has real shop search/inspection through the production backend and already resolves an offline Shopify session for production Shopify operations. What is missing is a small Studio contract representing **which shop is being authored/tested against**.

Phase 1 needs this context before live tool testing or agent configuration is introduced. The selection itself is UI work owned by ARCH-021-COMMERCE-004.

## Scope

- Add a Studio shop-execution-context type distinct from the existing merchant-inspection detail model.
- Add authenticated server service/action(s) to list/search eligible Studio shops and resolve one exact selected shop by id.
- Resolve shop id/domain/label/plan from existing Commerce data.
- Determine whether an offline Shopify session exists for the resolved shop using existing session data.
- Return only bounded availability metadata; never return the Shopify offline token/session secret.
- Translate missing/unauthorised/unavailable states using existing Studio result semantics.

## Out of Scope

- Persisting a selected shop in the database.
- Adding the global shop selector UI.
- Performing Shopify API calls.
- Resolving external credentials for the selected shop.
- Modifying Shopify Session schema or token lifecycle.
- Prompt/model configuration.

## Requirements

The Phase 1 shop context must be explicit and server-validated. A conceptual shape is:

```ts
{
  shopId: string;
  domain: string;
  label: string;
  plan: string;
  shopifyOfflineSessionAvailable: boolean;
}
```

Equivalent naming is permitted, but:

- `shopId` is the durable Commerce shop id;
- domain comes from the persisted shop record;
- the browser never supplies/overrides a domain independently of the selected id;
- offline-session availability is boolean/status metadata only;
- no access token or session payload crosses the server boundary.

A shop lacking an offline session is still a valid selectable shop context; later live Shopify execution must fail/disable explicitly rather than silently changing shops.

## Work Items

- [ ] Add the bounded Studio shop-execution-context contract.
- [ ] Add authenticated list/search and exact-resolution service/action support, reusing current production shop inspection/search.
- [ ] Add offline Shopify session availability lookup without selecting/serialising the token.
- [ ] Add tests for found, missing, unavailable and no-offline-session states.
- [ ] Add a data-safety regression proving no Shopify access token/session secret appears in the returned object or serialized test response.

## Interfaces / Contracts

Consumes:

- existing production Commerce shop search/inspection from ARCH-020-COMMERCE-013/018
- nested Prisma `Shop`/`Session` data already used by Commerce Shopify policy execution
- existing Studio auth/result contracts

Produces:

- one Commerce-local Studio shop-execution-context contract and server resolver.

No Database or Shared schema change is required.

## Dependencies

- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-018

Both are Complete in the Phase 1 definition snapshot.

## Enables

- ARCH-021-COMMERCE-004

## Acceptance Criteria

- [ ] A real persisted shop can be searched and resolved by exact shop id.
- [ ] The resolved domain cannot be replaced by caller-supplied domain text.
- [ ] The result reports whether an offline Shopify session exists without returning its token.
- [ ] A shop without an offline session remains selectable and is marked unavailable for future Shopify execution rather than silently substituted.
- [ ] Missing/forbidden/unavailable states use existing bounded Studio failure semantics.

## Validation

- [ ] focused shop-context service tests
- [ ] focused server action/auth test
- [ ] data-safety assertion for Session/accessToken non-disclosure
- [ ] targeted lint/typecheck for changed files
- [ ] `git diff --check`

No Shopify network call is permitted in this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin ARCH-021-COMMERCE-004.

## Implementation Notes

Reuse the existing shop/session schema. Do not create a new durable `selectedShop` field; Phase 1 selection is request/navigation context, not business state.

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
