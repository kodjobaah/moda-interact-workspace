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
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-006: Define the minimal outreach MCP execution-context contract

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Portable task definition: **defined but not materialised**; no local developer Git claim, branch or push is asserted.

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

- [ ] Create the exact source module below.
- [ ] Export it from `moda-interact-shared/src/commerce/index.ts`.
- [ ] Add the exact structural fixtures and negative tests to `src/commerce/contracts.test.ts`.
- [ ] Verify existing conversation, tool input/output and generic result tests remain unchanged.

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

- [ ] The specified schema/type are published through the existing `/commerce` entrypoint.
- [ ] Valid context passes and unknown fields, missing attempt ID or wrong purpose fail structural parsing.
- [ ] Existing conversation assertion, discount tool inputs/outputs and generic MCP result envelope are unchanged.
- [ ] No outreach-context lookup tool or independent HMAC/business-validation framework is added to Shared.
- [ ] Business authorisation and current merchant-policy checks remain assigned to MCP.

## Validation

- [ ] `npm run typecheck`, `npm test`, `npm run build` as declared by Shared.
- [ ] Unit/negative tests in `src/commerce/contracts.test.ts`, including unchanged old cases.
- [ ] `git diff --check`, export-shape check for published `/commerce`.

## Stop Condition

On passing Work Items, Acceptance Criteria and Validation, update the Completion Report, set the task to `review`, return worktree/commit evidence to `moda_architect` and **STOP**. Do not self-accept or begin dependent tasks.

## Implementation Notes

Implement the exact source and exported type above. Do not invent alternate assertion purposes or model-provided shop identity. In case of a newly discovered mismatch with the existing MCP header transport, return it to architect for a bounded implementation-task correction rather than broadening Shared.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Implementation must confirm package versions and the current task worktree baseline.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Escalate any unexpected provider API/auth/Shared/schema/contract gap to `moda_architect` without inventing a second implementation.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only. No implementation accepted.

### Reviewed Files

Relevant October 29, 2026 code snapshot and task definition; no implementation source changes for this task reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through the canonical launcher only after all dependency task YAMLs are Complete.
