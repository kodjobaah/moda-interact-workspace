---
id: ARCH-052-SHARED-013
architecture_id: ARCH-052
title: Add source-observed subtotal threshold currency to discount condition facts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 23
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-012
enables:
- ARCH-052-SHARED-014
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-SHARED-013 — Add subtotal threshold currency to condition facts

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Portable task definition; defined but not materialised.** The developer's Git worktrees, task branch, commit and push are not available to this architect session.

## Objective

Extend the existing Shared Commerce discount condition-facts shape with **one required nullable currency field** identifying the denomination of `minimumSubtotal`/`maximumSubtotal`, without changing business eligibility semantics or the accepted 2.8.1 artifact.

## Context

SHARED-011 was architect accepted and SHARED-012 published `@modainteract/moda-interact-shared@2.8.1` before the discount-eligibility task refinement. The published `CommerceDiscountConditionFactsSchema` contains decimal `minimumSubtotal`/`maximumSubtotal` but **no currency for those thresholds**. `discountCurrency` cannot be assumed to represent threshold currency, because it describes the discount amount's currency and may be null for percentage offers. Background cannot compare a bare decimal threshold to a checkout subtotal safely. Do **not** rewrite SHARED-011, SHARED-012, the npm 2.8.1 tarball or accepted Completion Reports.

## Scope

- Repository `moda-interact-shared/`; change `src/commerce/schemas.ts` beside `CommerceDiscountConditionFactsSchema.minimumSubtotal` and `.maximumSubtotal`, and focused `src/commerce/contracts.test.ts` fixtures. Reuse existing `CurrencySchema` imported from `src/commerce/primitives.ts`.
- Preserve the existing named `@modainteract/moda-interact-shared/commerce` entrypoint, Zod strictness, all fields, exported TypeScript inference and the exact generic `CommerceToolResultSchema` envelope. The new field must be available through the existing `CommerceDiscountDetailsSchema.facts`.
- Implement **only the structural contract**, not provider retrieval, shop-currency inference, basket validation or currency conversion. Those are owned by BACKGROUND-013, MCP-002 and BACKGROUND-010.

## Out of Scope

No new tool, REST route, database migration/table, discount/redemption engine, background agent, monetary calculation library, merchant UI, or modification of accepted Shared 011/012 tasks. Do not add business-rule Zod `.refine()`/`.superRefine()`. Do not create a v2 Woo restore response or change the ARCH-053 checkout URL architecture.

## Requirements

- Add **exactly** `subtotalRequirementCurrency: CurrencySchema.nullable()` as a **required property** of `CommerceDiscountConditionFactsSchema`, adjacent to `minimumSubtotal` and `maximumSubtotal`. Do not use `z.optional()`, `z.default()`, inferred values, or rename `discountCurrency`.
- Semantics: a three-letter normalised source-observed currency for the effective minimum and/or maximum merchandise-subtotal requirement; **null** when no effective threshold exists or when the source currency cannot be established. `null` with an effective threshold means eligibility must remain `UNVERIFIABLE` in Background; MCP supplies `THRESHOLD_CURRENCY_UNKNOWN` as an unrepresented reason. Do not make the schema itself infer whether a threshold is effective.
- A provider exposing differing currencies across minimum/maximum conditions must be represented as `null` plus an explicit uncertainty reason by the consumer; one scalar must never falsely certify two different currencies.
- Numeric zeros used by Woo core for absent minimum/maximum limits remain the **consumer's provider-specific policy**, not a Shared Zod policy. A source decimal amount is a string; no float conversion, rounding, locale inference or implied exchange rate is allowed.
- The new field is a structural **breaking addition** to the pre-production Shared wire contract. Preserve versioned, published artifact `2.8.1`; SHARED-014 publishes a later version after acceptance. Consumer pinned versions update independently, no duplicate local schema or old-version compatibility adapter.

## Work Items

