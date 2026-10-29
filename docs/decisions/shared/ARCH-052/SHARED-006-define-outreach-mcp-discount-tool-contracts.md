---
id: ARCH-052-SHARED-006
architecture_id: ARCH-052
title: Define the purpose-only outreach MCP context discriminator
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

# ARCH-052-SHARED-006: Define the purpose-only outreach MCP context discriminator

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Portable task definition: **defined but not materialised**; no local developer Git claim, branch or push is asserted.

## Objective

Define the exact **purpose-only** structural discriminator carried in the existing MCP `toolContext` when a trusted Background initial-outreach agent invokes commerce tools. Do not introduce recovery identity, attempt identity, merchant policy, checkout data, a new MCP result envelope or service-side business rules into the Shared context schema.

## Context

`moda-interact-mcp/src/mcp/authentication.ts` already receives a private-ingress request context with top-level `shopId` and optional `toolContext`. The existing `CommerceToolResultSchema` is the generic success/error envelope for all MCP tools; conversational `CommerceAssertionSchema` remains a separate contract. Background loads checkout, merchant settings and instructions as part of its own recovery lifecycle and passes them directly to its agent; MCP only supplies reusable commerce capabilities.

## Scope

- Create only the exact `CommerceOutreachToolContextSchema` module below and export it from the existing Shared `/commerce` entrypoint.
- The new `toolContext` holds **only** `purpose: "INITIAL_RECOVERY_OUTREACH"`. Existing top-level MCP transport remains responsible for `shopId`/environment. The AI cannot author or modify trusted transport context.
- MCP owns shop-scoped tool access, the current merchant discount mode/selected-discount rules and published-tool entitlements; Background owns recovery eligibility, attempt lifecycle and final-send admission. No MCP recovery/attempt database lookup is required by this context.
- Preserve the current generic `CommerceToolResultSchema` and existing conversational tool contracts without alteration.

## Out of Scope

- No `checkoutRecoveryId`, `outreachAttemptId`, checkout fingerprint, product IDs, merchant selected IDs, token, nonce, HMAC or policy snapshot inside this `toolContext`.
- No `commerce_get_outreach_context` MCP tool; no tool registration, discount eligibility logic, provider requests, persistence, conversation lease, grant framework, or customer-message publication in Shared.
- This task does **not** modify the separate `RecoveryDiscountProofRequestSchema` from SHARED-005. Its proof-specific identity fields and how targeted proof obtains trusted data are a distinct contract issue, not a reason to add identifiers to the generic MCP purpose context.

## Requirements

- Zod performs **structural parsing only**: the fixed literal discriminator and unknown-key rejection. No business-rule `.refine`, `.superRefine`, `.transform` or `.check`.
- Keep the shop identity in the established private MCP context, outside `toolContext`; do not duplicate it or let model-authored tool arguments substitute for it.
- Only MCP's runtime determines what tools the trusted shop/purpose may discover or call. Successful Zod parsing does not grant a capability.
- Do not add MCP lookups of `CheckoutRecovery` or `RecoveryOutreachAttempt` to validate this purpose. Recovery/attempt admission remains in Background.
- Follow the existing dedicated mirrored task-worktree and Completion Report policies. Do not log private request headers or customer data.

## Work Items

- [ ] Create `moda-interact-shared/src/commerce/outreach-context.ts` with the exact source below.
- [ ] Export it from `moda-interact-shared/src/commerce/index.ts` without changing other commerce exports.
- [ ] Add the exact positive and negative structural fixtures to `src/commerce/contracts.test.ts`.
- [ ] Verify the existing generic MCP result envelope, conversation assertions and commerce tool schemas are unchanged.

## Interfaces / Contracts

**Create `moda-interact-shared/src/commerce/outreach-context.ts` exactly as follows:**

```typescript
import { z } from "zod";

export const CommerceOutreachToolContextSchema = z.strictObject({
  purpose: z.literal("INITIAL_RECOVERY_OUTREACH"),
});

export type CommerceOutreachToolContext =
  z.infer<typeof CommerceOutreachToolContextSchema>;
```

