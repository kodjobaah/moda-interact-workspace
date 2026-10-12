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
attempt: 1
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

Ready for Architect review (Attempt 1, 2026-10-12). Implementation commit: `8602773` (`feat(admin): configure WhatsApp recipient suppression duration`).

### Files Changed

Updated `src/lib/admin/billing-control-validation.ts`, `src/app/actions/billing-controls.ts`, and `src/components/admin/billing-controls.tsx`; added required keys in `src/i18n/required-keys.ts` and English strings in `src/i18n/locales/en.json`; expanded `tests/security/admin-billing-controls.test.mjs`.

### Work Completed

Exposed `whatsappRecipientSuppressionDays` on the existing SUPER_ADMIN Platform Billing Policy form with the persisted value shown and a seven-day default when no policy exists. The server parser requires a positive whole number and surfaces bounded validation messages. The existing policy upsert explicitly persists the field on create and update, preserving it when the full form is saved; existing before/after audit snapshots and version increments remain in the same transaction. SUPER_ADMIN authorization and the singleton policy store are unchanged. No schema, migration, Shop override, or runtime suppression logic was added.

### Validation Results

PASS: focused `node --test tests/security/admin-billing-controls.test.mjs` (11/11), including positive, zero, negative, fractional and missing duration inputs; persistence mappings; default/current rendering; translations; existing authorization/audit assertions.

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

### Architectural Concerns

No new architectural concerns. Existing audit/version behavior and SUPER_ADMIN authorization remain in the established Platform Billing Policy transaction; no duplicate policy store or cross-repository change was introduced.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
