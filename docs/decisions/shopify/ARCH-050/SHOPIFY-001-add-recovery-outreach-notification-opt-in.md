---
id: ARCH-050-SHOPIFY-001
architecture_id: ARCH-050
title: Add Shopify merchant recovery-outreach notification preference
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-050-DATABASE-001
enables:
  - ARCH-050-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-27
---

# Add Shopify merchant recovery-outreach notification preference

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Expose and persist the default-off notification toggle in existing Shopify Recovery Settings using current authenticated, revision-protected save flows.

## Context

`app/services/recovery-policy/recovery-policy.server.ts`, `app/components/settings/SettingsForm.tsx`, `app/routes/app/settings-save/route.ts` and their tests already own the merchant recovery settings.

## Scope

**Modify in `moda-interact/`:**

- `app/services/recovery-policy/recovery-policy.server.ts` — add opt-in to `loadRecoveryPolicySnapshot()`, `parseMerchantRecoveryPolicy()`/save input and optimistic update logic without changing the published Shared effective-recovery-policy structure.
- `app/routes/app/settings-save/route.ts` — extend the `intent === "recovery"` exact form allowlist and submit payload.
- `app/routes/app/recovery-settings/RecoverySettingsView.tsx` — add a labelled merchant-controlled checkbox in the existing Recovery Settings form, with explicit true/false submission.
- `app/i18n/locales/*.json` — add `recoverySettings.initialOutreachNotification.title`, `.description` (and any other genuinely required keys) in all 20 supported merchant locales.
- Update `tests/unit/recovery-policy.test.ts`, `tests/unit/recovery-settings-i18n.test.ts`, `tests/unit/recovery-settings-submit-guard.test.tsx` and a focused settings route UI test if needed.

`app/components/settings/SettingsForm.tsx` is the existing wrapper; modify only if an identified form-submission issue requires it. Do not edit the Support inbox/recovery-detail views here (SHOPIFY-002).

## Out of Scope

- Support action links, Background sends, a new settings page or Shopify Admin notification API.

## Requirements

- Expose `notifyOnInitialRecoveryOutreach` as a **top-level Boolean** in the Shopify settings loader snapshot or a separate merchant settings field; do not put it in `effective`/`merchant` objects passed to `parseEffectiveRecoveryPolicy` from Shared, which owns only delays/offer/follow-up.
- Initialise unchecked/default OFF from the `ShopSettings` row. Save exactly `"true"` or `"false"` as a form field named `notifyOnInitialRecoveryOutreach` (include explicit false; native unchecked checkbox omission is not acceptable for this strict form contract).
- Update the exact allowed field list in `settings-save/route.ts`; reject missing, ambiguous, duplicated or non-Boolean string values with `INVALID_INPUT`. Do not silently convert arbitrary truthy strings to true.
- Extend `saveMerchantRecoveryPolicy(shopId, input, now, expectedRevision, client)` to update notification preference *in the same existing ShopSettings transaction*. The current early-return equality uses only `revisionOf(toPolicy(...))` and would silently discard a **preference-only** update: include this Boolean in the comparison before returning unchanged.
- Keep `lockSettingsShop`, row revision check, discount validation and existing merchant-policy values intact. For a real preference change, enforce expected `updatedAt` revision even if delay/offer/follow-up fields match. Concurrent stale preference saves must fail with 409.
- Admin override remains a read-only discount/delay/follow-up mechanism; it does not replace or force the opt-in. Saving the checkbox cannot change credit accounting or initiate a recovery.
- Use existing Shopify merchant i18n for all 20 language files, accessible checkbox label/help, no English-only hardcoded UI.
- For server-side handling, reuse `@modainteract/moda-interact-shared/logging` and the existing Shopify process identity/environment, with no new JSON/console logger. `settings-save/route.ts` must preserve existing expected validation/conflict responses; when a newly caught or already-caught unexpected policy/Prisma exception occurs, record a bounded `merchant.recovery_settings.save.failed` error event (`shopId`, `operation:"recovery_notice_preference"`, safe error category, `{error}`) and rethrow to the existing framework error boundary. Do not log raw form data, customer data or discount IDs, or report `{ok:true}` on failure.
- Do not add `catch {}` to parse/save/UI flows. An invalid Boolean is an intentional HTTP 400 and a stale revision is an intentional conflict; if a caught error is mapped to such a response, log at `warn` only where existing logging conventions require it, never as an internal failure. Logging sink trouble cannot alter HTTP success/failure semantics.

## Work Items

