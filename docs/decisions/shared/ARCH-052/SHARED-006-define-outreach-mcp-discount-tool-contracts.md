---
id: ARCH-052-SHARED-006
architecture_id: ARCH-052
title: Define the minimal outreach MCP execution-context contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: 2026-10-29
---


# ARCH-052-SHARED-006: Define the minimal outreach MCP execution-context contract

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Task materialised and claimed through the prepared launcher on 2026-10-29. The launcher created the dedicated mirrored task worktrees, synchronized both task branches, initialized the implementation submodules, and pushed the Attempt 1 claim before implementation began.

## Objective

Define the **exact, minimal structural context** used when Background invokes MCP tools on behalf of a recovery attempt before any customer conversation exists. Reuse MCP's existing generic request/result infrastructure and do not add a new commerce feature or business validator to Shared.

## Context

`moda-interact-mcp/src/mcp/authentication.ts` already decodes a trusted, private-ingress context containing `shopId` and an optional opaque `toolContext`. MCP's execution ports pass that context to registered adapters. Existing `CommerceAssertionSchema` (`resolve`/`execute`) is for conversational CommerceAgent turns; `CommerceToolResultSchema` is generic and already used by MCP. Neither should be replaced.

## Scope

- Introduce only the new `CommerceOutreachToolContextSchema` module shown below and export it through the existing `/commerce` entrypoint.
- Background supplies the recovery/attempt identifiers as part of the **trusted MCP request context**, never as model-authored `tools/call` arguments.
- MCP performs shop/recovery/attempt and current merchant discount-scope checks in its own runtime, not by Zod field refinements.
- Preserve the existing conversational `CommerceToolInputs` and `CommerceToolOutputs` signatures and generic `CommerceToolResultSchema`. No additional response envelope.

## Out of Scope

- No `commerce_get_outreach_context` MCP tool. Background already supplies checkout and merchant context directly to its agent.
- No attempt policy snapshot, signed HMAC protocol, provider-client change, business grant machinery, new database state, conversation lease/inbound-message fabrication or tool publication.
- No new MCP tool input/output schemas in this task; system-defined discount tool advertisement/execution belongs to `ARCH-052-MCP-002` and product tools to `ARCH-052-SHARED-008`/`MCP-003`.

## Requirements

- Zod checks only the fixed discriminator and field types; no business-rule `.refine`, `.superRefine`, `.transform` or `.check`.
- The top-level MCP `shopId` comes from the existing authenticated private-ingress context; it is not duplicated inside the new `toolContext` schema.
- MCP must independently establish that the supplied recovery/attempt belongs to the top-level shop, and enforce current merchant settings, with failure mapped into existing generic MCP errors. This verification is not implemented in Shared.
- Follow dedicated mirrored task-worktree preparation and completion-report rules; use the existing Shared logger for any runtime logging and never log raw private request headers or customer data.

## Work Items

- [x] Create the exact source module below.
- [x] Export it from `moda-interact-shared/src/commerce/index.ts`.
- [x] Add the exact structural fixtures and negative tests to `src/commerce/contracts.test.ts`.
- [x] Verify existing conversation, tool input/output and generic result tests remain unchanged.

## Interfaces / Contracts

**Create `moda-interact-shared/src/commerce/outreach-context.ts` exactly as follows:**

```typescript
import { z } from "zod";
import { IdSchema } from "./primitives";

export const CommerceOutreachToolContextSchema = z.strictObject({
  purpose: z.literal("INITIAL_RECOVERY_OUTREACH"),
  checkoutRecoveryId: IdSchema,
  outreachAttemptId: IdSchema,
});

export type CommerceOutreachToolContext =
  z.infer<typeof CommerceOutreachToolContextSchema>;
```

**Add this exact export to `moda-interact-shared/src/commerce/index.ts`:**

```typescript
export * from "./outreach-context";
```

No new package subpath is necessary: the existing `@modainteract/moda-interact-shared/commerce` export already points to `src/commerce/index.ts` through the build.

**Trusted MCP context example (outer shape is already owned by MCP):**

```json
{
  "shopId": "shop_123",
  "toolContext": {
    "purpose": "INITIAL_RECOVERY_OUTREACH",
    "checkoutRecoveryId": "recovery_456",
    "outreachAttemptId": "attempt_789"
  }
}
```

