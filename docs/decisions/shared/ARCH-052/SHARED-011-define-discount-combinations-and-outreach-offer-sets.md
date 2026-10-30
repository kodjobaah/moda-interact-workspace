---
id: ARCH-052-SHARED-011
architecture_id: ARCH-052
title: Define combination facts and bounded checkout offer sets
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 15
executor: codex
claimed_at: 2026-10-30T18:59:09Z
attempt: 1
depends_on:
- ARCH-052-SHARED-010
enables:
- ARCH-053-SHARED-003
- ARCH-052-SHARED-012
created: 2026-10-30
updated: 2026-10-30
---

# ARCH-052-SHARED-011 — Define combination facts and bounded checkout offer sets

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Architect coordination task; **portable definition, not materialised**. No branch or runtime implementation has been created by this artifact.

## Objective

Extend the published Commerce discount facts and immutable outreach receipt shape so Background can select up to three source-backed, mutually compatible checkout discounts without inventing a second MCP contract or a discount redemption engine.

## Context

SHARED-009/010 (published 2.7.0) correctly represents eligibility and targeting conditions, but not Shopify combination policy, own tags and discount classes. BACKGROUND-011 preserves some combination metadata in providerSnapshot with `PARTIAL`. Existing checkout template bindings only expose `offer.code` for one code, while the confirmed message receipt is the durable source of historical offers. SHARED-011 is a new implementation rather than rewriting accepted SHARED-009/010 history.

## Scope

- Modify `moda-interact-shared/src/commerce/schemas.ts`, `src/commerce/contracts.test.ts` to add `CommerceDiscountCombinationFactsSchema` and a `combination` member to the existing `CommerceDiscountConditionFactsSchema`; add source-backed `providerDiscountId` to `CommerceDiscountDetailsSchema` (nullable where not observed).
- Create `moda-interact-shared/src/commerce/outreach-checkout-offer-set.ts` and tests; export from the EXISTING `src/commerce/index.ts` entrypoint.
- Add `offer.codes` to `src/recovery-template-bindings.ts` semantic enum and matching tests. It is a single bounded, source-rendered text value, **not** a newly invented template URL/button or an array passed to Meta.
- Add tests proving required fields, invalid values, null-vs-empty semantics, strict unknown-key rejection, three-item bound and exact ordered wire round trips.

## Out of Scope

- No provider queries/Prisma changes, WordPress coupon application, Meta template approval, background offer ranking, hosted API work, new `CommerceToolResultSchema`, alternative product discount set, checkout-link generation or old-version compatibility adapter.

## Requirements

- All schemas must be structural only. No `.refine()` or `.superRefine()` for applicability, Shopify Plus, stacking, customer eligibility, expiry, tenant authorization or coupon amounts.
- Provider-native unknown facts MUST be `null`, not empty/false. Truncation or unsupported Shopify types must remain `PARTIAL` with reason codes; a present partial combination observation is not proof of overall checkout applicability.
- A selected checkout offer set is ordered as sent, limited to 1..3; no additional table, `offerSnapshot.sentOffer` field or Redis-only receipt is introduced. All consumer runtime semantics belong to Background/API.
- The `offer.codes` binding is a provider-grounded, bounded human-readable code list. Preserve `offer.code` for single-code approved registrations; neither binding authorizes use of an unapproved Meta template.

## Work Items

- [ ] Implement the new combination facts shape and source fixtures.
- [ ] Implement the immutable checkout-offer-set wire and stable exports.
- [ ] Add the new semantic key and validate all relevant structured contract tests.
- [ ] Run Shared declared tests/typecheck/build and `git diff --check`.

## Interfaces / Contracts

**Exact additional Zod shape** (place beside `CommerceDiscountConditionFactsSchema` in `src/commerce/schemas.ts`; its `combination` member is REQUIRED, but its source-dependent fields are nullable):

