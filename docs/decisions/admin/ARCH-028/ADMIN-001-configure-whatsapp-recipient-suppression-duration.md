---
id: ARCH-028-ADMIN-001
architecture_id: ARCH-028
title: Configure WhatsApp recipient suppression duration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 15
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-028-DATABASE-001
enables:
  - ARCH-028-SYSTEM-TEST-001
created: 2026-10-07
updated: 2026-10-12
---

# Configure WhatsApp recipient suppression duration

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Expose the ARCH-028 platform-level WhatsApp recipient suppression duration through the existing SUPER_ADMIN Platform Billing Policy controls, defaulting to seven days and preserving existing policy audit/version semantics.

## Context

DATABASE-001 adds `PlatformBillingPolicy.whatsappRecipientSuppressionDays @default(7)`. The Admin application already reads/mutates/audits the singleton Platform Billing Policy through SUPER_ADMIN controls.

## Scope

- Read/render the current suppression-day value on `/system-controls/platform-policy` using existing UI conventions.
- Accept a required positive integer day count; default/read value is `7` from persistence.
- Persist through the existing platform-policy mutation/upsert transaction.
- Include the field in before/after billing audit snapshots and policy version increment automatically through the existing path.
- Add/update Admin translations/tests/types/read models required by the existing form.

## Out of Scope

- Per-Shop suppression override.
- Reachability runtime logic.
- Provider-code classification.
- Database schema/migration.

## Requirements

- [x] Existing SUPER_ADMIN authorization remains unchanged.
- [x] Value must be positive; zero/negative/invalid input is rejected with bounded UI error.
- [x] Saving another policy field must not silently reset suppression days.
- [x] No duplicate policy store/config mechanism is introduced.

## Work Items

- [x] Extend policy validation/input types/action/read model.
- [x] Add form field/help text/translations.
- [x] Add focused validation/action/component tests.

## Interfaces / Contracts

Consumes `PlatformBillingPolicy.whatsappRecipientSuppressionDays` from DATABASE-001.

## Dependencies

- `ARCH-028-DATABASE-001`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Existing persisted value displays correctly.
- [x] Seven-day default is visible when policy is initialized normally.
- [x] SUPER_ADMIN can change value and audited policy mutation increments version.
- [x] Invalid non-positive values are rejected.

## Validation

Use repository-declared focused unit/component/action tests, lint/typecheck/build as available, and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

This is a platform policy, not a merchant setting. Do not add a ShopBillingPolicyOverride field in ARCH-028.

## Completion Report

### Status

Ready for Architect review (Attempt 2, 2026-10-12). Implementation remains unchanged at `8602773` (`feat(admin): configure WhatsApp recipient suppression duration`); this attempt adds required execution evidence only.

### Files Changed

Updated `src/lib/admin/billing-control-validation.ts`, `src/app/actions/billing-controls.ts`, and `src/components/admin/billing-controls.tsx`; added required keys in `src/i18n/required-keys.ts` and English strings in `src/i18n/locales/en.json`; expanded `tests/security/admin-billing-controls.test.mjs`.

### Work Completed

Exposed `whatsappRecipientSuppressionDays` on the existing SUPER_ADMIN Platform Billing Policy form with the persisted value shown and a seven-day default when no policy exists. The server parser requires a positive whole number and surfaces bounded validation messages. The existing policy upsert explicitly persists the field on create and update, preserving it when the full form is saved; existing before/after audit snapshots and version increments remain in the same transaction. SUPER_ADMIN authorization and the singleton policy store are unchanged. No schema, migration, Shop override, or runtime suppression logic was added.

### Validation Results

PASS: focused `node --test tests/security/admin-billing-controls.test.mjs` (11/11), including positive, zero, negative, fractional and missing duration inputs; persistence mappings; default/current rendering; translations; existing authorization/audit assertions.

PASS: reran the focused test on Attempt 2 from the launcher-resolved implementation worktree: `node --test tests/security/admin-billing-controls.test.mjs` (11/11).

PASS: `npm run build` (TypeScript and production build), `npm run lint` (0 errors; one existing warning in `database/eslint.config.mjs`), `npm run prisma:validate`, changed-file diagnostics (no errors), and `git diff --check`.

PARTIAL: `npm run test:unit` completed with 318 passed and 2 unrelated failures: an outdated Agent Instructions selector expectation in `tests/unit/agent-instructions.test.ts`, and unresolved `@/lib` alias import in `tests/unit/shopify-taxonomy.test.ts`.

PARTIAL: `npm test` reported 2 unrelated failures in `tests/security/admin-store-categories.test.mjs` and `tests/security/admin-tenant-business-kpis.test.mjs`, whose expectations do not match the current untouched components. The task-specific billing-controls test passes.

The initial full-unit attempt was run before installing dependencies in the fresh worktree and failed on missing packages. `npm ci` from the committed lockfile and `npm run prisma:generate` restored the test/build environment; no tracked dependency manifest or lockfile changed.

### Deviations

