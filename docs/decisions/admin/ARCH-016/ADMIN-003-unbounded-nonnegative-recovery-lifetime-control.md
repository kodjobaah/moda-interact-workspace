---
id: ARCH-016-ADMIN-003
architecture_id: ARCH-016
title: Allow administrator-defined non-negative whole-day recovery lifetimes without a fixed maximum
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-016-DATABASE-002
  - ARCH-016-BACKGROUND-005
  - ARCH-016-ADMIN-001
enables:
  - ARCH-016-SYSTEM-TEST-001
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-016-ADMIN-003 — Non-negative administrator-controlled recovery lifetime

## Architecture

- Architecture: `ARCH-016` — `docs/architecture/ARCH-016-merchant-recovery-policy-shopify-discounts-followups-expiry.md`.
- Coordinator: `moda_architect`; implementation owner: `moda_admin`.

## Objective

Let the existing audited platform Admin runtime control accept **any non-negative whole-number** recovery lifetime representable by the persisted PostgreSQL `INTEGER`, with no fixed business maximum and with the existing default of 21 days.

## Context

The Admin field in `src/lib/admin/background-runtime-control-validation.ts` currently uses:

```typescript
integerField("checkoutRecoveryLifetimeDays", "Checkout recovery lifetime", /* guidance */, "days", 1, 90, 21)
```

`validateRuntimeConfig()` enforces `value < field.min || value > field.max`, and `src/components/admin/background-runtime-controls.tsx` always renders a numeric `max` attribute. The page currently advertises a `1–90 days` range. All three must change together; deleting the number 90 from one field is insufficient.

## Scope

Authorized changes within `moda-interact-admin`:

```text
src/lib/admin/background-runtime-control-validation.ts
src/components/admin/background-runtime-controls.tsx
tests/unit/background-runtime-control-validation.test.ts
focused admin form/action tests directly affected by the field's optional upper bound
```

Do not modify `src/app/actions/background-runtime-controls.ts` unless source inspection identifies a **real field-specific 90-day rejection**; the current action already delegates to the central validator and keeps audited optimistic concurrency. Any such modification must be narrowly justified in the Completion Report.

## Out of Scope

- No database migration or Background runtime implementation; those belong to DATABASE-002 and BACKGROUND-005.
- No other runtime field's bounds, Shopify/WooCommerce checkout policy, billing, customer-facing checkout, or recovery-generation change.
- Do not create a separate settings store, bypass admin audit/reason/version gates, or introduce a new business upper limit (365 etc.).
- Do not change `docs/decisions/**/_index.md`.

## Requirements

1. Make `RuntimeField.max` explicitly nullable, e.g. `max: number | null`, while keeping bounded fields' current max numbers unchanged. Update only the required helper type, `integerField()` signature and `checkoutRecoveryLifetimeDays` registration to use:

   ```typescript
   integerField(
     "checkoutRecoveryLifetimeDays",
     "Checkout recovery lifetime",
     "Expire an active checkout recovery after this many days without checkout/customer activity. Zero expires eligible recoveries immediately; expired history remains. Choose a non-negative whole number of days.",
     "days", 0, null, 21,
   )
   ```

2. In `validateRuntimeConfig()`, use `Number.isSafeInteger(value)`, `value >= field.min`, and `(field.max === null || value <= field.max)` for the existing unified validation loop. **Do not add a second numeric ceiling**. Retain all other cross-field rules and bounds.
3. In `runtimeFieldDisplayRange()`, show `0 or more whole days` for this unlimited field; show existing `min–max` strings for every other field.
4. In `src/components/admin/background-runtime-controls.tsx`, keep `type="number"`, `step="1"`, and `min={0}`, but omit the HTML `max` attribute when `field.max === null` (e.g. use `max={field.max === null ? undefined : field.max / (field.displayMultiplier ?? 1)}`). Keep every other input's existing min/max representation unchanged.
5. Input parsing must reject `-1`, `1.5`, `21.0`, empty values, scientific notation and non-finite/unsafe integer values. Accept `0`, `1`, `21`, `90`, `91`, `180`, `365`, and `2147483647` as strings (the existing SQL `INTEGER` still defines its technical representational range).
6. Preserve the existing `expectedVersion` optimistic update, required admin reason, `BackgroundRuntimeConfigAuditEvent`, `beforeValue/afterValue` and permission checks. Do not change any other runtime control's metadata.
7. Make the UI guidance clear: **zero means recovery eligibility expires immediately** and may prevent recovery outreach; the default remains 21, and no policy maximum is displayed.
8. Do not display Moda errors on a merchant's storefront. This is a platform-admin setting and existing admin-only validation feedback remains appropriate. For Node-side dependency failures, use the published shared structured logger when logging is required, preserve original diagnostic messages with sensitive data redacted and do not swallow exceptions silently.