**Add this exact export to `moda-interact-shared/src/commerce/index.ts`:**

```typescript
export * from "./outreach-context";
```

The existing `@modainteract/moda-interact-shared/commerce` entrypoint remains canonical. No new package subpath or extra result envelope is required.

**Trusted MCP request-context example (outer shape remains owned by MCP):**

```json
{
  "shopId": "shop_123",
  "toolContext": {
    "purpose": "INITIAL_RECOVERY_OUTREACH"
  }
}
```

The new Shared schema parses only the value of `toolContext`. The existing MCP private-ingress path is responsible for the outer `shopId`/environment; the `toolContext` does not prove recovery eligibility.

**Existing definitions that MUST remain unchanged:**

```typescript
// src/commerce/schemas.ts — existing contracts, not new code
CommerceToolInputs.commerce_get_discount_options; // {}
CommerceToolInputs.commerce_evaluate_discount; // {offerId, proposal}
CommerceToolResultSchema; // generic commerce.v1 OK / ERROR
CommerceAssertionSchema; // conversation resolve / execute
```

**Add exactly these structural cases to `src/commerce/contracts.test.ts`:**

```typescript
import { strict as assert } from "node:assert";
import { CommerceOutreachToolContextSchema } from "./outreach-context";

assert.equal(CommerceOutreachToolContextSchema.safeParse({
  purpose: "INITIAL_RECOVERY_OUTREACH",
}).success, true);

assert.equal(CommerceOutreachToolContextSchema.safeParse({
  purpose: "INITIAL_RECOVERY_OUTREACH",
  checkoutRecoveryId: "recovery_456", // no recovery identity in MCP purpose context
}).success, false);

assert.equal(CommerceOutreachToolContextSchema.safeParse({
  purpose: "INITIAL_RECOVERY_OUTREACH",
  outreachAttemptId: "attempt_789", // no attempt identity in MCP purpose context
}).success, false);

assert.equal(CommerceOutreachToolContextSchema.safeParse({
  purpose: "INITIAL_RECOVERY_OUTREACH",
  shopId: "model_forged_shop", // top-level context, not toolContext
}).success, false);

assert.equal(CommerceOutreachToolContextSchema.safeParse({
  purpose: "CONVERSATION",
}).success, false);

assert.equal(CommerceOutreachToolContextSchema.safeParse({}).success, false);
```

**Business/authorisation checks outside Zod:** MCP checks current shop identity, current merchant permissions and tool publication/entitlement at its existing runtime boundary; Background handles attempt lifecycle, checkout recoverability, consent and final send. The proof-specific request in SHARED-005 is separate from the MCP tool-purpose discriminator.

## Dependencies

None.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] The exact one-field schema and inferred type compile and export from the existing `/commerce` package entrypoint.
- [ ] The valid purpose-only object passes. Missing/wrong purpose, extra shop/recovery/attempt keys fail structural parsing.
- [ ] No new MCP envelope, attempt/recovery identity lookup, policy snapshot, HMAC, AI business rules or provider client is added to Shared.
- [ ] Existing conversation assertions, tool inputs/outputs and generic result envelope remain unmodified.

## Validation

- [ ] Run the declared `typecheck`, `test` and `build` scripts in Shared (or record any unavailable command as unverified).
- [ ] Run `src/commerce/contracts.test.ts` cases including the added fixtures and unchanged existing cases.
- [ ] Run `git diff --check` and verify the `/commerce` export in generated package output.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation pass, complete the task report, set task to `review`, return evidence to `moda_architect` and **STOP**. Do not self-accept or start dependent tasks.

## Implementation Notes

Implement the specified source and export only. Any mismatch with the existing private ingress header format must be reported to the architect, not resolved by putting checkout or attempt identities into this purpose-only contract.

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

Escalate any unexpected cross-repository contract/security gap to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only. No implementation accepted.

### Reviewed Files

Relevant October 29, 2026 code snapshot and task definition; no implementation source changes reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through the canonical launcher only after all dependency task YAMLs are Complete.
