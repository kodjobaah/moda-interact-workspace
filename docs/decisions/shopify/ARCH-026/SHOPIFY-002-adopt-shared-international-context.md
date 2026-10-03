---
id: ARCH-026-SHOPIFY-002
architecture_id: ARCH-026
title: Adopt the shared merchant international context in the Shopify application
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor: copilot
claimed_at: 2026-10-03T15:55:07Z
attempt: 1
depends_on:
  - ARCH-026-DATABASE-002
  - ARCH-026-SHOPIFY-001
enables:
  - ARCH-026-BACKGROUND-002
  - ARCH-026-ADMIN-002
created: 2026-10-02
updated: 2026-10-03
---

# Adopt the shared merchant international context in the Shopify application

## Architecture

Architecture ID: `ARCH-026`

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator: `moda_architect`

## Objective

Make provider-neutral `commerce.Shop` international-context fields authoritative for Shopify application business reads while continuing to mirror the retained Shopify ShopSettings fields during the development transition.

The shared fields are:

```text
Shop.storeLocale
Shop.defaultLanguageTag
Shop.defaultTimeZone
Shop.defaultCountryCode
```

This task must preserve current Shopify behavior while removing the architectural requirement that downstream cross-platform code read international context from `shopify.ShopSettings`.

## Context

The Shopify Shop provisioning service already receives:

```text
primary shop locale
IANA timezone
country code
```

and currently writes normalized defaults into `ShopSettings`. DATABASE-002 adds shared Shop fields and backfills existing language/time-zone/country values while retaining the old columns.

`storeLocale` is new and represents provider-native locale identity. For Shopify, persist the primary locale returned by Shopify after bounded trim/validation; do not force it through the current fixed Admin locale catalogue.

The normalized `defaultLanguageTag` remains the value used by Moda business/translation helpers. Translation coverage does not constrain which provider locale may be persisted.

## Scope

Modify only `moda-interact` production/tests needed to migrate Shopify-owned international-context writes and application reads.

Current inspected areas include Shop provisioning, Merchant Knowledge, merchant support/billing notifications, recovery query presentation and merchant i18n helpers.

### Authoritative writes

When Shopify provisioning establishes merchant international context, write both:

```text
commerce.Shop.storeLocale
a shared normalized language/time-zone/country context
```

and the existing ShopSettings language/time-zone/country compatibility fields in the same bounded provisioning operation where practical.

Do not clear a previously-known shared value merely because a provider response omits an optional field during a later/reinstall lookup unless current product semantics explicitly require clearing it.

### Authoritative reads

After this task, Shopify application business code that needs merchant/store international context must read the shared Shop fields rather than querying ShopSettings solely for those values.

Keep ShopSettings reads that are genuinely required for Shopify-specific recovery/discount settings.

### Locale policy

Do not introduce or reuse a fixed Moda allowlist to validate the provider-native store locale.

`storeLocale` preserves the bounded Shopify locale identifier. `defaultLanguageTag` continues through the existing canonical language-tag normalizer when possible.

Do not change the Shopify Admin user's UI-locale catalogue in this task; that is a separate UI concern.

## Out of Scope

- Removing the legacy ShopSettings fields.
- Woo/WordPress locale mapping.
- Background migration; owned by BACKGROUND-002.
- Admin migration; owned by ADMIN-002.
- Translation catalogue expansion.
- Billing/recovery semantics unrelated to the context source.
- Merchant Knowledge language-policy redesign.

## Requirements

### R1 — Shared context is authoritative for application business reads

Production `moda-interact/app` code must not require ShopSettings solely to obtain merchant language/time-zone/country after this task.

### R2 — Provider locale remains open-ended

Do not reject a Shopify store locale because it is absent from a Moda UI translation list.

### R3 — Legacy mirrors remain coherent

Current ShopSettings language/time-zone/country columns remain populated as compatibility mirrors when Shopify establishes those values.

### R4 — Missing provider data does not manufacture locale

Do not invent a provider-native `storeLocale` from a fallback language tag when Shopify does not supply one.