## Work Items

- [ ] Update `RuntimeField` / `integerField()` to represent a field without an upper bound, without changing any other field's maximum.
- [ ] Change the recovery lifetime field to `min=0`, `max=null`, `defaultValue=21`, with explicit zero semantics.
- [ ] Adjust common validator and range display to account for `max === null`.
- [ ] Make the HTML input omit `max` only for this field.
- [ ] Replace old 1–90 tests with all allowed and rejected values, including values >90 and 0; add UI/metadata assertions for the missing `max` attribute, `step=1`, and unchanged other inputs.
- [ ] Verify existing audited update and concurrency tests still pass; record actual results.

## Interfaces / Contracts

Platform Admin POST action remains unchanged. `checkoutRecoveryLifetimeDays` remains a number stored in the existing singleton `public."BackgroundRuntimeConfig"` field; no new API route or wire schema.

The field metadata is **unbounded by business policy**:

```typescript
{
  key: "checkoutRecoveryLifetimeDays",
  unit: "days",
  min: 0,
  max: null, // no business maximum
  defaultValue: 21,
}
```

User input still must be a whole number `>= 0`. The database column remains a 32-bit signed SQL integer; do not imply it can store arbitrary-precision values.

## Dependencies

- `ARCH-016-DATABASE-002` — migration removing the database ceiling accepted.
- `ARCH-016-BACKGROUND-005` — Background can safely accept zero and large non-negative integers.
- `ARCH-016-ADMIN-001` — original audited control (Complete).

## Enables

- Existing terminal `ARCH-016-SYSTEM-TEST-001`, once all implementation tasks are accepted.

## Acceptance Criteria

- [ ] Admin accepts and persists `0`, `1`, `91`, `180`, `365` and a representable large integer; the audit records the intended before/after values and reason.
- [ ] Admin rejects negative and fractional values before database mutation, and rejects malformed or unsafe numeric input without changing the current config.
- [ ] The field renders no HTML `max` attribute and shows the correct open-ended range; all other fields still respect their original maximums.
- [ ] The default remains 21; no automatic reset or migration of existing settings occurs.
- [ ] Zero is explicitly explained as immediate inactivity expiry and potential prevention of outreach.
- [ ] Existing admin permissions, optimistic versioning, reason requirement and audit trail still function.
- [ ] No additional policy limit, new table, storefront errors or cross-repository source changes.

## Validation

Inspect `package.json`, then run the declared scripts relevant to this task, including:

```bash
npm run test:unit
npm run lint
npm run build
git diff --check
```

Include focused assertions for form values, HTML input metadata, rejection without mutation, and a successful audited update. Record the commands, result and any genuine baseline limitations in the Completion Report.

## Stop Condition

When the implementation, criteria and validation are complete, finish the Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not start ARCH-016 system tests or ARCH-053 implementation.

## Implementation Notes

The only permitted business validation is *non-negative whole days*; SQL/Prisma representational limits and JavaScript safe-integer parsing remain technical constraints, not an administrator-configured maximum. The zero-day setting is valid but intentionally expires active recovery episodes immediately; this is not the same as deleting recovery history.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

Not Started

### Validation Results

Not Run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation evidence.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not assessed.

### Follow-up

None