- [x] Project `ShopSettings.notifyOnInitialRecoveryOutreach` in settings loader with default false.
- [x] Add checkbox and explicit Boolean form serialization to `RecoverySettingsView` under existing `SettingsForm`.
- [x] Add strict form key/Boolean validation to `settings-save/route.ts`.
- [x] Update save transaction/no-op comparison and revision protection to persist this field even when it is the only changed value.
- [x] Add all locale keys, unit/UI tests and stale-revision cases.
- [x] Add server-side shared structured failure logging at the recovery settings action boundary (reuse/create approved process logger), and tests showing unexpected save errors are logged and rethrown, not converted to success.

## Interfaces / Contracts

- Persisted: `ShopSettings.notifyOnInitialRecoveryOutreach: boolean`.
- Form field: `notifyOnInitialRecoveryOutreach = "true" | "false"`; existing `intent:"recovery"`, `revision`, `operationId` remain mandatory.
- Loader: `loadRecoveryPolicySnapshot(...).notifyOnInitialRecoveryOutreach: boolean` (top-level). Existing `merchant`/`effective` `RecoveryPolicy` schemas remain unchanged.
- `parseMerchantRecoveryPolicy(input)` and `saveMerchantRecoveryPolicy` accept the parsed Boolean alongside existing inputs; expect a true Boolean internally after parsing the strict form.
- No API route version change, Shared package edit or change to shop onboarding.
- Logging contract: existing shared `StructuredLogger`/`createLogger` mechanism; stable event `merchant.recovery_settings.save.failed` (`error`, validated `shopId`, stable `operation`, `errorCategory`), no raw form payload.

## Dependencies

