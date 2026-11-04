---
id: ARCH-057-SHOPIFY-007
architecture_id: ARCH-057
title: Unify settings reads and guard merchant policy writes
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: codex
claimed_at: 2026-11-04T20:07:53Z
attempt: 1
depends_on:
- ARCH-057-SHOPIFY-001
enables:
- ARCH-057-SHOPIFY-008
- ARCH-057-SHOPIFY-011
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SHOPIFY-007: Unify settings reads and guard merchant policy writes

## Architecture

Architecture ID: `ARCH-057`. Architecture document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory execution/logging/validation contract: `docs/architecture/ARCH-057/task-contract.md`. **Defined but not materialised.** Canonical destination: `docs/decisions/shopify/ARCH-057/SHOPIFY-007-unify-settings-reads-and-guard-policy-writes.md`.

## Objective

Compose merchant settings from one request-local read projection, perform no discount writes for unchanged policy, and require ACTIVE Shop state under the existing category-selection lock before committing a category change.

## Context

Review F11 identifies overlapping settings/subscription/feature reads and a settings guard that fetches a row mutation callers discard. F12 identifies discount deselect/reselect writes before the no-op check. F18 identifies a category lifecycle check performed before preparation but not under the later Shop lock. The architect now selects **ACTIVE at category-selection commit** as a requirement. This decision does not move or redefine the separate onboarding milestone.

SHOPIFY-001 supplies scalar Shop/Subscription/ShopSettings facts. This task owns the additional settings-specific plan/features/preference projection and freezes its interface for SHOPIFY-008. It does not put heavy relation includes into the global merchant context.

## Scope

Paths are relative to `moda-interact`.

| Existing path | Required edit |
|---|---|
| `app/services/feature-preferences/access.server.ts` | Add the explicit no-settings-read mutation guard; retain existing settingsAccess contract and policy |
| `app/services/feature-preferences/feature-preferences.server.ts` | Extract a pure feature projection consumed by page reads and the existing fresh transactional loader; preserve feature revision bytes |
| `app/routes/app/recovery-settings/route.tsx` | Pass framework context, construct one settings read context, reuse it for features/policy; keep knowledge invocation for SHOPIFY-008 to migrate |
| `app/services/recovery-policy/recovery-policy.server.ts` | Accept supplied settings for read composition; implement prewrite no-op and added/removed discount sets; preserve atomic revision fencing |
| `app/routes/app/settings-save/route.ts` | Use the mutation guard, retain bounded form handling and all current intents, complete operational diagnostics for every intent |
| `app/services/store-profile/store-category-selection.server.ts` | Enforce ACTIVE and existing Shop under FOR UPDATE; preserve preparation/current-template validation/generation CAS; retain actual render failure cause |
| `app/routes/app/store-profile/category/route.ts` | Consume request context, map the new lifecycle denial, log operational errors and retain existing safe response shape |
| `app/components/settings/StoreProfileSection.tsx` | Extend only the typed result union for SHOP_UNAVAILABLE; use the existing localized saveFailed presentation |
| `tests/unit/recovery-policy-save.test.ts`, `tests/unit/recovery-policy-snapshot.test.ts` | Change true no-op expectations to zero UPDATEs and cover supplied settings/delta writes |
| `tests/unit/settings-save-recovery-route.test.ts`, `tests/unit/merchant-settings-action.test.ts`, `tests/unit/ai-response-delay-loader.test.ts` | Verify guard/context reuse and unchanged form/error/revision behavior |
| `tests/unit/store-category-selection.test.ts` | Verify ACTIVE-under-lock and generation/provenance behavior |
| `tests/integration/shopify-recovery-discounts.postgres.integration.test.ts` | Preserve selected-field ownership tests; remove any fixture assumption that every save always makes exactly two updates |
| `tests/integration/merchant-feature-preferences.test.ts` | Preserve existing feature/revision integration cases; use pgvector/pgvector:pg17 instead of its obsolete postgres:15-alpine fixture |
| `tests/integration/store-category-selection.postgres.integration.test.ts` | Retain existing initial/active selection, provenance and concurrency cases |
| `package.json` | Register the exact focused scripts below |

New files:

- `app/services/feature-preferences/settings-read-context.server.ts`: the settings-specific server-only read projection below.
- `app/services/feature-preferences/merchant-settings-observability.server.ts`: thin Shared-based settings/category semantic diagnostics.
- `tests/unit/settings-read-context.test.ts`: scalar reuse, plan/preference read and pure-selector cases.
- `tests/unit/merchant-settings-observability.test.ts`: actual Shared output, code/cause/redaction/sink checks.
- `tests/integration/merchant-settings-writes.postgres.test.ts`: true no-op/selection deltas/concurrent policy revisions.
- `tests/integration/store-category-lifecycle.postgres.test.ts`: explicit lifecycle/selection lock race.
- `tests/helpers/merchant-settings-postgres.ts`: small PG17 migration/client/fixture helpers for the two new suites; no generic runner.

New files remain below 300 lines. Existing large suites need only focused edits; do not undertake unrelated test reorganization. `ai-response-delay.server.ts`, category activation service, onboarding callbacks/resume and locale catalogues are preservation/read-only touchpoints.

## Out of Scope

No onboarding milestone reorder, category-activation/Background hook, new subscription admission policy, knowledge processing implementation, global cache, schema/index/migration, discount synchronization change, provider call, per-source queue change, locale rewrite or generic repository framework. SHOPIFY-008 migrates the eight knowledge actions to the new guard. Do not change feature no-op/stale-revision semantics merely to make them match recovery policy.

## Requirements

### R1 — one presentation projection, separate mutation access

1. Add `settingsMutationAccess(request, context?)` with the exact contract below. It performs authenticated local context resolution and the same Shop lifecycle/RECOVERY_SETTINGS policy as current settingsAccess, including the old active/trialing subscription filtering. For an established tenant with valid prerequisites it does not call `readSettings` or query ShopSettings. Retain SHOPIFY-001's authenticated missing-prerequisite bootstrap/repair; this exceptional recovery is outside the guard-only zero-read budget. All production callers owned here pass actual framework context.
2. Keep `settingsAccess(request, context?)` returning `{shop, settings, session, merchant}`. Reuse one private authorization path and obtain settings only for this read-oriented method. Do not duplicate authentication/subscription I/O between the two methods.
3. Add `loadSettingsReadContext(merchant, client=db)`. Obtain scalar subscription/settings through `merchant.readSubscription()` and `merchant.readSettings()`. For a non-null planId, read its BillingPlan with current Feature mappings/Feature scalar fields in one explicit Prisma call, ordered exactly as the current feature loader. Read ShopFeaturePreference once with its existing featureId ordering. Use the already authenticated Shop's status/default language. A missing plan remains null; no replacement plan or provider sync is allowed. A missing settings row is represented as null and retains the policy reader's existing SETTINGS_NOT_FOUND failure, not a fabricated authorization denial.
4. Extract `projectFeaturePreferences` as a pure function over the settings read facts. Preserve filtering, editable/effective feature semantics and exact `revisionOf` input shape/order. The page uses this selector rather than `loadFeaturePreferences` rereading Subscription/preferences. Keep `loadFeaturePreferences(shopId, transaction)` for mutations: it still loads current transaction facts and calls the same pure selector. `saveFeaturePreferences` retains Shop lock, fresh read, no-change early return, revision check, per-changed-feature upserts and fresh returned revision.
5. Extend `loadRecoveryPolicySnapshot` with an optional supplied-settings argument below. If present, including `{settings:null}`, do not query ShopSettings. Continue reading the current override and discount catalogue, and preserve every returned field, sorting, selected dormant discounts and effective/merchant distinction. The page supplies `readContext.settings` and uses that same row for AI delay. Do not serialize the read context.
6. Expose the read context for SHOPIFY-008, but do not alter knowledge services/actions here. After this task, the settings-specific path reads subscription/settings only through memoized scalar getters and performs one plan/features plus one preference-list read. Its remaining knowledge duplicate reads are explicitly assigned to SHOPIFY-008, not hidden in a global heavy projection.

### R2 — no-op and delta discount persistence

