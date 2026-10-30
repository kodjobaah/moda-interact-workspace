---
id: ARCH-053-SHARED-003
architecture_id: ARCH-053
title: Define offer-aware Woo restore resolver v2 contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 22
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-SHARED-001
enables:
- ARCH-053-SHARED-002
created: 2026-10-30
updated: 2026-10-30
---

# ARCH-053-SHARED-003 — Define offer-aware Woo restore resolver v2 contracts

## Architecture

`ARCH-053` — `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`, coordinated by `moda_architect`. Defined but **not materialised**; no branch, worktree, commit, push or acceptance is claimed.

## Objective

Define a **second, explicitly versioned restore-resolver wire response** carrying one authenticated, confirmed outreach offer for a Woo checkout, without changing the published v1 response or making Shared responsible for coupon eligibility.

## Context

`ARCH-053-SHARED-001` defines strict `woo.restore.resolve.v1` request/response and `woo.cart-restore.v1` original coupons. That immutable original snapshot is NOT the source of an ARCH-052 recommended coupon. The initial outbound attempt and its provider-confirmed `ConversationMessage.content.recoveryPromise` provide the recommendation evidence; extracting/authorising it belongs to API-003. A v1 response is strict, so adding `outreachOffer` to v1 would break existing WooCommerce-002 consumers. Use **v2 opt-in** for the extra data.

## Scope

Change only these `moda-interact-shared` repository files (relative paths):

- **Create** `src/woocommerce/outreach-offer.ts`: the exact code in Interfaces / Contracts.
- **Update** `src/woocommerce/index.ts`: explicit re-exports of new schemas, inferred types and version constant while preserving all SHARED-001 exports.
- **Create** `src/woocommerce/outreach-offer.test.ts`: structural and version-selection tests.
- **Create** `src/woocommerce/__fixtures__/woo-restore-outreach-v2.json`: golden positive resolver fixture below.
- **Update** `package.json`: include only the new fixture under `files` and export `./woocommerce/outreach-offer-fixtures` to the JSON file; do **not** bump or publish package version.

Re-use the existing `./woocommerce` package entrypoint and existing `tsup.config.ts` entry from SHARED-001; do **not** add another runtime entrypoint. Consumer API/WooCommerce tasks remain separate.

## Out of Scope

No business coupon proof, no interpretation of a sent message, no API route, no Woo cart calls, no ARCH-052 dynamic discount discovery, no new database table and no runtime logging in Shared.

## Requirements

- The v2 resolver request has the **same** recoveryId/token constraints as V1, but `schemaVersion: 'woo.restore.resolve.v2'`. No shop ID, product input, coupon input, message ID or customer data from the caller.
- The v2 positive response repeats the **v1 authorised recovery identity and original supported snapshot**, and adds **one** `outreachOffer` discriminated union. The union contains no original coupons; original coupons remain at `snapshot.appliedCouponCodes`.
- `CHECKOUT_CODE` carries the **single recommended code** and provider ID. `CHECKOUT_AUTOMATIC` carries provider ID but **no code**. `ALTERNATIVE_PRODUCT` is deliberately not a checkout coupon. `NONE` carries a bounded reason (`NO_CONFIRMED_OFFER|UNVERIFIABLE`); it never means the original snapshot had no coupons.
- Zod checks **shape only**: strict keys, version literals, Unicode control-character exclusion, max lengths, the union's required fields. WooCommerce alone decides whether code is valid, applies to the basket, stacks, remains in-date or affects payable total. No `.refine`, `.superRefine`, `.check` or `.transform` for business policy.
- The existing v1 schema must still reject v2's extra fields; v2 is used only when a v2 request was explicitly submitted. No silent version downgrade or publisher/consumer mismatch.

### Repository / execution safeguards

- Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the launcher preparation packet and the parent ARCH-053 architecture before claiming. Work from dedicated, synchronized mirrored task worktrees; record both physical paths, initial SHAs and validation in the Completion Report. A snapshot does not establish the developer's current branch/status.
- Only change the **permitted owning-repository files** in Scope and this task's own authorised task metadata/Completion Report. No `_index.md`, no unrelated code, no other agent's task, no production WhatsApp activation, no merge/push to `main`.
- Node services use `@modainteract/moda-interact-shared/logging`. Log bounded identifiers and event codes, not raw URLs, bearer tokens, coupon codes, full customer data, original message text or unbounded provider bodies. Log and propagate unexpected dependency errors to the owner; never silently swallow them. PHP uses existing plugin-safe diagnostics, not a new generic logger.
- Keep checkout restoration read-only in the hosted API and cart-local in WooCommerce. Never have PHP query Moda PostgreSQL/Redis or an API handler change a visitor cart. Never create a new discount, extend an expired coupon, use ARCH-052 discovery code, bypass merchant consent/STOP/order/final provider gates or impose a cross-generation outreach cap.
- When the specified receipt/provider contract is absent, conflicting or untestable, **stop and return the gap to moda_architect**; do not invent an approximation, copy a Shared schema locally or broaden the task to another repo. System-test tasks are terminal and may not gate implementation tasks.


## Work Items

- [ ] Implement the exact v2 request, response and offer union schemas below, reusing SHARED-001 fields via `.omit(...).safeExtend(...)`.
- [ ] Export types and schemas from `@modainteract/moda-interact-shared/woocommerce`, retaining all v1 exports.
- [ ] Add complete fixture and positive/negative tests, including structural acceptance of codes even when business-ineligible.

## Interfaces / Contracts

**Create `src/woocommerce/outreach-offer.ts` with these exact public declarations:**

```typescript
import { z } from "zod";
import {
  WooRestoreResolveRequestV1Schema,
  WooRestoreResolveResponseV1Schema,
} from "./contracts.js";

export const WOO_RESTORE_RESOLVE_OFFER_VERSION =
  "woo.restore.resolve.v2" as const;

const BoundedCouponCodeSchema = z.string().min(1).max(128)
  .regex(/^[^\p{Cc}]+$/u);
const ProviderDiscountIdSchema = z.string().min(1).max(191)
  .regex(/^[^\p{Cc}]+$/u);

export const WooRestoreOutreachOfferV1Schema = z.discriminatedUnion("kind", [
  z.strictObject({
    kind: z.literal("NONE"),
    reason: z.enum(["NO_CONFIRMED_OFFER", "UNVERIFIABLE"]),
  }),
  z.strictObject({
    kind: z.literal("CHECKOUT_CODE"),
    code: BoundedCouponCodeSchema,
    providerDiscountId: ProviderDiscountIdSchema,
  }),
  z.strictObject({
    kind: z.literal("CHECKOUT_AUTOMATIC"),
    providerDiscountId: ProviderDiscountIdSchema,
  }),
  z.strictObject({
    kind: z.literal("ALTERNATIVE_PRODUCT"),
  }),
]);
export type WooRestoreOutreachOfferV1 =
  z.infer<typeof WooRestoreOutreachOfferV1Schema>;

export const WooRestoreResolveOfferRequestV2Schema =
  WooRestoreResolveRequestV1Schema.omit({ schemaVersion: true })
    .safeExtend({ schemaVersion: z.literal(WOO_RESTORE_RESOLVE_OFFER_VERSION) });
export type WooRestoreResolveOfferRequestV2 =
  z.infer<typeof WooRestoreResolveOfferRequestV2Schema>;

export const WooRestoreResolveOfferResponseV2Schema =
  WooRestoreResolveResponseV1Schema.omit({ schemaVersion: true })
    .safeExtend({
      schemaVersion: z.literal(WOO_RESTORE_RESOLVE_OFFER_VERSION),
      outreachOffer: WooRestoreOutreachOfferV1Schema,
    });
export type WooRestoreResolveOfferResponseV2 =
  z.infer<typeof WooRestoreResolveOfferResponseV2Schema>;
```

This intentionally **does not** modify `WooRestoreResolveResponseV1Schema` or introduce generic `coupon?: string` on the original snapshot. Retain the existing browser-safe `woocommerce/index` entry and add to `index.ts` explicit named exports/types for every new `WooRestore*` plus `WOO_RESTORE_RESOLVE_OFFER_VERSION`.

