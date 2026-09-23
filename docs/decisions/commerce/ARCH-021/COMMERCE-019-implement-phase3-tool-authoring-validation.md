---
id: ARCH-021-COMMERCE-019
architecture_id: ARCH-021
title: Establish Phase 3 authoring validation contract and publication gate
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 34
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-021-COMMERCE-023
  - ARCH-021-COMMERCE-024
created: 2026-09-23
updated: 2026-09-24
---

# Establish Phase 3 authoring validation contract and publication gate

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Define one common server-side validation result/authentication contract for Phase 3 Tool authoring and install the fail-closed `LIVE_TEST_REQUIRED` publication gate, without coupling External HTTP validation to Shopify Admin compiler work.

## Context

The existing ARCH-020 external publication validator uses synthetic response samples/receipts. ARCH-021 requires a successful real selected-shop/provider test for the exact saved revision before a newly authored Phase 3 Tool can publish.

External HTTP and Shopify Admin authoring are independently useful capabilities with different compiler dependencies. This task therefore owns only their common validation/publication semantics. COMMERCE-023 owns External HTTP authoring validation; COMMERCE-024 owns Shopify Admin authoring validation.

## Scope

Primary files:

```text
src/commerce/tool-authoring/contracts.ts
src/commerce/tool-authoring/auth.ts              # only if a shared helper is required
src/commerce/external-publication/index.ts
src/commerce/external-publication/contracts.ts
src/commerce/publication/validation.ts            # only if central dispatch needs exact new-kind handling
tests/tool-authoring-common-validation.test.ts
package.json
```

## Out of Scope

- Compiling or previewing request JavaScript (COMMERCE-023).
- Validating connection revisions (COMMERCE-023).
- Compiling Shopify Admin GraphQL (COMMERCE-024).
- Real Shopify/external requests.
- Live-test receipt implementation (Phase 4).
- Tool editor UI.
- Provider credentials in browser/client contracts.
- Replacing old ARCH-020 historical publication evidence for already-published development revisions.

## Requirements

### R1 — exact common validation result

Expose the canonical result consumed by both domain validators and both Phase 3 editors:

```ts
type ToolAuthoringValidation =
  | { valid: true; schemaHash: string | null; issues: [] }
  | {
      valid: false;
      schemaHash: string | null;
      issues: Array<{
        path: string;
        code: string;
        message: string;
        line?: number | null;
        column?: number | null;
      }>;
    };
```

Maximum 32 issues. Messages MUST NOT contain raw credentials, tokens or provider response payloads.

### R2 — common authenticated server boundary

Provide/reuse one server-side ADMIN/SUPER_ADMIN authorization helper for Phase 3 authoring actions. Preserve the accepted development rule:

```text
developmentBypass === true
    -> trusted development path is sufficient
```

Do not reintroduce ID/role cross-validation under bypass. Domain validators may compose this helper but remain separate server actions/ports.

### R3 — Phase 3 publication gate

For a DRAFT using either canonical Phase 3 kind:

```text
EXTERNAL_HTTP             (new request-based contract)
SHOPIFY_ADMIN_GRAPHQL
```

`validateForPublication` MUST return exactly the stable non-success result:

```text
code: LIVE_TEST_REQUIRED
path: /liveTest
message: Run a successful live tool test for the current saved revision before publishing.
```

This gate applies only after the definition is otherwise structurally valid according to its owning domain validator. Phase 4 will replace the fail-closed gate with exact live-test receipt validation.

### R4 — synthetic evidence cannot satisfy publication

Synthetic fixture/sample validation MUST NOT create, translate into or reuse a receipt that satisfies the Phase 3 publication gate. Existing automated fixture utilities remain test assets only.

Already-published historical revisions are read-only history; this task MUST NOT retroactively unpublish them.

### R5 — domain-validator contract

COMMERCE-023 and COMMERCE-024 MUST return `ToolAuthoringValidation` and use the common authorization convention. This task MUST NOT import or invoke either domain compiler and MUST perform zero provider I/O.

### R6 — exact focused validation

Add `test:arch021-tool-authoring-common` proving:

- exact common validation result is bounded to 32 safe issues;
- canonical EXTERNAL_HTTP publication returns `LIVE_TEST_REQUIRED`;
- canonical SHOPIFY_ADMIN_GRAPHQL publication returns `LIVE_TEST_REQUIRED`;
- synthetic ARCH-020 sample evidence cannot satisfy either new Phase 3 gate;
- already-published historical revisions are not retroactively invalidated;
- development bypass does not consult PlatformAdmin authorization;
- no request-JS/Admin compiler/provider transport is invoked by this common layer.

## Work Items

- [ ] Add the common authoring-validation result contract.
- [ ] Centralize/reuse the Phase 3 authorization helper where needed.
- [ ] Install the fail-closed live-test publication gate for both canonical Phase 3 kinds.
- [ ] Ensure synthetic evidence cannot satisfy the new gate.
- [ ] Add focused common-contract/publication tests.

## Interfaces / Contracts

Consumes the COMMERCE-016 canonical Tool-definition contract and accepted ARCH-020 publication lifecycle.

Produces the common validation/auth/publication contract consumed by COMMERCE-023 and COMMERCE-024 and surfaced by COMMERCE-021/022.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-020-COMMERCE-030

## Enables

- ARCH-021-COMMERCE-023
- ARCH-021-COMMERCE-024

## Acceptance Criteria

- [ ] External and Admin validators can evolve independently behind one validation result contract.
- [ ] Both canonical Phase 3 kinds fail publication with exact `LIVE_TEST_REQUIRED` until Phase 4.
- [ ] Synthetic evidence cannot satisfy the Phase 3 publication gate.
- [ ] Common validation/publication code performs zero provider I/O.

## Validation

- [ ] `npm run test:arch021-tool-authoring-common`
- [ ] `npm run test:arch020-external-publication`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not implement either domain validator, Tool UI or live tests.

## Implementation Notes

Keep historical ARCH-020 fixture utilities for automated tests; they cease to be proof for publishing new Phase 3 definitions.

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
