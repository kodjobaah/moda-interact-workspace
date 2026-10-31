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
status: review
priority: 40
executor: null
claimed_at: null
attempt: 2
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

- [x] Update `RuntimeField` / `integerField()` to represent a field without an upper bound, without changing any other field's maximum.
- [x] Change the recovery lifetime field to `min=0`, `max=null`, `defaultValue=21`, with explicit zero semantics.
- [x] Adjust common validator and range display to account for `max === null`.
- [x] Make the HTML input omit `max` only for this field.
- [x] Replace old 1–90 tests with all allowed and rejected values, including values >90 and 0; add UI/metadata assertions for the missing `max` attribute, `step=1`, and unchanged other inputs.
- [x] Verify existing audited update and concurrency tests still pass; record actual results.

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

Ready for Review (Attempt 2). The requested behavioral action-test correction is implemented and validated. Attempt 1 details below are historical; its full-suite and repository-lint caveats apply only to that prior run.

### Attempt 1 Historical Record

Attempt 1 returned with Changes Requested. The launcher incremented the attempt for the current rework.

### Files Changed

- `moda-interact-admin/src/lib/admin/background-runtime-control-validation.ts`
- `moda-interact-admin/src/components/admin/background-runtime-controls.tsx`
- `moda-interact-admin/tests/unit/background-runtime-control-validation.test.ts`
- `moda-interact-admin/tests/security/admin-background-runtime-controls.test.mjs`
- Implementation commit: `4ade253` (`Allow unbounded recovery lifetime setting`), pushed to `task/ARCH-016-ADMIN-003`.

### Work Completed

- Made `RuntimeField.max` nullable and changed only `checkoutRecoveryLifetimeDays` to `min: 0`, `max: null`, `defaultValue: 21`, with the exact requested field guidance.
- Updated shared validation to require safe integers and honor a nullable maximum. The open-ended range displays as `0 or more whole days`; all bounded fields retain their existing maxima.
- Removed the HTML `max` only for an unbounded field, retained numeric type, step, and minimum metadata, and explained that zero immediately expires eligible recoveries and may prevent outreach.
- Left the server action unchanged: permission checks, required reason, expected-version compare-and-set, audit event snapshots, and transaction ordering remain intact. Focused assertions verify validation occurs before mutation and audit creation follows the successful update.
- Added accepted/rejected input coverage, unchanged-config-on-rejection coverage, field-bound/input metadata assertions, and updated the focused admin security contract test.

### Validation Results

- `node --conditions=import --import tsx --test tests/unit/background-runtime-control-validation.test.ts`: passed, 9 tests.
- `node --test tests/security/admin-background-runtime-controls.test.mjs`: passed, 6 tests.
- `npm run test:unit`: 569 passed, 17 failed out of 586. Failures are outside the changed files, in agent-instruction, ARCH-047 publication/translation, commerce-policy harness, merchant-pricing, Shopify taxonomy, and store-category tests. Observed causes include `tslib` interop failures and test harnesses rejecting dependencies; the focused runtime-control tests passed in both runs.
- `npm run lint`: failed on the unrelated `src/components/admin/whatsapp-templates/media/use-shop-brand-media-role.ts` `react-hooks/set-state-in-effect` error; three unrelated warnings were also reported.
- `npx eslint src/lib/admin/background-runtime-control-validation.ts src/components/admin/background-runtime-controls.tsx tests/unit/background-runtime-control-validation.test.ts`: no changed-source lint errors; ESLint skipped the unit test file under an existing ignore pattern.
- `npm run build`: passed, including Prisma client generation and TypeScript checks. Next.js reported existing BullMQ warnings, including unresolved optional `@valkey/valkey-glide` imports.
- `git diff --check`: passed.

### Deviations

- No source/action deviation. The full unit suite and repository-wide lint remain limited by unrelated failures noted above; no unrelated files were changed.

### Assumptions

The existing SQL `INTEGER` column continues to define the persisted representational range; no additional application policy ceiling was introduced.

### Unresolved Issues

None