- `ARCH-050-DATABASE-001` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-001` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [x] Settings UI starts OFF for existing and new shops; a merchant can toggle and save ON/OFF without touching recovery delay/follow-up/offer values.
- [x] Notification-only changes are persisted and advance the settings revision; unchanged saves are no-op.
- [x] Missing/duplicated/invalid Boolean, stale revision and unauthorised merchant save are rejected.
- [x] Admin override does not alter the persisted preference; all 20 locale catalogues validate.
- [x] Database/save exceptions are visible through structured logs and the existing route failure boundary; no swallowed catch or falsely successful preference update.

## Validation

- [x] Focused `vitest`/repository declared tests for `recovery-policy`, `recovery-settings-i18n`, `recovery-settings-submit-guard`, and settings route fixtures.
- [x] Route-level test stubs failing persistence and verifies safe shared-logger failure event plus unchanged 500/error-boundary behaviour; validation/conflict status remains unchanged.
- [x] Owning Shopify repository typecheck/lint/build **only where scripts exist**; check `package.json`, then `git diff --check`.
- [x] Verify 20 locale keys are present and exposed through the existing merchant-i18n utility.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

The snapshot's early no-op comparison is a critical correctness detail. Save success must only be returned after the opt-in is actually persisted. This task does not decide notification emission; Background reads `ShopSettings` at first confirmed-send finalisation.

Follow mirrored task branch/worktree policy; no `_index.md` update until user closes the architecture session.

## Completion Report

### Status

Accepted by architect at Attempt 1; task completed automatically.

### Files Changed

- `app/services/recovery-policy/recovery-policy.server.ts`
- `app/routes/app/settings-save/route.ts`
- `app/routes/app/recovery-settings/RecoverySettingsView.tsx`
- `app/i18n/locales/*.json` (all 20 supported merchant locales)
- `tests/unit/recovery-policy.test.ts`
- `tests/unit/recovery-policy-save.test.ts`
- `tests/unit/recovery-policy-snapshot.test.ts`
- `tests/unit/recovery-settings-i18n.test.ts`
- `tests/unit/settings-save-recovery-route.test.ts`
- `tests/integration/merchant-feature-preferences.test.ts` (existing direct save fixture now supplies default false)

### Work Completed

- Loaded the persisted preference as a top-level, default-off snapshot field; it is not included in the Shared merchant/effective policy structures, so admin overrides do not control it.
- Added an accessible localized Recovery Settings checkbox with an explicit hidden `true`/`false` form value, including explicit false.
- Added exact form allowlisting and rejection for missing, duplicated, or non-Boolean preference fields.
- Persisted ON/OFF changes in the existing locked ShopSettings transaction. The unchanged comparison now includes the preference; preference-only changes require the expected `updatedAt` revision and stale writes return conflict.
- Added Shared structured failure logging for unexpected recovery settings persistence errors (`merchant.recovery_settings.save.failed`, bounded error field, validated shop id, fixed operation/category) and rethrow to the existing framework failure boundary. Expected validation/conflict responses retain their existing status behavior.
- Added translated title/help strings and locale contract coverage across all 20 supported merchant locales.

### Validation Results

- Focused Vitest: **passed**, 6 files / 25 tests, covering recovery policy parsing, ON and OFF preference-only saves, stale revision, no-op, default-off snapshot, all locale catalogs, submit guard, strict route inputs, Shared failure event and rethrow, and conflict response.
- `npm run typecheck`: **passed**.
- `npm run lint`: **passed** after removing one unused test import found on the first run.
- `npm run build`: **passed**. Bundler emitted warnings for an unresolved Prisma browser import, Zod annotation comments and bundle size; both client and server builds completed.
- `git diff --check`: **passed**.
- PostgreSQL integration suite was not run; transaction and stale-revision cases were covered by focused mocked-client tests.

### Deviations

None.

### Assumptions

The existing `ShopSettings.notifyOnInitialRecoveryOutreach Boolean @default(false)` field from the completed database dependency is authoritative and requires no schema or migration change in this repository task.

### Unresolved Issues

None.

### Architectural Concerns

None discovered.

### Task Branch / Worktree Evidence

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-SHOPIFY-001`
  parent branch: `task/ARCH-050-SHOPIFY-001`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-SHOPIFY-001`
  implementation branch: `task/ARCH-050-SHOPIFY-001`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  recorded database submodule commit: `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`

Claim evidence: Attempt 1, executor `codex`, claim commit `8fc3b0b5a3a95150dc01a1e7fad73d49e4f0db43` pushed by the deterministic launcher.
Implementation evidence: commit `cab6f08` on `task/ARCH-050-SHOPIFY-001`, pushed to `origin`.

## Architect Review — Attempt 1 — Accepted — 27 October 2026

### Review Status

Accepted.

### Review Notes

The Shopify settings snapshot exposes the persisted notification preference at the top level with default OFF; the shared effective recovery policy remains unchanged. The recovery settings UI initializes from that field and submits explicit `true`/`false`. The route allowlist rejects missing, repeated, or invalid Boolean values, and the save service includes the setting in its existing locked ShopSettings transaction and no-op comparison. A preference-only change therefore checks the expected revision and persists atomically with existing recovery policy values. Admin overrides do not alter the merchant preference.

Unexpected recovery preference persistence failures are logged through the existing Shared logger with the specified stable event, shop and operation context, category, and original error, then rethrown to the framework boundary. Existing validation and conflict responses remain intact. The checkbox title/help are localized across all 20 supported merchant locales. No Support UI, send behavior, billing, or Shared policy schema changes were introduced.

### Reviewed Files

- `moda-interact/app/services/recovery-policy/recovery-policy.server.ts`
- `moda-interact/app/routes/app/settings-save/route.ts`
- `moda-interact/app/routes/app/recovery-settings/RecoverySettingsView.tsx`
- All 20 changed locale files.
- Focused recovery policy, save route, snapshot, i18n, and submit guard tests.
- Attempt 1 Completion Report and canonical worktree/publication evidence.

### Validation Reviewed

- Focused Vitest: 6 files / 25 tests passed, per the task report, including ON/OFF preference-only persistence, stale revisions, default-off snapshot, locale catalogs, strict inputs, Shared failure logging/rethrow, and conflict handling.
- `npm run typecheck`, `npm run lint`, and `npm run build` passed. The build reported non-fatal Prisma browser import, Zod annotation, and bundle-size warnings.
- `git diff --check` passed.
- PostgreSQL integration was not run; transaction and stale-revision behavior were covered by focused mocked-client tests.
- Implementation branch `task/ARCH-050-SHOPIFY-001` is clean and published at `cab6f0822a4cc1369f56414f0322bcd31829beaf`; database submodule is at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`. Neither task branch was merged to `main`.

### Architecture Conformance

Conforms to ARCH-050: the opt-in is an independent merchant setting, remains default-off, and does not affect the shared recovery-policy shape, admin override semantics, credit accounting, or send behavior.

### Dependency Frontier

This task uses `completion_mode: automatic`; architect acceptance completes Attempt 1. All declared prerequisites of `ARCH-050-SYSTEM-TEST-001` are now complete: BACKGROUND-002, SHOPIFY-001, and SHOPIFY-002. Its canonical task advances from `pending` to `ready` at Attempt 0; it remains unclaimed and manual-gated for developer validation before execution. No implementation task is enabled by this terminal test task.

### Lifecycle

`status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`. Neither task branch was merged to `main`.
