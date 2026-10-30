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
status: complete
priority: 15
executor: null
claimed_at: null
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

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Implementation is materialised on the dedicated task branch and submitted for Architect review.

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

- [x] Implement the new combination facts shape and source fixtures.
- [x] Implement the immutable checkout-offer-set wire and stable exports.
- [x] Add the new semantic key and validate all relevant structured contract tests.
- [x] Run Shared declared tests/typecheck/build and `git diff --check`.

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

- [x] Contract fixtures cover Shopify Plus tri-state, pairwise mutual class booleans and own/allowed tag distinction, providerDiscountId nullable vs authoritative, Woo individualUse nullable, negative/partial combination facts and array bound 1..3.
- [x] One canonical checkout offer-set schema is exported through the existing Commerce entrypoint for Background and API; 2.7.0 contract history remains unchanged.
- [x] No business rules are hidden in Zod; source-specific rules remain explicit in consumers.

## Validation

- [x] Shared focused contract tests and TypeScript inference tests passed (23 tests).
- [x] Shared declared typecheck, build and export smoke test passed.
- [x] Shared declared test suite passed: 401 passed, 1 skipped (TEST_REDIS_URL is not configured).
- [x] `git diff --check` passed.

## Stop Condition

After the specified work, validation and acceptance criteria pass, update this task's Work Items and Completion Report, set status to `review`, hand back the implementation branch and evidence, and STOP. Do not self-accept, implement enabled tasks, modify other task/index files or push main.

## Implementation Notes

Use the launcher-resolved dedicated mirrored parent/implementation worktrees and shared structured logger. All unexpected errors must be logged with bounded identifiers and propagated to the owning failure/retry boundary. Never log coupon codes, customer information, bearer tokens or raw checkout URLs. Use relative workspace edit paths; do not touch `_index.md`.

## Completion Report

### Status

Implementation accepted by the architect. Attempt 1.

### Files Changed

- `src/commerce/schemas.ts`
- `src/commerce/outreach-checkout-offer-set.ts`
- `src/commerce/outreach-checkout-offer-set.test.ts`
- `src/commerce/index.ts`
- `src/commerce/contracts.test.ts`
- `src/commerce/tool-contracts.test.ts`
- `src/recovery-template-bindings.ts`
- `src/recovery-template-bindings.test.ts`

### Work Completed

- Added the strict combination facts schema, including nullable source observations and the required combination facts member on discount conditions.
- Added nullable, bounded provider discount identity to discount details.
- Added the strict, versioned checkout offer-set receipt with an ordered 1–3 offer bound and stable type/schema exports from the existing Commerce entrypoint.
- Added `offer.codes` as a single bounded text semantic, with tests ensuring it is not a button URL or an array contract.
- Added focused and entrypoint tests covering source nulls, empty observations, Shopify tri-state and pairwise facts, Woo individual-use, own versus allowed tags, strictness, bounds, exact order-preserving round trips and inferred types.
- Left consumer repositories and historical 2.7.0 contract history unchanged.

### Validation Results

- Focused contract tests: 23 passed.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- `npm run validate:commerce-entrypoints`: passed, including clean-process Commerce and runner imports.
- `npm test`: 401 passed, 1 skipped; the skipped Redis telemetry test requires `TEST_REDIS_URL`.
- `git diff --check`: passed.

### Deviations

None.

### Assumptions

Provider-specific interpretation and offer applicability remain consumer responsibilities. The Shared package exposes one canonical structural receipt contract for consumers.

### Unresolved Issues

None identified.

### Architectural Concerns

None identified during implementation.

### Synchronization and Version Control

- Canonical workspace checkout: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; unchanged.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-SHARED-011`, branch `task/ARCH-052-SHARED-011`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-SHARED-011`, branch `task/ARCH-052-SHARED-011`.
- Shared package checkout began at `origin/main` commit `17cf8d426c46f60d97314ec2d6bc20b957029cd2`; no main merge was performed.
- Recursive submodules: ready; no entries required updates.
- Other task worktrees reused: none.
- Implementation commit: `cba9decf56e6cf22c8973e814c713330412db8c1`.
- Implementation branch push: yes; `origin/task/ARCH-052-SHARED-011` matches commit `cba9decf56e6cf22c8973e814c713330412db8c1`.
- Parent task claim commit: `87513ff6fae710c5c36cc1a1db7ef1b2c4d6af64` (already pushed).
- Parent completion-record commit: `116727dab93a9d4cf1b619ee4211f4046a25521a`; pushed to `origin/task/ARCH-052-SHARED-011`. The local and remote task branch revisions match.
- Main was not modified or pushed.

## Architect Review

### Review Status

Accepted — Attempt 1.

### Review Notes

The implementation matches the task's specified structural contract. Combination facts use the required nullable provider observations and distinguish unknown (`null`) from observed-empty arrays/false values. The required combination member and nullable provider identity are added to the existing strict discount schemas. The checkout-offer receipt is a strict, ordered 1..3 structure, exported through the existing Commerce entrypoint. `offer.codes` is available as a text semantic and remains excluded from URL-button bindings.

The schemas remain structural: source authorization, provider consistency, pairwise applicability and send policy are left to the owning consumers as required. The report's initial VCS push statement was stale; direct branch inspection confirms implementation commit `cba9decf56e6cf22c8973e814c713330412db8c1` and parent report commit `116727dab93a9d4cf1b619ee4211f4046a25521a` are both published on their task branches, and both worktrees are clean. The report has been corrected to record that evidence.

### Reviewed Files

- `moda-interact-shared/src/commerce/schemas.ts`
- `moda-interact-shared/src/commerce/outreach-checkout-offer-set.ts`
- `moda-interact-shared/src/commerce/index.ts`
- `moda-interact-shared/src/recovery-template-bindings.ts`
- Related Commerce contract and template-binding tests.
- This task's Completion Report and task-branch evidence.

### Validation Reviewed

The report records 23 focused contract tests, typecheck, build, Commerce entrypoint validation, the full suite (401 passed, 1 skipped because `TEST_REDIS_URL` is unset), and `git diff --check` as passing. These implementation validations were not rerun during this architect review.

### Architecture Conformance

Accepted. All Work Items and Acceptance Criteria are satisfied. No provider, consumer-runtime, authorization, eligibility, publication, or compatibility work was pulled into this task.

### Follow-up

Mark ARCH-052-SHARED-011 complete. ARCH-053-SHARED-003 is now dependency-ready and may be materialized/claimed; keep ARCH-052-SHARED-012 pending until ARCH-053-SHARED-003 is complete.
