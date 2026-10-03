---
id: ARCH-026-BACKGROUND-002
architecture_id: ARCH-026
title: Adopt the shared merchant international context in Background
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-026-DATABASE-002
  - ARCH-026-SHOPIFY-002
  - ARCH-026-BACKGROUND-001
  - ARCH-025-BACKGROUND-015
enables: []
created: 2026-10-02
updated: 2026-10-03
---

# Adopt the shared merchant international context in Background

## Architecture

Architecture ID: `ARCH-026`

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator: `moda_architect`

## Objective

Migrate Background runtime reads of merchant language, time zone and country from Shopify-specific `ShopSettings` to provider-neutral `commerce.Shop` international context, preserving existing conversation/recovery/template semantics.

## Context

ARCH-025 has completed the CheckoutRecovery maintainability refactor. Current Background reads of `ShopSettings.defaultLanguageTag`, `defaultTimeZone` and `defaultCountryCode` are now owned by three distinct boundaries:

```text
src/services/conversation.service.ts
src/services/whatsapp-template-selector.service.ts
src/services/checkout-recovery/recovery-snapshot-builder.service.ts
```

`CheckoutRecoveryService` is now a thin façade and no longer owns merchant-default international-context loading. `RecoverySnapshotBuilderService` owns the Shop lookup and passes the resulting defaults to the existing pure `recovery-mappers.ts` policy. DATABASE-002 establishes these values on shared Shop; SHOPIFY-002 ensures current Shopify provisioning maintains them.

Woo Background workflows must not require a Shopify settings row merely to resolve merchant international context.

## Scope

Modify only `moda-interact-background` code/tests required to change the source of merchant/store international context.

Current inspected production areas are:

```text
src/services/conversation.service.ts
src/services/whatsapp-template-selector.service.ts
src/services/checkout-recovery/recovery-snapshot-builder.service.ts
```

Migrate related query projections and focused tests as required. `checkout-recovery.service.ts` must not regain international-context query ownership.

### Authoritative reads

Use the shared Shop fields actually required by each existing Background flow:

```text
Shop.defaultLanguageTag
Shop.defaultTimeZone
Shop.defaultCountryCode
```

`Shop.storeLocale` is the provider-native identity owned by the shared data model, but no current inspected Background flow consumes it directly. Do not add a synthetic `storeLocale` read or translation-coverage check merely to mention the field.

Do not read ShopSettings as a fallback for these values after this task. The accepted DATABASE-002 migration/backfill and SHOPIFY-002 writer migration are the compatibility mechanism.

### Locale policy

Do not add a fixed locale allowlist. Existing business helpers may normalize `defaultLanguageTag` for provider/tool requirements, but an unknown provider-native `storeLocale` must not cause job failure by itself.

Preserve the existing distinction between merchant/store default language and customer/conversation language. CommerceAgent should continue replying in the conversation/customer language where the existing architecture says so.

## Out of Scope

- Writing shared international context.
- Woo plugin locale synchronization.
- Shopify app migration; owned by SHOPIFY-002.
- Admin migration; owned by ADMIN-002.
- Translation-provider/catalogue redesign.
- Queue/event contract changes.
- Billing/recovery lifecycle redesign.

## Requirements

### R1 — Shared context is authoritative

Background international-context reads come from Shop, not ShopSettings.

### R2 — No Shopify row requirement

A Woo Shop with no ShopSettings row can supply shared language/time-zone/country context to Background.

### R3 — No locale allowlist

Provider-native locale identity is not rejected because it lacks a Moda-authored translation.

### R4 — Existing language semantics remain intact

Store default language and conversation/customer response language remain separate concepts.

## Work Items

- [x] Verify the nested database gitlink is already pinned to accepted DATABASE-002 and regenerate Prisma.
- [x] Migrate `ConversationService.getOrCreateRecoveryConversation(...)` merchant-default language projection to `Shop.defaultLanguageTag`.
- [x] Migrate `WhatsAppTemplateSelectorService` from an injected `shopSettings` reader to an injected `shop` reader and resolve merchant language from `Shop.defaultLanguageTag`.
- [x] Migrate `RecoverySnapshotBuilderService` to select top-level Shop `defaultLanguageTag/defaultTimeZone/defaultCountryCode`; keep `recovery-mappers.ts` precedence/normalization policy unchanged.
- [x] Add/update focused tests for all three owners, including Woo-like Shop fixtures with no ShopSettings row.
- [x] Update documentation that names ShopSettings as the international-context source.
- [x] Add a static audit of production ShopSettings international-context references.

## Interfaces / Contracts

Database owner: `ARCH-026-DATABASE-002`.

No queue/shared-package contract changes.

## Dependencies

- `ARCH-026-DATABASE-002`
- `ARCH-026-SHOPIFY-002`
- `ARCH-026-BACKGROUND-001`
- `ARCH-025-BACKGROUND-015`