### R5 — Existing normalization behavior is preserved

Use the existing language-tag, time-zone and country canonicalization rules for the shared normalized fields rather than inventing new semantics.

## Work Items

- [x] Update the nested database gitlink to accepted DATABASE-002 and regenerate Prisma.
- [x] Write Shopify primary provider locale to `Shop.storeLocale` without a fixed allowlist.
- [x] Write normalized language/time-zone/country to shared Shop fields during provisioning.
- [x] Continue mirroring retained ShopSettings international-context fields.
- [x] Migrate application reads that use ShopSettings solely for international context to shared Shop fields.
- [x] Preserve Shopify-specific settings reads unrelated to international context.
- [x] Update focused tests for non-English/region locales, nulls and unsupported-by-Moda-translation provider locales.
- [x] Add a static audit of remaining production ShopSettings international-context reads/writes and document compatibility mirrors.

## Interfaces / Contracts

Database owner: `ARCH-026-DATABASE-002`.

Authoritative shared fields:

```text
commerce.Shop.storeLocale
commerce.Shop.defaultLanguageTag
commerce.Shop.defaultTimeZone
commerce.Shop.defaultCountryCode
```

Retained mirrors:

```text
shopify.ShopSettings.defaultLanguageTag
shopify.ShopSettings.defaultTimeZone
shopify.ShopSettings.defaultCountryCode
```

## Dependencies

- `ARCH-026-DATABASE-002`
- `ARCH-026-SHOPIFY-001`

SHOPIFY-001 serializes the two ARCH-026 migrations in `moda-interact`; DATABASE-002 provides the accepted shared schema.

## Enables

- `ARCH-026-BACKGROUND-002`
- `ARCH-026-ADMIN-002`

## Acceptance Criteria

- [x] Shopify provisioning persists provider-native primary locale to `Shop.storeLocale` without a fixed allowlist.
- [x] Shared Shop normalized language/time-zone/country fields are populated using existing canonicalization rules.
- [x] Legacy ShopSettings fields remain present and are mirrored for compatibility.
- [x] Production application business reads no longer require ShopSettings solely for international context.
- [x] A syntactically bounded Shopify provider locale lacking Moda translation coverage is preserved rather than rejected.
- [x] Null/missing provider values do not create invented locale/time-zone/country values.
- [x] Existing Merchant Knowledge/recovery/billing behavior is unchanged except for the source of international context.

## Validation

- [x] Prisma generation from accepted DATABASE-002;
- [x] typecheck;
- [x] targeted lint;
- [x] focused Shop provisioning tests including regional/non-English/provider-locale cases;
- [x] Merchant Knowledge/recovery/billing notification tests affected by context-source migration;
- [x] static audit of ShopSettings international-context references;
- [x] production build;
- [x] `git diff --check`;
- [x] clean task-worktree evidence.

## Stop Condition

After required work and validation, set status to `review`, complete the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

Do not expand this source migration into a general i18n refactor. Reuse current canonicalizers and preserve existing behavior.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

Implementation commit `e55ba35eae1376ed546c1de18ade89b1dff421e2` changes 26 files in `moda-interact`: Shopify Shop provisioning, merchant UI context consumers, Merchant Knowledge language defaults, support/billing notification readers, and focused unit/integration fixtures. The nested `database/` gitlink was already at the accepted DATABASE-002 commit `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`; it was not changed or staged by this task.

### Work Completed

Shopify provisioning now writes the primary provider locale to `commerce.Shop.storeLocale` after bounded trim and syntax validation, without a Moda translation-catalogue allowlist. Existing language, time-zone, and country canonicalizers populate the shared normalized Shop fields. The Shop, Subscription, and ShopSettings compatibility mirror upserts run in one Prisma transaction. Missing or invalid optional provider values are omitted from updates so previously known shared values and mirrors are preserved; no fallback locale is manufactured.

