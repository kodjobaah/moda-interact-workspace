---
id: ARCH-052-SHARED-005
architecture_id: ARCH-052
title: Define a typed provider discount-evidence payload for on-demand MCP calls
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

# ARCH-052-SHARED-005: Define a typed provider discount-evidence payload for on-demand MCP calls

## Architecture

Architecture ID: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`.

Portable task definition: **defined but not materialised**. No real developer branch, worktree, commit or push is asserted.

## Objective

Create the **exact structural wire contract** for a targeted discount-evidence request and response exchanged by MCP and the provider-backed discount capability. The agent invokes this only when it needs evidence; it is **not** a mandatory catalogue-wide eligibility scan. No business rules are implemented in Zod.

## Context

The snapshot has `CommerceEvidenceSchema`, but that contract requires a conversational `turn`, `grantId` and `releaseId`; initial outreach has no inbound conversation turn. `src/recovery-offer-proof.ts` and this task's proposed exports do not yet exist. `CommerceToolResultSchema` already supplies the generic MCP success/error envelope; it is not replaced.

## Scope

- Create the exact browser-safe module and package subpath described under Interfaces / Contracts.
- Define only the identity, target, outcome and evidence **data shapes** shown below. Maintain exact naming and nullability.
- Add schema-only contract fixtures and type inference checks. Do not implement discount eligibility, savings computation, expiry comparisons, store-host checks or offer selection in Shared.
- Document consuming runtime responsibilities in the owning MCP/Commerce/WooCommerce tasks; do not implement them here.

## Out of Scope

- No bulk discount scan, provider HTTP call, database access, coupon creation/application, AI decision or new MCP result envelope.
- No pre-production migration, historical compatibility adapter, new table/column, private HMAC scheme or conversation-runner change.

## Requirements

- **Zod boundary:** types, required/nullable fields, literals, discriminants, lexical formats already provided by existing Shared primitives and unknown-key rejection only. Do not introduce `.refine()`, `.superRefine()`, `.transform()` or `.check()` for business rules.
- **MCP/provider boundary:** independently confirm the requested discount and target belong to the authenticated shop/recovery; decide eligibility, applicable code/method pairing, supported restrictions, savings, evidence freshness and whether evidence authorises a marketing claim. These checks are **not** part of `RecoveryDiscountProofResultSchema`.
- Existing conversation tool inputs and the generic `commerce.v1` success/error envelope remain unchanged.
- Follow the mirrored dedicated-worktree and start-of-attempt evidence rules in `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and the prepared launcher packet. No unsafe logs, silent exception swallowing or competing logger; use Shared structured logging if runtime logging is introduced.

## Work Items

- [ ] Create `moda-interact-shared/src/recovery-offer-proof.ts` with the exact source below.
- [ ] Add `recovery-offer-proof` to `moda-interact-shared/tsup.config.ts` and `moda-interact-shared/package.json` exports with the exact entrypoint below.
- [ ] Add `moda-interact-shared/src/recovery-offer-proof.test.ts` with the positive/negative schema cases below.
- [ ] Run the repository's declared `typecheck`, `test` and `build` scripts. Record any unavailable validation, not a substitute check.

## Interfaces / Contracts

**Create `moda-interact-shared/src/recovery-offer-proof.ts` exactly as follows:**

```typescript
import { z } from "zod";
import {
  IdSchema,
  HashSchema,
  DateSchema,
  CurrencySchema,
  MoneySchema,
} from "./commerce/primitives";

export const RecoveryDiscountTargetSchema = z.discriminatedUnion("kind", [
  z.strictObject({
    kind: z.literal("CHECKOUT"),
  }),
  z.strictObject({
    kind: z.literal("ALTERNATIVE_PRODUCT"),
    productId: IdSchema,
    variantId: IdSchema.nullable(),
  }),
]);
export type RecoveryDiscountTarget =
  z.infer<typeof RecoveryDiscountTargetSchema>;

const RecoveryProofIdentityShape = {
  schemaVersion: z.literal(1),
  shopId: IdSchema,
  checkoutRecoveryId: IdSchema,
  outreachAttemptId: IdSchema,
  catalogueDiscountId: IdSchema,
  providerDiscountId: IdSchema,
  checkoutFingerprint: HashSchema,
  target: RecoveryDiscountTargetSchema,
};

export const RecoveryDiscountProofRequestSchema = z.strictObject({
  ...RecoveryProofIdentityShape,
});
export type RecoveryDiscountProofRequest =
  z.infer<typeof RecoveryDiscountProofRequestSchema>;

export const RecoveryEligibleDiscountProofSchema = z.strictObject({
  ...RecoveryProofIdentityShape,
  checkedAt: DateSchema,
  outcome: z.literal("eligible"),
  method: z.enum(["CODE", "AUTOMATIC"]),
  code: z.string().nullable(),
  verifiedDescription: z.string(),
  currency: CurrencySchema.nullable(),
  savings: MoneySchema.nullable(),
  expiresAt: DateSchema,
  verifiedConditions: z.array(z.string()),
});

export const RecoveryNonEligibleDiscountProofSchema = z.strictObject({
  ...RecoveryProofIdentityShape,
  checkedAt: DateSchema,
  outcome: z.enum([
    "ineligible", "unsupported", "unavailable", "stale",
  ]),
  reasonCodes: z.array(z.string()),
});

export const RecoveryDiscountProofResultSchema = z.union([
  RecoveryEligibleDiscountProofSchema,
  RecoveryNonEligibleDiscountProofSchema,
]);
export type RecoveryDiscountProofResult =
  z.infer<typeof RecoveryDiscountProofResultSchema>;
```