7. Keep parsing, active Shop FOR UPDATE, current settings lookup, expected-revision comparison, selected-ID uniqueness/50 limit and same-Shop ownership validation before writes. Compute the old/new selected-ID sets and compare the full desired policy plus notification preference before any UPDATE.
8. If nothing changes, return the current settings revision with **zero discount UPDATE calls, zero settings UPDATE calls and unchanged row timestamps**. If only settings/notification fields change, leave all discount rows untouched.
9. For changed selection, issue only a nonempty removed-ID update to false and a nonempty added-ID update to true, each constrained by shopId/IDs and expected current availability. Verify affected counts against those sets; a concurrent disappearance/state mismatch raises the existing DISCOUNT_SELECTION_CHANGED error and rolls back. Retained selected IDs are never toggled. Do not filter ownership by provider ACTIVE/selectability: existing dormant/expired selections remain legitimate merchant-owned preferences.
10. Persist changed settings once in the same transaction, including changed selected-set semantics even if other fields are identical. Advance updatedAt monotonically using the existing AI-delay pattern `new Date(Math.max(Date.now(), current.updatedAt.getTime() + 1))`, so two changes cannot retain the same millisecond revision. Preserve fixedShopifyDiscountId compatibility, sorted first selection, admin override separation and provider sync ownership of provider fields. Do not remove fresh mutation checks because a page read passed.

### R3 — category ACTIVE under lock

11. Change the existing Shop lock to `WHERE id = shopId AND status = 'ACTIVE' FOR UPDATE`, inspect returned rows and fail before profile/prompt/configuration writes if no row qualifies. Add `SHOP_UNAVAILABLE` to StoreCategorySelectionError and map it to HTTP403 with `{ok:false,error:'SHOP_UNAVAILABLE'}`. Missing/inactive Shop have the same safe response. Existing CONFLICT409 and CATEGORY_UNAVAILABLE400 remain unchanged.
12. Keep prompt rendering/preparation outside the transaction, then current category/template/mapping checks under the existing lock, expected pending-generation CAS, active-category immediate publication, configuration preservation and selected draft provenance. A lifecycle update that wins the Shop lock first prevents category writes; if category selection wins first, it completes atomically before the lifecycle writer proceeds. Prove both orders with separate PostgreSQL connections and explicit barriers.
13. Keep existing onboarding/callback/resume/category activation semantics and tests unchanged. An authenticated callback milestone is not moved after billing/category success. This task adds a commit-time guard to category selection only.

### R4 — logging and failure ownership

Use the mandatory Shared error contract, actual original safe error/code/cause and existing `resolveDeploymentEnvironmentName`. The semantic adapter may expose settings/category event functions; it must not implement a generic serializer/redactor. Never log form values, selected discount titles/code text, rendered prompts/source contexts, taxonomy payloads, customer information or credentials.

| Failure/injection | Diagnostic owner | Required result |
|---|---|---|
| SHOPIFY-001 auth/scalar context failure | SHOPIFY-001 source owner | Propagate; no duplicate source error at rethrow-only settings caller |
| Settings-specific plan/features/preferences/override/catalogue read fails | The owning settings read function | Original safe DB message/code/cause once; no fabricated empty features/catalogue |
| Policy/feature/AI-delay transaction fails unexpectedly | settings-save action, with actual intent/stage | Original error once for every intent, including features; preserve rollback and safe HTTP behavior |
| Expected invalid input, revision conflict, inactive Shop, invalid feature/discount ownership | Existing typed business outcome | Preserve current 400/403/409/422 mapping; do not invent provider errors |
| Category rendering throws | Preparation boundary | Log original safe cause once before wrapping CATEGORY_UNAVAILABLE with `cause`; do not log prompt/context |
| Category transaction/preflight DB fails | Category action | Original DB error/code/cause; no partial publication/profile/config change |
| ACTIVE-under-lock finds no Shop | Typed SHOP_UNAVAILABLE | 403, no write; not an invented database outage |
| Throwing Shared sink | Shared isolation | Read failure, revision winner, rollback and public response unchanged |

## Work Items

