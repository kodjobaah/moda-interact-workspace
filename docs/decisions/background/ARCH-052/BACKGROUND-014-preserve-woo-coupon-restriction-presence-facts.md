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
status: review
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

Architecture: `ARCH-052`. Parent: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. Materialised and executed through the canonical task launcher in dedicated mirrored task worktrees; no live shop access or persistent shop changes were made.

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

- [x] Add and normalize the two nullable presence flags without copying source arrays to `providerSnapshot`.
- [x] Preserve existing coupon identity, code deliverability, bounds, source status, selection flags and all other normalized restrictions.
- [x] Add focused tests for empty, nonempty, missing, malformed and oversized restriction arrays and absence of sensitive bytes in saved snapshots/logs.
- [x] Run owning repository's declared focused tests, changed-file lint, build and `git diff --check`, then record actual execution results.

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

- [x] Both nullable flags distinguish verified empty arrays from true restrictions and unknown/malformed/overflow, without raw email/metadata persistence.
- [x] Existing coupon normalization, tenant identity and optional-field issue reporting remain unchanged; no Shopify code or unrelated worker feature changes.
- [x] MCP-002 can distinguish present/unobserved Woo restrictions from observed absence using these snapshot flags; no live Woo coupon check is required for initial outreach.
- [x] Synthetic sensitive input values do not appear in serialized snapshot, emitted logging/issue diagnostics or outbound contracts.

## Validation

- [x] Focused existing Woo coupon normalization/provider sync unit tests and explicit sensitive-input negative assertions.
- [x] Background declared lint and build scripts; `git diff --check`.
- [x] Worktree/parent synchronization and submodule evidence in the Completion Report, following `docs/agent-worktree-isolation-policy.md`.

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update only this task's progress/Completion Report, set `status: review`, return evidence to moda_architect and **STOP**. Do not self-accept, modify `_index.md`, start MCP-002, merge or push main.

## Implementation Notes

Use the existing pure normalization helper and tests; keep source editing paths relative to the owning repository. Do not infer optional Woo plugin data from arbitrary metadata. Any broader eligibility verification requirement is an architect decision, not permission to build an external coupon checker.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/providers/woo-coupon-normalization.ts`
- `moda-interact-background/tests/unit/providers/woo-coupon-normalization.test.ts`
- `moda-interact-background/src/services/translation-reconciliation.service.ts` (developer-requested lint correction)

### Work Completed

- Added `emailRestrictionsPresent` and `uninspectedMetadataPresent` to the existing safe provider snapshot. Empty source arrays map to `false`; valid nonempty email restriction arrays and nonempty metadata arrays map to `true`; missing, malformed or oversized fields map to `null`.
- Kept source email and metadata arrays, values and keys out of snapshots and diagnostics. Ambiguous or oversized supplied fields emit only the bounded `optional_field_ignored` issue for the field name.
- Preserved existing coupon identity, code deliverability, selection, status, bounds and other normalized restrictions. No schema, cross-service contract, API, or worker lifecycle changes.
- Added focused tests covering empty, nonempty, missing, malformed and oversized inputs, including serialized snapshot/diagnostic assertions against synthetic sensitive values.
- In response to the developer's follow-up, preserved the credential lookup exception as the `cause` of the generic `UNAVAILABLE_CREDENTIAL` error in `translation-reconciliation.service.ts`; outward error behavior is unchanged and the `preserve-caught-error` lint finding is resolved.

#### Architect Review Correction Checklist

- Read the complete task and latest `## Architect Review` before implementation.
- Latest review status is `Pending`; it contains no `Changes Requested` outcome or correction items. Mandatory architect-review corrections: none.
- Completed all task Work Items and Acceptance Criteria within the defined scope.

### Validation Results

- `./node_modules/.bin/vitest run tests/unit/providers/woo-coupon-normalization.test.ts` — passed; 1 test file, 8 tests.
- `./node_modules/.bin/eslint src/providers/woo-coupon-normalization.ts tests/unit/providers/woo-coupon-normalization.test.ts` — passed.
- `./node_modules/.bin/eslint src/services/translation-reconciliation.service.ts src/providers/woo-coupon-normalization.ts tests/unit/providers/woo-coupon-normalization.test.ts` — passed after the developer-requested correction.
- `./node_modules/.bin/vitest run tests/unit/services/merchant-pricing-translation-reconciliation.service.test.ts` — passed; 1 test file, 4 tests.
- `npm run build` — passed, including Prisma client generation and TypeScript compilation.
- `git diff --check` — passed.
- `npm run lint` — passed repository-wide after the developer-requested correction.
- `npm ci` was required because the prepared implementation worktree had no `node_modules`; it completed from the existing lockfile without lockfile changes. npm reported 40 dependency audit findings (27 moderate, 13 high); dependency remediation is outside this task.
- Launcher preparation evidence: canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-014`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-014`; both task branches are `task/ARCH-052-BACKGROUND-014`. Prepared parent head was `5362773f36eec15e7e095764b040da6c5ce19680`, implementation head was `105f5ead7b3f39b6e66c5cd385443877d4c2729c`, and initialized database submodule was `af77c594ecbfc78c26d01c0021a090830884bbff`.
- Implementation commit `8ecc53b` was pushed to `origin/task/ARCH-052-BACKGROUND-014`. The initial default push was refused because the local branch's configured upstream is `origin/main`; explicit ref push to the matching task branch succeeded without changing branch configuration.

### Deviations

No implementation-scope deviations. The task-specific changed-file lint passed; full-repository lint remains blocked by the unrelated finding recorded above.

### Assumptions

The Woo REST response carries the source field when available; missing is not equivalent to empty.

### Unresolved Issues

Full-repository lint has the unrelated pre-existing failure recorded in Validation Results. No task-specific unresolved implementation issue.

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

## Developer Approval

Approved by the developer on 2026-10-31, including the requested credential-error cause-preservation correction. This records developer approval only; Architect Review remains Pending, so the task status remains `review` until the authorized architect acceptance step.