The first full-unit run exposed the empty dependency state of the newly prepared worktree. Dependencies were installed with `npm ci`, and Prisma Client was generated with the declared script. The workspace doctor also reported the documented `DEP-ZOD-001` Admin direct-Zod declaration issue and `NPM-CONFIG-001` warning; these are outside this task and were not changed.

### Assumptions

The existing Platform Billing Policy remains the single source of truth. Its persisted suppression duration is expected to be provided by the completed DATABASE-001 contract.

### Unresolved Issues

Repository-wide `npm run test:unit` and `npm test` each retain two unrelated failures listed above. The task-owned focused suite, build, lint, schema validation, diagnostics, and diff check pass.

### Architect Review Follow-up (Attempt 2)

All six evidence-only corrections are implemented in this task document; implementation and test source files were not changed:

1. **Parent task worktree path:** `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-ADMIN-001` on `task/ARCH-028-ADMIN-001`.
2. **Implementation task worktree path:** `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-ADMIN-001` on `task/ARCH-028-ADMIN-001`.
3. **Start-of-attempt synchronization:** launcher reports parent remote task fast-forward `not-needed`, current `origin/main` incorporated (`yes`), synchronized head `33a434a3dfa3b78e63dce37df0fc48fc2bff125e` before the Attempt 2 claim. Implementation remote task fast-forward `not-needed`, `origin/main` already current, head `860277325a47e520910c481581845454fddf6a5f`.
4. **Submodule materialization:** launcher reports recursive submodules ready and initialized; `database` is at `5f6c7d473771ca7beac8dd64729f228438d95bc4` (`heads/main`).
5. **Post-validation synchronization:** implementation worktree clean at `860277325a47e520910c481581845454fddf6a5f`, equal to `origin/task/ARCH-028-ADMIN-001`; parent worktree clean at `6b7acdfa800806b8fd29ed001b18471a487259ed`, equal to `origin/task/ARCH-028-ADMIN-001`, before this report-only follow-up commit. Both task branches remain named `task/ARCH-028-ADMIN-001`.
6. **Focused validation:** rerun on Attempt 2 from the canonical implementation worktree passed, 11 tests across the billing-controls policy validation, persistence mappings, rendering, translations, authorization and audit coverage.

Attempt 1 remains recorded above with its implementation commit and broader validation. Attempt 2 changes only this parent task document to supply the requested execution evidence.

### Architectural Concerns

No new architectural concerns. Existing audit/version behavior and SUPER_ADMIN authorization remain in the established Platform Billing Policy transaction; no duplicate policy store or cross-repository change was introduced.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation is functionally acceptable, but the Completion Report is missing mandatory task-worktree execution evidence required by the architect review protocol. This is an evidence-only correction; no runtime or test code changes are requested.

The implementation correctly:
- renders the persisted `whatsappRecipientSuppressionDays` value in the existing SUPER_ADMIN Platform Billing Policy form with a seven-day fallback;
- validates the submitted value as a required positive whole number;
- persists the value through the existing singleton Platform Billing Policy upsert on create and update;
- preserves existing SUPER_ADMIN authorization, version increment, and before/after BillingAuditEvent snapshots;
- introduces no second policy/configuration store.

### Reviewed Files

- `src/lib/admin/billing-control-validation.ts`
- `src/app/actions/billing-controls.ts`
- `src/components/admin/billing-controls.tsx`
- `src/i18n/required-keys.ts`
- `src/i18n/locales/en.json`
- `tests/security/admin-billing-controls.test.mjs`

### Validation Reviewed

- Independently rerun: `node --test tests/security/admin-billing-controls.test.mjs` — PASS, 11/11.
- Completion Report evidence reviewed for build, lint, Prisma validation, changed-file diagnostics, and `git diff --check` — reported PASS.
- Broader `npm run test:unit` and `npm test` retain two unrelated failures each as recorded by the implementing agent; no task-owned billing-controls regression was identified.

### Architecture Conformance

The implementation conforms to ARCH-028 suppression-policy ownership and the ADMIN-001 task scope. The field remains part of the existing `PlatformBillingPolicy`, uses the existing audited transaction and SUPER_ADMIN boundary, and does not introduce merchant-level overrides or runtime suppression logic.

Acceptance is withheld only because the Completion Report does not record the mandatory launcher-resolved physical task-worktree evidence.

### Follow-up

Evidence-only correction required on the same task:

1. Reclaim `ARCH-028-ADMIN-001` through the canonical task launcher/worktree path for Attempt 2.
2. Record the launcher-resolved parent task worktree path and implementation task worktree path in the Completion Report.
3. Record start-of-attempt synchronization evidence for both worktrees/branches.
4. Record implementation submodule status/materialisation evidence required by the launcher packet.
5. Confirm both task branches/worktrees are clean and synchronized with their upstreams after validation.
6. Rerun the required focused validation from the canonical implementation task worktree and update the Completion Report.
7. Do not change implementation or test files solely to manufacture a new implementation commit if the existing implementation remains unchanged and valid.

Return the same task to `review`. Preserve Attempt 1 history; the next authorized claim should increment to Attempt 2.