- [ ] Insert the required nullable property in `src/commerce/schemas.ts`, re-exporting via the existing declared Commerce schema/type exports without changing other properties.
- [ ] Update all existing `CommerceDiscountConditionFacts` positive fixtures to include `subtotalRequirementCurrency` with either a source currency or `null`; update `CommerceDiscountDetails` nested fixtures.
- [ ] Add negative fixtures: field omitted, invalid lower-case/non-ISO currency, wrong type; include positive fixtures for percentage discount currency-null with threshold currency known, no effective threshold with `null`, effective threshold with unknown currency `null` and `THRESHOLD_CURRENCY_UNKNOWN` reason, and one source-currency mismatch represented as `null`.
- [ ] Run Shared declared tests, typecheck, build and `git diff --check`; complete the task's report, worktree evidence and commit evidence, then STOP for architect review. **Do not publish from this task.**

## Interfaces / Contracts

Canonical owner: `moda-interact-shared`. Published entrypoint after SHARED-014: `@modainteract/moda-interact-shared/commerce`. Producer: MCP-002. Consumers: Background-010/008 and existing approved Commerce discount readers. Exact TypeScript/Zod delta to existing schema:

```typescript
// Within the existing CommerceDiscountConditionFactsSchema = z.strictObject({ ... })
minimumSubtotal: MoneySchema.nullable(),
maximumSubtotal: MoneySchema.nullable(),
subtotalRequirementCurrency: CurrencySchema.nullable(),
```

**Illustrative facts fragments** (not complete `CommerceDiscountConditionFacts` payloads):

```json
{ "minimumSubtotal": "100.00", "maximumSubtotal": null, "subtotalRequirementCurrency": "GBP", "discountCurrency": null, "unrepresentedConditions": [] }
```

```json
{ "minimumSubtotal": "100.00", "maximumSubtotal": null, "subtotalRequirementCurrency": null, "discountCurrency": null, "unrepresentedConditions": ["THRESHOLD_CURRENCY_UNKNOWN"] }
```

Source amount and currency from Shopify `DiscountMinimumSubtotal.greaterThanOrEqualToSubtotal` (`MoneyV2.amount` and `.currencyCode`) are captured by BACKGROUND-013. For Woo core, MCP-002 may use an independently authenticated shop currency only where documented Woo semantics prove it is the threshold denomination. No producer may assume `discountCurrency` is threshold currency.

## Dependencies

- ARCH-052-SHARED-012 — accepted published 2.8.1 combination/offer-set baseline.

## Enables

- ARCH-052-SHARED-014 — release corrected Shared condition fact to MCP and Background.

## Acceptance Criteria

- [ ] Source-compatible decimal and currency field is structurally validated with required-nullable semantics.
- [ ] Omitted new property fails the strict detail schema; `null` and valid ISO currency strings pass according to existing `CurrencySchema`.
- [ ] No eligibility, exchange-rate, Shopify Plus, stacking or coupon lifecycle business rule is embedded in Zod.
- [ ] Existing exports and unrelated Commerce/ARCH-053 contracts remain unchanged; all declared validation passes and no publication occurred.

## Validation

- [ ] Focused updated Commerce contract fixtures and dependent Shared test suites.
- [ ] Repository declared Shared typecheck and build.
- [ ] `git diff --check` and completion report with launcher-resolved worktree/branch, implementation SHA, synchronization and relevant submodule evidence.

## Stop Condition

After Work Items, Acceptance Criteria and Validation, move **this task only** to `review`, record the Completion Report and STOP for `moda_architect`. Do not publish a package, begin the enabled task, merge/push main or modify domain `_index.md`.

## Implementation Notes

Use the existing Shared exports. Unexpected errors must not be swallowed; use the Shared logger for runtime code that requires structured logging. Keep sensitive coupon/customer information out of logs. No deployment keys or environment assumptions are needed for a structural schema change.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Pre-production breaking rollout permitted; existing published 2.8.1 remains immutable.

### Unresolved Issues

None at definition.

### Architectural Concerns

Return any newly discovered cross-repository contract mismatch to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None.
