---
id: ARCH-021-COMMERCE-019
architecture_id: ARCH-021
title: Establish Phase 3 authoring validation and publication gate
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 34
executor: copilot
claimed_at: 2026-09-25T12:25:05Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-027
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-021-COMMERCE-023
  - ARCH-021-COMMERCE-024
created: 2026-09-23
updated: 2026-09-25
---

# Establish Phase 3 authoring validation and publication gate

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Define one common server-side validation/result/authorization contract for Phase 3 Tool authoring and install the fail-closed `LIVE_TEST_REQUIRED` publication gate, consuming the simplified Auth.js role hierarchy and explicit error model without introducing another auth layer, function-valued production port or generic `unknown` validation result.

## Context

COMMERCE-016 owns the canonical Commerce-local Tool definition. COMMERCE-027 established the hierarchical Studio authorization model:

```text
PLATFORM_SUPER_ADMIN > PLATFORM_ADMIN > MERCHANT_ADMIN > MERCHANT_EDITOR > MERCHANT_VIEWER
```

Phase 3 Tools remain platform-owned in this phase. Merchant Tool ownership is not introduced here. The simplification terminal system test remains Ready by developer choice and is not a dependency of this implementation task.

The existing ARCH-020 external publication validator uses synthetic response samples/receipts. ARCH-021 requires a successful real selected-shop/provider test for the exact saved revision before a newly authored Phase 3 Tool can publish. Phase 4 owns that live-test receipt.

## Scope

Primary files:

```text
src/commerce/tool-authoring/contracts.ts
src/commerce/external-publication/index.ts
src/commerce/external-publication/contracts.ts
src/commerce/publication/validation.ts            # only exact gate/error propagation needed
lib/auth/merchant-access.ts                       # consume existing helper; no new role model
lib/auth/role-hierarchy.ts                        # consume only; modify only if a task-owned defect is proven
tests/tool-authoring-common-validation.test.ts
tests/tool-authoring-authorization.test.ts
package.json
```

Do NOT create `src/commerce/tool-authoring/auth.ts` or another authorization matrix. Use the accepted COMMERCE-027 helpers directly.

## Out of Scope

- Compiling or previewing request JavaScript (COMMERCE-023).
- Validating connection revisions (COMMERCE-023).
- Compiling Shopify Admin GraphQL (COMMERCE-024).
- Real Shopify/external requests.
- Live-test receipt implementation (Phase 4).
- Tool editor UI.
- Merchant-owned Tool libraries.
- Provider credentials in browser/client contracts.
- Replacing historical ARCH-020 publication evidence for already-published development revisions.

## Requirements

### R1 — exact common validation result

Export exactly one bounded structural-validation envelope:

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

Maximum 32 issues. Each `path`, `code` and `message` is bounded to 512 UTF-8 bytes. Messages MUST NOT contain credentials, access tokens, authorization headers, provider response payloads or raw database connection details.

### R2 — exact Phase 3 authorization policy

Every new Phase 3 platform Tool authoring Server Action MUST use the already-accepted helper:

```ts
requireStudioPlatformRole('ADMIN')
```

from `lib/auth/merchant-access.ts`.

This means:

```text
PLATFORM_ADMIN        allowed
PLATFORM_SUPER_ADMIN  allowed through hierarchy
MERCHANT_ADMIN        denied
MERCHANT_EDITOR       denied
MERCHANT_VIEWER       denied
```

`developmentBypass === true` is already resolved by COMMERCE-027 to the development `PLATFORM_SUPER_ADMIN`; Phase 3 MUST NOT re-check bypass id, role, email, provider subject or `PlatformAdmin` membership.

Publishing/enabling/disabling remains subject to the existing lifecycle `SUPER_ADMIN` requirement. This task MUST NOT weaken that requirement.

### R3 — exact Server Action failure contract

For non-mutating Phase 3 validation/metadata/request-preview Server Actions, export/reuse this exact envelope:

```ts
type ToolAuthoringActionCode =
  | 'FORBIDDEN'
  | 'INVALID_INPUT'
  | 'NOT_FOUND'
  | 'DATABASE_UNAVAILABLE'
  | 'INTERNAL_ERROR';

type ToolAuthoringActionResult<T> =
  | { kind: 'ok'; value: T }
  | {
      kind: 'error';
      code: ToolAuthoringActionCode;
      message: string;
      retryable: boolean;
    };
```

Rules:

1. known validation errors are `INVALID_INPUT`;
2. missing durable authoring resources are `NOT_FOUND`;
3. authorization denial is `FORBIDDEN`;
4. Prisma connectivity/timeout/disconnect classes `P1001`, `P1002`, `P1008`, `P1017` are `DATABASE_UNAVAILABLE` with `retryable: true`;
5. unexpected exceptions are logged server-side through the approved shared structured logger and returned as bounded `INTERNAL_ERROR`;
6. the result MUST NOT contain `kind: 'unknown'`;
7. a validation/read action MUST NOT create UI `UNCONFIRMED` state because it makes no durable mutation.