```typescript
export const CommerceDiscountCombinationFactsSchema = z.strictObject({
  discountClasses: z.array(z.enum(["ORDER", "PRODUCT", "SHIPPING"])).max(3).nullable(),
  shopifyPlus: z.boolean().nullable(),
  combinesWith: z.strictObject({
    orderDiscounts: z.boolean().nullable(),
    productDiscounts: z.boolean().nullable(),
    shippingDiscounts: z.boolean().nullable(),
  }).nullable(),
  discountTags: z.array(z.string().min(1).max(128)).max(64).nullable(),
  allowedSameLineProductTags: z.array(z.string().min(1).max(128)).max(64).nullable(),
});
export type CommerceDiscountCombinationFacts =
  z.infer<typeof CommerceDiscountCombinationFactsSchema>;
// ADD inside existing CommerceDiscountConditionFactsSchema:
combination: CommerceDiscountCombinationFactsSchema,
// ADD inside existing CommerceDiscountDetailsSchema beside offer and facts:
providerDiscountId: z.string().min(1).max(191).nullable(),
```

For Woo use `individualUse` already on `CommerceDiscountConditionFactsSchema`; do not invent Shopify class booleans for Woo. Woo `combination` uses all-null fields unless genuinely observed by Woo. `discountClasses` may contain multiple source-reported classes. `shopifyPlus` is sourced from a trusted `shop.plan.shopifyPlus` observation, never inferred from a discount's `tags` or shop name. `CommerceDiscountDetailsSchema.providerDiscountId` comes from the authenticated same-shop persisted provider identity, never from the agent, and is needed to preserve historical Woo redemption identity. Shopify `discountTags` are the discount's **own** `tags`, distinct from the allowlist `combinesWith.productDiscountsWithTagsOnSameCartLine` mapped to `allowedSameLineProductTags`.

**New source-bound immutable receipt format** in `src/commerce/outreach-checkout-offer-set.ts` exported through `@modainteract/moda-interact-shared/commerce`:

```typescript
export const InitialOutreachCheckoutOfferSetSchema = z.strictObject({
  schemaVersion: z.literal("moda.outreach.checkout-offers.v1"),
  offers: z.array(z.strictObject({
    offerId: z.string().min(1).max(191),
    providerDiscountId: z.string().min(1).max(191).nullable(),
    method: z.enum(["CODE", "AUTOMATIC"]),
    code: z.string().min(1).max(128).nullable(),
  })).min(1).max(3),
});
export type InitialOutreachCheckoutOfferSet =
  z.infer<typeof InitialOutreachCheckoutOfferSetSchema>;
```

Positive group example:

```json
{"schemaVersion":"moda.outreach.checkout-offers.v1","offers":[
  {"offerId":"discount-10","providerDiscountId":"woo:coupon:10","method":"CODE","code":"SAVE10"},
  {"offerId":"discount-20","providerDiscountId":"woo:coupon:20","method":"CODE","code":"SHIPFREE"}
]}
```

Shared validates the structure only: Background verifies method/code consistency, unique offer IDs, selected shop, source identity, merchant mode, pairwise combination policy and current send permission. API verifies the same immutable confirmed receipt chain before projecting Woo restoration data. No model-generated code or provider ID may enter this structure. A `providerDiscountId:null` cannot be passed as a verified Woo coupon. Do not replace existing `CommerceOfferSchema`, MCP tool dictionaries or the generic result wrapper.

## Dependencies

- ARCH-052-SHARED-010

## Enables

- ARCH-053-SHARED-003
- ARCH-052-SHARED-012

## Acceptance Criteria

- [ ] Contract fixtures cover Shopify Plus tri-state, pairwise mutual class booleans and own/allowed tag distinction, providerDiscountId nullable vs authoritative, Woo individualUse nullable, negative/partial combination facts and array bound 1..3.
- [ ] One canonical checkout offer set is imported by Background and API; 2.7.0 contract history remains unchanged.
- [ ] No business rules are hidden in Zod; source-specific rules remain explicit in consumers.

## Validation

- [ ] Shared focused contract test and TypeScript inference tests.
- [ ] Shared declared typecheck, build and export smoke test.
- [ ] `git diff --check`

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Not started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No production compatibility is required; all required source provenance remains available for implementing agents to verify.

### Unresolved Issues

None at definition time.

### Architectural Concerns

Any source contract/deployment gap must be escalated rather than patched locally.

## Architect Review

### Review Status

Pending.

### Review Notes

New multi-discount feature task; no implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

No implementation validation yet.

### Architecture Conformance

Pending implementation and review.

### Follow-up

None.
