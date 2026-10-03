---
id: ARCH-026-SHOPIFY-001
architecture_id: ARCH-026
title: Adopt the shared Shop onboarding milestone in the Shopify application
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: copilot
claimed_at: 2026-10-03T14:41:43Z
attempt: 1
depends_on:
  - ARCH-026-DATABASE-001
enables:
  - ARCH-026-ADMIN-001
  - ARCH-026-SHOPIFY-002
created: 2026-10-02
updated: 2026-10-03
---

# Adopt the shared Shop onboarding milestone in the Shopify application

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Migrate the Shopify merchant application from treating `shopify.ShopSettings.onboardingCompleted` as the authoritative one-time Moda onboarding milestone to using the provider-neutral `commerce.Shop.onboardingCompleted` introduced by `ARCH-026-DATABASE-001`, while retaining the legacy Shopify field as a compatibility mirror for now.

Preserve the existing merchant lifecycle semantics:

```text
Shop.status != ACTIVE
    -> SIGNED_OUT / REINSTALLING / SUPPORT_ONLY

Shop.status == ACTIVE
and Shop.onboardingCompleted == false
    -> ONBOARDING

Shop.status == ACTIVE
and Shop.onboardingCompleted == true
    -> derive ACTIVE / NO_CONTRACT / FROZEN / BILLING_ATTENTION
       from the existing Subscription projection
```

This task MUST NOT introduce a stored `ACCOUNT_PENDING_ACTIVATION` enum/state. Existing pending subscription/activation evidence remains the mechanism used while initial activation converges.

## Context

Before ARCH-026, Shopify persists the one-time onboarding milestone in:

```text
shopify.ShopSettings.onboardingCompleted
```

and production application code reads it from merchant home/status/access/discount paths and writes it when a verified initial billing activation completes.

DATABASE-001 adds:

```text
commerce.Shop.onboardingCompleted
```

and backfills existing development data, but intentionally does not remove the legacy Shopify field.

WooCommerce cannot depend on a Shopify-specific settings table. The shared `Shop` field therefore becomes the provider-neutral lifecycle boundary. During this development transition the Shopify application must keep a successful `false -> true` completion mirrored to the legacy field so not-yet-migrated consumers remain coherent.

Normal runtime onboarding is monotonic. This task must not add any production path that resets a completed Shop to onboarding.

## Scope

Modify only `moda-interact` application/test files required to adopt the shared milestone.

Current inspected production references include:

```text
app/routes/app/billing/callback/route.tsx
app/routes/app/billing/status/route.ts
app/routes/app/home/route.jsx
app/routes/webhooks/app/scopes-update/route.jsx
app/services/billing/merchant-billing-setup-state.ts
app/services/discounts/shopify-discount-lifecycle.service.ts
app/services/shop/merchant-route-access-policy.ts
```

Update focused tests/fixtures in the same repository as required.

### Authoritative read

After this task, Shopify merchant lifecycle decisions owned by `moda-interact` MUST read:

```text
commerce.Shop.onboardingCompleted
```

rather than `ShopSettings.onboardingCompleted`.

`ShopSettings` remains the owner of Shopify-specific merchant settings such as recovery configuration, language/time-zone defaults and Shopify discount configuration; only the onboarding milestone moves to the shared Shop lifecycle boundary.

### Completion write

When the Shopify app durably marks initial onboarding complete, update both:

```text
commerce.Shop.onboardingCompleted = true
shopify.ShopSettings.onboardingCompleted = true
```

in one database transaction/command boundary where both mutations belong to the same application operation.

Requirements:

- the transition is monotonic (`false -> true` only);
- do not reset either field to `false` in normal runtime behavior;
- failure must not leave the shared field true while the compatibility field remains false for a completed Shopify onboarding command;
- do not create `ShopSettings` solely to host the compatibility flag if the normal Shopify Shop provisioning invariant has been violated; surface the existing invariant/error rather than silently manufacturing partial settings.

The legacy mirror exists only for transition compatibility and MUST NOT remain the authoritative read after this task.

### Merchant experience state

`resolveMerchantExperienceState(...)` and its callers must use the shared Shop milestone.

Do not change the existing state vocabulary or surface matrix in this task.

Specifically do not introduce or persist `ACCOUNT_PENDING_ACTIVATION`. Current billing setup/finalization presentation remains derived from Subscription projection/pending-selection evidence.

### Shopify-specific eligibility

Shopify discount/catalogue or other application-local eligibility that currently checks `settings.onboardingCompleted` must consume the shared Shop milestone while preserving all other Shopify-specific provider conditions.

## Out of Scope