Application merchant UI context, recovery access, billing/promotion/usage surfaces, Merchant Knowledge defaults, merchant support, and subscription-ended notifications now read international context from shared Shop fields. ShopSettings reads needed for recovery policy and feature preferences remain. ShopSettings language/time-zone/country columns remain compatibility mirrors written only by Shopify provisioning in this scope.

The static authority test scans production `app/` sources for legacy international-context reads and checks that shared fields and compatibility mirrors are written within the provisioning transaction. Focused tests cover regional and non-catalogue provider locales, missing values, shared-Shop Merchant Knowledge defaults, and route/business-reader behavior.

### Validation Results

Passed:
- `npm run prisma:generate` generated Prisma Client 6.19.3 from the accepted DATABASE-002 schema; `npm run build` also regenerated the client.
- `npm run typecheck`.
- Targeted ESLint over all changed production and test files.
- Provisioning, static authority, merchant-support, and subscription-ended notification suites: 4 files passed, 35 tests passed.
- Merchant Knowledge shared-Shop language fallback test: 1 passed (the other four tests were filtered out).
- Affected route/UI and Merchant Knowledge action/upload suites: 9 files passed, 153 tests passed.
- `npm run build` completed client and SSR builds.
- `git diff --check` passed before commit; both task worktrees were clean after their respective commits.
- Production `app/` source audit found no remaining international-context business reads from ShopSettings. Remaining ShopSettings reads are for recovery/feature configuration, while the international-context fields are written as compatibility mirrors by `ShopService`.

Limitations / baseline diagnostics:
- The two affected PostgreSQL-backed Merchant Knowledge integration files skipped all 11 tests because their environment gate prerequisites were unavailable.
- Running the entire `merchant-knowledge-read-model.test.ts` file still produces one pre-existing catalogue-filter assertion failure (the assertion expects only `WEB_PAGE`/`REMOTE_URL`, while the unchanged implementation queries `REMOTE_URL` and `UPLOAD`). The assertion was verified unchanged from the task-branch baseline. The new shared-Shop language test passes independently.
- The production build completed with existing dependency/bundler warnings (Prisma browser entry externalization, Zod annotation comments, empty route chunks, and a large merchant-i18n chunk). Dependency manifests were not changed.

### Deviations

The PostgreSQL-backed integration tests were environment-skipped, and the unchanged Merchant Knowledge catalogue-filter baseline assertion fails when its entire test file is run; both limitations are recorded above. GitKraken's push helper encountered an upstream configuration mismatch pointing at `main`, so the implementation commit was explicitly pushed to `origin/task/ARCH-026-SHOPIFY-002`. No push to `main`, merge, or scope deviation occurred.

### Assumptions

- DATABASE-002 is complete and the shared fields are available in the accepted nested database gitlink.

### Unresolved Issues

No implementation blockers. Architect review should note the environment-skipped database integration tests and the unrelated baseline Merchant Knowledge catalogue-filter assertion failure.

### Architectural Concerns

None identified. The legacy Shopify language/time-zone/country fields remain compatibility mirrors; provider-neutral Shop fields are authoritative for application business reads.

### Git / VCS

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-SHOPIFY-002`, branch `task/ARCH-026-SHOPIFY-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-SHOPIFY-002`, branch `task/ARCH-026-SHOPIFY-002`.
- Shared workspace and shared implementation source checkout were not switched or mutated for task work; no other task worktree was reused.
- Launcher synchronization: parent and implementation remote task-branch fast-forwards were not needed; `origin/main` was already incorporated/current in both prepared worktrees. Parent claim commit: `f23e7a5004de971ace45d01bf67990c4d556a843`.
- Launcher recursive `git submodule sync --recursive` and `git submodule update --init --recursive` passed. `database/` was verified at `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.
- Implementation commit `e55ba35eae1376ed546c1de18ade89b1dff421e2` was pushed to `origin/task/ARCH-026-SHOPIFY-002`; implementation worktree was clean after commit.
- The parent task report is committed and pushed separately on `task/ARCH-026-SHOPIFY-002`; no implementation gitlink was staged.

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