**Package entrypoint additions (do not replace the existing export map):**

```typescript
// moda-interact-shared/tsup.config.ts — add to entry
"recovery-offer-proof": "src/recovery-offer-proof.ts",
```

```json
{
  "./recovery-offer-proof": {
    "types": "./dist/recovery-offer-proof.d.ts",
    "import": "./dist/recovery-offer-proof.js"
  }
}
```

`commerceToolResultSchema(RecoveryDiscountProofResultSchema)` remains the mechanism for checking an MCP `status: "OK"` result's `data`. Tool failures continue using the existing `CommerceToolResultSchema` `status: "ERROR"` branch.

**Illustrative, structurally valid request:**

```json
{
  "schemaVersion": 1,
  "shopId": "shop_123",
  "checkoutRecoveryId": "recovery_456",
  "outreachAttemptId": "attempt_789",
  "catalogueDiscountId": "discount_123",
  "providerDiscountId": "provider_123",
  "checkoutFingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "target": { "kind": "CHECKOUT" }
}
```

**Illustrative complete eligible result:**

```json
{
  "schemaVersion": 1,
  "shopId": "shop_123",
  "checkoutRecoveryId": "recovery_456",
  "outreachAttemptId": "attempt_789",
  "catalogueDiscountId": "discount_123",
  "providerDiscountId": "provider_123",
  "checkoutFingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "target": { "kind": "CHECKOUT" },
  "checkedAt": "2026-10-29T18:00:00.000Z",
  "outcome": "eligible",
  "method": "CODE",
  "code": "RUN20",
  "verifiedDescription": "20% off running shoes",
  "currency": "GBP",
  "savings": "20.00",
  "expiresAt": "2026-10-29T18:01:00.000Z",
  "verifiedConditions": ["PRODUCT_MATCH"]
}
```

**Illustrative complete non-eligible result:**

```json
{
  "schemaVersion": 1,
  "shopId": "shop_123",
  "checkoutRecoveryId": "recovery_456",
  "outreachAttemptId": "attempt_789",
  "catalogueDiscountId": "discount_123",
  "providerDiscountId": "provider_123",
  "checkoutFingerprint": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "target": {
    "kind": "ALTERNATIVE_PRODUCT",
    "productId": "product_123",
    "variantId": null
  },
  "checkedAt": "2026-10-29T18:00:00.000Z",
  "outcome": "unsupported",
  "reasonCodes": ["PROVIDER_RESTRICTION_UNKNOWN"]
}
```

**Business checks explicitly delegated to the owning runtime (not Zod):**

| Rule | Owning runtime |
|---|---|
| `shopId`, recovery, attempt and target represent the current authorised operation | MCP |
| Request/result IDs and fingerprint are equal; no cross-shop contamination | MCP/provider adapter |
| A `CODE` offer has a real redeemable code, an `AUTOMATIC` offer has no code | Provider-specific eligibility implementation |
| Dates describe an acceptable evidence lifetime; selected discount still current | MCP/Background send boundary |
| Savings reflect actual provider rules, not an AI guess | Provider-specific eligibility implementation |
| Claiming “eligible” is supported by known conditions; unsupported restrictions fail safely | Provider-specific eligibility implementation |

These rules **must not be reintroduced as Zod refinements**. In particular, a structurally valid `eligible` result with `method: "CODE", code: null` may pass the schema but **must not** be authorised for sending by the MCP/provider business layer.

## Dependencies

None.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] Both schemas and inferred TypeScript types exactly match the specified module; existing `CommerceEvidenceSchema` is untouched.
- [ ] A full `CHECKOUT` and `ALTERNATIVE_PRODUCT` request and both result branches parse.
- [ ] Missing IDs, unknown fields, invalid discriminants, missing alternative `productId`, malformed `checkoutFingerprint` and missing `checkedAt` fail structural parsing.
- [ ] No business-rule `.refine`, `.superRefine`, `.transform` or `.check` is introduced; `CODE`/code consistency, date ordering and identity match are verified in the owning runtime rather than the Shared schema.
- [ ] Generic MCP success/error envelope and conversation contracts remain unchanged.

## Validation

- [ ] `npm run typecheck`, `npm test`, `npm run build` in the Shared repository (or record any environmental limitation).
- [ ] Structural fixtures using `safeParse` and `commerceToolResultSchema` covering the specified valid and invalid cases.
- [ ] `git diff --check`; confirm browser-safe subpath export in generated package and no Node-only dependencies.

## Stop Condition

After Work Items, Acceptance Criteria and Validation have passed, fill the Completion Report, set `status: review`, return the mirrored task-branch evidence to `moda_architect`, and **STOP**. Do not start dependent tasks or mark your own task Complete.

## Implementation Notes

The source snippet is **normative for this review draft**: do not rename fields, invent proof statuses, add an additional result envelope, or move business policy into the schema. If a current source conflict prevents it, report the exact conflict for architect review instead of choosing a replacement contract.

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

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