- [ ] Add the minimal mutation guard and settings read context/selector contracts.
- [ ] Wire the settings page/save/category route with actual framework context and existing DTOs.
- [ ] Move complete no-op checks before writes and implement nonempty selection deltas plus monotonic revision.
- [ ] Enforce ACTIVE under the existing category lock and preserve onboarding/activation semantics.
- [ ] Complete original-error diagnostics for settings/category operational branches.
- [ ] Implement/register/run focused unit/UI and real PostgreSQL cases; publish accurate count/row/log evidence in the report.

## Interfaces / Contracts

Consumes `ARCH-057-SHOPIFY-001`'s exact `MerchantRequestContext` and `getMerchantRequestContext` contracts. GET/HEAD scalar reads may be memoized; non-GET and all write transactions use fresh admission. SHOPIFY-008 consumes these new contracts without copying their queries:

```ts
settingsMutationAccess(request: Request, context?: RouterContextProvider): Promise<{
  shop: Shop;
  session: MerchantRequestContext["authentication"]["session"];
  merchant: MerchantRequestContext;
}>;

type SettingsPlan = Prisma.BillingPlanGetPayload<{
  include: { features: { include: { feature: true } } };
}>;
type SettingsReadContext = Readonly<{
  shop: Pick<Shop, "id" | "status" | "defaultLanguageTag">;
  settings: ShopSettings | null;
  subscription: Subscription | null;
  plan: SettingsPlan | null;
  preferences: readonly ShopFeaturePreference[];
}>;

loadSettingsReadContext(
  merchant: MerchantRequestContext,
  client?: PrismaClient,
): Promise<SettingsReadContext>;

projectFeaturePreferences(
  facts: Pick<SettingsReadContext, "shop" | "subscription" | "plan" | "preferences">,
): ExistingFeaturePreferencesSnapshot;

loadRecoveryPolicySnapshot(
  shopId: string, now?: Date, client?: PrismaClient,
  supplied?: { settings: ShopSettings | null },
): Promise<ExistingRecoveryPolicySnapshot>;
```

Use imported concrete Prisma/SDK/router types and existing output aliases; the `Existing...` names above refer to the unchanged inferred DTOs, not additional public wire schemas. The plan read includes the Feature metadata/configuration SHOPIFY-008 needs, including inactive mappings; it must not discard them before the pure selector applies its policy. No context object enters browser data.

Add exact package scripts:

```json
{
  "test:merchant-settings:unit": "vitest run tests/unit/settings-read-context.test.ts tests/unit/merchant-settings-observability.test.ts tests/unit/recovery-policy-save.test.ts tests/unit/recovery-policy-snapshot.test.ts tests/unit/settings-save-recovery-route.test.ts tests/unit/merchant-settings-action.test.ts tests/unit/ai-response-delay-loader.test.ts tests/unit/ai-response-delay.test.ts tests/unit/store-category-selection.test.ts",
  "test:merchant-settings:postgres": "MODA_DISPOSABLE_INTEGRATION=1 MODA_SETTINGS_POSTGRES=1 vitest run tests/integration/merchant-settings-writes.postgres.test.ts tests/integration/store-category-lifecycle.postgres.test.ts tests/integration/shopify-recovery-discounts.postgres.integration.test.ts tests/integration/store-category-selection.postgres.integration.test.ts tests/integration/merchant-feature-preferences.test.ts"
}
```

## Dependencies

- ARCH-057-SHOPIFY-001

## Enables

- ARCH-057-SHOPIFY-008
- ARCH-057-SHOPIFY-011

## Acceptance Criteria

- [ ] For an established tenant with valid prerequisites the mutation guard performs no settings read; authenticated missing-prerequisite repair and the old surface/lifecycle policy remain intact.
- [ ] The page reuses scalar Subscription/ShopSettings, one plan/features read and one preference list; pure feature revision/output remains identical for the same facts.
- [ ] Identical policy saves issue no UPDATEs and leave timestamps unchanged; settings-only changes do not touch discounts; only added/removed selections change.
- [ ] Real concurrent policy writers using one revision have one changed-state winner, and provider synchronization does not overwrite merchant availability selections.
- [ ] Category writes require ACTIVE under the Shop lock, with no partial state if lifecycle changes first; the selected first-writer order is proven on PG17.
- [ ] Existing initial/active category publication, pinned provenance, config preservation, stale-generation handling and onboarding ordering remain intact.
- [ ] Every operational failure in the matrix emits safe original error/code/cause through Shared; business-denial behavior and localization remain unchanged.