SHOPIFY-002 ensures the current provider writer maintains shared fields; BACKGROUND-001 serializes ARCH-026 changes in the Background repository. ARCH-025-BACKGROUND-015 is Complete and establishes the final CheckoutRecovery ownership boundary, including `RecoverySnapshotBuilderService`, that this task must modify.

## Enables

None.

## Acceptance Criteria

- [x] Background production code no longer requires ShopSettings solely for language/time-zone/country context.
- [x] Woo-like Shop fixtures without ShopSettings can resolve shared international context.
- [x] Existing conversation language and WhatsApp template-selection semantics remain unchanged.
- [x] Existing recovery country/time-zone/language precedence and normalization behavior in `recovery-mappers.ts` remains unchanged apart from the merchant-default source.
- [x] Unknown provider-native store locale does not fail jobs solely due to translation coverage; no new Background `storeLocale` validation/read is introduced where none exists today.
- [x] No queue/event contract or business lifecycle changes are introduced.

## Validation

- [x] `npm run prisma:generate` from accepted DATABASE-002 and `npm run prisma:validate`;
- [x] focused `tests/unit/services/conversation.service.test.ts`;
- [x] focused `tests/unit/services/whatsapp-template-selector.service.test.ts`;
- [x] focused `tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`;
- [x] matured-candidate/materialization regression where it protects recovery snapshot/context behavior;
- [x] Woo-like no-ShopSettings fixtures proving all three migrated readers work from shared Shop state;
- [x] static audit of production `src/` for `ShopSettings.defaultLanguageTag/defaultTimeZone/defaultCountryCode` reads;
- [x] `npm run test:unit` (executed; unrelated suite failures detailed in Completion Report);
- [x] `npm test` (executed; unrelated failures and unavailable PostgreSQL detailed in Completion Report);
- [x] `npm run build` (the repository build runs TypeScript compilation);
- [x] `git diff --check`;
- [x] clean task-worktree evidence.

The repository currently declares no standalone `lint` or `typecheck` npm script. Do not invent one for this task.

## Stop Condition

After required work and validation, set status to `review`, complete the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

This is a source migration, not an opportunity to redesign language selection or translation fallbacks. Preserve the ARCH-025 ownership split: `RecoverySnapshotBuilderService` loads merchant defaults; `recovery-mappers.ts` remains the pure precedence/normalization policy; `CheckoutRecoveryService` remains a façade.

## Completion Report

### Status

Review

### Files Changed