### Architectural Concerns

None

### Attempt 2 Correction

Replaced the action source-order assertion with tests that execute `mutateBackgroundRuntimeControlsAction` through the existing `loadPolicyModule` harness. The successful action test proves the configured lifetime changes from 21 to 180 days, the optimistic version advances from 7 to 8, and the audit contains exact complete before/after snapshots, the platform-admin identity, and the supplied reason. The same test suite verifies that a non-SUPER_ADMIN, stale expected version, and negative lifetime do not update configuration or create an audit. No production action code or action semantics changed.

### Attempt 2 Files Changed

- `moda-interact-admin/tests/security/admin-background-runtime-controls.test.mjs`
- `moda-interact-admin/tests/unit/background-runtime-control-validation.test.ts`
- Implementation commit: `4214934` (`test(admin): exercise runtime controls audit action`), pushed to `task/ARCH-016-ADMIN-003`.

### Attempt 2 Validation Results

- `node --test tests/security/admin-background-runtime-controls.test.mjs`: passed, 8 tests, including the successful audited action and permission/version/invalid-input checks.
- `node --conditions=import --import tsx --test tests/unit/background-runtime-control-validation.test.ts`: passed, 8 tests.
- `npm run build`: passed, including TypeScript checking. Existing BullMQ optional-dependency/critical-dependency warnings for `@valkey/valkey-glide` remain.
- `npx eslint tests/security/admin-background-runtime-controls.test.mjs tests/unit/background-runtime-control-validation.test.ts`: exited 0; ESLint's existing ignore rules skipped both test files, so this did not lint their contents.
- `git diff --check`: passed.
- Full unit suite and repository-wide lint were not rerun. The 17 unrelated unit failures and unrelated lint error recorded above belong to Attempt 1 and are not Attempt 2 results.

### Attempt 2 Deviations and Unresolved Issues

None. Production action behavior remains unchanged.

## Architect Review

### Review Status

Attempt 1 — Changes Requested

### Review Notes

The runtime field metadata, validation, open-ended display range, missing HTML
`max`, and zero-day guidance match the task. The safe-integer parser accepts
the required values and rejects decimals, scientific notation, empty and
unsafe input. One acceptance blocker remains:

1. The new `validates before mutation and retains optimistic audited update
   fields` test only reads `src/app/actions/background-runtime-controls.ts`
   as text and checks source ordering and regex matches. It does not invoke
   `mutateBackgroundRuntimeControlsAction`, prove that an allowed lifetime is
   persisted, or assert that the successful audit event contains the expected
   before/after values and required reason. The task explicitly requires a
   successful audited update and rejection without mutation. Add a behavioral
   action test using suitable mocks or a focused database fixture to verify a
   successful update/audit and invalid-input rejection before mutation; retain
   the expected-version and permission checks.

### Reviewed Files

- `src/lib/admin/background-runtime-control-validation.ts`
- `src/components/admin/background-runtime-controls.tsx`
- `src/app/actions/background-runtime-controls.ts`
- `tests/unit/background-runtime-control-validation.test.ts`
- `tests/security/admin-background-runtime-controls.test.mjs`
- This task definition and Completion Report

### Validation Reviewed

The Completion Report records 9 focused validation tests and 6 security
contract tests passing, build and diff check passing, and changed-source lint
passing. The repository-wide unit suite reported 17 unrelated failures and
repository-wide lint failed on an unchanged file. No tests were rerun for this
review. The existing test evidence does not exercise a successful audited
action mutation.

### Architecture Conformance

The field-level validation and UI conform to the no-maximum policy. The report
does not yet demonstrate that the complete Admin action persists the new
values and writes their audit snapshot as required.

### Follow-up

Add behavioral coverage for the successful audited update and invalid input
with no mutation, then rerun focused tests, build, changed-file lint and
`git diff --check`. Record the results and resubmit Attempt 1; do not increment
the attempt in this review. `ARCH-016-ADMIN-003` remains Ready and
`ARCH-016-SYSTEM-TEST-001` remains Pending.