## Validation

- [ ] `npm run test:merchant-settings:unit` — named cases for cached getter reuse, null settings, inactive/absent plan, pure revision parity, transaction freshness, true no-op, added/removed/retained IDs, changed same-millisecond revision, lifecycle denial and log ownership.
- [ ] `npm run test:merchant-settings:postgres` — all suites use task-owned `pgvector/pgvector:pg17` with canonical forward migrations. New cases use distinct clients and explicit lock barriers, not sleeps/mocks, for two stale policy writers and both category/lifecycle lock orders. Assert physical rows/timestamps and no partial prompt/profile/configuration writes. Existing source-sync fixture must still prove actual selection ownership after the changed update shape. Skips block acceptance.
- [ ] `npm test -- tests/unit/recovery-settings-discounts.test.tsx tests/unit/recovery-settings-submit-guard.test.tsx tests/unit/ai-response-delay-settings.test.tsx tests/unit/recovery-settings-i18n.test.ts tests/unit/onboarding-store-category.test.jsx tests/unit/store-category-activation.test.ts` — preserve UI, locale and deliberate activation/milestone behavior.
- [ ] `npm run typecheck` and `npm run build`.
- [ ] `npx --no-install eslint app/services/feature-preferences app/services/recovery-policy/recovery-policy.server.ts app/services/store-profile/store-category-selection.server.ts app/routes/app/recovery-settings/route.tsx app/routes/app/settings-save/route.ts app/routes/app/store-profile/category/route.ts app/components/settings/StoreProfileSection.tsx tests/unit/settings-read-context.test.ts tests/unit/merchant-settings-observability.test.ts tests/unit/recovery-policy-save.test.ts tests/unit/recovery-policy-snapshot.test.ts tests/unit/settings-save-recovery-route.test.ts tests/unit/merchant-settings-action.test.ts tests/unit/ai-response-delay-loader.test.ts tests/unit/store-category-selection.test.ts tests/integration/merchant-settings-writes.postgres.test.ts tests/integration/store-category-lifecycle.postgres.test.ts tests/integration/shopify-recovery-discounts.postgres.integration.test.ts tests/integration/store-category-selection.postgres.integration.test.ts tests/integration/merchant-feature-preferences.test.ts tests/helpers/merchant-settings-postgres.ts`.
- [ ] `git diff --check`; same-fixture before/after call/SQL/affected-row evidence and actual Shared JSON/cause/redaction/sink evidence; exact installed versions, canonical pins and task-owned cleanup.

## Stop Condition

After required work, acceptance and validation, set review and return the Completion Report to `moda_architect`. Stop for a changed context contract, required schema modification, non-current source or a proposed onboarding/activation policy change. Do not implement knowledge processing, modify downstream state, mark Complete or begin enabled tasks.

## Implementation Notes

A request read context is not a transaction snapshot. Preserve the existing fresh `loadFeaturePreferences` call inside mutations. The policy no-op must be checked after current revision/ownership validation, before any write. Use the new selected-set deltas rather than broad false/true updates. Category lifecycle enforcement fits its existing Shop lock and needs no new synchronization mechanism.

## Completion Report

### Status

Not Started. Defined but not materialised; no execution claim.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands/cases, prepared worktree evidence, source/Database/Shared/router pins, actual SQL/affected rows/revision winners, emitted diagnostic markers/causes and cleanup. State skipped/blocked checks explicitly.

### Deviations

None.

### Assumptions

The accepted SHOPIFY-001 context and actual integrated source are verified by the launcher before execution.

### Unresolved Issues

Implementation and required evidence remain outstanding.

### Architectural Concerns

Return changes to task ownership, schema, persisted revision semantics, queue/provider contracts or onboarding policy to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable task definition only; no implementation accepted.

### Reviewed Files

Definition and latest unchanged settings/category touchpoints.

### Validation Reviewed

Definition inspection only.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return for review; do not begin SHOPIFY-008 or another enabled task.
