---
id: ARCH-052-BACKGROUND-014
architecture_id: ARCH-052
title: Preserve WooCommerce coupon restriction presence without personal data
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 33
executor: copilot
claimed_at: 2026-10-31T04:00:53Z
attempt: 1
depends_on: []
enables:
  - ARCH-052-MCP-002
  - ARCH-052-SYSTEM-TEST-002
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-052-BACKGROUND-014 — Preserve Woo coupon restriction-presence evidence

## Architecture

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**: no local task Git branch, commit, running agent or live shop access is claimed.

## Objective

Make existing WooCommerce coupon snapshots sufficient to distinguish **verified absence** of customer/extension restrictions from **unobserved or present** restrictions, without storing customer email addresses, changing the coupon catalogue schema or calling WooCommerce during outreach.

## Context

Inspected `moda-interact-background/src/providers/woo-coupon-normalization.ts` in the 30 October 18:09 workspace: it persists `individualUse`, `usageLimitPerUser`, item/category IDs, `maximumUsageItems` and expiry facts, but **drops** `email_restrictions` and coupon `meta_data` entirely. MCP-002 cannot infer that absent snapshot keys mean unrestricted coupons. Woo REST `email_restrictions` is an array of customer email addresses and `meta_data` may contain sensitive custom values; neither belongs in the catalogue snapshot or logs. A simple safe presence/unknown signal is sufficient for deterministic eligibility; native Woo checkout still decides redemption.

## Scope

- Modify **only** `moda-interact-background/src/providers/woo-coupon-normalization.ts`, its existing provider-sync unit fixtures and narrowly related tests. Reuse the current `providerSnapshot` JSON field on `ShopifyDiscount` and the existing Woo sync lifecycle; **no Prisma change, migration, separate table, API route, extension call or Shared wire contract**.
- Extract **presence flags only**, without persisting or logging the original restrictions, from canonical Woo REST coupon response:
  - `emailRestrictionsPresent: boolean | null`: `false` only when the source field is an actual empty array; `true` when it is a nonempty array of strings; `null` when missing, malformed, oversized or ambiguous.
  - `uninspectedMetadataPresent: boolean | null`: `false` only when the provider explicitly supplied an empty `meta_data` array; `true` for a nonempty array (do not inspect/store keys or values); `null` when absent, malformed or oversized.
  - Existing `maximumUsageItems` and other bounded restrictions remain **unchanged**, including `null` for unknown. Do not silently discard source-specific restrictions or convert missing into `false`.
- On any ambiguous/oversized source field, retain `null` and record only an existing bounded, non-PII issue (`optional_field_ignored`) referencing the **field name**, never addresses or metadata values. Do not fail the whole catalogue sync for one optional field; keep provider identity/fatal response rules unchanged.

## Out of Scope

No Shopify GraphQL changes, no new coupon proof service, no Woo hook/plugin alteration, customer identity lookup, customer contact capture, checkout mutation, cross-tenant provider read, new Shared exports or changes to currently claimed `ARCH-049-BACKGROUND-003`, `ARCH-052-MCP-005`, `ARCH-052-SHOPIFY-001`.

## Requirements

- `false` requires a **source-observed empty array**, **not** the absence of a property or an empty customer email field synthesized by the caller. `true` is a restriction-presence signal, **not** a list of allowed emails or a decision that the shopper qualifies. Any `true` or `null` flag forces MCP-002 to report a customer/extension restriction uncertainty and prevents Background-010 from declaring full eligibility without an approved source proof (not added by this initiative). `false` is only the absence of that specific flag, never a guarantee that no plugin hook can reject a coupon.
- Data minimisation: `providerSnapshot` must contain only the two booleans/null plus existing safe coupon projection. Do not store `email_restrictions`, `meta_data`, emails, customer IDs, arbitrary metadata keys/values or raw provider errors in the snapshot, tests' recorded fixtures, logs or persisted attempts. In test fixtures use synthetic values; check serialized snapshots explicitly **do not contain** the synthetic addresses or metadata values.
- Keep existing snapshot compatibility for the current development-only catalogue; no backfill, adapters or new versions. Provider truth at cart redemption stays with WooCommerce and ARCH-053.
- `@modainteract/moda-interact-shared/logging` remains the generic logger; propagate unexpected errors, keep the optional-field issue count bounded and log no PII.

## Work Items

- [ ] Add and normalize the two nullable presence flags without copying source arrays to `providerSnapshot`.
- [ ] Preserve existing coupon identity, code deliverability, bounds, source status, selection flags and all other normalized restrictions.
- [ ] Add focused tests for empty, nonempty, missing, malformed and oversized restriction arrays and absence of sensitive bytes in saved snapshots/logs.
- [ ] Run owning repository's declared focused tests, changed-file lint, build and `git diff --check`, then record actual execution results.

## Interfaces / Contracts

**Internal existing snapshot fields only**, not a published Shared/MCP schema:

```typescript
interface WooCouponRestrictionPresenceSnapshot {
  emailRestrictionsPresent: boolean | null;
  uninspectedMetadataPresent: boolean | null;
}
```

MCP-002 projects true/null to `unrepresentedConditions` reason codes and uses false only as positive evidence that these **two** specific restriction categories are absent. The downstream contract remains `CommerceDiscountConditionFactsSchema` owned by SHARED-011/012. The provider's `individual_use` flag is separate and remains unchanged.

## Dependencies

None. The existing accepted Woo coupon synchronization is reused; do not reopen it.

## Enables

- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Both nullable flags distinguish verified empty arrays from true restrictions and unknown/malformed/overflow, without raw email/metadata persistence.
- [ ] Existing coupon normalization, tenant identity and optional-field issue reporting remain unchanged; no Shopify code or unrelated worker feature changes.
- [ ] MCP-002 can distinguish present/unobserved Woo restrictions from observed absence using these snapshot flags; no live Woo coupon check is required for initial outreach.
- [ ] Synthetic sensitive input values do not appear in serialized snapshot, emitted logging/issue diagnostics or outbound contracts.

## Validation

- [ ] Focused existing Woo coupon normalization/provider sync unit tests and explicit sensitive-input negative assertions.
- [ ] Background declared lint and build scripts; `git diff --check`.
- [ ] Worktree/parent synchronization and submodule evidence in the Completion Report, following `docs/agent-worktree-isolation-policy.md`.

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update only this task's progress/Completion Report, set `status: review`, return evidence to moda_architect and **STOP**. Do not self-accept, modify `_index.md`, start MCP-002, merge or push main.

## Implementation Notes

Use the existing pure normalization helper and tests; keep source editing paths relative to the owning repository. Do not infer optional Woo plugin data from arbitrary metadata. Any broader eligibility verification requirement is an architect decision, not permission to build an external coupon checker.

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

The Woo REST response carries the source field when available; missing is not equivalent to empty.

### Unresolved Issues

None at task definition time.

### Architectural Concerns

Report newly observed provider restriction types or unsafe data requirements to moda_architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation reviewed.

### Reviewed Files

`moda-interact-background/src/providers/woo-coupon-normalization.ts` (30 October 18:09 snapshot), architecture and existing coupon task definitions.

### Validation Reviewed

None for implementation.

### Architecture Conformance

Pending implementation review.

### Follow-up

MCP-002 may begin only after this task and all its other prerequisites are architect-accepted Complete.