Only `toolContext` is parsed by the new Shared schema; `shopId` is parsed by existing MCP authentication and `environment` is supplied by the MCP runtime.

**Existing definitions that MUST remain unmodified:**

```typescript
// src/commerce/schemas.ts — existing signatures, not new code
CommerceToolInputs.commerce_get_discount_options; // {}
CommerceToolInputs.commerce_evaluate_discount; // {offerId, proposal}
CommerceToolResultSchema; // commerce.v1 OK / ERROR
CommerceAssertionSchema; // existing conversation resolve / execute assertions
```

**Concrete structural fixtures:**

```typescript
import { strict as assert } from "node:assert";
import { CommerceOutreachToolContextSchema } from "./outreach-context";

assert.equal(CommerceOutreachToolContextSchema.safeParse({
  purpose: "INITIAL_RECOVERY_OUTREACH",
  checkoutRecoveryId: "recovery_456",
  outreachAttemptId: "attempt_789",
}).success, true);

assert.equal(CommerceOutreachToolContextSchema.safeParse({
  purpose: "INITIAL_RECOVERY_OUTREACH",
  checkoutRecoveryId: "recovery_456",
  outreachAttemptId: "attempt_789",
  shopId: "model_forged_shop", // unknown extra key
}).success, false);

assert.equal(CommerceOutreachToolContextSchema.safeParse({
  purpose: "CONVERSATION",
  checkoutRecoveryId: "recovery_456",
  outreachAttemptId: "attempt_789",
}).success, false);
```

**Domain checks outside Zod:** MCP validates the existing top-level shop identity; matches recovery and attempt to that shop in PostgreSQL; rejects model-controlled identities; restricts tool discovery/calls to the permitted context and current merchant settings. Successful structural parsing **never by itself grants a capability**.

## Dependencies

None.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [x] The specified schema/type are published through the existing `/commerce` entrypoint.
- [x] Valid context passes and unknown fields, missing attempt ID or wrong purpose fail structural parsing.
- [x] Existing conversation assertion, discount tool inputs/outputs and generic MCP result envelope are unchanged.
- [x] No outreach-context lookup tool or independent HMAC/business-validation framework is added to Shared.
- [x] Business authorisation and current merchant-policy checks remain assigned to MCP.

## Validation

- [x] `npm run typecheck`, `npm test`, `npm run build` as declared by Shared.
- [x] Unit/negative tests in `src/commerce/contracts.test.ts`, including unchanged old cases.
- [x] `git diff --check`, export-shape check for published `/commerce`.

## Stop Condition

On passing Work Items, Acceptance Criteria and Validation, update the Completion Report, set the task to `review`, return worktree/commit evidence to `moda_architect` and **STOP**. Do not self-accept or begin dependent tasks.

## Implementation Notes

Implement the exact source and exported type above. Do not invent alternate assertion purposes or model-provided shop identity. In case of a newly discovered mismatch with the existing MCP header transport, return it to architect for a bounded implementation-task correction rather than broadening Shared.

## Completion Report

### Status

Ready for Review. Attempt 1 was claimed and pushed by the prepared launcher. Implementation commit `29ed192` and parent report commit `437608cc` are pushed on their mirrored task branches.

### Files Changed

`src/commerce/outreach-context.ts`, `src/commerce/index.ts`, and `src/commerce/contracts.test.ts` in `moda-interact-shared`.

### Work Completed

- Added the specified strict context schema and inferred type with only the purpose literal and recovery/attempt IDs. No business authorisation was added to Shared.
- Exported the schema/type from the existing `/commerce` entrypoint.
- Added positive, unknown-field, invalid-purpose and missing-attempt fixtures in the existing commerce contracts test file.
- Existing conversation assertion, discount input/output schemas and generic tool result schema were not modified.