- `src/services/conversation.service.ts`
- `src/services/whatsapp-template-selector.service.ts`
- `src/services/checkout-recovery/recovery-snapshot-builder.service.ts`
- `tests/unit/services/conversation.service.test.ts`
- `tests/unit/services/whatsapp-template-selector.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- `docs/commerce-host.md`

### Work Completed

- Migrated recovery conversation initialization to select `shop.defaultLanguageTag` through the `CheckoutRecovery` relation and pass it to the existing language resolver.
- Changed `WhatsAppTemplateSelectorService` to inject/use `PrismaClient.shop`, query the Shop by `id`, and normalize `defaultLanguageTag` as before. Customer language and template candidate precedence are unchanged.
- Changed `RecoverySnapshotBuilderService` to select shared Shop `defaultLanguageTag`, `defaultCountryCode`, and `defaultTimeZone` directly. `recovery-mappers.ts` remains unchanged, preserving its precedence and normalization policy.
- Updated focused tests to use Shop-only international-context fixtures with no `ShopSettings`; retained existing null/invalid-language and country/time-zone precedence coverage.
- Updated the matured-candidate materialization fixture and expectation to match the existing mapper contract: merchant default supplies recovery language while current checkout country/time zone retain precedence.
- Updated `docs/commerce-host.md` to identify `Shop.defaultLanguageTag` as the recovery-conversation language source.
- Implementation commit pushed to `origin/task/ARCH-026-BACKGROUND-002`: `94da7caba06741a16d708689a92fdcfc42b34ff4`.
- Confirmed the nested `database/` gitlink was already at accepted DATABASE-002 commit `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`; no gitlink or schema changes were needed.
- Static source audit found no `ShopSettings.defaultLanguageTag`, `ShopSettings.defaultTimeZone`, or `ShopSettings.defaultCountryCode` reads under production `src/`. Remaining selected defaults in the three owners are direct Shop projections; documentation names the shared Shop field.
- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  - parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-BACKGROUND-002` / `task/ARCH-026-BACKGROUND-002`
  - implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-BACKGROUND-002` / `task/ARCH-026-BACKGROUND-002`
  - shared workspace checkout switched/mutated: no; shared implementation checkout switched/mutated: no; another task worktree reused: no.
- Start-of-attempt synchronization: parent and implementation remote task branches fast-forwarded `not-needed`; `origin/main` incorporated `already-current` in both worktrees.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database/` initialized at `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.

### Validation Results

- `npm ci`: passed; installed 496 packages from the lockfile. npm reported 4 high and 2 moderate dependency audit findings and install-script approval notices.
- `npm run prisma:generate`: passed against accepted DATABASE-002 `database/` commit `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3` using Prisma 6.19.3.
- `npm run prisma:validate`: passed; schema valid.
- Focused `npm exec vitest -- run tests/unit/services/conversation.service.test.ts tests/unit/services/whatsapp-template-selector.service.test.ts tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`: passed, 27/27.
- Focused `npm exec vitest -- run tests/unit/services/matured-candidate.materialization.test.ts`: passed, 25/25.
- `npm run build`: passed; Prisma generation and TypeScript compilation succeeded.
- Static audit: `rg` over production `src/` found no ShopSettings international-context field reads.
- `npm run test:unit`: 1,547 passed and 3 failed across 118 files; the failures are three billing-reconciliation cases. An additional suite failed to load because `tests/unit/commerce/evidence.test.ts` references the missing fixture `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-BACKGROUND-002/docs/architecture/ARCH-020-evidence-contract-fixtures.json`.
- `npm test`: 1,597 passed, 38 skipped, 7 failed across 136 files; includes the same three billing-reconciliation failures, the missing ARCH-020 fixture, and four PostgreSQL integration cases unable to connect to `localhost:5432`.
- `git diff --check`: passed.
- The repository declares no standalone lint or typecheck script; the production build supplied TypeScript validation.

### Deviations

- The full unit/repository suites are not green for unrelated billing tests, a missing external ARCH-020 task-worktree fixture, and unavailable local PostgreSQL. No changes were made outside the task scope to address these failures.

### Assumptions

- SHOPIFY-002 is complete before this task so current Shopify writers maintain shared context.

### Unresolved Issues

Repository-wide validation remains partially blocked by the failures documented above; the focused tests for all modified context readers, Prisma checks, and build pass.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

Accepted. Implementation `94da7caba06741a16d708689a92fdcfc42b34ff4` performs the bounded ARCH-026 source migration without changing Background language-selection or recovery precedence policy. `ConversationService` now reads the merchant default from `Shop.defaultLanguageTag`; `WhatsAppTemplateSelectorService` changes only its merchant-fallback source to shared Shop while preserving customer exact/base and platform fallback ordering; and `RecoverySnapshotBuilderService` loads `Shop.defaultLanguageTag/defaultCountryCode/defaultTimeZone` and passes them into the unchanged pure `recovery-mappers.ts` policy.

The matured-candidate regression change is conformant rather than a policy change: ARCH-025 already established merchant-only recovery language (`merchant-default`) while country/time-zone/currency retain current/event precedence. The former frozen assertion lagged that accepted contract; B002 updates it and the suite now passes 25/25. Production `src/` contains no remaining `ShopSettings` reads of `defaultLanguageTag`, `defaultTimeZone` or `defaultCountryCode`, and no synthetic `storeLocale` read or locale allowlist was introduced.

The full-suite residuals do not block acceptance. The three billing-reconciliation failures, four PostgreSQL translation-enum failures (`localhost:5432` unavailable), and missing ARCH-020 evidence fixture are identities governed by `ARCH025-BACKGROUND-TEST-001`. The previous matured-candidate baseline identity disappears in this submission; per the baseline rule, that is an improvement and must not be recreated.

### Reviewed Files

- `src/services/conversation.service.ts`
- `src/services/whatsapp-template-selector.service.ts`
- `src/services/checkout-recovery/recovery-snapshot-builder.service.ts`
- `tests/unit/services/conversation.service.test.ts`
- `tests/unit/services/whatsapp-template-selector.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-snapshot-builder.service.test.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- `docs/commerce-host.md`

### Validation Reviewed

- `npm run prisma:generate`: passed against accepted DATABASE-002 `database@16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.
- `npm run prisma:validate`: passed.
- Conversation/template/snapshot focused tests: 27/27 passed.
- Matured-candidate regression: 25/25 passed.
- Production static audit: no ShopSettings international-context reads remain.
- `npm run build`: passed.
- `npm run test:unit`: 1,547 passed / 3 known billing baseline failures plus the known missing ARCH-020 fixture collection error.
- `npm test`: 1,597 passed / 38 skipped / 7 failed: three known billing baseline identities plus four known PostgreSQL-unavailable translation-enum identities; the same ARCH-020 fixture collection error remains.
- `git diff --check`: passed.
- Submitted launcher/worktree/synchronization/recursive-submodule evidence is complete; both task refs are published and clean.

### Architecture Conformance

Conformant. Shared `commerce.Shop` is now authoritative for Background merchant international context, Woo-like Shops no longer require `shopify.ShopSettings` for those defaults, existing conversation/template/recovery semantics are preserved, and ARCH-025 ownership boundaries remain intact.

### Follow-up

None for this task. ARCH-026 Background migration is complete through BACKGROUND-002; this task enables no dependant.