- Removing `shopify.ShopSettings.onboardingCompleted` from Prisma/database.
- Background-service migration; owned by `ARCH-026-BACKGROUND-001`.
- Admin migration; owned by `ARCH-026-ADMIN-001`.
- WooCommerce UI/API onboarding implementation.
- Changing Subscription statuses or pending-plan semantics.
- Billing-provider abstraction.
- Shop installation/reinstall state redesign.
- Recovery/product/discount redesign beyond replacing the onboarding source.
- System-test terminal validation.

## Requirements

### R1 — Shared Shop field is authoritative for Shopify app reads

After this task no production `moda-interact/app` lifecycle decision may require `ShopSettings.onboardingCompleted` as its source of truth.

### R2 — Legacy flag remains present

Do not remove, rename or repurpose `ShopSettings.onboardingCompleted`.

### R3 — Successful completion is mirrored

A Shopify-app-owned successful onboarding completion sets both shared and legacy flags to true as one bounded durable operation.

### R4 — One-time lifecycle is preserved

Once shared `Shop.onboardingCompleted` is true, normal cancellation, NO_CONTRACT, billing attention, reinstall or provider reconciliation must not return the merchant to ONBOARDING.

### R5 — No new stored activation state

Do not add `ACCOUNT_PENDING_ACTIVATION` or another duplicate durable merchant-state enum. Existing subscription projection/pending activation evidence remains unchanged.

### R6 — Shopify settings retain their real responsibility

Do not move recovery/language/discount settings out of `ShopSettings` in this task.

## Work Items

- [x] Update Shopify Shop/query projections needed by merchant routes to include shared `Shop.onboardingCompleted`.
- [x] Migrate merchant home/status/access-policy lifecycle reads from `ShopSettings.onboardingCompleted` to `Shop.onboardingCompleted`.
- [x] Migrate Shopify scopes/discount lifecycle eligibility reads to the shared Shop milestone where onboarding is the only reason for reading the legacy flag.
- [x] Change the app-owned onboarding completion command to set `Shop.onboardingCompleted=true` and mirror `ShopSettings.onboardingCompleted=true` atomically.
- [x] Preserve existing Subscription/pending-plan based billing setup/finalization behavior.
- [x] Update focused unit/integration tests to prove monotonic shared onboarding behavior and legacy mirroring.
- [x] Add a static audit/test ensuring production `moda-interact/app` lifecycle code no longer treats the legacy field as authoritative.

## Interfaces / Contracts

### Database contract owner

`ARCH-026-DATABASE-001`

### Shared lifecycle field

```text
commerce.Shop.onboardingCompleted
```

### Transitional compatibility field retained

```text
shopify.ShopSettings.onboardingCompleted
```

The compatibility field remains present but is not authoritative for application lifecycle reads after this task.

## Dependencies

- `ARCH-026-DATABASE-001`

DATABASE-001 must be architect-accepted Complete and the `moda-interact` nested `database/` gitlink must be updated to the accepted database main commit before implementation.

## Enables

- `ARCH-026-ADMIN-001`
- `ARCH-026-SHOPIFY-002`

ADMIN-001 additionally depends on BACKGROUND-001 so the shared milestone is maintained by both current production completion writers before Admin makes it its cross-platform presentation source. SHOPIFY-002 is the next serialized `moda-interact` ARCH-026 migration and adopts shared international context after the onboarding migration is accepted.

## Acceptance Criteria

- [x] Shopify merchant experience derives ONBOARDING from `Shop.onboardingCompleted`, not the legacy ShopSettings flag.
- [x] Existing post-onboarding Subscription projection continues to derive ACTIVE / NO_CONTRACT / FROZEN / BILLING_ATTENTION unchanged.
- [x] No `ACCOUNT_PENDING_ACTIVATION` durable enum/state is introduced.
- [x] Shopify app onboarding completion sets both shared and legacy flags to true in one bounded durable operation.
- [x] No normal runtime path resets shared onboarding completion to false.
- [x] Reinstall/cancellation/billing failure does not return a previously completed Shop to ONBOARDING.
- [x] Shopify-specific settings remain in `ShopSettings` and are not duplicated onto Shop.
- [x] Production Shopify app lifecycle reads no longer use `ShopSettings.onboardingCompleted` as authority.
- [x] Existing focused billing/home/access/discount tests remain active and pass with assertions updated to the shared source.
- [x] No Woo-specific or Background implementation is introduced.

## Validation

Run repository-declared validation plus focused tests for the changed lifecycle paths.

Required categories:

- [x] Confirm nested `database/` gitlink is at accepted DATABASE-001 main commit `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3` and run Prisma generation;
- [x] typecheck;
- [x] targeted lint for changed files (two existing baseline diagnostics remain; details below);
- [x] focused merchant-route/access-policy tests;
- [x] focused billing callback/setup tests including atomic dual-write behavior;
- [x] focused Shopify discount lifecycle eligibility tests;
- [x] reinstall/cancel/no-contract regression tests proving completed onboarding remains completed;
- [x] static search/audit of production `app/` references to legacy `onboardingCompleted` with the intentional compatibility writes documented;
- [x] production build;
- [x] `git diff --check`;
- [x] clean task-worktree evidence after commit.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect`, and STOP. Do not begin another ARCH-026 task.

## Implementation Notes

This is a development/pre-production migration. Do not build a permanent compatibility abstraction around the old field. The legacy mirror remains only because other repositories are being migrated in bounded tasks and the user explicitly requested that the column not be removed yet.

Prefer changing lifecycle query projections to load the shared Shop field directly rather than copying it through `ShopSettings` DTOs.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

Implementation commit `93f36cbecc396ee4c5f3c6d7f70b2a425733c5f0` changes 25 files in `moda-interact`: merchant lifecycle policy and route readers, billing callback mirroring, Shopify discount/scope eligibility, lifecycle resolver call sites, and focused unit/integration tests. The database submodule gitlink was already at the accepted DATABASE-001 commit and was not changed by this task.

### Work Completed

`commerce.Shop.onboardingCompleted` is now the only lifecycle authority used by the Shopify app. Merchant home, billing setup/status, access policy, discount sync and scope-update eligibility consume the shared Shop field. Successful billing activation updates the shared Shop and existing ShopSettings compatibility mirror to true in one Prisma transaction; update counts enforce both pre-existing rows and any invariant failure throws to roll back the transaction. No production false reset, activation-state enum, or Shopify-settings relocation was introduced. Obsolete settings reads were removed while settings reads needed for merchant UI context remain.

The static source test checks that production app code does not read the legacy onboarding field as authority, while documenting the two intentional transactional/migration-compatible writes. Existing Subscription status and pending-selection behavior is retained.

### Validation Results

Passed:
- `npm run prisma:generate` (also run by the production build) generated Prisma Client 6.19.3 against the accepted database gitlink.
- `npm run typecheck`.
- Focused Vitest suite: 7 files passed, 1 PostgreSQL-dependent integration file skipped; 114 tests passed, 6 skipped. This includes merchant access policy, home, billing callback/status, discount lifecycle, scopes update, and the static shared-onboarding authority audit.
- `npm run build` completed for client and SSR output.
- `git diff --check`.
- Production `app/` search found lifecycle reads only from shared Shop projections. The only completion writes are the shared Shop and legacy mirror assignments inside the billing callback transaction; no false reset was found.
- Implementation branch commit was pushed to `origin/task/ARCH-026-SHOPIFY-001`; implementation worktree was clean after commit.

Limitations / existing diagnostics:
- `tests/integration/merchant-feature-preferences.test.ts` skipped all six cases because PostgreSQL container prerequisites are unavailable in this environment.
- Targeted ESLint reported two existing diagnostics outside this task's behavior: `process` is undefined in `app/routes/app/billing/select/route.jsx`, and `i18n.t` lacks prop validation in `app/routes/app/merchant-support/route.jsx`. Migration-related unused queries/imports found during lint were removed.
- The build completed with existing dependency/bundler warnings (Zod annotation comments, external Prisma browser entry, empty route chunks, and a large merchant-i18n chunk). `npm ci` also reported 41 dependency audit vulnerabilities; dependency manifests were not changed.

### Deviations

The targeted lint command is not fully clean because of the two existing findings listed above. PostgreSQL-backed integration cases could not execute and were skipped by the suite. No scope or implementation-boundary deviations.

### Assumptions

- DATABASE-001 adds/backfills `commerce.Shop.onboardingCompleted` and retains the legacy Shopify field.
- Background migration is performed separately by ARCH-026-BACKGROUND-001.

### Git / VCS

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-SHOPIFY-001`, branch `task/ARCH-026-SHOPIFY-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-SHOPIFY-001`, branch `task/ARCH-026-SHOPIFY-001`.
- Shared workspace and shared implementation source checkout were not switched or mutated for task work; no other task worktree was reused.
- Launcher synchronization: parent and implementation remote task-branch fast-forwards were not needed; `origin/main` was already incorporated/current in both prepared worktrees. Parent claim commit: `64ee8f74a6c8470b90653eb09fabbc4ffd7c7438`.
- Launcher recursive `git submodule sync --recursive` and `git submodule update --init --recursive` passed. `database/` was verified at `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.
- Implementation commit: `93f36cbecc396ee4c5f3c6d7f70b2a425733c5f0`, pushed to `origin/task/ARCH-026-SHOPIFY-001`.
- Parent task report is being committed and pushed separately on `task/ARCH-026-SHOPIFY-001`; no implementation gitlink was staged.

### Unresolved Issues

The two existing targeted lint diagnostics and unavailable PostgreSQL container prerequisites are the only validation limitations. No implementation blocker remains.

### Architectural Concerns

None identified. The legacy field remains a write-only compatibility mirror for the Shopify app during the bounded cross-repository migration.

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
