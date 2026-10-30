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
attempt: 1
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-SHARED-006: Define the purpose-only outreach MCP context discriminator

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Task materialised and claimed through the prepared launcher on 2026-10-29. The launcher created the dedicated mirrored task worktrees, synchronized both task branches, initialized the implementation submodules, and pushed the Attempt 1 claim before implementation began.

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

Escalate any unexpected cross-repository contract/security gap to `moda_architect`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 was previously accepted, but review against the current Attempt 9 contract found a material mismatch in the accepted implementation. At implementation commit `29ed192`, `src/commerce/outreach-context.ts` requires `checkoutRecoveryId` and `outreachAttemptId` using `IdSchema`; `src/commerce/contracts.test.ts` treats both as required. The task's normative schema and current architecture require exactly `{ purpose: "INITIAL_RECOVERY_OUTREACH" }` and explicitly reject both identifiers. The prior acceptance is superseded. The `/commerce` export and unchanged generic result envelope are not the issue.

Correction contract: remove both identity fields from the schema/type; add the purpose-only positive fixture and negative fixtures for extra `checkoutRecoveryId`, `outreachAttemptId`, `shopId`, missing purpose and wrong purpose; rerun the task's required Shared validation and report the corrected implementation evidence. Do not add a recovery/attempt lookup or change ownership boundaries.

### Reviewed Files

- Attempt 1 Completion Report, task scope, Acceptance Criteria and Validation.
- Shared implementation branch `task/ARCH-052-SHARED-006` at `29ed192`, clean with a three-file diff from `origin/main`.
- `src/commerce/outreach-context.ts`.
- `src/commerce/index.ts` and `src/commerce/contracts.test.ts`.
- Existing `src/commerce/schemas.ts` and ARCH-052 dependency records.

### Validation Reviewed

The Attempt 1 report records successful typecheck, tests, build, package export and diff checks. Those results do not establish conformance: the source and tests at `29ed192` require identity fields prohibited by the current contract. The correction must rerun the checks listed in Validation.

### Architecture Conformance

The implementation does not conform to the purpose-only SHARED-006 contract or current ARCH-052 boundary because it places recovery and attempt identities in `toolContext`. MCP authorization and current merchant-policy ownership remain unchanged.

### Follow-up

Task returned to `ready`; `executor` and `claimed_at` are clear, and attempt 1 is preserved for the next claim. Reclaim the same task and implement the correction contract above. `ARCH-052-SHARED-003` remains `pending`; no publication or consumer task is promoted.