Transport uncertainty for Tool mutations is owned by COMMERCE-020 and is reconciled through `CommerceAuditEvent.operationId`; it is not represented by this validation result.

### R4 — exact Phase 3 publication gate

For an otherwise structurally valid DRAFT using either canonical Phase 3 kind:

```text
EXTERNAL_HTTP
SHOPIFY_ADMIN_GRAPHQL
```

`validateForPublication` MUST preserve/return exactly:

```text
code: LIVE_TEST_REQUIRED
path: /liveTest
message: Run a successful live tool test for the current saved revision before publishing.
```

The publication lifecycle must preserve `LIVE_TEST_REQUIRED` as an identifiable failure code through the Server Action/UI boundary; do not collapse it into a generic `UNAVAILABLE`/`INTERNAL_ERROR` message.

Phase 4 will replace this fail-closed gate with exact live-test receipt validation.

### R5 — synthetic evidence cannot satisfy publication

Synthetic fixture/sample validation MUST NOT create, translate into or reuse a receipt that satisfies the Phase 3 publication gate. Existing automated fixture utilities remain test assets only.

Already-published historical revisions are read-only history; this task MUST NOT retroactively unpublish them.

### R6 — domain-validator boundary

COMMERCE-023 and COMMERCE-024 MUST return `ToolAuthoringActionResult<ToolAuthoringValidation>` from their named Server Actions and use `requireStudioPlatformRole('ADMIN')` directly. This common task MUST NOT import or invoke either domain compiler and MUST perform zero provider I/O.

### R7 — focused validation

Add `test:arch021-tool-authoring-common` proving all of:

- validation result is bounded to 32 safe issues;
- PLATFORM_ADMIN is admitted;
- PLATFORM_SUPER_ADMIN is admitted through hierarchy;
- all merchant roles are denied for platform Tool authoring;
- development bypass is admitted without a second identity/role lookup;
- `DATABASE_UNAVAILABLE` is returned explicitly and is not converted to unknown;
- unexpected errors are logged and returned as bounded `INTERNAL_ERROR`;
- canonical EXTERNAL_HTTP publication returns exact `LIVE_TEST_REQUIRED`;
- canonical SHOPIFY_ADMIN_GRAPHQL publication returns exact `LIVE_TEST_REQUIRED`;
- synthetic ARCH-020 evidence cannot satisfy either gate;
- already-published historical revisions are not retroactively invalidated;
- no request-JS/Admin compiler/provider transport is invoked by this common layer.

## Work Items

- [ ] Add the bounded common validation and action-result contracts.
- [ ] Consume COMMERCE-027 `requireStudioPlatformRole('ADMIN')`; create no alternate auth helper.
- [ ] Install/preserve exact `LIVE_TEST_REQUIRED` propagation for both canonical Phase 3 kinds.
- [ ] Ensure synthetic evidence cannot satisfy the new gate.
- [ ] Add hierarchy/error/publication focused tests.

## Interfaces / Contracts

Consumes COMMERCE-016 Tool-definition contracts, COMMERCE-027 authorization hierarchy and the accepted ARCH-020 publication lifecycle.

Produces `ToolAuthoringValidation` and `ToolAuthoringActionResult<T>` consumed by COMMERCE-023/024 and surfaced by COMMERCE-021/022.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-027
- ARCH-020-COMMERCE-030

## Enables

- ARCH-021-COMMERCE-023
- ARCH-021-COMMERCE-024

## Acceptance Criteria

- [ ] Phase 3 platform Tool authoring uses the accepted role hierarchy and no duplicate auth model.
- [ ] Validation/read failures are explicit; no common validation path returns generic unknown.
- [ ] External and Admin validators evolve independently behind one bounded validation result.
- [ ] Both canonical Phase 3 kinds fail publication with exact `LIVE_TEST_REQUIRED` until Phase 4.
- [ ] Synthetic evidence cannot satisfy the gate.
- [ ] Common validation/publication code performs zero provider I/O.

## Validation

- [ ] `npm run test:arch021-tool-authoring-common`
- [ ] `npm run test:arch020-external-publication`
- [ ] `npm run test -- --run tests/auth-role-requirements.test.ts tests/auth-permissions.test.ts`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set task to `review`, return Completion Report and STOP. Do not implement either domain validator, Tool UI or live tests.

## Implementation Notes

The simplification `ARCH-021-SYSTEM-TEST-001` remains a terminal Ready task and is intentionally not a dependency. The developer is holding terminal system tests until the implementation phases are finished.

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