**Package JSON export for golden fixtures only:**

```json
{
  "./woocommerce/outreach-offer-fixtures":
    "./src/woocommerce/__fixtures__/woo-restore-outreach-v2.json"
}
```

**`woo-restore-outreach-v2.json` — complete golden fixture:**

```json
{
  "request": {
    "schemaVersion": "woo.restore.resolve.v2",
    "recoveryId": "recovery_456",
    "token": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
  },
  "eligibleResponse": {
    "schemaVersion": "woo.restore.resolve.v2",
    "status": "eligible",
    "recoveryId": "recovery_456",
    "checkoutKey": "woo-example-checkout",
    "snapshot": {
      "schemaVersion": "woo.cart-restore.v1",
      "kind": "supported",
      "appliedCouponCodes": ["SAVE10"],
      "lines": [
        {"productId": "101", "quantity": 2},
        {"productId": "202", "variationId": "207", "quantity": 1,
          "attributes": {"attribute_pa_color": "navy"}}
      ]
    },
    "outreachOffer": {
      "kind": "CHECKOUT_CODE",
      "code": "EXTRA15",
      "providerDiscountId": "woo-discount-915"
    }
  }
}
```

The fixture token is an **inert shape vector**, not an authentication example; API-003 must test real constant-time token checks using API-002. `NONE`, `CHECKOUT_AUTOMATIC` and `ALTERNATIVE_PRODUCT` are separate strictly parsed fixtures in tests. For example `{"kind":"NONE","reason":"UNVERIFIABLE"}` is valid; `{"kind":"CHECKOUT_AUTOMATIC","code":"EXTRA15","providerDiscountId":"id"}` must be rejected structurally.

**Ownership:** Shared publishes the type; API-003 produces v2 from confirmed outbound evidence; WooCommerce-007 consumes v2 server-side on the shopper's confirmed POST. The PHP implementation must check canonical JSON fixtures because it cannot import Node modules.

## Dependencies

- `ARCH-053-SHARED-001` — accepted implementation of the base restore/resolver schemas.

## Enables

- `ARCH-053-SHARED-002` — one publication gate for the accepted v1 + v2 Shared exports.

## Acceptance Criteria

- [ ] All exact exports compile and v1 remains unchanged/strict; v1 and v2 cannot be confused.
- [ ] Both `CHECKOUT_CODE` and `CHECKOUT_AUTOMATIC` parse with precisely the declared fields; `ALTERNATIVE_PRODUCT` cannot carry a coupon code.
- [ ] Missing coupon, oversized code/provider ID, unexpected keys, unknown variants or wrong versions fail parse; a structurally valid but expired coupon is **not** rejected by Zod.
- [ ] Original coupon list remains only under `snapshot.appliedCouponCodes`.
- [ ] No runtime dependency on Prisma, WordPress or the Backend, and no package publication in this task.

## Validation

- [ ] `npm run typecheck`, `npm test`, `npm run build` in Shared (commands actually declared in snapshot)
- [ ] Browser-safe `@modainteract/moda-interact-shared/woocommerce` import/export and golden-fixture smoke tests
- [ ] `git diff --check`

## Stop Condition

When all defined Work Items, Acceptance Criteria and Validation are satisfied, update only this task's authorized metadata and Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin Enabled tasks, self-accept, create new tasks, modify a sibling repository or merge/push main.

## Implementation Notes

Use Zod 4 (`safeExtend`) and the established TypeScript `.js` ESM import convention. Do not duplicate the v1 ID/token/snapshot schema or put billing/customer data in the v2 response. Stop after this task's Completion Report enters review.

## Completion Report

### Status

Not Started — portable task definition, not claimed.

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not run. Report exact commands, results and any environment blockers after execution.

### Deviations

None.

### Assumptions

Defined from the 2026-10-30 uploaded snapshot. Re-read current task and repository HEAD after launcher preparation.

### Unresolved Issues

None claimed resolved. See explicit dependency/receipt gates above.

### Architectural Concerns

Escalate contract or ownership gaps instead of inventing a new transport or persistence location.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