### Prepared Launcher and Start-of-Attempt Synchronization Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-006`, branch `task/ARCH-052-SHARED-006`, prepared start HEAD `b1a4e84be53d3a2db06984daef0ff46064a80622`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-006`, repository `moda-interact-shared`, branch `task/ARCH-052-SHARED-006`, prepared start HEAD `7e0e167e04540ef57787dac3d42e7fbf645cf28f`.
- Both worktrees were created fresh; each task branch needed no remote fast-forward and already included `origin/main`. The prepared implementation submodule synchronization/update passed; no recursive submodule entries were present and status was `ready`.
- Attempt 1 claim commit `422916eb247e4525981ac99df2240884ab34791e` was committed and pushed by the launcher. Final parent sync incorporated `origin/main` at `961ec7b2aa172ce86e7c0cf014f561b8ff7ff3b1` before implementation. No shared/default checkout was switched or used for implementation.
- Implementation commit `29ed192` and parent report commit `437608cc` were pushed on their respective `task/ARCH-052-SHARED-006` branches.

### Validation Results

- `npm ci --prefer-offline` installed the locked dependencies. npm reported three audit notices (1 low, 2 high) and five pending package install scripts; no install-script failure affected the successful validations below.
- `npm run typecheck` passed.
- `npm test` passed: 382 tests, 381 passed, 0 failed, 1 skipped because `TEST_REDIS_URL` is not configured (BullMQ trace-context integration).
- `npm run build` passed and generated the Commerce declarations/bundle with the new export.
- A clean package import from `@modainteract/moda-interact-shared/commerce` confirmed `CommerceOutreachToolContextSchema` is exported and accepts the valid structural fixture.
- `git diff --check` passed. The complete suite retained all existing conversation, discount input/output and generic-result coverage.

### Deviations

The first sandboxed install/test/build attempts were denied while creating `node_modules`, the `tsx` IPC socket and a temporary tsup config. Retried with the required repository/temp-file access; all three requested scripts passed. npm’s optional install scripts remained pending, but the package build and test suite both succeeded.

### Assumptions

The recovery and attempt identifiers in `toolContext` are trusted MCP request-context values supplied by Background, not model-authored tool arguments; MCP owns identity matching and authorization.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Escalate any unexpected provider API/auth/Shared/schema/contract gap to `moda_architect` without inventing a second implementation.

## Architect Review

### Review Status

Accepted

### Review Notes

The task is correctly submitted in `review` at Attempt 1. The implementation branch `task/ARCH-052-SHARED-006` is clean at `29ed192` and contains only the three task-scoped files. `CommerceOutreachToolContextSchema` matches the normative strict object: it carries only the fixed `INITIAL_RECOVERY_OUTREACH` purpose and recovery/attempt identifiers, reusing the existing `IdSchema`. The export is available from the existing `/commerce` entrypoint. Tests cover the valid context, unknown/forged `shopId`, wrong purpose, and missing attempt identifier. Existing conversation assertions, discount input/output schemas, and generic result envelopes are unchanged. No separate MCP tool, new package subpath, business validator, or persistence was introduced.

The Completion Report records dedicated parent and implementation worktrees, start synchronization, submodule preparation, and pushed task commits. Required typecheck, full suite (381 passed, 1 skipped, 0 failed), build, package import/export check, and diff check passed. npm's install notices did not cause validation failures or change dependency manifests. No tests were rerun for this review.

### Reviewed Files

- Attempt 1 Completion Report, task scope, Acceptance Criteria and Validation.
- Shared implementation branch `task/ARCH-052-SHARED-006` at `29ed192`, clean with a three-file diff from `origin/main`.
- `src/commerce/outreach-context.ts`.
- `src/commerce/index.ts` and `src/commerce/contracts.test.ts`.
- Existing `src/commerce/schemas.ts` and ARCH-052 dependency records.

### Validation Reviewed

Reviewed `npm run typecheck`, `npm test` (381 passed, 1 skipped, 0 failed), `npm run build`, import through `@modainteract/moda-interact-shared/commerce`, and `git diff --check`. No tests were rerun for this review.

### Architecture Conformance

The contract uses trusted MCP request context as intended and gives no capability based on structural parsing alone. Authorization and current merchant-policy checks remain MCP-owned. The implementation conforms to the task and ARCH-052 boundaries.

### Follow-up

Set this automatic-completion task to `complete`. Keep `ARCH-052-SHARED-003` `pending`; its other Shared implementation prerequisites have not all reached `complete`. No publication or consumer task is promoted by this acceptance.
